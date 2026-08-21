# architecture AI 개발 지침

> **캐논 참조**: 이 저장소의 공통 개발 원칙(DB/트랜잭션/보안/배포 규칙 등)은 `~/msa/AGENTS.md`를 우선 따른다. 아래는 이 저장소만의 특이사항이다.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`architecture` (Docker Hub / K8s resource name: `architecture-web`) is a small Flask app that renders a
static architecture diagram for the leedohyun.com K3s cluster at `architecture.leedohyun.com`. It has no
database, no auth, and does not talk to the cluster API — it's a documentation page, not a monitoring tool.

## Commands

```bash
pip install -r requirements.txt
python app.py             # runs on :5000
```

```bash
docker build -t architecture-web .
docker run -p 5000:5000 architecture-web
```

CI (`.github/workflows/docker-image.yml`) builds and pushes `leedohyun1985/architecture-web:latest` and
`:<sha>` to Docker Hub on push to `main`. There is no test suite and no CD job — deployment to the cluster
is manual (`kubectl set image ... -n default`, see [gateway](../gateway) repo's CD jobs for the pattern this
repo doesn't yet have).

## Architecture

- Single file (`app.py`): a hardcoded Python dict `architecture_data` describes the cluster's services,
  domains, and status per section (`current`, and any historical snapshots). `templates/index.html` renders
  it; `static/` holds any CSS/JS/images.
- **This data does not update itself.** When the live cluster changes (new service, new domain, route
  change), `architecture_data` has to be edited by hand and redeployed, or the diagram silently goes stale.
  This has happened before — see `~/msa/CLAUDE.md` on this server for the 230-day-stale deployment incident
  this app was involved in (unrelated to data staleness, but same root cause: nothing enforces the diagram
  matches reality).
- Port 5000 inside the container; the K8s Service (`architecture-web-service`) maps 80→5000. There is a
  second, older Service (`architecture-web`, 80→80) left over from a previous nginx-based deployment — not
  used by the current image, do not confuse the two when touching K8s manifests.

## Related

- K8s manifests for this app live in `~/msa/architecture/` on the deployment host, not in this repo.
- [gateway](../gateway) routes `architecture.leedohyun.com` to this app's Service.

## Docs

Deeper design notes / work logs for specific changes go in [`docs/`](docs/), one file per topic.

