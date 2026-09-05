import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './router.jsx';
import OfflineIndicator from './components/OfflineIndicator.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
      <OfflineIndicator />
    </BrowserRouter>
  );
}
