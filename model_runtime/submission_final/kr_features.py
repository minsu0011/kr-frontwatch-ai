"""Causal public OHLCV formulas from the existing cross-market17 contract.

This module constructs candidates only; it does not assign unverified transfer
tiers or donor directions. No model scores/labels are accepted as inputs.
"""
import numpy as np
import pandas as pd

FEATURES=['log_volume_median60','log_local_value_median60','zero_volume_fraction60','realized_volatility20','realized_volatility60','short_vol_minus_long_vol','momentum20','momentum60','intraday_range20','amihud20_local','amihud60_local','volume_shock20_60','drawdown60','return_iqr20','gap_median20']
FAMILIES={'log_volume_median60':'LIQUIDITY','log_local_value_median60':'LIQUIDITY','zero_volume_fraction60':'LIQUIDITY','realized_volatility20':'VOLATILITY','realized_volatility60':'VOLATILITY','short_vol_minus_long_vol':'VOLATILITY','momentum20':'TREND','momentum60':'TREND','intraday_range20':'VOLATILITY','amihud20_local':'LIQUIDITY','amihud60_local':'LIQUIDITY','volume_shock20_60':'LIQUIDITY','drawdown60':'TREND','return_iqr20':'ROBUST_DISTRIBUTION_V2','gap_median20':'RETURNS'}

def per_security(d):
    d=d.sort_values('Date').copy();d['session_index']=np.arange(len(d))
    # A gap in the complete market's session index identifies absent sessions;
    # no synthetic 2021 sessions, relisting splice or zero-price interpolation.
    breaks=d.market_session.diff().ne(1)|d.exchange.ne(d.exchange.shift())|d.year.diff().gt(1)|(~d.bar_valid)|(~d.bar_valid.shift(fill_value=False))
    d['segment']=breaks.cumsum();parts=[]
    for _,g in d.groupby('segment',sort=False):
        q=g.copy();c=q.Close.where(q.bar_valid);v=q.Volume.where(q.bar_valid);o=q.Open.where(q.bar_valid);h=q.High.where(q.bar_valid);l=q.Low.where(q.bar_valid)
        ret=c.pct_change(fill_method=None);value=c.abs()*v;intr=(h-l)/c.abs();gap=(o/c.shift()-1).abs();amihud=ret.abs()/value.where(value>0)
        q['log_volume_median60']=np.log1p(v.rolling(60,min_periods=60).median());q['log_local_value_median60']=np.log1p(value.rolling(60,min_periods=60).median())
        q['zero_volume_fraction60']=v.eq(0).where(v.notna()).rolling(60,min_periods=60).mean()
        q['realized_volatility20']=ret.rolling(20,min_periods=20).std(ddof=1);q['realized_volatility60']=ret.rolling(60,min_periods=60).std(ddof=1);q['short_vol_minus_long_vol']=q.realized_volatility20-q.realized_volatility60
        q['momentum20']=c/c.shift(20)-1;q['momentum60']=c/c.shift(60)-1
        q['intraday_range20']=intr.rolling(20,min_periods=20).median();q['amihud20_local']=amihud.rolling(20,min_periods=20).median();q['amihud60_local']=amihud.rolling(60,min_periods=60).median()
        q['volume_shock20_60']=np.log1p(value.rolling(20,min_periods=20).median())-np.log1p(value.rolling(60,min_periods=60).median())
        q['drawdown60']=c/c.rolling(60,min_periods=60).max()-1
        q['return_iqr20']=ret.rolling(20,min_periods=20).quantile(.75)-ret.rolling(20,min_periods=20).quantile(.25)
        q['gap_median20']=gap.rolling(20,min_periods=20).median()
        q['return_1d']=ret;q['return_3d']=c/c.shift(3)-1;q['range_position20']=(c-l.rolling(20,min_periods=20).min())/(h.rolling(20,min_periods=20).max()-l.rolling(20,min_periods=20).min()).replace(0,np.nan)
        q['volume_acceleration']=v/v.rolling(20,min_periods=20).median();q['volatility_ratio']=q.realized_volatility20/q.realized_volatility60.replace(0,np.nan)
        q['history_sessions']=np.arange(1,len(q)+1)
        q['price_limit_proxy']=ret.abs().ge(.295)
        # Not a CA detector: observed discontinuity is only a conservative unsafe proxy.
        q['mechanics_discontinuity']=ret.abs().gt(.32)|gap.gt(.32)
        q['recent_mechanics_ambiguity']=q.mechanics_discontinuity.rolling(252,min_periods=1).max().astype(bool)
        for f in FEATURES:
            # Window excludes current value; normalized reference has at most252 past sessions.
            # rolling rank over previous252 plus current is equivalent midpoint ECDF
            # and avoids exposing future values. Ties explicitly midpoint-adjusted later.
            q['self__'+f]=q[f].rolling(253,min_periods=61).rank(pct=True)
            q['history_count__'+f]=q[f].shift().rolling(252,min_periods=1).count()
        parts.append(q)
    return pd.concat(parts,ignore_index=True)
