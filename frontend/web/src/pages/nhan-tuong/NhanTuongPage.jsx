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
  IconCamera,
  IconX,
  IconRotate,
} from '@tabler/icons-react';
import { nhanTuongService, visionService } from '../../services/api';
import BiometricConsentModal from '../../components/BiometricConsentModal';
import InterpretationTabs from '../../components/InterpretationTabs';
import QuotaBadge from '../../components/QuotaBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;

export default function NhanTuongPage() {
  const [activeTab, setActiveTab] = useState('tay');
  const [hasConsent, setHasConsent] = useState(false);
  const [showConsentModal, setShowConsentModal] = useState(false);
  const [checkingConsent, setCheckingConsent] = useState(true);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [resultData, setResultData] = useState(null);
  const [quotaTrigger, setQuotaTrigger] = useState(0);
  const [showCamera, setShowCamera] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [cameraError, setCameraError] = useState(null);
  const [facingMode, setFacingMode] = useState('user');

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const cameraCanvasRef = useRef(null);

  const checkConsentStatus = async () => {
    try {
      setCheckingConsent(true);
      const res = await visionService.getConsent();
      setHasConsent(!!(res.data?.da_dong_y_sinh_trac_hoc));
    } catch { setHasConsent(false); }
    finally { setCheckingConsent(false); }
  };
  useEffect(() => { checkConsentStatus(); }, []);

  const resizeImageClientSide = (file) => new Promise((resolve, reject) => {
    const img = new Image(), reader = new FileReader();
    reader.onload = (e) => { img.src = e.target.result; };
    reader.onerror = () => reject(new Error('Cannot read file'));
    img.onload = () => {
      const maxDim = 1280;
      let w = img.width, h = img.height;
      if (w > maxDim || h > maxDim) {
        if (w > h) { h = Math.round((h * maxDim) / w); w = maxDim; }
        else { w = Math.round((w * maxDim) / h); h = maxDim; }
      }
      const canvas = document.createElement('canvas');
      canvas.width = w; canvas.height = h;
      canvas.getContext('2d').drawImage(img, 0, 0, w, h);
      canvas.toBlob((blob) => {
        if (!blob) { resolve(file); return; }
        resolve(new File([blob], file.name, { type: 'image/jpeg', lastModified: Date.now() }));
      }, 'image/jpeg', 0.85);
    };
    reader.readAsDataURL(file);
  });

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!hasConsent) { setShowConsentModal(true); return; }
    if (file.size > MAX_FILE_SIZE_BYTES) { setError('Dung lượng tệp vượt quá 5MB.'); return; }
    setError(null);
    try {
      const resized = await resizeImageClientSide(file);
      setSelectedFile(resized); setPreviewUrl(URL.createObjectURL(resized)); setResultData(null);
    } catch { setSelectedFile(file); setPreviewUrl(URL.createObjectURL(file)); }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) { setError('Vui lòng chọn hình ảnh trước.'); return; }
    if (!hasConsent) { setShowConsentModal(true); return; }
    setIsProcessing(true); setError(null);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('cau_hoi', activeTab === 'tay'
      ? 'Luận giải tướng bàn tay, đường chỉ đạo và cung vị tài lộc'
      : 'Luận giải diện mạo khuôn mặt, tam đình và ngũ quan');
    try {
      const apiCall = activeTab === 'tay' ? nhanTuongService.xemTay : nhanTuongService.xemMat;
      const res = await apiCall(formData);
      setResultData(res.data?.du_lieu || res.data);
      setQuotaTrigger((p) => p + 1);
    } catch (err) {
      if (err.response?.status === 403) { setHasConsent(false); setShowConsentModal(true); setError('Chưa xác nhận đồng ý sinh trắc học.'); }
      else { const d = err.response?.data?.detail || err.response?.data?.loi; setError(typeof d === 'string' ? d : 'Phân tích thất bại.'); }
    } finally { setIsProcessing(false); }
  };

  const handleDeletePhoto = async () => {
    if (!resultData?.id) return;
    try {
      await visionService.deleteAnh(resultData.id);
      setSelectedFile(null); setPreviewUrl(null); setResultData(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch { setError('Không thể xóa ảnh.'); }
  };

  const handleReset = () => {
    setSelectedFile(null); setPreviewUrl(null); setResultData(null); setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const stopCamera = () => {
    if (cameraStream) { cameraStream.getTracks().forEach((t) => t.stop()); setCameraStream(null); }
  };
  useEffect(() => () => stopCamera(), []);

  const openCamera = async () => {
    setCameraError(null);
    if (!navigator?.mediaDevices?.getUserMedia) { setCameraError('Trình duyệt không hỗ trợ camera.'); return; }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: facingMode }, width: { ideal: 1920 }, height: { ideal: 1080 } },
        audio: false,
      });
      setCameraStream(stream); setShowCamera(true);
      setTimeout(() => { if (videoRef.current) { videoRef.current.srcObject = stream; videoRef.current.play().catch(() => {}); } }, 50);
    } catch (err) {
      if (err.name === 'NotAllowedError') setCameraError('Bạn đã từ chối quyền camera.');
      else if (err.name === 'NotFoundError') setCameraError('Không tìm thấy camera.');
      else setCameraError('Không thể mở camera: ' + (err.message || err.name));
    }
  };

  const switchCamera = async () => {
    stopCamera();
    const next = facingMode === 'user' ? 'environment' : 'user'; setFacingMode(next);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: next } }, audio: false });
      setCameraStream(stream);
      setTimeout(() => { if (videoRef.current) { videoRef.current.srcObject = stream; videoRef.current.play().catch(() => {}); } }, 50);
    } catch (err) { setCameraError('Không thể chuyển camera.'); }
  };

  const closeCamera = () => { stopCamera(); setShowCamera(false); setCameraError(null); };

  const captureFromCamera = async () => {
    const video = videoRef.current, canvas = cameraCanvasRef.current;
    if (!video || !canvas) return;
    const w = video.videoWidth || 1280, h = video.videoHeight || 720;
    canvas.width = w; canvas.height = h;
    canvas.getContext('2d').drawImage(video, 0, 0, w, h);
    canvas.toBlob(async (blob) => {
      if (!blob) { setCameraError('Không thể chụp ảnh.'); return; }
      const ts = Date.now();
      const file = new File([blob], `camera-${ts}.jpg`, { type: 'image/jpeg', lastModified: ts });
      setError(null);
      try {
        const resized = await resizeImageClientSide(file);
        setSelectedFile(resized); setPreviewUrl(URL.createObjectURL(resized)); setResultData(null);
      } catch { setSelectedFile(file); setPreviewUrl(URL.createObjectURL(file)); }
      closeCamera();
    }, 'image/jpeg', 0.92);
  };

  const dacDiem = resultData?.dac_diem_quan_sat || {};

  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* Header */}
      <header className="bg-primary text-text-on-primary border-b border-[#552218] px-4 sm:px-8 py-4 shadow-subtle sticky top-0 z-20">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link to="/dashboard"
              className="p-1.5 rounded-btn bg-[#552218] border border-surface-border/30 hover:border-accent text-text-on-primary transition-colors"
              title="Quay lại Tổng quan">
              <IconArrowLeft size={18} />
            </Link>
            <div>
              <h1 className="font-heading text-xl sm:text-2xl font-bold tracking-wide text-text-on-primary flex items-center gap-2">
                <span>Nhân Tướng Học Thị Giác</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-accent/30 text-text-on-primary border border-accent/40 font-normal">Vision AI</span>
              </h1>
              <p className="text-xs text-[#D8C7B5] font-body hidden sm:block">Phân Tích Vân Tay, Chỉ Tay &amp; Diện Mạo Khuôn Mặt</p>
            </div>
          </div>
          <QuotaBadge refreshTrigger={quotaTrigger} className="bg-[#552218] border-[#D4AF37]/60 text-text-on-primary" />
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-8 py-8 space-y-8">
        {error && <ErrorMessage message={error} onClose={() => setError(null)} className="mb-4" />}

        {/* Tab switcher */}
        <div className="flex rounded-card p-1.5 bg-[#FAF5EE] border border-surface-border gap-2">
          <button type="button" onClick={() => { setActiveTab('tay'); handleReset(); }}
            className={`flex-1 py-3 text-sm font-body font-semibold rounded-btn flex items-center justify-center gap-2 transition-all ${
              activeTab === 'tay' ? 'bg-primary text-text-on-primary shadow-subtle' : 'text-text-secondary hover:text-text-primary'
            }`}>
            <IconHandStop size={18} className={activeTab === 'tay' ? 'text-accent' : ''} />
            <span>Tướng Bàn Tay &amp; Chỉ Tay</span>
          </button>
          <button type="button" onClick={() => { setActiveTab('mat'); handleReset(); }}
            className={`flex-1 py-3 text-sm font-body font-semibold rounded-btn flex items-center justify-center gap-2 transition-all ${
              activeTab === 'mat' ? 'bg-primary text-text-on-primary shadow-subtle' : 'text-text-secondary hover:text-text-primary'
            }`}>
            <IconEye size={18} className={activeTab === 'mat' ? 'text-accent' : ''} />
            <span>Diện Mạo Khuôn Mặt</span>
          </button>
        </div>

        {/* Upload card */}
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
                <IconShieldCheck size={16} /><span>Đã kích hoạt bảo mật</span>
              </span>
            )}
          </div>

          <div className="space-y-4">
            <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/png,image/jpeg,image/webp" className="hidden" />

            {/* No image yet */}
            {!previewUrl && (
              <div className="space-y-4">
                {hasConsent ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button type="button" onClick={openCamera}
                      className="flex flex-col items-center justify-center gap-3 p-8 rounded-card border-2 border-dashed border-surface-border bg-[#FAF5EE]/40 hover:bg-[#FAF5EE]/80 hover:border-accent/40 transition-all cursor-pointer group">
                      <div className="w-14 h-14 rounded-full bg-surface border border-surface-border flex items-center justify-center text-accent shadow-xs group-hover:shadow-md transition-all">
                        <IconCamera size={28} stroke={1.75} />
                      </div>
                      <div className="space-y-1 text-center">
                        <p className="font-body text-sm font-semibold text-text-primary">Chụp ảnh trực tiếp</p>
                        <p className="font-body text-xs text-text-secondary">Dùng camera thiết bị để chụp ngay</p>
                      </div>
                    </button>
                    <button type="button" onClick={() => fileInputRef.current?.click()}
                      className="flex flex-col items-center justify-center gap-3 p-8 rounded-card border-2 border-dashed border-surface-border bg-[#FAF5EE]/40 hover:bg-[#FAF5EE]/80 hover:border-accent/40 transition-all cursor-pointer group">
                      <div className="w-14 h-14 rounded-full bg-surface border border-surface-border flex items-center justify-center text-accent shadow-xs group-hover:shadow-md transition-all">
                        <IconUpload size={28} stroke={1.75} />
                      </div>
                      <div className="space-y-1 text-center">
                        <p className="font-body text-sm font-semibold text-text-primary">Tải ảnh từ thiết bị</p>
                        <p className="font-body text-xs text-text-secondary">JPG, PNG, WEBP — tối đa 5MB</p>
                      </div>
                    </button>
                  </div>
                ) : (
                  <button type="button" onClick={() => setShowConsentModal(true)}
                    className="w-full flex flex-col items-center justify-center gap-3 p-10 rounded-card border-2 border-dashed border-surface-border bg-surface text-center cursor-pointer hover:bg-[#FAF5EE]/40 transition-all">
                    <div className="w-14 h-14 rounded-full border border-surface-border flex items-center justify-center">
                      <IconX size={14} style={{ color: '#c0392b' }} />
                    </div>
                    <p className="font-body text-sm font-semibold text-text-secondary">
                      Vui lòng đồng ý điều khoản sinh trắc học để tiếp tục
                    </p>
                    <span className="text-xs font-body text-accent underline">Xem và đồng ý ngay</span>
                  </button>
                )}
              </div>
            )}

            {/* Has image */}
            {previewUrl && (
              <div className="space-y-4">
                <div className="relative rounded-card overflow-hidden border border-surface-border bg-black/5 max-w-sm mx-auto shadow-subtle">
                  <img src={previewUrl} alt="Preview" className="w-full max-h-[400px] object-contain object-center" />
                  <button type="button" onClick={handleReset}
                    className="absolute top-2 right-2 p-1.5 rounded-full bg-surface/90 hover:bg-surface text-text-primary shadow-subtle transition-all"
                    title="Xóa ảnh">
                    <IconX size={16} />
                  </button>
                </div>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
                  <button type="button" onClick={() => fileInputRef.current?.click()} disabled={isProcessing}
                    className="btn-outline w-full sm:w-auto px-5 py-2.5 text-sm flex items-center justify-center gap-1.5">
                    <IconUpload size={15} />
                    Thêm Ảnh
                  </button>
                  <button type="button" onClick={handleAnalyze} disabled={isProcessing}
                    className="btn-primary w-full sm:w-auto px-7 py-2.5 text-sm shadow-subtle">
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

            {/* Camera modal */}
            {showCamera && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                <div className="relative w-full max-w-3xl mx-4 rounded-2xl overflow-hidden shadow-2xl bg-surface border border-surface-border">
                  <div className="flex items-center justify-between px-6 py-4 border-b border-surface-border">
                    <h3 className="font-heading text-xl font-bold text-primary">Chụp Ảnh</h3>
                    <div className="flex items-center gap-3">
                      <button type="button" onClick={switchCamera}
                        className="p-2 rounded-full bg-surface/90 hover:bg-surface text-text-primary transition-colors"
                        title="Chuyển camera"><IconRotate size={16} /></button>
                      <button type="button" onClick={closeCamera}
                        className="p-2 rounded-full bg-surface/90 hover:bg-surface text-text-primary transition-colors"
                        title="Đóng"><IconX size={16} /></button>
                    </div>
                  </div>
                  <div className="relative flex-1 flex items-center justify-center bg-black/50">
                    <video ref={videoRef} className="w-full h-full object-contain max-h-[500px]" autoPlay playsInline />
                    <canvas ref={cameraCanvasRef} className="absolute top-0 left-0 w-full h-full opacity-0" />
                  </div>
                  <div className="flex items-center justify-between px-6 py-4 border-t border-surface-border">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-body text-text-secondary">
                        {facingMode === 'user' ? 'Camera trước' : 'Camera sau'}
                      </span>
                      {cameraError && (
                        <span className="text-xs font-body text-[#c0392b] bg-[#FFF9EE]/50 px-2 py-0.5 rounded-full">
                          {cameraError}
                        </span>
                      )}
                    </div>
                    <button type="button" onClick={captureFromCamera}
                      className="btn-primary px-6 py-2.5 text-sm shadow-subtle flex items-center gap-1.5"
                      disabled={!cameraStream}>
                      <IconCheck size={16} />
                      <span>Chụp Ảnh</span>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Results */}
        {resultData && (
          <div className="space-y-8 animate-fadeIn">
            <div className="card-base p-6 sm:p-8 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
                <div>
                  <span className="text-xs font-mono font-bold text-accent uppercase tracking-wider block">Thị Giác Máy Tính</span>
                  <h3 className="font-heading text-2xl font-bold text-primary mt-0.5">Đặc Điểm Nhân Tướng Nhận Diện</h3>
                </div>
                <button type="button" onClick={handleDeletePhoto}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-btn bg-[#FAF0EE] border border-[#E6C2BC] text-xs font-body text-primary font-medium hover:bg-[#FAF0EE]/80 transition-colors self-start sm:self-auto"
                  title="Xóa vĩnh viễn hình ảnh khỏi hệ thống máy chủ">
                  <IconTrash size={15} />
                  <span>Xóa Ảnh Này Ngay Lập Tức</span>
                </button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {Object.keys(dacDiem).length > 0 ? (
                  Object.entries(dacDiem).map(([key, val], idx) => {
                    const labelMap = {
                      hinh_dang_tran: 'Hình Dáng Trán',
                      hinh_dang_mat: 'Hình Dáng Mắt',
                      hinh_dang_mui: 'Hình Dáng Mũi',
                      hinh_dang_mieng: 'Hình Dáng Miệng & Môi',
                      hinh_dang_cam: 'Hình Dáng Cằm & Quai Hàm',
                      vi_tri_not_ruoi: 'Vị Trí Nốt Ruồi Cố Định',
                      ti_vet_da_lieu_hoac_mun: 'Mụn & Tì Vết Tạm Thời (Không Phải Nốt Ruồi)',
                      mo_ta_them: 'Mô Tả Tổng Thể',
                      hinh_dang_ban_tay: 'Hình Dáng Bàn Tay',
                      do_ro_duong_tam_dao: 'Đường Tâm Đạo (Tình Cảm)',
                      do_ro_duong_tri_dao: 'Đường Trí Đạo (Trí Tuệ)',
                      do_ro_duong_sinh_dao: 'Đường Sinh Đạo (Thể Lực)',
                      hinh_dang_ngon_tay: 'Hình Dáng Ngón Tay',
                    };
                    const label = labelMap[key] || key.replace(/_/g, ' ').replace(/^./, (s) => s.toUpperCase());
                    let displayVal = val;
                    if (Array.isArray(val)) {
                      displayVal = val.length === 0
                        ? (key === 'vi_tri_not_ruoi' ? 'Không phát hiện nốt ruồi cố định'
                          : key === 'ti_vet_da_lieu_hoac_mun' ? 'Làn da bình thường, không có nốt mụn sậm màu'
                          : 'Không ghi nhận')
                        : val.join(', ');
                    } else if (typeof val === 'object' && val !== null) { displayVal = JSON.stringify(val); }
                    else if (!val) { displayVal = 'Không ghi nhận'; }
                    const isMole = key === 'vi_tri_not_ruoi', isAcne = key === 'ti_vet_da_lieu_hoac_mun';
                    return (
                      <div key={idx} className={`p-3.5 rounded-btn border space-y-1 ${
                        isMole ? 'bg-[#FFF9EE] border-[#D4AF37]/50' : isAcne ? 'bg-[#FAF2F0] border-[#E6C2BC]' : 'bg-[#FAF5EE] border-surface-border'
                      }`}>
                        <div className="flex items-center justify-between gap-1">
                          <span className={`text-[11px] font-mono font-bold uppercase tracking-wider block ${
                            isMole ? 'text-[#8B1C13]' : isAcne ? 'text-amber-800' : 'text-text-secondary'
                          }`}>{label}</span>
                          {isAcne && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-900 font-semibold">
                              Không tính nốt ruồi
                            </span>
                          )}
                        </div>
                        <div className="font-body text-sm font-semibold text-text-primary">{String(displayVal)}</div>
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
            <InterpretationTabs luanGiai={resultData.luan_giai} systemName="Nhân Tướng Học" />
          </div>
        )}
      </main>

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
