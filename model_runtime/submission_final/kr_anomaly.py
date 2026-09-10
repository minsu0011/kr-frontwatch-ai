import numpy as np
from sklearn.ensemble import IsolationForest
from .kr_adapter import ecdf

def fit_model(x):
    if not np.isfinite(x).all():raise ValueError('Incomplete features are not zero-filled')
    return IsolationForest(n_estimators=256,random_state=20260907,contamination='auto',n_jobs=6).fit(x)

def raw_anomaly(model,x):
    # Lower decision_function means more anomalous; negate before reference ECDF.
    out=np.full(len(x),np.nan);valid=np.isfinite(x).all(axis=1)
    if valid.any():out[valid]=-model.decision_function(x[valid])
    return out

def anomaly_percentile(model,x,reference):return 100*ecdf(reference,raw_anomaly(model,x))
