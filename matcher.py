# matcher.py
import re
from typing import List, Dict, Optional

import pandas as pd
from rapidfuzz import process, fuzz


# 점안제 이름에서 공통적으로 제거하고 싶은 단어들
REMOVE_TOKENS = [
    "점안액", "점안겔", "점안현탁액", "점안제",
    "안연고",
    "(1회용)", "1회용",
    "미니", "에스디", "SD",
    "%", "㎖", "mL", "mg", "g", "μg",
]

# OCR에서 자주 헷갈리는 문자 교정용
CONFUSION_MAP = {
    "０": "0",
    "１": "1",
    "２": "2",
    "３": "3",
    "４": "4",
    "５": "5",
    "６": "6",
    "７": "7",
    "８": "8",
    "９": "9",
    "O": "0",
    "o": "0",
    "Ⅰ": "1",
    "l": "1",
    "I": "1",
    "Ｂ": "B",
    "㎎": "mg",
    "㎖": "mL",
}


def normalize_text(text: str) -> str:
    """약 이름 비교용 정규화 함수"""
    if not isinstance(text, str):
        return ""

    s = text.strip()

    # 자주 헷갈리는 문자들 통일
    for src, dst in CONFUSION_MAP.items():
        s = s.replace(src, dst)

    # 대문자 변환
    s = s.upper()

    # 공통 토큰 제거
    for token in REMOVE_TOKENS:
        s = s.replace(token.upper(), "")

    # 괄호 안 내용은 크게 의미 없으니 제거 (ex: (히알루론산나트륨))
    s = re.sub(r"\(.*?\)", "", s)

    # 한글/영문/숫자만 남기고 나머지 제거
    s = re.sub(r"[^0-9A-Z가-힣]", "", s)

    # 연속 공백 정리
    s = re.sub(r"\s+", "", s)

    return s


class DrugMatcher:
    def __init__(self, csv_path: str):
        print(f"[INIT] loading CSV: {csv_path}")
        self.df = pd.read_csv(csv_path)

        if "제품명" not in self.df.columns:
            raise ValueError("CSV에 '제품명' 컬럼이 없습니다. 헤더 이름을 꼭 '제품명'으로 맞춰주세요.")

        # 정규화된 이름 컬럼 추가
        self.df["__norm_name"] = self.df["제품명"].astype(str).apply(normalize_text)
        self.choices = self.df["__norm_name"].tolist()
        print(f"[INIT] rows: {len(self.df)}")

    def match_one(self, text: str, top_k: int = 5, min_score: int = 60) -> List[Dict]:
        """
        text: OCR로 읽은 한 줄(또는 전체 문자열)
        top_k: 상위 몇 개 후보까지 보여줄지
        min_score: 이 점수 이하인 매칭은 버림
        """
        norm = normalize_text(text)
        if not norm:
            return []

        results = process.extract(
            norm,
            self.choices,
            scorer=fuzz.WRatio,
            limit=top_k,
        )

        matches: List[Dict] = []
        for matched_norm, score, idx in results:
            if score < min_score:
                continue
            row = self.df.iloc[idx]

            matches.append({
                "score": int(score),
                "matched_name": str(row["제품명"]),
                "row_index": int(idx),
                "row": row.to_dict(),  # 필요하면 클라이언트에서 다른 컬럼도 사용
            })

        return matches

    def match_lines(self, lines: List[str], top_k: int = 5, min_score: int = 60) -> Dict[str, List[Dict]]:
        """
        여러 줄 텍스트 한꺼번에 매칭.
        결과는 { 입력문자열: [매칭결과들...] } 형태.
        """
        out: Dict[str, List[Dict]] = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            out[line] = self.match_one(line, top_k=top_k, min_score=min_score)
        return out
