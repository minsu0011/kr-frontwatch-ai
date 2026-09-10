import numpy as np

def risk_score(anomaly,activation,donor_effective,public):
    return np.clip(.50*np.asarray(anomaly)+.15*np.asarray(activation)+.20*np.asarray(donor_effective)+.15*np.asarray(public),0,100)

def confidence(market,history,features,peer,domain,evidence=0.,timestamp=.25,gate='LIMITED'):
    c=100*(.25*np.asarray(market)+.20*np.minimum(np.asarray(history)/252,1)+.20*np.asarray(features)+.10*np.minimum(np.asarray(peer)/20,1)+.10*np.asarray(domain)+.10*np.asarray(evidence)+.05*np.asarray(timestamp))
    return np.where(np.asarray(gate)=='UNSAFE',0,np.minimum(c,np.where(np.asarray(gate)=='LIMITED',75.,100.)))

def route(score,conf,gate):
    if gate=='UNSAFE' or not np.isfinite(score) or not np.isfinite(conf) or conf<45:return 'ABSTAIN','데이터 부족'
    if score<35:return 'LOW','정상 범위'
    if score<55:return 'WATCH','관찰 필요'
    if score<70:return 'REVIEW','주의'
    return 'REVIEW_HIGH','위험 · 우선검토'
