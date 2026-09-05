# Hướng Dẫn Đóng Gói Ứng Dụng Mobile Android (APK / AAB) Bằng Bubblewrap

Tài liệu hướng dẫn quy trình chuyển đổi **Khai Tâm Huyền Học (PWA)** thành ứng dụng Android Native hoàn chỉnh thông qua công nghệ **Trusted Web Activity (TWA)** và công cụ mã nguồn mở chính thức của Google: **Bubblewrap CLI**.

---

## 1. Yêu Cầu Tiên Quyết (Prerequisites)

Để xây dựng file APK / AAB trên máy tính, bạn cần cài đặt các công cụ sau:

1. **Node.js**: Phiên bản $\ge 18.x$ và npm/npx.
2. **Java Development Kit (JDK)**: Phiên bản **JDK 17** (khuyến nghị dùng OpenJDK 17 hoặc Eclipse Temurin 17).
   - Kiểm tra bằng lệnh: `java -version`.
3. **Android SDK Command-line Tools**:
   - Tải từ Android Studio hoặc standalone command-line tools.
   - Thiết lập biến môi trường `ANDROID_HOME` trỏ tới thư mục SDK.
4. **Domain HTTPS thật (Bắt buộc cho Trusted Web Activity)**:
   - TWA yêu cầu website phải chạy trên tên miền HTTPS có chứng chỉ SSL hợp lệ (ví dụ: `https://khaitam.vn` hoặc `https://tuvi-ai.vercel.app`).
   - *Lưu ý quan trọng:* **KHÔNG THỂ** dùng `localhost` hoặc địa chỉ IP nội bộ (`http://127.0.0.1`) cho bản build phát hành thật, vì Android OS sẽ từ chối xác thực chữ ký Digital Asset Links và sẽ hiện thanh địa chỉ trình duyệt giống như mở trang web thông thường.
5. **Icon Ứng Dụng Đạt Chuẩn**:
   - Sử dụng tệp icon kích thước $512 	imes 512$ pixel đã chuẩn bị sẵn tại:
     `frontend/web/public/icons/icon-512.png` (nền chuẩn màu `#6B2B1F`, biểu tượng vàng đồng `#C9962C`).

---

## 2. Các Bước Đóng Gói Bằng Bubblewrap

### Bước 1: Khởi Tạo Dự Án TWA (Init)

Chạy lệnh npx để khởi tạo dự án trực tiếp từ tệp `manifest.json` đã triển khai trên domain HTTPS:

```bash
cd frontend/mobile
npx @bubblewrap/cli init --manifest=https://your-domain.com/manifest.json
```

Bubblewrap sẽ tự động tải `manifest.json` và hướng dẫn bạn cấu hình các thông số:
- **Application name**: `Khai Tâm Huyền Học`
- **Short name**: `Khai Tâm AI`
- **Application ID (Package Name)**: `com.khaitam.tuvixemboi`
- **Display mode**: `standalone`
- **Status bar color**: `#6B2B1F`
- **Navigation bar color**: `#F5EDE0`
- **Splash screen background color**: `#F5EDE0`
- **Icon URL**: `https://your-domain.com/icons/icon-512.png`
- **Maskable icon URL**: `https://your-domain.com/icons/icon-512.png`
- **Signing key (Keystore)**:
  - Chọn tạo mới một Keystore (`android.keystore`).
  - Nhập mật khẩu Keystore, bí danh Alias (`khaitam`), tên đơn vị phát hành.
  - *Lưu ý:* Lưu trữ cẩn thận file `.keystore` và mật khẩu để nâng cấp phiên bản sau này.

---

### Bước 2: Thiết Lập Digital Asset Links (`assetlinks.json`)

Để Android xóa bỏ hoàn toàn thanh địa chỉ trình duyệt (URL bar) và cho phép ứng dụng hiển thị dạng toàn màn hình nguyên bản (Full native look & feel), bạn phải liên kết chữ ký của file APK với tên miền website:

1. Sau khi chạy `bubblewrap init`, công cụ sẽ in ra chuỗi vân tay chứng chỉ **SHA-256 Fingerprint** của keystore.
2. Tạo tệp `assetlinks.json` với nội dung mẫu sau:

```json
[
  {
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
      "namespace": "android_app",
      "package_name": "com.khaitam.tuvixemboi",
      "sha256_cert_fingerprints": [
        "14:6D:E9:7E:0F:52:AC:46:E6:1B:39:61:92:82:70:..."
      ]
    }
  }
]
```

3. Đưa tệp này lên máy chủ web tại đường dẫn tuyệt đối:
   `https://your-domain.com/.well-known/assetlinks.json`
   - Đảm bảo header phản hồi là `Content-Type: application/json`.
   - Có thể kiểm tra tính hợp lệ bằng công cụ [Google Digital Asset Links Tester](https://developers.google.com/digital-asset-links/tools/generator).

---

### Bước 3: Đóng Gói Ứng Dụng (Build APK / AAB)

Chạy lệnh build để biên dịch toàn bộ mã nguồn:

```bash
npx @bubblewrap/cli build
```

Kết quả tạo ra trong thư mục:
- `app-release-signed.apk`: File APK đã ký số, sẵn sàng cài đặt trực tiếp lên các thiết bị Android.
- `app-release-bundle.aab`: File Android App Bundle dùng để đăng tải lên Google Play Console.

---

## 3. Cài Đặt Thử Nghiệm Trên Thiết Bị Android Thật

### Cách 1: Cài đặt qua Android Debug Bridge (ADB)
1. Bật chế độ **Tùy chọn cho nhà phát triển (Developer Options)** và **Gỡ lỗi USB (USB Debugging)** trên điện thoại Android.
2. Kết nối điện thoại với máy tính qua cáp USB.
3. Chạy lệnh:
   ```bash
   adb install -r app-release-signed.apk
   ```

### Cách 2: Cài đặt trực tiếp từ file APK
1. Gửi file `app-release-signed.apk` qua Google Drive, Zalo hoặc cắm dây truyền file vào bộ nhớ trong máy.
2. Mở trình quản lý file trên Android, bấm vào file APK và chọn "Cài đặt ứng dụng từ nguồn này".

---

## 4. Kiểm Thử Trải Nghiệm Ứng Dụng Trên Điện Thoại

Sau khi cài đặt thành công:
1. **Màn hình chính**: Ứng dụng hiển thị icon nền nâu đỏ `#6B2B1F` với biểu tượng la bàn phong thủy vàng đồng `#C9962C` sắc nét.
2. **Mở ứng dụng**: Xuất hiện Splash screen nền kem giấy dó `#F5EDE0`, sau đó vào thẳng giao diện mà không hề có thanh địa chỉ URL của Chrome.
3. **Chế độ ngoại tuyến (Offline)**: Khi bật Chế độ máy bay (ngắt Wifi & 4G), mở ứng dụng vẫn hiển thị đầy đủ giao diện, các lá số Tử Vi / Bát Tự đã tra cứu trước đó vẫn xem được mượt mà, kèm theo huy hiệu thông báo ngoại tuyến ở góc dưới màn hình.
