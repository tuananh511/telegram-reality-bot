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
    "người ở lại",
    "sự phù hợp",
    "cảm giác được thấu hiểu",
    "sự cô đơn",
    "mất mát",
    "hy vọng",

    "sự tử tế",
    "sự biết ơn",
    "thời gian",
    "những điều giản dị",
    "một ngày bình thường",
    "những điều không còn như trước",

    "góc nhìn mới",
    "nghịch lý cuộc sống",
    "một ý tưởng có hai mặt",
    "điều đáng suy ngẫm",
    "sự thật khó nhận ra",
    "một nhận thức thay đổi cách nhìn",

    "bản ngã",
    "nỗi sợ",
    "sự bình yên",
    "buông bỏ",
    "kỳ vọng",
    "sự chấp nhận"
]

theme = random.choice(themes)

# =========================
# PROMPT
# =========================

prompt = f"""
Viết 1 đoạn quote ngắn bằng tiếng Việt.

Theme hôm nay:
{theme}

Mục tiêu:

Tạo ra một nội dung khiến người đọc dừng lại vài giây để suy nghĩ.

Nội dung có thể thuộc MỘT trong các dạng sau:

1. Một quan sát đời sống
2. Một cảm xúc chân thật
3. Một nghịch lý thú vị
4. Một góc nhìn mới
5. Một nhận thức bất ngờ
6. Một sự thật đơn giản nhưng ít ai để ý

Yêu cầu:

- tự nhiên
- tinh tế
- ngắn gọn
- có chiều sâu
- không màu mè

Cấm:

- quote nổi tiếng
- văn diễn giả
- văn LinkedIn
- văn lãnh đạo
- self-help sáo rỗng
- "hãy cố lên"
- "bạn sẽ thành công"
- "càng lớn càng hiểu"
- "một mình vượt qua tất cả"
- đạo lý quá trực diện

Ưu tiên:

- insight
- góc nhìn ngược
- nghịch lý
- suy nghĩ khiến người đọc phải nghĩ lại

Ví dụ tốt:

"Có những người không thay đổi.
Chỉ là đến một lúc nào đó,
họ không còn cố làm hài lòng tất cả nữa."

hoặc

"Nhiều thứ làm ta mệt,
không phải vì chúng nặng,
mà vì ta mang chúng quá lâu."

hoặc

"Có những cánh cửa không khóa.
Chỉ là mình đã quen đứng bên ngoài."

hoặc

"Càng cố thắng một cuộc tranh cãi,
người ta càng dễ thua một mối quan hệ."

hoặc

"Nỗi sợ thường lớn nhất
ngay trước khi ta bắt đầu."

hoặc

"Sự bình yên không đến khi mọi thứ hoàn hảo.
Nó đến khi ta thôi đòi hỏi mọi thứ phải hoàn hảo."

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
