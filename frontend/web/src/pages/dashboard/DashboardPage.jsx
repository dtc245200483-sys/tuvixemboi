import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  IconCompass,
  IconChartBar,
  IconCoins,
  IconEye,
  IconUser,
  IconCalendar,
  IconArrowRight,
  IconPlus,
  IconSparkles,
  IconLogout,
  IconMessageCircle,
  IconSettings
} from '@tabler/icons-react';
import { birthProfileService } from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import QuotaBadge from '../../components/QuotaBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function DashboardPage() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfiles = async () => {
      try {
        setLoading(true);
        const res = await birthProfileService.getAll();
        const list = res.data?.du_lieu || res.data || [];
        setProfiles(list);
        if (list.length > 0) {
          setSelectedProfile(list[0]);
        }
      } catch (err) {
        console.error('Lỗi lấy danh sách hồ sơ sinh:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfiles();
  }, []);

  const systems = [
    {
      id: 'tu-vi',
      name: 'Tử Vi Đẩu Số',
      subtitle: 'Lập lá số 12 cung định mệnh, an 108 vì sao và dự đoán vận hạn trọn đời.',
      icon: IconCompass,
      badge: 'Chính Tông',
      requiresProfile: true,
      path: selectedProfile ? `/tu-vi?profile_id=${selectedProfile.id}` : '/tu-vi',
    },
    {
      id: 'bat-tu',
      name: 'Bát Tự Tứ Trụ',
      subtitle: 'Phân tích Thiên Can - Địa Chi, cân bằng Ngũ Hành và tìm Dụng Thần cải mệnh.',
      icon: IconChartBar,
      badge: 'Tử Bình',
      requiresProfile: true,
      path: selectedProfile ? `/bat-tu?profile_id=${selectedProfile.id}` : '/bat-tu',
    },
    {
      id: 'kinh-dich',
      name: 'Kinh Dịch Chiêm Bái',
      subtitle: 'Gieo quẻ hỏi việc cụ thể qua Lục Hào, định đoán thời vận cát hung hanh thông.',
      icon: IconCoins,
      badge: 'Chu Dịch',
      requiresProfile: false,
      path: '/kinh-dich',
    },
    {
      id: 'nhan-tuong',
      name: 'Nhân Tướng Học',
      subtitle: 'Thị giác máy tính phân tích vân bàn tay, gò chỉ và diện mạo khuôn mặt.',
      icon: IconEye,
      badge: 'Vision AI',
      requiresProfile: false,
      path: '/nhan-tuong',
    },
  ];

  const handleSelectSystem = (sys) => {
    if (sys.requiresProfile && !selectedProfile) {
      navigate('/birth-profile');
    } else {
      navigate(sys.path);
    }
  };

  const lunar = selectedProfile?.thong_tin_am_lich || {};

  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* Header thanh điều hướng chính */}
      <header className="bg-primary text-text-on-primary border-b border-[#552218] px-4 sm:px-8 py-4 shadow-subtle sticky top-0 z-20">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-btn bg-[#552218] border border-accent/40 flex items-center justify-center text-accent">
              <IconCompass size={24} stroke={1.75} />
            </div>
            <div>
              <h1 className="font-heading text-xl sm:text-2xl font-bold tracking-wide text-text-on-primary">
                Khai Tâm Huyền Học
              </h1>
              <p className="text-xs text-[#D8C7B5] font-body hidden sm:block">
                Nền tảng luận giải Mệnh Lý & Trí Tuệ Nhân Tạo
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/chat"
              className="text-xs font-body px-3 py-1.5 rounded-btn bg-[#552218] border border-surface-border/30 hover:border-accent text-text-on-primary flex items-center gap-1.5 transition-colors"
              title="Đàm đạo cùng Trợ lý Huyền học AI"
            >
              <IconMessageCircle size={15} className="text-accent" />
              <span className="hidden sm:inline font-medium">Trò Chuyện AI</span>
            </Link>
            <QuotaBadge className="bg-[#552218] border-surface-border/30 text-text-on-primary" />
            <Link
              to="/settings"
              className="text-xs font-body px-3 py-1.5 rounded-btn bg-[#552218] border border-surface-border/30 hover:border-accent text-text-on-primary flex items-center gap-1.5 transition-colors"
              title="Cài đặt tài khoản & dữ liệu"
            >
              <IconSettings size={15} className="text-[#D8C7B5] hover:text-accent" />
              <span className="hidden md:inline">Cài Đặt</span>
            </Link>
            <button
              onClick={logout}
              className="text-xs font-body px-3 py-1.5 rounded-btn bg-[#552218] border border-surface-border/30 hover:border-accent text-text-on-primary flex items-center gap-1.5 transition-colors"
              title="Đăng xuất khỏi tài khoản"
            >
              <IconLogout size={15} />
              <span className="hidden sm:inline">Đăng xuất</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-8 py-8 space-y-8">
        {/* Khối Thông Tin Hồ Sơ Mệnh Chủ */}
        {loading ? (
          <div className="card-base p-6 text-center">
            <LoadingSpinner size="md" text="Đang đồng bộ hồ sơ mệnh chủ..." />
          </div>
        ) : selectedProfile ? (
          <div className="card-base p-6 sm:p-7 border border-surface-border shadow-subtle flex flex-col md:flex-row items-start md:items-center justify-between gap-6 bg-surface">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full bg-[#FAF5EE] border border-surface-border text-xs font-semibold text-accent uppercase tracking-wider">
                <IconUser size={14} />
                <span>Hồ Sơ Mệnh Đang Chọn</span>
              </div>
              <h2 className="font-heading text-2xl sm:text-3xl font-bold text-primary">
                {selectedProfile.ho_ten || 'Mệnh Chủ'}
              </h2>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm font-body text-text-secondary">
                <span>
                  Dương lịch: <strong>{selectedProfile.ngay_sinh_duong}</strong> ({selectedProfile.gio_sinh}h:{String(selectedProfile.phut_sinh).padStart(2, '0')})
                </span>
                <span>•</span>
                <span>
                  Âm lịch: Ngày {lunar.ngay_am || selectedProfile.ngay_sinh_am || '--'} tháng {lunar.thang_am || '--'} năm {lunar.nam_am || '--'}
                </span>
                <span>•</span>
                <span className="text-primary font-medium">
                  {lunar.can_chi_nam || ''} ({selectedProfile.gioi_tinh === 'nam' ? 'Nam Mạng' : 'Nữ Mạng'})
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3 w-full md:w-auto">
              <Link
                to="/birth-profile"
                className="btn-outline w-full md:w-auto text-xs sm:text-sm px-4 py-2.5 flex items-center justify-center gap-1.5"
              >
                <IconPlus size={16} />
                <span>Hồ Sơ Khác</span>
              </Link>
            </div>
          </div>
        ) : (
          <div className="card-base p-6 sm:p-8 border-2 border-dashed border-accent/40 bg-[#FAF5EE]/50 text-center space-y-4">
            <div className="w-12 h-12 mx-auto rounded-full bg-surface border border-accent/30 flex items-center justify-center text-accent">
              <IconCalendar size={24} />
            </div>
            <div>
              <h3 className="font-heading text-2xl font-bold text-primary">
                Chưa Có Hồ Sơ Mệnh Lý
              </h3>
              <p className="font-body text-sm text-text-secondary max-w-md mx-auto mt-1">
                Vui lòng nhập thông tin ngày giờ sinh để hệ thống tự động quy đổi Âm lịch, an sao Tử Vi và tính Tứ Trụ Bát Tự.
              </p>
            </div>
            <Link
              to="/birth-profile"
              className="btn-primary inline-flex items-center gap-2 px-6 py-3 text-sm shadow-subtle"
            >
              <IconPlus size={18} />
              <span>Thiết Lập Hồ Sơ Sinh Ngay</span>
            </Link>
          </div>
        )}

        {/* Banner Trò Chuyện Huyền Học AI */}
        <div className="card-base p-6 sm:p-7 border border-accent/40 bg-[#FAF5EE] shadow-subtle flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-card bg-surface border border-accent/40 flex items-center justify-center text-accent flex-shrink-0 shadow-xs">
              <IconMessageCircle size={26} stroke={1.75} />
            </div>
            <div className="space-y-1">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-surface border border-surface-border text-[11px] font-semibold text-accent uppercase tracking-wider">
                <IconSparkles size={13} />
                <span>Trí Tuệ Nhân Tạo Tích Hợp</span>
              </div>
              <h3 className="font-heading text-xl sm:text-2xl font-bold text-primary">
                Đàm Đạo Huyền Học Cùng AI
              </h3>
              <p className="font-body text-sm text-text-secondary max-w-2xl leading-relaxed">
                Đặt câu hỏi tự do, tra cứu vận hạn, gieo quẻ Kinh Dịch, hoặc tải ảnh khuôn mặt và bàn tay để AI phân tích đa hệ thống theo thời gian thực.
              </p>
            </div>
          </div>

          <Link
            to="/chat"
            className="btn-primary w-full md:w-auto px-5 py-2.5 text-sm flex items-center justify-center gap-2 flex-shrink-0 shadow-subtle"
          >
            <span>Bắt Đầu Trò Chuyện</span>
            <IconArrowRight size={16} />
          </Link>
        </div>

        {/* Tiêu đề Danh Mục Hệ Thống */}
        <div className="space-y-1">
          <h2 className="font-heading text-2xl sm:text-3xl font-bold text-primary">
            Bốn Trụ Cột Huyền Học Á Đông
          </h2>
          <p className="font-body text-sm text-text-secondary">
            Chọn phương pháp chiêm đoán để bắt đầu hành trình thấu thị vận mệnh
          </p>
        </div>

        {/* Lưới 4 Card Lớn (2x2 Desktop, 1 Cột Mobile) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {systems.map((sys) => {
            const Icon = sys.icon;
            return (
              <div
                key={sys.id}
                onClick={() => handleSelectSystem(sys)}
                className="card-base p-6 sm:p-8 cursor-pointer group hover:border-accent hover:shadow-elevated transition-all flex flex-col justify-between space-y-6"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="w-14 h-14 rounded-card bg-[#FAF5EE] border border-surface-border group-hover:border-accent/40 flex items-center justify-center text-accent transition-colors shadow-xs">
                      <Icon size={30} stroke={1.75} />
                    </div>
                    <span className="text-xs font-mono font-bold text-accent uppercase tracking-wider px-3 py-1 rounded-full bg-[#FAF5EE] border border-surface-border">
                      {sys.badge}
                    </span>
                  </div>

                  <div className="space-y-2">
                    <h3 className="font-heading text-2xl font-bold text-text-primary group-hover:text-primary transition-colors">
                      {sys.name}
                    </h3>
                    <p className="font-body text-sm text-text-secondary leading-relaxed">
                      {sys.subtitle}
                    </p>
                  </div>
                </div>

                <div className="pt-4 border-t border-surface-border flex items-center justify-between text-sm font-body text-primary font-medium group-hover:translate-x-1 transition-transform">
                  <span>Khám phá ngay</span>
                  <IconArrowRight size={18} className="text-accent" />
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
