import React, { useState, useRef, useEffect } from 'react';
import { IconSend, IconPaperclip, IconX, IconPhoto, IconAlertCircle } from '@tabler/icons-react';
import { visionService } from '../../services/api';

export default function ChatInput({
  onSendMessage,
  isSending,
  quotaExceeded,
  onRequireConsent,
  pendingFileFromConsent,
  onClearPendingFile,
}) {
  const [text, setText] = useState('');
  const [attachedImage, setAttachedImage] = useState(null);
  const [isProcessingImage, setIsProcessingImage] = useState(false);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  // Resize image via HTML5 canvas (<1280px, ~85% quality JPEG)
  const processImageFile = (file) => {
    setIsProcessingImage(true);
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        const maxDim = 1280;

        if (width > maxDim || height > maxDim) {
          if (width > height) {
            height = Math.round((height * maxDim) / width);
            width = maxDim;
          } else {
            width = Math.round((width * maxDim) / height);
            height = maxDim;
          }
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            if (!blob) {
              setIsProcessingImage(false);
              return;
            }
            const cleanName = file.name.replace(/\.[^/.]+$/, '') + '.jpg';
            const resizedFile = new File([blob], cleanName, { type: 'image/jpeg' });
            const previewUrl = URL.createObjectURL(blob);

            setAttachedImage({
              file: resizedFile,
              previewUrl,
              name: file.name,
            });
            setIsProcessingImage(false);
          },
          'image/jpeg',
          0.85
        );
      };
      img.onerror = () => setIsProcessingImage(false);
      img.src = e.target.result;
    };
    reader.onerror = () => setIsProcessingImage(false);
    reader.readAsDataURL(file);
  };

  // If user granted consent and parent passes pending file back
  useEffect(() => {
    if (pendingFileFromConsent) {
      processImageFile(pendingFileFromConsent);
      if (onClearPendingFile) {
        onClearPendingFile();
      }
    }
  }, [pendingFileFromConsent]);

  // Handle file selection from input
  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset file input value so same file can be picked again
    e.target.value = '';

    try {
      // Check biometric consent status
      const res = await visionService.getConsent();
      const consentGiven = res.data?.consent_given;

      if (!consentGiven) {
        // Show modal and store file in parent
        if (onRequireConsent) {
          onRequireConsent(file);
        }
        return;
      }

      // If consent already given, process image
      processImageFile(file);
    } catch (err) {
      // If error checking consent, fallback to requiring consent confirmation
      if (onRequireConsent) {
        onRequireConsent(file);
      }
    }
  };

  const handleRemoveImage = () => {
    if (attachedImage?.previewUrl) {
      URL.revokeObjectURL(attachedImage.previewUrl);
    }
    setAttachedImage(null);
  };

  // Handle auto-expanding textarea
  const handleTextChange = (e) => {
    setText(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  // Handle Enter to send, Shift+Enter for newline
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (isSending || quotaExceeded || isProcessingImage) return;
    if (!text.trim() && !attachedImage) return;

    onSendMessage({
      text: text.trim(),
      attachedImage,
    });

    setText('');
    setAttachedImage(null);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const isSubmitDisabled =
    isSending ||
    quotaExceeded ||
    isProcessingImage ||
    (!text.trim() && !attachedImage);

  return (
    <div className="w-full bg-surface/95 backdrop-blur-md border-t border-surface-border p-3 sm:p-4 shadow-sm">
      <div className="max-w-4xl mx-auto space-y-2">
        {/* Quota Exceeded Warning */}
        {quotaExceeded && (
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-[#FAF0EE] border border-[#E6C2BC] text-primary text-xs font-body">
            <IconAlertCircle size={16} className="flex-shrink-0" />
            <span>
              Bạn đã dùng hết hạn mức vấn đáp miễn phí trong ngày hôm nay. Hạn mức sẽ tự động được làm mới vào ngày mai.
            </span>
          </div>
        )}

        {/* Attached Image Preview */}
        {attachedImage && (
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#FAF5EE] border border-surface-border text-xs text-text-primary">
            <div className="w-8 h-8 rounded-lg overflow-hidden border border-accent/40 bg-surface flex items-center justify-center flex-shrink-0">
              <img
                src={attachedImage.previewUrl}
                alt="Đính kèm"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="max-w-[180px] sm:max-w-[280px] truncate font-medium">
              {attachedImage.name}
            </div>
            <button
              type="button"
              onClick={handleRemoveImage}
              disabled={isSending}
              className="p-1 rounded-full text-text-secondary hover:text-primary transition-colors focus:outline-none"
              title="Xóa ảnh"
            >
              <IconX size={14} />
            </button>
          </div>
        )}

        {/* Main Input Form */}
        <form onSubmit={handleSubmit} className="flex items-end gap-2">
          {/* Paperclip Button */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isSending || quotaExceeded || isProcessingImage}
            title="Đính kèm ảnh diện mạo hoặc bàn tay để xem tướng"
            className="p-2.5 rounded-xl border border-surface-border bg-surface text-text-secondary hover:text-accent hover:border-accent/60 transition-all focus:outline-none disabled:opacity-50 flex-shrink-0"
          >
            {isProcessingImage ? (
              <div className="w-5 h-5 border-2 border-accent border-t-transparent rounded-full animate-spin" />
            ) : (
              <IconPaperclip size={20} />
            )}
          </button>

          {/* Auto-expanding Textarea */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              rows={1}
              value={text}
              onChange={handleTextChange}
              onKeyDown={handleKeyDown}
              disabled={isSending || quotaExceeded}
              placeholder={
                quotaExceeded
                  ? 'Hạn mức hôm nay đã hết...'
                  : 'Hỏi về vận mệnh, sự nghiệp, tình duyên, lá số, hoặc gieo quẻ...'
              }
              className="w-full resize-none rounded-xl border border-surface-border bg-surface px-3.5 py-2.5 text-sm font-body text-text-primary placeholder:text-text-secondary/60 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-all disabled:bg-[#FAF5EE] disabled:opacity-60 max-h-[120px] overflow-y-auto"
            />
          </div>

          {/* Send Button */}
          <button
            type="submit"
            disabled={isSubmitDisabled}
            className="p-2.5 rounded-xl bg-primary hover:bg-[#552218] text-text-on-primary transition-all focus:outline-none disabled:opacity-40 disabled:hover:bg-primary shadow-sm flex-shrink-0"
            title="Gửi câu hỏi (Enter)"
          >
            {isSending ? (
              <div className="w-5 h-5 border-2 border-text-on-primary border-t-transparent rounded-full animate-spin" />
            ) : (
              <IconSend size={20} />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
