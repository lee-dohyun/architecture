# posselect E2E (Playwright)

실제 **배포된** posselect.com 서비스 간 흐름만 검증한다 — Test Pyramid 의 최상단(적게, 핵심 플로우만).
계층 정의와 저장소별 현황은 [`docs/2026-08-21-test-pyramid-strategy.md`](../docs/2026-08-21-test-pyramid-strategy.md).
(Storybook interaction test 는 Unit 에 가깝고 여기와 계층이 다르다.)

## 실행

```bash
cd e2e
npm ci
npx playwright install chromium     # 최초 1회
npm run test:smoke                  # 읽기 전용(기본). 운영에 아무것도 쓰지 않는다
E2E_ALLOW_WRITES=1 npm test         # + flow(장바구니). 운영 Redis 에 비로그인 장바구니를 만든다
npm run report                      # HTML 리포트
```

대상은 기본이 운영이다(개발 단계, 실사용자 트래픽 없음 — `~/msa/AGENTS.md` "현재 단계"). 스테이징이 생기면
`E2E_HOME_URL` / `E2E_PRODUCT_URL` / `E2E_CUSTOMER_URL` 만 바꿔 같은 스위트를 돌린다.

## 프로젝트

| 프로젝트 | 파일 | 쓰기 | 내용 |
|---|---|---|---|
| `smoke` | `*.smoke.spec.ts` | 없음 | 메인 렌더, 목록·더보기·검색, 상세(API 와 화면 일치), 비로그인 접근 제어 |
| `flow`  | `*.flow.spec.ts`  | 있음(`E2E_ALLOW_WRITES=1`) | 비로그인 장바구니 담기→표시→삭제, 재고 불변 |

CI(`.github/workflows/e2e.yml`)는 PR(e2e 변경 시)·매일 05:00 KST·수동으로 `smoke` 를 돌리고 리포트를 아티팩트로 남긴다.
`flow` 는 수동 실행에서 `allow_writes` 를 켰을 때만 돈다.

## 규칙

- **특정 상품 ID 를 하드코딩하지 않는다.** 공개 목록 API 에서 그때의 카탈로그를 읽어 쓴다(`tests/support/catalog.ts`). 시드가 바뀌어도 깨지지 않게.
- **예기치 않은 4xx/5xx 는 실패다.** 비로그인에서 정상적으로 4xx 를 내는 호출만 `tests/support/fixtures.ts` 의 허용 목록에 근거와 함께 적는다. 목록에 새 줄을 추가하려면 "왜 정상인가"를 주석으로 남길 것.
- **쓰기 테스트는 자기가 만든 것을 되돌린다**(`finally`). 장바구니는 빈 `cart:<CART_ID>` Redis 키(`{}`, TTL 30일)가 남는다 — 앱 API 로는 지울 수 없는 잔여물이다.
- 새 테스트가 통과하는 것만 보고 믿지 말 것. 대상 URL 을 일부러 어긋나게 해서(예: `E2E_PRODUCT_URL=https://customer.posselect.com`) **실패하는지** 확인한다.
- 로그인·주문 플로우는 아직 없다: 운영 자격증명을 CI 에 두는 방식(테스트 계정 Secret, SMS OTP 우회 여부)이 정해지지 않았다. 후속 이슈로 분리.
