# architecture

leedohyun.com K3s 클러스터의 아키텍처를 시각화하는 Flask 웹앱. `architecture.leedohyun.com`에 배포됨.

## 개요

- 구조도 데이터는 `data/{ko,en,ja,zh}.json` 4개 파일에 있고, `app.py`는 요청 언어에 맞는 파일을 읽어 `templates/index.html`에 넘기는 얇은 로더다 (2026-08-16 다국어 전환 이전에는 `app.py` 안의 `architecture_data` 딕셔너리였으나 지금은 없음)
- 언어별 URL: `/`(=ko), `/en/`, `/ja/`, `/zh/`. JSON 파일 하나는 `ui`(UI 문구) / `data`(구조도 내용) / `mermaid`(다이어그램 6종) 세 부분으로 구성
- 실제 클러스터 구성이 바뀌면 **4개 언어 파일을 전부** 수동으로 갱신해야 함 (자동 수집 아님). 한 언어에만 있는 키는 다른 언어 화면에서 에러 없이 빈칸으로 렌더링되므로, 편집 후 `.claude/hooks/check-i18n-keys.sh`와 `.claude/hooks/check-mermaid.sh`로 확인할 것
- `build_static.py`는 같은 앱을 정적 미러로 렌더해 GitHub Pages에 올린다 (`.github/workflows/pages-deploy.yml`)

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
