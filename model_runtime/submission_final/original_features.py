"""Selected exact original DAILY_CORE formulas, strictly through previous session."""
import numpy as np,pandas as pd

def selected_formulas(g,features):
    c=g.Close;v=g.Volume;pc=c.shift();pv=v.shift();r=c.pct_change(fill_method=None).shift();out={}
    for f in features:
        if f=='pre_log_volume':z=np.log1p(pv.clip(lower=0))
        elif f.startswith('pre_ema_distance_'):
            w=int(f.split('_')[-1]);z=pc/pc.ewm(span=w,min_periods=max(2,w//2),adjust=False).mean()-1
        elif f.startswith('pre_sma_distance_'):
            w=int(f.split('_')[-1]);z=pc/pc.rolling(w,min_periods=max(2,w//2)).mean()-1
        elif f.startswith('pre_range_position_'):
            w=int(f.split('_')[-1]);lo=pc.rolling(w,min_periods=w//2).min();hi=pc.rolling(w,min_periods=w//2).max();z=(pc-lo)/(hi-lo).replace(0,np.nan)
        elif f.startswith('pre_logret_'):
            w=int(f.split('_')[-1]);ret=pc/pc.shift(w)-1;z=np.log1p(ret.where(ret>-1))
        elif f.startswith('pre_ret_'):
            w=int(f.split('_')[-1]);z=pc/pc.shift(w)-1
        elif f.startswith('pre_volume_mean_'):
            w=int(f.split('_')[-1]);z=pv.rolling(w,min_periods=max(3,w//2)).mean()
        elif f.startswith('pre_volume_median_'):
            w=int(f.split('_')[-1]);z=pv.rolling(w,min_periods=w//2).median()
        elif f=='pre_momentum_accel_5_20':z=(pc/pc.shift(5)-1)-(pc/pc.shift(20)-1)
        elif f.startswith('pre_trend_slope_'):
            w=int(f.split('_')[-1]);z=np.log(pc/pc.shift(w))/w
        elif f.startswith('pre_zero_return_ratio_'):
            w=int(f.split('_')[-1]);z=r.eq(0).rolling(w,min_periods=w//2).mean()
        elif f.startswith('absret_percentile_'):
            w=int(f.split('_')[-1]);z=r.abs().rolling(w,min_periods=max(5,w//2)).rank(pct=True)
        elif f.startswith('abs_tail_exceedance_count_'):
            w=int(f.split('_')[-1]);q=r.abs().rolling(60,min_periods=30).quantile(.95);z=(r.abs()>q).rolling(w,min_periods=max(5,w//2)).sum()
        else:raise ValueError('Unimplemented authoritative feature: '+f)
        out[f]=z
    return pd.DataFrame(out,index=g.index).replace([np.inf,-np.inf],np.nan)

def original_per_security(task):
    d,features=task;d=d.sort_values('Date');out=pd.DataFrame(index=d.index)
    # Segment horizon never admits a row to runtime before its own252 sessions.
    # Short segments cannot contain an eligible row; skip expensive calculations.
    pieces=[]
    for _,g in d.groupby('segment',sort=False):
        if len(g)<252:continue
        f=selected_formulas(g,features)
        for name in features:
            f['self__'+name]=f[name].rolling(253,min_periods=61).rank(pct=True)
            f['history_count__'+name]=f[name].shift().rolling(252,min_periods=1).count()
        pieces.append(f)
    if not pieces:return out
    return pd.concat(pieces)
