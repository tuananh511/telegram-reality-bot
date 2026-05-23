# Daily Quote Telegram Bot

Bot Telegram tự động gửi những đoạn quote ngắn bằng tiếng Việt mang cảm giác sâu lắng, trưởng thành và đời thực — giống các caption chữa lành, suy ngẫm về cuộc sống, gia đình, cô đơn, thời gian và hành trình trưởng thành.

Nếu trong ngày có sự kiện đặc biệt (lễ, ngày kỷ niệm, sự kiện quốc tế...), bot sẽ tự động gắn thêm phần thông báo phía trên quote.

Hệ thống chạy hoàn toàn tự động bằng GitHub Actions theo cron schedule, không cần VPS hay server riêng.

---

## Demo Output

### Có sự kiện

```text
🔥 SỰ KIỆN HÔM NAY
Hôm nay là Tết Trung Thu 🌕

Khi lớn lên,
bạn bắt đầu hiểu...
ba mẹ cũng chỉ là những người
lần đầu làm cha mẹ.

━━━━━━━━━━━━

📅 20/05/2026
```

### Không có sự kiện
```text
Áp lực lớn nhất của đàn ông,
nhiều khi là phải tỏ ra mình vẫn ổn.

━━━━━━━━━━━━

📅 20/05/2026
```

# Tính năng
- Tự động gửi quote theo lịch
- Nội dung mang phong cách:
  - trưởng thành
  - đời thực
  - chữa lành
  - suy ngẫm
  - gia đình
  - cô đơn
  - áp lực cuộc sống
  - sự cố gắng âm thầm
- Chống gửi trùng nội dung
- Tự động phát hiện sự kiện đặc biệt trong ngày
- Random tần suất gửi để tránh spam
- Không chạy trong khung giờ nghỉ (23:00 → 08:00)
- Không cần VPS
- Chi phí gần như bằng 0
# AI sử dụng
- Google Gemini API
- Model:
gemini-3.1-flash-lite

AI được dùng để:

- Sinh quote tiếng Việt tự nhiên
- Giảm cảm giác "AI quote machine"
- Tạo nội dung giống caption Facebook sâu lắng
- Kiểm tra sự kiện đặc biệt trong ngày
# Cách hoạt động
- GitHub Actions chạy mỗi 2 giờ.
- Nếu ngoài khung 08:00–23:00 → bot dừng.
- Mỗi lần chạy:
Kiểm tra event trong ngày.
- Random theme cảm xúc.
- Sinh quote mới bằng Gemini AI.
- Kiểm tra duplicate.
Quyết định gửi:
- Có event → luôn gửi.
- Không có event → random 20%.

State được lưu bằng JSON:

- used_messages.json
- event_sent.json
  
# Theme đang sử dụng

Bot sẽ random các vibe như:

- gia đình
- trưởng thành
- đàn ông
- cô đơn
- áp lực cuộc sống
- sự tử tế
- thời gian
- tuổi trẻ
- sự cố gắng âm thầm
- bình yên
- chữa lành
- mất mát
- hành trình lớn lên
- trách nhiệm
- đêm khuya và suy nghĩ
# Tech Stack
- Python
- GitHub Actions
- Telegram Bot API
- Google Gemini API
- JSON state tracking
# Mục tiêu dự án
- Tạo một “daily mental reset” nhẹ mỗi ngày
- Nội dung ngắn, không spam
- Hoạt động hoàn toàn miễn phí
- Tối giản nhưng đủ ổn định để chạy lâu dài
- Dễ mở rộng thêm:
  - habit tracking
  - reminder
  - AI companion
  - personal assistant layer
# Lưu ý

Hiện bot được thiết kế theo hướng cá nhân (single-user).

Do hệ thống sử dụng GitHub Actions cron thay vì server real-time, project hiện phù hợp để:

fork dùng riêng
self-host cá nhân
automation cá nhân

Chưa phù hợp để scale thành public multi-user bot nếu không có VPS hoặc webhook/polling server chạy 24/7.

# Inspiration

Một phần vibe nội dung được lấy cảm hứng từ kiểu viết:

những caption trưởng thành đời thực
các page chữa lành
các tác giả/content creator như:
Nghĩ Hữu Trí
Huỳnh Duy Khương
AYP mindset style

# Bot không copy nội dung gốc, chỉ tham khảo tinh thần và tone viết.
