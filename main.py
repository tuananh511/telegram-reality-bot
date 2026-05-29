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

# =========================
# TIME
# =========================

now_vn = datetime.now(timezone.utc) + timedelta(hours=7)
hour_vn = now_vn.hour
date_str = now_vn.strftime("%d/%m/%Y")

print("START BOT")
print("HOUR VN:", hour_vn)
print("DATE:", date_str)

# =========================
# SLEEP WINDOW
# =========================

# ngủ từ 23h -> 8h

if hour_vn >= 23 or hour_vn < 8:
    print("SLEEP WINDOW")
    exit()

# =========================
# THEME RANDOMIZER
# =========================

themes = [
    "gia đình",
    "tuổi thơ",
    "tình bạn",
    "sự tử tế",
    "bình yên",
    "trưởng thành",
    "thời gian",
    "tuổi trẻ",
    "chữa lành",
    "một ngày bình thường",
    "niềm vui nhỏ",
    "cảm giác được về nhà",
    "sự cố gắng âm thầm",
    "hành trình lớn lên",
    "đêm khuya và suy nghĩ",
    "cà phê và cuộc sống",
    "những người đã từng gặp",
    "sự biết ơn",
    "những điều giản dị",
    "sự cô đơn",
    "áp lực cuộc sống",
    "mất mát",
    "hy vọng",
    "sự nhẹ nhõm",
    "những ngày mệt mỏi",
    "mùa mưa",
    "thành phố về đêm",
    "những cuộc trò chuyện ngắn",
    "sự bình tĩnh",
    "những điều không còn như trước",
    "tình yêu trưởng thành",
    "những mối quan hệ tốt",
    "cảm giác được thấu hiểu",
    "đúng người sai thời điểm",
    "sự phù hợp",
    "người ở lại"
]

theme = random.choice(themes)

# =========================
# QUOTE GENERATION
# =========================

prompt = f"""
Hãy viết 1 đoạn quote ngắn bằng tiếng Việt.

Theme hôm nay:
{theme}

Phong cách:
- tự nhiên
- đời thực
- cảm xúc nhẹ
- đôi khi sâu lắng
- đôi khi bình yên
- đôi khi tích cực
- giống một suy nghĩ thật trong cuộc sống
- không cần lúc nào cũng buồn

Tone tham khảo:
- caption Facebook sâu lắng
- suy nghĩ trong đêm
- một điều nhận ra sau nhiều năm
- một khoảnh khắc nhỏ trong cuộc sống
- cảm giác trưởng thành dần
- sự tử tế
- những điều giản dị

Yêu cầu:

- KHÔNG quote nổi tiếng
- KHÔNG motivational sáo rỗng
- KHÔNG dạy đời
- KHÔNG kiểu "hãy cố lên"
- tránh lặp lại motif "một mình vượt qua tất cả"
- có thể liên quan tới tình cảm hoặc các mối quan hệ, nhưng theo hướng trưởng thành và tinh tế
- KHÔNG hashtag
- KHÔNG emoji
- wording tự nhiên như người thật viết
- tối đa 5 dòng
- ngắn gọn
- đọc có cảm giác thật

Ví dụ vibe:

"Càng lớn mới hiểu,
nhiều người không rời đi vì hết thương,
mà vì đã quá mệt."

hoặc:

"Có những ngày bình thường thôi,
nhưng sau này nhớ lại
lại thấy rất đẹp."

hoặc:

"Thứ làm người ta nhẹ lòng nhất,
đôi khi chỉ là có ai đó hỏi:
'Hôm nay ổn không?'"

hoặc:

"Ngay cả khi bạn ở trạng thái tốt nhất,
bạn vẫn sẽ không đủ tốt
với người không phù hợp."

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

    # =========================
    # VALIDATION
    # =========================

    if len(raw) < 20:
        print("INVALID")
        exit()

    # =========================
    # DUPLICATE CHECK
    # =========================

    if raw in used_messages:
        print("DUPLICATE")
        exit()

    used_messages.append(raw)

    # giữ 100 quote gần nhất

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

    # 25% chance gửi

    if random.random() < 0.75:
        print("SKIP RANDOM")
        exit()

    # =========================
    # BUILD MESSAGE
    # =========================

    final_text = f"""
{raw}

━━━━━━━━━━━━

📅 {date_str}
""".strip()

    # =========================
    # SEND TELEGRAM
    # =========================

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    res = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": final_text
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
