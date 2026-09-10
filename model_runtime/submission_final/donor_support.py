"""No direction authority means no directional donor contribution, never guessed signs."""
import numpy as np
from .kr_adapter import TIER_WEIGHT

def donor_support(u,specs,history,peer,cross_section,gate):
    weights=np.asarray([TIER_WEIGHT[s['tier']]*({'STABLE':1.,'CONDITIONAL':.75,'WEAK':.4}.get(s['family_stability'],0.)) if s.get('direction') in [-1,1] and s.get('direction_authority_SHA') else 0. for s in specs])
    signs=np.asarray([s.get('direction') or 0 for s in specs]);valid=np.isfinite(u)&(weights>0);numer=np.where(valid,np.where(signs>0,u,1-u)*weights,0.).sum(axis=1);denom=np.where(valid,weights,0.).sum(axis=1)
    raw=np.divide(100*numer,denom,out=np.full(len(u),np.nan),where=denom>0)
    total=weights.sum();observed=np.divide(denom,total,out=np.zeros(len(u)),where=total>0)
    tier_quality=sum(TIER_WEIGHT[s['tier']] for s in specs)/len(specs)
    domain=np.clip(observed*(.30+.20*tier_quality+.20*np.minimum(history/252,1)+.15*np.minimum(peer/20,1)+.15*np.minimum(cross_section/100,1))*np.where(np.asarray(gate)=='LIMITED',.75,np.where(np.asarray(gate)=='VERIFIED',1.,0.)),0,1)
    effective=np.where(np.isfinite(raw),raw*domain,0.)
    return raw,domain,effective
