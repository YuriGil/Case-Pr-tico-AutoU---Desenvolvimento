import os
import logging
from typing import List, Dict
import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()

# Configuração da API do Google
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        # Configuração do modelo para chat
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        chat_model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        logging.info("Google AI Gemini configurado com sucesso para chat")
    except Exception as e:
        logging.error(f"Erro ao configurar Google AI para chat: {e}")
        chat_model = None
else:
    chat_model = None
    logging.warning("GOOGLE_API_KEY não encontrada. Chat não disponível.")

def chat_with_ai(message: str, history: List[Dict] = None) -> Dict:
    """
    Função para interagir com o chatbot da Google AI.
    """
    if chat_model is None:
        return {
            "resposta": "Desculpe, o serviço de chat não está disponível no momento. Por favor, verifique a configuração da API.",
            "history": history or []
        }
    
    try:
        # Prepara o histórico de conversa
        chat_history = []
        if history:
            for msg in history:
                if msg.get("role") == "user":
                    chat_history.append({"role": "user", "parts": [msg.get("content", "")]})
                elif msg.get("role") == "assistant":
                    chat_history.append({"role": "model", "parts": [msg.get("content", "")]})
        
        # Inicia a conversa
        chat = chat_model.start_chat(history=chat_history)
        
        # Envia a mensagem atual
        response = chat.send_message(message)
        
        # Atualiza o histórico
        updated_history = (history or []) + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response.text}
        ]
        
        return {
            "resposta": response.text,
            "history": updated_history
        }
        
    except Exception as e:
        logging.error(f"Erro no chat: {e}")
        return {
            "resposta": "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.",
            "history": history or []
        }