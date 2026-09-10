# 소스와 배포

`main`에서 모델 구현, API, UI와 개발 문서를 함께 관리합니다. 모델은 `model_runtime/submission_final`, 웹은 `app`·`static`, 입력과 점수 계약은 `contracts`에 있습니다.

학습 바이너리·특징 capsule·결과 캐시는 별도 자료입니다. 배포 전에 지정된 manifest와 일치하는 파일을 공급해야 하며, 파일을 임의 생성하거나 누락을 새 예측으로 대체하지 않습니다. Git 소스 공개와 서비스 배포는 별도 절차입니다.
