import React, { useState, useEffect } from 'react';
import { IconWifiOff, IconWifi, IconCheck } from '@tabler/icons-react';

export default function OfflineIndicator() {
  const [isOnline, setIsOnline] = useState(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );
  const [showReconnected, setShowReconnected] = useState(false);

  useEffect(() => {
    let reconnectTimer = null;

    const handleOnline = () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      setIsOnline(true);
      setShowReconnected(true);
      reconnectTimer = setTimeout(() => {
        setShowReconnected(false);
      }, 2500);
    };

    const handleOffline = () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      setIsOnline(false);
      setShowReconnected(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // When fully online and not showing temporary reconnected message, render nothing
  if (isOnline && !showReconnected) {
    return null;
  }

  return (
    <aside
      aria-live="polite"
      aria-atomic="true"
      className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 transition-all animate-fade-in font-body"
    >
      {!isOnline ? (
        <div
          role="status"
          className="flex items-center gap-2.5 px-4 py-2 rounded-full bg-surface border border-accent/80 text-text-primary text-xs shadow-elevated"
        >
          <IconWifiOff size={16} className="text-accent flex-shrink-0 animate-pulse" />
          <span className="font-medium">
            Ngoại tuyến — Đang sử dụng dữ liệu đã lưu trong máy
          </span>
        </div>
      ) : (
        <div
          role="status"
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#FAF5EE] border border-surface-border text-primary text-xs shadow-subtle"
        >
          <IconWifi size={16} className="text-accent flex-shrink-0" />
          <span className="font-medium">Đã khôi phục kết nối mạng</span>
        </div>
      )}
    </aside>
  );
}
