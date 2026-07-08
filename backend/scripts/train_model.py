"""Train the demo TF-IDF + Logistic Regression model on the sample CSV."""
from pathlib import Path
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample_train.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "model.joblib"

def main():
    df = pd.read_csv(DATA)
    X = df['text'].astype(str)
    y = df['label']
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000)),
        ("clf", LogisticRegression(max_iter=1000))
    ])
    pipeline.fit(X, y)
    joblib.dump(pipeline, MODEL_PATH)
    print("Model trained and saved to", MODEL_PATH)

if __name__ == '__main__':
    main()
