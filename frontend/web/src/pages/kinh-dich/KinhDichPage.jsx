import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  IconCoins,
  IconArrowLeft,
  IconSparkles,
  IconClock,
  IconArrowRight,
  IconHelpCircle,
  IconYinYang
} from '@tabler/icons-react';
import { kinhDichService } from '../../services/api';
import InterpretationTabs from '../../components/InterpretationTabs';
import QuotaBadge from '../../components/QuotaBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

export default function KinhDichPage() {
  const [cauHoi, setCauHoi] = useState('');
  const [phuongPhap, setPhuongPhap] = useState('dong_xu'); // 'dong_xu' hoặc 'thoi_gian'
  const [isCasting, setIsCasting] = useState(false);
  const [revealedLinesCount, setRevealedLinesCount] = useState(0);
  const [error, setError] = useState(null);
  const [resultData, setResultData] = useState(null);
  const [quotaTrigger, setQuotaTrigger] = useState(0);

  const handleGieoQue = async (e) => {
    e.preventDefault();
    if (!cauHoi.trim()) {
      setError('Vui lòng nhập câu hỏi hoặc sự việc quý vị muốn chiêm bái trước khi gieo quẻ.');
      return;
    }

    setError(null);
    setIsCasting(true);
    setRevealedLinesCount(0);
    setResultData(null);

    // Hiệu ứng tuần tự xuất hiện 6 hào (từ hào 1 dưới cùng lên hào 6)
    const interval = setInterval(() => {
      setRevealedLinesCount((prev) => {
        if (prev >= 6) {
          clearInterval(interval);
          return 6;
        }
        return prev + 1;
      });
    }, 280);

    try {
      const res = await kinhDichService.gieoQue({
        cau_hoi: cauHoi.trim(),
        phuong_phap: phuongPhap,
      });
      const data = res.data?.du_lieu || res.data;

      // Đảm bảo hiệu ứng hào chạy xong trước khi hiển thị trọn vẹn kết quả
      setTimeout(() => {
        clearInterval(interval);
        setRevealedLinesCount(6);
        setResultData(data);
        setIsCasting(false);
        setQuotaTrigger((prev) => prev + 1);
      }, 1800);
    } catch (err) {
      clearInterval(interval);
      setIsCasting(false);
      if (err.response) {
        const detail = err.response.data?.detail || err.response.data?.loi;
        setError(typeof detail === 'string' ? detail : 'Không thể gieo quẻ lúc này. Vui lòng thử lại.');
      } else {
        setError('Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại mạng.');
      }
    }
  };

  const chiTietQue = resultData?.chi_tiet_que || {};
  const queChinh = chiTietQue.que_chinh || {};
  const queBien = chiTietQue.que_bien;
  const danhSachHao = chiTietQue.danh_sach_hao || [];
  const luanGiai = resultData?.luan_giai;

  // Render một vạch hào (Dương = liền, Âm = đứt, Động = viền vàng đồng)
  const renderHaoLine = (isDuong, isDong = false, key = '') => {
    return (
      <div
        key={key}
        className={`w-full h-4 flex items-center justify-between transition-all duration-300 ${
          isDong ? 'text-accent' : 'text-primary'
        }`}
        title={isDong ? 'Hào biến động (Chuyển hóa Âm / Dương)' : isDuong ? 'Hào Dương (Cương kiện)' : 'Hào Âm (Nhu thuận)'}
      >
        {isDuong ? (
          // Hào Dương: thanh liền
          <div
            className={`w-full h-3 rounded-full ${
              isDong ? 'bg-accent shadow-xs' : 'bg-primary'
            }`}
          />
        ) : (
          // Hào Âm: thanh đứt (2 đoạn)
          <div className="w-full flex items-center justify-between gap-2.5">
            <div
              className={`w-[45%] h-3 rounded-full ${
                isDong ? 'bg-accent shadow-xs' : 'bg-primary'
              }`}
            />
            <div
              className={`w-[45%] h-3 rounded-full ${
                isDong ? 'bg-accent shadow-xs' : 'bg-primary'
              }`}
            />
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* Header thanh điều hướng */}
      <header className="bg-primary text-text-on-primary border-b border-[#552218] px-4 sm:px-8 py-4 shadow-subtle sticky top-0 z-20">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              className="p-1.5 rounded-btn bg-[#552218] border border-surface-border/30 hover:border-accent text-text-on-primary transition-colors"
              title="Quay lại Tổng quan"
            >
              <IconArrowLeft size={18} />
            </Link>
            <div>
              <h1 className="font-heading text-xl sm:text-2xl font-bold tracking-wide text-text-on-primary flex items-center gap-2">
                <span>Kinh Dịch Chiêm Bái</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-accent/30 text-text-on-primary border border-accent/40 font-normal">
                  Chu Dịch
                </span>
              </h1>
              <p className="text-xs text-[#D8C7B5] font-body hidden sm:block">
                Lục Hào Khởi Quẻ, Quẻ Biến & Lời Khuyên Hành Động
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <QuotaBadge refreshTrigger={quotaTrigger} className="bg-[#552218] border-surface-border/30 text-text-on-primary" />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-8 py-8 space-y-8">
        {error && (
          <ErrorMessage
            message={error}
            onClose={() => setError(null)}
            className="mb-4"
          />
        )}

        {/* 1. KHUNG NHẬP CÂU HỎI & CHỌN PHƯƠNG PHÁP */}
        <div className="card-base p-6 sm:p-8 space-y-5">
          <div className="border-b border-surface-border pb-4">
            <h2 className="font-heading text-2xl font-bold text-primary flex items-center gap-2">
              <IconCoins size={24} className="text-accent" />
              <span>Khởi Niệm Chiêm Quẻ</span>
            </h2>
            <p className="text-xs font-body text-text-secondary mt-1">
              "Kinh Dịch chỉ giải việc có thành tâm". Hãy giữ tâm trí tĩnh lặng và tập trung vào một vấn đề rõ ràng.
            </p>
          </div>

          <form onSubmit={handleGieoQue} className="space-y-4">
            {/* Textarea nhập câu hỏi */}
            <div>
              <label className="block font-body text-xs font-semibold text-text-primary uppercase tracking-wider mb-1.5">
                Nội Dung Sự Việc Cần Chiêm Đoán <span className="text-primary">*</span>
              </label>
              <textarea
                rows={3}
                value={cauHoi}
                onChange={(e) => setCauHoi(e.target.value)}
                disabled={isCasting}
                placeholder="Ví dụ: Công việc và dự án kinh doanh mới của tôi trong 6 tháng tới diễn tiến ra sao?"
                className="w-full p-3.5 bg-surface rounded-btn border border-surface-border text-sm text-text-primary placeholder:text-text-secondary/60 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all font-body leading-relaxed"
              />
            </div>

            {/* Phương pháp gieo quẻ */}
            <div className="space-y-1.5">
              <label className="block font-body text-xs font-semibold text-text-primary uppercase tracking-wider">
                Phương Thức Gieo Quẻ
              </label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { id: 'dong_xu', title: 'Tam Tiền Chiêm Cổ', desc: 'Gieo 3 đồng tiền theo lối Lục Hào', icon: IconCoins },
                  { id: 'thoi_gian', title: 'Mai Hoa Dịch Số', desc: 'Lấy quẻ theo Thời khắc vũ trụ hiện tại', icon: IconClock },
                ].map((m) => {
                  const Icon = m.icon;
                  return (
                    <button
                      key={m.id}
                      type="button"
                      disabled={isCasting}
                      onClick={() => setPhuongPhap(m.id)}
                      className={`p-3 rounded-btn border text-left transition-all flex items-start gap-2.5 ${
                        phuongPhap === m.id
                          ? 'bg-surface border-2 border-primary shadow-subtle ring-1 ring-primary/20'
                          : 'bg-[#FAF5EE]/50 border-surface-border hover:border-accent/60'
                      }`}
                    >
                      <Icon size={20} className={phuongPhap === m.id ? 'text-accent' : 'text-text-secondary'} />
                      <div>
                        <div className="text-xs font-semibold text-text-primary font-body">
                          {m.title}
                        </div>
                        <div className="text-[11px] text-text-secondary font-body mt-0.5">
                          {m.desc}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Nút Gieo Quẻ */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={isCasting}
                className="btn-primary w-full py-3 text-base shadow-subtle disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isCasting ? (
                  <LoadingSpinner size="sm" color="white" text="Đang cung thỉnh 6 hào Kinh Dịch..." />
                ) : (
                  <>
                    <IconYinYang size={20} className="text-accent animate-spin-slow" />
                    <span>Thành Tâm Khởi Quẻ</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* HIỆU ỨNG ĐANG GIEO: 6 HÀO LẦN LƯỢT HIỆN RA */}
        {isCasting && (
          <div className="card-base p-8 text-center space-y-5 animate-fadeIn border-2 border-accent/40 bg-[#FAF5EE]">
            <h3 className="font-heading text-xl font-bold text-primary">
              Đang Thu Thập Khí Vận Lục Hào ({revealedLinesCount}/6)
            </h3>
            <div className="max-w-[200px] mx-auto space-y-2.5 flex flex-col-reverse p-4 bg-surface rounded-card border border-surface-border">
              {Array.from({ length: 6 }, (_, i) => {
                const lineNum = i + 1;
                const isRevealed = lineNum <= revealedLinesCount;
                return (
                  <div
                    key={lineNum}
                    className={`h-3 rounded-full transition-all duration-300 ${
                      isRevealed ? 'bg-primary scale-100 opacity-100' : 'bg-surface-border/40 scale-95 opacity-40'
                    }`}
                  />
                );
              })}
            </div>
            <p className="font-body text-xs text-text-secondary italic">
              "Khởi từ Hào Sơ (dưới cùng) dần thăng lên Hào Thượng (trên cùng)..."
            </p>
          </div>
        )}

        {/* 2. KẾT QUẢ QUẺ CHÍNH & QUẺ BIẾN (SAU KHI GIEO XONG) */}
        {resultData && !isCasting && (
          <div className="space-y-8 animate-fadeIn">
            <div className="card-base p-6 sm:p-8 space-y-6">
              <div className="border-b border-surface-border pb-4">
                <span className="text-xs font-mono font-bold text-accent uppercase tracking-wider block">
                  Kết Quả Chiêm Bái
                </span>
                <h3 className="font-heading text-2xl font-bold text-primary mt-0.5">
                  Quẻ Khởi: "{resultData.cau_hoi}"
                </h3>
              </div>

              {/* Bảng so sánh Quẻ Chính và Quẻ Biến */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {/* Quẻ Chính */}
                <div className="p-6 rounded-card bg-surface border-2 border-accent/40 shadow-subtle space-y-5 text-center">
                  <div>
                    <span className="text-xs font-mono font-bold text-accent uppercase tracking-wider block">
                      Quẻ Chủ Sự
                    </span>
                    <h4 className="font-heading text-3xl font-bold text-primary mt-1">
                      {queChinh.ten_que || resultData.ma_que_chinh}
                    </h4>
                    <span className="text-xs font-body text-text-secondary">
                      Thượng: {queChinh.quai_tren || '--'} • Hạ: {queChinh.quai_duoi || '--'}
                    </span>
                  </div>

                  {/* 6 Hào của Quẻ Chính (Render từ Hào 6 trên xuống Hào 1 dưới) */}
                  <div className="max-w-[180px] mx-auto space-y-3 p-4 bg-[#FAF5EE]/70 rounded-btn border border-surface-border">
                    {danhSachHao.slice().reverse().map((h) => {
                      const isDuong = h.gia_tri === 1;
                      const isDong = h.la_hao_dong;
                      return (
                        <div key={h.vi_tri} className="relative">
                          {renderHaoLine(isDuong, isDong, `chinh-${h.vi_tri}`)}
                          {isDong && (
                            <span className="absolute -right-6 top-0 text-[10px] font-bold text-accent font-mono">
                              O
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {resultData.hao_dong && resultData.hao_dong.length > 0 ? (
                    <div className="text-xs font-body text-primary bg-[#FAF0EE] border border-[#E6C2BC] py-1.5 px-3 rounded-full inline-block">
                      Động tại Hào: <strong>{resultData.hao_dong.map((h) => `Hào ${h}`).join(', ')}</strong>
                    </div>
                  ) : (
                    <div className="text-xs font-body text-text-secondary">
                      Quẻ Tĩnh (Không có hào động)
                    </div>
                  )}
                </div>

                {/* Quẻ Biến (Nếu có hào động) */}
                {queBien ? (
                  <div className="p-6 rounded-card bg-surface border border-surface-border shadow-subtle space-y-5 text-center">
                    <div>
                      <span className="text-xs font-mono font-bold text-[#8A6F52] uppercase tracking-wider block">
                        Quẻ Tương Lai Biến Dịch
                      </span>
                      <h4 className="font-heading text-3xl font-bold text-text-primary mt-1">
                        {queBien.ten_que || resultData.ma_que_bien}
                      </h4>
                      <span className="text-xs font-body text-text-secondary">
                        Thượng: {queBien.quai_tren || '--'} • Hạ: {queBien.quai_duoi || '--'}
                      </span>
                    </div>

                    {/* 6 Hào của Quẻ Biến */}
                    <div className="max-w-[180px] mx-auto space-y-3 p-4 bg-[#FAF5EE]/70 rounded-btn border border-surface-border">
                      {danhSachHao.slice().reverse().map((h) => {
                        // Sau khi biến: hào động đảo ngược giá trị
                        const isDuongBien = h.la_hao_dong ? h.gia_tri === 0 : h.gia_tri === 1;
                        return renderHaoLine(isDuongBien, false, `bien-${h.vi_tri}`);
                      })}
                    </div>

                    <div className="text-xs font-body text-text-secondary bg-[#FAF5EE] border border-surface-border py-1.5 px-3 rounded-full inline-block">
                      Hậu vận biến đổi theo quy luật Âm Dương
                    </div>
                  </div>
                ) : (
                  <div className="p-6 rounded-card bg-[#FAF5EE]/40 border border-dashed border-surface-border flex flex-col justify-center items-center text-center space-y-2">
                    <IconSparkles size={28} className="text-accent" />
                    <h5 className="font-heading text-lg font-bold text-primary">
                      Quẻ Tĩnh Toàn Khí
                    </h5>
                    <p className="text-xs font-body text-text-secondary max-w-xs">
                      Quẻ không có hào biến động, sự việc giữ nguyên trạng thái ổn định lâu dài theo lời Thoán Từ của Quẻ Chính.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* 3. BẢN LUẬN GIẢI THOÁN TỪ & HÀO TỪ TỪ ORCHESTRATOR */}
            <InterpretationTabs luanGiai={luanGiai} systemName="Kinh Dịch Chiêm Bái" />
          </div>
        )}
      </main>
    </div>
  );
}
