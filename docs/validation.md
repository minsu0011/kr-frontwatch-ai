# 재생 결과의 무결성

웹은 `contracts/final_runtime_manifest.json`, 선택적 모델 replay는 `model_runtime/MODEL_RUNTIME_MANIFEST.json`의 파일 크기·SHA-256을 확인합니다. 누락되거나 다른 파일이면 임의 결과로 대체하지 않습니다.

API 테스트는 종목·날짜 경계, 캐시·모델 출력의 일치와 상태를 확인합니다. 모델 테스트에는 지정된 학습 바이너리와 특징 capsule이 필요합니다. 실행 시 학습하지 않으며 고정 사례의 수치 일치를 독립 일반화 성능으로 해석하지 않습니다.
