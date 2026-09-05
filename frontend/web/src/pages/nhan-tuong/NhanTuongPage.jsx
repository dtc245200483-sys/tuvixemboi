import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  IconEye,
  IconHandStop,
  IconArrowLeft,
  IconUpload,
  IconTrash,
  IconShieldCheck,
  IconCheck,
  IconSparkles,
  IconInfoCircle,
  IconRefresh
} from '@tabler/icons-react';
import { nhanTuongService, visionService } from '../../services/api';
import BiometricConsentModal from '../../components/BiometricConsentModal';
import InterpretationTabs from '../../components/InterpretationTabs';
import QuotaBadge from '../../components/QuotaBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024; // 5MB

export default function NhanTuongPage() {
  const [activeTab, setActiveTab] = useState('tay'); // 'tay' hoặc 'mat'
  const [hasConsent, setHasConsent] = useState(false);
  const [showConsentModal, setShowConsentModal] = useState(false);
  const [checkingConsent, setCheckingConsent] = useState(true);

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [resultData, setResultData] = useState(null);
  const [quotaTrigger, setQuotaTrigger] = useState(0);

  const fileInputRef = useRef(null);

  // 1. Kiểm tra trạng thái Consent khi vào trang
  const checkConsentStatus = async () => {
    try {
      setCheckingConsent(true);
      const res = await visionService.getConsent();
      const status = res.data?.da_dong_y_sinh_trac_hoc;
      setHasConsent(!!status);
    } catch (err) {
      setHasConsent(false);
    } finally {
      setCheckingConsent(false);
    }
  };

  useEffect(() => {
    checkConsentStatus();
  }, []);

  // 2. Client-side Resize Image sử dụng HTML5 Canvas API (< 1280px max dimension, JPEG 0.85)
  const resizeImageClientSide = (file) => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const reader = new FileReader();

      reader.onload = (e) => {
        img.src = e.target.result;
      };
      reader.onerror = (e) => reject(new Error('Không thể đọc file ảnh'));

      img.onload = () => {
        const maxDim = 1280;
        let width = img.width;
        let height = img.height;

        if (width > maxDim || height > maxDim) {
          if (width > height) {
            height = Math.round((height * maxDim) / width);
            width = maxDim;
          } else {
            width = Math.round((width * maxDim) / height);
            height = maxDim;
          }
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            if (!blob) {
              resolve(file); // Fallback về file gốc nếu canvas lỗi
              return;
            }
            const resizedFile = new File([blob], file.name, {
              type: 'image/jpeg',
              lastModified: Date.now(),
            });
            resolve(resizedFile);
          },
          'image/jpeg',
          0.85
        );
      };

      reader.readAsDataURL(file);
    });
  };

  // 3. Xử lý khi chọn file ảnh
  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!hasConsent) {
      setShowConsentModal(true);
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setError('Dung lượng tệp vượt quá 5MB. Vui lòng chọn ảnh nhỏ hơn.');
      return;
    }

    setError(null);
    try {
      const resized = await resizeImageClientSide(file);
      setSelectedFile(resized);
      setPreviewUrl(URL.createObjectURL(resized));
      setResultData(null);
    } catch (err) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  // 4. Kích hoạt phân tích ảnh Vision
  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Vui lòng chọn hình ảnh trước khi bắt đầu phân tích.');
      return;
    }

    if (!hasConsent) {
      setShowConsentModal(true);
      return;
    }

    setIsProcessing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append(
      'cau_hoi',
      activeTab === 'tay'
        ? 'Luận giải tướng bàn tay, đường chỉ đạo và cung vị tài lộc'
        : 'Luận giải diện mạo khuôn mặt, tam đình và ngũ quan'
    );

    try {
      const apiCall = activeTab === 'tay' ? nhanTuongService.xemTay : nhanTuongService.xemMat;
      const res = await apiCall(formData);
      const data = res.data?.du_lieu || res.data;
      setResultData(data);
      setQuotaTrigger((prev) => prev + 1);
    } catch (err) {
      if (err.response) {
        if (err.response.status === 403) {
          setHasConsent(false);
          setShowConsentModal(true);
          setError('Quý vị chưa xác nhận sự đồng ý sinh trắc học. Vui lòng xác nhận trước khi tiếp tục.');
        } else {
          const detail = err.response.data?.detail || err.response.data?.loi;
          setError(typeof detail === 'string' ? detail : 'Phân tích hình ảnh thất bại. Vui lòng thử lại.');
        }
      } else {
        setError('Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại mạng.');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  // 5. Xóa ảnh ngay lập tức
  const handleDeletePhoto = async () => {
    if (!resultData?.id) return;
    try {
      await visionService.deleteAnh(resultData.id);
      setSelectedFile(null);
      setPreviewUrl(null);
      setResultData(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      setError('Không thể xóa ảnh lúc này. Vui lòng thử lại.');
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResultData(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const dacDiem = resultData?.dac_diem_quan_sat || {};

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
                <span>Nhân Tướng Học Thị Giác</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-accent/30 text-text-on-primary border border-accent/40 font-normal">
                  Vision AI
                </span>
              </h1>
              <p className="text-xs text-[#D8C7B5] font-body hidden sm:block">
                Phân Tích Vân Tay, Chỉ Tay & Diện Mạo Khuôn Mặt
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

        {/* Chuyển đổi 2 Tab: Xem Tay và Xem Mặt */}
        <div className="flex rounded-card p-1.5 bg-[#FAF5EE] border border-surface-border gap-2">
          <button
            type="button"
            onClick={() => {
              setActiveTab('tay');
              handleReset();
            }}
            className={`flex-1 py-3 text-sm font-body font-semibold rounded-btn flex items-center justify-center gap-2 transition-all ${
              activeTab === 'tay'
                ? 'bg-primary text-text-on-primary shadow-subtle'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            <IconHandStop size={18} className={activeTab === 'tay' ? 'text-accent' : ''} />
            <span>Tướng Bàn Tay & Chỉ Tay</span>
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveTab('mat');
              handleReset();
            }}
            className={`flex-1 py-3 text-sm font-body font-semibold rounded-btn flex items-center justify-center gap-2 transition-all ${
              activeTab === 'mat'
                ? 'bg-primary text-text-on-primary shadow-subtle'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            <IconEye size={18} className={activeTab === 'mat' ? 'text-accent' : ''} />
            <span>Diện Mạo Khuôn Mặt</span>
          </button>
        </div>

        {/* Khối Tải Ảnh & Xem Trước */}
        <div className="card-base p-6 sm:p-8 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-surface-border pb-4">
            <div>
              <h2 className="font-heading text-2xl font-bold text-primary flex items-center gap-2">
                {activeTab === 'tay' ? <IconHandStop size={24} className="text-accent" /> : <IconEye size={24} className="text-accent" />}
                <span>{activeTab === 'tay' ? 'Tải Ảnh Bàn Tay' : 'Tải Ảnh Khuôn Mặt'}</span>
              </h2>
              <p className="text-xs font-body text-text-secondary mt-0.5">
                {activeTab === 'tay'
                  ? 'Chụp lòng bàn tay thẳng, ánh sáng rõ nét để nhận diện chính xác các đường Tâm đạo, Trí đạo, Sinh đạo.'
                  : 'Chụp chính diện khuôn mặt với biểu cảm tự nhiên để quan sát rõ Tam đình, Ngũ nhạc và Khí sắc.'}
              </p>
            </div>
            {hasConsent && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FAF5EE] border border-surface-border text-xs font-body text-accent self-start sm:self-auto">
                <IconShieldCheck size={16} />
                <span>Đã kích hoạt bảo mật</span>
              </span>
            )}
          </div>

          {/* Vùng Upload Kéo - Thả / Chọn File */}
          <div className="space-y-4">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/png,image/jpeg,image/webp"
              className="hidden"
            />

            {!previewUrl ? (
              <div
                onClick={() => {
                  if (!hasConsent) {
                    setShowConsentModal(true);
                  } else {
                    fileInputRef.current?.click();
                  }
                }}
                className="border-2 border-dashed border-surface-border hover:border-accent rounded-card p-8 sm:p-12 text-center cursor-pointer bg-[#FAF5EE]/40 hover:bg-[#FAF5EE]/80 transition-all space-y-3"
              >
                <div className="w-14 h-14 mx-auto rounded-full bg-surface border border-surface-border flex items-center justify-center text-accent shadow-xs">
                  <IconUpload size={26} stroke={1.75} />
                </div>
                <div className="space-y-1">
                  <p className="font-body text-sm font-semibold text-text-primary">
                    Bấm để chọn tệp hoặc kéo thả hình ảnh vào đây
                  </p>
                  <p className="font-body text-xs text-text-secondary">
                    Hỗ trợ định dạng JPG, PNG, WEBP (Tự động nén tối ưu, tối đa 5MB)
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Xem trước ảnh */}
                <div className="relative rounded-card overflow-hidden border border-surface-border bg-black/5 max-w-sm mx-auto shadow-subtle">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="w-full h-64 object-cover object-center"
                  />
                  <button
                    type="button"
                    onClick={handleReset}
                    className="absolute top-2 right-2 p-1.5 rounded-full bg-surface/90 hover:bg-surface text-text-primary shadow-subtle transition-all"
                    title="Đổi ảnh khác"
                  >
                    <IconRefresh size={16} />
                  </button>
                </div>

                {/* Nút hành động */}
                <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
                  <button
                    type="button"
                    onClick={handleReset}
                    disabled={isProcessing}
                    className="btn-outline w-full sm:w-auto px-5 py-2.5 text-sm"
                  >
                    Chọn Ảnh Khác
                  </button>
                  <button
                    type="button"
                    onClick={handleAnalyze}
                    disabled={isProcessing}
                    className="btn-primary w-full sm:w-auto px-7 py-2.5 text-sm shadow-subtle"
                  >
                    {isProcessing ? (
                      <LoadingSpinner size="sm" color="white" text="Đang phân tích đặc điểm nhân tướng..." />
                    ) : (
                      <>
                        <IconSparkles size={18} className="text-accent" />
                        <span>Bắt Đầu Luận Giải Tướng</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 2. KẾT QUẢ ĐẶC ĐIỂM QUAN SÁT & NÚT XÓA ẢNH */}
        {resultData && (
          <div className="space-y-8 animate-fadeIn">
            <div className="card-base p-6 sm:p-8 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
                <div>
                  <span className="text-xs font-mono font-bold text-accent uppercase tracking-wider block">
                    Thị Giác Máy Tính
                  </span>
                  <h3 className="font-heading text-2xl font-bold text-primary mt-0.5">
                    Đặc Điểm Nhân Tướng Nhận Diện
                  </h3>
                </div>
                <button
                  type="button"
                  onClick={handleDeletePhoto}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-btn bg-[#FAF0EE] border border-[#E6C2BC] text-xs font-body text-primary font-medium hover:bg-[#FAF0EE]/80 transition-colors self-start sm:self-auto"
                  title="Xóa vĩnh viễn hình ảnh khỏi hệ thống máy chủ"
                >
                  <IconTrash size={15} />
                  <span>Xóa Ảnh Này Ngay Lập Tức</span>
                </button>
              </div>

              {/* Lưới các đặc điểm chi tiết */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {Object.keys(dacDiem).length > 0 ? (
                  Object.entries(dacDiem).map(([key, val], idx) => {
                    const label = key
                      .replace(/_/g, ' ')
                      .replace(/^./, (s) => s.toUpperCase());
                    return (
                      <div
                        key={idx}
                        className="p-3.5 rounded-btn bg-[#FAF5EE] border border-surface-border space-y-1"
                      >
                        <span className="text-[11px] font-mono text-text-secondary uppercase tracking-wider block">
                          {label}
                        </span>
                        <div className="font-body text-sm font-semibold text-text-primary">
                          {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="col-span-full p-4 rounded-btn bg-[#FAF5EE] text-center text-xs font-body text-text-secondary">
                    Đã trích xuất cấu trúc hình học tổng quát phục vụ phân tích.
                  </div>
                )}
              </div>
            </div>

            {/* 3. BẢN LUẬN GIẢI CHUYÊN SÂU TỪ ORCHESTRATOR */}
            <InterpretationTabs luanGiai={resultData.luan_giai} systemName="Nhân Tướng Học" />
          </div>
        )}
      </main>

      {/* Modal Chấp Thuận Điều Khoản Sinh Trắc Học */}
      <BiometricConsentModal
        isOpen={showConsentModal}
        onClose={() => setShowConsentModal(false)}
        onConsentSuccess={() => {
          setHasConsent(true);
          setShowConsentModal(false);
          fileInputRef.current?.click();
        }}
      />
    </div>
  );
}
