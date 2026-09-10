# 고정 모델과 replay

`submission_final`은 한국 특징 계산·adapter·Isolation Forest·표시 지수·재생 코드입니다. 24개 실제 모델 입력은 `contracts/06_KR_ADAPTER_MANIFEST.json`과 `original_features.py`를 함께 봅니다. `kr_features.py`의 보조 특징 목록을 24개 최종 입력 전체로 혼동하지 않습니다.

학습 바이너리에는 학습 분포의 참조값도 들어 있습니다. 원천 데이터와 재배포 조건이 확인되지 않아 가중치·특징 capsule·결과 캐시는 저장소에 포함하지 않습니다. 코드만으로 과거 학습 결과가 자동 생성되지는 않습니다.

권한 있는 자료에서 아래 파일을 이 디렉터리에 준비합니다.

- `06_KR_ADAPTER_FITTED.joblib`
- `07_KR_ISOLATION_FOREST.joblib`
- `cache/DEMO_FEATURE_CAPSULE.parquet`

`MODEL_RUNTIME_MANIFEST.json`은 각 파일의 크기와 SHA-256을 정의합니다. Joblib은 신뢰할 수 있는 출처의 파일만 사용합니다. 임의 파일을 불러오면 코드를 실행할 수 있습니다.

```bash
pip install -r requirements.txt -r requirements-model.txt
python -m pytest tests/test_model_source.py -q
python -m pytest tests/test_app.py tests/test_model_integration.py -q
```

통합 테스트에는 별도의 `data/final` 캐시도 필요합니다. API 모델 replay는 2023-12-28의 지정된 12개 사례만 허용하며, 결과가 고정 API와 맞지 않으면 응답을 거절합니다. 새 학습·실시간 예측은 수행하지 않습니다.
