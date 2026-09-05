import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import {
  IconCompass,
  IconArrowLeft,
  IconRefresh,
  IconSparkles,
  IconUser,
  IconStar,
  IconInfoCircle,
  IconZoomIn,
  IconFlame,
  IconShieldCheck
} from '@tabler/icons-react';
import { tuViService, birthProfileService } from '../../services/api';
import InterpretationTabs from '../../components/InterpretationTabs';
import QuotaBadge from '../../components/QuotaBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

// Tọa độ CSS Grid (4x4) chuẩn truyền thống cho 12 Địa Chi (0 = Tý ... 11 = Hợi)
const PALACE_GRID_POSITIONS = {
  0: { row: 4, col: 3, name: 'Tý' },
  1: { row: 4, col: 2, name: 'Sửu' },
  2: { row: 4, col: 1, name: 'Dần' },
  3: { row: 3, col: 1, name: 'Mão' },
  4: { row: 2, col: 1, name: 'Thìn' },
  5: { row: 1, col: 1, name: 'Tỵ' },
  6: { row: 1, col: 2, name: 'Ngọ' },
  7: { row: 1, col: 3, name: 'Mùi' },
  8: { row: 1, col: 4, name: 'Thân' },
  9: { row: 2, col: 4, name: 'Dậu' },
  10: { row: 3, col: 4, name: 'Tuất' },
  11: { row: 4, col: 4, name: 'Hợi' },
};

// Vòng Tràng Sinh danh sách để phát hiện sao Tràng Sinh hiển thị ở góc
const TRANG_SINH_STARS = [
  'Tràng Sinh', 'Mộc Dục', 'Quan Đới', 'Lâm Quan', 'Đế Vượng',
  'Suy', 'Bệnh', 'Tử', 'Mộ', 'Tuyệt', 'Thai', 'Dưỡng'
];

// Hàm trả về màu sắc theo Ngũ Hành phong thủy chuẩn Design System
const getElementStyle = (nguHanh) => {
  switch ((nguHanh || '').trim().toLowerCase()) {
    case 'kim':
      return {
        text: 'text-slate-700 font-bold',
        badge: 'bg-slate-100 text-slate-700 border-slate-300',
        dot: 'bg-slate-400'
      };
    case 'mộc':
      return {
        text: 'text-emerald-700 font-bold',
        badge: 'bg-emerald-50 text-emerald-800 border-emerald-300',
        dot: 'bg-emerald-500'
      };
    case 'thủy':
      return {
        text: 'text-blue-700 font-bold',
        badge: 'bg-blue-50 text-blue-800 border-blue-300',
        dot: 'bg-blue-500'
      };
    case 'hỏa':
      return {
        text: 'text-rose-700 font-bold',
        badge: 'bg-rose-50 text-rose-800 border-rose-300',
        dot: 'bg-rose-500'
      };
    case 'thổ':
      return {
        text: 'text-amber-800 font-bold',
        badge: 'bg-amber-50 text-amber-800 border-amber-300',
        dot: 'bg-amber-500'
      };
    default:
      return {
        text: 'text-text-primary font-bold',
        badge: 'bg-[#FAF5EE] text-text-primary border-surface-border',
        dot: 'bg-gray-400'
      };
  }
};

// Hàm hiển thị huy hiệu độ sáng sao (Miếu/Vượng/Đắc/Bình/Hãm)
const renderDacHam = (dacHam) => {
  if (!dacHam) return null;
  const val = dacHam.toUpperCase();
  let color = 'text-text-primary';
  let title = 'Bình hòa';
  if (val === 'M') {
    color = 'text-rose-600 font-bold';
    title = 'Miếu địa (Sáng nhất, rực rỡ)';
  } else if (val === 'V') {
    color = 'text-amber-600 font-bold';
    title = 'Vượng địa (Rất sáng, tốt lành)';
  } else if (val === 'Đ') {
    color = 'text-emerald-600 font-bold';
    title = 'Đắc địa (Tốt đẹp, đắc thời)';
  } else if (val === 'H') {
    color = 'text-gray-400 italic underline';
    title = 'Hãm địa (Tối tăm, bất lợi)';
  }
  return (
    <span className={`text-[10px] ml-0.5 ${color}`} title={title}>
      ({val})
    </span>
  );
};

// Hiển thị huy hiệu Tứ Hóa
const renderHoaBadge = (hoa) => {
  if (!hoa) return null;
  const map = {
    'Hóa Lộc': 'bg-emerald-600 text-white',
    'Hóa Quyền': 'bg-rose-600 text-white',
    'Hóa Khoa': 'bg-blue-600 text-white',
    'Hóa Kỵ': 'bg-purple-700 text-white'
  };
  const style = map[hoa] || 'bg-amber-600 text-white';
  const label = hoa.replace('Hóa ', '');
  return (
    <span className={`text-[9px] px-1 py-0.2 rounded font-bold ml-1 ${style}`} title={hoa}>
      {label}
    </span>
  );
};

// Danh mục 14 chính tinh và nhóm sát hung tinh
const CHINH_TINH_NAMES = [
  'Tử Vi', 'Liêm Trinh', 'Thiên Đồng', 'Vũ Khúc', 'Thái Dương', 'Thiên Cơ',
  'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương',
  'Thất Sát', 'Phá Quân'
];

const HUNG_SAT_TYPES = ['sat_tinh', 'hung_tinh', 'bai_tinh'];

// Phân loại sao an toàn dự phòng
const phanLoaiSao = (cung) => {
  const allStars = cung?.danh_sach_sao || [];

  let chinhTinh = (cung?.chinh_tinh && cung.chinh_tinh.length > 0) ? [...cung.chinh_tinh] : [];
  if (chinhTinh.length === 0) {
    chinhTinh = allStars.filter((s) => s.loai === 'chinh_tinh' || CHINH_TINH_NAMES.includes(s.ten));
  }

  let satTinh = (cung?.sat_tinh && cung.sat_tinh.length > 0) ? [...cung.sat_tinh] : [];
  if (satTinh.length === 0) {
    satTinh = allStars.filter((s) => HUNG_SAT_TYPES.includes(s.loai) && !CHINH_TINH_NAMES.includes(s.ten));
  }

  let catTinh = (cung?.cat_tinh && cung.cat_tinh.length > 0) ? [...cung.cat_tinh] : [];
  if (catTinh.length === 0) {
    const chinhNames = new Set(chinhTinh.map((s) => s.ten));
    const satNames = new Set(satTinh.map((s) => s.ten));
    catTinh = allStars.filter((s) => !chinhNames.has(s.ten) && !satNames.has(s.ten) && !TRANG_SINH_STARS.includes(s.ten));
  }

  return { chinhTinh, catTinh, satTinh, allStars };
};

const getCanChiCung = (cung) => {
  if (!cung) return '';
  if (cung.can_chi_cung) return cung.can_chi_cung;
  if (cung.can_cung && cung.ten_dia_chi) return `${cung.can_cung} ${cung.ten_dia_chi}`;
  return cung.ten_dia_chi || '';
};

const getThanCuText = (laSo, cacCung) => {
  if (laSo?.than_cu) return laSo.than_cu;
  const thanCung = (cacCung || []).find((c) => c.la_cung_than);
  if (thanCung) return thanCung.ten_cung_chuc_nang;
  return '--';
};

const getMenhCuText = (laSo, cacCung) => {
  if (laSo?.ten_cung_menh) return laSo.ten_cung_menh;
  const menhCung = (cacCung || []).find((c) => (c.ten_cung_chuc_nang || '').includes('Mệnh'));
  if (menhCung) return getCanChiCung(menhCung);
  return '--';
};

export default function TuViPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [laSoData, setLaSoData] = useState(null);
  const [luanGiaiData, setLuanGiaiData] = useState(null);
  const [selectedPalace, setSelectedPalace] = useState(null);
  const [quotaTrigger, setQuotaTrigger] = useState(0);
  const [isOfflineData, setIsOfflineData] = useState(false);

  const fetchLaSo = async (profileId) => {
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

      const res = await tuViService.getLaSo(targetId);
      const data = res.data?.du_lieu || res.data;
      const fromCache =
        res.headers?.['x-from-cache'] === '1' ||
        (typeof navigator !== 'undefined' && !navigator.onLine);
      setIsOfflineData(Boolean(fromCache));

      setLaSoData(data.la_so);
      setLuanGiaiData(data.luan_giai);
      setQuotaTrigger((prev) => prev + 1);

      // Mặc định chọn cung Mệnh
      const cungList = data.la_so?.cac_cung || [];
      const menhCung = cungList.find((c) => (c.ten_cung_chuc_nang || '').includes('Mệnh')) || cungList[0];
      setSelectedPalace(menhCung);
    } catch (err) {
      if (err.response) {
        const detail = err.response.data?.detail || err.response.data?.loi;
        setError(typeof detail === 'string' ? detail : 'Không thể tải lá số Tử Vi.');
      } else {
        setError('Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại mạng.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const pId = searchParams.get('profile_id');
    fetchLaSo(pId);
  }, [searchParams]);

  const basicInfo = laSoData?.thong_tin_co_ban || {};
  const cucInfo = laSoData?.cuc || {};
  const cacCung = laSoData?.cac_cung || [];

  // Tính quan hệ Ngũ Hành giữa Mệnh và Cục
  const tuongSinhTuongKhac = useMemo(() => {
    if (!laSoData?.ngu_hanh_nap_am || !cucInfo?.ngu_hanh) return '';
    const menhHanh = laSoData.ngu_hanh_nap_am.split(' ').pop();
    const cucHanh = cucInfo.ngu_hanh;
    if (menhHanh === cucHanh) return 'Mệnh Cục Tỷ Hòa (Cuộc đời bình ổn, hài hòa)';
    
    // Tương sinh
    const sinhMap = { 'Kim': 'Thủy', 'Thủy': 'Mộc', 'Mộc': 'Hỏa', 'Hỏa': 'Thổ', 'Thổ': 'Kim' };
    if (sinhMap[cucHanh] === menhHanh) return `Cục (${cucHanh}) sinh Mệnh (${menhHanh}) — Đại Cát! Được hoàn cảnh ưu ái.`;
    if (sinhMap[menhHanh] === cucHanh) return `Mệnh (${menhHanh}) sinh Cục (${cucHanh}) — Vất vả, phải cống hiến cho thời cuộc.`;

    // Tương khắc
    const khacMap = { 'Kim': 'Mộc', 'Mộc': 'Thổ', 'Thổ': 'Thủy', 'Thủy': 'Hỏa', 'Hỏa': 'Kim' };
    if (khacMap[cucHanh] === menhHanh) return `Cục (${cucHanh}) khắc Mệnh (${menhHanh}) — Gian nan, hay gặp nghịch cảnh thử thách.`;
    if (khacMap[menhHanh] === cucHanh) return `Mệnh (${menhHanh}) khắc Cục (${cucHanh}) — Bản lĩnh vượt khó, tự tay lập nghiệp.`;
    return '';
  }, [laSoData, cucInfo]);

  // Tìm các cung liên hệ của cung đang chọn (Tam hợp, Xung chiếu)
  const relatedPalaces = useMemo(() => {
    if (!selectedPalace || cacCung.length < 12) return null;
    const pos = selectedPalace.vi_tri_dia_chi;
    const xungPos = (pos + 6) % 12;
    const tamHop1 = (pos + 4) % 12;
    const tamHop2 = (pos + 8) % 12;

    const findCung = (p) => cacCung.find((c) => c.vi_tri_dia_chi === p);
    return {
      xungChieu: findCung(xungPos),
      tamHop: [findCung(tamHop1), findCung(tamHop2)],
    };
  }, [selectedPalace, cacCung]);

  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* Header thanh điều hướng - Chuẩn Nâu Đỏ Trầm #6B2B1F */}
      <header className="bg-primary text-text-on-primary border-b border-[#552218] px-4 sm:px-8 py-3.5 shadow-subtle sticky top-0 z-20">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              className="p-1.5 rounded-btn bg-[#552218] text-text-on-primary hover:bg-[#431A12] transition-colors"
              title="Quay lại Tổng quan"
            >
              <IconArrowLeft size={18} />
            </Link>
            <div>
              <h1 className="font-heading text-xl sm:text-2xl font-bold tracking-wide text-text-on-primary flex items-center gap-2">
                <span>Tử Vi Đẩu Số Toàn Thư</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-[#552218] text-accent font-bold border border-accent/30">
                  Kinh Điển 108 Sao
                </span>
              </h1>
              <p className="text-xs text-text-on-primary/80 font-body hidden sm:block">
                Thiên Bàn 12 Cung Chuẩn Cổ Học — Phân Cột Cát Hung & Luận Vận Hạn Trọn Đời
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <QuotaBadge refreshTrigger={quotaTrigger} />
          </div>
        </div>
      </header>

      {/* Nội dung chính */}
      <main className="max-w-7xl mx-auto px-2 sm:px-6 py-6 space-y-6">
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
            className="p-3 sm:p-3.5 rounded-card bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center justify-between shadow-subtle"
          >
            <div className="flex items-center gap-2.5">
              <IconInfoCircle size={18} className="text-accent flex-shrink-0" />
              <span>
                <strong>Chế độ ngoại tuyến:</strong> Bạn đang xem bản đã lưu offline (dữ liệu từ bộ nhớ đệm).
              </span>
            </div>
            <span className="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-900 text-[11px] font-bold border border-amber-300 flex-shrink-0">
              Bản lưu đệm
            </span>
          </aside>
        )}

        {loading ? (
          <div className="card-base p-12 text-center space-y-4 shadow-card">
            <LoadingSpinner size="lg" text="Đang an toàn diện 108 vì sao và khởi tạo Thiên Bàn Tử Vi..." />
            <p className="font-body text-xs text-text-secondary max-w-sm mx-auto">
              Hệ thống an sao kinh điển kết hợp Vòng Thái Tuế, Bác Sĩ, Tràng Sinh, Tứ Hóa, Tuần Triệt và định hình lá số chuẩn xác.
            </p>
          </div>
        ) : laSoData ? (
          <>
            {/* KHỐI THIÊN BÀN 12 CUNG KINH ĐIỂN */}
            <div className="card-base p-3 sm:p-6 space-y-4 shadow-card">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-3">
                <div>
                  <h2 className="font-heading text-xl sm:text-2xl font-bold text-primary flex items-center gap-2">
                    <IconCompass size={24} className="text-accent" />
                    <span>Thiên Bàn 12 Cung Bản Mệnh</span>
                  </h2>
                  <p className="text-xs text-text-secondary font-body">
                    Chính tinh in đậm kèm độ sáng (M/V/Đ/H). Cột trái là Cát Tinh, cột phải là Hung/Sát Tinh. Bấm vào ô cung để xem luận bàn chi tiết.
                  </p>
                </div>
                {selectedPalace && (
                  <div className="text-xs font-body px-3 py-1.5 rounded-btn bg-[#FAF5EE] border border-surface-border text-text-primary self-start sm:self-auto flex items-center gap-1.5 shadow-subtle">
                    <span>Đang xem:</span>
                    <strong className="text-primary font-bold">{selectedPalace.ten_cung_chuc_nang}</strong>
                    <span className="font-mono text-accent">({getCanChiCung(selectedPalace)})</span>
                    {selectedPalace.la_cung_than && (
                      <span className="px-1.5 py-0.2 rounded-full bg-rose-700 text-white font-bold text-[10px] shadow-xs">
                        THÂN
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* BÀN CỜ 4x4 TRUYỀN THỐNG VỚI CUỘN NGANG VÀ VIỀN NHÃ NHẶN */}
              <div className="overflow-x-auto pb-2">
                <div className="min-w-[880px] grid grid-cols-4 grid-rows-4 gap-2 bg-[#F4EDE2]/70 p-2 rounded-card border border-surface-border">
                  {/* Render 12 cung theo vị trí Grid cố định 4x4 */}
                  {cacCung.map((cung) => {
                    const pos = PALACE_GRID_POSITIONS[cung.vi_tri_dia_chi] || { row: 1, col: 1, name: '' };
                    const isSelected = selectedPalace?.vi_tri_dia_chi === cung.vi_tri_dia_chi;
                    const { chinhTinh, catTinh, satTinh, allStars } = phanLoaiSao(cung);
                    const canChiText = getCanChiCung(cung);

                    // Tìm sao Tràng Sinh nếu có trong cung
                    const saoTrangSinh = allStars.find((s) => TRANG_SINH_STARS.includes(s.ten));

                    return (
                      <div
                        key={cung.vi_tri_dia_chi}
                        onClick={() => setSelectedPalace(cung)}
                        style={{
                          gridRow: pos.row,
                          gridColumn: pos.col,
                        }}
                        className={`min-h-[190px] sm:min-h-[215px] p-2 rounded-btn cursor-pointer transition-all flex flex-col justify-between select-none ${
                          isSelected
                            ? 'bg-surface border-2 border-accent shadow-md ring-2 ring-accent/30'
                            : 'bg-surface/95 border border-surface-border hover:border-accent/70 hover:bg-[#FAF5EE]/70 shadow-subtle'
                        }`}
                      >
                        {/* 1. Header ô cung: Tên cung, Can Chi, Huy hiệu Thân, Tuần, Triệt */}
                        <div className="border-b border-surface-border/60 pb-1">
                          <div className="flex items-center justify-between">
                            <span className="font-heading text-xs sm:text-sm font-bold truncate tracking-tight text-primary uppercase">
                              {cung.ten_cung_chuc_nang}
                            </span>
                            <span className="text-[10px] sm:text-xs font-mono font-bold px-1.5 py-0.2 rounded bg-[#FAF5EE] text-text-primary border border-surface-border">
                              {canChiText}
                            </span>
                          </div>

                          {/* Dải huy hiệu trạng thái: THÂN, TUẦN, TRIỆT */}
                          <div className="flex items-center gap-1 mt-0.5">
                            {cung.la_cung_than && (
                              <span className="px-1.5 py-0.2 rounded-full bg-rose-700 text-white font-bold text-[9px] shadow-xs">
                                THÂN
                              </span>
                            )}
                            {cung.co_tuan && (
                              <span className="px-1.5 py-0.2 rounded font-bold text-[9px] bg-amber-100 text-amber-900 border border-amber-300">
                                TUẦN
                              </span>
                            )}
                            {cung.co_triet && (
                              <span className="px-1.5 py-0.2 rounded font-bold text-[9px] bg-rose-100 text-rose-900 border border-rose-300">
                                TRIỆT
                              </span>
                            )}
                          </div>
                        </div>

                        {/* 2. Phần Chính Tinh (In đậm, độ sáng M/V/Đ/H, Tứ Hóa) */}
                        <div className="py-1 min-h-[34px]">
                          {chinhTinh.length > 0 ? (
                            <div className="flex flex-wrap gap-x-2 gap-y-0.5 items-center">
                              {chinhTinh.map((s, idx) => {
                                const style = getElementStyle(s.ngu_hanh);
                                return (
                                  <div key={idx} className="flex items-center leading-tight">
                                    <span className={`text-xs sm:text-sm font-bold font-heading ${style.text}`}>
                                      {s.ten}
                                    </span>
                                    {renderDacHam(s.dac_ham)}
                                    {renderHoaBadge(s.hoa)}
                                  </div>
                                );
                              })}
                            </div>
                          ) : (
                            <span className="text-[11px] text-text-secondary italic font-body">
                              Vô chính diệu
                            </span>
                          )}
                        </div>

                        {/* 3. Phần Phụ Tinh Chia 2 Cột: Cát Tinh (trái) vs Hung/Sát Tinh (phải) */}
                        <div className="grid grid-cols-2 gap-1 border-t border-surface-border/40 pt-1 flex-1 text-[10px] sm:text-[11px] font-body overflow-hidden">
                          {/* Cột Trái: CÁT TINH */}
                          <div className="space-y-0.5 border-r border-surface-border/40 pr-1">
                            {catTinh.map((s, idx) => {
                              const style = getElementStyle(s.ngu_hanh);
                              return (
                                <div key={idx} className="flex items-center justify-between leading-snug">
                                  <span className={`truncate font-bold ${style.text}`}>
                                    {s.ten}
                                  </span>
                                  {renderHoaBadge(s.hoa)}
                                </div>
                              );
                            })}
                          </div>

                          {/* Cột Phải: HUNG/SÁT TINH & BẠI TINH */}
                          <div className="space-y-0.5 pl-1">
                            {satTinh.map((s, idx) => (
                              <div key={idx} className="flex items-center justify-between leading-snug text-rose-800 font-medium">
                                <span className="truncate font-bold">
                                  {s.ten}
                                </span>
                                {renderDacHam(s.dac_ham)}
                                {renderHoaBadge(s.hoa)}
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* 4. Footer ô cung: Đại Vận, Tràng Sinh, Tiểu Hạn */}
                        <div className="border-t border-surface-border/50 pt-1 flex items-center justify-between text-[10px] font-mono text-text-secondary">
                          <div className="font-bold text-primary text-[11px]" title={`Đại vận từ ${cung.dai_van_tuoi} đến ${(cung.dai_van_tuoi || 0) + 9} tuổi`}>
                            {cung.dai_van_tuoi !== undefined ? cung.dai_van_tuoi : ''}
                          </div>
                          {saoTrangSinh && (
                            <div className="text-[10px] font-serif font-bold italic text-purple-800" title="Vòng Tràng Sinh">
                              {saoTrangSinh.ten}
                            </div>
                          )}
                          <div className="text-[10px]" title={`Tiểu hạn năm ${cung.tieu_han_chi}`}>
                            {cung.tieu_han_chi || ''}
                          </div>
                        </div>
                      </div>
                    );
                  })}

                  {/* THIÊN TÂM / Ô TRUNG TÂM (2x2 ở giữa Thiên Bàn) - Chuẩn Nền Trắng Sáng */}
                  <div
                    style={{ gridRow: '2 / span 2', gridColumn: '2 / span 2' }}
                    className="bg-surface/98 border-2 border-accent/50 rounded-card p-3 sm:p-5 flex flex-col justify-between shadow-subtle relative overflow-hidden"
                  >
                    {/* Header Trung Tâm */}
                    <div className="text-center space-y-1 border-b border-surface-border/70 pb-2">
                      <div className="flex items-center justify-center gap-2">
                        <span className="bg-[#FAF5EE] text-primary px-3 py-0.5 rounded-full border border-surface-border text-[10px] sm:text-xs tracking-widest inline-flex items-center gap-1.5 uppercase font-medium">
                          <IconCompass size={14} className="text-accent" />
                          LÁ SỐ TỬ VI ĐẨU SỐ TOÀN THƯ
                        </span>
                      </div>
                      <h3 className="font-heading text-lg sm:text-2xl font-bold text-primary">
                        {basicInfo.ho_ten || 'Mệnh Chủ'}
                      </h3>
                      <div className="text-xs font-body text-text-secondary">
                        {basicInfo.am_duong_nam_nu || (basicInfo.gioi_tinh === 'nam' ? 'Dương Nam' : 'Âm Nữ')}
                      </div>
                    </div>

                    {/* Bảng Thông Số Chi Tiết - chia ô rõ ràng với đường viền nhã nhặn */}
                    <div className="grid grid-cols-2 gap-x-3 gap-y-1.5 text-xs font-body py-2 divide-x divide-surface-border">
                      <div className="space-y-1 pr-2">
                        <div className="flex justify-between">
                          <span className="text-text-secondary">Dương Lịch:</span>
                          <strong className="text-text-primary font-medium">
                            {basicInfo.ngay_duong_str || (basicInfo.ngay_sinh_duong ? `${basicInfo.ngay_sinh_duong.slice(8, 10)}/${basicInfo.ngay_sinh_duong.slice(5, 7)}/${basicInfo.ngay_sinh_duong.slice(0, 4)}` : '--')}
                          </strong>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-text-secondary">Giờ Sinh:</span>
                          <strong className="text-text-primary font-medium">
                            {basicInfo.gio_sinh_str || (basicInfo.gio_sinh !== undefined ? `Giờ ${basicInfo.chi_gio || basicInfo.gio_sinh}` : '--')}
                          </strong>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-text-secondary">Âm Lịch:</span>
                          <strong className="text-accent font-bold">
                            {basicInfo.ngay_am_str || (basicInfo.ngay_sinh_am ? `${basicInfo.ngay_sinh_am.slice(8, 10)}/${basicInfo.ngay_sinh_am.slice(5, 7)}/${basicInfo.ngay_sinh_am.slice(0, 4)} (Âm)` : '--')}
                          </strong>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-text-secondary">Năm Can Chi:</span>
                          <strong className="text-primary font-bold">
                            {basicInfo.can_chi_nam || laSoData.can_chi_nam || '--'}
                          </strong>
                        </div>
                      </div>

                      <div className="space-y-1 pl-3">
                        <div className="flex justify-between">
                          <span className="text-text-secondary">Bản Mệnh:</span>
                          <strong className="text-primary font-bold">
                            {laSoData.ngu_hanh_nap_am || '--'}
                          </strong>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-text-secondary">Cục Số:</span>
                          <strong className="text-accent font-bold">
                            {cucInfo.ten || cucInfo.cuc_so || '--'}
                          </strong>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-text-secondary">Mệnh Cư:</span>
                          <strong className="text-primary font-bold">
                            {getMenhCuText(laSoData, cacCung)}
                          </strong>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-text-secondary">Thân Cư:</span>
                          <strong className="text-rose-700 font-bold">{getThanCuText(laSoData, cacCung)}</strong>
                        </div>
                      </div>
                    </div>

                    {/* Footer Thiên Tâm: Mệnh Chủ, Thân Chủ, Tương sinh Mệnh - Cục */}
                    <div className="border-t border-surface-border/70 pt-2 text-[11px] font-body space-y-1 bg-[#FAF5EE]/70 -mx-3 -mb-3 sm:-mx-5 sm:-mb-5 p-2.5 rounded-b-card text-text-secondary">
                      <div className="flex items-center justify-between">
                        <div>Mệnh Chủ: <strong className="text-text-primary font-medium">{laSoData.menh_chu || '--'}</strong></div>
                        <div>Thân Chủ: <strong className="text-text-primary font-medium">{laSoData.than_chu || '--'}</strong></div>
                        <div>Đại Vận: <strong className="text-accent font-bold">{laSoData.chieu_dai_van || 'Thuận'}</strong></div>
                      </div>
                      {tuongSinhTuongKhac && (
                        <div className="text-[10px] text-accent font-medium text-center truncate">
                          {tuongSinhTuongKhac}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* BẢNG CHI TIẾT CUNG ĐANG CHỌN (INSPECTOR CHUYÊN SÂU) */}
              {selectedPalace && (() => {
                const { chinhTinh: selChinhTinh, catTinh: selCatTinh, satTinh: selSatTinh, allStars: selAllStars } = phanLoaiSao(selectedPalace);
                const selCanChi = getCanChiCung(selectedPalace);
                return (
                  <div className="mt-4 p-4 sm:p-5 rounded-card bg-[#FAF5EE] border border-accent/40 animate-fadeIn space-y-4 shadow-subtle">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-surface-border/70 pb-3">
                      <div className="flex items-center gap-2.5">
                        <IconStar size={22} className="text-accent" />
                        <h3 className="font-heading text-lg sm:text-xl font-bold text-primary">
                          Chi Tiết Cung {selectedPalace.ten_cung_chuc_nang} — An Tại {selCanChi}
                        </h3>
                        {selectedPalace.la_cung_than && (
                          <span className="px-2 py-0.5 rounded-full bg-rose-700 text-white font-bold text-xs shadow-xs">
                            CUNG AN THÂN
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-text-secondary font-body">
                        <span>Đại vận: <strong className="text-primary font-bold">{selectedPalace.dai_van_tuoi !== undefined ? `${selectedPalace.dai_van_tuoi} - ${selectedPalace.dai_van_tuoi + 9}` : '--'} tuổi</strong></span>
                        <span>•</span>
                        <span>Hội tụ: <strong className="text-primary font-bold">{selAllStars.length} tinh tú</strong></span>
                      </div>
                    </div>

                    {/* Thông tin Tam hợp & Xung chiếu */}
                    {relatedPalaces && (
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs font-body">
                        <div className="p-2.5 rounded-btn bg-surface border border-surface-border shadow-subtle">
                          <span className="text-text-secondary text-[11px] block">Xung Chiếu (Đối Cung):</span>
                          <strong className="text-primary font-heading font-bold text-sm">
                            {relatedPalaces.xungChieu?.ten_cung_chuc_nang} ({getCanChiCung(relatedPalaces.xungChieu)})
                          </strong>
                        </div>
                        <div className="p-2.5 rounded-btn bg-surface border border-surface-border sm:col-span-2 shadow-subtle">
                          <span className="text-text-secondary text-[11px] block">Tam Hợp Chiếu:</span>
                          <strong className="text-accent font-heading font-bold text-sm">
                            {relatedPalaces.tamHop[0]?.ten_cung_chuc_nang} ({getCanChiCung(relatedPalaces.tamHop[0])})
                            {' — '}
                            {relatedPalaces.tamHop[1]?.ten_cung_chuc_nang} ({getCanChiCung(relatedPalaces.tamHop[1])})
                          </strong>
                        </div>
                      </div>
                    )}

                    {/* Danh sách toàn bộ tinh tú trong cung phân loại cụ thể */}
                    <div className="space-y-3">
                      {/* Chính Tinh */}
                      {selChinhTinh.length > 0 && (
                        <div>
                          <h4 className="text-xs font-heading font-bold text-primary mb-1.5 uppercase tracking-wide">
                            Chính Tinh ({selChinhTinh.length})
                          </h4>
                          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                            {selChinhTinh.map((s, idx) => {
                              const style = getElementStyle(s.ngu_hanh);
                              return (
                                <div key={idx} className="p-2.5 rounded-btn bg-surface border border-surface-border space-y-1 shadow-subtle">
                                  <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-1">
                                      <strong className={`text-sm font-bold ${style.text}`}>{s.ten}</strong>
                                      {renderDacHam(s.dac_ham)}
                                      {renderHoaBadge(s.hoa)}
                                    </div>
                                    <span className={`text-[10px] px-1.5 py-0.2 rounded border ${style.badge}`}>
                                      Hành {s.ngu_hanh}
                                    </span>
                                  </div>
                                  <p className="text-[11px] text-text-secondary line-clamp-2">
                                    {s.chuc_nang}
                                  </p>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* Cát Tinh & Quý Tinh */}
                      {selCatTinh.length > 0 && (
                        <div>
                          <h4 className="text-xs font-heading font-bold text-emerald-800 mb-1.5 uppercase tracking-wide">
                            Cát Tinh & Văn Tinh, Quý Tinh ({selCatTinh.length})
                          </h4>
                          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1.5 text-xs">
                            {selCatTinh.map((s, idx) => {
                              const style = getElementStyle(s.ngu_hanh);
                              return (
                                <div key={idx} className="p-2 rounded-btn bg-surface border border-surface-border flex items-center justify-between shadow-subtle">
                                  <div className="truncate">
                                    <span className={`font-bold ${style.text}`}>{s.ten}</span>
                                    {renderHoaBadge(s.hoa)}
                                  </div>
                                  <span className="text-[10px] font-mono text-text-secondary ml-1">
                                    {s.ngu_hanh}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* Hung/Sát Tinh & Bại Tinh */}
                      {selSatTinh.length > 0 && (
                        <div>
                          <h4 className="text-xs font-heading font-bold text-rose-800 mb-1.5 uppercase tracking-wide">
                            Hung Sát Tinh & Bại Tinh ({selSatTinh.length})
                          </h4>
                          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1.5 text-xs">
                            {selSatTinh.map((s, idx) => (
                              <div key={idx} className="p-2 rounded-btn bg-surface border border-surface-border flex items-center justify-between shadow-subtle">
                                <div className="truncate">
                                  <span className="font-medium text-rose-800">{s.ten}</span>
                                  {renderDacHam(s.dac_ham)}
                                  {renderHoaBadge(s.hoa)}
                                </div>
                                <span className="text-[10px] font-mono text-text-secondary ml-1">
                                  {s.ngu_hanh}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })()}
            </div>

            {/* BẢN LUẬN GIẢI CHUYÊN SÂU TỪ ORCHESTRATOR */}
            <InterpretationTabs luanGiai={luanGiaiData} systemName="Tử Vi Đẩu Số" />
          </>
        ) : null}
      </main>
    </div>
  );
}
