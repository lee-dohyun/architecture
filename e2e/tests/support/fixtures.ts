import { test as base, expect } from '@playwright/test';

/**
 * 비로그인 상태에서 정상적으로 4xx 를 내는 호출 — 이 외의 4xx/5xx 는 실패로 본다.
 *  - customer /api/auth/me 401 : 로그인 여부 확인
 *  - /api/wishlists/product-ids 400 : 비로그인 찜 조회(2026-10-04 실측. 401/빈 목록이 아니라 400 이라 별도 점검 거리)
 *  - /api/auth/me/grade, /api/auth/addresses 401 : 장바구니 페이지가 회원 정보(등급·배송지)를 프리필하려고 비로그인에서도 호출(2026-10-04 실측)
 */
const KNOWN_GUEST_NOISE: { status: number; path: RegExp }[] = [
  { status: 401, path: /\/api\/auth\/me$/ },
  { status: 400, path: /\/api\/wishlists\/product-ids$/ },
  { status: 401, path: /\/api\/auth\/(me\/grade|addresses)$/ },
];

export const test = base.extend<{ badResponses: string[] }>({
  badResponses: async ({ page }, use) => {
    const bad: string[] = [];
    page.on('response', (res) => {
      const status = res.status();
      if (status < 400) return;
      const url = new URL(res.url());
      if (!/posselect\.com$/.test(url.hostname) && !url.hostname.endsWith('.posselect.com')) return;
      if (KNOWN_GUEST_NOISE.some((k) => k.status === status && k.path.test(url.pathname))) return;
      bad.push(`${status} ${res.request().method()} ${url.origin}${url.pathname}`);
    });
    await use(bad);
  },
});

export { expect };
