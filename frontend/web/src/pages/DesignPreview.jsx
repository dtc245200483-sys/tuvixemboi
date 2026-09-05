import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  IconCompass,
  IconCoins,
  IconEye,
  IconHandStop,
  IconYinYang,
  IconSparkles,
  IconBook,
  IconCheck,
  IconCopy,
  IconFlame,
  IconShieldCheck,
  IconMoonStars,
  IconArrowLeft
} from '@tabler/icons-react';

const COLOR_TOKENS = [
  {
    name: 'primary',
    hex: '#6B2B1F',
    role: 'Nâu đỏ trầm',
    desc: 'Thanh điều hướng Header, nút hành động chính (CTA), màu thương hiệu chủ đạo',
    textColor: '#FBF3E6',
    border: false
  },
  {
    name: 'accent',
    hex: '#C9962C',
    role: 'Vàng đồng',
    desc: 'Biểu tượng chức năng, viền nhấn, badge xếp hạng, sao chiếu mệnh',
    textColor: '#FBF3E6',
    border: false
  },
  {
    name: 'background',
    hex: '#F5EDE0',
    role: 'Kem giấy dó',
    desc: 'Nền tổng thể toàn ứng dụng, giảm mỏi mắt, gợi cảm giác hoài cổ',
    textColor: '#3B2417',
    border: true
  },
  {
    name: 'surface',
    hex: '#FFFFFF',
    role: 'Trắng tinh khiết',
    desc: 'Nền thẻ card, form nhập liệu, hộp thoại modal dialog',
    textColor: '#3B2417',
    border: true
  },
  {
    name: 'surface-border',
    hex: '#EADFC8',
    role: 'Viền thẻ nhẹ',
    desc: 'Đường viền 1px thanh mảnh phân chia ranh giới giữa các khối',
    textColor: '#3B2417',
    border: true
  },
  {
    name: 'text-primary',
    hex: '#3B2417',
    role: 'Nâu đen mực tàu',
    desc: 'Tiêu đề, nội dung chính, độ tương phản cao, dễ đọc',
    textColor: '#FBF3E6',
    border: false
  },
  {
    name: 'text-secondary',
    hex: '#8A6F52',
    role: 'Nâu nhạt',
    desc: 'Mô tả, chú thích, ngày giờ can chi, metadata phụ',
    textColor: '#FBF3E6',
    border: false
  },
  {
    name: 'text-on-primary',
    hex: '#FBF3E6',
    role: 'Kem sáng',
    desc: 'Chữ trên nền primary (nâu đỏ) hoặc nền accent (vàng đồng)',
    textColor: '#3B2417',
    border: true
  }
];

export default function DesignPreview() {
  const [copiedHex, setCopiedHex] = useState(null);

  const handleCopy = (hex) => {
    navigator.clipboard.writeText(hex);
    setCopiedHex(hex);
    setTimeout(() => setCopiedHex(null), 2000);
  };

  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* Header thương hiệu */}
      <header className="bg-primary text-text-on-primary border-b border-[#552218] px-6 py-5 sticky top-0 z-30 shadow-subtle">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-btn bg-[#552218] border border-accent/40 flex items-center justify-center text-accent">
              <IconYinYang size={24} stroke={1.75} />
            </div>
            <div>
              <h1 className="font-heading text-2xl font-bold tracking-wide text-text-on-primary">
                Tử Vi & Xem Bói AI
              </h1>
              <p className="text-xs text-[#D8C7B5] font-body">
                Hệ Thống Design Tokens & Quy Chuẩn Thẩm Mỹ (High-End Visual Design)
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              className="bg-[#552218] hover:bg-[#441a13] border border-accent/50 text-accent hover:text-text-on-primary px-3.5 py-1.5 rounded-btn text-xs font-semibold flex items-center gap-1.5 transition-all shadow-subtle"
            >
              <IconArrowLeft size={16} />
              <span>Vào Ứng Dụng (Dashboard)</span>
            </Link>
            <div className="hidden sm:flex items-center gap-2 bg-[#552218] px-3.5 py-1.5 rounded-full border border-accent/30 text-xs text-accent">
              <IconSparkles size={16} />
              <span>Prompt 8.0 — Design System</span>
            </div>
          </div>
        </div>
      </header>

      {/* Thân trang */}
      <main className="max-w-6xl mx-auto px-6 py-10 space-y-12">
        {/* Banner thông báo tiêu chuẩn */}
        <div className="bg-surface border border-surface-border rounded-card p-6 shadow-subtle flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-[#FAF5EE] border border-surface-border text-xs font-medium text-accent mb-2">
              <IconShieldCheck size={16} />
              <span>Quy Chuẩn Bắt Buộc</span>
            </div>
            <h2 className="font-heading text-2xl font-bold text-primary">
              Bảng Màu & Phong Cách Thẩm Mỹ Cố Định
            </h2>
            <p className="font-body text-text-secondary text-sm mt-1 max-w-2xl">
              Mọi màn hình và module Frontend từ Prompt 8.1 trở đi đều phải tuân thủ nghiêm ngặt 8 tokens màu này. Tuyệt đối không tự ý đổi mã màu hoặc áp dụng shadow nặng/gradient sặc sỡ.
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs text-text-secondary">
            <span className="px-3 py-1.5 rounded-btn bg-background border border-surface-border">
              Card Radius: <strong>12px</strong>
            </span>
            <span className="px-3 py-1.5 rounded-btn bg-background border border-surface-border">
              Button Radius: <strong>10px</strong>
            </span>
          </div>
        </div>

        {/* PHẦN 1: BẢNG MÀU CHÍNH THỨC */}
        <section className="space-y-4">
          <div className="border-b border-surface-border pb-2 flex items-center justify-between">
            <h3 className="font-heading text-2xl font-bold text-primary flex items-center gap-2">
              <span className="w-2.5 h-6 bg-accent rounded-full inline-block"></span>
              1. Bảng Màu Chính Thức (8 Design Tokens)
            </h3>
            <span className="text-xs text-text-secondary">Click để copy mã HEX</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {COLOR_TOKENS.map((token) => (
              <div
                key={token.name}
                onClick={() => handleCopy(token.hex)}
                className="bg-surface border border-surface-border rounded-card p-4 shadow-subtle hover:border-accent hover:shadow-elevated transition-all cursor-pointer group flex flex-col justify-between"
              >
                <div>
                  <div
                    className="h-20 w-full rounded-btn flex items-center justify-center relative transition-transform group-hover:scale-[1.02]"
                    style={{
                      backgroundColor: token.hex,
                      border: token.border ? '1px solid #EADFC8' : 'none'
                    }}
                  >
                    <span
                      className="font-mono text-sm font-semibold tracking-wider px-2 py-0.5 rounded"
                      style={{ color: token.textColor }}
                    >
                      {token.hex}
                    </span>
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      {copiedHex === token.hex ? (
                        <IconCheck size={18} style={{ color: token.textColor }} />
                      ) : (
                        <IconCopy size={18} style={{ color: token.textColor }} />
                      )}
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-primary">
                        {token.name}
                      </span>
                      <span className="text-xs font-medium text-accent">
                        {token.role}
                      </span>
                    </div>
                    <p className="text-xs text-text-secondary mt-1 line-clamp-2 leading-relaxed">
                      {token.desc}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* PHẦN 2: HỆ THỐNG TYPOGRAPHY TIẾNG VIỆT */}
        <section className="space-y-4">
          <div className="border-b border-surface-border pb-2">
            <h3 className="font-heading text-2xl font-bold text-primary flex items-center gap-2">
              <span className="w-2.5 h-6 bg-accent rounded-full inline-block"></span>
              2. Hệ Thống Phông Chữ & Kiểm Thử Tiếng Việt
            </h3>
          </div>

          <div className="bg-surface border border-surface-border rounded-card p-6 shadow-subtle space-y-6">
            <div>
              <span className="text-xs font-mono text-accent uppercase tracking-wider block mb-1">
                Heading 1 — Cormorant Garamond Bold (36px)
              </span>
              <h1 className="font-heading text-heading-1">
                Huyền Học Khởi Nguyên — Vận Mệnh, Thiên Can & Địa Chi
              </h1>
            </div>

            <div className="border-t border-surface-border/60 pt-4">
              <span className="text-xs font-mono text-accent uppercase tracking-wider block mb-1">
                Heading 2 — Cormorant Garamond SemiBold (28px)
              </span>
              <h2 className="font-heading text-heading-2">
                Lá Số Tử Vi Đẩu Số Trọn Đời — Cung Mệnh & Thân Tọa
              </h2>
            </div>

            <div className="border-t border-surface-border/60 pt-4">
              <span className="text-xs font-mono text-accent uppercase tracking-wider block mb-1">
                Heading 3 — Cormorant Garamond Medium (21.6px)
              </span>
              <h3 className="font-heading text-heading-3">
                Quẻ Kinh Dịch Số 1: Thuần Càn — Nguyên Hanh Lợi Trinh
              </h3>
            </div>

            <div className="border-t border-surface-border/60 pt-4">
              <span className="text-xs font-mono text-accent uppercase tracking-wider block mb-1">
                Body Regular — Be Vietnam Pro (15.2px)
              </span>
              <p className="font-body text-body-regular text-text-primary">
                Cung Mệnh an tại Ngọ, nạp âm Thiên Hà Thủy, có sao Tử Vi Thiên Phủ đồng cung. Đây là cách cục cát tường, chủ về mưu trí sâu rộng, công danh sự nghiệp phát triển vững bền, được quý nhân phù trợ lúc hoạn nạn. Tứ Trụ Bát Tự cân bằng ngũ hành, Kim Thủy tương sinh, vận thế hanh thông rực rỡ.
              </p>
            </div>

            <div className="border-t border-surface-border/60 pt-4">
              <span className="text-xs font-mono text-accent uppercase tracking-wider block mb-1">
                Caption & Metadata — Be Vietnam Pro (13.2px)
              </span>
              <p className="font-body text-caption">
                Dương lịch: 15/10/1992 08:15 • Âm lịch: Ngày 20 tháng 9 năm Nhâm Thân (Giờ Mậu Thìn) • Cục: Thủy Nhị Cục
              </p>
            </div>
          </div>
        </section>

        {/* PHẦN 3: HỆ THỐNG NÚT BẤM (BUTTONS) */}
        <section className="space-y-4">
          <div className="border-b border-surface-border pb-2">
            <h3 className="font-heading text-2xl font-bold text-primary flex items-center gap-2">
              <span className="w-2.5 h-6 bg-accent rounded-full inline-block"></span>
              3. Mẫu Nút Bấm Chuẩn (Button Components — Radius 10px)
            </h3>
          </div>

          <div className="bg-surface border border-surface-border rounded-card p-6 shadow-subtle">
            <div className="flex flex-wrap items-center gap-4">
              {/* Primary CTA */}
              <button className="btn-primary">
                <IconCompass size={20} className="text-accent" />
                <span>Nút Chính (Primary CTA)</span>
              </button>

              {/* Accent Button */}
              <button className="btn-accent">
                <IconCoins size={20} />
                <span>Nút Nhấn (Accent Button)</span>
              </button>

              {/* Outline Button */}
              <button className="btn-outline">
                <IconBook size={20} className="text-accent" />
                <span>Nút Viền (Outline)</span>
              </button>

              {/* Disabled Button */}
              <button
                disabled
                className="bg-[#EADFC8]/50 text-text-secondary cursor-not-allowed px-5 py-2.5 rounded-btn font-medium inline-flex items-center gap-2 border border-surface-border"
              >
                <span>Nút Vô Hiệu Hóa</span>
              </button>
            </div>
          </div>
        </section>

        {/* PHẦN 4: THẺ CARD MẪU CHO 4 HỆ THỐNG HUYỀN HỌC */}
        <section className="space-y-4">
          <div className="border-b border-surface-border pb-2">
            <h3 className="font-heading text-2xl font-bold text-primary flex items-center gap-2">
              <span className="w-2.5 h-6 bg-accent rounded-full inline-block"></span>
              4. Mẫu Thẻ Card (Radius 12px, Viền #EADFC8 1px, Shadow Nhẹ)
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Card 1: Tử Vi */}
            <div className="card-base p-5 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-btn bg-[#FAF5EE] border border-surface-border flex items-center justify-center text-accent mb-3">
                  <IconCompass size={24} stroke={1.75} />
                </div>
                <h4 className="font-heading text-lg font-bold text-primary">Tử Vi Đẩu Số</h4>
                <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                  Lập lá số 12 cung hoàng đạo, an sao chính tinh, phụ tinh, luận giải đại hạn trọn đời.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-surface-border/70 flex items-center justify-between text-xs">
                <span className="text-accent font-medium">12 Cung Vị</span>
                <span className="text-text-secondary">Chi tiết &rarr;</span>
              </div>
            </div>

            {/* Card 2: Bát Tự */}
            <div className="card-base p-5 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-btn bg-[#FAF5EE] border border-surface-border flex items-center justify-center text-accent mb-3">
                  <IconYinYang size={24} stroke={1.75} />
                </div>
                <h4 className="font-heading text-lg font-bold text-primary">Bát Tự Tứ Trụ</h4>
                <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                  Phân tích Năm - Tháng - Ngày - Giờ sinh, độ vượng suy ngũ hành, xác định Dụng Thần.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-surface-border/70 flex items-center justify-between text-xs">
                <span className="text-accent font-medium">Ngũ Hành Âm Dương</span>
                <span className="text-text-secondary">Chi tiết &rarr;</span>
              </div>
            </div>

            {/* Card 3: Kinh Dịch */}
            <div className="card-base p-5 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-btn bg-[#FAF5EE] border border-surface-border flex items-center justify-center text-accent mb-3">
                  <IconCoins size={24} stroke={1.75} />
                </div>
                <h4 className="font-heading text-lg font-bold text-primary">Kinh Dịch Chiêm Bói</h4>
                <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                  Gieo quẻ 3 đồng xu hoặc theo thời khắc, quẻ chính, quẻ biến và hào động thời vận.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-surface-border/70 flex items-center justify-between text-xs">
                <span className="text-accent font-medium">64 Quẻ Dịch</span>
                <span className="text-text-secondary">Chi tiết &rarr;</span>
              </div>
            </div>

            {/* Card 4: Nhân Tướng */}
            <div className="card-base p-5 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-btn bg-[#FAF5EE] border border-surface-border flex items-center justify-center text-accent mb-3">
                  <IconHandStop size={24} stroke={1.75} />
                </div>
                <h4 className="font-heading text-lg font-bold text-primary">Nhân Tướng Học</h4>
                <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                  Phân tích đường chỉ tay, tam đình ngũ nhạc khuôn mặt qua thị giác máy tính Vision AI.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-surface-border/70 flex items-center justify-between text-xs">
                <span className="text-accent font-medium">Chỉ Tay & Tướng Diện</span>
                <span className="text-text-secondary">Chi tiết &rarr;</span>
              </div>
            </div>
          </div>
        </section>

        {/* PHẦN 5: BỘ BIỂU TƯỢNG TABLER ICONS VỚI MÀU ACCENT (#C9962C) */}
        <section className="space-y-4">
          <div className="border-b border-surface-border pb-2">
            <h3 className="font-heading text-2xl font-bold text-primary flex items-center gap-2">
              <span className="w-2.5 h-6 bg-accent rounded-full inline-block"></span>
              5. Bộ Biểu Tượng Chuẩn (Tabler Icons — Màu Accent #C9962C)
            </h3>
          </div>

          <div className="bg-surface border border-surface-border rounded-card p-6 shadow-subtle">
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-4 text-center">
              <div className="p-3 rounded-btn bg-[#FAF5EE] border border-surface-border flex flex-col items-center gap-2">
                <IconCompass size={28} className="text-accent" stroke={1.75} />
                <span className="text-xs font-mono text-text-secondary">IconCompass</span>
              </div>
              <div className="p-3 rounded-btn bg-[#FAF5EE] border border-surface-border flex flex-col items-center gap-2">
                <IconCoins size={28} className="text-accent" stroke={1.75} />
                <span className="text-xs font-mono text-text-secondary">IconCoins</span>
              </div>
              <div className="p-3 rounded-btn bg-[#FAF5EE] border border-surface-border flex flex-col items-center gap-2">
                <IconHandStop size={28} className="text-accent" stroke={1.75} />
                <span className="text-xs font-mono text-text-secondary">IconHandStop</span>
              </div>
              <div className="p-3 rounded-btn bg-[#FAF5EE] border border-surface-border flex flex-col items-center gap-2">
                <IconEye size={28} className="text-accent" stroke={1.75} />
                <span className="text-xs font-mono text-text-secondary">IconEye</span>
              </div>
              <div className="p-3 rounded-btn bg-[#FAF5EE] border border-surface-border flex flex-col items-center gap-2">
                <IconYinYang size={28} className="text-accent" stroke={1.75} />
                <span className="text-xs font-mono text-text-secondary">IconYinYang</span>
              </div>
              <div className="p-3 rounded-btn bg-[#FAF5EE] border border-surface-border flex flex-col items-center gap-2">
                <IconMoonStars size={28} className="text-accent" stroke={1.75} />
                <span className="text-xs font-mono text-text-secondary">IconMoonStars</span>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-[#FAF5EE] border-t border-surface-border py-6 text-center text-xs text-text-secondary mt-16">
        <div className="max-w-6xl mx-auto px-6">
          <p>Tử Vi & Xem Bói AI Platform &copy; 2026. Thiết kế theo tiêu chuẩn Soft-Skill / High-End Visual Design.</p>
        </div>
      </footer>
    </div>
  );
}
