from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd
import os
import re
from dotenv import load_dotenv

# -----------------------------
# APIRouter instead of FastAPI app
# -----------------------------
backend2_router = APIRouter()

class QueryRequest(BaseModel):
    query: str

# =============================
# BACKEND2: Extraction CSV logic
# =============================
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if HF_TOKEN:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = HF_TOKEN

# Load CSV
df2 = pd.read_csv("extraction.csv")
df2.columns = df2.columns.str.strip().str.upper()
for col in ["STATE", "DISTRICT", "BLOCK", "CAT1", "CAT2"]:
    df2[col] = df2[col].astype(str).str.strip().str.upper().str.replace(" ", "_")

df2["VAL1"] = pd.to_numeric(df2["VAL1"], errors="coerce")
df2["VAL2"] = df2["VAL2"].astype(str).str.strip()

CATEGORY_GROUPS = {
    "SGWE": ["SGWE_NC", "SGWE_TOTAL", "SGWE_C", "SGWE_PQ"],
    "CAU": ["CAU_PQ", "CAU_TOTAL", "CAU_NC", "CAU_C"]
}

NATURAL_KEYWORDS = {
    "STAGE_OF_GROUND_WATER_EXTRACTION": "SGWE_TOTAL",
    "STAGE_OF_GROUNDWATER_EXTRACTION": "SGWE_TOTAL",
    "CATEGORY_ASSESSMENT_UNIT_CANALIC": "CAU_C",
    "CATEGORY_ASSESSMENT_UNIT_NON_CANALIC": "CAU_NC",
    "CATEGORY_ASSESSMENT_UNIT_TOTAL": "CAU_TOTAL",
    "CATEGORY_ASSESSMENT_UNIT_PQ": "CAU_PQ"
}

# Optional LLaMA setup
try:
    from langchain_experimental.agents import create_pandas_dataframe_agent
    from langchain_huggingface import HuggingFaceEndpoint

    llama_llm2 = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-2-13b-chat-hf",
        temperature=0.1,
        max_new_tokens=512
    )
    llama_agent2 = create_pandas_dataframe_agent(llama_llm2, df2, verbose=False)
except Exception:
    llama_agent2 = None

# -----------------------------
# Helper functions
# -----------------------------
def detect_category(query: str):
    q = query.upper().replace(" ", "_")
    for key, val in NATURAL_KEYWORDS.items():
        if key in q:
            return [val]

    if "SGWE" in q or "TOTAL_STAGE_OF_GROUNDWATER_EXTRACTION" in q:
        for sub in CATEGORY_GROUPS["SGWE"]:
            if sub in q:
                return [sub]
        return ["SGWE_TOTAL"]

    for key, subcats in CATEGORY_GROUPS.items():
        for sub in subcats:
            if sub in q:
                return [sub]
        if key in q:
            return subcats
    return None

def find_best_match(query: str, series: pd.Series):
    words = query.upper().split()
    candidates = [s for s in series.dropna().unique() if s]
    candidates = sorted(candidates, key=lambda x: len(x), reverse=True)
    for cand in candidates:
        cand_words = cand.upper().split()
        if all(w in words for w in cand_words):
            return cand.upper()
    return None

# -----------------------------
# Backend2 main logic
# -----------------------------
def query(query: str) -> str:
    query_upper = query.upper()
    matched = df2.copy()

    block = find_best_match(query, df2["BLOCK"])
    district = None
    state = None
    if block:
        matched = matched[matched["BLOCK"] == block]
    else:
        district = find_best_match(query, df2["DISTRICT"])
        if district:
            matched = matched[matched["DISTRICT"] == district]
        else:
            state = find_best_match(query, df2["STATE"])
            if state:
                matched = matched[matched["STATE"] == state]

    location = block or district or state or "selected region"
    cats = detect_category(query)
    if cats:
        matched = matched[matched["CAT1"].isin(cats) | matched["CAT2"].isin(cats)]

    if matched.empty:
        if llama_agent2:
            try:
                return f"🦙 LLaMA says: {llama_agent2.run(query).strip()}"
            except Exception as e:
                return f"⚠ LLaMA query failed: {e}"
        return "⚠ No matching data found."

    matched["VAL1"] = matched["VAL1"].fillna("has not been calculated")
    matched["VAL2"] = matched["VAL2"].replace(["nan", "NaN", "None"], "has not been calculated")

    if any(c.startswith("CAU") for c in cats or []):
        val = matched["VAL2"].dropna().unique().tolist()
        val = ["has not been calculated" if str(v).strip().upper() in ["NAN", "NONE"] else str(v) for v in val]
        display_val = val[:10]
        if len(val) > 10: display_val.append("...and more")
        return f"✅ {', '.join(cats)} values in {location}: {', '.join(display_val)}"

    if "DIFFERENCE" in query_upper or "DIFF" in query_upper:
        areas = []
        for area_type in ["BLOCK", "DISTRICT", "STATE"]:
            for val in df2[area_type].unique():
                val_words = val.upper().split()
                if all(w in query_upper.split() for w in val_words):
                    areas.append((area_type, val.upper()))
        if len(areas) < 2:
            return "⚠ Please specify exactly two areas for difference calculation."
        (type1, area1), (type2, area2) = areas[:2]
        diff_texts = []
        for cat in cats or []:
            if not cat.startswith("SGWE"): continue
            sub_df = df2[(df2["CAT1"] == cat)]
            val1 = sub_df[sub_df[type1] == area1]["VAL1"]
            val2 = sub_df[sub_df[type2] == area2]["VAL1"]
            val1_sum = val1.replace("has not been calculated", 0).sum()
            val2_sum = val2.replace("has not been calculated", 0).sum()
            diff = abs(val1_sum - val2_sum)
            diff_texts.append(f"✅ Difference in {cat} between {area1} and {area2} = {diff:,.2f}")
        return "\n".join(diff_texts)

    if any(c.startswith("SGWE") for c in cats or []):
        sgwe_values = matched["VAL1"].unique().tolist()
        sgwe_values = [str(v) if v != "has not been calculated" else v for v in sgwe_values]
        if "SGWE_TOTAL" in cats:
            numeric_vals = [float(v) for v in sgwe_values if v != "has not been calculated"]
            total_val = sum(numeric_vals)
            return f"✅ Total SGWE in {location} = {total_val:,.2f}"
        display_val = sgwe_values[:10]
        if len(sgwe_values) > 10: display_val.append("...and more")
        return f"✅ {', '.join(cats)} values in {location}: {', '.join(display_val)}"

    val1 = [str(v) if v != "has not been calculated" else v for v in matched["VAL1"].unique().tolist()]
    val2 = ["has not been calculated" if str(v).strip().upper() in ["NAN", "NONE"] else str(v) for v in matched["VAL2"].unique().tolist()]

    if len(val1) > 10: val1 = val1[:10] + ["...and more"]
    if len(val2) > 10: val2 = val2[:10] + ["...and more"]

    return f"✅ Values in {location}:\nVAL1: {', '.join(val1)}\nVAL2: {', '.join(val2)}"

# -----------------------------
# Router endpoints
# -----------------------------
@backend2_router.get("/")
def root():
    return {"message": "Backend2 CSV Query API is running!"}

@backend2_router.post("/query")
def ask_query(request: QueryRequest):
    answer = query(request.query)
    return {"query": request.query, "answer": answer}


