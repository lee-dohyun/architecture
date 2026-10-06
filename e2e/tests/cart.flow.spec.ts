import { request } from '@playwright/test';
import { test, expect } from './support/fixtures';
import { ALLOW_WRITES, URLS } from './support/env';
import { fetchCatalog, won } from './support/catalog';

// 운영 Redis 에 비로그인 장바구니(CART_ID 쿠키, 30일 TTL)를 만든다 → 명시적으로 허용했을 때만.
test.skip(!ALLOW_WRITES, 'E2E_ALLOW_WRITES=1 일 때만 실행(운영에 쓰기 발생)');

async function stockOf(id: number): Promise<number> {
  const ctx = await request.newContext();
  try {
    const res = await ctx.get(`${URLS.product}/api/products/${id}`);
    return (await res.json()).stockQuantity as number;
  } finally {
    await ctx.dispose();
  }
}

test.describe('비로그인 장바구니', () => {
  test('담기 → 장바구니 표시 → 삭제 → 빈 장바구니, 그리고 재고는 변하지 않는다', async ({ page, badResponses }) => {
    const product = (await fetchCatalog(24)).find((p) => p.stockQuantity > 0);
    test.skip(!product, '재고 있는 상품이 없다');
    const { id, name, price } = product!;
    const stockBefore = await stockOf(id);

    try {
      await page.goto(`${URLS.product}/products/${id}`, { waitUntil: 'networkidle' });
      const add = page.waitForResponse((r) => r.url().endsWith('/api/cart/items') && r.request().method() === 'POST');
      await page.getByRole('button', { name: '장바구니 담기' }).click();
      expect((await add).status(), '장바구니 담기 응답').toBe(200);

      await page.goto(`${URLS.product}/cart`, { waitUntil: 'networkidle' });
      const row = page.getByRole('row').filter({ hasText: name });
      await expect(row).toBeVisible();
      await expect(row).toContainText(won(price));
      await expect(page.getByText(`합계: ${won(price)}`)).toBeVisible();
    } finally {
      // 테스트가 중간에 실패해도 자기가 담은 것은 되돌린다.
      await page.goto(`${URLS.product}/cart`, { waitUntil: 'networkidle' });
      const remove = page.getByRole('button', { name: '삭제' });
      while (await remove.count()) {
        await remove.first().click();
        await page.waitForTimeout(400);
      }
    }

    await expect(page.getByText('장바구니가 비어 있습니다')).toBeVisible();
    expect(await stockOf(id), '장바구니는 재고를 차감하지 않는다').toBe(stockBefore);
    expect(badResponses, '장바구니 플로우에서 예기치 않은 오류 응답').toEqual([]);
  });
});
