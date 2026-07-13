# Daily Quote Telegram Bot

Bot Telegram tự động gửi những đoạn quote ngắn bằng tiếng Việt mang cảm giác sâu lắng, trưởng thành và đời thực — giống các caption chữa lành, suy ngẫm về cuộc sống, gia đình, cô đơn, thời gian và hành trình trưởng thành.

Hệ thống chạy hoàn toàn tự động bằng **GitHub Actions** theo cron schedule, không cần VPS hay server riêng, chi phí gần như bằng 0.

---

## Tính năng

- Tự động sinh và gửi quote theo lịch
- Chấm điểm chất lượng quote bằng AI trước khi gửi (loại bỏ quote < 8 điểm)
- Chống trùng nội dung (duplicate theo văn bản + duplicate theo ý nghĩa/semantic)
- Lọc theo danh sách từ/chủ đề cấm và kiểu mở đầu lặp lại
- Random tần suất gửi để tránh spam (~25% mỗi lần chạy)
- Không chạy trong khung giờ nghỉ (23:00 → 08:00, giờ VN)
- Không cần VPS, không cần server chạy 24/7

## AI sử dụng

- **Provider:** Google Gemini API (`google-genai`)
- **Model:** `gemini-3.1-flash-lite`

AI được dùng cho 3 việc trong mỗi lần chạy:
1. Sinh quote tiếng Việt tự nhiên theo chủ đề random
2. Chấm điểm chất lượng quote (1–10)
3. Kiểm tra trùng lặp ý nghĩa (semantic) so với 20 quote gần nhất

## Cách hoạt động

1. GitHub Actions chạy theo lịch cron (mỗi 2 giờ).
2. Nếu ngoài khung 08:00–23:00 (giờ VN) → bot dừng ngay.
3. Random 75% → bỏ qua lượt chạy (chỉ ~25% số lần chạy thực sự gửi quote).
4. Random chọn 1 trong 15 chủ đề (theme) cảm xúc.
5. Gọi Gemini sinh quote mới theo prompt đã cấu hình sẵn (có ví dụ mẫu, danh sách từ/chủ đề cấm, kiểu mở đầu cấm).
6. Gọi Gemini chấm điểm quote — nếu điểm < 8 thì dừng.
7. Gọi Gemini kiểm tra trùng ý tưởng với 20 quote gần nhất — nếu SIMILAR thì dừng.
8. Kiểm tra validation cuối: độ dài, từ cấm, chủ đề cấm, kiểu mở đầu cấm, trùng lặp văn bản.
9. Nếu qua hết → gửi quote qua Telegram Bot API và lưu lại vào `used_messages.json`.

State được lưu bằng JSON:
- `used_messages.json` — lịch sử quote đã gửi (tối đa 1000 quote gần nhất), dùng để chống trùng

## Cài đặt

### 1. Yêu cầu

- Python 3.x
- Tài khoản Telegram Bot (tạo qua [@BotFather](https://t.me/BotFather))
- Google Gemini API key ([Google AI Studio](https://aistudio.google.com/))

### 2. Cài dependencies

```bash
pip install -r requirements.txt
```

Dependencies: `requests`, `google-genai`

### 3. Biến môi trường

| Biến | Mô tả |
|---|---|
| `BOT_TOKEN` | Token của Telegram bot (lấy từ BotFather) |
| `CHAT_ID` | ID của chat/kênh sẽ nhận quote |
| `GEMINI_API_KEY` | API key của Google Gemini |

Trên GitHub, thêm các biến này vào **Settings → Secrets and variables → Actions**.

### 4. Chạy thử local

```bash
export BOT_TOKEN="xxx"
export CHAT_ID="xxx"
export GEMINI_API_KEY="xxx"
python main.py
```

### 5. Tự động hóa bằng GitHub Actions

Workflow chạy theo cron schedule đã cấu hình trong `.github/workflows/`. Không cần server, GitHub Actions sẽ tự động thực thi `main.py` theo lịch.

## Theme đang sử dụng

Bot sẽ random một trong các vibe:

`gia đình` · `trưởng thành` · `đàn ông` · `cô đơn` · `áp lực cuộc sống` · `sự tử tế` · `thời gian` · `tuổi trẻ` · `sự cố gắng âm thầm` · `bình yên` · `chữa lành` · `mất mát` · `hành trình lớn lên` · `trách nhiệm` · `đêm khuya và suy nghĩ`

## Tech Stack

- Python
- GitHub Actions (scheduler + runtime)
- Telegram Bot API
- Google Gemini API (`gemini-3.1-flash-lite`)
- JSON state tracking

## Mục tiêu dự án

- Tạo một "daily mental reset" nhẹ mỗi ngày
- Nội dung ngắn, không spam
- Hoạt động hoàn toàn miễn phí
- Tối giản nhưng đủ ổn định để chạy lâu dài
- Dễ mở rộng thêm: habit tracking, reminder, AI companion, personal assistant layer

## Lưu ý

Bot hiện được thiết kế theo hướng **cá nhân (single-user)**.

Do hệ thống dùng GitHub Actions cron thay vì server real-time, project hiện phù hợp để:
- fork dùng riêng
- self-host cá nhân
- automation cá nhân

Chưa phù hợp để scale thành public multi-user bot nếu không có VPS hoặc webhook/polling server chạy 24/7.

## Inspiration

Một phần vibe nội dung được lấy cảm hứng từ kiểu viết của các caption trưởng thành đời thực, các page chữa lành, và phong cách của các tác giả/content creator như Nghĩ Hữu Trí, Huỳnh Duy Khương, AYP mindset style.

> Bot không copy nội dung gốc, chỉ tham khảo tinh thần và tone viết.
