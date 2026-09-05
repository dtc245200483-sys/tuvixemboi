# -*- coding: utf-8 -*-
"""
KHAI TÂM HUYỀN HỌC - TỬ VI & XEM BÓI AI PLATFORM
Script Tự Động Khởi Chạy Toàn Bộ Ứng Dụng (Backend + Frontend + Mở Trình Duyệt Web)

Chỉ cần bấm đúp hoặc chạy file này:
1. Tự động kiểm tra và khởi động Backend API (FastAPI) trên cổng 8000
2. Tự động kiểm tra và khởi động Frontend Web (Vite React) trên cổng 5180
3. Tự động mở trình duyệt web mặc định vào ứng dụng: http://localhost:5180
4. Giữ cửa sổ chạy và tự động dọn dẹp tiến trình khi nhấn Ctrl + C
"""

import os
import sys
import time
import socket
import urllib.request
import webbrowser
import subprocess
import atexit
import signal
import shutil

# Cấu hình UTF-8 và line buffering cho console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)

# Xác định đường dẫn thư mục gốc dự án
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Thư mục gốc tuvixemboi (nếu script nằm trong tuvixemboi/run thì lùi 1 cấp)
if os.path.basename(CURRENT_DIR).lower() == "run":
    ROOT_DIR = os.path.dirname(CURRENT_DIR)
else:
    ROOT_DIR = CURRENT_DIR

BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend", "web")

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5180"
BACKEND_CHECK_URL = "http://127.0.0.1:8000/docs"
FRONTEND_CHECK_URL = "http://127.0.0.1:5180"

backend_process = None
frontend_process = None


def is_port_in_use(port: int) -> bool:
    """Kiểm tra xem cổng TCP đã có tiến trình nào lắng nghe chưa"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_for_port(port: int, timeout: int = 10, service_name: str = "Service", proc=None) -> bool:
    """Kiểm tra cổng dịch vụ đã sẵn sàng và kết nối thành công"""
    print(f"[*] Đang kết nối tới {service_name} (cổng {port})...", end="", flush=True)
    start_time = time.time()
    while time.time() - start_time < timeout:
        if proc and proc.poll() is not None:
            print(f" [LỖI: Tiến trình đã dừng với mã {proc.poll()}]", flush=True)
            return False
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.8):
                print(" [SẴN SÀNG]", flush=True)
                return True
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(0.5)
    print(" [TIẾP TỤC]", flush=True)
    return False


def kill_process_tree(proc):
    """Dọn dẹp tiến trình con trên Windows và Unix"""
    if proc is None:
        return
    try:
        if os.name == "nt":
            # Trên Windows: Dùng taskkill để diệt toàn bộ process tree
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        else:
            proc.terminate()
            proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def cleanup():
    """Dọn dẹp tài nguyên khi thoát"""
    global backend_process, frontend_process, backend_log_file, frontend_log_file
    print("\n[*] Đang dừng các dịch vụ...")
    if backend_process:
        print(" -> Đang dừng Backend...")
        kill_process_tree(backend_process)
        backend_process = None
    if frontend_process:
        print(" -> Đang dừng Frontend...")
        kill_process_tree(frontend_process)
        frontend_process = None
    try:
        if backend_log_file and not backend_log_file.closed:
            backend_log_file.close()
        if frontend_log_file and not frontend_log_file.closed:
            frontend_log_file.close()
    except Exception:
        pass
    print("[✓] Đã dừng toàn bộ ứng dụng an toàn. Tạm biệt!\n")


atexit.register(cleanup)


def signal_handler(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
if hasattr(signal, "SIGTERM"):
    signal.signal(signal.SIGTERM, signal_handler)


backend_log_file = None
frontend_log_file = None

def start_backend():
    """Khởi động Backend FastAPI qua Uvicorn"""
    global backend_process, backend_log_file
    if is_port_in_use(8000):
        print("[✓] Backend API đã đang chạy sẵn trên cổng 8000.")
        return

    print("[*] Đang khởi động Backend FastAPI (Uvicorn 8000)...")
    env = os.environ.copy()
    python_paths = [ROOT_DIR, BACKEND_DIR, os.path.join(ROOT_DIR, "interpretation_api"), os.path.join(ROOT_DIR, "knowledge_base")]
    env["PYTHONPATH"] = os.pathsep.join(python_paths) + (os.pathsep + env.get("PYTHONPATH", "") if env.get("PYTHONPATH") else "")
    env["PORT"] = "8000"

    logs_dir = os.path.join(ROOT_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    backend_log_path = os.path.join(logs_dir, "backend.log")
    backend_log_file = open(backend_log_path, "a", encoding="utf-8", errors="replace")

    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    backend_process = subprocess.Popen(
        cmd,
        cwd=BACKEND_DIR,
        env=env,
        stdout=backend_log_file,
        stderr=subprocess.STDOUT
    )


def start_frontend():
    """Khởi động Frontend Vite Dev Server"""
    global frontend_process, frontend_log_file
    if is_port_in_use(5180):
        print("[✓] Frontend Web đã đang chạy sẵn trên cổng 5180.")
        return

    # Dọn dẹp cache .vite cũ nếu có để tránh lỗi chunk cache
    vite_cache = os.path.join(FRONTEND_DIR, "node_modules", ".vite")
    if os.path.exists(vite_cache):
        try:
            shutil.rmtree(vite_cache, ignore_errors=True)
        except Exception:
            pass

    print("[*] Đang khởi động Frontend Web (Vite 5180)...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    cmd = [npm_cmd, "run", "dev"]

    logs_dir = os.path.join(ROOT_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    frontend_log_path = os.path.join(logs_dir, "frontend.log")
    frontend_log_file = open(frontend_log_path, "a", encoding="utf-8", errors="replace")

    frontend_process = subprocess.Popen(
        cmd,
        cwd=FRONTEND_DIR,
        stdout=frontend_log_file,
        stderr=subprocess.STDOUT,
        shell=(os.name == "nt")
    )


def main():
    print("=" * 76)
    print("      KHAI TÂM HUYỀN HỌC — TỬ VI & XEM BÓI TRÍ TUỆ NHÂN TẠO")
    print("               Tự Động Khởi Chạy Ứng Dụng Đa Nền Tảng")
    print("=" * 76)

    # 1. Khởi động Backend
    start_backend()

    # 2. Khởi động Frontend
    start_frontend()

    # 3. Chờ các dịch vụ sẵn sàng
    wait_for_port(8000, timeout=25, service_name="Backend API", proc=backend_process)
    wait_for_port(5180, timeout=20, service_name="Frontend Web", proc=frontend_process)

    # 4. Tự động mở trình duyệt web
    print("\n[🚀] Đang tự động mở ứng dụng trên trình duyệt web mặc định...")
    time.sleep(1)
    webbrowser.open(FRONTEND_URL)

    # 5. Bảng thông tin điều hướng
    print("\n" + "=" * 76)
    print(" ỨNG DỤNG ĐÃ KHỞI CHẠY THÀNH CÔNG VÀ SẴN SÀNG SỬ DỤNG!")
    print("=" * 76)
    print(f" [🌐] Giao Diện Ứng Dụng Web:   {FRONTEND_URL}")
    print(f" [⚙️] Backend API Máy Chủ:     {BACKEND_URL}")
    print(f" [📖] Tài Liệu Swagger Docs:    {BACKEND_URL}/docs")
    print(f" [❤️] Kiểm Tra Sức Khỏe:       {BACKEND_URL}/health")
    print("=" * 76)
    print(" HƯỚNG DẪN:")
    print(" • Cửa sổ này đang duy trì hoạt động của ứng dụng.")
    print(" • Bạn có thể sử dụng ứng dụng ngay trên trình duyệt vừa mở ra.")
    print(" • Để DỪNG ứng dụng: Nhấn tổ hợp phím [Ctrl + C] tại cửa sổ này.")
    print("=" * 76 + "\n")

    # 6. Giữ tiến trình sống và theo dõi
    try:
        while True:
            # Kiểm tra nếu tiến trình con đột ngột crash
            if backend_process and backend_process.poll() is not None:
                print("\n[!] Cảnh báo: Backend process đã dừng.")
                break
            if frontend_process and frontend_process.poll() is not None:
                print("\n[!] Cảnh báo: Frontend process đã dừng.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
