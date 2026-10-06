import { request } from '@playwright/test';
import { URLS } from './env';

export interface ApiProduct {
  id: number;
  name: string;
  price: number;
  stockQuantity: number;
}

/** 공개 목록 API(비로그인 GET)에서 현재 카탈로그를 읽는다 — 특정 상품 ID 를 하드코딩하지 않기 위함. */
export async function fetchCatalog(size = 24): Promise<ApiProduct[]> {
  const ctx = await request.newContext();
  try {
    const res = await ctx.get(`${URLS.product}/api/products?page=0&size=${size}`);
    if (!res.ok()) throw new Error(`catalog API ${res.status()}`);
    const body = (await res.json()) as ApiProduct[];
    if (!Array.isArray(body) || body.length === 0) throw new Error('catalog API returned no products');
    return body;
  } finally {
    await ctx.dispose();
  }
}

export const won = (n: number) => `${Math.round(n).toLocaleString('ko-KR')}원`;
