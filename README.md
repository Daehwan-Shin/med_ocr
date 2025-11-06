# Eyedrops OCR Matcher

이미지 → OCR(PaddleOCR) → `eyedrops_oint.csv`와 퍼지매칭해 정확 제품명을 찾아주는 FastAPI 서버.

## 준비
1) `data/eyedrops_oint.csv` 넣기 (첫 컬럼이 제품명, 혹은 '제품명/품목명' 등 자동인식)
2) 설치:
   ```bash
   pip install -r requirements.txt
   ```

## 실행
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API
- `POST /match` (multipart)
  - `file`: 이미지
  - `topk`: 정수(기본 5)

- `POST /match_text` (form)
  - `text`: 줄바꿈으로 구분된 문자열
  - `topk`: 정수

## 샘플
```bash
curl -X POST "http://localhost:8000/match"   -F "file=@sample.jpg" -F "topk=5"
```
