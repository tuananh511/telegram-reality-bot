import os
import json
import random
import requests
import google.generativeai as genai
from datetime import datetime, timezone, timedelta

# =========================
# ENV
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# LOAD MEMORY
# =========================

try:
    with open("used_messages.json", "r", encoding="utf-8") as f:
        used_messages = json.load(f)
except:
    used_messages = []

# =========================
# TIME (VN)
# =========================

hour_vn = (datetime.now(timezone.utc) + timedelta(hours=7)).hour

print("START BOT")
print("HOUR VN:", hour_vn)

# =========================
# TIME GATE
# =========================

if 7 <= hour_vn <= 20:

    # giữ random nhưng debug được
    if random.random() < 0.35:

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
Bạn là một người cố vấn thực tế.

Viết 10 câu ngắn tiếng Việt.

Category:
{category}

Yêu cầu:
- dưới 18 từ
- thực tế
- logic
- không motivational rác
- không emoji
- không dấu !

Cấm từ:
vũ trụ, ánh sáng, niềm tin, ước mơ, thành công, tỏa sáng
"""

        try:
            response = model.generate_content(prompt)

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

            payload = {
                "chat_id": CHAT_ID,
                "text": final_message
            }

            res = requests.post(url, json=payload)

            print("SENT:", final_message)
            print("TELEGRAM RESPONSE:", res.status_code, res.text)

        except Exception as e:
            print("ERROR:", e)

    else:
        print("SKIP (random)")

else:
    print("OUTSIDE TIME WINDOW")
