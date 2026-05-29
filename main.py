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

# ngủ từ 23h -> 8h

if hour_vn >= 23 or hour_vn < 8:
    print("SLEEP WINDOW")
    exit()

# =========================
# RANDOM SEND
# =========================

# chỉ có 25% gửi

if random.random() < 0.75:
    print("SKIP RANDOM")
    exit()

# =========================
# THEMES
# =========================

themes = [
    "gia đình",
    "tuổi thơ",
    "sự trưởng thành",
    "tình bạn",
    "tình yêu trưởng thành",
    "đúng người sai thời điểm",
    "sự phù hợp",
    "người ở lại",
    "cảm giác được thấu hiểu",
    "những ngày mệt mỏi",
    "một ngày bình thường",
    "sự tử tế",
    "sự bình yên",
    "thời gian",
    "tuổi trẻ",
    "những điều giản dị",
    "niềm vui nhỏ",
    "mất mát",
    "hy vọng",
    "sự cô đơn",
    "đêm khuya và suy nghĩ",
    "những điều không còn như trước",
    "cảm giác được về nhà",
    "những người từng gặp",
    "sự biết ơn",
    "mùa mưa",
    "thành phố về đêm",
    "những cuộc trò chuyện ngắn",
    "áp lực cuộc sống",
    "sự nhẹ nhõm",
    "hành trình lớn lên"
]

theme = random.choice(themes)

# =========================
# PROMPT
# =========================

prompt = f"""
Hãy viết 1 đoạn quote ngắn bằng tiếng Việt.

Theme hôm nay:
{theme}

Mục tiêu:
Tạo cảm giác như một người thật từng trải đang viết ra một suy nghĩ thật.

Phong cách:
- tự nhiên
- đời thường
- nhẹ
- tinh tế
- có chiều sâu
- cảm xúc thật
- đôi khi buồn
- đôi khi bình yên
- đôi khi chỉ là một sự nhận ra nhỏ

Tone:
- giống caption Facebook hay thật sự
- giống suy nghĩ lúc khuya
- giống một điều hiểu ra khi lớn lên
- không cần quá triết lý

Yêu cầu:

- KHÔNG quote nổi tiếng
- KHÔNG motivational sáo rỗng
- KHÔNG văn "càng lớn càng hiểu"
- KHÔNG kiểu diễn giả / dạy đời
- KHÔNG kiểu quote Facebook đại trà
- KHÔNG văn LinkedIn / lãnh đạo / thành công
- tránh kết luận đạo lý trực diện
- tránh motif "một mình vượt qua tất cả"
- ưu tiên cảm giác thật hơn là triết lý
- có thể liên quan tới tình cảm hoặc các mối quan hệ
- wording phải tự nhiên như người thật viết
- không hashtag
- không emoji
- tối đa 5 dòng
- ngắn gọn
- dễ đọc
- không dùng quá nhiều dấu "..."

Ví dụ vibe tốt:

"Có những người,
sau này nhớ lại
thứ tiếc nhất
không phải là mất nhau,
mà là lúc đó đã không hiểu nhau hơn."

hoặc:

"Lớn lên rồi mới thấy,
được ăn cơm cùng gia đình
một bữa đầy đủ
cũng là một loại hạnh phúc."

hoặc:

"Nhiều chuyện lúc nhỏ tưởng là bình thường,
sau này mới hiểu
đó là vì đã có người âm thầm lo giúp mình."

hoặc:

"Có những ngày bình thường thôi,
nhưng sau này nhớ lại
lại thấy rất đẹp."

hoặc:

"Thứ làm người ta nhẹ lòng nhất,
đôi khi chỉ là có ai đó hỏi:
'Hôm nay ổn không?'"

Chỉ trả về nội dung quote.
"""

# =========================
# GENERATE
# =========================

try:

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    raw = response.text.strip()

    print("THEME:", theme)
    print("RAW:")
    print(raw)

    # =========================
    # VALIDATION
    # =========================

    if len(raw) < 20:
        print("INVALID LENGTH")
        exit()

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

    lower_raw = raw.lower()

    for phrase in banned_phrases:
        if phrase in lower_raw:
            print("BANNED PHRASE:", phrase)
            exit()

    # =========================
    # DUPLICATE CHECK
    # =========================

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
    # FINAL MESSAGE
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

    print("SENT")

    print(
        "TELEGRAM:",
        res.status_code,
        res.text
    )

except Exception as e:
    print("ERROR:", e)
