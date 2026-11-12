import os, time, io
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError

app = FastAPI(title="RoadWatch ML Inference", version="0.1.0")
MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/best.pt"))
CONFIDENCE = float(os.getenv("YOLO_CONFIDENCE", "0.35"))
MAX_BYTES = 10 * 1024 * 1024
ALLOWED = {"image/jpeg", "image/png", "image/webp"}
model = None
if MODEL_PATH.is_file():
    try:
        from ultralytics import YOLO
        model = YOLO(str(MODEL_PATH))
    except Exception as exc:
        print(f"Model could not be loaded: {exc}")

@app.get("/health")
def health():
    return {"status": "ok", "modelLoaded": model is not None, "modelVersion": MODEL_PATH.name if model else None}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(415, "Only JPEG, PNG, or WebP images are accepted")
    raw = await file.read(MAX_BYTES + 1)
    if not raw:
        raise HTTPException(400, "Image file is empty")
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "Image exceeds the 10 MB limit")
    try:
        image = Image.open(io.BytesIO(raw)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(400, "Uploaded file is not a valid image")
    if model is None:
        return {"detections": [], "modelVersion": "unavailable", "inferenceTimeMs": 0, "warning": "Weights missing; no inference was run."}
    start = time.perf_counter()
    outputs = model.predict(image, conf=CONFIDENCE, verbose=False)
    result = outputs[0]
    names = result.names
    detections = []
    for box in result.boxes:
        xyxy = box.xyxy[0].tolist()
        detections.append({"class": str(names[int(box.cls[0].item())]), "confidence": float(box.conf[0].item()), "bbox": [round(float(v), 2) for v in xyxy]})
    return {"detections": detections, "modelVersion": MODEL_PATH.name, "inferenceTimeMs": round((time.perf_counter()-start)*1000)}
