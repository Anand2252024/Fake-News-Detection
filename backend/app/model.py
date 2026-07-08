import os
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import joblib
from typing import Tuple
from io import BytesIO
from PIL import Image
from PIL import ImageFilter, ImageOps, ImageEnhance

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "model.joblib")


def load_or_train_model():
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "models"), exist_ok=True)

    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            # Sanity check that the loaded model is usable with the current sklearn version.
            model.predict_proba(["sanity check"])
            return model
        except Exception:
            os.remove(MODEL_PATH)

    # Train on sample data
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_train.csv")
    if not os.path.exists(data_path):
        raise RuntimeError("Training data not found. Run the training script.")
    df = pd.read_csv(data_path)
    X = df['text'].astype(str)
    y = df['label']
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=5000)),
            ("clf", LogisticRegression(max_iter=1000))
        ]
    )
    pipeline.fit(X, y)
    joblib.dump(pipeline, MODEL_PATH)
    return pipeline


def predict_text(model: Pipeline, text: str) -> Tuple[str, float]:
    probs = model.predict_proba([text])[0]
    idx = probs.argmax()
    label = model.classes_[idx]
    score = probs[idx]
    return label, score


def extract_text_from_image(contents: bytes) -> str:
    try:
        img = Image.open(BytesIO(contents)).convert('RGB')
    except Exception as e:
        raise RuntimeError("Invalid image file") from e

    # Preprocessing: convert to grayscale, enhance contrast, apply median filter, and auto-threshold
    try:
        gray = ImageOps.grayscale(img)
        # increase contrast
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(1.5)
        # reduce noise
        gray = gray.filter(ImageFilter.MedianFilter(size=3))
        # apply simple threshold
        bw = gray.point(lambda x: 0 if x < 128 else 255, '1')
        # import pytesseract locally to avoid import-time errors on some Python versions
        try:
            import pytesseract
        except Exception:
            raise RuntimeError("pytesseract is not available or incompatible with this Python version. Install a compatible pytesseract or use Python 3.11/3.10.")
        # pass to tesseract
        text = pytesseract.image_to_string(bw)
    except Exception as e:
        raise RuntimeError("Tesseract OCR failed. Ensure tesseract is installed on your system and pytesseract is configured.") from e
    return text
