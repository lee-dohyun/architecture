#!/usr/bin/env bash
# data/{ko,en,ja,zh}.json 의 키가 4개 언어에서 고르게 존재하는지 확인한다.
#
# 왜: app.py 는 data/{lang}.json 을 그대로 읽어 Jinja 템플릿에 넘긴다. 템플릿이 참조하는 키가
# 특정 언어에 없으면 그 언어 화면에서 해당 문구가 **조용히 빈칸으로** 렌더링된다. 에러도 로그도 없다.
# 실제로 ko 6개 / en·ja·zh 2개가 빈칸으로 나가고 있었다(2026-08-21 발견).
#
# 오류(exit 1) = 템플릿이 참조하는데 없는 키. 정보 = 어느 언어엔 있으나 템플릿이 안 쓰는 키.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$PWD}" || exit 0
[ -f data/ko.json ] || exit 0

python3 - <<'PY'
import json, sys, os, re

LANGS = ("ko", "en", "ja", "zh")
TPL = "templates/index.html"
tpl = open(TPL, encoding="utf-8").read() if os.path.exists(TPL) else ""

def flat(o, p=""):
    if isinstance(o, dict):
        s = set()
        for k, v in o.items():
            s |= flat(v, f"{p}.{k}" if p else k)
        return s
    if isinstance(o, list):
        return {f"{p}[len={len(o)}]"}
    return {p}

docs, keys = {}, {}
for lang in LANGS:
    path = f"data/{lang}.json"
    if not os.path.exists(path):
        print(f"{path} 없음", file=sys.stderr); sys.exit(1)
    try:
        docs[lang] = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"{path} 파싱 실패: {e}", file=sys.stderr); sys.exit(1)
    keys[lang] = flat(docs[lang])

union = set().union(*keys.values())

def referenced(dotted):
    """templates/index.html 이 이 키를 참조하는가"""
    if not tpl:
        return True          # 템플릿을 못 읽으면 모두 참조된 것으로 보수적 취급
    base = re.sub(r"\[len=\d+\]$", "", dotted)
    return f"t.{base}" in tpl

errors, info = [], []
for k in sorted(union):
    missing = [l for l in LANGS if k not in keys[l]]
    if not missing:
        continue
    (errors if referenced(k) else info).append((k, missing))

for k, missing in errors:
    print(f"빈칸으로 렌더링됨 — 템플릿이 t.{k} 를 참조하는데 {'/'.join(missing)} 에 없습니다",
          file=sys.stderr)
for k, missing in info:
    print(f"  (정보) {k}: {'/'.join(missing)} 에 없으나 템플릿이 참조하지 않는 키입니다")

if errors:
    print(f"\n총 {len(errors)}개 키가 일부 언어에서 빈칸으로 나갑니다.", file=sys.stderr)
    sys.exit(1)
print(f"i18n 키 정상 (4개 언어, 템플릿 참조 키 전부 존재)")
PY
