import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  IconCompass, IconChartBar, IconCoins, IconEye, IconUser,
  IconCalendar, IconArrowRight, IconPlus, IconSparkles, IconLogout,
  IconMessageCircle, IconSettings, IconLayoutDashboard, IconUsersGroup,
  IconStar, IconFlame, IconShieldCheck,
} from '@tabler/icons-react';
import { birthProfileService } from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import QuotaBadge from '../../components/QuotaBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import SelectProfileModal from '../../components/SelectProfileModal';
import CalendarView from './CalendarView';
import ForumView from './ForumView';

// ============================================================
// Helpers
// ============================================================
function getTodayCanChi() {
  // Tính Can Chi ngày hôm nay từ epoch (Can Chi = (julianDay + offset) mod 10/12)
  const today = new Date();
  const jd = Math.floor(today.getTime() / 86400000) + 2440588;
  const CAN = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'];
  const CHI = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];
  const can = CAN[(jd + 9) % 10];
  const chi = CHI[(jd + 1) % 12];
  return `${can} ${chi}`;
}

function getGreeting() {
  const h = new Date().getHours();
  if (h < 6) return 'Chúc buổi đêm an lành';
  if (h < 12) return 'Chào buổi sáng';
  if (h < 18) return 'Chào buổi chiều';
  return 'Chào buổi tối';
}

const TODAY_DATE = new Date().toLocaleDateString('vi-VN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

// ============================================================
// Tab definitions
// ============================================================
const TABS = [
  { id: 'overview', label: 'Tổng Quan', icon: IconLayoutDashboard },
  { id: 'calendar', label: 'Xem Ngày', icon: IconCalendar },
  { id: 'systems', label: 'Huyền Học', icon: IconCompass },
  { id: 'chat', label: 'Trò Chuyện AI', icon: IconMessageCircle },
  { id: 'forum', label: 'Diễn Đàn', icon: IconUsersGroup },
];

// ============================================================
// Quick Stats widget
// ============================================================
function TodayWidget() {
  const canChi = getTodayCanChi();
  return (
    <div className="rounded-2xl overflow-hidden" style={{ border: '1px solid var(--color-surface-border)', background: 'var(--color-surface)' }}>
      <div className="px-5 py-3 border-b" style={{ borderColor: 'var(--color-surface-border)', background: 'rgba(107,43,31,0.03)' }}>
        <p className="text-xs font-body font-semibold uppercase tracking-wider" style={{ color: 'var(--color-accent)' }}>
          📅 Thông tin hôm nay
        </p>
      </div>
      <div className="px-5 py-4 grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div>
          <p className="text-[11px] font-body" style={{ color: 'var(--color-text-secondary)' }}>Ngày Can Chi</p>
          <p className="text-sm font-body font-bold mt-0.5" style={{ color: 'var(--color-primary)' }}>{canChi}</p>
        </div>
        <div>
          <p className="text-[11px] font-body" style={{ color: 'var(--color-text-secondary)' }}>Dương lịch</p>
          <p className="text-sm font-body font-bold mt-0.5" style={{ color: 'var(--color-text-primary)' }}>
            {new Date().toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })}
          </p>
        </div>
        <div className="col-span-2 sm:col-span-1">
          <p className="text-[11px] font-body" style={{ color: 'var(--color-text-secondary)' }}>Thứ trong tuần</p>
          <p className="text-sm font-body font-bold mt-0.5" style={{ color: 'var(--color-text-primary)' }}>
            {new Date().toLocaleDateString('vi-VN', { weekday: 'long' })}
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// System cards
// ============================================================
function SystemCard({ sys, onSelect }) {
  const Icon = sys.icon;
  return (
    <div
      onClick={() => onSelect(sys)}
      className="rounded-2xl p-5 cursor-pointer group transition-all hover:shadow-md"
      style={{ background: 'var(--color-surface)', border: '1px solid var(--color-surface-border)' }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 rounded-xl flex items-center justify-center transition-colors"
          style={{ background: 'rgba(107,43,31,0.08)', border: '1px solid var(--color-surface-border)' }}>
          <Icon size={26} style={{ color: 'var(--color-accent)' }} stroke={1.75} />
        </div>
        <span className="text-[11px] font-body font-bold uppercase tracking-wider px-2.5 py-1 rounded-full"
          style={{ background: 'rgba(201,150,44,0.12)', color: 'var(--color-accent)', border: '1px solid rgba(201,150,44,0.3)' }}>
          {sys.badge}
        </span>
      </div>
      <h3 className="font-body text-base font-bold group-hover:text-primary transition-colors" style={{ color: 'var(--color-text-primary)' }}>
        {sys.name}
      </h3>
      <p className="font-body text-xs mt-1.5 leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
        {sys.subtitle}
      </p>
      <div className="mt-4 pt-3 border-t flex items-center justify-between text-sm font-body font-medium group-hover:translate-x-1 transition-transform"
        style={{ borderColor: 'var(--color-surface-border)', color: 'var(--color-primary)' }}>
        <span>Khám phá ngay</span>
        <IconArrowRight size={16} style={{ color: 'var(--color-accent)' }} />
      </div>
    </div>
  );
}

// ============================================================
// Overview Tab Content
// ============================================================
function OverviewTab({ selectedProfile, systems, onSelectSystem, setActiveTab }) {
  return (
    <div className="space-y-6">
      {/* Today widget */}
      <TodayWidget />

      {/* Quick Actions */}
      <div>
        <h3 className="font-body font-semibold text-sm mb-3" style={{ color: 'var(--color-text-secondary)' }}>
          ⚡ Truy cập nhanh
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'An Sao Tử Vi', icon: IconCompass, emoji: '🔭', action: () => window.location.href = selectedProfile ? `/tu-vi?profile_id=${selectedProfile.id}` : '/tu-vi' },
            { label: 'Gieo Quẻ', icon: IconCoins, emoji: '☯️', action: () => window.location.href = '/kinh-dich' },
            { label: 'Nhân Tướng', icon: IconEye, emoji: '👁️', action: () => window.location.href = '/nhan-tuong' },
            { label: 'Đàm Đạo AI', icon: IconMessageCircle, emoji: '💬', action: () => setActiveTab('chat') },
          ].map((q) => (
            <button key={q.label} type="button" onClick={q.action}
              className="flex flex-col items-center gap-2 p-3.5 rounded-2xl text-center transition-all hover:shadow-md group"
              style={{ background: 'var(--color-surface)', border: '1px solid var(--color-surface-border)' }}>
              <span className="text-2xl">{q.emoji}</span>
              <span className="text-xs font-body font-semibold group-hover:text-primary transition-colors" style={{ color: 'var(--color-text-primary)' }}>
                {q.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* AI Chat banner */}
      <div className="rounded-2xl overflow-hidden" style={{ background: 'linear-gradient(135deg, rgba(107,43,31,0.08) 0%, rgba(201,150,44,0.08) 100%)', border: '1px solid var(--color-surface-border)' }}>
        <div className="p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center"
              style={{ background: 'var(--color-surface)', border: '1px solid var(--color-surface-border)' }}>
              <IconSparkles size={24} style={{ color: 'var(--color-accent)' }} />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[11px] font-body font-bold uppercase tracking-wider px-2 py-0.5 rounded-full"
                  style={{ background: 'var(--color-accent)', color: 'var(--color-text-on-primary)' }}>AI</span>
                <span className="text-[11px] font-body" style={{ color: 'var(--color-text-secondary)' }}>Tích hợp đa hệ thống</span>
              </div>
              <h4 className="font-body font-bold text-base" style={{ color: 'var(--color-text-primary)' }}>Đàm Đạo Huyền Học Cùng AI</h4>
              <p className="text-xs font-body mt-0.5" style={{ color: 'var(--color-text-secondary)' }}>
                Tử Vi • Bát Tự • Kinh Dịch • Nhân Tướng — hỏi đáp tự do
              </p>
            </div>
          </div>
          <Link to="/chat"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-body font-medium flex-shrink-0 transition-all hover:shadow-md"
            style={{ background: 'var(--color-primary)', color: 'var(--color-text-on-primary)' }}>
            Bắt đầu <IconArrowRight size={14} />
          </Link>
        </div>
      </div>

      {/* 4 Systems preview (2x2) */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-body font-semibold text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            🔮 Bốn Trụ Cột Huyền Học
          </h3>
          <button type="button" onClick={() => setActiveTab('systems')}
            className="text-xs font-body flex items-center gap-1 transition-colors hover:opacity-80"
            style={{ color: 'var(--color-accent)' }}>
            Xem tất cả <IconArrowRight size={13} />
          </button>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {systems.map((sys) => <SystemCard key={sys.id} sys={sys} onSelect={onSelectSystem} />)}
        </div>
      </div>
    </div>
  );
}

// ============================================================
// Main DashboardPage
// ============================================================
export default function DashboardPage() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSelectModal, setShowSelectModal] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchProfiles = async () => {
      try {
        setLoading(true);
        const res = await birthProfileService.getAll();
        const list = res.data?.du_lieu || res.data || [];
        setProfiles(list);
        if (list.length > 0) {
          const savedId = typeof window !== 'undefined' ? localStorage.getItem('selected_ho_so_menh_id') : null;
          let matched = null;
          if (user?.default_birth_profile_id || list.some((p) => p.is_default)) {
            matched = list.find((p) => p.is_default || (user?.default_birth_profile_id && String(p.id) === String(user.default_birth_profile_id)));
          }
          if (!matched && savedId) matched = list.find((p) => String(p.id) === String(savedId));
          if (!matched) {
            const nonQuick = list.filter((p) => !p.is_quick_chart);
            matched = [...(nonQuick.length > 0 ? nonQuick : list)].sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0))[0];
          }
          setSelectedProfile(matched);
          if (matched && typeof window !== 'undefined') localStorage.setItem('selected_ho_so_menh_id', matched.id);
        }
      } catch (err) {
        console.error('Lỗi lấy danh sách hồ sơ sinh:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfiles();
  }, [user]);

  const systems = [
    { id: 'tu-vi', name: 'Tử Vi Đẩu Số', subtitle: 'Lập lá số 12 cung định mệnh, an 108 vì sao và dự đoán vận hạn trọn đời.', icon: IconCompass, badge: 'Chính Tông', requiresProfile: true, path: selectedProfile ? `/tu-vi?profile_id=${selectedProfile.id}` : '/tu-vi' },
    { id: 'bat-tu', name: 'Bát Tự Tứ Trụ', subtitle: 'Phân tích Thiên Can - Địa Chi, cân bằng Ngũ Hành và tìm Dụng Thần cải mệnh.', icon: IconChartBar, badge: 'Tử Bình', requiresProfile: true, path: selectedProfile ? `/bat-tu?profile_id=${selectedProfile.id}` : '/bat-tu' },
    { id: 'kinh-dich', name: 'Kinh Dịch Chiêm Bái', subtitle: 'Gieo quẻ hỏi việc cụ thể qua Lục Hào, định đoán thời vận cát hung hanh thông.', icon: IconCoins, badge: 'Chu Dịch', requiresProfile: false, path: '/kinh-dich' },
    { id: 'nhan-tuong', name: 'Nhân Tướng Học', subtitle: 'Thị giác máy tính phân tích vân bàn tay, gò chỉ và diện mạo khuôn mặt.', icon: IconEye, badge: 'Vision AI', requiresProfile: false, path: '/nhan-tuong' },
  ];

  const handleSelectSystem = (sys) => {
    if (sys.requiresProfile && !selectedProfile) navigate('/birth-profile');
    else navigate(sys.path);
  };

  const lunar = selectedProfile?.thong_tin_am_lich || {};

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-background)', color: 'var(--color-text-primary)' }}>
      {/* ============================================================
          HEADER
      ============================================================ */}
      <header style={{ background: 'var(--color-primary)', color: 'var(--color-text-on-primary)' }}
        className="border-b border-black/10 px-4 sm:px-8 py-3.5 shadow-md sticky top-0 z-20">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(201,150,44,0.4)' }}>
              <IconCompass size={20} style={{ color: 'var(--color-accent)' }} stroke={1.75} />
            </div>
            <div>
              <h1 className="font-body text-lg font-bold tracking-wide" style={{ color: 'var(--color-text-on-primary)' }}>
                Khai Tâm Huyền Học
              </h1>
              <p className="text-[11px] hidden sm:block" style={{ color: 'rgba(251,243,230,0.7)' }}>
                Nền tảng Mệnh Lý & Trí Tuệ Nhân Tạo
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <QuotaBadge />
            <Link to="/settings"
              className="hidden sm:flex items-center gap-1.5 text-xs font-body px-2.5 py-1.5 rounded-lg transition-colors"
              style={{ background: 'rgba(0,0,0,0.15)', color: 'var(--color-text-on-primary)' }}>
              <IconSettings size={14} /> Cài đặt
            </Link>
            <button onClick={logout}
              className="flex items-center gap-1.5 text-xs font-body px-2.5 py-1.5 rounded-lg transition-colors"
              style={{ background: 'rgba(0,0,0,0.15)', color: 'var(--color-text-on-primary)' }}>
              <IconLogout size={14} />
              <span className="hidden sm:inline">Đăng xuất</span>
            </button>
          </div>
        </div>
      </header>

      {/* ============================================================
          HERO — Profile card
      ============================================================ */}
      <div style={{ background: 'var(--color-primary)' }} className="border-b border-black/10">
        <div className="max-w-6xl mx-auto px-4 sm:px-8 py-6">
          {loading ? (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full animate-pulse" style={{ background: 'rgba(255,255,255,0.15)' }} />
              <div className="space-y-1.5">
                <div className="h-3 w-32 rounded animate-pulse" style={{ background: 'rgba(255,255,255,0.15)' }} />
                <div className="h-2 w-48 rounded animate-pulse" style={{ background: 'rgba(255,255,255,0.1)' }} />
              </div>
            </div>
          ) : selectedProfile ? (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                  style={{ background: 'rgba(255,255,255,0.15)', border: '2px solid rgba(201,150,44,0.5)' }}>
                  <IconUser size={24} style={{ color: 'var(--color-accent)' }} />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-body font-bold uppercase tracking-widest px-2 py-0.5 rounded-full"
                      style={{ background: 'rgba(201,150,44,0.25)', color: 'var(--color-accent)', border: '1px solid rgba(201,150,44,0.4)' }}>
                      Hồ Sơ Mệnh Đang Chọn
                    </span>
                  </div>
                  <h2 className="font-body text-xl sm:text-2xl font-bold" style={{ color: 'var(--color-text-on-primary)' }}>
                    {getGreeting()}, {selectedProfile.ho_ten?.split(' ').pop() || 'Mệnh Chủ'}!
                  </h2>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 text-xs font-body mt-1"
                    style={{ color: 'rgba(251,243,230,0.75)' }}>
                    <span>Dương Lịch: <strong style={{ color: 'rgba(251,243,230,0.95)' }}>{selectedProfile.ngay_sinh_duong ? selectedProfile.ngay_sinh_duong.split('-').reverse().join('/') : '--'}</strong></span>
                    <span>•</span>
                    <span>Âm Lịch: <strong style={{ color: 'rgba(251,243,230,0.95)' }}>Ngày {lunar.ngay_am || selectedProfile.ngay_sinh_am || '--'} tháng {lunar.thang_am || '--'} năm {lunar.nam_am || '--'}</strong></span>
                    <span>•</span>
                    <span style={{ color: 'var(--color-accent)' }}>{lunar.can_chi_nam || ''} ({selectedProfile.gioi_tinh === 'nam' ? 'Nam Mạng' : 'Nữ Mạng'})</span>
                  </div>
                </div>
              </div>
              <button type="button" onClick={() => setShowSelectModal(true)}
                className="flex items-center gap-1.5 text-xs font-body px-4 py-2 rounded-xl self-start sm:self-auto transition-all hover:shadow-md"
                style={{ background: 'rgba(255,255,255,0.12)', color: 'var(--color-text-on-primary)', border: '1px solid rgba(255,255,255,0.2)' }}>
                <IconPlus size={14} /> Đổi hồ sơ
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="font-body text-xl font-bold" style={{ color: 'var(--color-text-on-primary)' }}>
                  {getGreeting()}! Chào mừng đến Khai Tâm Huyền Học
                </h2>
                <p className="text-xs font-body mt-1" style={{ color: 'rgba(251,243,230,0.7)' }}>
                  Thiết lập hồ sơ mệnh lý để mở khóa toàn bộ tính năng
                </p>
              </div>
              <Link to="/birth-profile"
                className="flex items-center gap-1.5 text-xs font-body px-4 py-2.5 rounded-xl flex-shrink-0"
                style={{ background: 'var(--color-accent)', color: '#2E1B10', fontWeight: 600 }}>
                <IconPlus size={14} /> Tạo hồ sơ
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* ============================================================
          FEATURE TABS (hàng ngang)
      ============================================================ */}
      <div style={{ background: 'var(--color-surface)', borderBottom: '1px solid var(--color-surface-border)' }}
        className="sticky top-[61px] z-10 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-8">
          <div className="flex overflow-x-auto scrollbar-none">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className="flex items-center gap-2 px-4 py-3.5 text-sm font-body font-medium whitespace-nowrap transition-all border-b-2 flex-shrink-0"
                  style={{
                    borderColor: isActive ? 'var(--color-primary)' : 'transparent',
                    color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                  }}
                >
                  <Icon size={16} />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ============================================================
          TAB CONTENT
      ============================================================ */}
      <main className="max-w-6xl mx-auto px-4 sm:px-8 py-6">
        {/* OVERVIEW */}
        {activeTab === 'overview' && (
          <OverviewTab
            selectedProfile={selectedProfile}
            systems={systems}
            onSelectSystem={handleSelectSystem}
            setActiveTab={setActiveTab}
          />
        )}

        {/* CALENDAR */}
        {activeTab === 'calendar' && (
          <div className="space-y-4">
            <div>
              <h2 className="font-body font-bold text-xl" style={{ color: 'var(--color-text-primary)' }}>
                📅 Xem Ngày — Âm Dương Lịch
              </h2>
              <p className="text-sm font-body mt-1" style={{ color: 'var(--color-text-secondary)' }}>
                Tra cứu ngày tháng, ghi nhật ký, đặt lịch nhắc và theo dõi Can Chi từng ngày.
              </p>
            </div>
            <CalendarView />
          </div>
        )}

        {/* SYSTEMS */}
        {activeTab === 'systems' && (
          <div className="space-y-6">
            <div>
              <h2 className="font-body font-bold text-xl" style={{ color: 'var(--color-text-primary)' }}>
                🔮 Bốn Trụ Cột Huyền Học Á Đông
              </h2>
              <p className="text-sm font-body mt-1" style={{ color: 'var(--color-text-secondary)' }}>
                Chọn phương pháp chiêm đoán để bắt đầu hành trình thấu thị vận mệnh
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {systems.map((sys) => <SystemCard key={sys.id} sys={sys} onSelect={handleSelectSystem} />)}
            </div>
          </div>
        )}

        {/* CHAT */}
        {activeTab === 'chat' && (
          <div className="space-y-4">
            <div>
              <h2 className="font-body font-bold text-xl" style={{ color: 'var(--color-text-primary)' }}>
                💬 Đàm Đạo Huyền Học Cùng AI
              </h2>
              <p className="text-sm font-body mt-1" style={{ color: 'var(--color-text-secondary)' }}>
                Hỏi đáp tự do về Tử Vi, Bát Tự, Kinh Dịch, Nhân Tướng và vận hạn.
              </p>
            </div>
            <div className="rounded-2xl p-6 text-center space-y-4"
              style={{ background: 'var(--color-surface)', border: '1px solid var(--color-surface-border)' }}>
              <div className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center"
                style={{ background: 'rgba(107,43,31,0.08)', border: '1px solid var(--color-surface-border)' }}>
                <IconSparkles size={32} style={{ color: 'var(--color-accent)' }} />
              </div>
              <div>
                <h3 className="font-body font-bold text-lg" style={{ color: 'var(--color-text-primary)' }}>
                  Mở trang trò chuyện riêng
                </h3>
                <p className="text-sm font-body mt-2 max-w-md mx-auto leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                  Phiên trò chuyện riêng biệt, lưu lịch sử theo từng chủ đề, hỗ trợ đính kèm ảnh nhân tướng.
                </p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-lg mx-auto text-xs">
                {['🔭 Tử Vi', '📊 Bát Tự', '☯️ Kinh Dịch', '👁️ Nhân Tướng'].map((f) => (
                  <div key={f} className="px-2 py-1.5 rounded-lg font-body"
                    style={{ background: 'rgba(107,43,31,0.06)', color: 'var(--color-primary)' }}>
                    {f}
                  </div>
                ))}
              </div>
              <Link to="/chat"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-body font-semibold shadow-md transition-all hover:shadow-lg"
                style={{ background: 'var(--color-primary)', color: 'var(--color-text-on-primary)' }}>
                <IconMessageCircle size={18} /> Vào Trò Chuyện AI
              </Link>
            </div>
          </div>
        )}

        {/* FORUM */}
        {activeTab === 'forum' && (
          <div className="space-y-4">
            <div>
              <h2 className="font-body font-bold text-xl" style={{ color: 'var(--color-text-primary)' }}>
                🌐 Diễn Đàn Cộng Đồng
              </h2>
              <p className="text-sm font-body mt-1" style={{ color: 'var(--color-text-secondary)' }}>
                Chia sẻ kinh nghiệm, hỏi đáp và giao lưu về Huyền Học cùng cộng đồng.
              </p>
            </div>
            <ForumView />
          </div>
        )}
      </main>

      {/* Select Profile Modal */}
      <SelectProfileModal
        isOpen={showSelectModal}
        onClose={() => setShowSelectModal(false)}
        profiles={profiles}
        selectedProfileId={selectedProfile?.id}
        onProfileSelected={(p) => {
          setSelectedProfile(p);
          if (typeof window !== 'undefined') localStorage.setItem('selected_ho_so_menh_id', p.id);
        }}
      />
    </div>
  );
}
