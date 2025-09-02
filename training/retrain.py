import re
import joblib
import json
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score
import nltk
from nltk.corpus import stopwords
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("training.log"), logging.StreamHandler()]
)

def ensure_nltk_data():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

def anonymize_text(text: str) -> str:
    """Anonimiza dados sensíveis no texto"""
    if not text:
        return ""
    
    # Anonimiza emails
    text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[EMAIL]", text)
    # Anonimiza CPFs
    text = re.sub(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", "[CPF]", text)
    text = re.sub(r"\b\d{11}\b", "[CPF]", text)
    # Anonimiza números longos
    text = re.sub(r"\b\d{6,}\b", "[NUMERO]", text)
    return text

def load_dataset(path="sample_emails/dataset.json"):
    """Carrega e prepara o dataset"""
    p = Path(path)
    if not p.exists():
        logging.error(f"Dataset não encontrado: {path}")
        return [], []
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        texts = []
        labels = []
        
        for item in data:
            text = item.get("text", "").strip()
            label = item.get("label", "").strip().lower()
            
            if text and label:
                texts.append(anonymize_text(text))
                # Converte label para binário (1 = Produtivo, 0 = Improdutivo)
                labels.append(1 if label.startswith("prod") else 0)
        
        logging.info(f"Carregados {len(texts)} exemplos do dataset")
        return texts, labels
        
    except Exception as e:
        logging.error(f"Erro ao carregar dataset: {e}")
        return [], []

def augment_dataset(texts, labels):
    """Aumenta o dataset com variações simples"""
    augmented_texts = texts.copy()
    augmented_labels = labels.copy()
    
    # Adiciona algumas variações simples para melhorar o modelo
    for text, label in zip(texts, labels):
        if label == 1:  # Apenas para emails produtivos
            augmented_texts.append(text + " Por favor, me retorne.")
            augmented_labels.append(1)
            
            augmented_texts.append("Prezados, " + text)
            augmented_labels.append(1)
    
    return augmented_texts, augmented_labels

def train_and_evaluate():
    """Treina e avalia o modelo"""
    ensure_nltk_data()
    
    X, y = load_dataset()
    if not X:
        logging.error("Nenhum dado para treinar. Verifique o dataset.")
        return
    
    # Aumenta o dataset
    X, y = augment_dataset(X, y)
    logging.info(f"Dataset após aumento: {len(X)} exemplos")
    
    # Split dos dados
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    
    logging.info(f"Treino: {len(X_train)}, Val: {len(X_val)}, Teste: {len(X_test)}")
    
    # Stopwords em português e inglês
    pt_stop = stopwords.words("portuguese")
    en_stop = stopwords.words("english")
    stop_words = list(set(pt_stop + en_stop))
    
    # Pipeline de classificação
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=3000, 
            stop_words=stop_words,
            ngram_range=(1, 2),  # Inclui bigramas
            min_df=2,            # Ignora termos muito raros
            max_df=0.8           # Ignora termos muito comuns
        )),
        ("clf", LogisticRegression(
            max_iter=1000, 
            class_weight="balanced",
            random_state=42,
            C=0.1
        ))
    ])
    
    # Treinamento
    pipeline.fit(X_train, y_train)
    
    # Avaliação
    for name, X_data, y_data in [("Validação", X_val, y_val), ("Teste", X_test, y_test)]:
        y_pred = pipeline.predict(X_data)
        accuracy = accuracy_score(y_data, y_pred)
        f1 = f1_score(y_data, y_pred)
        
        logging.info(f"{name} - Acurácia: {accuracy:.4f}, F1-Score: {f1:.4f}")
        
        report = classification_report(y_data, y_pred, output_dict=True)
        logging.info(f"Relatório de {name}:\n" + json.dumps(report, indent=2, ensure_ascii=False))
    
    # Salva o modelo
    Path("models").mkdir(exist_ok=True)
    joblib.dump(pipeline, "models/model.joblib")
    logging.info("Modelo salvo em models/model.joblib")
    
    # Salva as métricas
    Path("metrics").mkdir(exist_ok=True)
    y_pred_test = pipeline.predict(X_test)
    test_report = classification_report(y_test, y_pred_test, output_dict=True)
    
    with open("metrics/test_metrics.json", "w", encoding="utf-8") as f:
        json.dump(test_report, f, indent=2, ensure_ascii=False)
    
    logging.info("Métricas salvas em metrics/test_metrics.json")

if __name__ == "__main__":
    train_and_evaluate()