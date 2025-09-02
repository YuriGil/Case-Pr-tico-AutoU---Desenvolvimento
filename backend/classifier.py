import joblib
from pathlib import Path
import os
import sys
import logging

# Adiciona o diretório atual ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.preprocessor import clean_text
from utils.responses import suggest_response

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tenta localizar model.joblib no diretório models/
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "model.joblib"

def classify_email(text: str):
    if not text or not text.strip():
        return {"categoria": "Improdutivo", "resposta": "Texto vazio ou inválido."}
    
    cleaned = clean_text(text)
    
    # Se existir modelo salvo, carrega o pipeline
    if MODEL_PATH.exists():
        try:
            pipeline = joblib.load(MODEL_PATH)
            # pipeline espera texto cru (o vetorizer faz transform)
            pred = pipeline.predict([cleaned])[0]
            # assumimos 1 = Produtivo, 0 = Improdutivo
            category = "Produtivo" if int(pred) == 1 else "Improdutivo"
            logger.info(f"Classificado usando modelo: {category}")
        except Exception as e:
            logger.error(f"Erro carregando/preditando com o modelo: {e}. Usando fallback por keywords.")
            category = _fallback_by_keywords(cleaned)
    else:
        logger.warning("Modelo não encontrado. Usando fallback por keywords.")
        category = _fallback_by_keywords(cleaned)
    
    response = suggest_response(category, text)
    return {"categoria": category, "resposta": response}

def _fallback_by_keywords(text_cleaned: str) -> str:
    keywords_produtivo = [
        "suporte", "problema", "erro", "status", "atualizacao", "atualização",
        "dúvida", "duvida", "reunião", "reuniao", "contrato", "anexo", "urgente",
        "processo", "solicitação", "solicitacao", "chamado", "ajuda", "suporte", "cliente",
        "projeto", "prazo", "entrega", "relatório", "relatorio", "documento", "pagamento",
        "fatura", "nota fiscal", "orcamento", "orçamento", "proposta", "contrato"
    ]
    
    if any(word in text_cleaned for word in keywords_produtivo):
        return "Produtivo"
    return "Improdutivo"