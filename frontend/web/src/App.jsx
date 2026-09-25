import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './router.jsx';
import OfflineIndicator from './components/OfflineIndicator.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import MobileBottomNav from './components/MobileBottomNav.jsx';

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <div className="min-h-screen pb-16 md:pb-0">
          <AppRoutes />
          <MobileBottomNav />
          <OfflineIndicator />
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

