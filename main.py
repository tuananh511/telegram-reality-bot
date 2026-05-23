import os
import json
import random
import requests
from google import genai
from datetime import datetime, timezone, timedelta

# =========================
# ENV
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# LOAD STATE
# =========================

try:
    with open("used_messages.json", "r", encoding="utf-8") as f:
        used_messages = json.load(f)
except:
    used_messages = []

try:
    with open("event_sent.json", "r", encoding="utf-8") as f:
        event_sent = json.load(f)
except:
    event_sent = {}

# =========================
# TIME
# =========================

now_vn = datetime.now(timezone.utc) + timedelta(hours=7)
hour_vn = now_vn.hour
date_str = now_vn.strftime("%d/%m/%Y")

print("START BOT")
print("HOUR VN:", hour_vn)
print("DATE:", date_str)

# 23:00 -> 08:00 ngủ
if hour_vn >= 23 or hour_vn < 8:
    print("SLEEP WINDOW")
    exit()

# =========================
#  CHECK
# =========================

special_ = None
_key = date_str

_prompt = f"""
Hôm nay là {date_str}.

Có sự kiện đặc biệt nào không
(lễ tết Việt Nam, ngày quốc tế, ngày kỷ niệm lớn)?

Yêu cầu:
- đúng 1 dòng ngắn
- dưới 15 từ
- tự nhiên
- có thể thêm emoji nhẹ nếu phù hợp

Nếu không có:
NONE
"""

if _key not in _sent:
    try:
        _response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=_prompt
        )

        result = _response.text.strip()

        print(" RAW:")
        print(result)

        if result != "NONE" and len(result) > 3:
            special_ = result
            _sent[_key] = True

    except Exception as e:
        print("EVENT ERROR:", e)

# save state
with open("event_sent.json", "w", encoding="utf-8") as f:
    json.dump(event_sent, f, ensure_ascii=False, indent=2)

# =========================
# QUOTE GENERATION
# =========================

themes = [
    "gia đình",
    "sự trưởng thành",
    "cô đơn",
    "đàn ông trưởng thành",
    "sự tử tế",
    "bình yên",
    "áp lực cuộc sống",
    "sự cố gắng âm thầm",
    "thời gian",
    "tuổi trẻ",
    "chữa lành",
    "sự mất mát",
    "tình thân",
    "sự kiên trì",
    "những ngày mệt mỏi",
]

theme = random.choice(themes)

prompt = f"""
Hãy viết 1 đoạn quote ngắn bằng tiếng Việt.

Chủ đề hôm nay:
{theme}

Vibe:
- trưởng thành
- từng trải
- nhẹ nhưng thấm
- đời thực
- đàn ông trưởng thành
- gia đình
- cô đơn
- chữa lành
- sự cố gắng âm thầm
- bình yên
- áp lực cuộc sống
- hành trình lớn lên

Phong cách giống:
- caption Facebook sâu lắng
- suy nghĩ thật của người từng trải
- viết tự nhiên
- không triết lý sách vở
- giống một người thật đang suy ngẫm

Yêu cầu:
- KHÔNG quote nổi tiếng
- KHÔNG motivational sáo rỗng
- KHÔNG dạy đời
- KHÔNG hashtag
- KHÔNG emoji
- tối đa 5 dòng
- ngắn gọn
- phải tạo cảm giác chân thật
- wording tự nhiên như status Facebook chất lượng

TRÁNH:
- lặp ý tưởng cũ
- các câu kiểu "hãy cố gắng"
- productivity mindset
- self-help cliché

Ví dụ vibe:

"Áp lực lớn nhất của đàn ông,
nhiều khi là phải tỏ ra
mình vẫn ổn."

hoặc:

"Rồi sẽ có lúc bạn nhận ra...
thứ mình cần nhất
không phải hơn thua,
mà là một nơi để quay về."

hoặc:

"Đi nhiều rồi mới hiểu,
thứ khiến người ta mệt nhất
không phải công việc,
mà là lòng mình."

Chỉ trả về đúng nội dung quote.
"""

try:
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    raw = response.text.strip()

    print("QUOTE RAW:")
    print(raw)

    # =========================
    # VALIDATION
    # =========================

    if len(raw) < 20:
        print("INVALID")
        exit()

    # chống trùng exact wording
    if raw in used_messages:
        print("DUPLICATE")
        exit()

    used_messages.append(raw)

    # chỉ giữ 100 quote gần nhất
    used_messages = used_messages[-100:]

    with open("used_messages.json", "w", encoding="utf-8") as f:
        json.dump(
            used_messages,
            f,
            ensure_ascii=False,
            indent=2
        )

    # =========================
    # SEND DECISION
    # =========================

    force_send = special_event is not None

    # không có event -> random 50%
    if not force_send and random.random() < 0.8:
        print("SKIP RANDOM")
        exit()

    # =========================
    # BUILD MESSAGE
    # =========================

    def build_message(event, quote):
        parts = []

        if event:
            parts.append(
                f"🔥 *SỰ KIỆN HÔM NAY*\n{event}"
            )

        parts.append(quote)

        parts.append("━━━━━━━━━━━━")
        parts.append(f"📅 {date_str}")

        return "\n\n".join(parts)

    final_text = build_message(
        special_event,
        raw
    )

    # =========================
    # SEND TELEGRAM
    # =========================

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    res = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": final_text,
            "parse_mode": "Markdown"
        }
    )

    print("SENT:")
    print(final_text)

    print(
        "TELEGRAM:",
        res.status_code,
        res.text
    )

except Exception as e:
    print("ERROR:", e)
