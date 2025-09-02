# AutoU Email Classifier

Sistema de classificação automática de emails usando IA para identificar mensagens produtivas e improdutivas.

## Funcionalidades

- 📧 Upload de emails em formato TXT ou PDF
- 🤖 Classificação automática usando IA
- 💬 Chatbot assistente integrado
- 📋 Sugestão de respostas automáticas
- 🎨 Interface moderna e responsiva

## Tecnologias

- **Backend**: FastAPI + Python
- **Frontend**: React + TypeScript + Vite
- **IA**: Google Gemini API + Scikit-learn
- **Deploy**: Render/Vercel/Heroku compatível

## Como executar

### Pré-requisitos

- Python 3.9+
- Node.js 16+
- Conta Google AI (para Gemini API)

### Configuração

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd autou-email-case
Configure o backend:

bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
Configure as variáveis de ambiente:

bash
cp .env.example .env
# Edite o .env com sua GOOGLE_API_KEY
Execute o backend:

bash
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
Em outro terminal, configure o frontend:

bash
cd frontend
npm install
Execute o frontend:

bash
npm run dev
Acesse: http://localhost:5173