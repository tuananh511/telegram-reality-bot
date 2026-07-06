"""
Daily Quote Telegram Bot
-------------------------
Sinh và gửi một quote tiếng Việt tới Telegram theo lịch định kỳ (cronjob).

Thiết kế để chạy dưới dạng một script "chạy một lần rồi thoát" (one-shot),
được gọi lặp lại bởi cron / systemd timer / task scheduler bất kỳ.
Mỗi lần chạy, script tự quyết định có nên gửi quote hay không (dựa trên
khung giờ hoạt động và xác suất ngẫu nhiên), sinh nội dung bằng Gemini,
tự kiểm tra chất lượng/trùng lặp, rồi gửi qua Telegram Bot API.

State (các quote đã dùng) được lưu trong một file JSON cục bộ, do đó cần
chạy trên một máy có ổ đĩa bền (VPS, máy chủ cá nhân...) — không phù hợp
với môi trường serverless/stateless mà không có volume lưu trữ riêng.
"""

from __future__ import annotations

import json
import logging
import os
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import requests
from google import genai

# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("quote-bot")


# =========================
# CONFIG
# =========================

@dataclass(frozen=True)
class Config:
    bot_token: str
    chat_id: str
    gemini_api_key: str
    gemini_model: str
    used_messages_path: Path
    sleep_hour_start: int
    sleep_hour_end: int
    send_probability: float
    min_score: int
    max_history: int
    utc_offset_hours: int
    request_timeout: int
    max_retries: int

    @classmethod
    def from_env(cls) -> "Config":
        def _env_float(name: str, default: float) -> float:
            try:
                return float(os.getenv(name, default))
            except ValueError:
                return default

        def _env_int(name: str, default: int) -> int:
            try:
                return int(os.getenv(name, default))
            except ValueError:
                return default

        return cls(
            bot_token=os.getenv("BOT_TOKEN", ""),
            chat_id=os.getenv("CHAT_ID", ""),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
            used_messages_path=Path(os.getenv("USED_MESSAGES_PATH", "used_messages.json")),
            sleep_hour_start=_env_int("SLEEP_HOUR_START", 23),
            sleep_hour_end=_env_int("SLEEP_HOUR_END", 8),
            send_probability=_env_float("SEND_PROBABILITY", 0.25),
            min_score=_env_int("MIN_SCORE", 8),
            max_history=_env_int("MAX_HISTORY", 1000),
            utc_offset_hours=_env_int("UTC_OFFSET_HOURS", 7),  # Asia/Ho_Chi_Minh
            request_timeout=_env_int("REQUEST_TIMEOUT", 20),
            max_retries=_env_int("MAX_RETRIES", 2),
        )

    def validate(self) -> None:
        missing = [
            name
            for name, value in (
                ("BOT_TOKEN", self.bot_token),
                ("CHAT_ID", self.chat_id),
                ("GEMINI_API_KEY", self.gemini_api_key),
            )
            if not value
        ]
        if missing:
            raise SystemExit(
                f"Thiếu biến môi trường bắt buộc: {', '.join(missing)}. "
                "Xem README / .env.example để biết cách cấu hình."
            )


# =========================
# CONTENT PROMPTS
# =========================

CONTENT_PROMPTS = {
    "life_observation": "một quan sát sâu sắc về cuộc sống thường ngày",
    "relationship": "một sự thật hoặc góc nhìn về các mối quan hệ",
    "family": "một quan sát chân thực về gia đình",
    "friendship": "một góc nhìn về tình bạn",
    "psychology": "một insight tâm lý học về hành vi con người",
    "paradox": "một nghịch lý khiến người đọc phải suy nghĩ lại",
    "thought_experiment": "một câu hỏi hoặc giả định kích thích tư duy",
    "harsh_truth": "một sự thật khó nghe nhưng đúng",
    "modern_life": "một góc nhìn về cuộc sống hiện đại",
    "self_respect": "một góc nhìn về lòng tự trọng",
    "letting_go": "một góc nhìn về việc buông bỏ",
    "solitude": "một góc nhìn về việc ở một mình",
    "gratitude": "một góc nhìn về sự biết ơn",
    "aging": "một nhận thức về tuổi tác và thời gian",
    "humor_with_meaning": "một câu có chút hài hước nhưng mang ý nghĩa sâu sắc",
}

BANNED_PHRASES = [
    "càng lớn càng hiểu",
    "hãy cố lên",
    "thành công",
    "lãnh đạo",
    "kỷ luật",
    "động lực",
    "vượt qua tất cả",
    "mạnh mẽ lên",
    "nỗ lực",
    "không bao giờ bỏ cuộc",
]

BAD_STARTS = ["chúng ta", "người ta", "đôi khi", "có những", "ta vẫn"]

BANNED_TOPICS = ["tuổi thơ", "người cũ", "ký ức", "trưởng thành", "hồn nhiên"]

MIN_QUOTE_LENGTH = 20

QUOTE_PROMPT_TEMPLATE = """
Viết 1 quote tiếng Việt.

Chủ đề hôm nay:
{selected_prompt}

Định dạng ngẫu nhiên một trong các kiểu:
- one-liner
- paradox
- question
- contrast
- thought experiment

Ưu tiên các câu ngắn, dễ nhớ.

Mục tiêu:
Tạo một nội dung ngắn khiến người đọc dừng lại vài giây để suy nghĩ.

Yêu cầu:
- Tự nhiên
- Ngắn gọn
- Có chiều sâu
- Không màu mè
- Có thể là insight, nghịch lý hoặc góc nhìn mới

KHÔNG được bắt đầu bằng:
- Chúng ta
- Người ta
- Đôi khi
- Có những
- Ta vẫn

KHÔNG được nói về:
- tuổi thơ
- người cũ
- ký ức
- thời gian trôi
- trưởng thành

KHÔNG:
- quote nổi tiếng
- văn diễn giả
- văn LinkedIn
- self-help sáo rỗng
- dạy đời
- động lực kiểu mạng xã hội

Ưu tiên:
- thought experiment
- psychology
- paradox
- harsh truth
- observation

Chỉ trả về nội dung quote, không thêm giải thích hay chú thích.
""".strip()

SCORE_PROMPT_TEMPLATE = """
Đánh giá quote sau từ 1 đến 10.

Tiêu chí:
- đáng nhớ
- có ý mới
- không sáo rỗng
- ngắn gọn
- khiến người đọc phải suy nghĩ

Quote:
{quote}

Chỉ trả về 1 số, không thêm chữ nào khác.
""".strip()

DUPLICATE_PROMPT_TEMPLATE = """
Quote mới:
{quote}

{history_size} quote gần nhất:
{recent_quotes}

Nếu quote mới quá giống về ý tưởng, chủ đề hoặc thông điệp so với các quote
gần nhất, trả về: SIMILAR
Nếu đủ khác biệt, trả về: UNIQUE

Chỉ trả về đúng một từ (SIMILAR hoặc UNIQUE).
""".strip()


# =========================
# STATE (used_messages.json)
# =========================

def load_used_messages(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        log.warning("File %s không chứa một list, bỏ qua nội dung cũ.", path)
        return []
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("Không đọc được %s (%s), bắt đầu với danh sách rỗng.", path, exc)
        return []


def save_used_messages(path: Path, messages: list[str]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        tmp_path.replace(path)  # atomic on same filesystem
    except OSError as exc:
        log.error("Không lưu được state vào %s: %s", path, exc)


# =========================
# TIME WINDOW
# =========================

def local_now(offset_hours: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=offset_hours)


def in_sleep_window(hour: int, start: int, end: int) -> bool:
    """Khung giờ nghỉ có thể vòng qua nửa đêm (ví dụ 23 -> 8)."""
    if start == end:
        return False
    if start > end:
        return hour >= start or hour < end
    return start <= hour < end


# =========================
# GEMINI CALLS (with retry)
# =========================

def generate_with_retry(client: genai.Client, model: str, prompt: str, max_retries: int) -> str:
    last_exc: Optional[Exception] = None
    for attempt in range(1, max_retries + 2):
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            text = (response.text or "").strip()
            if not text:
                raise ValueError("Gemini trả về nội dung rỗng")
            return text
        except Exception as exc:  # noqa: BLE001 - retry on any API error
            last_exc = exc
            log.warning("Gemini call thất bại (lần %s/%s): %s", attempt, max_retries + 1, exc)
            if attempt <= max_retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Gemini call thất bại sau nhiều lần thử: {last_exc}")


def parse_score(text: str) -> int:
    digits = "".join(c for c in text if c.isdigit())
    if not digits:
        return 0
    try:
        return int(digits[:2])
    except ValueError:
        return 0


# =========================
# VALIDATION
# =========================

def fails_static_checks(quote: str) -> Optional[str]:
    """Trả về lý do fail (str) nếu quote không hợp lệ, None nếu ok."""
    if len(quote) < MIN_QUOTE_LENGTH:
        return "INVALID_LENGTH"

    lower = quote.lower()

    for phrase in BANNED_PHRASES:
        if phrase in lower:
            return f"BANNED_PHRASE:{phrase}"

    for start in BAD_STARTS:
        if lower.startswith(start):
            return f"REPETITIVE_STYLE:{start}"

    for topic in BANNED_TOPICS:
        if topic in lower:
            return f"REPETITIVE_TOPIC:{topic}"

    return None


# =========================
# TELEGRAM
# =========================

def send_telegram_message(bot_token: str, chat_id: str, text: str, timeout: int) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    res = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=timeout)
    log.info("Telegram response: %s %s", res.status_code, res.text)
    res.raise_for_status()


# =========================
# MAIN
# =========================

def main() -> int:
    cfg = Config.from_env()
    cfg.validate()

    now = local_now(cfg.utc_offset_hours)
    log.info("Bắt đầu chạy | giờ local: %s | ngày: %s", now.strftime("%H:%M"), now.strftime("%d/%m/%Y"))

    if in_sleep_window(now.hour, cfg.sleep_hour_start, cfg.sleep_hour_end):
        log.info("Đang trong khung giờ nghỉ (%02d:00-%02d:00), bỏ qua lần chạy này.",
                  cfg.sleep_hour_start, cfg.sleep_hour_end)
        return 0

    if random.random() < (1 - cfg.send_probability):
        log.info("Bỏ qua do random gate (send_probability=%.2f).", cfg.send_probability)
        return 0

    used_messages = load_used_messages(cfg.used_messages_path)
    client = genai.Client(api_key=cfg.gemini_api_key)

    content_type = random.choice(list(CONTENT_PROMPTS.keys()))
    selected_prompt = CONTENT_PROMPTS[content_type]
    log.info("Content type: %s", content_type)

    try:
        raw = generate_with_retry(
            client, cfg.gemini_model,
            QUOTE_PROMPT_TEMPLATE.format(selected_prompt=selected_prompt),
            cfg.max_retries,
        )
    except RuntimeError as exc:
        log.error("Không sinh được quote: %s", exc)
        return 1
    log.info("Quote thô: %s", raw)

    static_fail_reason = fails_static_checks(raw)
    if static_fail_reason:
        log.info("Quote không đạt kiểm tra tĩnh: %s", static_fail_reason)
        return 0

    if raw in used_messages:
        log.info("Quote trùng chính xác với lịch sử, bỏ qua.")
        return 0

    try:
        score_text = generate_with_retry(
            client, cfg.gemini_model,
            SCORE_PROMPT_TEMPLATE.format(quote=raw),
            cfg.max_retries,
        )
        score = parse_score(score_text)
    except RuntimeError as exc:
        log.warning("Không chấm điểm được, coi như score=0: %s", exc)
        score = 0
    log.info("Score: %s", score)

    if score < cfg.min_score:
        log.info("Score dưới ngưỡng (%s < %s), bỏ qua.", score, cfg.min_score)
        return 0

    recent_quotes = used_messages[-20:]
    if recent_quotes:
        try:
            dup_text = generate_with_retry(
                client, cfg.gemini_model,
                DUPLICATE_PROMPT_TEMPLATE.format(
                    quote=raw,
                    history_size=len(recent_quotes),
                    recent_quotes="\n\n".join(recent_quotes),
                ),
                cfg.max_retries,
            )
            if "SIMILAR" in dup_text.upper():
                log.info("Semantic duplicate, bỏ qua.")
                return 0
        except RuntimeError as exc:
            log.warning("Không kiểm tra được duplicate, tiếp tục mà không check: %s", exc)

    used_messages.append(raw)
    used_messages = used_messages[-cfg.max_history:]
    save_used_messages(cfg.used_messages_path, used_messages)

    date_str = now.strftime("%d/%m/%Y")
    final_text = f"{raw}\n\n━━━━━━━━━━━━\n📅 {date_str}"

    try:
        send_telegram_message(cfg.bot_token, cfg.chat_id, final_text, cfg.request_timeout)
    except requests.RequestException as exc:
        log.error("Gửi Telegram thất bại: %s", exc)
        return 1

    log.info("Đã gửi quote thành công.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
