import { useEffect, useRef, useState } from 'react';
import { useAsync } from 'react-use';

import { getImageUrl } from '../../lib/image/getImageUrl';

export const useImage = ({ 
  height, 
  imageId, 
  width,
  lazy = true 
}: { 
  height: number; 
  imageId: string; 
  width: number;
  lazy?: boolean;
}) => {
  const [shouldLoad, setShouldLoad] = useState(!lazy);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const elementRef = useRef<HTMLElement | null>(null);

  // Intersection Observerの設定
  useEffect(() => {
    if (!lazy || shouldLoad) return;

    const callback = (entries: IntersectionObserverEntry[]) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setShouldLoad(true);
          observerRef.current?.disconnect();
        }
      });
    };

    observerRef.current = new IntersectionObserver(callback, {
      rootMargin: '50px', // 50px手前から読み込み開始
      threshold: 0.01
    });

    return () => {
      observerRef.current?.disconnect();
    };
  }, [lazy, shouldLoad]);

  const { value } = useAsync(async () => {
    if (!shouldLoad) return null;

    const dpr = window.devicePixelRatio;

    const img = new Image();
    img.src = getImageUrl({
      format: 'jpg',
      height: height * dpr,
      imageId,
      width: width * dpr,
    });

    await img.decode();

    const canvas = document.createElement('canvas');
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    const ctx = canvas.getContext('2d')!;

    // Draw image to canvas as object-fit: cover
    const imgAspect = img.naturalWidth / img.naturalHeight;
    const targetAspect = width / height;

    if (imgAspect > targetAspect) {
      const srcW = img.naturalHeight * targetAspect;
      const srcH = img.naturalHeight;
      const srcX = (img.naturalWidth - srcW) / 2;
      const srcY = 0;
      ctx.drawImage(img, srcX, srcY, srcW, srcH, 0, 0, width * dpr, height * dpr);
    } else {
      const srcW = img.naturalWidth;
      const srcH = img.naturalWidth / targetAspect;
      const srcX = 0;
      const srcY = (img.naturalHeight - srcH) / 2;
      ctx.drawImage(img, srcX, srcY, srcW, srcH, 0, 0, width * dpr, height * dpr);
    }

    return canvas.toDataURL('image/png');
  }, [height, imageId, width, shouldLoad]);

  // 要素を監視対象に追加するための関数
  const setRef = (element: HTMLElement | null) => {
    if (element && lazy && !shouldLoad) {
      elementRef.current = element;
      observerRef.current?.observe(element);
    }
  };

  // 後方互換性のため、直接値を返すこともサポート
  return value;
};