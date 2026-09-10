"""Portable FastAPI router. Serves frozen historical outputs; no hidden live fit."""
import json,os,re
from pathlib import Path
from functools import lru_cache
from fastapi import APIRouter,FastAPI,HTTPException,Query
from fastapi.responses import FileResponse

DATA_ROOT=Path(os.environ.get('FRONTWATCH_DATA_ROOT',str(Path(__file__).resolve().parents[2])))
router=APIRouter(tags=['FrontWatch historical research'])

@lru_cache(maxsize=24)
def artifact(name):
    path=DATA_ROOT/name
    if not path.is_file():raise HTTPException(503,'Frozen artifact missing: '+name)
    return json.loads(path.read_text(encoding='utf-8-sig'))

@router.get('/api/kr/demo')
def kr_demo():return artifact('10_KR_TARGET_DEMO.json')

@router.get('/api/kr/model-info')
def model_info():
    return {'model':artifact('06_KR_ADAPTER_MANIFEST.json'),'donor_fit':artifact('03_US_TO_KR_DONOR_FIT_RECEIPT.json'),
      'score_policy':artifact('08_SCORE_POLICY_FROZEN.json'),'explanation':artifact('13_MODEL_EXPLAINER_KO.json'),
      'limits':artifact('18_LIMITATIONS.json'),'scope':'HISTORICAL_REPLAY_NOT_LIVE','scientific_validation_pass':False}

@router.get('/api/kr/securities')
def securities(q:str=Query(default='',max_length=80),limit:int=Query(default=30,ge=1,le=200)):
    rows=artifact('cache/KR_LATEST_RESULTS.json');term=q.strip().casefold()
    selected=[r for r in rows if not term or term in r['security_code'] or term in r['name'].casefold()]
    return {'total_matches':len(selected),'items':[{k:r[k] for k in ('security_code','name','exchange','data_as_of')} for r in selected[:limit]],'lookup_semantics':'Name search only; analyze uses exact six-digit code'}

@router.get('/api/kr/analyze/{code}')
def analyze(code:str,date:str|None=Query(default=None,description='Exact supported historical YYYY-MM-DD; omitted=2023-12-28')):
    if not re.fullmatch(r'[0-9]{6}',code):raise HTTPException(422,'Six-digit exact Korean security code required')
    if date is not None:
        if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',date):raise HTTPException(422,'YYYY-MM-DD calendar date required')
        from datetime import date as calendar_date
        try:calendar_date.fromisoformat(date)
        except ValueError:raise HTTPException(422,'YYYY-MM-DD calendar date required')
    rows=artifact('cache/KR_LATEST_RESULTS.json')+artifact('cache/KR_DEMO_HISTORY.json')
    target=date or '2023-12-28'
    exact=[r for r in rows if r['security_code']==code and r['analysis_date']==target]
    if len(exact)!=1:raise HTTPException(404,{'reason':'EXACT_HISTORICAL_ROW_NOT_AVAILABLE','code':code,'date':target,'no_forward_fill':True,'no_live_fallback':True})
    return exact[0]

@router.get('/api/us/donor-demo')
def us_demo():return artifact('11_US_DONOR_DEMO.json')

@router.get('/api/us/research-summary')
def us_summary():return artifact('11_US_DONOR_DEMO.json')['research_summary']

@router.get('/api/transfer/audit')
def transfer_audit():return artifact('12_US_KR_TRANSFER_AUDIT_SUMMARY.json')

@router.get('/frontwatch',include_in_schema=False)
def frontwatch():return FileResponse(DATA_ROOT/'web/frontwatch.html')

def create_app():
    app=FastAPI(title='KR FrontWatch AI — Historical Research MVP',version='0.1.0-original-donor-research')
    app.include_router(router)
    return app

app=create_app()
