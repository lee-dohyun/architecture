import { test, expect } from './support/fixtures';
import { URLS } from './support/env';
import { fetchCatalog } from './support/catalog';

test.describe('상품 목록·검색', () => {
  test('목록이 첫 페이지를 보여주고 "더보기"가 다음 페이지를 이어 붙인다', async ({ page, badResponses }) => {
    await page.goto(URLS.product, { waitUntil: 'networkidle' });

    const cards = page.locator('a[href*="/products/"]');
    const more = page.getByRole('button', { name: /더보기 \(\d+ \/ \d+\)/ });
    await expect(more).toBeVisible();

    const before = await cards.count();
    expect(before).toBeGreaterThan(0);
    const [, total] = (await more.innerText()).match(/\((\d+) \/ (\d+)\)/)!.slice(1).map(Number);

    await more.click();
    await expect.poll(() => cards.count(), { message: '더보기 후 카드 수 증가' }).toBeGreaterThan(before);
    expect(await cards.count()).toBeLessThanOrEqual(total);

    expect(badResponses, '목록에서 예기치 않은 오류 응답').toEqual([]);
  });

  test('검색어로 해당 상품이 나오고, 없는 검색어는 빈 상태를 보여준다', async ({ page }) => {
    const [first] = await fetchCatalog(1);
    const term = first.name.split(/\s+/).sort((a, b) => b.length - a.length)[0];

    await page.goto(`${URLS.product}/?q=${encodeURIComponent(term)}`, { waitUntil: 'networkidle' });
    await expect(page.locator('a[href*="/products/"]').filter({ hasText: first.name }).first()).toBeVisible();

    await page.goto(`${URLS.product}/?q=zzzzqqqq-no-such-product`, { waitUntil: 'networkidle' });
    await expect(page.getByText('등록된 상품이 없습니다')).toBeVisible();
    await expect(page.locator('a[href*="/products/"]')).toHaveCount(0);
  });

  test('검색 입력창으로 검색하면 q 파라미터가 반영된다', async ({ page }) => {
    await page.goto(URLS.product, { waitUntil: 'networkidle' });
    const input = page.locator('input[name="q"]');
    await input.fill('zzzzqqqq-no-such-product');
    await input.press('Enter');
    await expect(page).toHaveURL(/[?&]q=zzzzqqqq/);
  });
});
