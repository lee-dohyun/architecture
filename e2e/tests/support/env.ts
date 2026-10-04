// 대상 환경. 기본값은 운영(개발 단계라 실사용자 트래픽 없음, ~/msa/AGENTS.md "현재 단계").
// 스테이징이 생기면 환경변수만 바꿔 같은 스위트를 돌린다.
export const URLS = {
  home: process.env.E2E_HOME_URL ?? 'https://home.posselect.com',
  product: process.env.E2E_PRODUCT_URL ?? 'https://product.posselect.com',
  customer: process.env.E2E_CUSTOMER_URL ?? 'https://customer.posselect.com',
};

export const ALLOW_WRITES = process.env.E2E_ALLOW_WRITES === '1';
