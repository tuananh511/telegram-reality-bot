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

categories = [
    "anti overthinking",
    "financial awareness",
    "discipline",
    "systems thinking",
    "anti procrastination",
    "reality check"
]

category = random.choice(categories)
prompt = f"""
Viết 10 câu ngắn tiếng Việt.
Category: {category}
Yêu cầu:
- dưới 18 từ
- thực tế, logic
- không motivational rác
- không emoji
- không dấu !
- tránh từ sáo rỗng
"""

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    print("RAW RESPONSE:")
    print(response.text)

    raw_lines = response.text.split("\n")
    candidates = []
    banned_words = [
        "vũ trụ", "ánh sáng", "niềm tin",
        "ước mơ", "thành công", "tỏa sáng",
        "✨", "🔥", "❤️"
    ]

    for line in raw_lines:
        clean = line.strip("-•1234567890. ").strip()
        if len(clean) < 10:
            continue
        if len(clean) > 80:
            continue
        if clean in used_messages:
            continue
        if any(w in clean.lower() for w in banned_words):
            continue
        candidates.append(clean)

    print("CANDIDATES COUNT:", len(candidates))

    if not candidates:
        print("NO VALID MESSAGE")
        exit()

    final_message = random.choice(candidates)
    used_messages.append(final_message)
    used_messages = used_messages[-200:]

    with open("used_messages.json", "w", encoding="utf-8") as f:
        json.dump(used_messages, f, ensure_ascii=False, indent=2)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": final_message
    })
    print("SENT:", final_message)
    print("TELEGRAM:", res.status_code, res.text)

except Exception as e:
    print("ERROR:", e)
