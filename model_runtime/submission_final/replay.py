"""Re-score bundled KR feature capsule using only locally fitted trusted models."""
import json,argparse
from pathlib import Path
import numpy as np,pandas as pd,joblib
from .kr_adapter import ecdf
from .kr_anomaly import raw_anomaly
from .activation import activation
from .donor_support import donor_support
from .risk_index import risk_score,confidence,route

def replay(root):
    root=Path(root);bundle=joblib.load(root/'06_KR_ADAPTER_FITTED.joblib');model=joblib.load(root/'07_KR_ISOLATION_FOREST.joblib')
    d=pd.read_parquet(root/'cache/DEMO_FEATURE_CAPSULE.parquet');x,u=bundle['adapter'].transform(d)
    anomaly=100*ecdf(bundle['anomaly_reference'],raw_anomaly(model,x));act,_=activation(d)
    raw,dom,eff=donor_support(u,bundle['core'],d.history_sessions.to_numpy(),d.peer_size.to_numpy(),d.cross_section_size.to_numpy(),d.domain_gate.to_numpy())
    conf=confidence(d.bar_valid.to_numpy(float),d.history_sessions.to_numpy(),np.isfinite(x).mean(axis=1),d.peer_size.to_numpy(),dom,gate=d.domain_gate.to_numpy())
    risk=risk_score(anomaly,act,eff,50.)
    return sorted([{'security_code':r.Code,'analysis_date':str(r.Date.date()),'risk_index':float(risk[i]),'confidence_index':float(conf[i]),'kr_market_anomaly':float(anomaly[i]),'activation_index':float(act[i]),'us_donor_support_effective':float(eff[i]),'risk_level':route(risk[i],conf[i],r.domain_gate)[0]} for i,(_,r) in enumerate(d.iterrows())],key=lambda x:x['security_code'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);a=p.parse_args()
    print(json.dumps(replay(a.root),ensure_ascii=True,sort_keys=True,allow_nan=False))
