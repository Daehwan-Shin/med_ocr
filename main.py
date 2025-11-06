# main.py
from typing import List, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel

from matcher import DrugMatcher

CSV_PATH = "data/eyedrops_oint.csv"

app = FastAPI(title="Eyedrops Matcher API")

MATCHER = DrugMatcher(CSV_PATH)


class MatchTextRequest(BaseModel):
    # ML Kit / 앱 OCR 결과 전체 문자열
    text: str
    top_k: int = 5
    min_score: int = 60


class MatchLinesRequest(BaseModel):
    # OCR 결과를 줄 단위로 이미 쪼개서 보낼 때
    lines: List[str]
    top_k: int = 5
    min_score: int = 60


@app.get("/")
def root():
    return {
        "message": "Eyedrops matcher running.",
        "csv_rows": len(MATCHER.df),
    }


@app.post("/match_text")
def match_text(req: MatchTextRequest) -> Dict[str, Any]:
    """
    전체 텍스트 한 덩어리를 보내면,
    줄 단위로 쪼개서 매칭해줌.
    """
    # 줄 단위로 split
    lines = [l for l in req.text.splitlines() if l.strip()]
    result = MATCHER.match_lines(lines, top_k=req.top_k, min_score=req.min_score)
    return {
        "lines": lines,
        "result": result,
    }


@app.post("/match_lines")
def match_lines(req: MatchLinesRequest) -> Dict[str, Any]:
    """
    이미 줄 단위로 쪼개진 OCR 결과 리스트를 바로 보내고 싶을 때 사용.
    """
    result = MATCHER.match_lines(req.lines, top_k=req.top_k, min_score=req.min_score)
    return {
        "result": result,
    }
