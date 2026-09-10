# 연구 계보와 현재 serving 구조

## 미국 연구 단계

| 단계 | 역할 | 다음 단계와의 경계 |
|---|---|---|
| Stage1 | 후보 선별·우선순위 | 최종 판단 확률이 아님 |
| Stage2A | 움직임 활성화 보조 | Hybrid에 숫자를 무조건 추가하지 않음 |
| Stage2B | Market + Evidence Hybrid | 개발 성과와 독립 reserve 검증 구분 |
| Stage3 / Evidence | 근거의 의미·시점·가용성 | 미수집을 음성으로 바꾸지 않음 |
| Stage4 | deterministic 출력 라우팅 | 앞 단계 실패를 인증 성공으로 바꾸지 않음 |

미국 Hybrid의 모델 카드에서는 Market raw16 + Evidence3의 19개 입력 열을 11개 변환 차원으로 다룹니다. 이 구조는 현재 한국의 24-feature 모델과 다릅니다. 두 모델을 동일한 최종 모델이라고 설명하지 않습니다.

## 한국 데이터 모델

과거 한국 시계열에서 계산한 특징을 Isolation Forest와 adapter로 처리합니다. 입력은 자기 이력·peer·시장 맥락의 이상 정도를 표현하며, 독립 사건 label을 충분히 갖춘 감독학습 사건 확률이 아닙니다.

미국 donor는 방향 참고입니다. 미국 학습 계수나 calibration을 한국시장에 재사용하지 않는 이유는 시장 구조·label·자료 coverage가 다르기 때문입니다.

## Serving 분리

```text
offline 특징·모델 계산 → 고정 결과와 점수 정책
                                  ↓
                           manifest 무결성 확인
                                  ↓
                  frozen_replay → FastAPI → browser
```

[app/frozen_replay.py](../../app/frozen_replay.py)가 결과를 읽고, [app/main.py](../../app/main.py)가 API와 정적 화면을 연결합니다. [app/model_bridge.py](../../app/model_bridge.py)는 선택적인 지정 사례 replay입니다.

`start.py`는 한 Uvicorn worker로 시작합니다. 일반 웹 의존성과 모델 의존성을 분리했고, 캐시가 없거나 맞지 않으면 임의 결과를 만들어 정상 응답하지 않습니다.

## 지수와 확률

`risk_index`, `confidence_index`, `activation_index` 등은 정책에 따른 표시 지수입니다. 높은 지수가 불법행위 가능성이나 미래 수익 확률인 것은 아닙니다. 데이터가 제한된 상태와 정상적인 상태도 구분해야 합니다.
