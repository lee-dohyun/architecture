#!/usr/bin/env bash
# data/*.json 의 리스트 항목 중 템플릿이 **인덱스로 하드코딩해** 참조하는 것들이
# 실제로 전부 렌더링되는지 확인한다.
#
# 왜: templates/index.html 은 data.current.issues 를 `issues[0]`~`issues[N]` 처럼
# 개별 인덱스로 꺼내 탭별로 나눠 배치한다(문제점마다 들어갈 탭이 다르기 때문). 그래서
# JSON 에 항목을 append 해도 템플릿에 <li> 를 추가하지 않으면 **에러 없이 화면에서 사라진다.**
# check-i18n-keys.sh 는 언어 간 리스트 길이만 비교하므로 이 경우를 못 잡는다.
# 실제로 issues[8](Velero 오프사이트 사본 없음)·issues[9](레이트리밋/서킷브레이커)가
# 데이터에만 있고 어느 탭에도 안 나오고 있었다(2026-08-28 발견).
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$PWD}" || exit 0
[ -f data/ko.json ] || exit 0

python3 - <<'PY'
import json, os, re, sys

TPL = "templates/index.html"
if not os.path.exists(TPL):
    sys.exit(0)
tpl = open(TPL, encoding="utf-8").read()

# 템플릿이 인덱스로 참조하는 리스트: t.data.<경로>[<n>]
INDEXED = {"data.current.issues": "issues"}

bad = False
for path, token in INDEXED.items():
    used = {int(m) for m in re.findall(rf"{token}\[(\d+)\]", tpl)}
    doc = json.load(open("data/ko.json", encoding="utf-8"))
    node = doc
    for part in path.split("."):
        node = node[part]
    total = len(node)
    missing = sorted(set(range(total)) - used)
    if missing:
        bad = True
        print(f"{TPL}: {path} 의 인덱스 {missing} 가 템플릿에서 참조되지 않습니다 "
              f"— 그 항목은 어느 탭에도 렌더링되지 않고 조용히 사라집니다.", file=sys.stderr)
        for i in missing:
            print(f"  [{i}] {str(node[i])[:80]}", file=sys.stderr)
    out_of_range = sorted(i for i in used if i >= total)
    if out_of_range:
        bad = True
        print(f"{TPL}: {path}[{out_of_range}] 는 데이터 범위(0~{total-1})를 벗어납니다 "
              f"— 빈 <li> 로 렌더링됩니다.", file=sys.stderr)

if bad:
    sys.exit(1)
print("인덱스 참조 정상")
PY
