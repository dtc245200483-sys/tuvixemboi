import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  IconArrowLeft,
  IconSparkles,
  IconPlus,
  IconTrash,
  IconMessage,
  IconChevronDown,
  IconMenu2,
  IconX,
  IconUser,
} from '@tabler/icons-react';
import useChatStream from '../../hooks/useChatStream';
import { birthProfileService } from '../../services/api';
import ChatHistoryList from './ChatHistoryList';
import ChatInput from './ChatInput';
import QuotaBadge from '../../components/QuotaBadge';
import BiometricConsentModal from '../../components/BiometricConsentModal';

/* ------------------------------------------------------------------
   Helpers
------------------------------------------------------------------ */
function formatSessionDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const now = new Date();
  const diffDays = Math.floor((now - d) / 86400000);
  if (diffDays === 0) return 'Hôm nay';
  if (diffDays === 1) return 'Hôm qua';
  if (diffDays < 7) return `${diffDays} ngày trước`;
  return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
}

/* ------------------------------------------------------------------
   Sidebar
------------------------------------------------------------------ */
function SessionSidebar({
  sessions,
  activeSessionId,
  isLoadingSessions,
  onNewSession,
  onSelectSession,
  onDeleteSession,
  defaultProfile,
  onClose,
}) {
  const [confirmDelete, setConfirmDelete] = useState(null);

  const handleDeleteClick = (e, sessionId) => {
    e.stopPropagation();
    setConfirmDelete(sessionId);
  };

  const handleConfirmDelete = (e, sessionId) => {
    e.stopPropagation();
    onDeleteSession(sessionId);
    setConfirmDelete(null);
  };

  return (
    <aside
      className="flex flex-col h-full border-r"
      style={{
        background: 'var(--color-surface)',
        borderColor: 'var(--color-surface-border)',
      }}
    >
      {/* Header */}
      <div className="px-4 pt-5 pb-3 flex items-center justify-between">
        <span
          className="text-[11px] font-semibold uppercase tracking-widest font-body"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          Trò Chuyện AI
        </span>
        {/* Close – mobile only */}
        <button
          type="button"
          onClick={onClose}
          className="lg:hidden p-1.5 rounded-lg transition-colors"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          <IconX size={16} />
        </button>
      </div>

      {/* New chat button */}
      <div className="px-3 pb-3">
        <button
          type="button"
          onClick={onNewSession}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-[var(--radius-btn)]
            text-sm font-medium font-body transition-all duration-150 active:scale-[0.98] shadow-sm"
          style={{
            background: 'var(--color-primary)',
            color: 'var(--color-text-on-primary)',
          }}
        >
          <IconPlus size={16} />
          <span>Cuộc trò chuyện mới</span>
        </button>
      </div>

      {/* Sessions list */}
      <div className="flex-1 overflow-y-auto px-2 space-y-0.5 pb-2">
        {isLoadingSessions && sessions.length === 0 && (
          <p
            className="text-center py-8 text-xs font-body"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            Đang tải...
          </p>
        )}
        {!isLoadingSessions && sessions.length === 0 && (
          <div className="text-center py-10 flex flex-col items-center gap-2">
            <IconMessage size={28} style={{ color: 'var(--color-surface-border)' }} />
            <p className="text-xs font-body" style={{ color: 'var(--color-text-secondary)' }}>
              Chưa có cuộc trò chuyện nào
            </p>
          </div>
        )}
        {sessions.map((sess) => {
          const isActive = sess.id === activeSessionId;
          const isConfirming = confirmDelete === sess.id;
          return (
            <div
              key={sess.id}
              onClick={() => !isConfirming && onSelectSession(sess.id)}
              className="group relative flex items-start gap-2 px-3 py-2.5 rounded-[var(--radius-btn)] cursor-pointer transition-all duration-150"
              style={{
                background: isActive ? 'rgba(107,43,31,0.08)' : 'transparent',
                color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
              }}
              onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.background = 'rgba(107,43,31,0.05)'; }}
              onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.background = 'transparent'; }}
            >
              <IconMessage size={14} className="mt-0.5 flex-shrink-0 opacity-60" />
              <div className="flex-1 min-w-0">
                <p
                  className="text-xs font-medium truncate leading-tight font-body"
                  style={{ color: isActive ? 'var(--color-primary)' : 'var(--color-text-primary)' }}
                >
                  {sess.tieu_de || 'Cuộc trò chuyện'}
                </p>
                <p className="text-[10px] mt-0.5 font-body" style={{ color: 'var(--color-text-secondary)' }}>
                  {formatSessionDate(sess.updated_at || sess.created_at)}
                </p>
              </div>

              {!isConfirming ? (
                <button
                  type="button"
                  onClick={(e) => handleDeleteClick(e, sess.id)}
                  className="flex-shrink-0 p-1 rounded-lg opacity-0 group-hover:opacity-100 transition-all duration-150"
                  style={{ color: 'var(--color-text-secondary)' }}
                  title="Xóa cuộc trò chuyện"
                  onMouseEnter={(e) => { e.currentTarget.style.color = '#c0392b'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--color-text-secondary)'; }}
                >
                  <IconTrash size={12} />
                </button>
              ) : (
                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                  <button
                    type="button"
                    onClick={(e) => handleConfirmDelete(e, sess.id)}
                    className="text-[10px] px-1.5 py-0.5 rounded font-body font-medium"
                    style={{ background: 'var(--color-primary)', color: 'var(--color-text-on-primary)' }}
                  >
                    Xóa
                  </button>
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); setConfirmDelete(null); }}
                    className="text-[10px] px-1.5 py-0.5 rounded font-body"
                    style={{ background: 'var(--color-surface-border)', color: 'var(--color-text-secondary)' }}
                  >
                    Huỷ
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer – active destiny profile */}
      {defaultProfile && (
        <div className="px-3 py-3 border-t" style={{ borderColor: 'var(--color-surface-border)' }}>
          <div
            className="flex items-center gap-2 px-2 py-2 rounded-[var(--radius-btn)]"
            style={{ background: 'rgba(107,43,31,0.06)' }}
          >
            <div
              className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ background: 'rgba(107,43,31,0.15)' }}
            >
              <IconUser size={12} style={{ color: 'var(--color-primary)' }} />
            </div>
            <div className="min-w-0">
              <p className="text-[10px] leading-none font-body" style={{ color: 'var(--color-text-secondary)' }}>
                Mệnh chủ đang chọn
              </p>
              <p
                className="text-xs font-semibold truncate mt-0.5 font-body"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {defaultProfile.ho_ten || 'Chưa đặt tên'}
              </p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}

/* ------------------------------------------------------------------
   Floating scroll-to-bottom button
------------------------------------------------------------------ */
function ScrollToBottomButton({ chatRef }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = chatRef?.current;
    if (!el) return;
    const handleScroll = () => {
      setVisible(el.scrollHeight - el.scrollTop - el.clientHeight > 120);
    };
    el.addEventListener('scroll', handleScroll, { passive: true });
    return () => el.removeEventListener('scroll', handleScroll);
  }, [chatRef]);

  if (!visible) return null;

  return (
    <button
      type="button"
      onClick={() => chatRef?.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' })}
      className="absolute bottom-4 right-4 z-20 w-9 h-9 rounded-full shadow-md
        flex items-center justify-center transition-all duration-200 active:scale-95"
      style={{
        background: 'var(--color-primary)',
        color: 'var(--color-text-on-primary)',
        boxShadow: 'var(--shadow-dropdown)',
      }}
      title="Cuộn xuống tin nhắn mới nhất"
    >
      <IconChevronDown size={18} />
    </button>
  );
}

/* ------------------------------------------------------------------
   ChatPage (main)
------------------------------------------------------------------ */
export default function ChatPage() {
  const navigate = useNavigate();
  const {
    messages,
    isSending,
    isLoadingHistory,
    hasMore,
    quotaExceeded,
    sendMessage,
    loadHistory,
    retryLastMessage,
    sessions,
    activeSessionId,
    isLoadingSessions,
    selectSession,
    startNewSession,
    deleteSession,
  } = useChatStream();

  const [defaultProfile, setDefaultProfile] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chatScrollRef = useRef(null);

  useEffect(() => {
    birthProfileService.getAll().then((res) => {
      const list = res.data?.du_lieu || [];
      const def = list.find((p) => p.is_default) || list[0] || null;
      setDefaultProfile(def);
    }).catch(() => {});
  }, []);

  // Biometric Consent state
  const [showConsentModal, setShowConsentModal] = useState(false);
  const [pendingFile, setPendingFile] = useState(null);
  const [pendingFileFromConsent, setPendingFileFromConsent] = useState(null);

  const handleRequireConsent = (file) => { setPendingFile(file); setShowConsentModal(true); };
  const handleConsentSuccess = () => {
    setShowConsentModal(false);
    if (pendingFile) { setPendingFileFromConsent(pendingFile); setPendingFile(null); }
  };
  const handleConsentClose = () => { setShowConsentModal(false); setPendingFile(null); };

  const handleNewSession = () => { startNewSession(); setSidebarOpen(false); };
  const handleSelectSession = (id) => { selectSession(id); setSidebarOpen(false); };

  return (
    <div
      className="h-[100dvh] flex overflow-hidden font-body"
      style={{ background: 'var(--color-background)', color: 'var(--color-text-primary)' }}
    >
      {/* ============================================================
          Sidebar
      ============================================================ */}
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <div
        className={`
          fixed lg:relative z-40 lg:z-auto
          w-64 h-full flex-shrink-0
          transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <SessionSidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          isLoadingSessions={isLoadingSessions}
          onNewSession={handleNewSession}
          onSelectSession={handleSelectSession}
          onDeleteSession={deleteSession}
          defaultProfile={defaultProfile}
          onClose={() => setSidebarOpen(false)}
        />
      </div>

      {/* ============================================================
          Main chat area
      ============================================================ */}
      <div className="flex-1 flex flex-col min-w-0 min-h-0">
        {/* Top Navigation Bar */}
        <header
          className="h-14 px-3 sm:px-4 flex items-center justify-between z-10 flex-shrink-0 border-b"
          style={{
            background: 'rgba(245,237,224,0.96)',
            backdropFilter: 'blur(12px)',
            borderColor: 'var(--color-surface-border)',
            boxShadow: 'var(--shadow-subtle)',
          }}
        >
          <div className="flex items-center gap-1.5">
            {/* Mobile hamburger */}
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-[var(--radius-btn)] transition-colors"
              style={{ color: 'var(--color-text-secondary)' }}
              title="Mở danh sách cuộc trò chuyện"
            >
              <IconMenu2 size={20} />
            </button>
            {/* Back button */}
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="p-2 rounded-[var(--radius-btn)] transition-colors"
              style={{ color: 'var(--color-text-secondary)' }}
              title="Quay về Trang chủ"
            >
              <IconArrowLeft size={18} />
            </button>
            <div>
              <h1
                className="text-sm sm:text-base font-bold leading-tight font-body flex items-center gap-1.5"
                style={{ color: 'var(--color-primary)' }}
              >
                Đàm Đạo Huyền Học
                <IconSparkles size={14} style={{ color: 'var(--color-accent)' }} className="inline-block flex-shrink-0" />
              </h1>
              <p className="text-[10px] sm:text-xs font-body" style={{ color: 'var(--color-text-secondary)' }}>
                Tử Vi • Bát Tự • Kinh Dịch • Nhân Tướng
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <QuotaBadge />
          </div>
        </header>

        {/* Load-more banner */}
        {hasMore && (
          <button
            type="button"
            onClick={() => loadHistory(false)}
            className="w-full py-1.5 text-center text-[11px] font-body transition-colors border-b"
            style={{
              background: 'var(--color-surface)',
              color: 'var(--color-text-secondary)',
              borderColor: 'var(--color-surface-border)',
            }}
          >
            ↑ Cuộn lên hoặc bấm để xem thêm tin nhắn cũ
          </button>
        )}

        {/* Main Conversation Area */}
        <main className="flex-1 flex flex-col min-h-0 relative">
          <div ref={chatScrollRef} className="flex-1 overflow-y-auto">
            <ChatHistoryList
              messages={messages}
              isSending={isSending}
              isLoadingHistory={isLoadingHistory}
              hasMore={hasMore}
              onLoadMore={() => loadHistory(false)}
              onRetry={retryLastMessage}
              onSelectSampleQuestion={(q) => sendMessage({ text: q, birthProfileId: defaultProfile?.id || null })}
            />
          </div>

          {/* Floating scroll-to-bottom */}
          <ScrollToBottomButton chatRef={chatScrollRef} />

          {/* Bottom Chat Input */}
          <ChatInput
            onSendMessage={(params) => sendMessage({ ...params, birthProfileId: defaultProfile?.id || null })}
            isSending={isSending}
            quotaExceeded={quotaExceeded}
            onRequireConsent={handleRequireConsent}
            pendingFileFromConsent={pendingFileFromConsent}
            onClearPendingFile={() => setPendingFileFromConsent(null)}
          />
        </main>
      </div>

      {/* Biometric Consent Modal */}
      <BiometricConsentModal
        isOpen={showConsentModal}
        onClose={handleConsentClose}
        onConsentSuccess={handleConsentSuccess}
      />
    </div>
  );
}
