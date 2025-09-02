import os
import logging
import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()
# Configuração da API do Google
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        # Configuração do modelo
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
        
        model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        logging.info("Google AI Gemini configurado com sucesso para respostas")
    except Exception as e:
        logging.error(f"Erro ao configurar Google AI: {e}")
        model = None
else:
    model = None
    logging.warning("GOOGLE_API_KEY não encontrada. Usando respostas padrão.")

def suggest_response(category: str, text: str) -> str:
    """
    Gera sugestão de resposta usando Google Gemini API com fallback.
    """
    if model is not None:
        prompt = f"""
        Classificação: {category}
        Email: {text}
        
        Com base na classificação e conteúdo do email acima, sugira uma resposta curta, educada e profissional em português.
        A resposta deve ser direta e adequada ao contexto do email.
        
        Se for um email produtivo (que requer ação), ofereça ajuda e indique que a equipe irá analisar.
        Se for um email improdutivo (sem necessidade de ação), agradeça de forma cordial.
        """
        
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logging.error(f"Erro ao chamar Google AI: {e}")
    
    # Respostas padrão quando Google AI não disponível
    if category == "Produtivo":
        return "Olá! Recebemos sua solicitação e nossa equipe irá analisar e retornar o mais breve possível. Obrigado."
    return "Obrigado pela sua mensagem! No momento nenhuma ação é necessária. Abraços."