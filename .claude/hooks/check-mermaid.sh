#!/usr/bin/env bash
# data/*.json 의 mermaid 정의 무결성을 확인한다.
#
# 왜: 부분 문자열 치환으로 노드 라벨이 잘린 채 커밋된 사례가 반복됐다. 렌더링은 브라우저에서만
# 실패하므로 CI/테스트로는 드러나지 않는다.
# 주의: `graph TB`/`graph LR` 지시자는 templates/index.html 이 <div class="mermaid"> 안에
# 하드코딩해 주입한다. 따라서 JSON 값 자체에는 지시자가 없는 것이 정상이며, 다이어그램 방향은
# 데이터가 아니라 템플릿이 결정한다.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$PWD}" || exit 0

python3 - <<'PY'
import json, glob, re, sys, os

bad = False
tpl = ""
if os.path.exists("templates/index.html"):
    tpl = open("templates/index.html", encoding="utf-8").read()

for path in sorted(glob.glob("data/*.json")):
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"{path}: JSON 파싱 실패 — {e}", file=sys.stderr); bad = True; continue

    blocks = doc.get("mermaid")
    if not isinstance(blocks, dict):
        continue
    for name, src in blocks.items():
        if not isinstance(src, str):
            continue
        # 괄호 짝: 부분 치환으로 노드 라벨이 잘린 경우를 잡는다
        for o, c in (("[", "]"), ("(", ")"), ("{", "}")):
            if src.count(o) != src.count(c):
                print(f"{path} :: {name} — '{o}{c}' 짝 불일치 ({src.count(o)} vs {src.count(c)}) "
                      f"— 노드 라벨이 잘렸을 수 있습니다", file=sys.stderr)
                bad = True
        # 지시자가 데이터에 들어오면 템플릿의 것과 중복되어 렌더링이 깨진다
        head = src.strip().splitlines()[0].strip() if src.strip() else ""
        if re.match(r'^(graph|flowchart)\s+(TB|TD|LR|RL|BT)\b', head):
            print(f"{path} :: {name} — 데이터에 '{head}' 지시자가 있습니다. "
                  f"지시자는 templates/index.html 이 주입하므로 중복됩니다", file=sys.stderr)
            bad = True
        # 템플릿이 이 블록을 실제로 참조하는지
        if tpl and f"t.mermaid.{name}" not in tpl:
            print(f"{path} :: {name} — templates/index.html 이 참조하지 않는 미사용 블록입니다",
                  file=sys.stderr)
            bad = True
if bad:
    sys.exit(1)
print("mermaid 정의 정상")
PY
