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

content_types = [
    "life_observation",
    "relationship",
    "family",
    "friendship",
    "psychology",
    "paradox",
    "thought_experiment",
    "harsh_truth",
    "modern_life",
    "self_respect",
    "letting_go",
    "solitude",
    "gratitude",
    "aging",
    "humor_with_meaning"
]

content_type = random.choice(content_types)

# =========================
# PROMPT
# =========================

prompt = f"""
Viết 1 quote tiếng Việt.

Loại nội dung:
{content_type}

Yêu cầu:

- KHÔNG bắt đầu bằng:
  "Chúng ta"
  "Người ta"
  "Đôi khi"
  "Có những"
  "Ta vẫn"

- KHÔNG nói về:
  tuổi thơ
  người cũ
  ký ức
  thời gian trôi
  trưởng thành

- KHÔNG văn diễn giả
- KHÔNG văn LinkedIn
- KHÔNG self-help

- Ngắn
- Có punchline
- Có góc nhìn mới
- Có thể hơi nghịch lý

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

Chỉ trả về quote.
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

    bad_starts = [
    "chúng ta",
    "người ta",
    "đôi khi",
    "có những",
    "ta vẫn"
]

for start in bad_starts:
    if lower_raw.startswith(start):
        print("REPETITIVE STYLE")
        exit()

    banned_topics = [
    "tuổi thơ",
    "người cũ",
    "ký ức",
    "trưởng thành",
    "thời gian trôi",
    "hồn nhiên"
]

for topic in banned_topics:
    if topic in lower_raw:
        print("REPETITIVE TOPIC")
        exit()

    # =========================
    # DUPLICATE CHECK
    # =========================

    if raw in used_messages:
        print("DUPLICATE")
        exit()

    used_messages.append(raw)

    # chỉ giữ 300 quote gần nhất

    used_messages = used_messages[-300:]

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
