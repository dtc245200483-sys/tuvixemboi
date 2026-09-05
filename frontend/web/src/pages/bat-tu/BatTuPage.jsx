import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import {
  IconChartBar,
  IconArrowLeft,
  IconSparkles,
  IconFlame,
  IconDroplet,
  IconLeaf,
  IconMountain,
  IconCoin,
  IconInfoCircle,
  IconShieldCheck
} from '@tabler/icons-react';
import { batTuService, birthProfileService } from '../../services/api';
import InterpretationTabs from '../../components/InterpretationTabs';
import QuotaBadge from '../../components/QuotaBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

// Bảng tra Ngũ Hành của Thiên Can & Địa Chi
const CAN_NGU_HANH = {
  'Giáp': 'Mộc', 'Ất': 'Mộc',
  'Bính': 'Hỏa', 'Đinh': 'Hỏa',
  'Mậu': 'Thổ', 'Kỷ': 'Thổ',
  'Canh': 'Kim', 'Tân': 'Kim',
  'Nhâm': 'Thủy', 'Quý': 'Thủy',
};

const CHI_NGU_HANH = {
  'Tý': 'Thủy', 'Sửu': 'Thổ',
  'Dần': 'Mộc', 'Mão': 'Mộc',
  'Thìn': 'Thổ', 'Tỵ': 'Hỏa',
  'Ngọ': 'Hỏa', 'Mùi': 'Thổ',
  'Thân': 'Kim', 'Dậu': 'Kim',
  'Tuất': 'Thổ', 'Hợi': 'Thủy',
};

const NGU_HANH_COLORS = {
  'Kim': { bg: 'bg-[#FAF5EE]', text: 'text-text-primary', border: 'border-surface-border', bar: 'bg-[#C9962C]' },
  'Mộc': { bg: 'bg-[#FAF5EE]', text: 'text-text-primary', border: 'border-surface-border', bar: 'bg-[#8A6F52]' },
  'Thủy': { bg: 'bg-[#FAF5EE]', text: 'text-text-primary', border: 'border-surface-border', bar: 'bg-[#552218]' },
  'Hỏa': { bg: 'bg-[#FAF0EE]', text: 'text-primary', border: 'border-[#E6C2BC]', bar: 'bg-primary' },
  'Thổ': { bg: 'bg-[#FAF5EE]', text: 'text-text-primary', border: 'border-accent/40', bar: 'bg-[#B38222]' },
};

export default function BatTuPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tuTruData, setTuTruData] = useState(null);
  const [luanGiaiData, setLuanGiaiData] = useState(null);
  const [quotaTrigger, setQuotaTrigger] = useState(0);
  const [isOfflineData, setIsOfflineData] = useState(false);

  const fetchBatTu = async (profileId) => {
    setLoading(true);
    setError(null);
    try {
      let targetId = profileId;
      if (!targetId) {
        const profRes = await birthProfileService.getAll();
        const list = profRes.data?.du_lieu || profRes.data || [];
        if (list.length === 0) {
          navigate('/birth-profile');
          return;
        }
        targetId = list[0].id;
      }

      const res = await batTuService.getTuTru(targetId);
      const data = res.data?.du_lieu || res.data;
      const fromCache =
        res.headers?.['x-from-cache'] === '1' ||
        (typeof navigator !== 'undefined' && !navigator.onLine);
      setIsOfflineData(Boolean(fromCache));

      setTuTruData(data.tu_tru);
      setLuanGiaiData(data.luan_giai);
      setQuotaTrigger((prev) => prev + 1);
    } catch (err) {
      if (err.response) {
        const detail = err.response.data?.detail || err.response.data?.loi;
        setError(typeof detail === 'string' ? detail : 'Không thể tải lá số Bát Tự.');
      } else {
        setError('Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại mạng.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const pId = searchParams.get('profile_id');
    fetchBatTu(pId);
  }, [searchParams]);

  // Tính toán tỷ lệ Ngũ Hành dựa trên 4 Can và 4 Chi
  const nguHanhStats = useMemo(() => {
    if (!tuTruData) return { Kim: 0, Mộc: 0, Thủy: 0, Hỏa: 0, Thổ: 0, total: 8 };

    const counts = { Kim: 0, Mộc: 0, Thủy: 0, Hỏa: 0, Thổ: 0 };
    const trus = [
      tuTruData.tru_nam,
      tuTruData.tru_thang,
      tuTruData.tru_ngay,
      tuTruData.tru_gio,
    ].filter(Boolean);

    trus.forEach((t) => {
      if (t.can && CAN_NGU_HANH[t.can]) counts[CAN_NGU_HANH[t.can]]++;
      if (t.chi && CHI_NGU_HANH[t.chi]) counts[CHI_NGU_HANH[t.chi]]++;
    });

    const total = Object.values(counts).reduce((a, b) => a + b, 0) || 8;
    return { ...counts, total };
  }, [tuTruData]);

  const columns = [
    { title: 'Trụ Năm', desc: 'Tổ Tiên / Gốc Rễ', data: tuTruData?.tru_nam },
    { title: 'Trụ Tháng', desc: 'Cha Mẹ / Lệnh Tháng', data: tuTruData?.tru_thang },
    { title: 'Trụ Ngày (Nhật Chủ)', desc: 'Bản Thân / Vợ Chồng', data: tuTruData?.tru_ngay, isNhatChu: true },
    { title: 'Trụ Giờ', desc: 'Con Cái / Hậu Vận', data: tuTruData?.tru_gio },
  ];

  const nhatChuCan = tuTruData?.tru_ngay?.can || 'Mậu';
  const nhatChuHanh = CAN_NGU_HANH[nhatChuCan] || 'Thổ';

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
                <span>Bát Tự Tứ Trụ Tử Bình</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-accent/30 text-text-on-primary border border-accent/40 font-normal">
                  Chính Tông
                </span>
              </h1>
              <p className="text-xs text-[#D8C7B5] font-body hidden sm:block">
                Cân Bằng Ngũ Hành, Thân Vượng Nhược & Định Đoán Dụng Thần
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <QuotaBadge refreshTrigger={quotaTrigger} className="bg-[#552218] border-surface-border/30 text-text-on-primary" />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-8 py-8 space-y-8">
        {error && (
          <ErrorMessage
            message={error}
            onClose={() => setError(null)}
            className="mb-4"
          />
        )}

        {isOfflineData && !loading && (
          <aside
            role="status"
            className="p-3 sm:p-3.5 rounded-card bg-[#FAF5EE] border border-accent/60 text-text-primary text-xs flex items-center justify-between shadow-subtle"
          >
            <div className="flex items-center gap-2.5">
              <IconInfoCircle size={18} className="text-accent flex-shrink-0" />
              <span>
                <strong>Chế độ ngoại tuyến:</strong> Bạn đang xem bản đã lưu offline (dữ liệu từ bộ nhớ đệm).
              </span>
            </div>
            <span className="px-2.5 py-0.5 rounded-full bg-accent/20 text-primary text-[11px] font-semibold border border-accent/40 flex-shrink-0">
              Bản lưu đệm
            </span>
          </aside>
        )}

        {loading ? (
          <div className="card-base p-12 text-center space-y-4">
            <LoadingSpinner size="lg" text="Đang phân tích Thiên Can - Địa Chi và thiết lập Tứ Trụ..." />
            <p className="font-body text-xs text-text-secondary max-w-sm mx-auto">
              Áp dụng nguyên lý Tử Bình Chân Thuyên để định lượng tỷ lệ Ngũ Hành và tìm Dụng Thần điều hòa bản mệnh.
            </p>
          </div>
        ) : tuTruData ? (
          <>
            {/* 1. KHỐI 8 CHỮ TỨ TRỤ (4 CỘT X 2 HÀNG) */}
            <div className="card-base p-6 sm:p-8 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-surface-border pb-4">
                <div>
                  <h2 className="font-heading text-2xl font-bold text-primary flex items-center gap-2">
                    <IconChartBar size={24} className="text-accent" />
                    <span>Lá Số Tứ Trụ Bát Tự</span>
                  </h2>
                  <p className="text-xs font-body text-text-secondary">
                    4 Cột biểu trưng cho 4 thời khắc: Năm - Tháng - Ngày - Giờ (Thiên Can ở trên, Địa Chi ở dưới).
                  </p>
                </div>
                <div className="text-xs font-body px-3 py-1 rounded-btn bg-[#FAF5EE] border border-accent/40 text-primary font-semibold self-start sm:self-auto">
                  Nhật Chủ: <strong className="text-accent">{nhatChuCan} ({nhatChuHanh})</strong>
                </div>
              </div>

              {/* Lưới 4 cột */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {columns.map((col, idx) => {
                  const can = col.data?.can || '--';
                  const chi = col.data?.chi || '--';
                  const canHanh = CAN_NGU_HANH[can] || '';
                  const chiHanh = CHI_NGU_HANH[chi] || '';

                  return (
                    <div
                      key={idx}
                      className={`p-4 rounded-card border transition-all text-center space-y-3 ${
                        col.isNhatChu
                          ? 'bg-surface border-2 border-accent shadow-subtle ring-2 ring-accent/20'
                          : 'bg-[#FAF5EE]/50 border-surface-border hover:border-accent/50'
                      }`}
                    >
                      <div>
                        <span className={`text-xs font-mono font-bold uppercase tracking-wider block ${col.isNhatChu ? 'text-accent' : 'text-text-secondary'}`}>
                          {col.title}
                        </span>
                        <span className="text-[11px] font-body text-text-secondary/80 block">
                          {col.desc}
                        </span>
                      </div>

                      {/* Ô Can Trên */}
                      <div className="p-3 bg-surface rounded-btn border border-surface-border shadow-xs space-y-1">
                        <span className="text-[10px] font-mono text-text-secondary uppercase block">
                          Thiên Can
                        </span>
                        <div className="font-heading text-3xl font-bold text-primary">
                          {can}
                        </div>
                        <span className="text-xs font-body px-2 py-0.5 rounded-full bg-[#FAF5EE] text-[#8A6F52] inline-block">
                          Hành {canHanh}
                        </span>
                      </div>

                      {/* Ô Chi Dưới */}
                      <div className="p-3 bg-surface rounded-btn border border-surface-border shadow-xs space-y-1">
                        <span className="text-[10px] font-mono text-text-secondary uppercase block">
                          Địa Chi
                        </span>
                        <div className="font-heading text-3xl font-bold text-text-primary">
                          {chi}
                        </div>
                        <span className="text-xs font-body px-2 py-0.5 rounded-full bg-[#FAF5EE] text-[#8A6F52] inline-block">
                          Hành {chiHanh}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* 2. BIỂU ĐỒ CÂN BẰNG NGŨ HÀNH & THẺ PHÂN TÍCH */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Cột 1 & 2: Biểu đồ tỷ lệ 5 Ngũ Hành */}
              <div className="md:col-span-2 card-base p-6 sm:p-7 space-y-5">
                <div className="flex items-center justify-between border-b border-surface-border pb-3">
                  <h3 className="font-heading text-xl font-bold text-primary flex items-center gap-2">
                    <IconSparkles size={20} className="text-accent" />
                    <span>Cân Bằng Ngũ Hành Bản Mệnh</span>
                  </h3>
                  <span className="text-xs font-body text-text-secondary">
                    Tổng 8 tự phối chiếu
                  </span>
                </div>

                <div className="space-y-4">
                  {['Kim', 'Mộc', 'Thủy', 'Hỏa', 'Thổ'].map((hanh) => {
                    const count = nguHanhStats[hanh] || 0;
                    const pct = Math.round((count / nguHanhStats.total) * 100);
                    const cfg = NGU_HANH_COLORS[hanh];

                    return (
                      <div key={hanh} className="space-y-1.5 font-body">
                        <div className="flex justify-between text-xs font-medium">
                          <span className="text-text-primary">Hành {hanh}</span>
                          <span className="text-text-secondary">
                            {count} tự ({pct}%)
                          </span>
                        </div>
                        <div className="w-full h-3 bg-[#FAF5EE] rounded-full overflow-hidden border border-surface-border/60">
                          <div
                            className={`h-full ${cfg.bar} transition-all duration-500 rounded-full`}
                            style={{ width: `${Math.max(pct, count > 0 ? 8 : 0)}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Cột 3: Thẻ Dụng Thần & Thân Vượng/Nhược */}
              <div className="card-base p-6 sm:p-7 space-y-5 flex flex-col justify-between bg-surface border-2 border-accent/40">
                <div className="space-y-4">
                  <div className="flex items-center gap-2 border-b border-surface-border pb-3">
                    <IconShieldCheck size={20} className="text-accent" />
                    <h3 className="font-heading text-xl font-bold text-primary">
                      Định Đoán Tử Bình
                    </h3>
                  </div>

                  {/* Thân Vượng / Nhược */}
                  <div className="p-3.5 rounded-btn bg-[#FAF5EE] border border-surface-border space-y-1">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-text-secondary block">
                      Khí Lực Bản Thân
                    </span>
                    <div className="text-xl font-heading font-bold text-primary">
                      Thân Vượng / Đắc Khí
                    </div>
                    <p className="text-xs font-body text-text-secondary leading-relaxed">
                      Nhật Chủ {nhatChuCan} ({nhatChuHanh}) có trợ lực vững vàng, năng lực hành động và quyết đoán cao.
                    </p>
                  </div>

                  {/* Dụng Thần */}
                  <div className="p-3.5 rounded-btn bg-surface border-2 border-accent/60 space-y-1 shadow-xs">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-accent font-bold block">
                      Dụng Thần Cứu Mệnh
                    </span>
                    <div className="text-xl font-heading font-bold text-primary">
                      Bổ Khuyết Điều Hòa
                    </div>
                    <p className="text-xs font-body text-text-secondary leading-relaxed">
                      Nên ưu tiên các phương vị và màu sắc tương sinh, tiết chế khí lực dư thừa để đạt thái bình an lạc.
                    </p>
                  </div>
                </div>

                <p className="text-[11px] font-body text-text-secondary italic text-center pt-2">
                  * Dụng Thần là chìa khóa then chốt giúp hóa giải xung khắc trong Tứ Trụ.
                </p>
              </div>
            </div>

            {/* 3. BẢN LUẬN GIẢI TỪ ORCHESTRATOR */}
            <InterpretationTabs luanGiai={luanGiaiData} systemName="Bát Tự Tứ Trụ" />
          </>
        ) : null}
      </main>
    </div>
  );
}
