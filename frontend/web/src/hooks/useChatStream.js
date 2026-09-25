import { useState, useEffect, useCallback, useRef } from 'react';
import { chatService, visionService } from '../services/api';
import { notifyQuotaUpdated } from '../components/QuotaBadge';

export default function useChatStream() {
  const [messages, setMessages] = useState([]);
  const [isSending, setIsSending] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState(null);
  const [quotaExceeded, setQuotaExceeded] = useState(false);
  const [lastFailedMessage, setLastFailedMessage] = useState(null);

  // ---- Session state ----
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);

  const isInitialLoaded = useRef(false);

  // ==============================================================
  // Load danh sách sessions
  // ==============================================================
  const loadSessions = useCallback(async () => {
    try {
      setIsLoadingSessions(true);
      const res = await chatService.getSessions();
      const list = res.data?.du_lieu?.danh_sach || [];
      setSessions(list);
    } catch (err) {
      console.error('Lỗi khi tải danh sách sessions:', err);
    } finally {
      setIsLoadingSessions(false);
    }
  }, []);

  // ==============================================================
  // Load tin nhắn của 1 session cụ thể (có phân trang)
  // ==============================================================
  const loadSessionMessages = useCallback(async (sessionId, reset = false) => {
    if (!sessionId) return;
    try {
      setIsLoadingHistory(true);
      const targetPage = reset ? 1 : page;
      const res = await chatService.getSessionMessages(sessionId, {
        page: targetPage,
        page_size: 20,
      });
      const duLieu = res.data?.du_lieu;
      if (!duLieu) { setHasMore(false); return; }

      const danhSach = duLieu.danh_sach || [];
      const total = duLieu.tong_so || 0;
      const sortedItems = [...danhSach].reverse();

      const convertedMessages = [];
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

      const loaded = targetPage * (duLieu.kich_thuoc_trang || 20);
      setHasMore(loaded < total);
    } catch (err) {
      console.error('Lỗi khi tải tin nhắn session:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  }, [page]);

  // ==============================================================
  // Tải lịch sử chung (legacy - dùng cho chat không có session)
  // ==============================================================
  const loadHistory = useCallback(async (reset = false) => {
    if (activeSessionId) {
      await loadSessionMessages(activeSessionId, reset);
      return;
    }
    // Nếu không có session đang chọn thì không tải gì
    setMessages([]);
    setHasMore(false);
  }, [activeSessionId, loadSessionMessages]);

  // Load initial sessions on mount
  useEffect(() => {
    if (!isInitialLoaded.current) {
      isInitialLoaded.current = true;
      loadSessions();
    }
  }, [loadSessions]);

  // ==============================================================
  // Chọn 1 session - tải tin nhắn của session đó
  // ==============================================================
  const selectSession = useCallback(async (sessionId) => {
    setActiveSessionId(sessionId);
    setMessages([]);
    setPage(1);
    setHasMore(false);
    setError(null);
    setQuotaExceeded(false);
    if (sessionId) {
      try {
        setIsLoadingHistory(true);
        const res = await chatService.getSessionMessages(sessionId, { page: 1, page_size: 20 });
        const duLieu = res.data?.du_lieu;
        if (!duLieu) return;

        const danhSach = duLieu.danh_sach || [];
        const total = duLieu.tong_so || 0;
        const sortedItems = [...danhSach].reverse();

        const convertedMessages = [];
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
        setMessages(convertedMessages);
        setPage(2);
        setHasMore(20 < total);
      } catch (err) {
        console.error('Lỗi khi chọn session:', err);
      } finally {
        setIsLoadingHistory(false);
      }
    }
  }, []);

  // ==============================================================
  // Bắt đầu cuộc trò chuyện mới
  // ==============================================================
  const startNewSession = useCallback(() => {
    setActiveSessionId(null);
    setMessages([]);
    setPage(1);
    setHasMore(false);
    setError(null);
    setQuotaExceeded(false);
    setLastFailedMessage(null);
  }, []);

  // ==============================================================
  // Xóa 1 session
  // ==============================================================
  const deleteSession = useCallback(async (sessionId) => {
    try {
      await chatService.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        startNewSession();
      }
    } catch (err) {
      console.error('Lỗi khi xóa session:', err);
    }
  }, [activeSessionId, startNewSession]);

  // ==============================================================
  // Gửi tin nhắn
  // ==============================================================
  const sendMessage = async ({ text, attachedImage = null, referenceId = null, heThongUuTien = null, birthProfileId = null }) => {
    if (!text?.trim() && !attachedImage) return;

    const trimmedText = text?.trim() || 'Xin mời luận giải giúp tôi hình ảnh đính kèm.';
    const tempId = `msg-usr-${Date.now()}`;

    // Kiểm tra offline
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
      setLastFailedMessage({ tempId, text: trimmedText, attachedImage, referenceId, heThongUuTien });
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
      // 1. Upload ảnh nếu cần
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

      // 2. Gọi chat API với session_id và birth_profile_id
      const payload = {
        cau_hoi: trimmedText,
        reference_id: effectiveReferenceId || null,
        he_thong: heThongUuTien || (effectiveReferenceId ? 'nhan_tuong' : null),
        session_id: activeSessionId || null,
        birth_profile_id: birthProfileId || null,
      };

      const res = await chatService.sendMessage(payload);
      const resData = res.data?.du_lieu || {};

      // 3. Cập nhật activeSessionId từ response (khi tạo session mới tự động)
      if (resData.session_id && !activeSessionId) {
        setActiveSessionId(resData.session_id);
        // Tải lại danh sách sessions
        await loadSessions();
      } else if (resData.session_id && activeSessionId !== resData.session_id) {
        setActiveSessionId(resData.session_id);
        await loadSessions();
      }

      // 4. Mark user message sent
      setMessages((prev) =>
        prev.map((m) => (m.id === tempId ? { ...m, status: 'sent' } : m))
      );

      // 5. Tạo AI message
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
          birthProfileId,
        });
      }
    } finally {
      setIsSending(false);
    }
  };

  // Retry gửi lại tin nhắn lỗi
  const retryLastMessage = async () => {
    if (!lastFailedMessage) return;
    const { tempId, text, attachedImage, referenceId, heThongUuTien, birthProfileId } = lastFailedMessage;
    setMessages((prev) => prev.filter((m) => m.id !== tempId));
    setLastFailedMessage(null);
    setError(null);
    await sendMessage({ text, attachedImage, referenceId, heThongUuTien, birthProfileId });
  };

  return {
    // Messages
    messages,
    isSending,
    isLoadingHistory,
    hasMore,
    error,
    quotaExceeded,
    sendMessage,
    loadHistory,
    retryLastMessage,
    // Sessions
    sessions,
    activeSessionId,
    isLoadingSessions,
    loadSessions,
    selectSession,
    startNewSession,
    deleteSession,
  };
}
