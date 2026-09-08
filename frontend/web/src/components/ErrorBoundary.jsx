import React from 'react';
import { IconAlertTriangle, IconRefresh, IconArrowLeft } from '@tabler/icons-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  handleReload = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#FAF6EE] flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-2xl p-6 shadow-xl border border-red-100 text-center space-y-4">
            <div className="w-14 h-14 mx-auto rounded-full bg-red-50 flex items-center justify-center text-red-600">
              <IconAlertTriangle size={32} />
            </div>
            <h2 className="text-xl font-bold text-gray-800 font-heading">Đã xảy ra lỗi giao diện</h2>
            <p className="text-xs text-gray-600 font-body leading-relaxed">
              Hệ thống đã ghi nhận sự cố gián đoạn tạm thời. Quý bạn chỉ cần làm mới lại trang hoặc quay về trang chủ để tiếp tục.
            </p>
            <div className="pt-2 flex items-center justify-center gap-3">
              <button
                onClick={this.handleReload}
                className="px-4 py-2 bg-[#6B2D1F] hover:bg-[#552218] text-white rounded-lg text-xs font-bold flex items-center gap-1.5 transition-colors shadow-sm"
              >
                <IconRefresh size={16} /> Làm mới trang
              </button>
              <a
                href="/dashboard"
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-colors"
              >
                <IconArrowLeft size={16} /> Về Trang Chủ
              </a>
            </div>

            {this.state.error && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200 text-left overflow-auto max-h-48 text-[11px] font-mono text-red-600">
                <div className="font-bold mb-1">Chi tiết lỗi (Debug):</div>
                <div>{this.state.error.toString()}</div>
                {this.state.error.stack && (
                  <pre className="text-[10px] text-gray-500 mt-2 whitespace-pre-wrap">{this.state.error.stack}</pre>
                )}
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
