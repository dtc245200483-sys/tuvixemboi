import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import {
  IconCompass,
  IconArrowLeft,
  IconRefresh,
  IconSparkles,
  IconUser,
  IconStar,
  IconInfoCircle,
  IconUsers,
  IconPlus
} from '@tabler/icons-react';
import { tuViService, birthProfileService } from '../../services/api';
import InterpretationTabs from '../../components/InterpretationTabs';
import QuotaBadge from '../../components/QuotaBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';
import TuViQuickInputBar from '../../components/TuViQuickInputBar';
import TuViCustomizerSidebar from '../../components/TuViCustomizerSidebar';
import { getLunarInfoForSolarMonth } from '../../utils/lunarConverter';
import '../../styles/tuvi_vn.css';

/**
 * BẢNG THÔNG TIN 12 ĐỊA CHI (VỊ TRÍ GRID 4x4, NGŨ HÀNH, VIẾT TẮT CAN CHI CHUẨN TUVI.VN)
 */
const BRANCH_CONFIG = {
  'Tỵ':  { gridRow: 1, gridCol: 1, elementText: '-Hoả',  elementClass: 'element-hoa',  defaultStem: 'Q' },
  'Ngọ': { gridRow: 1, gridCol: 2, elementText: '+Hoả',  elementClass: 'element-hoa',  defaultStem: 'G' },
  'Mùi': { gridRow: 1, gridCol: 3, elementText: '-Thổ',  elementClass: 'element-tho',  defaultStem: 'Ấ' },
  'Thân':{ gridRow: 1, gridCol: 4, elementText: '+Kim',  elementClass: 'element-kim',  defaultStem: 'B' },
  'Dậu': { gridRow: 2, gridCol: 4, elementText: '-Kim',  elementClass: 'element-kim',  defaultStem: 'Đ' },
  'Tuất':{ gridRow: 3, gridCol: 4, elementText: '+Thổ',  elementClass: 'element-tho',  defaultStem: 'M' },
  'Hợi': { gridRow: 4, gridCol: 4, elementText: '-Thuỷ', elementClass: 'element-thuy', defaultStem: 'K' },
  'Tý':  { gridRow: 4, gridCol: 3, elementText: '+Thuỷ', elementClass: 'element-thuy', defaultStem: 'C' },
  'Sửu': { gridRow: 4, gridCol: 2, elementText: '-Thổ',  elementClass: 'element-tho',  defaultStem: 'T' },
  'Dần': { gridRow: 4, gridCol: 1, elementText: '+Mộc',  elementClass: 'element-moc',  defaultStem: 'C' },
  'Mão': { gridRow: 3, gridCol: 1, elementText: '-Mộc',  elementClass: 'element-moc',  defaultStem: 'T' },
  'Thìn':{ gridRow: 2, gridCol: 1, elementText: '+Thổ',  elementClass: 'element-tho',  defaultStem: 'N' }
};

const BRANCH_INDEX_MAP = {
  'Tý': 0, 'Sửu': 1, 'Dần': 2, 'Mão': 3,
  'Thìn': 4, 'Tỵ': 5, 'Ngọ': 6, 'Mùi': 7,
  'Thân': 8, 'Dậu': 9, 'Tuất': 10, 'Hợi': 11
};

const STEM_ABBR = {
  'Giáp': 'G', 'Ất': 'Ấ', 'Bính': 'B', 'Đinh': 'Đ', 'Mậu': 'M',
  'Kỷ': 'K', 'Canh': 'C', 'Tân': 'T', 'Nhâm': 'N', 'Quý': 'Q'
};

const MONTH_TRACKING = {
  'Sửu': 'Th.1', 'Dần': 'Th.2', 'Mão': 'Th.3', 'Thìn': 'Th.4',
  'Tỵ': 'Th.5',  'Ngọ': 'Th.6', 'Mùi': 'Th.7', 'Thân': 'Th.8',
  'Dậu': 'Th.9', 'Tuất': 'Th.10', 'Hợi': 'Th.11', 'Tý': 'Th.12'
};

const DV_TRACKING = {
  'Tỵ': 'ĐV.ĐIỀN', 'Ngọ': 'ĐV.QUAN', 'Mùi': 'ĐV.NÔ',   'Thân': 'ĐV.DI',
  'Dậu': 'ĐV.TẬT', 'Tuất': 'ĐV.TÀI',  'Hợi': 'ĐV.TỬ',   'Tý': 'ĐV.PHỐI',
  'Sửu': 'ĐV.HUYNH', 'Dần': 'ĐV.MỆNH', 'Mão': 'ĐV.PHỤ',  'Thìn': 'ĐV.PHÚC'
};

const LN_TRACKING = {
  'Tỵ': 'LN.DI',   'Ngọ': 'LN.TẬT',  'Mùi': 'LN.TÀI',  'Thân': 'LN.TỬ',
  'Dậu': 'LN.PHỐI', 'Tuất': 'LN.HUYNH', 'Hợi': 'LN.MỆNH', 'Tý': 'LN.PHỤ',
  'Sửu': 'LN.PHÚC', 'Dần': 'LN.ĐIỀN', 'Mão': 'LN.QUAN', 'Thìn': 'LN.NÔ'
};

const STAR_METADATA = {
  // 14 Chính Tinh
  'Tử Vi':      { element: 'tho',  isGood: true,  isMajor: true, polarity: '+' },
  'Thiên Cơ':   { element: 'moc',  isGood: true,  isMajor: true, polarity: '-' },
  'Thái Dương': { element: 'hoa',  isGood: true,  isMajor: true, polarity: '+' },
  'Vũ Khúc':    { element: 'kim',  isGood: true,  isMajor: true, polarity: '-' },
  'Thiên Đồng': { element: 'thuy', isGood: true,  isMajor: true, polarity: '+' },
  'Liêm Trinh': { element: 'hoa',  isGood: true,  isMajor: true, polarity: '-' },
  'Thiên Phủ':  { element: 'tho',  isGood: true,  isMajor: true, polarity: '+' },
  'Thái Âm':    { element: 'thuy', isGood: true,  isMajor: true, polarity: '-' },
  'Tham Lang':  { element: 'thuy', isGood: true,  isMajor: true, polarity: '+' },
  'Cự Môn':     { element: 'thuy', isGood: true,  isMajor: true, polarity: '-' },
  'Thiên Tướng':{ element: 'thuy', isGood: true,  isMajor: true, polarity: '+' },
  'Thiên Lương':{ element: 'moc',  isGood: true,  isMajor: true, polarity: '+' },
  'Thất Sát':   { element: 'kim',  isGood: true,  isMajor: true, polarity: '+' },
  'Phá Quân':   { element: 'thuy', isGood: true,  isMajor: true, polarity: '-' },

  // Cát Tinh
  'Văn Xương':  { element: 'kim',  isGood: true },
  'Văn Khúc':   { element: 'thuy', isGood: true },
  'Tả Phù':     { element: 'tho',  isGood: true },
  'Hữu Bật':    { element: 'thuy', isGood: true },
  'Thiên Khôi': { element: 'hoa',  isGood: true },
  'Thiên Việt': { element: 'hoa',  isGood: true },
  'Lộc Tồn':    { element: 'tho',  isGood: true },
  'Hóa Lộc':    { element: 'moc',  isGood: true },
  'Hóa Quyền':  { element: 'thuy', isGood: true },
  'Hóa Khoa':   { element: 'thuy', isGood: true },
  'Thiên Mã':   { element: 'hoa',  isGood: true },
  'Đào Hoa':    { element: 'moc',  isGood: true },
  'Hồng Loan':  { element: 'thuy', isGood: true },
  'Thiên Hỷ':   { element: 'thuy', isGood: true },
  'Thiên Quan': { element: 'hoa',  isGood: true },
  'Thiên Phúc': { element: 'tho',  isGood: true },
  'Ân Quang':   { element: 'moc',  isGood: true },
  'Thiên Quý':  { element: 'tho',  isGood: true },
  'Tam Thai':   { element: 'thuy', isGood: true },
  'Bát Tọa':    { element: 'thuy', isGood: true },
  'Long Trì':   { element: 'thuy', isGood: true },
  'Phượng Các': { element: 'tho',  isGood: true },
  'Giải Thần':  { element: 'moc',  isGood: true },
  'Bác Sỹ':     { element: 'thuy', isGood: true },
  'Lực Sỹ':     { element: 'hoa',  isGood: true },
  'Thanh Long': { element: 'thuy', isGood: true },
  'Tướng Quân': { element: 'moc',  isGood: true },
  'Tấu Thư':    { element: 'kim',  isGood: true },
  'Hỷ Thần':    { element: 'hoa',  isGood: true },
  'Hoa Cái':    { element: 'kim',  isGood: true },
  'Thiếu Dương':{ element: 'hoa',  isGood: true },
  'Thiếu Âm':   { element: 'thuy', isGood: true },
  'Long Đức':   { element: 'thuy', isGood: true },
  'Phúc Đức':   { element: 'tho',  isGood: true },
  'Thiên Thọ':  { element: 'tho',  isGood: true },
  'Thiên Tài':  { element: 'tho',  isGood: true },
  'Thiên Trù':  { element: 'tho',  isGood: true },
  'Phong Cáo':  { element: 'tho',  isGood: true },

  // Hung Tinh / Sát Tinh
  'Kình Dương': { element: 'kim',  isGood: false },
  'Đà La':      { element: 'kim',  isGood: false },
  'Hỏa Tinh':   { element: 'hoa',  isGood: false },
  'Linh Tinh':  { element: 'hoa',  isGood: false },
  'Địa Không':  { element: 'hoa',  isGood: false },
  'Địa Kiếp':   { element: 'hoa',  isGood: false },
  'Thiên Hình': { element: 'hoa',  isGood: false },
  'Thiên Riêu': { element: 'thuy', isGood: false },
  'Thiên Khốc': { element: 'kim',  isGood: false },
  'Thiên Hư':   { element: 'thuy', isGood: false },
  'Tang Môn':   { element: 'moc',  isGood: false },
  'Bạch Hổ':    { element: 'kim',  isGood: false },
  'Đại Hao':    { element: 'hoa',  isGood: false },
  'Tiểu Hao':   { element: 'hoa',  isGood: false },
  'Kiếp Sát':   { element: 'hoa',  isGood: false },
  'Cô Thần':    { element: 'tho',  isGood: false },
  'Quả Tú':     { element: 'tho',  isGood: false },
  'Thiên Không':{ element: 'hoa',  isGood: false },
  'Phi Liêm':   { element: 'hoa',  isGood: false },
  'Phục Binh':  { element: 'hoa',  isGood: false },
  'Quan Phù':   { element: 'hoa',  isGood: false },
  'Quan Phủ':   { element: 'hoa',  isGood: false },
  'Tuế Phá':    { element: 'hoa',  isGood: false },
  'Thái Tuế':   { element: 'hoa',  isGood: false },
  'Điếu Khách': { element: 'hoa',  isGood: false },
  'Trực Phù':   { element: 'hoa',  isGood: false },
  'Tử Phù':     { element: 'kim',  isGood: false },
  'Bệnh Phù':   { element: 'tho',  isGood: false },
  'Hóa Kỵ':     { element: 'thuy', isGood: false },
  'Thiên Sứ':   { element: 'thuy', isGood: false },
  'Thiên Thương':{ element: 'tho', isGood: false }
};

function formatBrightness(b) {
  if (!b) return '';
  const upper = b.toString().toUpperCase().trim();
  if (upper.startsWith('M') || upper.includes('MIẾU')) return '(M)';
  if (upper.startsWith('V') || upper.includes('VƯỢNG')) return '(V)';
  if (upper.startsWith('Đ') || upper.startsWith('D') || upper.includes('ĐẮC')) return '(Đ)';
  if (upper.startsWith('B') || upper.includes('BÌNH')) return '(B)';
  if (upper.startsWith('H') || upper.includes('HÃM')) return '(H)';
  return `(${upper.charAt(0)})`;
}

function getStarInfo(starName) {
  let cleanName = starName.replace(/^Lưu\s+|^L\./, '').trim();
  const isLuu = starName.startsWith('Lưu ') || starName.startsWith('L.');

  if (cleanName === 'Lộc') cleanName = 'Lộc Tồn';
  if (cleanName === 'Dương') cleanName = 'Kình Dương';
  if (cleanName === 'Đà') cleanName = 'Đà La';
  if (cleanName === 'Mã') cleanName = 'Thiên Mã';
  if (cleanName === 'Hổ') cleanName = 'Bạch Hổ';
  if (cleanName === 'Khốc') cleanName = 'Thiên Khốc';
  if (cleanName === 'Hư') cleanName = 'Thiên Hư';
  if (cleanName === 'Tang') cleanName = 'Tang Môn';
  if (cleanName === 'Xương') cleanName = 'Văn Xương';
  if (cleanName === 'Khúc') cleanName = 'Văn Khúc';

  const meta = STAR_METADATA[cleanName] || {
    element: 'thuy',
    isGood: !['Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp', 'Kình Dương', 'Đà La', 'Tang Môn', 'Bạch Hổ'].includes(cleanName),
    polarity: ''
  };

  return {
    cleanName,
    isLuu,
    displayName: isLuu ? `L.${cleanName}` : cleanName,
    elementClass: `element-${meta.element}`,
    isGood: meta.isGood,
    polarity: meta.polarity || '',
    isMajor: !!meta.isMajor
  };
}

export default function TuViPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [laSoData, setLaSoData] = useState(null);
  const [luanGiaiData, setLuanGiaiData] = useState(null);
  const [profiles, setProfiles] = useState([]);
  const [currentProfileId, setCurrentProfileId] = useState(null);
  const [selectedPalace, setSelectedPalace] = useState(null);
  const [hoveredBranchId, setHoveredBranchId] = useState(null);
  const [quotaTrigger, setQuotaTrigger] = useState(0);

  // Trạng thái Tùy chỉnh lá số (chuẩn tuvi.vn)
  const [isGrayscale, setIsGrayscale] = useState(false);
  const [showChieuLine, setShowChieuLine] = useState(true);
  const [showPalaceDetail, setShowPalaceDetail] = useState(true);
  const [xemNam, setXemNam] = useState(2026);
  const [xemThang, setXemThang] = useState(7);
  const [mobileViewMode, setMobileViewMode] = useState('grid'); // 'grid' | 'cards'

  // 1. Tải danh sách hồ sơ sinh
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
          const found = list.find(p => String(p.id) === String(qId));
          if (found) {
            setCurrentProfileId(found.id);
          } else if (list.length > 0) {
            const pref = getPreferredProfile(list);
            console.warn(`Hồ sơ ${qId} không tồn tại trong danh sách, tự động chọn hồ sơ ưu tiên: ${pref?.id}`);
            setCurrentProfileId(pref.id);
            navigate(`/tu-vi?profile_id=${pref.id}`, { replace: true });
          } else {
            navigate('/birth-profile');
          }
        } else if (list.length > 0) {
          const pref = getPreferredProfile(list);
          setCurrentProfileId(pref.id);
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
    return () => { isMounted = false; };
  }, [searchParams, navigate]);

  const [aiLoading, setAiLoading] = useState(false);

  // 2. Tải lá số theo currentProfileId (Tải nhanh tức thì < 200ms, không đợi AI)
  useEffect(() => {
    if (!currentProfileId) return;

    let isMounted = true;
    const fetchLaSo = async () => {
      setLoading(true);
      setError(null);
      setLuanGiaiData(null);

      // BƯỚC 1: LẤY DỮ LIỆU LÁ SỐ CỰC NHANH (< 200ms)
      let laSo = null;
      let chartError = null;
      try {
        const res = await tuViService.getChartOnly(currentProfileId);
        const data = res.data?.du_lieu || res.data;
        laSo = data.la_so || data;
      } catch (err1) {
        try {
          const res = await tuViService.getLaSo(currentProfileId, true);
          const data = res.data?.du_lieu || res.data;
          laSo = data.la_so || data;
        } catch (err2) {
          console.error("Lỗi tải lá số:", err2);
          chartError = err2;
        }
      }

      if (!isMounted) return;

      if (laSo && (laSo.palaces || laSo.data?.palaces)) {
        setLaSoData(laSo);
        const pList = laSo.palaces || laSo.data?.palaces || [];
        const menh = pList.find(p => p.name && (p.name.includes('Mệnh') || p.name.includes('命'))) || pList[0];
        setSelectedPalace(menh);
        setLoading(false); // HIỂN THỊ BẢNG LÁ SỐ NGAY LẬP TỨC!
      } else {
        const is404 = chartError?.response?.status === 404;
        const msg = is404
          ? 'Không tìm thấy thông tin lá số cho hồ sơ này (có thể đã bị xoá). Quý bạn vui lòng chọn hồ sơ khác từ danh sách.'
          : 'Hệ thống đang bận tải dữ liệu lá số. Quý bạn vui lòng nhấn "Thử lại" bên dưới.';
        setError(msg);
        setLoading(false);
      }

      // BƯỚC 2: TẢI LUẬN GIẢI AI CHẠY NGẦM (KHÔNG LÀM TREO GIAO DIỆN)
      setAiLoading(true);
      tuViService.getLaSo(currentProfileId, false)
        .then((fullRes) => {
          if (!isMounted) return;
          const fullData = fullRes.data?.du_lieu || fullRes.data;
          if (fullData.luan_giai) {
            setLuanGiaiData(fullData.luan_giai);
            setQuotaTrigger((prev) => prev + 1);
          }
          if (!laSo && fullData.la_so) {
            setLaSoData(fullData.la_so);
            const pList = fullData.la_so.palaces || fullData.la_so.data?.palaces || [];
            const menh = pList.find(p => p.name && (p.name.includes('Mệnh') || p.name.includes('命'))) || pList[0];
            setSelectedPalace(menh);
            setError(null);
          }
        })
        .catch((aiErr) => {
          if (!isMounted) return;
          console.warn("Luận giải AI chưa sẵn sàng:", aiErr);
          setLuanGiaiData({
            thanh_cong: false,
            thong_bao: 'Hệ thống AI đang bận kết nối. Quý bạn chỉ cần nhấn lại là được.',
            cau_tra_loi: null
          });
        })
        .finally(() => {
          if (isMounted) {
            setAiLoading(false);
            setLoading(false);
          }
        });
    };

    fetchLaSo();
    return () => { isMounted = false; };
  }, [currentProfileId]);

  const handleRetryGeneral = useCallback(() => {
    if (!currentProfileId) return;
    setAiLoading(true);
    tuViService.getLaSo(currentProfileId, false)
      .then((fullRes) => {
        const fullData = fullRes.data?.du_lieu || fullRes.data;
        if (fullData.luan_giai) {
          setLuanGiaiData(fullData.luan_giai);
          setQuotaTrigger((prev) => prev + 1);
        }
      })
      .catch((aiErr) => {
        console.warn("Lỗi khi thử lại luận giải:", aiErr);
        setLuanGiaiData({
          thanh_cong: false,
          thong_bao: 'Hệ thống AI đang bận kết nối. Quý bạn chỉ cần nhấn lại là được.',
          cau_tra_loi: null
        });
      })
      .finally(() => {
        setAiLoading(false);
      });
  }, [currentProfileId]);


  // 3. Trích xuất dữ liệu tổng thể lá số
  const chartData = useMemo(() => {
    if (!laSoData) return null;
    const d = laSoData.data || laSoData;
    const palaces = laSoData.palaces || d.palaces || [];

    const userName = d.name || laSoData.thong_tin_co_ban?.ho_ten || 'Mệnh Chủ';
    const solarDate = laSoData.solarDate || d.solarDate || '1990-01-01';
    const solarParts = solarDate.split('-');
    const solarYear = solarParts[0] || '1990';
    const solarMonth = parseInt(solarParts[1] || '1', 10);
    const solarDay = parseInt(solarParts[2] || '1', 10);

    const baziParts = (laSoData.chineseDate || d.chineseDate || '').split(' - ');
    const yearCanChi = baziParts[0] || d.can_chi_tuoi || '';
    const monthCanChi = baziParts[1] || '';
    const dayCanChi = baziParts[2] || '';
    const hourCanChi = baziParts[3] || '';

    const amDuong = d.am_duong_ban_menh || laSoData.thong_tin_co_ban?.am_duong_nam_nu || '';
    const napAmVal = d.loai_hanh_cua_ban_menh || laSoData.ngu_hanh_nap_am || '';
    const cucVal = d.cuc_cua_tuoi || laSoData.cuc?.ten || '';
    const canLuongVal = d.can_luong || laSoData.can_luong || '';
    const menhChuVal = d.menh_chu || laSoData.menh_chu || '';
    const thanChuVal = d.than_chu || laSoData.than_chu || '';
    const viewYearStr = d.view_year || '';
    const hourDisplay = d.hour || laSoData.thong_tin_co_ban?.gio_sinh || '';

    const menhPalace = palaces.find(p => p.name && (p.name.includes('Mệnh') || p.name.includes('命'))) || palaces[0];
    const menhBranch = menhPalace ? menhPalace.earthlyBranch : 'Dần';
    const defaultMenhIndex = BRANCH_INDEX_MAP[menhBranch] ?? 2;

    return {
      d,
      palaces,
      userName,
      solarYear,
      solarMonth,
      solarDay,
      yearCanChi,
      monthCanChi,
      dayCanChi,
      hourCanChi,
      amDuong,
      napAmVal,
      cucVal,
      canLuongVal,
      menhChuVal,
      thanChuVal,
      viewYearStr,
      hourDisplay,
      defaultMenhIndex
    };
  }, [laSoData]);

  // Highlight Tam Hợp & Xung Chiếu
  const relatedBranchIds = useMemo(() => {
    if (hoveredBranchId === null) return null;
    const bIdx = hoveredBranchId;
    const tamHop1 = (bIdx + 4) % 12;
    const tamHop2 = (bIdx + 8) % 12;
    const xungChieu = (bIdx + 6) % 12;
    return [bIdx, tamHop1, tamHop2, xungChieu];
  }, [hoveredBranchId]);

  // Chuyển đổi hồ sơ
  const handleProfileChange = (e) => {
    const newId = e.target.value;
    setCurrentProfileId(newId);
    navigate(`/tu-vi?profile_id=${newId}`);
  };

  // Safe list of profiles
  const safeProfiles = useMemo(() => (Array.isArray(profiles) ? profiles.filter((p) => p && p.id) : []), [profiles]);

  // Thông tin tính toán Năm xem & Tháng xem (tính theo Dương lịch quy đổi Âm lịch)
  const viewingLunar = useMemo(() => {
    return getLunarInfoForSolarMonth(xemThang, xemNam);
  }, [xemThang, xemNam]);

  const ageAtViewYear = useMemo(() => {
    const birthY = chartData?.solarYear || (chartData?.d?.year ? parseInt(chartData.d.year, 10) : 1995);
    return Math.max(1, xemNam - birthY + 1);
  }, [xemNam, chartData]);

  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* HEADER TOP NAVBAR */}
      <header className="bg-primary text-text-on-primary border-b border-[#552218] px-4 sm:px-8 py-3.5 shadow-subtle sticky top-0 z-20">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              className="p-1.5 rounded-btn bg-[#552218] text-text-on-primary hover:bg-[#431A12] transition-colors"
              title="Quay lại Tổng quan"
            >
              <IconArrowLeft size={18} />
            </Link>
            <div>
              <h1 className="font-heading text-lg sm:text-xl font-bold tracking-wide text-text-on-primary flex items-center gap-2">
                <span>Tử Vi Đẩu Số Toàn Thư</span>
              </h1>
              <p className="text-xs text-text-on-primary/80 font-body hidden md:block">
                Thiên Bàn 12 Cung Chuẩn Cổ Học — Phân Cột Cát Hung & Đồ Họa Chiếu Sao Xuyên Tâm
              </p>
            </div>
          </div>

          {/* QUICK PROFILE SWITCHER DROPDOWN */}
          <div className="flex items-center gap-3">
            {safeProfiles.length > 0 && (
              <div className="flex items-center gap-2 bg-[#552218] px-2.5 py-1.5 rounded-btn border border-accent/30 text-xs font-body">
                <IconUser size={15} className="text-accent flex-shrink-0" />
                <select
                  value={currentProfileId || ''}
                  onChange={handleProfileChange}
                  className="bg-transparent text-text-on-primary font-bold outline-none cursor-pointer text-xs max-w-[110px] sm:max-w-xs truncate"
                >
                  {safeProfiles.map((prof) => (
                    <option key={prof.id} value={prof.id} className="bg-[#431A12] text-text-on-primary">
                      {prof.ho_ten || 'Hồ sơ chưa đặt tên'} ({prof.gioi_tinh === 'nam' ? 'Nam' : 'Nữ'})
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
            <QuotaBadge refreshTrigger={quotaTrigger} />
          </div>
        </div>
      </header>

      {/* MAIN CONTAINER */}
      <main className="max-w-7xl mx-auto px-2 sm:px-6 py-6 space-y-6">
        {/* THANH NHẬP THÔNG TIN AN SAO LẬP LÁ SỐ NHANH TRÊN ĐẦU LÁ SỐ */}
        <TuViQuickInputBar
          currentProfile={safeProfiles.find((p) => String(p.id) === String(currentProfileId))}
          onProfileCreated={(newId) => {
            birthProfileService.getAll().then((res) => {
              const list = res.data?.du_lieu || res.data || [];
              setProfiles(list);
              setCurrentProfileId(newId);
              navigate(`/tu-vi?profile_id=${newId}`);
            });
          }}
        />

        {error && (
          <ErrorMessage
            message={error}
            onClose={() => setError(null)}
            className="mb-4"
          />
        )}

        {loading ? (
          <div className="card-base p-12 text-center space-y-4 shadow-card">
            <LoadingSpinner size="lg" text="Đang khởi tạo Thiên Bàn Tử Vi chuẩn giao diện tuvi.vn..." />
            <p className="font-body text-xs text-text-secondary max-w-sm mx-auto">
              Hệ thống đang an sao 12 cung, 14 chính tinh đắc hãm, tuần triệt, tứ hóa và chuẩn bị đồ họa chiếu sao Tam Hợp.
            </p>
          </div>
        ) : chartData ? (
          <>
            {/* BỐ CỤC 2 CỘT: CỘT TRÁI (LÁ SỐ TỬ VI) & CỘT PHẢI (SIDEBAR TÙY CHỈNH & LÁ SỐ ĐÃ TẠO) */}
            <div className="flex flex-col lg:flex-row items-start gap-6">
              {/* CỘT TRÁI: LÁ SỐ 12 CUNG + CHI TIẾT CUNG CHỌN */}
              <div className="flex-1 min-w-0 w-full space-y-6">
                {/* BỘ CHUYỂN ĐỔI CHẾ ĐỘ XEM TRÊN ĐIỆN THOẠI */}
                <div className="lg:hidden flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-2.5 rounded-xl bg-[#FAF5EE] border border-accent/40 shadow-2xs">
                  <div className="flex items-center gap-1.5 w-full sm:w-auto">
                    <button
                      type="button"
                      onClick={() => setMobileViewMode('grid')}
                      className={`flex-1 sm:flex-initial px-3 py-1.5 rounded-lg text-xs font-body font-semibold transition-all ${
                        mobileViewMode === 'grid'
                          ? 'bg-[#8B1C13] text-white shadow-xs'
                          : 'text-[#6B5A4D] hover:text-[#2C2420]'
                      }`}
                    >
                      Bàn Đồ 4x4 (↔ Vuốt ngang)
                    </button>
                    <button
                      type="button"
                      onClick={() => setMobileViewMode('cards')}
                      className={`flex-1 sm:flex-initial px-3 py-1.5 rounded-lg text-xs font-body font-semibold transition-all ${
                        mobileViewMode === 'cards'
                          ? 'bg-[#8B1C13] text-white shadow-xs'
                          : 'text-[#6B5A4D] hover:text-[#2C2420]'
                      }`}
                    >
                      Danh Sách Thẻ (Dễ Đọc)
                    </button>
                  </div>
                  {mobileViewMode === 'grid' && (
                    <span className="text-[11px] font-body text-text-secondary flex items-center gap-1">
                      <span>💡 Vuốt sang ngang ↔ để xem toàn cảnh 12 cung</span>
                    </span>
                  )}
                </div>

                {/* CHẾ ĐỘ 1: BÀN ĐỒ LƯỚI TRUYỀN THỐNG 4X4 (Có cuộn ngang mượt trên mobile) */}
                <div className={mobileViewMode === 'cards' ? 'hidden lg:block' : 'block'}>
                  <div className="tuvi-scroll-wrapper">
                    <div className={`tuvi-container ${isGrayscale ? 'grayscale' : ''}`}>
                      <div className="tuvi-grid-wrapper">
                    {/* HUY HIỆU TUẦN / TRIỆT TẠI BIÊN GIỚI CUNG */}
                    <div className="badge-tuan-triet badge-triet-default">TRIỆT</div>
                    <div className="badge-tuan-triet badge-tuan-default">TUẦN</div>

                    {/* BẢNG GRID 4X4 */}
                    <div className="tuvi-chart-grid" id="tuviGrid">
                      {/* Ô THIÊN BÀN TRUNG TÂM (2x2) */}
                      <div className="center-box">
                        {/* Đồ họa đường kẻ Tam Hợp & Xung Chiếu (ẩn nếu tắt xem cung chiếu) */}
                        {showChieuLine && (
                          <div
                            className={`view-con-giap-la-so list-line-${
                              hoveredBranchId !== null ? hoveredBranchId : chartData.defaultMenhIndex
                            }`}
                            id="list-line-la-so"
                            style={{ display: 'block' }}
                          />
                        )}

                    <div className="center-content">
                      <div className="center-header-branding" style={{ marginBottom: '16px' }}>
                        <div className="brand-chart-title" style={{ fontSize: '20px', letterSpacing: '2px', fontWeight: 800 }}>LÁ SỐ TỬ VI</div>
                      </div>

                      {/* Bảng thông tin cá nhân 2 cột */}
                      <div className="center-info-grid">
                        <div className="info-row">
                          <span className="info-label">Họ tên:</span>
                          <span className="info-val">{chartData.userName}</span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Năm:</span>
                          <span className="info-val">
                            {chartData.solarYear}
                            <span className="info-val-sub">{chartData.yearCanChi}</span>
                          </span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Tháng:</span>
                          <span className="info-val">
                            {chartData.solarMonth} (3)
                            <span className="info-val-sub">{chartData.monthCanChi}</span>
                          </span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Ngày:</span>
                          <span className="info-val">
                            {chartData.solarDay} (3)
                            <span className="info-val-sub">{chartData.dayCanChi}</span>
                          </span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Giờ:</span>
                          <span className="info-val">
                            {chartData.hourDisplay}
                            <span className="info-val-sub">{chartData.hourCanChi}</span>
                          </span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Năm xem:</span>
                          <span className="info-val">
                            {xemNam}
                            <span className="info-val-sub">{viewingLunar.yearCanChi} ({ageAtViewYear}t)</span>
                          </span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Tháng xem:</span>
                          <span className="info-val">
                            Tháng {xemThang} (DL)
                            <span className="info-val-sub">Th.{viewingLunar.lunarMonth} ÂL ({viewingLunar.monthCanChi})</span>
                          </span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Âm dương:</span>
                          <span className="info-val">{chartData.amDuong}</span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Bản mệnh:</span>
                          <span className="info-val">
                            {chartData.napAmVal} - {chartData.cucVal}
                          </span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Cân lượng:</span>
                          <span className="info-val">{chartData.canLuongVal}</span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Chủ mệnh:</span>
                          <span className="info-val">{chartData.menhChuVal}</span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Chủ thân:</span>
                          <span className="info-val">{chartData.thanChuVal}</span>
                        </div>
                        <div className="info-row">
                          <span className="info-label">Lai nhân cung:</span>
                          <span className="info-val">Mệnh</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* 12 CUNG ĐỊA CHI */}
                  {chartData.palaces.map((palace, idx) => {
                    const branch = palace.earthlyBranch;
                    const config = BRANCH_CONFIG[branch] || { gridRow: 1, gridCol: 1, elementText: '', elementClass: '', defaultStem: '' };
                    const bIdx = BRANCH_INDEX_MAP[branch] ?? 0;

                    // Hover state
                    let hoverClass = '';
                    if (relatedBranchIds !== null) {
                      if (relatedBranchIds.includes(bIdx)) {
                        hoverClass = 'cung-view-hover';
                      } else {
                        hoverClass = 'none-cung-view-hover';
                      }
                    }

                    const isSelected = selectedPalace?.earthlyBranch === branch;
                    const stemLetter = STEM_ABBR[palace.heavenlyStem] || config.defaultStem || palace.heavenlyStem?.charAt(0) || '';
                    const canChiAbbr = `${stemLetter}.${branch}`;
                    const daivanAge = (palace.decadal && Array.isArray(palace.decadal.range)) ? palace.decadal.range[0] : (idx * 10 + 5);

                    // Phân loại sao Cát / Hung
                    const leftStars = [];
                    const rightStars = [];

                    // 14 Chính Tinh
                    if (palace.majorStars) {
                      palace.majorStars.forEach(s => {
                        const info = getStarInfo(s.name);
                        const bTag = formatBrightness(s.brightness);
                        const sign = info.polarity ? info.polarity : '';
                        leftStars.push({
                          text: `${sign}${s.name.toUpperCase()} ${bTag}`.trim(),
                          cssClass: `star-line star-major ${info.elementClass}`,
                          key: `major-${s.name}`
                        });
                      });
                    }

                    // Phụ tinh
                    const minorList = (palace.minorStars || []).concat(palace.adjectiveStars || []);
                    minorList.forEach(s => {
                      const info = getStarInfo(s.name);
                      const bTag = formatBrightness(s.brightness);
                      const displayText = bTag ? `${s.name} ${bTag}` : s.name;
                      const starObj = {
                        text: displayText,
                        cssClass: `star-line ${info.elementClass}`,
                        key: `minor-${s.name}`
                      };
                      if (info.isGood) leftStars.push(starObj);
                      else rightStars.push(starObj);
                    });

                    // Vòng Bác Sĩ & Vòng Thái Tuế
                    const addedNames = new Set(leftStars.map(s => s.text).concat(rightStars.map(s => s.text)));
                    if (palace.boshi12 && !addedNames.has(palace.boshi12)) {
                      const info = getStarInfo(palace.boshi12);
                      const sObj = { text: palace.boshi12, cssClass: `star-line ${info.elementClass}`, key: `boshi-${palace.boshi12}` };
                      if (info.isGood) leftStars.push(sObj); else rightStars.push(sObj);
                      addedNames.add(palace.boshi12);
                    }
                    if (palace.suiqian12 && !addedNames.has(palace.suiqian12)) {
                      const info = getStarInfo(palace.suiqian12);
                      const sObj = { text: palace.suiqian12, cssClass: `star-line ${info.elementClass}`, key: `sui-${palace.suiqian12}` };
                      if (info.isGood) leftStars.push(sObj); else rightStars.push(sObj);
                      addedNames.add(palace.suiqian12);
                    }
                    if (palace.jiangqian12) {
                      const jName = palace.jiangqian12 === 'Hàm Trì' ? 'Đào Hoa' : palace.jiangqian12;
                      if (!addedNames.has(jName)) {
                        const info = getStarInfo(jName);
                        const sObj = { text: jName, cssClass: `star-line ${info.elementClass}`, key: `jiang-${jName}` };
                        if (info.isGood) leftStars.push(sObj); else rightStars.push(sObj);
                        addedNames.add(jName);
                      }
                    }

                    // Tứ hóa
                    if (palace.majorStars) {
                      palace.majorStars.forEach(s => {
                        if (s.mutagen) {
                          const mutText = s.mutagen.startsWith('Hóa ') ? s.mutagen : `Hóa ${s.mutagen}`;
                          const info = getStarInfo(mutText);
                          const sObj = { text: mutText, cssClass: `star-line ${info.elementClass}`, key: `mut-${s.name}` };
                          if (info.isGood) leftStars.push(sObj); else rightStars.push(sObj);
                        }
                      });
                    }

                    return (
                      <div
                        key={branch}
                        style={{
                          gridRow: config.gridRow,
                          gridColumn: config.gridCol
                        }}
                        className={`palace-cell cell-${config.elementClass} ${hoverClass} ${
                          isSelected ? 'ring-2 ring-accent' : ''
                        }`}
                        data-branch={branch}
                        data-branch-id={bIdx}
                        onClick={() => setSelectedPalace(palace)}
                        onMouseEnter={() => setHoveredBranchId(bIdx)}
                        onMouseLeave={() => setHoveredBranchId(null)}
                      >
                        {/* HEADER CUNG */}
                        <div className="palace-header">
                          <div className="header-left">
                            <span className="canchi-abbr">{canChiAbbr}</span>
                            <span className="cung-element">{config.elementText}</span>
                          </div>
                          <div className="header-center">
                            <span className={`palace-name ${config.elementClass}`}>
                              {(palace.name || '').toUpperCase()}
                              {palace.isBodyPalace && <span className="badge-than-tag ml-1">&lt;THÂN&gt;</span>}
                            </span>
                          </div>
                          <div className="header-right">
                            <span className="daivan-age">{daivanAge}</span>
                            <span
                              className={`thang-luu ${
                                MONTH_TRACKING[branch] === `Th.${viewingLunar.lunarMonth}`
                                  ? 'font-bold text-[#8B1C13] bg-[#8B1C13]/15 px-1 py-0.5 rounded ring-1 ring-[#8B1C13]/40'
                                  : ''
                              }`}
                              title={
                                MONTH_TRACKING[branch] === `Th.${viewingLunar.lunarMonth}`
                                  ? `Tháng xem hiện tại: Tháng ${xemThang} Dương lịch (~ Th.${viewingLunar.lunarMonth} ÂL)`
                                  : `Lưu Nguyệt: ${MONTH_TRACKING[branch] || ''}`
                              }
                            >
                              {MONTH_TRACKING[branch] || ''}
                            </span>
                          </div>
                        </div>

                        {/* BODY CUNG (2 CỘT) */}
                        <div className="palace-body">
                          <div className="col-cat">
                            {leftStars.map(st => (
                              <div key={st.key} className={st.cssClass}>
                                {st.text}
                              </div>
                            ))}
                          </div>
                          <div className="col-hung">
                            {rightStars.map(st => (
                              <div key={st.key} className={st.cssClass}>
                                {st.text}
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* FOOTER CUNG */}
                        <div className="palace-footer">
                          <span className="footer-left">{DV_TRACKING[branch] || ''}</span>
                          <span className="footer-center">{palace.changsheng12 || ''}</span>
                          <span className="footer-right">{LN_TRACKING[branch] || ''}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

                {/* FOOTER LEGEND */}
                <div className="tuvi-footer-legend">
                  <div className="legend-brightness">
                    <span className="legend-b-item"><span className="legend-b-code">M</span>: Miếu địa</span>
                    <span className="legend-b-item"><span className="legend-b-code">V</span>: Vượng địa</span>
                    <span className="legend-b-item"><span className="legend-b-code">Đ</span>: Đắc địa</span>
                    <span className="legend-b-item"><span className="legend-b-code">B</span>: Bình hòa</span>
                    <span className="legend-b-item"><span className="legend-b-code">H</span>: Hãm địa</span>
                  </div>
                  <div className="legend-elements">
                    <span className="legend-el-item"><span className="color-block bg-kim"></span> Kim</span>
                    <span className="legend-el-item"><span className="color-block bg-moc"></span> Mộc</span>
                    <span className="legend-el-item"><span className="color-block bg-thuy"></span> Thủy</span>
                    <span className="legend-el-item"><span className="color-block bg-hoa"></span> Hỏa</span>
                    <span className="legend-el-item"><span className="color-block bg-tho"></span> Thổ</span>
                  </div>
                  <div className="legend-chart-id">
                    ID: #{chartData.d?.id || currentProfileId || 'tuvi-vn'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* CHẾ ĐỘ 2: DANH SÁCH 12 CUNG DẠNG THẺ (Dành riêng cho màn hình điện thoại) */}
          {mobileViewMode === 'cards' && (
            <div className="lg:hidden space-y-4">
              {/* Ô Thông Tin Bản Mệnh Trung Tâm */}
              <div className="p-4 rounded-xl bg-[#FAF5EE] border border-[#D5C9B8] space-y-2 text-xs font-body shadow-xs">
                <div className="flex items-center justify-between border-b border-[#E2D9C8] pb-2">
                  <span className="font-heading font-bold text-sm text-[#8B1C13]">THÔNG TIN MỆNH CHỦ</span>
                  <span className="font-mono text-[11px] text-accent font-bold">{chartData.cucVal}</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div>Họ tên: <strong className="text-primary">{chartData.hoTenVal}</strong></div>
                  <div>Giới tính: <strong>{chartData.gioiTinhVal}</strong></div>
                  <div>Dương lịch: <strong>{chartData.ngayDuongVal}</strong></div>
                  <div>Âm lịch: <strong>{chartData.ngayAmVal}</strong></div>
                  <div>Bản mệnh: <strong className="text-accent">{chartData.napAmVal}</strong></div>
                  <div>Cân lượng: <strong>{chartData.canLuongVal}</strong></div>
                  <div>Chủ mệnh: <strong>{chartData.menhChuVal}</strong></div>
                  <div>Chủ thân: <strong>{chartData.thanChuVal}</strong></div>
                </div>
              </div>

              {/* Danh sách 12 Cung dạng thẻ */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {chartData.palaces.map((palace, idx) => {
                  const branch = palace.earthlyBranch;
                  const isSelected = selectedPalace?.earthlyBranch === branch;
                  const canChiText = `${palace.heavenlyStem || ''} ${branch}`;
                  const daivanAge = (palace.decadal && Array.isArray(palace.decadal.range)) ? `${palace.decadal.range[0]} - ${palace.decadal.range[1]}` : `${idx * 10 + 5}`;
                  const majorStars = palace.majorStars || [];
                  const minorList = (palace.minorStars || []).concat(palace.adjectiveStars || []);

                  return (
                    <div
                      key={branch}
                      onClick={() => {
                        setSelectedPalace(palace);
                        setShowPalaceDetail(true);
                      }}
                      className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-2.5 ${
                        isSelected
                          ? 'bg-white border-2 border-[#8B1C13] shadow-md ring-2 ring-[#8B1C13]/20'
                          : 'bg-white border-[#D5C9B8] hover:border-[#8B1C13]/60 shadow-xs'
                      }`}
                    >
                      <div className="flex items-center justify-between border-b border-[#E2D9C8] pb-2">
                        <div className="flex items-center gap-1.5">
                          <span className="font-heading font-bold text-sm text-[#8B1C13]">
                            Cung {palace.name}
                          </span>
                          <span className="text-[11px] font-mono text-text-secondary">
                            ({canChiText})
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          {palace.isBodyPalace && (
                            <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#8B1C13] text-white font-bold">
                              THÂN
                            </span>
                          )}
                          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#FAF5EE] text-[#855B14] font-semibold">
                            ĐV: {daivanAge}t
                          </span>
                        </div>
                      </div>

                      {/* Chính tinh */}
                      <div>
                        <span className="text-[10px] uppercase font-bold text-text-secondary block mb-1">Chính tinh:</span>
                        <div className="flex flex-wrap gap-1">
                          {majorStars.length > 0 ? (
                            majorStars.map((s) => {
                              const info = getStarInfo(s.name);
                              const bTag = formatBrightness(s.brightness);
                              return (
                                <span key={s.name} className={`px-2 py-0.5 rounded text-[11px] font-bold bg-[#FAF6EE] border border-surface-border/40 ${info.elementClass}`}>
                                  {s.name} {bTag}
                                </span>
                              );
                            })
                          ) : (
                            <span className="text-[11px] text-text-secondary italic">Vô chính diệu</span>
                          )}
                        </div>
                      </div>

                      {/* Phụ tinh tóm tắt */}
                      {minorList.length > 0 && (
                        <div>
                          <span className="text-[10px] uppercase font-bold text-text-secondary block mb-1">Phụ tinh nổi bật:</span>
                          <div className="flex flex-wrap gap-1">
                            {minorList.slice(0, 6).map((s) => {
                              const info = getStarInfo(s.name);
                              return (
                                <span key={s.name} className={`px-1.5 py-0.2 rounded text-[10px] bg-surface border border-surface-border/30 ${info.elementClass}`}>
                                  {s.name}
                                </span>
                              );
                            })}
                            {minorList.length > 6 && (
                              <span className="text-[10px] text-text-secondary font-mono self-center">
                                +{minorList.length - 6} sao
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      <div className="pt-1 flex items-center justify-between text-[11px] text-[#8B1C13] font-medium">
                        <span>{isSelected ? '✓ Đang xem chi tiết bên dưới' : 'Chạm để xem luận giải'}</span>
                        <span className="text-xs">→</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

              {/* BẢNG CHI TIẾT CUNG ĐANG CHỌN (CHỈ HIỂN THỊ NẾU showPalaceDetail === true) */}
              {showPalaceDetail && selectedPalace && (
                <div className="p-4 sm:p-5 rounded-card bg-[#FAF6EE] border border-[#E2D9C8] space-y-4 shadow-xs">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#E2D9C8] pb-3">
                    <div className="flex items-center gap-2.5">
                      <IconStar size={22} className="text-[#8B1C13]" />
                      <h3 className="font-heading text-lg sm:text-xl font-bold text-[#4A3B32]">
                        Chi Tiết Cung {selectedPalace.name || ''} — An Tại Cung {selectedPalace.earthlyBranch || ''}
                      </h3>
                      {selectedPalace.isBodyPalace && (
                        <span className="px-2 py-0.5 rounded-full bg-[#8B1C13] text-white font-bold text-xs shadow-xs">
                          CUNG AN THÂN
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-text-secondary font-body">
                      <span>Đại vận: <strong className="text-primary font-bold">{selectedPalace.decadal?.range && Array.isArray(selectedPalace.decadal.range) ? `${selectedPalace.decadal.range[0]} - ${selectedPalace.decadal.range[1]}` : '--'} tuổi</strong></span>
                      <span>•</span>
                      <span>Hành cung: <strong className="text-primary font-bold">{selectedPalace.heavenlyStem} {selectedPalace.earthlyBranch}</strong></span>
                    </div>
                  </div>

                  {/* Danh sách tinh tú chi tiết */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-body">
                    <div className="p-3 bg-white rounded-btn border border-[#E2D9C8] shadow-xs">
                      <h4 className="font-heading font-bold text-[#4A3B32] mb-2 flex items-center gap-1.5 uppercase text-xs">
                        <span>Chính Tinh ({selectedPalace.majorStars?.length || 0})</span>
                      </h4>
                      {selectedPalace.majorStars && selectedPalace.majorStars.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {selectedPalace.majorStars.map(s => {
                            const info = getStarInfo(s.name);
                            const bTag = formatBrightness(s.brightness);
                            return (
                              <span key={s.name} className={`px-2 py-1 rounded bg-[#FAF6EE] font-bold border border-surface-border/50 ${info.elementClass}`}>
                                {s.name} {bTag}
                              </span>
                            );
                          })}
                        </div>
                      ) : (
                        <span className="text-text-secondary italic">Vô chính diệu</span>
                      )}
                    </div>

                    <div className="p-3 bg-white rounded-btn border border-[#E2D9C8] shadow-xs">
                      <h4 className="font-heading font-bold text-[#4A3B32] mb-2 flex items-center gap-1.5 uppercase text-xs">
                        <span>Phụ Tinh & Vòng Sao</span>
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {(selectedPalace.minorStars || []).concat(selectedPalace.adjectiveStars || []).map(s => {
                          const info = getStarInfo(s.name);
                          return (
                            <span key={s.name} className={`px-2 py-0.5 rounded text-[11px] bg-surface border border-surface-border/40 ${info.elementClass}`}>
                              {s.name}
                            </span>
                          );
                        })}
                        {selectedPalace.changsheng12 && (
                          <span className="px-2 py-0.5 rounded text-[11px] bg-purple-50 text-purple-800 font-bold border border-purple-200">
                            {selectedPalace.changsheng12}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* CỘT PHẢI: SIDEBAR TÙY CHỈNH LÁ SỐ & LÁ SỐ ĐÃ TẠO */}
            <TuViCustomizerSidebar
              isGrayscale={isGrayscale}
              setIsGrayscale={setIsGrayscale}
              showChieuLine={showChieuLine}
              setShowChieuLine={setShowChieuLine}
              showPalaceDetail={showPalaceDetail}
              setShowPalaceDetail={setShowPalaceDetail}
              xemNam={xemNam}
              setXemNam={setXemNam}
              xemThang={xemThang}
              setXemThang={setXemThang}
              profiles={safeProfiles}
              currentProfileId={currentProfileId}
              onSelectProfile={(pId) => {
                setCurrentProfileId(pId);
                navigate(`/tu-vi?profile_id=${pId}`);
              }}
            />
          </div>

            {/* BẢN LUẬN GIẢI CHUYÊN SÂU TỪ ORCHESTRATOR */}
            <InterpretationTabs
              luanGiai={luanGiaiData}
              systemName="Tử Vi Đẩu Số"
              isLoading={aiLoading}
              birthProfileId={currentProfileId}
              chartData={chartData}
              onRetryGeneral={handleRetryGeneral}
            />

          </>
        ) : (
          <div className="card-base p-8 text-center space-y-4 max-w-md mx-auto shadow-card border border-amber-200 bg-amber-50/50 rounded-xl my-8">
            <IconInfoCircle size={44} className="mx-auto text-accent" />
            <h3 className="font-heading text-lg font-bold text-primary">Chưa Thể Hiển Thị Lá Số</h3>
            <p className="font-body text-xs text-text-secondary leading-relaxed">
              {error || 'Hồ sơ đã chọn không tồn tại hoặc dữ liệu chưa sẵn sàng. Quý bạn vui lòng chọn hồ sơ khác hoặc tạo mới.'}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
              <button
                onClick={() => {
                  if (currentProfileId) {
                    setLoading(true);
                    setError(null);
                    tuViService.getChartOnly(currentProfileId)
                      .then(res => {
                        const data = res.data?.du_lieu || res.data;
                        const ls = data.la_so || data;
                        if (ls) setLaSoData(ls);
                      })
                      .catch(() => {})
                      .finally(() => setLoading(false));
                  }
                }}
                className="px-4 py-2 bg-primary text-white rounded-btn text-xs font-bold hover:bg-primary-hover flex items-center gap-1.5 transition-colors shadow-xs"
              >
                <IconRefresh size={15} /> Thử lại
              </button>
              {safeProfiles.length > 0 && (
                <button
                  onClick={() => {
                    const next = safeProfiles.find(p => String(p.id) !== String(currentProfileId)) || safeProfiles[0];
                    if (next) {
                      setCurrentProfileId(next.id);
                      navigate(`/tu-vi?profile_id=${next.id}`);
                    }
                  }}
                  className="px-4 py-2 bg-white border border-primary/30 text-primary rounded-btn text-xs font-bold hover:bg-primary/5 flex items-center gap-1.5 transition-colors"
                >
                  <IconUser size={15} /> Chọn hồ sơ khác
                </button>
              )}
              <Link
                to="/birth-profile"
                className="px-4 py-2 bg-accent text-white rounded-btn text-xs font-bold hover:brightness-110 flex items-center gap-1.5 transition-colors shadow-xs"
              >
                <IconPlus size={15} /> Thêm hồ sơ mới
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
