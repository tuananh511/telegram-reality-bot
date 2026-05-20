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

# CHẶN 23H - 8H
if hour_vn >= 23 or hour_vn < 8:
    print("SLEEP WINDOW")
    exit()

# =========================
# EVENT CHECK (ALWAYS)
# =========================

special_event = None
event_prompt = f"""
Hôm nay là {date_str}.
Có sự kiện đặc biệt nào không (lễ tết Việt Nam, quốc tế, kỷ niệm lớn)?
Nếu có: 1 dòng ngắn <15 từ tiếng Việt.
Nếu không: NONE
"""

event_key = date_str

if event_key not in event_sent:
    try:
        event_response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=event_prompt
        )

        result = event_response.text.strip()
        print("EVENT RAW:", result)

        if result != "NONE" and len(result) > 3:
            special_event = result
            event_sent[event_key] = True

    except Exception as e:
        print("EVENT ERROR:", e)

# save event state
with open("event_sent.json", "w", encoding="utf-8") as f:
    json.dump(event_sent, f, ensure_ascii=False, indent=2)

# =========================
# QUOTE GENERATION
# =========================

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
Tìm 1 câu châm ngôn nổi tiếng bằng tiếng Anh, có trích dẫn tên tác giả.
Category: {category}

Yêu cầu:
- Dịch sang tiếng Việt tự nhiên
- Giữ tên người nói bằng tiếng Anh
- Format đúng:
"[câu tiếng Việt]" — [Tên người nói]
"""

try:
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    raw = response.text.strip()
    print("QUOTE RAW:", raw)

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

    # =========================
    # SEND LOGIC
    # =========================

    force_send = special_event is not None

    if not force_send and random.random() < 0.5:
        print("SKIP QUOTE")
        exit()

    final_text = raw

    if special_event:
        final_text = f"{special_event}\n\n{raw}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": final_text
    })

    print("SENT:", final_text)
    print("TELEGRAM:", res.status_code, res.text)

except Exception as e:
    print("ERROR:", e)
