# 모델에서 화면까지

과거 한국 데이터의 24개 특징을 Isolation Forest와 fitted adapter로 처리하고 점수 정책에 따라 지수를 만듭니다. 고정 결과 캐시는 `app.frozen_replay`가 읽고 FastAPI가 정적 화면에 전달합니다.

미국 donor는 방향 참고이며 미국 계수·확률을 재사용하지 않습니다. 웹 요청 중 학습하지 않고 지정된 캐시의 SHA-256이 다르거나 파일이 누락되면 실행을 중단합니다.

모델 구현은 `model_runtime/submission_final`, 지정 사례 replay는 `app/model_bridge.py`에 있습니다. 학습 바이너리와 데이터는 이용 조건을 확인한 별도 자료로 준비합니다.
