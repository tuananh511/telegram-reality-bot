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

try:
    with open("used_messages.json", "r", encoding="utf-8") as f:
        used_messages = json.load(f)
except:
    used_messages = []

hour_vn = (datetime.now(timezone.utc) + timedelta(hours=7)).hour
print("START BOT")
print("HOUR VN:", hour_vn)

if not (7 <= hour_vn <= 20):
    print("OUTSIDE TIME WINDOW")
    exit()

# 50% xác suất gửi
if random.random() < 0.5:
    print("SKIPPED (50% chance)")
    exit()

categories = [
    "stoicism",
    "discipline and focus",
    "reality and self-awareness",
    "wealth and ambition",
    "time and priorities",
    "mental toughness"
]

category = random.choice(categories)
prompt = f"""
Tìm 1 câu châm ngôn nổi tiếng bằng tiếng Anh, có trích dẫn rõ tên người nói.
Category: {category}
Yêu cầu:
- Dịch câu đó sang tiếng Việt, tự nhiên, không cứng nhắc
- Giữ tên người nói bằng tiếng Anh
- Format trả về đúng như sau, không thêm gì khác:
"[câu tiếng Việt]" — [Tên người nói]
Ví dụ:
"Chúng ta khổ sở không phải vì sự việc, mà vì cách ta nhìn nhận nó." — Marcus Aurelius
"""

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    print("RAW RESPONSE:")
    print(response.text)

    raw = response.text.strip()

    # Validate format cơ bản
    if "—" not in raw or len(raw) < 20:
        print("INVALID FORMAT")
        exit()

    if raw in used_messages:
        print("DUPLICATE")
        exit()

    used_messages.append(raw)
    used_messages = used_messages[-200:]

    with open("used_messages.json", "w", encoding="utf-8") as f:
        json.dump(used_messages, f, ensure_ascii=False, indent=2)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": raw
    })
    print("SENT:", raw)
    print("TELEGRAM:", res.status_code, res.text)

except Exception as e:
    print("ERROR:", e)
