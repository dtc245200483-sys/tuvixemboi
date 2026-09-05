# Ứng Dụng Tử Vi & Xem Bói Trí Tuệ Nhân Tạo (Khai Tâm Huyền Học Platform)

Hệ thống nền tảng đa nền tảng (Web PWA & Mobile Android) ứng dụng trí tuệ nhân tạo (AI) trong lĩnh vực huyền học Á Đông, hỗ trợ 4 phân hệ chính:
1. **Tử Vi Đẩu Số:** Lập và luận giải lá số 12 cung, 14 chính tinh, phụ tinh, đại vận, tiểu vận.
2. **Quẻ Kinh Dịch:** 64 quẻ dịch cổ điển, quẻ biến, thoán từ, hào từ và gieo quẻ Mai Hoa Dịch Số.
3. **Bát Tự / Tứ Trụ:** Phân tích Can-Chi giờ-ngày-tháng-năm sinh, tương tác ngũ hành, xác định Dụng Thần.
4. **Nhân Tướng Học:** Phân tích xem tay (đường chỉ tay, gò bàn tay) và xem mặt (tam đình ngũ quan, nốt ruồi).

---

## 🌐 Thông Số Môi Trường Sản Xuất (Production Endpoints)

| Thành Phần | Địa Chỉ Sản Xuất (Production URL) | Ghi Chú |
|---|---|---|
| **Frontend Web / PWA** | `https://khaitam.vercel.app` (hoặc `https://khaitam.vn`) | Giao diện chính thức, hỗ trợ PWA offline caching |
| **Backend Web API** | `https://tuvixemboi-api.onrender.com` | Cụm dịch vụ FastAPI trên Render (Region Singapore) |
| **API Health Check** | `https://tuvixemboi-api.onrender.com/health` | Kiểm tra trạng thái máy chủ (`{"status": "ok"}`) |
| **Tài Liệu Swagger API** | `https://tuvixemboi-api.onrender.com/docs` | OpenAPI / Swagger tương tác trực quan |
| **Giám Sát Lỗi Sentry** | `https://sentry.io/organizations/khaitam/issues/` | Dashboard theo dõi crash log, stack trace thời gian thực |

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
tuvixemboi/
├── frontend/
│   ├── web/                     # Ứng dụng Web React + Vite + TailwindCSS + Zustand + PWA
│   │   ├── src/                 # Mã nguồn React components, pages, router, services
│   │   ├── public/              # Static assets, manifest.json, sw.js (Workbox)
│   │   ├── vercel.json          # Cấu hình rewrite SPA routing trên Vercel
│   │   └── package.json         # Dependencies Frontend
│   └── mobile/                  # Hướng dẫn & cấu hình đóng gói APK qua Bubblewrap
│
├── backend/                     # Backend API (FastAPI)
│   ├── auth/                    # Xác thực, phân quyền (JWT, OAuth2, Passlib)
│   ├── db/                      # Cơ sở dữ liệu (SQLAlchemy ORM, Alembic migrations)
│   ├── middleware/              # Sentry, Rate Limiting, Backup Service, Retention
│   ├── api/                     # Các API routers nghiệp vụ
│   ├── tests/                   # Pytest test suites
│   ├── render.yaml              # Cấu hình Render Blueprint (Web, Disk /data, Postgres, Cron)
│   ├── Dockerfile               # Containerization đa nền tảng
│   ├── docker-compose.prod.yml  # Docker Compose sản xuất (FastAPI + Postgres)
│   ├── cron_jobs.py             # Script chạy độc lập các tác vụ bảo trì định kỳ
│   ├── deploy_production_db.py  # Script tự động migrate DB & nạp tri thức vector store
│   └── requirements.txt         # Danh mục dependencies Python (kèm psycopg2-binary)
│
├── knowledge_base/              # Kho tri thức chuyên gia & Vector Database (ChromaDB)
│   ├── ingest_pipeline.py       # Pipeline nạp dữ liệu tri thức vào ChromaDB
│   └── vector_store/            # Thư mục lưu trữ vector embeddings
│
├── interpretation_api/          # API điều phối luận giải AI chuyên sâu
├── Data_training/               # Dữ liệu nguồn huấn luyện 4 hệ thống huyền học
└── README.md                    # Tài liệu kỹ thuật dự án
```

---

## 🚀 Hướng Dẫn Triển Khai Sản Xuất (Production Deployment)

### Bước 1: Chuẩn Bị & Triển Khai Backend Lên Render / Railway

Hệ thống cung cấp sẵn file blueprint [backend/render.yaml](file:///d:/ung%20dung%20tri%20tue%20nhan%20ao/tuvixemboi/backend/render.yaml):

1. **Khởi tạo dịch vụ qua Blueprint**:
   - Đăng nhập [Render Dashboard](https://dashboard.render.com).
   - Chọn **New** $\to$ **Blueprint** $\to$ Liên kết kho mã nguồn Git của dự án.
   - Render sẽ tự động đọc `render.yaml` và tạo 3 tài nguyên:
     - **Web Service (`tuvixemboi-api`)**: Chạy lệnh `pip install -r requirements.txt && alembic upgrade head`, start lệnh `uvicorn main:app --host 0.0.0.0 --port $PORT`.
     - **Persistent Disk (`chroma-data`)**: Dung lượng 10GB, gắn tại mount path `/data` để lưu trữ Vector Database ChromaDB bền vững qua các lần deploy.
     - **PostgreSQL Database (`tuvixemboi-db`)**: Managed database tự động liên kết biến `DATABASE_URL`.
     - **Cron Job (`tuvixemboi-maintenance-cron`)**: Chạy `python cron_jobs.py` lúc 02:00 sáng hàng ngày để sao lưu và quét xóa ảnh hết hạn.

2. **Cấu hình biến môi trường trên Dashboard** (Không commit secret vào Git):
   - `AI_API_KEY`: API Key Google Gemini AI thật của bạn.
   - `SENTRY_DSN`: DSN dự án trên Sentry (để ghi nhận lỗi thời gian thực).
   - `CORS_ORIGINS`: Tên miền Frontend (ví dụ: `https://khaitam.vercel.app`).
   - `VECTOR_DB_PATH`: `/data/vector_store` (đảm bảo trỏ vào persistent volume).

---

### Bước 2: Khởi Tạo Cơ Sở Dữ Liệu & Nạp Tri Thức Vector Store

Sau khi cơ sở dữ liệu PostgreSQL và Backend đã hoạt động:

1. Mở terminal tại máy local hoặc chạy qua Render Shell:
   ```bash
   # Thiết lập biến trỏ vào DB sản xuất
   export DATABASE_URL="postgresql://user:pass@host:5432/tuvi_production?sslmode=require"
   export VECTOR_DB_PATH="/data/vector_store"
   export PYTHONPATH=".:backend:interpretation_api:knowledge_base"

   # Chạy pipeline tự động
   python backend/deploy_production_db.py
   ```
2. Script sẽ tự động:
   - Chạy `alembic upgrade head` để khởi tạo toàn bộ bảng cơ sở dữ liệu.
   - Kiểm tra xác nhận tính toàn vẹn của 8 bảng cốt lõi (`users`, `birth_profiles`, `la_so_tu_vi_results`, `tu_tru_results`, `que_kinh_dich_results`, `tuong_anh_results`, `chat_histories`, `usage_quotas`).
   - Nạp toàn bộ dữ liệu tri thức huyền học từ `Data_training/rewritten/` vào collection ChromaDB.

---

### Bước 3: Triển Khai Frontend Lên Vercel / Netlify

1. Đăng nhập [Vercel](https://vercel.com) $\to$ **Add New Project** $\to$ Nhập kho Git dự án.
2. Cấu hình cài đặt:
   - **Root Directory**: `frontend/web`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Cấu hình biến môi trường Build-time:
   - `VITE_API_URL`: `https://tuvixemboi-api.onrender.com` (Trỏ đúng URL Backend vừa deploy ở Bước 1).
4. Bấm **Deploy**. Nhờ file `vercel.json` và `_redirects` đã thiết lập, toàn bộ các route trang (`/dashboard`, `/tu-vi`, `/settings`) sẽ hoạt động hoàn hảo mà không bao giờ bị lỗi 404 khi tải lại trang.
5. Sau khi có tên miền Vercel (ví dụ: `https://khaitam.vercel.app`), quay lại Render Dashboard để bổ sung domain này vào biến `CORS_ORIGINS`.

---

### Bước 4: Vận Hành Tác Vụ Định Kỳ (Scheduled Jobs)

Hệ thống cung cấp cơ chế bảo trì kép:
1. **Chế độ 1 (Tích hợp trong Web)**: APScheduler chạy ngầm trong tiến trình FastAPI qua Lifespan handler, tự động kích hoạt vào lúc 02:00 sáng hàng ngày.
2. **Chế độ 2 (Độc lập qua Cron Job)**: Chạy script [backend/cron_jobs.py](file:///d:/ung%20dung%20tri%20tue%20nhan%20ao/tuvixemboi/backend/cron_jobs.py) thông qua Render Cron Job hoặc Crontab máy chủ:
   - **Sao lưu dữ liệu**: Snapshot database tự động (`pg_dump`) lưu trữ có timestamp.
   - **Dọn dẹp sao lưu cũ**: Tự động xóa các bản sao lưu cũ hơn 30 ngày.
   - **Bảo mật sinh trắc học**: Quét và xóa vĩnh viễn tệp ảnh khuôn mặt/bàn tay và bản ghi quá hạn 30 ngày theo quy chuẩn bảo vệ quyền riêng tư.

---

### Bước 5: Đóng Gói Ứng Dụng Di Động Android (APK)

Khi website đã chạy trên tên miền HTTPS chính thức:
1. Chuyển vào thư mục `frontend/mobile`.
2. Khởi tạo dự án Trusted Web Activity:
   ```bash
   npx @bubblewrap/cli init --manifest=https://khaitam.vercel.app/manifest.json
   ```
3. Khai báo Package ID: `com.khaitam.tuvixemboi`.
4. Xuất file `assetlinks.json` lên website tại `https://khaitam.vercel.app/.well-known/assetlinks.json`.
5. Đóng gói ứng dụng:
   ```bash
   npx @bubblewrap/cli build
   ```
6. Kết quả tạo ra file `app-release-signed.apk` sẵn sàng cài đặt trực tiếp lên các thiết bị Android với biểu tượng và giao diện chuẩn Design System.

---

## 🔍 Hướng Dẫn Giám Sát & Debug Khi Cần Thiết

### 1. Truy Cập Sentry
- Đăng nhập Sentry Dashboard: `https://sentry.io`.
- Vào mục **Issues**: Mọi ngoại lệ chưa được xử lý (HTTP 500) hoặc lỗi hệ thống nghiêm trọng sẽ tự động gửi kèm:
  - Stack trace chi tiết dòng code gây lỗi.
  - Endpoint bị tác động (nhờ middleware `gan_context_loi`).
  - Môi trường chạy (`production`).

### 2. Xem Live Logs & SSH Debug Trên Render
- **Xem Logs thời gian thực**:
  Vào Render Dashboard $\to$ Dịch vụ `tuvixemboi-api` $\to$ Chọn tab **Logs**. Bạn sẽ thấy toàn bộ request HTTP, mã phản hồi và thời gian xử lý.
- **Truy cập dòng lệnh trực tiếp (SSH / Shell)**:
  Tại Render Dashboard $\to$ Chọn tab **Shell** để mở phiên dòng lệnh tương tác trực tiếp trong container. Tại đây bạn có thể kiểm tra tệp lưu trữ, dung lượng đĩa `/data` hoặc chạy thủ công script bảo trì:
  ```bash
  python cron_jobs.py
  ```

---

## ✅ Quy Trình Tự Kiểm Tra (Self-Check 10 Bước)

1. **Giao diện Web Sản xuất**: Truy cập domain Vercel, kiểm tra bảng màu lụa/giấy dó (`#6B2B1F`, `#C9962C`, `#F5EDE0`), typography Cormorant Garamond và Be Vietnam Pro hiển thị sắc nét.
2. **Đăng ký & Đăng nhập**: Tạo tài khoản thật, xác nhận mật khẩu băm bcrypt an toàn và cấp phát JWT token chuẩn mực.
3. **Lập lá số Tử Vi**: Kiểm tra an sao 12 cung và nhận lời bình giải luận đoán từ AI kết hợp tri thức.
4. **Kiểm tra 4 phân hệ**: Xác nhận Tử Vi, Bát Tự, Kinh Dịch, Nhân Tướng hoạt động trơn tru không phát sinh lỗi 500.
5. **Kiểm tra Sentry**: Tạo request thử nghiệm xác nhận telemetry gửi về Sentry Dashboard thành công.
6. **Kiểm tra Sao lưu & Dọn dẹp**: Chạy thử `python backend/cron_jobs.py`, xác nhận file backup được tạo và ảnh quá hạn được quét dọn.
7. **Kiểm tra APK Mobile**: Cài đặt file APK lên thiết bị Android thật, xác nhận mở app ở chế độ toàn màn hình không thanh URL.
8. **Kiểm tra Đa phiên đồng thời**: Đăng nhập 2 tài khoản trên 2 trình duyệt riêng biệt, xác nhận phân tách dữ liệu độc lập.
9. **Lighthouse Audit**: Đạt chuẩn PWA (manifest, service worker offline cache, responsive layout).
10. **Rà soát An Ninh**: Xác nhận không còn sót bất kỳ credential hay secret mặc định/dev nào trên môi trường sản xuất.
