import { createMiddleware } from 'hono/factory';

export const cacheControlMiddleware = createMiddleware(async (c, next) => {
  await next();
  
  const url = c.req.url;
  const contentType = c.res.headers.get('Content-Type') || '';
  
  // 画像リソースの場合は長期キャッシュを設定
  if (contentType.startsWith('image/') || url.includes('/images/') || url.includes('/assets/')) {
    c.res.headers.set('Cache-Control', 'public, max-age=31536000, immutable');
  }
  // 静的なJS/CSSファイルの場合も長期キャッシュ
  else if (contentType.includes('javascript') || contentType.includes('css')) {
    c.res.headers.set('Cache-Control', 'public, max-age=31536000, immutable');
  }
  // APIレスポンスやHTMLは短期キャッシュ
  else if (contentType.includes('json') || contentType.includes('html')) {
    c.res.headers.set('Cache-Control', 'private, max-age=0, must-revalidate');
  }
  // その他のリソース
  else {
    c.res.headers.set('Cache-Control', 'private, no-store');
  }
});
