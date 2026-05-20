# Daily Quote Telegram Bot

Bot tự động gửi mỗi ngày một câu châm ngôn đã dịch sang tiếng Việt kèm tác giả. Nếu có sự kiện đặc biệt trong ngày (lễ, kỷ niệm, ngày quốc tế…), bot sẽ tự động gắn kèm phía trên nội dung.

Hệ thống chạy hoàn toàn tự động bằng GitHub Actions theo cron (mỗi 2 giờ), có cơ chế:
- Giới hạn thời gian chạy (08:00–23:00)
- Chống trùng nội dung
- Lưu trạng thái bằng JSON (used_messages, event_sent)
- Không cần server (0 cost infrastructure)

---

## AI sử dụng

- Google Gemini API
- Model: `gemini-3.1-flash-lite` ngày 20/05/2026

Dùng để:
- Sinh câu châm ngôn theo chủ đề (stoicism, discipline, mindset…)
- Phát hiện sự kiện đặc biệt trong ngày dựa trên ngữ cảnh thời gian

---

## Cách hoạt động

- GitHub Actions chạy mỗi 2 giờ
- Nếu ngoài khung 08:00–23:00 → bot dừng
- Mỗi lần chạy:
  - Kiểm tra sự kiện trong ngày (nếu chưa gửi)
  - Sinh câu châm ngôn
  - Quyết định gửi:
    - Nếu có event → luôn gửi
    - Nếu không có event → gửi ngẫu nhiên 50%

---

## Ví dụ output

### Có sự kiện


🔥 SỰ KIỆN HÔM NAY
Hôm nay là Tết Trung Thu 🌕

💭 CHÂM NGÔN
“Chúng ta khổ không phải vì sự việc, mà vì cách ta nhìn nhận nó.” — Marcus Aurelius

━━━━━━━━━━━━

📅 20/05/2026


---

### Không có sự kiện


💭 CHÂM NGÔN
“Discipline equals freedom.” — Jocko Willink

━━━━━━━━━━━━

📅 20/05/2026


---

## Mục tiêu dự án

- Tạo hệ thống “daily mental reset” tự động
- Nội dung ngắn, không spam
- 0 cost (chạy trên GitHub Actions)
- Dễ mở rộng (habit tracker, reminder, AI assistant layer)

---

## Tech stack

- Python
- GitHub Actions (cron scheduler)
- Telegram Bot API
- Google Gemini API
- JSON file state tracking
Mục tiêu dự án
Tự động hóa nội dung tinh gọn hằng ngày
Tạo hệ thống “daily mental reset” nhẹ, không spam
Chi phí = 0 (serverless hoàn toàn trên GitHub Actions)
Dễ mở rộng thêm quote, habit tracking, hoặc personal assistant layer
