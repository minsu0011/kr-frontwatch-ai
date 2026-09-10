# 과거 결과 replay 실행

```bash
pip install -r requirements.txt
python start.py
```

기본 포트는 10000이며 PORT 환경변수로 변경할 수 있습니다. 서버는 0.0.0.0에 바인딩하므로 외부 접근이 필요 없다면 방화벽과 실행 환경에서 접근을 제한합니다.

실행 전에 [final_runtime_manifest.json](../../contracts/final_runtime_manifest.json)의 `data/final/*.json.gz`를 준비합니다. 권한 있는 배포 자료와 일치해야 하며 임의의 다른 캐시로 대체하지 않습니다. 캐시가 없거나 해시가 다르면 시작 단계에서 중단합니다.

일반 웹 경로는 모델 학습 없이 고정 결과를 제공합니다. 선택적 모델 replay에는 `requirements-model.txt`의 환경과 지정 모델 파일이 추가로 필요합니다. 이 기능은 정해진 과거 사례 재생이며 임의 날짜·종목의 실시간 예측이 아닙니다.

읽는 순서는 [start.py](../../start.py), [main.py](../../app/main.py), [frozen_replay.py](../../app/frozen_replay.py), [static](../../static)입니다. API의 표시 지수는 투자 판단이나 사건 확률로 사용하지 않습니다.

`main`에는 모델·서비스·문서가 함께 있습니다. [모델 자료 준비](../../model_runtime/README.md) · [소스와 배포](../branches.md)
