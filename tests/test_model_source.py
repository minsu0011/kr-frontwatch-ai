import json
from pathlib import Path
import numpy as np
import pandas as pd

from model_runtime.submission_final.original_features import selected_formulas
from model_runtime.submission_final.kr_adapter import KRAdapter, ecdf, past_self
from model_runtime.submission_final.risk_index import risk_score, confidence, route

ROOT = Path(__file__).resolve().parents[1]


def test_exact_24_feature_contract_and_previous_session():
    contract = json.loads((ROOT / 'model_runtime/contracts/06_KR_ADAPTER_MANIFEST.json').read_text())
    names = contract['feature_names']
    assert len(names) == len(set(names)) == 24
    assert contract['training_cutoff'] == '2019-12-31'
    assert contract['reference_cutoff'] == '2020-12-31'
    data = pd.DataFrame({'Close': 100 + np.arange(400) * .1 + np.sin(np.arange(400)), 'Volume': 1000 + np.arange(400)})
    before = selected_formulas(data, names)
    changed = data.copy()
    changed.loc[300:, ['Close', 'Volume']] *= 10
    after = selected_formulas(changed, names)
    pd.testing.assert_frame_equal(before.loc[:300], after.loc[:300])
    assert before.shape == (400, 24)


def test_ecdf_ties_and_past_reference():
    np.testing.assert_allclose(ecdf([1., 2., 2., 4.], [0., 2., 5.]), [0., .5, 1.])
    data = pd.DataFrame({'history_count__x': [60., 59.], 'self__x': [31 / 61, .5]})
    values = past_self(data, 'x')
    assert values[0] == .5 and np.isnan(values[1])


def test_adapter_uses_fitted_distribution_without_refit():
    adapter = KRAdapter([{'feature': 'x', 'tier': 'A'}]).fit(pd.DataFrame({'x': [1., 2., 3., 4.]}))
    first, percent = adapter.transform(pd.DataFrame({'x': [2.5, np.nan]}))
    assert first[0, 0] == 0 and percent[0, 0] == .5
    assert np.isnan(first[1, 0]) and adapter.fit_rows == 4


def test_score_policy_and_abstention():
    assert risk_score(80, 20, 50, 50) == 60.5
    assert confidence(1, 252, 1, 20, 1, gate='UNSAFE') == 0
    assert confidence(1, 252, 1, 20, 1, gate='LIMITED') <= 75
    assert route(99, 44, 'LIMITED')[0] == 'ABSTAIN'
    assert route(99, 75, 'UNSAFE')[0] == 'ABSTAIN'
    assert route(70, 75, 'LIMITED')[0] == 'REVIEW_HIGH'
