import io
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from src.ocr_engine import OCREngine
from src.matcher import load_db, extract_candidates, match_top

CSV_PATH = "data/eyedrops_oint.csv"

app = FastAPI(title="Eyedrops OCR Matcher")

print("[INIT] Loading CSV...")
DF, NAME_COL, COMPANY_COL, DB_NAMES = load_db(CSV_PATH)
print(f"[INIT] CSV rows: {len(DF)} | name_col={NAME_COL}")

print("[INIT] Loading PaddleOCR...")
ENGINE = OCREngine()
print("[INIT] OCR ready.")

@app.post("/match")
async def match(file: UploadFile = File(...), topk: int = Form(5)):
    data = await file.read()
    import numpy as np, cv2
    file_bytes = np.frombuffer(data, np.uint8)
    bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if bgr is None:
        return JSONResponse({"error":"이미지 디코딩 실패"}, status_code=400)

    lines = ENGINE.ocr_lines(bgr)
    if not lines:
        return {"matches": [], "ocr_lines": []}

    cands = extract_candidates(lines)
    results = match_top(cands, DB_NAMES, DF, NAME_COL, COMPANY_COL, topk=topk)
    return {"matches": results, "ocr_lines": lines, "candidates": cands}

@app.post("/match_text")
async def match_text(text: str = Form(...), topk: int = Form(5)):
    lines = [t for t in text.split("\n") if t.strip()]
    cands = extract_candidates(lines)
    results = match_top(cands, DB_NAMES, DF, NAME_COL, COMPANY_COL, topk=topk)
    return {"matches": results, "ocr_lines": lines, "candidates": cands}

@app.get("/")
def root():
    return {"ok": True, "msg": "POST /match (file), /match_text (text) 사용"}
