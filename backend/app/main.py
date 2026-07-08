from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from .model import load_or_train_model, predict_text, extract_text_from_image
from .factcheck import fact_check_text
from .transformer_model import predict_zero_shot
import os

# Load local environment variables from .env if present
load_dotenv()

app = FastAPI(title="Fake News Detection (Prototype)")

# Allow local frontend dev server to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

model = load_or_train_model()


@app.post("/predict/text")
async def predict_text_endpoint(text: str = Form(...)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Empty text provided")
    label, score = predict_text(model, text)
    return JSONResponse({"label": label, "score": float(score)})


@app.post("/predict/image")
async def predict_image_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        extracted = extract_text_from_image(contents)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    label, score = predict_text(model, extracted)
    return JSONResponse({"extracted_text": extracted, "label": label, "score": float(score)})


@app.post("/factcheck/text")
async def factcheck_text_endpoint(text: str = Form(...)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Empty text provided")
    result = fact_check_text(text)
    return JSONResponse(result)


@app.post("/predict/text/transformer")
async def predict_text_transformer(text: str = Form(...)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Empty text provided")
    label, score, details = predict_zero_shot(text)
    return JSONResponse({"label": label, "score": score, "details": details})
