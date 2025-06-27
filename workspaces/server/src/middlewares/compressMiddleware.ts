import { encoding } from '@hapi/accept';
import { ZstdInit } from '@oneidentity/zstd-js/asm/index.cjs.js';
import { createMiddleware } from 'hono/factory';

const zstdInit = ZstdInit();

export const compressMiddleware = createMiddleware(async (c, next) => {
  await next();
  const { ZstdStream } = await zstdInit;

  const accept = encoding(c.req.header('Accept-Encoding'), ['zstd']);

  // コンテンツタイプとサイズに基づいて圧縮を最適化
  const contentType = c.res.headers.get('Content-Type') || '';
  const contentLength = parseInt(c.res.headers.get('Content-Length') || '0');
  
  // 小さいファイルや画像は圧縮しない
  if (contentLength > 0 && contentLength < 1024) {
    c.res.headers.append('Cache-Control', 'no-transform');
    return;
  }
  
  // 画像ファイルは既に圧縮されているのでスキップ
  if (contentType.startsWith('image/')) {
    c.res.headers.append('Cache-Control', 'no-transform');
    return;
  }

  switch (accept) {
    case 'zstd': {
      // コンテンツタイプに応じて圧縮レベルを調整
      let compressionLevel = 3; // デフォルトは低めに設定
      
      if (contentType.includes('json') || contentType.includes('javascript') || contentType.includes('css')) {
        compressionLevel = 6; // テキストファイルは中程度の圧縮
      } else if (contentType.includes('html')) {
        compressionLevel = 5; // HTMLは若干低め
      }
      
      const transform = new TransformStream<Uint8Array, Uint8Array>({
        transform(chunk, controller) {
          controller.enqueue(ZstdStream.compress(chunk, compressionLevel, false));
        },
      });

      c.res = new Response(c.res.body?.pipeThrough(transform), c.res);

      c.res.headers.delete('Content-Length');
      c.res.headers.append('Cache-Control', 'no-transform');
      c.res.headers.set('Content-Encoding', 'zstd');
      break;
    }
    default: {
      c.res.headers.append('Cache-Control', 'no-transform');
      break;
    }
  }
});
