import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './router.jsx';
import OfflineIndicator from './components/OfflineIndicator.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AppRoutes />
        <OfflineIndicator />
      </BrowserRouter>
    </ErrorBoundary>
  );
}

