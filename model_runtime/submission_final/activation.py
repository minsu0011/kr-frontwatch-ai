import numpy as np
FIELDS=['return_1d','return_3d','volume_acceleration','volatility_ratio','range_position20']
def activation(d):
    a=d[['activation__'+f for f in FIELDS]].to_numpy(float)
    count=np.isfinite(a).sum(axis=1);value=np.divide(np.nansum(a,axis=1)*100,count,out=np.full(len(d),np.nan),where=count==len(FIELDS))
    return value,np.where(value>=80,'HIGH',np.where(value>=60,'ELEVATED',np.where(np.isfinite(value),'LOW','UNKNOWN')))
