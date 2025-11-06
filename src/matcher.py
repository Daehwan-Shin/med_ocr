import re
import pandas as pd
from rapidfuzz import process, fuzz

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip()
    try:
        import unicodedata
        s = unicodedata.normalize("NFKC", s)
    except Exception:
        pass
    repl = {
        "㎖": "mL", "μ": "u", "％": "%", "°": "o", "–": "-",
        "／": "/", "ㆍ":"·", "·":"·"
    }
    for k,v in repl.items():
        s = s.replace(k,v)
    s = re.sub(r"\s+", " ", s)
    return s

def load_db(csv_path: str):
    df = pd.read_csv(csv_path)
    name_col = None
    for c in ["제품명","품목명","product","name"]:
        if c in df.columns:
            name_col = c; break
    if name_col is None:
        name_col = df.columns[0]

    company_col = None
    for c in ["회사","company","제조사","업체명"]:
        if c in df.columns:
            company_col = c; break

    names = [normalize_text(x) for x in df[name_col].fillna("").tolist()]
    return df, name_col, company_col, names

def extract_candidates(ocr_lines):
    KEY_HINTS = ["점안", "안연고", "mL", "mg", "%", "현탁", "겔"]
    cands = []
    for line in ocr_lines:
        t = normalize_text(line)
        if len(t) < 2: 
            continue
        score = 0
        if any(k in t for k in KEY_HINTS): score += 2
        score += min(len(t)//8, 3)
        cands.append((t, score))
    seen, uniq = set(), []
    for t, sc in sorted(cands, key=lambda x: -x[1]):
        if t in seen: continue
        seen.add(t); uniq.append(t)
    return uniq[:80]

def match_top(candidates, db_names, df, name_col, company_col, topk=5):
    overall = process.extract(
        " ".join(candidates[:20]),
        db_names,
        scorer=fuzz.WRatio,
        limit=topk
    )
    hits = []
    for c in candidates[:40]:
        hits.extend(process.extract(c, db_names, scorer=fuzz.WRatio, limit=5))

    best = {}
    for name, score, idx in (overall + hits):
        if name not in best or best[name][0] < score:
            best[name] = (score, idx)

    ranked = sorted([(k, v[0], v[1]) for k,v in best.items()], key=lambda x: -x[1])[:topk]
    out = []
    for name, score, idx in ranked:
        row = df.iloc[idx].to_dict()
        out.append({
            "name": row.get(name_col),
            "score": int(score),
            "company": row.get(company_col),
            "row": row
        })
    return out
