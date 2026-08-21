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

- **The content lives in `data/{ko,en,ja,zh}.json`, not in `app.py`.** (This used to be a hardcoded
  `architecture_data` dict inside `app.py`; the i18n conversion on 2026-08-16 moved it out and the dict no
  longer exists.) `app.py` is now a thin loader: `load_lang_data(lang)` reads one JSON file and hands it to
  `templates/index.html` as `t`, plus `t.data` again as `data`. Routes: `/` → ko, `/<lang>/` for the four
  supported languages (unknown language redirects to ko), and `/api/architecture?lang=`, `/api/status`.
- Each language file has exactly three top-level keys, and they are **not interchangeable**:
  - `ui` — UI chrome strings (tab labels, status badges, headings). Template references look like `t.ui.*`.
  - `data` — the cluster content itself (`current`, `domain_split`, `resources`, `improved`, `roadmap`,
    `updated_at`).
  - `mermaid` — six diagram bodies (`posselect`, `leedohyun`, `infra`, `domainsplit`, `improved`,
    `roadmap`). **The `graph TB` / `graph LR` directive is hardcoded by `templates/index.html`** inside
    `<div class="mermaid">`, so the JSON value must *not* start with one — the diagram's direction is a
    template decision, not data. Putting a directive in the data duplicates it and breaks rendering.
- **Two silent failure modes** — neither produces an error, a log line, or a CI failure:
  1. A key the template references (`t.something`) that is missing from one language renders as an **empty
     string** in that language only. Six keys were shipping blank in ko and two in en/ja/zh before this was
     caught (2026-08-21).
  2. A mermaid body whose brackets got truncated by a careless string replacement only fails **in the
     browser**, at render time. Nothing server-side notices.
  Both are checked mechanically by the hooks below — run them after any `data/*.json` edit.
- **This data does not update itself.** When the live cluster changes (new service, new domain, route
  change), all four language files have to be edited by hand and redeployed, or the diagram silently goes
  stale. Editing only `ko.json` is the common half-done case — the other three then disagree with reality.
  See `~/msa/CLAUDE.md` on this server for the 230-day-stale deployment incident this app was involved in
  (a different mechanism, same root cause: nothing enforces the diagram matches reality).
- Port 5000 inside the container; the K8s Service (`architecture-web-service`) maps 80→5000. There is a
  second, older Service (`architecture-web`, 80→80) left over from a previous nginx-based deployment — not
  used by the current image, do not confuse the two when touching K8s manifests.
- `build_static.py` renders the same Flask app to a static mirror for GitHub Pages
  (`.github/workflows/pages-deploy.yml` runs it). It is not one-off scaffolding — keep it working when
  changing routes or template links.

## Claude Code wiring

- **`.claude/hooks/check-i18n-keys.sh`** — compares the key sets of the four language files against what
  `templates/index.html` actually references. Exits non-zero for a referenced key missing in some language
  (i.e. one that will render blank); merely reports keys that exist but the template never uses.
- **`.claude/hooks/check-mermaid.sh`** — bracket-pair integrity of every `mermaid` block, plus two things
  that are easy to get wrong: a `graph TB`-style directive leaking into the data, and a block the template
  never references.
- Both run automatically as `PostToolUse` hooks after any `data/*.json` edit (see `.claude/settings.json`),
  and both work standalone. Run them before pushing — CI does not.

## Related

- K8s manifests for this app live in `~/msa/architecture/` on the deployment host, not in this repo.
- [gateway](../gateway) routes `architecture.leedohyun.com` to this app's Service.

## Docs

Deeper design notes / work logs for specific changes go in [`docs/`](docs/), one file per topic.

