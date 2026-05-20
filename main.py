import os
import json
import random
import requests
import google.generativeai as genai
from datetime import datetime

print("START BOT")
print("RAW:", response.text)
print("CANDIDATES:", len(candidates))

# =========================
# ENV
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =========================
# GEMINI
# =========================

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# LOAD MEMORY
# =========================

with open("used_messages.json", "r", encoding="utf-8") as f:
    used_messages = json.load(f)

# =========================
# TIME VN
# =========================

hour_vn = datetime.utcnow().hour + 7

# =========================
# ONLY 7H-20H
# =========================

if 7 <= hour_vn <= 20:

    # 35% chance mỗi giờ
    if random.random() < 0.35:

        # =========================
        # RANDOM CATEGORY
        # =========================

        categories = [
            "anti overthinking",
            "financial awareness",
            "discipline",
            "systems thinking",
            "anti procrastination",
            "reality check"
        ]

        category = random.choice(categories)

        # =========================
        # PROMPT
        # =========================

        prompt = f"""
Bạn là một người cố vấn thực tế.

Hãy viết 10 tin nhắn ngắn bằng tiếng Việt.

Category:
{category}

Yêu cầu:
- dưới 18 từ
- hơi lạnh
- logic
- actionable
- thực tế
- không fake deep
- không motivational rác
- không emoji
- không dấu !
- không thơ văn

Cấm dùng từ:
- vũ trụ
- ánh sáng
- niềm tin
- tỏa sáng
- thành công
- ước mơ

Viết như đang nhắc một người thông minh nhưng đang tự sabotage bản thân.
"""

        # =========================
        # GENERATE
        # =========================

        try:

            response = model.generate_content(prompt)

            raw_lines = response.text.split("\n")

            # =========================
            # CLEAN
            # =========================

            candidates = []

            banned_words = [
                "vũ trụ",
                "ánh sáng",
                "niềm tin",
                "ước mơ",
                "thành công",
                "tỏa sáng",
                "✨",
                "🔥",
                "❤️"
            ]

            for line in raw_lines:

                clean = line.strip("-•1234567890. ")

                if len(clean) < 10:
                    continue

                if len(clean) > 80:
                    continue

                if clean in used_messages:
                    continue

                if any(word in clean.lower() for word in banned_words):
                    continue

                candidates.append(clean)

            # =========================
            # FALLBACK
            # =========================

            if not candidates:
                exit()

            # =========================
            # PICK
            # =========================

            final_message = random.choice(candidates)

            # =========================
            # SAVE MEMORY
            # =========================

            used_messages.append(final_message)

            # giữ 200 message gần nhất
            used_messages = used_messages[-200:]

            with open(
                "used_messages.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    used_messages,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            # =========================
            # SEND TELEGRAM
            # =========================

            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

            payload = {
                "chat_id": CHAT_ID,
                "text": final_message
            }

            requests.post(url, json=payload)

            print("SENT:", final_message)

        except Exception as e:

            print("ERROR:", e)

else:

    print("Outside allowed hours")
