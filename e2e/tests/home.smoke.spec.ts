import { test, expect } from './support/fixtures';
import { URLS } from './support/env';

test.describe('메인 페이지', () => {
  test('섹션·헤더·푸터가 렌더되고 예기치 않은 4xx/5xx 가 없다', async ({ page, badResponses }) => {
    await page.goto(URLS.home, { waitUntil: 'networkidle' });

    await expect(page).toHaveTitle(/PosSelect/);
    await expect(page.locator('header')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();
    await expect(page.getByRole('heading', { name: '베스트 상품' })).toBeVisible();
    await expect(page.getByRole('heading', { name: '신상품' })).toBeVisible();

    expect(badResponses, '비로그인 메인에서 예기치 않은 오류 응답').toEqual([]);
  });

  test('상품 카드가 노출되고 상세로 연결된다', async ({ page }) => {
    await page.goto(URLS.home, { waitUntil: 'networkidle' });

    const cards = page.locator('a[href*="/products/"]');
    expect(await cards.count()).toBeGreaterThan(0);
    await expect(cards.first()).toHaveAttribute('href', /\/products\/\d+/);
  });

  test('헤더 핵심 진입점(검색·장바구니·로그인)이 있다', async ({ page }) => {
    await page.goto(URLS.home, { waitUntil: 'networkidle' });
    const header = page.locator('header');
    for (const name of ['로그인', '회원가입', '검색', '장바구니']) {
      const entry = header.getByRole('link', { name, exact: true }).or(header.getByRole('button', { name, exact: true }));
      await expect(entry.first(), `헤더 '${name}'`).toBeVisible();
    }
  });
});
