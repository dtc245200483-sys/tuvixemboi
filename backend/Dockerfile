# ==============================================================================
# Giai đoạn 1: Build Giao diện Web (React + Vite + TailwindCSS)
# ==============================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend/web

COPY frontend/web/package*.json ./
RUN npm install

COPY frontend/web/ ./
ENV VITE_API_URL=""
RUN npm run build

# ==============================================================================
# Giai đoạn 2: Python Backend (FastAPI) & Phục vụ Toàn Bộ Web Platform
# ==============================================================================
FROM python:3.10-slim

# Thiết lập biến môi trường tối ưu cho Python trong container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:/app/backend:/app/interpretation_api:/app/knowledge_base" \
    PORT=8000

# Cài đặt các công cụ hệ thống cần thiết (pg_dump cho sao lưu Postgres, build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt dependencies trước để tối ưu Docker layer caching
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Tạo thư mục mount cho Persistent Volume (/data) lưu trữ ChromaDB và backups
RUN mkdir -p /data/vector_store /data/backups

# Sao chép toàn bộ mã nguồn backend và tri thức huyền học
COPY backend /app/backend
COPY interpretation_api /app/interpretation_api
COPY knowledge_base /app/knowledge_base
COPY Data_training /app/Data_training

# Sao chép bản build giao diện Frontend từ Giai đoạn 1 vào backend static
COPY --from=frontend-builder /app/frontend/web/dist /app/backend/static

WORKDIR /app/backend

EXPOSE 8000

# Khởi động ứng dụng FastAPI qua Uvicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
