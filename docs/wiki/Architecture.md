# 모델에서 화면까지

미국 시장 연구는 특징과 근거를 어떻게 나눌지 탐색한 출발점입니다. 한국 runtime은 별도로 맞춘 24개 특징의 비지도 모델입니다. 미국 Stage1→Stage2B→Stage3/4를 한국 API가 차례로 실행하는 구조는 아닙니다.

## 두 실행 경로

```text
한국 과거 OHLCV
  → 이전 거래일까지의 24개 특징 → 한국 분포 adapter
  → Isolation Forest + activation + donor 방향 참고
  → 점수·confidence·보류 정책 → 고정 결과 캐시
                                  ↓
                     manifest 확인 → FastAPI → 화면

선택적 재생: 고정 12개 사례의 특징 capsule + fitted 모델
  → replay → model_bridge의 해시·캐시 일치 확인 → API
```

일반 웹 요청은 이미 계산한 과거 캐시를 읽습니다. 선택적 재생도 2023-12-28의 지정 사례만 지원하며, 임의 종목·날짜의 실시간 추론이나 학습 기능은 아닙니다.

## 코드별 역할

| 코드·설정 | 무엇을 하는가 |
|---|---|
| [original_features.py](../../model_runtime/submission_final/original_features.py) | DAILY_CORE에서 선택한 수식을 이전 거래일까지 계산 |
| [06_KR_ADAPTER_MANIFEST.json](../../model_runtime/contracts/06_KR_ADAPTER_MANIFEST.json) | 정확한 입력 24개와 순서, 학습·기준 분포의 cutoff 기록 |
| [05_PORTABLE_FEATURE_CORE.json](../../model_runtime/contracts/05_PORTABLE_FEATURE_CORE.json) | 특징별 전이 등급과 방향 참고 정의 |
| [kr_adapter.py](../../model_runtime/submission_final/kr_adapter.py) | 한국 학습 분포·시장·자기 이력·peer 기준 변환 |
| [kr_anomaly.py](../../model_runtime/submission_final/kr_anomaly.py) | 256개 트리의 Isolation Forest와 기준 분포상 이상 순위 |
| [activation.py](../../model_runtime/submission_final/activation.py) | 움직임 활성화 보조 지수 |
| [donor_support.py](../../model_runtime/submission_final/donor_support.py) | 미국 연구의 방향 참고를 자료 가용성과 함께 제한적으로 반영 |
| [risk_index.py](../../model_runtime/submission_final/risk_index.py) | 표시 점수, confidence와 보류·검토 단계 결정 |
| [replay.py](../../model_runtime/submission_final/replay.py) | 신뢰할 수 있는 fitted 모델과 고정 특징 capsule로 사례 재생 |
| [app/model_bridge.py](../../app/model_bridge.py) | 파일 해시 및 기존 API 결과와의 수치 일치를 확인한 후 연결 |
| [app/frozen_replay.py](../../app/frozen_replay.py) | 일반 웹에서 고정 결과 캐시 제공 |
| [app/main.py](../../app/main.py) · [static](../../static) | API와 화면 |

`kr_features.py`의 보조 수식 목록을 최종 24개 입력 계약으로 대신하지 않습니다. 실제 입력 순서는 다음과 같습니다.

```text
pre_ema_distance_10, pre_range_position_20,
abs_tail_exceedance_count_20, pre_logret_20,
pre_log_volume, pre_ema_distance_20,
pre_range_position_60, absret_percentile_20,
pre_ret_20, pre_volume_mean_20,
pre_ema_distance_60, absret_percentile_60,
pre_ret_40, pre_volume_mean_5,
pre_momentum_accel_5_20, pre_volume_mean_60,
pre_sma_distance_20, pre_volume_median_20,
pre_sma_distance_60, pre_volume_median_60,
pre_trend_slope_20, pre_zero_return_ratio_20,
pre_sma_distance_10, pre_zero_return_ratio_60
```

## 분포 변환과 시간 경계

최종 구성은 A 14개, B 1개, C 6개, D 3개이며 E는 없습니다. A는 fitted median/IQR, B는 같은 날짜 시장 순위, C는 이전 자기 이력의 ECDF, D는 같은 날짜 peer 순위를 사용합니다. 자기 이력은 이전 최대 252개 관측 중 최소 60개를 요구합니다. Peer는 거래소·시가총액·유동성·가격 구간을 사용하고 관측 peer가 20개 미만이면 거래소 기준으로 돌아갑니다. 같은 날짜 단면 정보는 장 종료 후 판단에만 사용합니다.

계약의 한국 비지도 학습 자료는 100,000행, cutoff는 2019-12-31입니다. 이상 순위의 기준 자료는 별도 100,000행이며 cutoff는 2020-12-31입니다. 이 과거 cutoff가 2023년 당시 사전 고정된 전향적 검증을 뜻하지는 않습니다.

## 점수는 확률이 아님

Risk는 `0.50 × anomaly + 0.15 × activation + 0.20 × donor_effective + 0.15 × public_context`를 0~100으로 제한한 지수입니다. 지정 사례 replay에서는 public context에 중립값 50을 사용합니다. Confidence가 45 미만이거나 입력이 유효하지 않거나 UNSAFE이면 보류합니다. LIMITED에서는 confidence 상한이 75입니다.

미국 계수나 사건 확률을 한국으로 복사한 모델이 아니며, 독립 사건 label을 갖춘 한국 감독학습 검증도 아닙니다. 모델 파일과 캐시는 별도 자료입니다. 파일이 없거나 해시가 맞지 않으면 임의 결과로 대체하지 않습니다.

[실행 안내](How-to-Run.md) · [검증과 한계](Validation-and-Results.md) · [연구 계보](Development-Journey.md)
