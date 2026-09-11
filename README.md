# KR FrontWatch AI

한국시장 종목의 과거 움직임을 자기 이력·동종 종목·시장 상태와 비교해 조사 우선순위를 보여주는 연구용 웹 application입니다. 시장 신호와 근거 자료를 구분하는 미국 연구에서 출발해, 한국 데이터에 맞는 모델·점수와 FastAPI·브라우저 화면으로 연결했습니다. 투자 추천이나 불법행위 확률을 제공하는 서비스는 아닙니다.

## 왜 단계를 나눴는가

가격 움직임이 크다는 것만으로 사건의 의미를 알 수 없고, 근거를 찾지 못했다고 정상 사례가 되는 것도 아닙니다. 후보 선별, 움직임과 공개 근거의 해석, 자료 품질에 따른 출력 결정을 나눠 다뤘습니다. 연구 단계에서 얻은 모든 모델을 하나의 점수로 더하지 않습니다.

## 사용 기술

Python, pandas, NumPy, scikit-learn의 Isolation Forest, FastAPI, Pydantic, Uvicorn, JavaScript, HTML/CSS를 사용합니다. 웹 serving은 가벼운 replay 경로이며 모델 의존성은 별도로 관리합니다.

## 데이터와 현재 모델 구조

한국시장 과거 시계열에서 계산한 24개 특징과 fitted adapter를 사용합니다. 자기과거·peer·시장 맥락의 특징을 한국 데이터의 분포에 맞춰 다루고, 미국 donor는 특징 방향을 참고하는 prior로만 사용합니다. 미국 모델의 회귀계수나 사건 확률을 한국시장에 직접 이식하지 않습니다.

```text
과거 한국 데이터 → 특징 / Isolation Forest / adapter → 점수 매핑
                                                     ↓
                                              고정 결과 캐시
                                                     ↓
                                               FastAPI → UI
```

점수는 검토 순서와 데이터 신뢰도를 표현합니다. 높은 지수가 법적 판단이나 사건 발생 확률이라는 뜻은 아닙니다.

## 개발 과정

### Stage1: 후보를 좁히는 연구

초기 단계는 조사할 시장 움직임의 후보와 우선순위를 만드는 역할입니다. 후보 선별과 최종 판정을 구분해야 이후 단계가 같은 신호를 반복 가중하지 않습니다.

### Stage2B: 시장 특징에 공개 근거 연결

미국 연구의 Hybrid는 시장 특징과 Evidence 특징을 결합했습니다. 개발 자료에서는 개선을 보였지만 최종 reserve의 label 구성과 근거 coverage가 충분하지 않아 독립 검증을 충족하지 못했습니다. 높은 개발 점수를 최종 인증으로 바꾸지 않고 연구용 한계를 남겼습니다.

### Stage3/4: 근거의 상태와 출력 라우팅

근거 자료의 존재·시점·가용성을 정리하고, 자료가 부족하거나 안전하지 않을 때 판단을 보류하는 deterministic 경로로 이어졌습니다. Evidence가 Hybrid에 이미 포함된 경우 이를 독립 확률처럼 다시 합산하지 않습니다. 이 단계들은 미국 연구 계보이며 아래 한국 모델과 동일한 학습기라는 뜻은 아닙니다.

### KR 모델·adapter: 데이터 부족을 다르게 다룸

한국의 충분한 독립 사건 label 없이 미국 감독학습 성능을 옮겨 주장할 수는 없었습니다. 그래서 한국 시계열 자체의 다변량 이상 정도를 Isolation Forest로 보고, 한국 adapter와 별도의 점수 매핑으로 연결했습니다. 미국 donor는 방향 참고로 남겼습니다.

### Scoring → API → UI

모델 결과와 웹 응답의 의미가 달라지지 않도록 고정 결과를 읽는 API를 구성했습니다. 캐시의 내용과 무결성을 확인한 뒤 종목·이력·방법론 화면으로 전달합니다. 선택적인 모델 replay도 정해진 과거 사례만 다루며 임의 날짜의 실시간 추론은 아닙니다.

## 주요 한계

현재 serving은 과거 결과 재생이며 실시간 추론·실행 중 재학습을 지원하지 않습니다. API/UI가 작동하는 것과 독립적인 탐지 성능 검증은 별개입니다. 미국 연구의 검증 실패, 한국 label 부족, 시점별 coverage와 자료 개정 문제를 해소한 production 모델은 아닙니다.

## 실행

```bash
pip install -r requirements.txt
python start.py
```

기본 포트는 10000입니다. 먼저 [runtime manifest](contracts/final_runtime_manifest.json)에 맞는 `data/final/*.json.gz`를 권한 있는 배포 자료에서 준비해야 합니다. 캐시가 없거나 맞지 않으면 실행을 중단하며 임의 예측을 만들지 않습니다. 모델 replay에는 추가 의존성과 지정된 모델 파일이 필요합니다.

모델 구현은 저장소에 포함되어 있습니다. 학습 artifact는 데이터 이용·재배포 조건을 확인해야 하므로 별도로 준비합니다. 상세 목록과 해시 검사는 [모델 실행 안내](model_runtime/README.md)를 따릅니다.

## 모델 코드를 읽는 순서

- [original_features.py](model_runtime/submission_final/original_features.py): 기존 DAILY_CORE 수식과 이전 session 특징
- [24-feature 계약](model_runtime/contracts/06_KR_ADAPTER_MANIFEST.json): 특징 순서·학습/참조 cutoff
- [kr_adapter.py](model_runtime/submission_final/kr_adapter.py): 학습 분포·자기 과거·peer·시장 기준의 변환
- [kr_anomaly.py](model_runtime/submission_final/kr_anomaly.py): Isolation Forest와 이상 정도
- [risk_index.py](model_runtime/submission_final/risk_index.py): 표시 지수와 보류 경계
- [replay.py](model_runtime/submission_final/replay.py), [model_bridge.py](app/model_bridge.py): 지정 사례의 모델 출력과 API 연결

일반 웹은 사전 결과 파일의 SHA-256을 확인한 뒤 읽습니다. 파일이 없거나 다르면 임의 결과로 대체하지 않고 실행을 중단합니다.

[app/main.py](app/main.py), [app/frozen_replay.py](app/frozen_replay.py), [static](static)이 서버에서 화면까지의 읽기 순서입니다.

[전체 개발 과정](https://github.com/minsu0011/kr-frontwatch-ai/wiki/Development-Journey) · [연구 단계와 현재 모델](https://github.com/minsu0011/kr-frontwatch-ai/wiki/Model-Evolution) · [병목과 해결](https://github.com/minsu0011/kr-frontwatch-ai/wiki/Bottlenecks-and-Solutions) · [검증과 한계](https://github.com/minsu0011/kr-frontwatch-ai/wiki/Validation-and-Results)

[Wiki 전체 보기](https://github.com/minsu0011/kr-frontwatch-ai/wiki) · [저장소 내 문서 사본](docs/wiki/Home.md)

[모델에서 화면까지: 코드 연결도](https://github.com/minsu0011/kr-frontwatch-ai/wiki/Architecture)
