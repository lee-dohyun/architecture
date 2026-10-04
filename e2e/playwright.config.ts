import { defineConfig, devices } from '@playwright/test';

/**
 * posselect.com E2E — 실제 배포된 서비스 간 흐름만 검증한다(Test Pyramid 최상단, 적게).
 * 계층 정의는 docs/2026-08-21-test-pyramid-strategy.md 참고.
 *
 * 프로젝트
 *  - smoke : 읽기 전용. 운영에 아무것도 쓰지 않는다. CI 기본값.
 *  - flow  : 쓰기가 있는 플로우(장바구니). E2E_ALLOW_WRITES=1 일 때만 실행되고, 각 테스트가 자기가 만든 것을 되돌린다.
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  timeout: 30_000,
  expect: { timeout: 8_000 },
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
  use: {
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    locale: 'ko-KR',
  },
  projects: [
    { name: 'smoke', testMatch: /.*\.smoke\.spec\.ts/, use: { ...devices['Desktop Chrome'] } },
    { name: 'flow', testMatch: /.*\.flow\.spec\.ts/, use: { ...devices['Desktop Chrome'] } },
  ],
});
