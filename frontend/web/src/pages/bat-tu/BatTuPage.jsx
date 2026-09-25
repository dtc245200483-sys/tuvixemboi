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
  IconShieldCheck,
  IconCheck,
  IconCompass,
  IconTimeline,
  IconPalette,
  IconNumbers,
  IconMapPin,
  IconBriefcase,
  IconLayersIntersect,
  IconAlertTriangle,
  IconUsers,
  IconPlus,
} from '@tabler/icons-react';
import { batTuService, birthProfileService } from '../../services/api';
import InterpretationTabs from '../../components/InterpretationTabs';
import QuotaBadge from '../../components/QuotaBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';
import BatTuPillarDetail from '../../components/BatTuPillarDetail';
import TuViAIChatModal from '../../components/TuViAIChatModal';
import TuViQuickInputBar from '../../components/TuViQuickInputBar';
import {
  CAN_DATA,
  CHI_DATA,
  getThapThan,
  getThanSat,
  PILLAR_DEFINITIONS
} from '../../utils/batTuAnalyzer';

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
  const [birthProfileId, setBirthProfileId] = useState(null);
  const [profiles, setProfiles] = useState([]);

  // Trụ đang được chọn để xem bình luận phân tích riêng (mặc định: Trụ Ngày / Nhật Chủ)
  const [selectedPillarId, setSelectedPillarId] = useState('tru_ngay');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInitialQuestion, setChatInitialQuestion] = useState(null);

  // 1. Tải danh sách hồ sơ & xác định profileId hiện tại
  useEffect(() => {
    let isMounted = true;
    const loadProfiles = async () => {
      try {
        const profRes = await birthProfileService.getAll();
        const list = profRes.data?.du_lieu || profRes.data || [];
        if (!isMounted) return;
        setProfiles(list);

        // Hàm xác định hồ sơ ưu tiên (cô lập an sao nhanh)
        const getPreferredProfile = (items) => {
          if (!items || items.length === 0) return null;
          const savedId = typeof window !== 'undefined' ? localStorage.getItem('selected_ho_so_menh_id') : null;
          let pref = items.find((p) => p.is_default);
          if (!pref && savedId) {
            pref = items.find((p) => String(p.id) === String(savedId));
          }
          if (!pref) {
            const nonQuick = items.filter((p) => !p.is_quick_chart);
            if (nonQuick.length > 0) {
              pref = [...nonQuick].sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0))[0];
            } else {
              pref = [...items].sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0))[0];
            }
          }
          return pref || items[0];
        };

        const qId = searchParams.get('profile_id');
        if (qId) {
          const found = list.find((p) => String(p.id) === String(qId));
          if (found) {
            setBirthProfileId(found.id);
          } else if (list.length > 0) {
            const pref = getPreferredProfile(list);
            console.warn(`Hồ sơ ${qId} không tồn tại trong danh sách, tự động chọn hồ sơ ưu tiên: ${pref?.id}`);
            setBirthProfileId(pref.id);
            navigate(`/bat-tu?profile_id=${pref.id}`, { replace: true });
          } else {
            navigate('/birth-profile');
          }
        } else if (list.length > 0) {
          const pref = getPreferredProfile(list);
          setBirthProfileId(pref.id);
        } else {
          navigate('/birth-profile');
        }
      } catch (err) {
        console.error('Lỗi nạp danh sách hồ sơ:', err);
        if (isMounted) {
          setError('Không thể tải danh sách hồ sơ. Quý bạn vui lòng kiểm tra kết nối mạng và thử lại.');
          setLoading(false);
        }
      }
    };

    loadProfiles();
    return () => {
      isMounted = false;
    };
  }, [searchParams, navigate]);

  // 2. Tải dữ liệu Bát Tự theo birthProfileId
  useEffect(() => {
    if (!birthProfileId) return;

    let isMounted = true;
    const fetchBatTu = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await batTuService.getTuTru(birthProfileId);
        if (!isMounted) return;
        const data = res.data?.du_lieu || res.data;
        const fromCache =
          res.headers?.['x-from-cache'] === '1' ||
          (typeof navigator !== 'undefined' && !navigator.onLine);
        setIsOfflineData(Boolean(fromCache));

        setTuTruData(data.tu_tru);
        setLuanGiaiData(data.luan_giai);
        setQuotaTrigger((prev) => prev + 1);
      } catch (err) {
        if (!isMounted) return;
        if (err.response) {
          const detail = err.response.data?.detail || err.response.data?.loi;
          setError(typeof detail === 'string' ? detail : 'Không thể tải lá số Bát Tự.');
        } else {
          setError('Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại mạng.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchBatTu();
    return () => {
      isMounted = false;
    };
  }, [birthProfileId]);

  // Chuyển đổi hồ sơ
  const handleProfileChange = (e) => {
    const newId = e.target.value;
    setBirthProfileId(newId);
    navigate(`/bat-tu?profile_id=${newId}`);
  };

  const safeProfiles = useMemo(() => (Array.isArray(profiles) ? profiles.filter((p) => p && p.id) : []), [profiles]);

  // Tính toán tỷ lệ Ngũ Hành
  const nguHanhStats = useMemo(() => {
    if (!tuTruData) return { Kim: 0, Mộc: 0, Thủy: 0, Hỏa: 0, Thổ: 0, total: 8 };

    if (tuTruData.ngu_hanh_count) {
      const counts = { ...tuTruData.ngu_hanh_count };
      const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
      return { ...counts, total };
    }

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

  const nhatChuCan = tuTruData?.tru_ngay?.can || 'Giáp';
  const nhatChuHanh = CAN_NGU_HANH[nhatChuCan] || 'Mộc';

  const columns = [
    { id: 'tru_nam', title: 'Trụ Năm', desc: 'Tổ Tiên / Gốc Rễ (1-16t)', data: tuTruData?.tru_nam },
    { id: 'tru_thang', title: 'Trụ Tháng', desc: 'Cha Mẹ / Lệnh Tháng (17-32t)', data: tuTruData?.tru_thang },
    { id: 'tru_ngay', title: 'Trụ Ngày (Nhật Chủ)', desc: 'Bản Thân / Vợ Chồng (33-48t)', data: tuTruData?.tru_ngay, isNhatChu: true },
    { id: 'tru_gio', title: 'Trụ Giờ', desc: 'Con Cái / Hậu Vận (49t+)', data: tuTruData?.tru_gio },
  ];

  // Chi tiết Cách Cục & Vượng Nhược & Dụng Thần
  const cachCuc = tuTruData?.cach_cuc || { ten_cach: 'Bát Tự Chính Tông', mo_ta: 'Cách cục cân bằng khí tiết theo Tử Bình.' };
  const vuongNhuocDetail = tuTruData?.vuong_nhuoc_detail || {
    ket_luan: tuTruData?.vuong_nhuoc || 'Vượng',
    chi_tiet: `Nhật Chủ ${nhatChuCan} (${nhatChuHanh}) khí lực vững vàng.`
  };
  const dungThanDetail = tuTruData?.dung_than_detail || {
    dung_than: tuTruData?.dung_than || 'Hỏa',
    hy_than: tuTruData?.hy_than || 'Mộc',
    ky_than: 'Thủy'
  };
  const caiMenh = tuTruData?.cai_menh || {
    mau_sac: 'Đỏ, Hồng, Tím, Cam',
    con_so: '2, 7 (Số Hỏa Lạc Thư)',
    phuong_huong: 'Hướng Nam',
    nghe_nghiep: 'Công nghệ, truyền thông, năng lượng, văn hóa nghệ thuật'
  };
  const daiVanList = tuTruData?.dai_van || [];
  const tuongTac = tuTruData?.tuong_tac || {};
  const khongVongList = tuTruData?.khong_vong || [];

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
                <span className="hidden md:inline-block text-xs font-mono px-2 py-0.5 rounded-full bg-accent/30 text-text-on-primary border border-accent/40 font-normal">
                  Kinh Điển Trần Khang Ninh
                </span>
              </h1>
              <p className="text-xs text-[#D8C7B5] font-body hidden sm:block">
                Cấu Trúc Tứ Trụ, Thập Thần, Thẩm Định Thân Vượng Nhược & Định Đoán Dụng Thần
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {safeProfiles.length > 0 && (
              <div className="flex items-center gap-1.5 bg-[#552218] px-2.5 py-1 rounded-btn border border-surface-border/30 text-xs">
                <IconUsers size={14} className="text-accent" />
                <select
                  value={birthProfileId || ''}
                  onChange={handleProfileChange}
                  className="bg-transparent text-text-on-primary text-xs outline-none cursor-pointer pr-1 font-medium max-w-[110px] sm:max-w-xs truncate"
                  title="Chọn hồ sơ mệnh chủ để lập lá số Bát Tự"
                >
                  {safeProfiles.map((p) => (
                    <option key={p.id} value={p.id} className="bg-primary text-text-on-primary">
                      {p.ho_ten} ({p.ngay_sinh_duong ? p.ngay_sinh_duong.split('-').reverse().join('/') : ''})
                    </option>
                  ))}
                </select>
                <Link
                  to="/birth-profile"
                  className="ml-1 text-accent hover:text-white transition-colors"
                  title="Thêm hồ sơ mới"
                >
                  <IconPlus size={15} />
                </Link>
              </div>
            )}
            <QuotaBadge refreshTrigger={quotaTrigger} className="bg-[#552218] border-surface-border/30 text-text-on-primary" />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-8 py-8 space-y-8">
        {/* THANH NHẬP THÔNG TIN AN SAO LẬP LÁ SỐ NHANH */}
        <TuViQuickInputBar
          currentProfile={safeProfiles.find((p) => String(p.id) === String(birthProfileId))}
          onProfileCreated={(newId) => {
            birthProfileService.getAll().then((res) => {
              const list = res.data?.du_lieu || res.data || [];
              setProfiles(list);
              setBirthProfileId(newId);
              navigate(`/bat-tu?profile_id=${newId}`);
            });
          }}
          buttonText="An Sao Lập Lá Số"
        />

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
              Áp dụng nguyên lý 'Dự Báo Theo Tử Bình' của tác giả Trần Khang Ninh để định lượng tỷ lệ Ngũ Hành và tìm Dụng Thần điều hòa bản mệnh.
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
                    Nhấn vào từng trụ (Năm, Tháng, Ngày, Giờ) để xem phân tích Thập Thần, Tàng Can, Thần Sát và bình luận riêng.
                  </p>
                </div>
                <div className="text-xs font-body px-3 py-1 rounded-btn bg-[#FAF5EE] border border-accent/40 text-primary font-semibold self-start sm:self-auto flex items-center gap-1.5">
                  <span>Nhật Chủ:</span>
                  <strong className="text-accent text-sm">{nhatChuCan} ({nhatChuHanh})</strong>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-primary/10 text-primary font-mono font-bold">
                    {cachCuc.ten_cach}
                  </span>
                </div>
              </div>

              {/* Lưới 4 cột - Cho phép Click chọn xem riêng */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {columns.map((col) => {
                  const isSelected = selectedPillarId === col.id;
                  const can = col.data?.can || '--';
                  const chi = col.data?.chi || '--';
                  const canHanh = CAN_NGU_HANH[can] || '';
                  const chiHanh = CHI_NGU_HANH[chi] || '';
                  const thapThanInfo = getThapThan(can, nhatChuCan, col.isNhatChu);

                  return (
                    <button
                      key={col.id}
                      type="button"
                      onClick={() => setSelectedPillarId(col.id)}
                      className={`p-4 rounded-card border transition-all duration-200 text-center space-y-3 relative group cursor-pointer focus:outline-hidden ${
                        isSelected
                          ? 'bg-surface border-2 border-[#D4AF37] shadow-md ring-4 ring-[#D4AF37]/20 scale-[1.02] -translate-y-1'
                          : 'bg-[#FAF5EE]/50 border-surface-border hover:border-[#D4AF37]/60 hover:bg-surface hover:-translate-y-0.5 hover:shadow-xs'
                      }`}
                    >
                      {/* Tiêu đề & Chỉ báo trạng thái chọn */}
                      <div className="space-y-0.5">
                        <span className={`text-xs font-mono font-bold uppercase tracking-wider block ${col.isNhatChu ? 'text-accent' : isSelected ? 'text-primary font-extrabold' : 'text-text-secondary'}`}>
                          {col.title}
                        </span>
                        <span className="text-[11px] font-body text-text-secondary/80 block line-clamp-1">
                          {col.desc}
                        </span>
                        <div className="pt-1">
                          {isSelected ? (
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#D4AF37] text-white font-bold inline-flex items-center gap-1 shadow-2xs">
                              <IconSparkles size={11} /> Đang Xem Phân Tích
                            </span>
                          ) : (
                            <span className="text-[10px] font-mono text-text-secondary/70 group-hover:text-accent transition-colors">
                              Nhấn xem riêng
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Ô Can Trên */}
                      <div className="p-3 bg-surface rounded-btn border border-surface-border shadow-xs space-y-1">
                        <span className="text-[10px] font-mono text-text-secondary uppercase block">
                          Thiên Can ({thapThanInfo.short})
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


                      {/* Mũi tên trỏ xuống khi được chọn */}
                      {isSelected && (
                        <div className="absolute -bottom-2.5 left-1/2 -translate-x-1/2 w-4 h-4 bg-surface border-r-2 border-b-2 border-[#D4AF37] transform rotate-45 z-10 hidden md:block" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* KHỐI BÌNH LUẬN & PHÂN TÍCH CHUYÊN SÂU CHO TRỤ ĐƯỢC CHỌN */}
            <BatTuPillarDetail
              selectedPillarId={selectedPillarId}
              onSelectPillar={setSelectedPillarId}
              tuTruData={tuTruData}
              onOpenChatWithQuestion={(q) => {
                setChatInitialQuestion(q);
                setIsChatOpen(true);
              }}
            />

            {/* 2. KHỐI CÁCH CỤC & DỤNG THẦN TỬ BÌNH KINH ĐIỂN */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Thẻ 1: Cách Cục & Thẩm Định Thân Vượng/Nhược (3 Chuẩn Mực Tử Bình) */}
              <div className="card-base p-6 space-y-4 bg-surface border-2 border-primary/20">
                <div className="flex items-center gap-2 border-b border-surface-border pb-3">
                  <IconShieldCheck size={20} className="text-primary" />
                  <h3 className="font-heading text-lg font-bold text-primary">
                    Cách Cục & Thân Mệnh
                  </h3>
                </div>

                <div className="p-3.5 rounded-card bg-[#FAF5EE] border border-surface-border space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono uppercase text-text-secondary">Định Cách Cục</span>
                    <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-primary/10 text-primary font-bold">
                      {cachCuc.thau_can || 'Chính Cách'}
                    </span>
                  </div>
                  <div className="font-heading text-xl font-extrabold text-primary">
                    {cachCuc.ten_cach}
                  </div>
                  <p className="text-xs font-body text-text-secondary leading-relaxed">
                    {cachCuc.mo_ta}
                  </p>
                </div>

                {/* Thẩm định Thân Vượng Nhược */}
                <div className="p-3.5 rounded-card bg-surface border border-surface-border space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono uppercase text-text-secondary">Khí Lực Nhật Chủ</span>
                    <span className={`text-xs font-mono px-2.5 py-0.5 rounded-full font-bold ${
                      vuongNhuocDetail.ket_luan === 'Vượng'
                        ? 'bg-[#E5F0E4] text-[#244A20] border border-[#B8D7B5]'
                        : 'bg-[#FAF0EE] text-[#7A150D] border border-[#E8BAB2]'
                    }`}>
                      Thân {vuongNhuocDetail.ket_luan}
                    </span>
                  </div>
                  <p className="text-xs font-body text-text-secondary leading-relaxed">
                    {vuongNhuocDetail.chi_tiet}
                  </p>
                  <div className="grid grid-cols-3 gap-1.5 pt-1 text-[11px] font-mono text-center">
                    <div className="p-1.5 rounded bg-[#FAF5EE] border border-surface-border">
                      <span className="block text-text-secondary text-[10px]">Đắc Lệnh</span>
                      <strong className={vuongNhuocDetail.dac_lenh ? 'text-green-700' : 'text-text-secondary'}>
                        {vuongNhuocDetail.dac_lenh ? '✓ Có' : '✗ Không'}
                      </strong>
                    </div>
                    <div className="p-1.5 rounded bg-[#FAF5EE] border border-surface-border">
                      <span className="block text-text-secondary text-[10px]">Đắc Địa</span>
                      <strong className={vuongNhuocDetail.dac_dia ? 'text-green-700' : 'text-text-secondary'}>
                        {vuongNhuocDetail.dac_dia ? '✓ Có Gốc' : '✗ Ít Gốc'}
                      </strong>
                    </div>
                    <div className="p-1.5 rounded bg-[#FAF5EE] border border-surface-border">
                      <span className="block text-text-secondary text-[10px]">Đắc Thế</span>
                      <strong className={vuongNhuocDetail.dac_the ? 'text-green-700' : 'text-text-secondary'}>
                        {vuongNhuocDetail.dac_the ? '✓ Có Trợ' : '✗ Ít Trợ'}
                      </strong>
                    </div>
                  </div>
                </div>
              </div>

              {/* Thẻ 2: Dụng Thần & Điều Hầu Dụng Thần */}
              <div className="card-base p-6 space-y-4 bg-surface border-2 border-accent/40">
                <div className="flex items-center gap-2 border-b border-surface-border pb-3">
                  <IconSparkles size={20} className="text-accent" />
                  <h3 className="font-heading text-lg font-bold text-primary">
                    Dụng Thần Cứu Cánh
                  </h3>
                </div>

                <div className="p-3.5 rounded-card bg-[#FAF5EE] border-2 border-accent/50 space-y-2">
                  <span className="text-[11px] font-mono uppercase text-accent font-bold block">
                    Phù Ức Dụng Thần (Trung Hòa)
                  </span>
                  <div className="font-heading text-2xl font-bold text-primary flex items-center justify-between">
                    <span>Hành {dungThanDetail.dung_than}</span>
                    <span className="text-xs font-mono font-normal px-2 py-0.5 rounded-full bg-accent/20 text-[#855B14]">
                      Hỷ Thần: {dungThanDetail.hy_than}
                    </span>
                  </div>
                  <p className="text-xs font-body text-text-secondary leading-relaxed">
                    Ngũ hành cốt tủy giúp tái lập thế quân bình cho bản mệnh. Kỵ thần đối nghịch: <strong>Hành {dungThanDetail.ky_than}</strong>.
                  </p>
                </div>

                {/* Điều Hầu Dụng Thần nếu có */}
                {dungThanDetail.dieu_hau ? (
                  <div className="p-3 rounded-card bg-[#FAF0EE] border border-[#E6C2BC] space-y-1.5">
                    <div className="flex items-center gap-1.5 text-xs font-heading font-bold text-[#8B1C13]">
                      <IconFlame size={16} />
                      <span>Điều Hầu Dụng Thần: Hành {dungThanDetail.dieu_hau.ngu_hanh}</span>
                    </div>
                    <p className="text-[11px] font-body text-text-secondary leading-relaxed">
                      {dungThanDetail.dieu_hau.ly_do}
                    </p>
                  </div>
                ) : (
                  <div className="p-3 rounded-card bg-surface border border-surface-border space-y-1">
                    <span className="text-xs font-heading font-bold text-primary block">
                      Khí Tiết Mùa Sinh Thuần Khiết
                    </span>
                    <p className="text-[11px] font-body text-text-secondary">
                      Khí hậu sinh vào mùa ôn hòa, không bị cực hàn đóng băng hay cực nhiệt thiêu đốt, ưu tiên bồi đắp Dụng Thần Phù Ức.
                    </p>
                  </div>
                )}
              </div>

              {/* Thẻ 3: Phương Pháp Cải Biến Vận Mệnh Đời Sống (Trần Khang Ninh tr. 134) */}
              <div className="card-base p-6 space-y-4 bg-gradient-to-b from-[#FFFDF9] to-[#FAF6EE] border-2 border-surface-border">
                <div className="flex items-center gap-2 border-b border-surface-border pb-3">
                  <IconCompass size={20} className="text-accent" />
                  <h3 className="font-heading text-lg font-bold text-primary">
                    Cải Biến Vận Mệnh Thực Tế
                  </h3>
                </div>

                <div className="space-y-2.5 text-xs font-body">
                  <div className="flex items-start gap-2.5 p-2 rounded-btn bg-surface border border-surface-border/60">
                    <IconPalette size={16} className="text-accent flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-text-primary block text-[11px] font-mono uppercase">Màu Sắc May Mắn:</strong>
                      <span className="text-text-secondary">{caiMenh.mau_sac}</span>
                    </div>
                  </div>

                  <div className="flex items-start gap-2.5 p-2 rounded-btn bg-surface border border-surface-border/60">
                    <IconNumbers size={16} className="text-accent flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-text-primary block text-[11px] font-mono uppercase">Con Số Lạc Thư:</strong>
                      <span className="text-text-secondary">{caiMenh.con_so}</span>
                    </div>
                  </div>

                  <div className="flex items-start gap-2.5 p-2 rounded-btn bg-surface border border-surface-border/60">
                    <IconMapPin size={16} className="text-accent flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-text-primary block text-[11px] font-mono uppercase">Phương Vị Cát Lợi:</strong>
                      <span className="text-text-secondary">{caiMenh.phuong_huong}</span>
                    </div>
                  </div>

                  <div className="flex items-start gap-2.5 p-2 rounded-btn bg-surface border border-surface-border/60">
                    <IconBriefcase size={16} className="text-accent flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-text-primary block text-[11px] font-mono uppercase">Ngành Nghề Tối Ưu:</strong>
                      <span className="text-text-secondary line-clamp-2">{caiMenh.nghe_nghiep}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 3. KHỐI BẢNG 8 ĐẠI VẬN CUỘC ĐỜI (TRẦN KHANG NINH TR. 58-64) */}
            {daiVanList.length > 0 && (
              <div className="card-base p-6 sm:p-8 space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-surface-border pb-4">
                  <div>
                    <h3 className="font-heading text-xl font-bold text-primary flex items-center gap-2">
                      <IconTimeline size={22} className="text-accent" />
                      <span>Bảng 8 Đại Vận Cuộc Đời (Chu Kỳ 10 Năm)</span>
                    </h3>
                    <p className="text-xs font-body text-text-secondary">
                      Quy luật chuyển biến vận trình theo âm dương nam nữ, khởi từ Nguyệt Lệnh Đề Cương.
                    </p>
                  </div>
                  <span className="text-xs font-mono px-3 py-1 rounded-btn bg-[#FAF5EE] border border-surface-border text-primary font-semibold self-start sm:self-auto">
                    Khởi Vận: 10 năm / bước vận
                  </span>
                </div>

                {/* Lưới 8 Đại Vận */}
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
                  {daiVanList.map((dv, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-card bg-[#FAF5EE]/60 border border-surface-border hover:border-accent hover:bg-surface transition-all text-center space-y-2 shadow-2xs group"
                    >
                      <span className="text-[10px] font-mono text-text-secondary uppercase block">
                        Vận {dv.thu_tu}
                      </span>
                      <div className="font-heading font-bold text-lg text-primary group-hover:text-accent transition-colors">
                        {dv.can_chi}
                      </div>
                      <span className="text-[11px] font-body px-1.5 py-0.5 rounded-full bg-surface border border-surface-border text-[#855B14] font-semibold block">
                        {dv.thap_than_short || dv.thap_than}
                      </span>
                      <span className="text-[10px] font-mono text-text-secondary block">
                        {dv.tuoi_range}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 4. BIỂU ĐỒ CÂN BẰNG NGŨ HÀNH & TƯƠNG TÁC CỤC DIỆN */}
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

              {/* Cột 3: Tương Tác Can Chi & Không Vong */}
              <div className="card-base p-6 sm:p-7 space-y-4 bg-surface border-2 border-surface-border">
                <div className="flex items-center gap-2 border-b border-surface-border pb-3">
                  <IconLayersIntersect size={20} className="text-accent" />
                  <h3 className="font-heading text-lg font-bold text-primary">
                    Tương Tác Cục Diện
                  </h3>
                </div>

                <div className="space-y-3 text-xs font-body">
                  {/* Không Vong */}
                  {khongVongList.length > 0 && (
                    <div className="p-2.5 rounded-btn bg-[#FAF5EE] border border-surface-border space-y-1">
                      <span className="font-mono text-[10px] text-accent uppercase font-bold block">
                        Tuần Không (Không Vong)
                      </span>
                      <p className="text-text-secondary">
                        Chi <strong>{khongVongList.join(', ')}</strong> lâm Không Vong (lực tác động giảm bớt).
                      </p>
                    </div>
                  )}

                  {/* Lục Hợp / Tam Hợp */}
                  {(tuongTac.chi_luc_hop?.length > 0 || tuongTac.chi_tam_hop?.length > 0) && (
                    <div className="p-2.5 rounded-btn bg-surface border border-surface-border space-y-1">
                      <span className="font-mono text-[10px] text-green-700 uppercase font-bold block">
                        Hợp Cục Tương Thân
                      </span>
                      <p className="text-text-secondary">
                        {[...(tuongTac.chi_luc_hop || []), ...(tuongTac.chi_tam_hop || [])].join(' • ')}
                      </p>
                    </div>
                  )}

                  {/* Lục Xung / Tương Hình */}
                  {(tuongTac.chi_luc_xung?.length > 0 || tuongTac.chi_tuong_hinh?.length > 0) && (
                    <div className="p-2.5 rounded-btn bg-[#FAF0EE] border border-[#E6C2BC] space-y-1">
                      <span className="font-mono text-[10px] text-[#8B1C13] uppercase font-bold block">
                        Xung Hình Đòi Hỏi Hóa Giải
                      </span>
                      <p className="text-text-secondary">
                        {[...(tuongTac.chi_luc_xung || []), ...(tuongTac.chi_tuong_hinh || [])].join(' • ')}
                      </p>
                    </div>
                  )}

                  {(!tuongTac.chi_luc_hop?.length && !tuongTac.chi_tam_hop?.length && !tuongTac.chi_luc_xung?.length && !tuongTac.chi_tuong_hinh?.length) && (
                    <p className="text-text-secondary italic text-center py-4">
                      Tứ Trụ khí thế bình ổn, không gặp đại xung đại hình, bản mệnh yên tĩnh thuận hòa.
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* 5. BẢN LUẬN GIẢI TỪ ORCHESTRATOR */}
            <InterpretationTabs
              luanGiai={luanGiaiData}
              systemName="Bát Tự Tứ Trụ"
              birthProfileId={birthProfileId}
              selectedPillarId={selectedPillarId}
              onSelectPillar={setSelectedPillarId}
              tuTruData={tuTruData}
            />

            {/* Modal Hỏi Đáp AI khi người dùng bấm hỏi sâu về từng Trụ */}
            {isChatOpen && birthProfileId && (
              <TuViAIChatModal
                birthProfileId={birthProfileId}
                chartData={{
                  userName: 'Mệnh chủ Bát Tự',
                  napAmVal: `Nhật Chủ ${nhatChuCan} (${nhatChuHanh})`,
                  cucVal: cachCuc.ten_cach,
                }}
                initialQuestion={chatInitialQuestion}
                onClose={() => {
                  setIsChatOpen(false);
                  setChatInitialQuestion(null);
                }}
              />
            )}
          </>
        ) : null}
      </main>
    </div>
  );
}
