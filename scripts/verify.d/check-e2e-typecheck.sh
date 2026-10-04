#!/usr/bin/env bash
# e2e/ (Playwright, architecture#11) 타입 검사. 네트워크·브라우저를 쓰지 않는다 — 테스트 실행 자체는 CI(e2e.yml)의 몫.
# 루트에 package.json 이 없어 scripts/verify.sh 의 Node 분기가 e2e/ 를 보지 못하므로 여기서 따로 건다.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)/e2e" 2>/dev/null || exit 0

if [ ! -d node_modules ]; then
  echo "check-e2e-typecheck: e2e/node_modules 없음 — 검사를 건너뜀(cd e2e && npm ci 후 다시)" >&2
  exit 0
fi
npx --no-install tsc -p . || { echo "check-e2e-typecheck: e2e/ 타입 오류" >&2; exit 1; }
