"""No matched PIT-authorized local KR disclosure universe is currently available."""
TERMS={'PUBLIC_EXPLANATION_STRONG':20.,'PUBLIC_EXPLANATION_PARTIAL':40.,'UNEXPLAINED_WITH_AVAILABLE_EVIDENCE':70.,'EVIDENCE_INSUFFICIENT':50.,'EVIDENCE_UNAVAILABLE':50.}
def context(code,analysis_date):
    return {'evidence_route':'EVIDENCE_UNAVAILABLE','public_context_term':50.,'evidence':[],'timing_state':'TIMING_AMBIGUOUS','exact_public_timestamp':None,'market_anomaly_start_time':None,'verified_pre_public':False,'reason':'NO_EXACT_CODE_DATE_PIT_SOURCE_AUTHORITY;2024_KIND_DOCUMENT_NOT_BACKFILLED_INTO2023'}
