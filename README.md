# Daily Quote Telegram Bot

Bot Telegram tự động sinh và gửi những quote ngắn bằng tiếng Việt, mang tone trưởng thành, đời thực và có chút chiều sâu — kiểu caption "chữa lành", suy ngẫm về cuộc sống, gia đình, cô đơn, thời gian, tuổi trẻ...

Nội dung được sinh bằng Google Gemini API dựa trên một bộ prompt cố định (chủ đề, style, danh sách từ/chủ đề bị chặn...). Bot tự chấm điểm và tự kiểm tra trùng lặp trước khi gửi, nên không phải quote nào sinh ra cũng được gửi đi.

Script được thiết kế để chạy **một lần rồi thoát** (one-shot). Bot chạy trên **GitHub Actions** (không cần VPS hay máy chủ riêng); vì lịch `schedule:` có sẵn của GitHub Actions không đáng tin cậy (GitHub có thể trì hoãn hoặc bỏ qua nếu repo ít hoạt động), việc "gọi bot chạy đúng giờ" được giao cho một dịch vụ cron ngoài — ví dụ [cron-job.org](https://cron-job.org) — gọi thẳng vào GitHub REST API để kích hoạt workflow (`workflow_dispatch`) theo lịch mong muốn.

Lịch sử quote đã gửi (để chống trùng) được lưu trong file `used_messages.json` ngay trong repo — workflow tự commit lại file này sau mỗi lần gửi thành công, nên state được giữ liên tục giữa các lần chạy dù mỗi lần GitHub Actions đều là một máy ảo mới, không có gì lưu sẵn từ trước.

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

Vì mỗi lần GitHub Actions chạy là một máy ảo hoàn toàn mới, `used_messages.json` phải được **commit lại vào repo** ở cuối mỗi lần chạy có gửi quote — đây là cách duy nhất để lịch sử chống trùng không bị mất giữa các lần chạy. Đừng thêm file này vào `.gitignore`.

## Cài đặt

### 1. Yêu cầu

- Một bot Telegram (tạo qua [@BotFather](https://t.me/BotFather)) và token của nó
- Chat ID (người dùng, group, hoặc channel) mà bot sẽ gửi quote tới
- Một API key của Google Gemini ([Google AI Studio](https://aistudio.google.com/))
- Một tài khoản GitHub (fork/clone repo này) — bot chạy trên GitHub Actions, không cần máy chủ riêng
- Một tài khoản ở dịch vụ gọi HTTP theo lịch, ví dụ [cron-job.org](https://cron-job.org) (miễn phí) — dùng để "bấm nút" cho GitHub Actions chạy đúng giờ

### 2. Thêm secrets vào GitHub

Vào repo trên GitHub → **Settings → Secrets and variables → Actions → Repository secrets** → tạo 3 secret:

| Tên secret | Giá trị |
|---|---|
| `BOT_TOKEN` | Token bot Telegram |
| `CHAT_ID` | Chat/group/channel ID nhận quote |
| `GEMINI_API_KEY` | API key Gemini |

Thiếu bất kỳ secret nào, `main.py` sẽ báo lỗi rõ ràng và dừng ngay khi chạy. File [`.env.example`](.env.example) liệt kê đầy đủ các biến (bắt buộc và tùy chọn) nếu bạn muốn chạy thử ở máy local trước.

### 3. Test workflow bằng tay

Vào tab **Actions** → chọn workflow **"Reality Bot"** → nút **Run workflow** → chạy thử. Mở log của lần chạy đó, xem bước **"Run bot"** để biết script đã làm gì (gửi thành công, hay bị chặn bởi khung giờ nghỉ/random gate/score thấp/trùng lặp).

### 4. Thiết lập lịch chạy tự động qua cron-job.org

Vì `schedule:` có sẵn của GitHub Actions không đáng tin cậy, ta dùng cron-job.org để gọi vào GitHub REST API, kích hoạt đúng workflow này theo lịch mong muốn.

**a. Tạo Personal Access Token (PAT) trên GitHub:**

- Vào **GitHub → Settings (tài khoản) → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**
- Chọn scope chỉ cho repo này, quyền **Actions: Read and write**
- Copy token lại (chỉ hiện một lần)

**b. Tạo cron job trên cron-job.org:**

- **URL:** `https://api.github.com/repos/tuananh511/telegram-reality-bot/actions/workflows/bot.yml/dispatches`
- **Method:** `POST`
- **Headers:**
  - `Accept: application/vnd.github+json`
  - `Authorization: Bearer <PAT vừa tạo>`
  - `X-GitHub-Api-Version: 2022-11-28`
- **Body (JSON):** `{"ref":"main"}`
- **Schedule:** ví dụ mỗi 2 giờ

Sau khi lưu, cron-job.org sẽ tự gọi endpoint này theo lịch, GitHub nhận request và chạy workflow — không cần máy chủ nào đứng chờ cả.

> Tần suất gọi cron-job.org và `SEND_PROBABILITY` (mặc định 0.25) cùng nhau quyết định số lượng quote thực tế mỗi ngày. Ví dụ gọi mỗi 2 giờ (12 lần/ngày, ~7 lần rơi vào khung hoạt động 08:00-23:00) thì trung bình gửi khoảng 1-2 quote/ngày.

### 5. (Tùy chọn) Chạy thử ở máy local trước khi đưa lên GitHub

```bash
git clone https://github.com/tuananh511/telegram-reality-bot.git
cd telegram-reality-bot
pip install -r requirements.txt
cp .env.example .env   # rồi điền giá trị thật vào .env
set -a && source .env && set +a
python3 main.py
```

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
- GitHub Actions (`workflow_dispatch`) để chạy script
- cron-job.org (hoặc dịch vụ tương đương) để trigger workflow theo lịch qua GitHub REST API
- `used_messages.json` trong repo, được workflow tự commit lại, dùng làm state lưu lịch sử chống trùng

## Giới hạn hiện tại

- Thiết kế cho **một chat/channel duy nhất** (single-user/single-target), không phải bot multi-tenant.
- State (`used_messages.json`) được lưu bằng cách commit trực tiếp vào repo — nếu 2 lần chạy trigger gần nhau (chồng chéo), có thể xảy ra race condition khi push (lần push sau bị lỗi do lịch sử đã thay đổi). Với tần suất gọi thấp (vài giờ/lần) thì rủi ro này rất nhỏ.
- Không có hàng đợi (queue) hay giới hạn tốc độ gọi Gemini/Telegram ngoài retry đơn giản; nếu tăng tần suất chạy lên rất cao, nên tự thêm rate limiting.
- Việc trigger phụ thuộc vào một dịch vụ bên thứ ba (cron-job.org) — nếu dịch vụ đó ngừng hoạt động hoặc PAT hết hạn, bot sẽ không tự chạy nữa cho tới khi bạn cấu hình lại.

## Định hướng mở rộng

- Habit tracking / reminder
- Lưu state vào database (SQLite/Postgres) thay vì JSON để hỗ trợ multi-target
- AI companion / personal assistant layer
- Dashboard xem lại lịch sử quote đã gửi

## Nguồn cảm hứng nội dung

Tone và cách viết được tham khảo tinh thần từ nhiều nguồn nội dung tiếng Việt về chủ đề trưởng thành, đời sống, tâm lý — không sao chép nguyên văn từ bất kỳ tác giả hay trang cụ thể nào. Toàn bộ quote thực tế đều do Gemini sinh ra theo prompt trong `main.py`, sau đó được lọc và chấm điểm tự động trước khi gửi.

## License

MIT — xem file [`LICENSE`](LICENSE). Dùng, fork, sửa tuỳ ý cho mục đích cá nhân hoặc thương mại, miễn giữ lại thông báo bản quyền.
