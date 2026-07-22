import os
import json
import random
import requests
from google import genai
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# MODEL FALLBACK LIST
# =========================
# Thứ tự ưu tiên: model đang dùng trước, sau đó tới các bản flash-lite khác
# còn "Stable" trên https://ai.google.dev/gemini-api/docs/models
MODEL_CANDIDATES = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash-lite",
]

MODELS_DOC_URL = "https://ai.google.dev/gemini-api/docs/models"


def is_model_error(e) -> bool:
    """Đoán xem lỗi có phải do model bị đổi tên / ngừng hỗ trợ hay không."""
    msg = str(e).lower()
    if "model" not in msg:
        return False
    keywords = [
        "not_found", "404", "not found", "deprecated",
        "unsupported", "not supported", "invalid",
        "does not exist", "permission",
    ]
    return any(k in msg for k in keywords)


def send_telegram_text(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, json={"chat_id": CHAT_ID, "text": text})
    print("TELEGRAM ALERT:", res.status_code, res.text)


def notify_model_failure(last_error):
    """Gửi cảnh báo lên Telegram khi TẤT CẢ model trong danh sách đều lỗi do model."""
    options_text = "\n".join(f"• {m}" for m in MODEL_CANDIDATES)
    text = (
        "⚠️ Bot lỗi do model Gemini không dùng được nữa.\n\n"
        f"Đã thử các model sau nhưng đều lỗi:\n{options_text}\n\n"
        f"👉 Xem danh sách model mới nhất tại:\n{MODELS_DOC_URL}\n\n"
        "Hãy vào trang trên, tìm các model thuộc nhóm \"Flash-Lite\" đang "
        "\"Stable\", rồi cập nhật MODEL_CANDIDATES trong main.py.\n\n"
        f"Chi tiết lỗi cuối cùng:\n{last_error}"
    )
    send_telegram_text(text)


def generate_with_fallback(prompt: str) -> str:
    """Gọi Gemini, tự động thử lần lượt các model trong MODEL_CANDIDATES.
    Nếu tất cả đều lỗi do model -> báo Telegram rồi raise lỗi cuối cùng.
    Nếu lỗi không liên quan tới model (network, quota...) -> raise ngay,
    không thử tiếp (tránh spam request khi không cần)."""
    last_error = None
    for model_name in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if model_name != MODEL_CANDIDATES[0]:
                print(f"NOTE: fallback thanh cong voi model {model_name}")
            return response.text.strip()
        except Exception as e:
            last_error = e
            if is_model_error(e):
                print(f"MODEL ERROR voi {model_name}: {e}")
                continue  # thử model tiếp theo trong danh sách
            else:
                # lỗi khác (mạng, quota, key sai...) -> không phải lúc để đổi model
                raise
    # Nếu chạy tới đây nghĩa là mọi model trong danh sách đều lỗi do model
    notify_model_failure(last_error)
    raise last_error


# =========================
# LOAD USED MESSAGES
# =========================
try:
    with open("used_messages.json", "r", encoding="utf-8") as f:
        used_messages = json.load(f)
except:
    used_messages = []

# =========================
# VN TIME
# =========================
now_vn = datetime.now(timezone.utc) + timedelta(hours=7)
hour_vn = now_vn.hour
date_str = now_vn.strftime("%d/%m/%Y")

print("START BOT")
print("TIME VN:", now_vn.strftime("%H:%M"))
print("DATE:", date_str)

# =========================
# SLEEP WINDOW
# =========================
if hour_vn >= 23 or hour_vn < 8:
    print("SLEEP WINDOW")
    exit()

# =========================
# RANDOM SEND
# =========================
if random.random() < 0.75:
    print("SKIP RANDOM")
    exit()

# =========================
# CONTENT TYPE
# =========================
content_prompts = {
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
    "humor_with_meaning": "một câu có chút hài hước nhưng mang ý nghĩa sâu sắc"
}

content_type = random.choice(list(content_prompts.keys()))
selected_prompt = content_prompts[content_type]

# =========================
# PROMPT
# =========================
prompt = f"""
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

Ví dụ:
"Nỗi sợ lớn nhất của nhiều người
không phải thất bại,
mà là bị người khác thấy mình thất bại."

hoặc

"Tiền không mua được thời gian.
Nhưng thiếu tiền,
người ta phải bán rất nhiều thời gian."

hoặc

"Càng cố chứng minh mình đúng,
càng ít người muốn lắng nghe."

hoặc

"Im lặng không phải lúc nào cũng là bình yên.
Đôi khi nó chỉ là một cuộc tranh cãi đã quá mệt để tiếp tục."

Chỉ trả về nội dung quote.
"""

# =========================
# GENERATE
# =========================
try:
    raw = generate_with_fallback(prompt)

    print("CONTENT TYPE:", content_type)
    print("RAW:")
    print(raw)

    # =========================
    # AI SCORE
    # =========================
    score_prompt = f"""
Đánh giá quote sau từ 1 đến 10.

Tiêu chí:
- đáng nhớ
- có ý mới
- không sáo rỗng
- ngắn gọn
- khiến người đọc phải suy nghĩ

Quote:
{raw}

Chỉ trả về 1 số.
"""

    score_text = generate_with_fallback(score_prompt)

    try:
        score = int(''.join(c for c in score_text if c.isdigit())[:2])
    except:
        score = 0

    print("SCORE:", score)

    if score < 8:
        print("LOW SCORE")
        exit()

    # =========================
    # SEMANTIC DUPLICATE
    # =========================
    recent_quotes = "\n\n".join(used_messages[-20:])

    duplicate_prompt = f"""
Quote mới:
{raw}

20 quote gần nhất:
{recent_quotes}

Nếu quote mới quá giống về ý tưởng,
chủ đề hoặc thông điệp:
Trả về:
SIMILAR

Nếu đủ khác biệt:
Trả về:
UNIQUE
"""

    dup_result = generate_with_fallback(duplicate_prompt).strip().upper()
    print("UNIQUENESS:", dup_result)

    if "SIMILAR" in dup_result:
        print("SEMANTIC DUPLICATE")
        exit()

    # =========================
    # VALIDATION
    # =========================
    if len(raw) < 20:
        print("INVALID LENGTH")
        exit()

    lower_raw = raw.lower()

    banned_phrases = [
        "càng lớn càng hiểu",
        "hãy cố lên",
        "thành công",
        "lãnh đạo",
        "kỷ luật",
        "động lực",
        "vượt qua tất cả",
        "mạnh mẽ lên",
        "nỗ lực",
        "không bao giờ bỏ cuộc"
    ]
    for phrase in banned_phrases:
        if phrase in lower_raw:
            print("BANNED PHRASE:", phrase)
            exit()

    bad_starts = ["chúng ta", "người ta", "đôi khi", "có những", "ta vẫn"]
    for start in bad_starts:
        if lower_raw.startswith(start):
            print("REPETITIVE STYLE")
            exit()

    banned_topics = ["tuổi thơ", "người cũ", "ký ức", "trưởng thành", "hồn nhiên"]
    for topic in banned_topics:
        if topic in lower_raw:
            print("REPETITIVE TOPIC")
            exit()

    if raw in used_messages:
        print("DUPLICATE")
        exit()

    used_messages.append(raw)
    used_messages = used_messages[-1000:]

    with open("used_messages.json", "w", encoding="utf-8") as f:
        json.dump(used_messages, f, ensure_ascii=False, indent=2)

    final_text = f"""
{raw}

━━━━━━━━━━━━
📅 {date_str}
""".strip()

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, json={"chat_id": CHAT_ID, "text": final_text})
    print("SENT")
    print("TELEGRAM:", res.status_code, res.text)

except Exception as e:
    print("ERROR:", e)
