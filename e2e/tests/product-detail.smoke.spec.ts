import { test, expect } from './support/fixtures';
import { URLS } from './support/env';
import { fetchCatalog, won } from './support/catalog';

test.describe('상품 상세', () => {
  test('목록 → 상세 이동 시 API 의 이름·가격과 화면이 일치한다', async ({ page, badResponses }) => {
    const [product] = await fetchCatalog(1);

    await page.goto(URLS.product, { waitUntil: 'networkidle' });
    await page.locator(`a[href$="/products/${product.id}"]`).first().click();
    await expect(page).toHaveURL(new RegExp(`/products/${product.id}$`));

    await expect(page.getByRole('heading', { level: 1 })).toHaveText(product.name);
    await expect(page.getByText(won(product.price)).first()).toBeVisible();
    await expect(page.getByRole('button', { name: '장바구니 담기' })).toBeEnabled();

    expect(badResponses, '상세에서 예기치 않은 오류 응답').toEqual([]);
  });

  test('존재하지 않는 상품은 5xx 가 아니라 정상적인 not-found 로 처리된다', async ({ page }) => {
    const res = await page.goto(`${URLS.product}/products/999999999`, { waitUntil: 'domcontentloaded' });
    expect(res?.status(), '없는 상품 상세 응답 코드').toBeLessThan(500);
  });
});
