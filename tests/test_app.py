import gzip
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.frozen_replay import ROOT,STATE,load_authority
from start import port_from_env

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:yield c

@pytest.mark.parametrize("path",["/","/kr","/us","/transfer","/methodology"])
def test_pages(client,path):
    r=client.get(path)
    assert r.status_code==200 and "KR FrontWatch" in r.text
    assert "PENDING_KR_FINAL_MODEL" not in r.text
    assert "2023" in r.text
    assert "script-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["x-content-type-options"]=="nosniff"

def test_health(client):
    d=client.get("/healthz").json()
    assert d["app_version"]=="KR_FRONTWATCH_SUBMISSION_FINAL"
    assert d["status"]=="ok" and d["kr_replay_ready"]
    assert d["kr_model_status"]=="CONNECTED_FROZEN_KR_REPLAY"
    assert not d["live_inference_enabled"] and d["public_data_hashes_verified"]

def test_actual_model(client):
    d=client.get("/api/kr/model-info").json()
    m=d["model"]
    assert m["input_features"]==24 and m["training_rows"]==m["reference_rows"]==100000
    assert m["model_params"]["n_estimators"]==256 and m["model_params"]["random_state"]==20260907
    assert m["training_cutoff"]=="2019-12-31" and m["reference_cutoff"]=="2020-12-31"
    assert [m["tier_counts"].get(t,0) for t in "ABCDE"]==[14,1,6,3,0]
    assert d["latest_cache_rows"]==2634 and d["total_cached_code_date_rows"]==2670
    assert d["date_row_counts"]=={"2023-03-31":12,"2023-06-30":12,"2023-09-27":12,"2023-12-28":2634}
    assert all(not d["donor_fit"][k] for k in ["US_coefficient_reused","US_calibration_reused","US_probability_reused"])
    assert d["score_policy"]["weights"]=={"KR_ANOMALY":.5,"ACTIVATION":.15,"DONOR_EFFECTIVE":.2,"PUBLIC_CONTEXT":.15}

CODES=["006800","033270","013360","019175","004370","002450","082210","019540","200230","105550","056080","071850"]

def test_demo_fixed_order(client):
    d=client.get("/api/kr/demo").json()
    assert [r["security_code"] for r in d["rows"]]==CODES
    assert d["row_count"]==12
    assert sum(r["exchange"]=="KOSPI" for r in d["rows"])==6

@pytest.mark.parametrize("code",CODES)
@pytest.mark.parametrize("date",["2023-03-31","2023-06-30","2023-09-27","2023-12-28"])
def test_every_demo_date_exact(client,code,date):
    r=client.get("/api/kr/analyze/"+code,params={"date":date})
    assert r.status_code==200
    assert r.json()==STATE["index"][(code,date)]
    if r.json()["risk_level"]=="ABSTAIN":
        assert r.json()["risk_index"] is None
    else:
        assert r.json()["risk_index"] is not None
    assert r.json()["confidence_index"]<=75

def test_full_cache_policy_consistency(client):
    from collections import Counter
    latest=STATE["artifacts"]["latest"]
    assert dict(Counter(r["risk_level"] for r in latest))=={"LOW":1008,"WATCH":839,"REVIEW":312,"REVIEW_HIGH":60,"ABSTAIN":415}
    for row in STATE["index"].values():
        assert row["alert_candidate"] is False
        assert row["evidence_route"]=="EVIDENCE_UNAVAILABLE"
        assert row["timing_state"]=="TIMING_AMBIGUOUS"
        assert row["public_context_term"]==50
        assert row["confidence_index"]<=75
        score=row["risk_index"]
        if row["domain_gate"]=="UNSAFE" or row["confidence_index"]<45:
            assert row["risk_level"]=="ABSTAIN"
            assert score is None
        else:
            expected=.5*row["kr_market_anomaly"]+.15*row["activation_index"]+.2*row["us_donor_support_effective"]+.15*row["public_context_term"]
            assert score==pytest.approx(expected,abs=1e-9)
            band="LOW" if score<35 else "WATCH" if score<55 else "REVIEW" if score<70 else "REVIEW_HIGH"
            assert row["risk_level"]==band
        assert not row["is_probability"] and not row["production_qualified"]

def test_broad_non_demo(client):
    row=next(x for x in STATE["artifacts"]["latest"] if x["security_code"] not in CODES and x["risk_index"] is not None)
    r=client.get("/api/kr/analyze/"+row["security_code"],params={"date":row["analysis_date"]})
    assert r.json()==row

def test_abstain_api(client):
    row=next(x for x in STATE["artifacts"]["latest"] if x["risk_level"]=="ABSTAIN")
    d=client.get("/api/kr/analyze/"+row["security_code"],params={"date":row["analysis_date"]}).json()
    assert d["risk_index"] is None and d["risk_label"]=="데이터 부족" and d["confidence_index"]==0

def test_hangul_search(client):
    d=client.get("/api/kr/securities",params={"q":"미래에셋증권","date":"2023-12-28"}).json()
    assert d["items"][0]["security_code"]=="006800"
    assert client.get("/api/kr/search",params={"q":"006800"}).json()["total_matches"]==1
    assert client.get("/api/kr/securities",params={"date":"2023-03-31","limit":200}).json()["total_matches"]==12

@pytest.mark.parametrize("day",["2026-09-07","2023-12-27","2021-12-31"])
def test_unsupported_date(client,day):
    r=client.get("/api/kr/analyze/006800",params={"date":day})
    assert r.status_code==404 and r.json()["detail"]["reason"]=="DATA_NOT_AVAILABLE_FOR_DATE"

@pytest.mark.parametrize("day",["2023-02-31","oops","23-1-1"])
def test_invalid_date(client,day):
    assert client.get("/api/kr/analyze/006800",params={"date":day}).status_code==422

@pytest.mark.parametrize("code",["abc","12345","1234567","００６８００"])
def test_invalid_code(client,code):
    assert client.get("/api/kr/analyze/"+code).status_code==422

def test_missing_code(client):
    r=client.get("/api/kr/analyze/999999",params={"date":"2023-12-28"})
    assert r.status_code==404 and r.json()["detail"]["reason"]=="SECURITY_NOT_AVAILABLE_FOR_DATE"

def test_no_date_fallback(client):
    assert client.get("/api/kr/analyze/000250",params={"date":"2023-03-31"}).status_code==404
    assert client.get("/api/kr/analyze/006800",params={"date":"2023-03-31","as_of":"2023-12-28"}).status_code==422

def test_us_authority(client):
    d=client.get("/api/us/donor-demo").json()
    assert d["row_count"]==len(d["rows"])==31
    s=client.get("/api/us/research-summary").json()
    assert s["full_research_event_rows"]==2098 and s["full_research_CIKs"]==31
    assert s["full_route_counts"]["WATCH"]==527 and s["full_route_counts"]["REVIEW"]==1571
    assert s["demo_route_counts"]=={"WATCH":3,"REVIEW":28} and s["scientific_qualification"]=="BLOCKED"

def test_transfer(client):
    d=client.get("/api/transfer/audit").json()
    assert sum(d["reported_handoff_metrics"]["Tier_counts"].values())==191
    assert [d["runtime_mapping"]["tier_counts"].get(t,0) for t in "ABCDE"]==[14,1,6,3,0]
    assert not d["is_KR_accuracy"] and not d["is_legal_probability"]

def test_methodology(client):
    d=client.get("/api/methodology").json()
    assert not d["prospective_2023_validation"] and not d["scientific_validation_pass"]
    assert not d["external_llm_used"] and not d["new_training_on_desktop"]

@pytest.mark.parametrize("path",["/.env","/Dockerfile","/requirements.txt","/docs","/openapi.json",
    "/data/final/latest.json.gz","/contracts/final_runtime_manifest.json","/static/../app/main.py"])
def test_no_source_exposure(client,path):
    assert client.get(path).status_code==404

def test_readonly(client):
    assert client.post("/api/kr/demo",json={}).status_code==405

def test_tamper_rejected(monkeypatch):
    original=Path.read_bytes
    def tamper(path):
        return b"tampered" if path==ROOT/"data/final/latest.json.gz" else original(path)
    monkeypatch.setattr(Path,"read_bytes",tamper)
    with pytest.raises(RuntimeError,match="hash mismatch"):load_authority()

def test_port(monkeypatch):
    monkeypatch.setenv("PORT","18772")
    assert port_from_env()==18772
