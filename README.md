# Daily Quote Telegram Bot
> Send daily reality-based quotes via Telegram.

![Release](https://img.shields.io/github/v/release/tuananh511/telegram-reality-bot)
![License](https://img.shields.io/github/license/tuananh511/telegram-reality-bot)
![Build](https://img.shields.io/github/actions/workflow/status/tuananh511/telegram-reality-bot/main.yml)

## Overview
Bot Telegram tự động gửi những đoạn quote ngắn bằng tiếng Việt mang cảm giác sâu lắng, trưởng thành và đời thực — giống các caption chữa lành, suy ngẫm về cuộc sống, gia đình, cô đơn, thời gian và hành trình trưởng thành. Nếu trong ngày có sự kiện đặc biệt (lễ, ngày kỷ niệm, sự kiện quốc tế...), bot tự động gắn thêm phần thông báo phía trên quote. Lịch chạy được điều khiển bởi **cron-job.org**, gọi tới GitHub Actions API (`workflow_dispatch`) theo chu kỳ đặt trước — bot vẫn thực thi trên GitHub-hosted runner nên không cần VPS hay server riêng.

## Features
- Gửi quote theo lịch, kích hoạt bởi cron-job.org qua GitHub Actions `workflow_dispatch`
- Chống trùng nội dung
- Tự động phát hiện sự kiện đặc biệt trong ngày và gắn thông báo
- Random tần suất gửi để tránh spam (15% khi không có event, luôn gửi khi có event)
- Không chạy trong khung giờ nghỉ (23:00 → 08:00)
- Sinh quote bằng Google Gemini API (`gemini-3.1-flash-lite`), theme random (gia đình, trưởng thành, cô đơn, thời gian, chữa lành, v.v.)
- Không cần VPS, chi phí gần như bằng 0

## Installation
```bash
git clone https://github.com/tuananh511/telegram-reality-bot.git
cd telegram-reality-bot
pip install -r requirements.txt
```

Cần thiết lập các biến môi trường (dùng GitHub Secrets):
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `GEMINI_API_KEY`

Trên GitHub: **Settings → Actions → General → Workflow permissions**, đảm bảo workflow được phép chạy qua `workflow_dispatch`. Sau đó tạo một Personal Access Token (scope `repo`/`workflow`) để cron-job.org dùng gọi API.

## Usage
Chạy thủ công (test cục bộ):
```bash
python main.py
```

Chạy tự động: cron-job.org được cấu hình gọi định kỳ tới endpoint:
POST https://api.github.com/repos/tuananh511/telegram-reality-bot/actions/workflows/main.yml/dispatches
kèm header `Authorization: Bearer <PAT>` và body `{"ref": "main"}`. Mỗi lần chạy, bot tự kiểm tra khung giờ (08:00–23:00), sự kiện trong ngày, sinh quote mới, kiểm tra trùng, và quyết định gửi. State được lưu trong `used_messages.json` và `event_sent.json`.

## Roadmap
- [ ] Habit tracking
- [ ] Reminder tích hợp
- [ ] AI companion layer
- [ ] Personal assistant layer
- [ ] Hỗ trợ multi-user (cần VPS/webhook server 24/7)

## License
MIT
