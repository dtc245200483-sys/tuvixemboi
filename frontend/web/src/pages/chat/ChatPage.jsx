import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { IconArrowLeft, IconSparkles } from '@tabler/icons-react';
import useChatStream from '../../hooks/useChatStream';
import ChatHistoryList from './ChatHistoryList';
import ChatInput from './ChatInput';
import QuotaBadge from '../../components/QuotaBadge';
import BiometricConsentModal from '../../components/BiometricConsentModal';

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
  } = useChatStream();

  // Biometric Consent state for face/palm image attachments
  const [showConsentModal, setShowConsentModal] = useState(false);
  const [pendingFile, setPendingFile] = useState(null);
  const [pendingFileFromConsent, setPendingFileFromConsent] = useState(null);

  const handleRequireConsent = (file) => {
    setPendingFile(file);
    setShowConsentModal(true);
  };

  const handleConsentSuccess = () => {
    setShowConsentModal(false);
    if (pendingFile) {
      setPendingFileFromConsent(pendingFile);
      setPendingFile(null);
    }
  };

  const handleConsentClose = () => {
    setShowConsentModal(false);
    setPendingFile(null);
  };

  return (
    <div className="h-[100dvh] flex flex-col bg-background text-text-primary overflow-hidden font-body">
      {/* Top Navigation Bar */}
      <header className="h-16 px-4 sm:px-6 bg-surface/95 backdrop-blur-md border-b border-surface-border flex items-center justify-between shadow-sm z-10 flex-shrink-0">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="p-2 -ml-2 rounded-xl text-text-secondary hover:text-primary hover:bg-[#FAF5EE] transition-all focus:outline-none"
            title="Quay về Trang chủ"
          >
            <IconArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-base sm:text-lg font-serif font-bold text-primary leading-tight flex items-center gap-1.5">
              <span>Đàm Đạo Huyền Học</span>
              <IconSparkles size={16} className="text-accent inline-block" />
            </h1>
            <p className="text-[11px] sm:text-xs text-text-secondary">
              Tử Vi • Bát Tự • Kinh Dịch • Nhân Tướng
            </p>
          </div>
        </div>

        {/* Quota Indicator */}
        <div className="flex items-center gap-2">
          <QuotaBadge />
        </div>
      </header>

      {/* Main Conversation Area */}
      <main className="flex-1 flex flex-col min-h-0 relative">
        <ChatHistoryList
          messages={messages}
          isSending={isSending}
          isLoadingHistory={isLoadingHistory}
          hasMore={hasMore}
          onLoadMore={() => loadHistory(false)}
          onRetry={retryLastMessage}
          onSelectSampleQuestion={(q) => sendMessage({ text: q })}
        />

        {/* Bottom Chat Input Form */}
        <ChatInput
          onSendMessage={sendMessage}
          isSending={isSending}
          quotaExceeded={quotaExceeded}
          onRequireConsent={handleRequireConsent}
          pendingFileFromConsent={pendingFileFromConsent}
          onClearPendingFile={() => setPendingFileFromConsent(null)}
        />
      </main>

      {/* Biometric Consent Modal */}
      <BiometricConsentModal
        isOpen={showConsentModal}
        onClose={handleConsentClose}
        onConsentSuccess={handleConsentSuccess}
      />
    </div>
  );
}
