"""Cache-first adapter of the Laptop submission_final/api.py contract; no inference."""
from collections import Counter
from datetime import date as calendar_date
import gzip
from hashlib import sha256
import json
from pathlib import Path
import re
from fastapi import APIRouter, HTTPException, Query

ROOT=Path(__file__).resolve().parents[1]
VERSION="KR_FRONTWATCH_SUBMISSION_FINAL"
STATE={}
router=APIRouter()
EXPECTED_KEYS={"latest","history","kr_demo","us","transfer","model","policy","donor","core",
               "explanation","limitations","demo_prelock","domain_gate","data_facts"}

def load_authority():
    manifest=json.loads((ROOT/"contracts/final_runtime_manifest.json").read_text(encoding="utf-8-sig"))
    if set(manifest["artifacts"])!=EXPECTED_KEYS:
        raise RuntimeError("Unexpected frozen runtime artifact set")
    artifacts={}
    for key,entry in manifest["artifacts"].items():
        expected_path="data/final/"+key+".json.gz"
        if entry["path"]!=expected_path:
            raise RuntimeError("Unexpected artifact path")
        compressed=(ROOT/expected_path).read_bytes()
        if sha256(compressed).hexdigest()!=entry["stored_sha256"]:
            raise RuntimeError("Stored authority hash mismatch")
        payload=gzip.decompress(compressed)
        if len(payload)!=entry["uncompressed_bytes"] or sha256(payload).hexdigest()!=entry["payload_sha256"]:
            raise RuntimeError("Payload authority hash mismatch")
        artifacts[key]=json.loads(payload.decode("utf-8-sig"))
    rows=artifacts["latest"]+artifacts["history"]
    index={(row["security_code"],row["analysis_date"]):row for row in rows}
    if len(index)!=len(rows):
        raise RuntimeError("Duplicate historical cache key")
    dates=dict(sorted(Counter(row["analysis_date"] for row in rows).items()))
    latest_dates={row["analysis_date"] for row in artifacts["latest"]}
    if len(latest_dates)!=1:
        raise RuntimeError("Ambiguous broad cache date")
    model=artifacts["model"];policy=artifacts["policy"]
    if model["model_SHA"]!=manifest["model_sha256"] or model["adapter_SHA"]!=manifest["adapter_sha256"]:
        raise RuntimeError("Model/adapter binding mismatch")
    if len(artifacts["kr_demo"]["rows"])!=12 or model["input_features"]!=24:
        raise RuntimeError("Frozen cohort/model geometry mismatch")
    return {"artifacts":artifacts,"index":index,"dates":dates,"latest_date":next(iter(latest_dates)),
            "manifest":manifest,"ready":True}

def artifact(key):
    if not STATE.get("ready"):
        raise HTTPException(503,{"reason":"FROZEN_REPLAY_NOT_READY"})
    return STATE["artifacts"][key]

def supported_date(value):
    target=value or STATE["latest_date"]
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}",target):
            raise ValueError()
        calendar_date.fromisoformat(target)
    except ValueError:
        raise HTTPException(422,{"reason":"INVALID_CALENDAR_DATE","date":target})
    if target not in STATE["dates"]:
        raise HTTPException(404,{"reason":"DATA_NOT_AVAILABLE_FOR_DATE","date":target,
                                "supported_dates":list(STATE["dates"]),
                                "no_forward_fill":True,"no_live_fallback":True})
    return target

@router.get("/api/kr/demo")
def kr_demo():
    return {**artifact("kr_demo"),"supported_dates":list(STATE["dates"]),
            "date_row_counts":STATE["dates"],"latest_broad_date":STATE["latest_date"],
            "model_status":"CONNECTED_FROZEN_KR_REPLAY","scientific_validation_pass":False}

@router.get("/api/kr/model-info")
def model_info():
    return {"model":artifact("model"),"donor_fit":artifact("donor"),"score_policy":artifact("policy"),
            "explanation":artifact("explanation"),"limits":artifact("limitations"),
            "data_facts":artifact("data_facts"),"product_mode":"HISTORICAL_RESEARCH_MVP",
            "kr_role":"TARGET_DOMAIN_ANOMALY_MODEL","us_role":"DONOR_RESEARCH",
            "kr_model_status":"CONNECTED_FROZEN_KR_REPLAY","kr_frozen_replay":True,
            "live_inference_enabled":False,"latest_broad_replay_date":STATE["latest_date"],
            "supported_dates":list(STATE["dates"]),"date_row_counts":STATE["dates"],
            "latest_cache_rows":len(artifact("latest")),"total_cached_code_date_rows":len(STATE["index"]),
            "authority_version":STATE["manifest"]["version"],
            "scientific_validation_pass":False,"production_qualified":False}

@router.get("/api/kr/securities")
@router.get("/api/kr/search")
def securities(q:str=Query(default="",max_length=80),limit:int=Query(default=30,ge=1,le=200),
               date:str|None=Query(default=None)):
    target=supported_date(date)
    term=q.strip().casefold()
    selected=[row for (code,day),row in STATE["index"].items()
              if day==target and (not term or term in code or term in row["name"].casefold())]
    return {"total_matches":len(selected),"date":target,
            "items":[{k:row[k] for k in ("security_code","name","exchange","data_as_of")} for row in selected[:limit]],
            "lookup_semantics":"Exact selected-date cache; name search is not an identifier join",
            "runtime_mode":"HISTORICAL_REPLAY"}

@router.get("/api/kr/analyze/{code}")
def analyze(code:str,date:str|None=Query(default=None),as_of:str|None=Query(default=None)):
    if not re.fullmatch(r"[0-9]{6}",code):
        raise HTTPException(422,{"reason":"EXACT_SIX_DIGIT_SECURITY_CODE_REQUIRED"})
    if date and as_of and date!=as_of:
        raise HTTPException(422,{"reason":"CONFLICTING_DATE_ARGUMENTS"})
    target=supported_date(date or as_of)
    row=STATE["index"].get((code,target))
    if row is None:
        raise HTTPException(404,{"reason":"SECURITY_NOT_AVAILABLE_FOR_DATE","code":code,"date":target,
                                "no_forward_fill":True,"no_live_fallback":True})
    return row

@router.get("/api/us/donor-demo")
def us_demo():
    return artifact("us")

@router.get("/api/us/research-summary")
def us_summary():
    return artifact("us")["research_summary"]

@router.get("/api/transfer/audit")
def transfer():
    return artifact("transfer")

@router.get("/api/methodology")
def methodology():
    return {"app_version":VERSION,"status":"CONNECTED_FROZEN_KR_REPLAY",
            "product_mode":"HISTORICAL_RESEARCH_MVP","model":artifact("model"),
            "score_policy":artifact("policy"),"donor":artifact("donor"),
            "explanation":artifact("explanation"),"limitations":artifact("limitations"),
            "latest_broad_date":STATE["latest_date"],"supported_dates":list(STATE["dates"]),
            "live_inference_enabled":False,"external_llm_used":False,
            "new_training_on_desktop":False,"new_threshold_tuning":False,
            "public_context":"EVIDENCE_UNAVAILABLE / neutral 50 / TIMING_AMBIGUOUS",
            "prospective_2023_validation":False,"scientific_validation_pass":False,
            "production_qualified":False,"us_scientific_qualification":artifact("us")["research_summary"]["scientific_qualification"]}
