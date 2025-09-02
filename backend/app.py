from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import fitz  # PyMuPDF
from typing import Dict, List, Optional
import os
import sys
import logging
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adiciona o diretório atual ao path para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from classifier import classify_email
    from chatbot import chat_with_ai
except ImportError as e:
    logger.error(f"Erro de importação: {e}")
    # Fallback para quando não conseguir importar
    def classify_email(text: str):
        return {"categoria": "Erro", "resposta": "Erro no servidor. Modelo não carregado."}
    
    def chat_with_ai(message: str, history: List):
        return {"resposta": "Erro no servidor. Chat não disponível."}

app = FastAPI(title="AutoU Email Classifier API", version="1.0.0")

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
else:
    logger.info("Frontend build não encontrado em %s — será necessário construir o frontend.", FRONTEND_DIST)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailInput(BaseModel):
    text: str

class ChatInput(BaseModel):
    message: str
    history: Optional[List] = []

@app.get("/")
async def root():
    return {"message": "AutoU Email Classifier API", "version": "1.0.0"}

@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/process_text")
async def process_text(data: EmailInput):
    try:
        result = classify_email(data.text)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Erro ao processar texto: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar texto: {str(e)}")

@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    content = ""
    
    if not filename.lower().endswith((".txt", ".pdf")):
        raise HTTPException(status_code=400, detail="Formato não suportado. Use .txt ou .pdf")
    
    try:
        data = await file.read()
        
        if filename.lower().endswith(".txt"):
            content = data.decode("utf-8", errors="ignore")
        elif filename.lower().endswith(".pdf"):
            pdf = fitz.open(stream=data, filetype="pdf")
            for page in pdf:
                content += page.get_text()
            pdf.close()
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro ao ler arquivo: {str(e)}")
    
    try:
        result = classify_email(content)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Erro ao classificar email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao classificar email: {str(e)}")

@app.post("/chat")
async def chat(data: ChatInput):
    try:
        result = chat_with_ai(data.message, data.history)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Erro no chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no chat: {str(e)}")