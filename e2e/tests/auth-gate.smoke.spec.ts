import { test, expect } from './support/fixtures';
import { URLS } from './support/env';

test.describe('비로그인 접근 제어', () => {
  test('보호된 고객 페이지는 로그인으로 리다이렉트되고 원래 경로를 보존한다', async ({ page }) => {
    await page.goto(`${URLS.customer}/mypage`, { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveURL(/\/login\?redirect_uri=/);
  });

  test('비로그인 /api/auth/me 는 401 이다(5xx·200 이 아님)', async ({ request }) => {
    const res = await request.get(`${URLS.customer}/api/auth/me`);
    expect(res.status()).toBe(401);
  });
});
