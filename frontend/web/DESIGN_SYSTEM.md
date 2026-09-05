# DESIGN SYSTEM CHÍNH THỨC — TỬ VI & XEM BÓI AI PLATFORM

> **QUY TẮC BẮT BUỘC CHO MỌI PROMPT FRONTEND (8.1, 8.2, 8.3, 8.4...):**
> Trước khi viết bất kỳ dòng code giao diện nào, bạn BẮT BUỘC phải đọc tài liệu này. Sử dụng ĐÚNG token màu, font chữ và quy tắc thẩm mỹ đã chốt dưới đây. **TUYỆT ĐỐI KHÔNG TỰ Ý ĐỔI MÀU HOẶC TẠO MÃ MÀU MỚI**.

---

## 1. Bảng Màu Chính Thức (Official Color Tokens)

Toàn bộ ứng dụng sử dụng bảng màu mang tính chất Á Đông huyền bí, tinh tế (Sophisticated Eastern Mystic), ấm áp như lụa và giấy dó:

| Token Name | Mã Hex | Tailwind Class | Vai trò & Mục đích sử dụng |
|---|---|---|---|
| `primary` | `#6B2B1F` | `bg-primary`, `text-primary-brand` | **Nâu đỏ trầm**: Thanh điều hướng Header, nút hành động chính (CTA Button), màu thương hiệu chủ đạo. |
| `accent` | `#C9962C` | `bg-accent`, `text-accent` | **Vàng đồng**: Biểu tượng chức năng (Icons), viền nhấn active, badge xếp hạng, sao chiếu mệnh. |
| `background` | `#F5EDE0` | `bg-background` | **Kem giấy dó**: Nền tổng thể toàn ứng dụng, dịu mắt, tránh mỏi mắt, gợi cảm giác hoài cổ trang nhã. |
| `surface` | `#FFFFFF` | `bg-surface` | **Trắng ngà tinh khiết**: Nền các thẻ chứa nội dung (Card), modal dialog, khung nhập liệu form. |
| `surface-border` | `#EADFC8` | `border-surface-border` | **Viền thẻ 1px**: Tạo ranh giới nhẹ nhàng giữa các khối dữ liệu, không dùng shadow nặng. |
| `text-primary` | `#3B2417` | `text-text-primary` | **Nâu đen mực tàu**: Tiêu đề chính, văn bản luận giải quan trọng, độ tương phản cao, dễ đọc. |
| `text-secondary` | `#8A6F52` | `text-text-secondary` | **Nâu nhạt**: Mô tả phụ, ngày giờ can chi, metadata, chú thích các cung/hào. |
| `text-on-primary` | `#FBF3E6` | `text-text-on-primary` | **Kem sáng**: Màu chữ hiển thị trên nền `primary` (nâu đỏ) hoặc `accent` (vàng đồng). |

---

## 2. Quy Tắc Bo Góc (Border Radius)

Nhất quán hình học trên mọi thành phần giao diện:
- **Card / Container / Dialog**: `rounded-card` = `12px` (`--radius-card: 12px;`)
- **Button / Input Field / Dropdown**: `rounded-btn` = `10px` (`--radius-btn: 10px;`)
- **Badge / Pill Tag**: `rounded-full` (`9999px`)

---

## 3. Quy Chuẩn Typography (Phông Chữ & Cỡ Chữ)

Sử dụng kết hợp 2 bộ phông chuẩn Google Fonts hỗ trợ trọn vẹn tiếng Việt có dấu:

1. **Phông Tiêu Đề (`font-heading`)**: `'Cormorant Garamond', Georgia, serif`
   - Dành riêng cho: Tiêu đề trang (H1), tên lá số Tử Vi, tên quẻ Kinh Dịch, tên cung hoàng đạo (H2, H3).
   - Đặc điểm: Đường nét thanh mảnh, cổ điển, trang nghiêm.
2. **Phông Nội Dung (`font-body`)**: `'Be Vietnam Pro', sans-serif`
   - Dành riêng cho: Toàn bộ nội dung luận giải, bảng sao, danh sách hào quẻ, biểu mẫu, nút bấm.
   - Đặc điểm: Cực kỳ dễ đọc trên màn hình di động lẫn máy tính, dấu thanh tiếng Việt chuẩn mực.

---

## 4. Quy Tắc Thẩm Mỹ & Đồ Họa (High-End Visual Design)

1. **Không dùng Gradient sặc sỡ**: Tránh xa các dải màu tím-neon, xanh-vàng gradient kiểu AI template. Giao diện phải mang vẻ đẹp phẳng, nhã nhặn của tranh thủy mặc và chất liệu giấy mộc.
2. **Không dùng Đổ Bóng (Shadow) nặng**: Tuyệt đối không dùng `shadow-2xl` hay shadow đen kịt. Chỉ dùng viền `border: 1px solid #EADFC8` kết hợp shadow cực nhẹ `rgba(107, 43, 31, 0.04)` để phân lớp.
3. **Khoảng Trắng (Whitespace)**: Bố cục rộng rãi, padding thoáng đãng (`p-6`, `gap-6`), không nhồi nhét chữ hay chi tiết vụn vặt.
4. **Biểu Tượng (Icons)**:
   - Sử dụng bộ **Tabler Icons** (`@tabler/icons-react`) với nét vẽ Outline thanh thoát (stroke width 1.5 - 1.75).
   - Màu sắc icon chức năng luôn dùng màu **Accent `#C9962C`** hoặc Nâu trầm `#6B2B1F`.

---

## 5. Mẫu Code Chuẩn Cho Các Thành Phần Cơ Bản

### Nút Bấm (Buttons)
```jsx
// Nút hành động chính (Primary CTA)
<button className="bg-primary hover:bg-[#552218] text-text-on-primary px-5 py-2.5 rounded-btn font-medium inline-flex items-center gap-2 transition-all shadow-subtle">
  <IconCompass size={20} className="text-accent" />
  Lập Lá Số Tử Vi
</button>

// Nút điểm nhấn (Accent Button)
<button className="bg-accent hover:bg-[#B38323] text-text-on-primary px-5 py-2.5 rounded-btn font-medium inline-flex items-center gap-2 transition-all">
  <IconCoins size={20} />
  Gieo Quẻ Kinh Dịch
</button>

// Nút phụ / Viền ngoài (Outline Button)
<button className="bg-surface hover:bg-[#FAF5EE] text-text-primary border border-surface-border hover:border-accent px-5 py-2.5 rounded-btn font-medium inline-flex items-center gap-2 transition-all">
  Xem Chi Tiết
</button>
```

### Thẻ Nội Dung (Card)
```jsx
<div className="bg-surface border border-surface-border rounded-card p-6 shadow-subtle hover:border-accent hover:shadow-elevated transition-all">
  <div className="flex items-center gap-3 mb-4">
    <div className="w-10 h-10 rounded-btn bg-[#FAF5EE] border border-surface-border flex items-center justify-center text-accent">
      <IconYinYang size={24} />
    </div>
    <h3 className="font-heading text-heading-3 text-text-primary">Cung Mệnh: Bính Ngọ</h3>
  </div>
  <p className="font-body text-body-regular text-text-secondary leading-relaxed">
    Cung Mệnh an tại Ngọ, có Tử Vi Thiên Phủ đồng cung, thời vận hanh thông, công danh vẹn toàn.
  </p>
</div>
```

---

*Tài liệu này được khóa cố định theo Prompt 8.0 — Design System Agent.*
