from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
import re
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import requests
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_huggingface import HuggingFaceEndpoint


# --- Load environment variables ---
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if HF_TOKEN:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = HF_TOKEN

# -------------------------------------------------
# 📂 Load CSV
# -------------------------------------------------
df = pd.read_csv("DelhiFandS.csv")

# ✅ Normalize column names and text fields
df.columns = df.columns.str.strip().str.upper()
for col in ["STATE", "DISTRICT", "TEHSIL", "ID"]:
    df[col] = df[col].astype(str).str.strip().str.upper()

# ✅ Convert numeric columns safely
df["FRESH"] = pd.to_numeric(df["FRESH"], errors="coerce")
df["SALINE"] = pd.to_numeric(df["SALINE"], errors="coerce")

# -------------------------------------------------
# ✅ ID mapping
# -------------------------------------------------
ID_MAP = {
    "UA": "TOTAL GROUND WATER AVAILABILITY IN UNCONFINED AQUIFER",
    "DC": "DYNAMIC CONFINED GROUND WATER RESOURCES",
    "IC": "IN-STORAGE CONFINED GROUND WATER RESOURCES",
    "TC": "TOTAL CONFINED GROUND WATER RESOURCES",
    "DSC": "DYNAMIC SEMI CONFINED GROUND WATER RESOURCES",
    "ISC": "IN-STORAGE SEMI CONFINED GROUND WATER RESOURCES",
    "TSC": "TOTAL SEMI-CONFINED CONFINED GROUND WATER RESOURCES",
    "TGW": "TOTAL GROUND WATER AVAILABILITY IN THE AREA"
}

# -------------------------------------------------
# ✅ LLaMA LLM Agent (optional)
# -------------------------------------------------
try:
    llama_llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-2-13b-chat-hf",
    temperature=0.1,
    max_new_tokens=512
)
    llama_agent = create_pandas_dataframe_agent(
        llama_llm,
        df,
        verbose=False,
        allow_dangerous_code=True
    )
except Exception as e:
    llama_agent = None
    print(f"⚠ Could not initialize LLaMA agent: {e}")


# -------------------------------------------------
# --- Helper Functions ---
# -------------------------------------------------
def detect_id(query: str):
    normalized_query = query.upper().replace("GROUNDWATER", "GROUND WATER")
    words = normalized_query.split()

    for short, full in ID_MAP.items():
        if short in words:
            return short
        full_words = full.upper().split()
        if all(w in words for w in full_words):
            return short

    if "GROUND" in words and "WATER" in words and "TOTAL" in words:
        return "TGW"
    if "UNCONFINED" in words:
        return "UA"
    if "CONFINED" in words and "SEMI" not in words:
        return "TC"
    if "SEMI" in words:
        return "TSC"

    return None


def find_best_match_in_column(query_upper: str, series: pd.Series):
    candidates = [s for s in pd.Series(series).dropna().astype(str).str.strip().unique() if s and s.upper() != "NAN"]
    candidates = sorted(candidates, key=lambda x: len(x), reverse=True)
    for cand in candidates:
        try:
            if re.search(rf"\b{re.escape(cand.upper())}\b", query_upper):
                return cand.upper()
        except re.error:
            if cand.upper() in query_upper:
                return cand.upper()
    return None


def answer_query_keyword(query: str) -> str:
    words = query.upper().split()
    matched = df.copy()

    state_found = None
    district_found = None
    tehsil_found = None
    measure = None

    # Detect measure
    if "FRESH" in words:
        measure = "FRESH"
    elif "SALINE" in words:
        measure = "SALINE"

    # --- Difference Queries ---
    if "DIFFERENCE" in words:
        areas = []

        for t in df["TEHSIL"].unique():
            t_words = t.upper().split()
            if all(w in words for w in t_words):
                areas.append(("TEHSIL", t.upper()))

        if len(areas) < 2:
            for d in df["DISTRICT"].unique():
                d_words = d.upper().split()
                if all(w in words for w in d_words):
                    areas.append(("DISTRICT", d.upper()))

        if len(areas) < 2:
            for s in df["STATE"].unique():
                s_words = s.upper().split()
                if all(w in words for w in s_words):
                    areas.append(("STATE", s.upper()))

        areas = areas[:2]

        if len(areas) < 2:
            return "⚠ Please mention exactly two areas for difference calculation."

        area_type1, area1 = areas[0]
        area_type2, area2 = areas[1]

        sub_df = df.copy()
        resource_id = detect_id(query)
        if resource_id:
            sub_df = sub_df[sub_df["ID"] == resource_id]

        measure_list = []
        if "FRESH" in words:
            measure_list.append("FRESH")
        if "SALINE" in words:
            measure_list.append("SALINE")
        if not measure_list:
            measure_list = ["FRESH", "SALINE"]

        diff_text = []
        for m in measure_list:
            val1 = sub_df[sub_df[area_type1] == area1][m].fillna(0).sum()
            val2 = sub_df[sub_df[area_type2] == area2][m].fillna(0).sum()
            diff = abs(val1 - val2)
            if resource_id:
                diff_text.append(f"✅ {m} difference for {ID_MAP[resource_id]} between {area1} and {area2} = {diff:,.2f}")
            else:
                diff_text.append(f"✅ {m} difference between {area1} and {area2} = {diff:,.2f}")

        return "\n".join(diff_text)

    query_upper = " ".join(words)
    tehsil_found = find_best_match_in_column(query_upper, df["TEHSIL"])
    if tehsil_found:
        matched = matched[matched["TEHSIL"] == tehsil_found]
    else:
        district_found = find_best_match_in_column(query_upper, df["DISTRICT"])
        if district_found:
            matched = matched[matched["DISTRICT"] == district_found]
        else:
            state_found = find_best_match_in_column(query_upper, df["STATE"])
            if state_found:
                matched = matched[matched["STATE"] == state_found]

    resource_id = detect_id(query)

    def fmt(n):
        return f"{n:,.2f}"

    # --- SPECIAL UA HANDLING ---
    if (tehsil_found or district_found) and resource_id == "UA":
        ua_matched = matched[matched["ID"] == "UA"]
        matched = ua_matched
        if ua_matched.empty:
            loc = tehsil_found if tehsil_found else district_found
            return f"⚠ No UA data found for {loc}"

        loc = tehsil_found if tehsil_found else district_found
        responses = []
        for idx, row in ua_matched.iterrows():
            fresh_value = row["FRESH"] if not pd.isna(row["FRESH"]) else 0
            saline_value = row["SALINE"] if not pd.isna(row["SALINE"]) else 0

            if measure == "FRESH":
                responses.append(f"✅ UA FRESH in {loc} = {fmt(fresh_value)}")
            elif measure == "SALINE":
                responses.append(f"✅ UA SALINE in {loc} = {fmt(saline_value)}")
            else:
                responses.append(f"✅ UA in {loc}: Fresh = {fmt(fresh_value)}, Saline = {fmt(saline_value)}")

        return "\n".join(responses)

    if "TOTAL" in words and resource_id == "UA":
        ua_matched = df[df["ID"] == "UA"]
        if ua_matched.empty:
            return "⚠ No UA data found."

        responses = []
        for idx, row in ua_matched.iterrows():
            loc_name = row["TEHSIL"] if not pd.isna(row["TEHSIL"]) else row["DISTRICT"]
            fresh_value = row["FRESH"] if not pd.isna(row["FRESH"]) else 0
            saline_value = row["SALINE"] if not pd.isna(row["SALINE"]) else 0
            responses.append(f"✅ UA in {loc_name}: Fresh = {fmt(fresh_value)}, Saline = {fmt(saline_value)}")

        return "\n".join(responses)

    if resource_id:
        matched = matched[matched["ID"] == resource_id]

    if matched.empty:
        return "⚠ No matching data found."

    if "SALINE" in words and "NUMBER" in words and state_found:
        filtered_df = matched.copy()
        saline_df = filtered_df[filtered_df["SALINE"] > 0]
        district_names = saline_df["DISTRICT"].unique().tolist()
        count = len(district_names)

        if count == 0:
            return f"⚠ No districts with saline water found in {state_found}"

        return (
            f"✅ Total number of districts with saline water in {state_found}: {count}\n"
            f"📍 Districts: {', '.join(district_names)}"
        )

    if tehsil_found or district_found:
        loc = tehsil_found if tehsil_found else district_found

        total_fresh = matched["FRESH"].fillna(0).sum()
        total_saline = matched["SALINE"].fillna(0).sum()

        if measure == "FRESH":
            return f"✅ Total FRESH in {loc} = {fmt(total_fresh)}"
        if measure == "SALINE":
            return f"✅ Total SALINE in {loc} = {fmt(total_saline)}"

        return f"✅ Total water in {loc}: Fresh = {fmt(total_fresh)}, Saline = {fmt(total_saline)}"

    total_fresh = matched["FRESH"].fillna(0).sum()
    total_saline = matched["SALINE"].fillna(0).sum()
    location = state_found or "selected regions"

    if measure:
        total = matched[measure].fillna(0).sum()
        return f"✅ Total {measure} in {location} = {total:,.2f}"

    return f"✅ Total water in {location}: Fresh = {total_fresh:,.2f}, Saline = {total_saline:,.2f}"


def ask_csv(query: str) -> str:
    keyword_answer = answer_query_keyword(query)
    if keyword_answer:
        return keyword_answer

    if llama_agent is None:
        return "⚠ LLaMA agent not available. Only keyword-based search is supported."

    try:
        response = llama_agent.run(query)
        return f"🦙 LLaMA says: {response.strip()}"
    except Exception as e:
        return f"⚠ LLaMA query failed: {e}"


# -------------------------------------------------
# 🚀 FastAPI Setup
# -------------------------------------------------
app = FastAPI(title="Delhi Groundwater API", version="1.0")

# Allow frontend React (localhost:5173) to talk to backend
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
def home():
    return {"message": "Welcome to the Delhi Groundwater API 🚰"}


@app.post("/ask")
def ask(request: QueryRequest):
    result = ask_csv(request.query)
    return {"query": request.query, "answer": result}

#.venv\Scripts\activate (.venv) activation
#uvicorn backend1:app --reload --port 8001 (running command)