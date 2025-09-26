import pandas as pd
from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# -----------------------------
# Load CSV
# -----------------------------
df = pd.read_csv("extraction.csv")

# Normalize columns and text
df.columns = df.columns.str.strip().str.upper()
for col in ["STATE", "DISTRICT", "BLOCK", "CAT1", "CAT2"]:
    df[col] = df[col].astype(str).str.strip().str.upper().str.replace(" ", "_")

# VAL1 numeric (SGWE), VAL2 string (CAU)
df["VAL1"] = pd.to_numeric(df["VAL1"], errors="coerce")
df["VAL2"] = df["VAL2"].astype(str).str.strip()

# -----------------------------
# Category mapping
# -----------------------------
CATEGORY_GROUPS = {
    "SGWE": ["SGWE_NC", "SGWE_TOTAL", "SGWE_C", "SGWE_PQ"],
    "CAU": ["CAU_PQ", "CAU_TOTAL", "CAU_NC", "CAU_C"]
}

# -----------------------------
# Keyword mapping for natural language
# -----------------------------
NATURAL_KEYWORDS = {
    "STAGE_OF_GROUND_WATER_EXTRACTION": "SGWE_TOTAL",
    "STAGE_OF_GROUNDWATER_EXTRACTION": "SGWE_TOTAL",
    "CATEGORY_ASSESSMENT_UNIT_CANALIC": "CAU_C",
    "CATEGORY_ASSESSMENT_UNIT_NON_CANALIC": "CAU_NC",
    "CATEGORY_ASSESSMENT_UNIT_TOTAL": "CAU_TOTAL",
    "CATEGORY_ASSESSMENT_UNIT_PQ": "CAU_PQ"
}

# -----------------------------
# LLaMA LLM setup (optional)
# -----------------------------
try:
    from langchain_experimental.agents import create_pandas_dataframe_agent
    from langchain_huggingface import HuggingFaceEndpoint

    llama_llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-2-13b-chat-hf",
    temperature=0.1,
    max_new_tokens=512
)
    llama_agent = create_pandas_dataframe_agent(llama_llm, df, verbose=False)
except Exception:
    llama_agent = None

# -----------------------------
# Helpers
# -----------------------------
def detect_category(query: str):
    q = query.upper().replace(" ", "_")
    # Natural language mapping
    for key, val in NATURAL_KEYWORDS.items():
        if key in q:
            return [val]

    # Standard SGWE/CAU mapping
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
# Main keyword-based query handler
# -----------------------------
def answer_query_keyword(query: str) -> str:
    query_upper = query.upper()
    matched = df.copy()
    block = find_best_match(query, df["BLOCK"])
    district = None
    state = None
    if block:
        matched = matched[matched["BLOCK"] == block]
    else:
        district = find_best_match(query, df["DISTRICT"])
        if district:
            matched = matched[matched["DISTRICT"] == district]
        else:
            state = find_best_match(query, df["STATE"])
            if state:
                matched = matched[matched["STATE"] == state]
    location = block or district or state or "selected region"

    cats = detect_category(query)
    if cats:
        matched = matched[matched["CAT1"].isin(cats) | matched["CAT2"].isin(cats)]

    if matched.empty:
        return None  # fallback to LLM

    # --- Replace None/NAN with "has not been calculated"
    matched["VAL1"] = matched["VAL1"].fillna("has not been calculated")
    matched["VAL2"] = matched["VAL2"].replace(["nan", "NaN", "None"], "has not been calculated")

    # --- CAU queries → VAL2 string ---
    if any(c.startswith("CAU") for c in cats or []):
        val = matched["VAL2"].dropna().unique().tolist()
        val = ["has not been calculated" if str(v).strip().upper() in ["NAN", "NONE"] else str(v) for v in val]

        # Limit to 10 values
        display_val = val[:10]
        if len(val) > 10:
            display_val.append("...and more")

        return f"✅ {', '.join(cats)} values in {location}: {', '.join(display_val)}"

    # --- Difference queries (SGWE only) ---
    if "DIFFERENCE" in query_upper or "DIFF" in query_upper:
        areas = []
        for area_type in ["BLOCK", "DISTRICT", "STATE"]:
            for val in df[area_type].unique():
                val_words = val.upper().split()
                if all(w in query_upper.split() for w in val_words):
                    areas.append((area_type, val.upper()))
        if len(areas) < 2:
            return "⚠ Please specify exactly two areas for difference calculation."
        (type1, area1), (type2, area2) = areas[:2]
        diff_texts = []
        for cat in cats or []:
            if not cat.startswith("SGWE"):
                continue
            sub_df = df[(df["CAT1"] == cat)]
            val1 = sub_df[sub_df[type1] == area1]["VAL1"]
            val2 = sub_df[sub_df[type2] == area2]["VAL1"]
            val1_sum = val1.replace("has not been calculated", 0).sum()
            val2_sum = val2.replace("has not been calculated", 0).sum()
            diff = abs(val1_sum - val2_sum)
            diff_texts.append(f"✅ Difference in {cat} between {area1} and {area2} = {diff:,.2f}")
        return "\n".join(diff_texts)

    # --- SGWE queries → VAL1 numeric ---
    if any(c.startswith("SGWE") for c in cats or []):
        sgwe_values = matched["VAL1"].unique().tolist()
        sgwe_values = [str(v) if v != "has not been calculated" else v for v in sgwe_values]

        if "SGWE_TOTAL" in cats:
            numeric_vals = [float(v) for v in sgwe_values if v != "has not been calculated"]
            total_val = sum(numeric_vals)
            return f"✅ Total SGWE in {location} = {total_val:,.2f}"

        display_val = sgwe_values[:10]
        if len(sgwe_values) > 10:
            display_val.append("...and more")

        return f"✅ {', '.join(cats)} values in {location}: {', '.join(display_val)}"

    # --- Fallback: return VAL1 + VAL2 ---
    val1 = matched["VAL1"].unique().tolist()
    val2 = matched["VAL2"].unique().tolist()

    val1 = [str(v) if v != "has not been calculated" else v for v in val1]
    val2 = ["has not been calculated" if str(v).strip().upper() in ["NAN", "NONE"] else str(v) for v in val2]

    if len(val1) > 10:
        val1 = val1[:10] + ["...and more"]
    if len(val2) > 10:
        val2 = val2[:10] + ["...and more"]

    return f"✅ Values in {location}:\nVAL1: {', '.join(val1)}\nVAL2: {', '.join(val2)}"

# -----------------------------
# Hybrid query handler
# -----------------------------
def ask_csv(query: str) -> str:
    answer = answer_query_keyword(query)
    if answer:
        return answer
    if llama_agent:
        try:
            response = llama_agent.run(query)
            return f"🦙 LLaMA says: {response.strip()}"
        except Exception as e:
            return f"⚠ LLaMA query failed: {e}"
    return "⚠ No matching data found."

# -----------------------------
# FastAPI setup
# -----------------------------
app = FastAPI(title="CSV Query API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "SGW CSV Query API is running!"}

@app.post("/query")
def ask_query(request: QueryRequest):
    result = ask_csv(request.query)
    return {"query": request.query, "answer": result}

#.venv\Scripts\activate (.venv) activation
#uvicorn backend2:app --reload --port 8002 (running command)