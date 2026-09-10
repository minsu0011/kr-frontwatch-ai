# 시장 연구에서 한국시장 웹 application으로

## 후보 선별과 최종 판단을 나눈 출발점

큰 시장 움직임을 찾는 것과 그 움직임의 의미를 판단하는 것은 다릅니다. Stage1은 upstream screening과 조사 우선순위, Stage2A는 activation 보조 역할입니다. 이후 Stage2B는 시장 특징과 공개 근거를 결합하는 연구로 이어졌습니다.

모든 단계를 독립적인 확률 모델처럼 더하지 않습니다. 같은 시장 움직임이나 같은 Evidence가 여러 단계에 나타나면 중복 가중이 될 수 있기 때문입니다.

## Stage2B Hybrid의 개발 이득과 검증 한계

미국 연구의 Hybrid 후보는 Market 특징과 Evidence3를 함께 사용했습니다. 개발 자료에서는 기본 시장 모델보다 나은 일부 결과가 있었지만, 재사용한 개발 평가와 최종 reserve는 별개입니다.

최종 reserve에서는 label 구성 때문에 필요한 대조가 성립하지 않았고, 이후 민감도 연구도 최종 독립 검증을 충족시키지 못했습니다. 이 결과를 숨기거나 웹 동작 성공으로 대체하지 않았습니다. 연구용 MVP 사용과 성능 인증을 분리했습니다.

## Stage3/4에서 근거와 가용성을 따로 다룸

공개 근거를 찾지 못한 경우는 근거가 없는 사건이라고 확정할 수 없습니다. 원문의 존재, 관측 시점, 자료 가용성, 중복 여부를 정리하고 deterministic router에서 출력 가능 범위를 결정하는 구조로 이어졌습니다.

Hybrid가 이미 Evidence3를 포함한다면 Evidence Engine을 독립 확률처럼 다시 가중합하면 안 됩니다. Stage1/2A 보조 신호와 Hybrid의 역할도 구분했습니다.

## 한국 label 부족과 donor 경계

미국 모델의 supervised 평가가 한국에서 그대로 성립한다고 볼 수 없었습니다. 한국 독립 사건 label과 coverage가 부족한 상태에서 미국 계수·확률을 직접 사용하는 대신, 한국 시계열 자체의 다변량 이상 정도를 보는 모델로 방향을 나눴습니다.

현재 한국 모델은 24개 특징의 Isolation Forest와 fitted adapter를 사용합니다. 미국 donor는 특징 방향의 참고 prior이며 한국 예측 정답이나 미국 확률의 복제가 아닙니다.

## 점수 의미를 API까지 유지

Risk·confidence·activation 등의 표시값은 검토 우선순위와 자료 해석을 위한 지수입니다. 화면에서 높은 지수를 확률처럼 읽지 않도록 모델 결과와 점수 정책, UI 설명을 연결했습니다.

웹은 고정 과거 결과를 읽는 cache-first 구조입니다. 요청 시 모델을 새로 학습하지 않고, 캐시 무결성을 확인한 뒤 FastAPI로 전달합니다. 선택적인 모델 replay는 정해진 과거 사례만 허용합니다.

## 현재 도달한 범위

과거 종목·이력·donor 참고·방법론을 한 application에서 읽는 연구용 MVP입니다. 실시간 추론이나 미래 성능이 인증된 서비스는 아닙니다. 미국 연구의 모든 Stage를 한국 runtime에서 순서대로 실행하는 구조도 아닙니다.

[단계별 역할](Model-Evolution.md) · [병목](Bottlenecks-and-Solutions.md) · [검증](Validation-and-Results.md)
