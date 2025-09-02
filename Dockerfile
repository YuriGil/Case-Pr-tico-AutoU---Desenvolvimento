# Etapa 1 - Build do frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Etapa 2 - Backend Python
FROM python:3.11-slim
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y build-essential libpoppler-cpp-dev pkg-config python3-dev

# Copiar backend
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend

# Copiar frontend build para dentro do backend
COPY --from=frontend-builder /app/frontend/dist ./backend/frontend/dist

# Variáveis de ambiente
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# Rodar servidor com Gunicorn + Uvicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "backend.app:app", "--bind", "0.0.0.0:8080", "--workers", "2"]
