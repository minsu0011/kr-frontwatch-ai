"""Feature-specific fitted transformations; missing values remain NaN."""
import numpy as np

TIER_WEIGHT={'A':1.0,'B':.9,'C':.8,'D':.6,'E':0.0}
def ecdf(reference,value):
    ref=np.asarray(reference,dtype=float);v=np.asarray(value,dtype=float)
    if len(ref)==0:return np.full(v.shape,np.nan)
    out=(np.searchsorted(ref,v,side='left')+np.searchsorted(ref,v,side='right'))/(2*len(ref))
    return np.where(np.isfinite(v),out,np.nan)

def past_self(d,feature):
    # Cached average rank includes current. Remove its one observation exactly;
    # result is midrank ECDF against previous<=252 observations only.
    n=d['history_count__'+feature].to_numpy(float);rank=d['self__'+feature].to_numpy(float)
    return np.where(n>=60,(rank*(n+1)-1)/n,np.nan)

class KRAdapter:
    def __init__(self,features):self.features=features;self.statistics={};self.fit_rows=0
    def fit(self,d):
        self.fit_rows=len(d)
        for spec in self.features:
            f=spec['feature'];v=d[f].to_numpy(float);v=np.sort(v[np.isfinite(v)])
            if not len(v):raise ValueError('No observed training reference:'+f)
            q=np.quantile(v,[.25,.5,.75]);scale=float(q[2]-q[0]);self.statistics[f]={'median':float(q[1]),'IQR':scale if scale>1e-12 else 1.0,'constant_reference':scale<=1e-12,'ECDF':v}
        return self
    def transform(self,d):
        x=[];percent=[]
        for spec in self.features:
            f=spec['feature'];tier=spec['tier'];r=self.statistics[f]
            if tier=='E':raise ValueError('TierE forbidden in runtime')
            if tier=='A':
                raw=d[f].to_numpy(float);value=(raw-r['median'])/r['IQR'];u=ecdf(r['ECDF'],raw)
            elif tier=='B':value=d['market__'+f].to_numpy(float);u=value
            elif tier=='C':value=past_self(d,f);u=value
            elif tier=='D':value=d['peer__'+f].to_numpy(float);u=value
            else:raise ValueError('Unknown transfer tier')
            x.append(value);percent.append(u)
        return np.column_stack(x).astype('float32'),np.column_stack(percent)

def hash_sample(d,n,namespace):
    import hashlib
    hashes=[hashlib.sha256((namespace+'|'+str(code)+'|'+str(day.date())).encode()).hexdigest() for code,day in zip(d.Code,d.Date)]
    order=np.argsort(np.asarray(hashes),kind='stable')[:min(n,len(d))]
    return d.iloc[order].copy(),[hashes[i] for i in order]
