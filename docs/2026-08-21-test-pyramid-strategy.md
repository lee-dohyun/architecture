# Test Pyramid 전략

## 배경

architecture#14(TDD 도입 및 Test Pyramid 전략 수립, 장기 개선)와 posselect-shell#26(통합 테스트 표준 —
Testcontainers 실DB 검증 체계)에서 도출. posselect #211(재고 차감 멱등성)에서 Mockito 단위 테스트 5건이
전부 통과했는데도 `readOnly` 트랜잭션 전파 버그를 놓쳐 배포 후 롤백한 사례가 계기 — 트랜잭션 전파·
멱등성·Flyway 마이그레이션·DB 제약은 단위 테스트만으로는 못 잡는 구조적 사각지대다.

## 계층 구조

```
    ▲  E2E (Playwright)              — 적게, 핵심 플로우(로그인→장바구니→주문 등)만
   ▲▲  Integration (Testcontainers)   — 서비스 경계 검증 (DB/Redis/MinIO 실제 컨테이너)
  ▲▲▲  Unit (Vitest / JUnit 5)        — 가장 많이, 도메인 로직/순수 함수
```

- **Unit**: 프론트엔드는 Vitest, 백엔드는 JUnit 5 + Mockito. 순수 로직(가격 계산, 소유권 검사, 포맷팅 등)과
  React 컴포넌트 단위. 가장 빠르고 가장 많아야 하는 계층.
- **Integration**: Testcontainers로 실제 Postgres(필요시 Redis/MinIO)를 띄워 리포지토리·서비스 계층을 검증.
  트랜잭션 전파/롤백, 멱등성(같은 키 2회 호출 → 1회만 반영), Flyway 마이그레이션 적용, CHECK/유니크 제약
  동작 — 이 4가지가 posselect #211에서 실제로 놓쳤던 사각지대이며 Integration 계층의 필수 커버 대상이다.
  **이 계층은 단위 테스트로 대체될 수 없다** — `~/msa/AGENTS.md` §3 "트랜잭션 / 정합성" 참고.
- **E2E**: Playwright. 핵심 사용자 플로우(로그인, 장바구니 담기→주문, 관리자 상품 등록 등)만 적게 유지 —
  전체 화면을 E2E로 덮으려 하지 않는다. Storybook interaction test(컴포넌트 단위 상호작용)와는 계층이
  다르다 — Storybook은 Unit에 가깝고, 여기서 말하는 E2E는 실제 배포된 서비스 간 흐름이다.

## 저장소별 현황 (2026-08-21 기준)

| 저장소 | Unit | Integration(Testcontainers) | 비고 |
|---|---|---|---|
| product.api | ✅ | ✅ | 첫 적용 사례(posselect #213/#220) |
| auth.api | ✅ | 도입 중 | auth.api#15 |
| order.api | 도입 중 | 도입 중 | Postgres+JPA+Flyway 핵심인데 기존엔 0 |
| gateway | 일부 | - (WebFlux, StepVerifier로 대체) | 라우팅은 YAML 선언이라 통합 테스트 대상이 작음 |
| posselect-ui / posselect-shell / product.front / admin.front / store.front / customer.front | 도입 중 | 해당 없음(Next.js BFF 없음, 서버 상태 없음) | Vitest + Testing Library, E2E는 향후 별도 검토 |

## 원칙

- 커버리지는 리포트만 하고 게이트로 쓰지 않는다(`~/msa/AGENTS.md` §3 TDD 절, 2026-08-21 결정) — 대부분
  저장소가 0%에서 시작하므로 즉시 임계값을 걸면 모든 PR이 막힌다.
- Integration 계층을 새로 만들 때는 `@ServiceConnection`(Spring Boot 3) + Testcontainers PostgreSQL을
  기본으로 한다. 컨테이너를 매 테스트 클래스마다 새로 띄우면 느려지므로 가능하면 재사용 설정을 켠다.
- 프론트엔드는 서버 상태를 갖지 않는 BFF가 없으므로(전부 API를 직접 호출하는 Next.js) Integration 계층이
  사실상 없고 Unit(Vitest+Testing Library)과 필요시 E2E(Playwright)만 존재한다.
