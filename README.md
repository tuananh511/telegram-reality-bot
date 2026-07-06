# Daily Quote Telegram Bot

Bot Telegram tự động sinh và gửi những quote ngắn bằng tiếng Việt, mang tone trưởng thành, đời thực và có chút chiều sâu — kiểu caption "chữa lành", suy ngẫm về cuộc sống, gia đình, cô đơn, thời gian, tuổi trẻ...

Nội dung được sinh bằng Google Gemini API dựa trên một bộ prompt cố định (chủ đề, style, danh sách từ/chủ đề bị chặn...). Bot tự chấm điểm và tự kiểm tra trùng lặp trước khi gửi, nên không phải quote nào sinh ra cũng được gửi đi.

Script được thiết kế để chạy **một lần rồi thoát** (one-shot), và được gọi lặp lại theo lịch bằng **cronjob** (hoặc systemd timer, Task Scheduler...) trên một máy chủ/VPS của riêng bạn — không phụ thuộc vào GitHub Actions hay bất kỳ nền tảng CI/CD nào.

---

## Tính năng

- Tự sinh quote tiếng Việt bằng Gemini, theo nhiều chủ đề/theme khác nhau
- Tự chấm điểm nội dung, chỉ gửi nếu đạt ngưỡng
- Chống trùng lặp 2 lớp: trùng chính xác (so khớp text) + trùng ngữ nghĩa (AI so sánh ý tưởng với lịch sử gần nhất)
- Bộ lọc tĩnh: chặn cụm từ sáo rỗng, chủ đề lặp, kiểu mở đầu lặp
- Không gửi trong khung giờ nghỉ (mặc định 23:00 → 08:00, tuỳ chỉnh được)
- Random tần suất gửi để tránh spam, tuỳ chỉnh được qua biến môi trường
- Toàn bộ hành vi (ngưỡng điểm, khung giờ, xác suất gửi, model Gemini...) cấu hình qua biến môi trường, không cần sửa code
- Không yêu cầu framework nặng, không cần webhook — chỉ cần Python + cron

## Cách hoạt động

Mỗi lần script được chạy (do cron gọi):

1. Kiểm tra giờ hiện tại có nằm trong khung giờ nghỉ không → nếu có, dừng.
2. Random theo `SEND_PROBABILITY` để quyết định có tiếp tục hay không → nếu không trúng, dừng.
3. Chọn ngẫu nhiên một theme, sinh quote bằng Gemini.
4. Chạy qua bộ lọc tĩnh (độ dài, từ cấm, chủ đề cấm, kiểu mở đầu lặp).
5. Nếu quote trùng chính xác với lịch sử → dừng.
6. Gửi quote cho Gemini tự chấm điểm 1-10, nếu dưới `MIN_SCORE` → dừng.
7. So sánh ngữ nghĩa với các quote gần nhất, nếu quá giống → dừng.
8. Nếu qua hết các bước trên: lưu quote vào lịch sử (`used_messages.json`) và gửi qua Telegram.

Vì state được lưu vào một file JSON trên đĩa, bot cần chạy trên một máy có ổ đĩa bền (VPS, máy chủ cá nhân, Raspberry Pi...) để lịch sử chống trùng không bị mất giữa các lần chạy.

## Cài đặt

### 1. Yêu cầu

- Python 3.10+
- Một bot Telegram (tạo qua [@BotFather](https://t.me/BotFather)) và token của nó
- Chat ID (người dùng, group, hoặc channel) mà bot sẽ gửi quote tới
- Một API key của Google Gemini ([Google AI Studio](https://aistudio.google.com/))

### 2. Clone và cài dependencies

```bash
git clone https://github.com/tuananh511/telegram-reality-bot.git
cd telegram-reality-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường

Copy `.env.example` thành `.env` và điền giá trị thật:

```bash
cp .env.example .env
```

Xem chi tiết từng biến (và giá trị mặc định) trong [`.env.example`](.env.example). Ba biến bắt buộc là `BOT_TOKEN`, `CHAT_ID`, `GEMINI_API_KEY` — thiếu bất kỳ biến nào script sẽ báo lỗi và dừng ngay, không chạy ngầm với config sai.

### 4. Chạy thử

```bash
set -a && source .env && set +a
python3 main.py
```

Xem log in ra console để biết script đã dừng ở bước nào (sleep window, random gate, score thấp, trùng lặp...) hoặc đã gửi thành công.

## Chạy định kỳ bằng cronjob

Đây là cách vận hành chính thức của project — không dùng GitHub Actions.

### Cách 1: cron trực tiếp với file `.env`

Tạo một script wrapper nhỏ, ví dụ `run.sh`:

```bash
#!/usr/bin/env bash
cd /path/to/telegram-reality-bot
set -a
source .env
set +a
/path/to/telegram-reality-bot/venv/bin/python3 main.py >> bot.log 2>&1
```

```bash
chmod +x run.sh
```

Thêm vào crontab (`crontab -e`), ví dụ chạy mỗi 2 giờ:

```cron
0 */2 * * * /path/to/telegram-reality-bot/run.sh
```

### Cách 2: systemd timer (khuyến khích nếu VPS dùng systemd)

`/etc/systemd/system/quote-bot.service`:

```ini
[Unit]
Description=Daily Quote Telegram Bot

[Service]
Type=oneshot
WorkingDirectory=/path/to/telegram-reality-bot
EnvironmentFile=/path/to/telegram-reality-bot/.env
ExecStart=/path/to/telegram-reality-bot/venv/bin/python3 main.py
```

`/etc/systemd/system/quote-bot.timer`:

```ini
[Unit]
Description=Run quote-bot every 2 hours

[Timer]
OnCalendar=*-*-* 0/2:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now quote-bot.timer
```

> Tần suất chạy cron/timer và `SEND_PROBABILITY` cùng nhau quyết định số lượng tin nhắn thực tế mỗi ngày. Ví dụ chạy mỗi 2 giờ (12 lần/ngày, trong đó ~7 lần rơi vào khung hoạt động 08:00-23:00) với `SEND_PROBABILITY=0.25` thì trung bình gửi khoảng 1-2 quote/ngày.

## Biến môi trường

Xem đầy đủ và có giải thích trong [`.env.example`](.env.example). Tóm tắt:

| Biến | Bắt buộc | Mặc định | Ý nghĩa |
|---|---|---|---|
| `BOT_TOKEN` | ✅ | — | Token bot Telegram |
| `CHAT_ID` | ✅ | — | Chat/channel/group nhận quote |
| `GEMINI_API_KEY` | ✅ | — | API key Gemini |
| `GEMINI_MODEL` | | `gemini-2.0-flash-001` | Model dùng để sinh/chấm quote |
| `USED_MESSAGES_PATH` | | `used_messages.json` | File lưu lịch sử chống trùng |
| `SLEEP_HOUR_START` / `SLEEP_HOUR_END` | | `23` / `8` | Khung giờ không gửi |
| `UTC_OFFSET_HOURS` | | `7` | Múi giờ tính "giờ local" |
| `SEND_PROBABILITY` | | `0.25` | Xác suất gửi mỗi lần chạy |
| `MIN_SCORE` | | `8` | Điểm tối thiểu để gửi (thang 1-10) |
| `MAX_HISTORY` | | `1000` | Số quote tối đa giữ trong lịch sử |
| `REQUEST_TIMEOUT` | | `20` | Timeout gọi Telegram API (giây) |
| `MAX_RETRIES` | | `2` | Số lần retry khi Gemini API lỗi |
| `LOG_LEVEL` | | `INFO` | Mức log |

## Tech stack

- Python 3
- Telegram Bot API (`requests`)
- Google Gemini API (`google-genai`)
- JSON file để lưu state
- cron / systemd timer để chạy định kỳ

## Giới hạn hiện tại

- Thiết kế cho **một chat/channel duy nhất** (single-user/single-target), không phải bot multi-tenant.
- State lưu bằng file JSON cục bộ — nếu chạy nhiều instance song song hoặc trên nhiều máy khác nhau, lịch sử chống trùng sẽ không được đồng bộ.
- Không có hàng đợi (queue) hay giới hạn tốc độ gọi Gemini/Telegram ngoài retry đơn giản; nếu tăng tần suất chạy lên rất cao, nên tự thêm rate limiting.

## Định hướng mở rộng

- Habit tracking / reminder
- Lưu state vào database (SQLite/Postgres) thay vì JSON để hỗ trợ multi-target
- AI companion / personal assistant layer
- Dashboard xem lại lịch sử quote đã gửi

## Nguồn cảm hứng nội dung

Tone và cách viết được tham khảo tinh thần từ nhiều nguồn nội dung tiếng Việt về chủ đề trưởng thành, đời sống, tâm lý — không sao chép nguyên văn từ bất kỳ tác giả hay trang cụ thể nào. Toàn bộ quote thực tế đều do Gemini sinh ra theo prompt trong `main.py`, sau đó được lọc và chấm điểm tự động trước khi gửi.

## License

MIT — xem file [`LICENSE`](LICENSE). Dùng, fork, sửa tuỳ ý cho mục đích cá nhân hoặc thương mại, miễn giữ lại thông báo bản quyền.
