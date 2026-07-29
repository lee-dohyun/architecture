# architecture

leedohyun.com K3s 클러스터의 아키텍처를 시각화하는 Flask 웹앱. `architecture.leedohyun.com`에 배포됨.

## 개요

- `app.py`의 `architecture_data` 딕셔너리에 현재/과거 구조도 데이터를 하드코딩해두고, `templates/index.html`이 이를 렌더링
- 실제 클러스터 구성이 바뀔 때마다 `architecture_data`를 수동으로 갱신해야 함 (자동 수집 아님)

## 빠른 시작

```bash
pip install -r requirements.txt
python app.py            # http://localhost:5000
```

Docker:

```bash
docker build -t architecture-web .
docker run -p 5000:5000 architecture-web
```

## 배포

- CI: `.github/workflows/docker-image.yml` — `main` push 시 Docker Hub(`leedohyun1985/architecture-web`)로 이미지 빌드/푸시
- CD: 미구축, 수동 배포 (`kubectl set image deployment/architecture-web architecture-web=leedohyun1985/architecture-web:<sha> -n default`)
- K8s 매니페스트는 이 저장소가 아니라 `~/msa/architecture/`에 있음 (별도 관리)

## 문서

세부 설계/작업 기록은 [`docs/`](docs/) 폴더 참고.
