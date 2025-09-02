import nltk
import pandas as pd
from nltk.corpus import stopwords
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
from pathlib import Path

# Garante stopwords
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download('stopwords')

# Dataset de exemplo
DATA = [
    ("Olá, preciso de uma atualização sobre o processo #123. Há previsão de entrega?", "Produtivo"),
    ("Bom dia, preciso que reabram o chamado 9876, não tive retorno.", "Produtivo"),
    ("Anexo o contrato para revisão. Obrigado.", "Produtivo"),
    ("Feliz Natal! Que 2025 seja incrível para toda a equipe!", "Improdutivo"),
    ("Obrigado pela ajuda ontem. Abraços.", "Improdutivo"),
    ("Parabéns pelo excelente trabalho de vocês!", "Improdutivo"),
]

df = pd.DataFrame(DATA, columns=["text", "label"])
X = df["text"]
y = df["label"].apply(lambda x: 1 if x == "Produtivo" else 0)

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Stopwords PT+EN
pt_stop = stopwords.words("portuguese")
en_stop = stopwords.words("english")
stop_words = list(set(pt_stop + en_stop))

# Pipeline
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1,2), max_features=5000, stop_words=stop_words)),
    ("clf", LogisticRegression(max_iter=1000, random_state=42))
])

# Train
pipeline.fit(X_train, y_train)

# Evaluation
y_pred = pipeline.predict(X_test)
print("\n===== Resultados de Validação =====")
print(classification_report(y_test, y_pred, target_names=["Improdutivo", "Produtivo"]))
print("Matriz de confusão:")
print(confusion_matrix(y_test, y_pred))

# Cria diretório models se não existir
Path("models").mkdir(exist_ok=True)

# Save model
joblib.dump(pipeline, "models/model.joblib")
print("\nModelo salvo em models/model.joblib")