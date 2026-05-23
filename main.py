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

# 23h -> 8h stop
if hour_vn >= 23 or hour_vn < 8:
    print("SLEEP WINDOW")
    exit()

# =========================
# EVENT CHECK
# =========================

special_event = None
event_key = date_str

event_prompt = f"""
Hôm nay là {date_str}.

Có sự kiện đặc biệt nào không
(lễ Việt Nam, ngày quốc tế, kỷ niệm lớn)?

Nếu có:
- đúng 1 dòng
- tiếng Việt
- dưới 15 từ

Nếu không có:
NONE
"""

if event_key not in event_sent:
    try:
        event_response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=event_prompt
        )

        result = event_response.text.strip()

        print("EVENT RAW:")
        print(result)

        if result != "NONE" and len(result) > 3:
            special_event = result
            event_sent[event_key] = True

    except Exception as e:
        print("EVENT ERROR:", e)

with open("event_sent.json", "w", encoding="utf-8") as f:
    json.dump(event_sent, f, ensure_ascii=False, indent=2)

# =========================
# THEME RANDOMIZER
# =========================

themes = [
    "gia đình",
    "trưởng thành",
    "đàn ông",
    "cô đơn",
    "áp lực cuộc sống",
    "sự tử tế",
    "thời gian",
    "tuổi trẻ",
    "sự cố gắng âm thầm",
    "bình yên",
    "chữa lành",
    "mất mát",
    "hành trình lớn lên",
    "trách nhiệm",
    "đêm khuya và suy nghĩ"
]

theme = random.choice(themes)

# =========================
# QUOTE GENERATION
# =========================

prompt = f"""
Hãy viết 1 đoạn quote ngắn bằng tiếng Việt.

Vibe chính hôm nay:
{theme}

Phong cách:
- trưởng thành
- từng trải
- đời thực
- sâu nhưng tự nhiên
- hơi giống caption Facebook hay
- cảm giác thật, không sách vở

Tone tham khảo:
- gia đình
- cô đơn
- đàn ông trưởng thành
- sự cố gắng âm thầm
- áp lực cuộc sống
- chữa lành
- bình yên
- thời gian
- hành trình lớn lên

Yêu cầu:

- KHÔNG quote nổi tiếng
- KHÔNG motivational sáo rỗng
- KHÔNG dạy đời
- KHÔNG kiểu "hãy cố lên"
- KHÔNG hashtag
- KHÔNG emoji
- wording tự nhiên như người từng trải viết
- tối đa 5 dòng
- ngắn gọn
- đọc có cảm giác thật

Ví dụ vibe:

"Áp lực lớn nhất của đàn ông,
nhiều khi là phải tỏ ra mình vẫn ổn."

hoặc:

"Rồi sẽ có lúc bạn nhận ra...
thứ mình cần nhất
không phải là hơn thua,
mà là một nơi để quay về."

Chỉ trả về đúng nội dung quote.
"""

try:

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    raw = response.text.strip()

    print("THEME:", theme)
    print("QUOTE RAW:")
    print(raw)

    # validation

    if len(raw) < 20:
        print("INVALID")
        exit()

    # duplicate

    if raw in used_messages:
        print("DUPLICATE")
        exit()

    used_messages.append(raw)

    # giữ 100 quote gần nhất

    used_messages = used_messages[-100:]

    with open("used_messages.json", "w", encoding="utf-8") as f:
        json.dump(used_messages, f, ensure_ascii=False, indent=2)

    # =========================
    # SEND DECISION
    # =========================

    force_send = special_event is not None

    if not force_send and random.random() < 0.85:
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

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

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
