import re
import unicodedata

def clean_text(text: str) -> str:
    if not text:
        return ""
    
    # Converte para minúsculas
    text = text.lower()
    
    # Remove acentos
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    
    # Mantém letras, números e espaços
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    
    # Remove espaços extras
    text = re.sub(r"\s+", " ", text).strip()
    
    return text