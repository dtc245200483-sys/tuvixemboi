import { useState, useEffect, useCallback, useRef } from 'react';
import { chatService, visionService } from '../services/api';
import { notifyQuotaUpdated } from '../components/QuotaBadge';

export default function useChatStream() {
  const [messages, setMessages] = useState([]);
  const [isSending, setIsSending] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState(null);
  const [quotaExceeded, setQuotaExceeded] = useState(false);
  const [lastFailedMessage, setLastFailedMessage] = useState(null);

  const isInitialLoaded = useRef(false);

  // Load chat history from backend
  const loadHistory = useCallback(async (reset = false) => {
    try {
      setIsLoadingHistory(true);
      const targetPage = reset ? 1 : page;
      const res = await chatService.getHistory({
        page: targetPage,
        page_size: 15,
      });

      const duLieu = res.data?.du_lieu;
      if (!duLieu) {
        setHasMore(false);
        return;
      }

      const danhSach = duLieu.danh_sach || [];
      const total = duLieu.tong_so || 0;

      // Each item in history is a pair: cau_hoi (user) and tra_loi (ai)
      // Since history is returned descending (newest first), reverse each batch to be chronological
      const convertedMessages = [];
      const sortedItems = [...danhSach].reverse();

      for (const item of sortedItems) {
        if (item.cau_hoi) {
          convertedMessages.push({
            id: `${item.id}-user`,
            sender: 'user',
            noi_dung: item.cau_hoi,
            created_at: item.created_at,
            reference_id: item.reference_id,
            status: 'sent',
          });
        }
        if (item.tra_loi) {
          convertedMessages.push({
            id: `${item.id}-ai`,
            sender: 'ai',
            noi_dung: item.tra_loi,
            he_thong: item.he_thong,
            created_at: item.created_at,
            status: 'sent',
          });
        }
      }

      if (reset) {
        setMessages(convertedMessages);
        setPage(2);
      } else {
        setMessages((prev) => [...convertedMessages, ...prev]);
        setPage((prev) => prev + 1);
      }

      const currentLoadedCount = (targetPage) * (duLieu.kich_thuoc_trang || 15);
      setHasMore(currentLoadedCount < total);
    } catch (err) {
      console.error('Lỗi khi tải lịch sử chat:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  }, [page]);

  // Load initial page on mount
  useEffect(() => {
    if (!isInitialLoaded.current) {
      isInitialLoaded.current = true;
      loadHistory(true);
    }
  }, [loadHistory]);

  // Send a message
  const sendMessage = async ({ text, attachedImage = null, referenceId = null, heThongUuTien = null }) => {
    if (!text?.trim() && !attachedImage) return;

    const trimmedText = text?.trim() || 'Xin mời luận giải giúp tôi hình ảnh đính kèm.';
    const tempId = `msg-usr-${Date.now()}`;

    // Kiểm tra kết nối mạng: Chặn gửi khi ngoại tuyến và thông báo rõ ràng
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      const userMsg = {
        id: tempId,
        sender: 'user',
        noi_dung: trimmedText,
        image_url: attachedImage?.previewUrl || null,
        created_at: new Date().toISOString(),
        status: 'error',
      };
      const offlineNotice = {
        id: `msg-offline-${Date.now()}`,
        sender: 'ai',
        noi_dung:
          'Thiết bị của bạn đang ngoại tuyến. Tính năng đàm đạo cùng Trí Tuệ Nhân Tạo yêu cầu kết nối mạng Internet để gửi và nhận luận giải. Vui lòng kết nối lại mạng để tiếp tục.',
        he_thong: 'system',
        created_at: new Date().toISOString(),
        status: 'sent',
      };
      setMessages((prev) => [...prev, userMsg, offlineNotice]);
      setError('Bạn đang ngoại tuyến. Cần kết nối mạng để gửi tin nhắn chat.');
      setLastFailedMessage({
        tempId,
        text: trimmedText,
        attachedImage,
        referenceId,
        heThongUuTien,
      });
      return;
    }

    const userMsg = {
      id: tempId,
      sender: 'user',
      noi_dung: trimmedText,
      image_url: attachedImage?.previewUrl || null,
      created_at: new Date().toISOString(),
      status: 'sending',
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsSending(true);
    setError(null);

    let effectiveReferenceId = referenceId;

    try {
      // 1. If an image file is attached without referenceId, upload it first
      if (attachedImage?.file && !effectiveReferenceId) {
        const formData = new FormData();
        formData.append('file', attachedImage.file);
        try {
          const uploadRes = await visionService.uploadMat(formData);
          effectiveReferenceId = uploadRes.data?.id || uploadRes.data?.du_lieu?.id;
        } catch (uploadErr) {
          throw new Error(
            uploadErr.response?.data?.detail ||
            uploadErr.response?.data?.loi ||
            'Không thể tải ảnh lên. Vui lòng kiểm tra lại.'
          );
        }
      }

      // 2. Call chat API
      const payload = {
        cau_hoi: trimmedText,
        reference_id: effectiveReferenceId || null,
        he_thong: heThongUuTien || (effectiveReferenceId ? 'nhan_tuong' : null),
      };

      const res = await chatService.sendMessage(payload);
      const resData = res.data?.du_lieu || {};

      // Mark user message as sent
      setMessages((prev) =>
        prev.map((m) => (m.id === tempId ? { ...m, status: 'sent' } : m))
      );

      // Create AI message
      const chiTiet = resData.chi_tiet || {};
      const aiMsg = {
        id: `msg-ai-${Date.now()}`,
        sender: 'ai',
        noi_dung: resData.tra_loi || 'Hệ thống đã ghi nhận câu hỏi của bạn.',
        he_thong: resData.he_thong,
        can_hoi_lai: Boolean(chiTiet.can_hoi_lai),
        chua_co_du_lieu: Boolean(chiTiet.chua_co_du_lieu),
        goi_y: chiTiet.goi_y_chuyen_muc || [],
        created_at: new Date().toISOString(),
        status: 'sent',
      };

      setMessages((prev) => [...prev, aiMsg]);
      setLastFailedMessage(null);
      notifyQuotaUpdated();
    } catch (err) {
      console.error('Lỗi khi gửi tin nhắn chat:', err);

      const status = err.response?.status;
      const errorMsg =
        err.response?.data?.loi ||
        err.response?.data?.detail ||
        err.message ||
        'Không thể gửi tin nhắn. Vui lòng kiểm tra kết nối.';

      if (status === 429) {
        setQuotaExceeded(true);
        // Mark user message sent and add in-chat friendly quota message
        setMessages((prev) =>
          prev.map((m) => (m.id === tempId ? { ...m, status: 'sent' } : m))
        );
        const quotaNotice = {
          id: `msg-quota-${Date.now()}`,
          sender: 'ai',
          noi_dung:
            'Bạn đã sử dụng hết hạn mức câu hỏi miễn phí trong ngày hôm nay. Hạn mức sẽ tự động được làm mới vào ngày mai.',
          he_thong: 'system',
          is_quota_notice: true,
          created_at: new Date().toISOString(),
          status: 'sent',
        };
        setMessages((prev) => [...prev, quotaNotice]);
        notifyQuotaUpdated();
      } else {
        // Mark user message as error
        setMessages((prev) =>
          prev.map((m) => (m.id === tempId ? { ...m, status: 'error' } : m))
        );
        setError(errorMsg);
        setLastFailedMessage({
          tempId,
          text: trimmedText,
          attachedImage,
          referenceId: effectiveReferenceId,
          heThongUuTien,
        });
      }
    } finally {
      setIsSending(false);
    }
  };

  // Retry sending last failed message
  const retryLastMessage = async () => {
    if (!lastFailedMessage) return;
    const { tempId, text, attachedImage, referenceId, heThongUuTien } = lastFailedMessage;

    // Remove failed user message before resending
    setMessages((prev) => prev.filter((m) => m.id !== tempId));
    setLastFailedMessage(null);
    setError(null);

    await sendMessage({ text, attachedImage, referenceId, heThongUuTien });
  };

  return {
    messages,
    isSending,
    isLoadingHistory,
    hasMore,
    error,
    quotaExceeded,
    sendMessage,
    loadHistory,
    retryLastMessage,
  };
}
