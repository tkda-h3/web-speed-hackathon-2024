import React, { Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import { styled } from 'styled-components';

import { SvgIcon } from './features/icons/components/SvgIcon';
import { Link } from './foundation/components/Link';
import { Text } from './foundation/components/Text';
import { ActionLayout } from './foundation/layouts/ActionLayout';
import { CommonLayout } from './foundation/layouts/CommonLayout';
import { Color, Space, Typography } from './foundation/styles/variables';

// ページコンポーネントの遅延読み込み
const TopPage = React.lazy(() => import('./pages/TopPage').then(m => ({ default: m.TopPage })));
const BookDetailPage = React.lazy(() => import('./pages/BookDetailPage').then(m => ({ default: m.BookDetailPage })));
const EpisodeDetailPage = React.lazy(() => import('./pages/EpisodeDetailPage').then(m => ({ default: m.EpisodeDetailPage })));
const AuthorDetailPage = React.lazy(() => import('./pages/AuthorDetailPage').then(m => ({ default: m.AuthorDetailPage })));
const SearchPage = React.lazy(() => import('./pages/SearchPage').then(m => ({ default: m.SearchPage })));

const _BackToTopButton = styled(Link)`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: ${Space * 1}px;
  border: none;
  background-color: transparent;
`;

export const Router: React.FC = () => {
  return (
    <Routes>
      <Route element={<CommonLayout />} path={'/'}>
        <Route element={<Suspense fallback={null}><TopPage /></Suspense>} path={''} />
      </Route>
      <Route
        element={
          <ActionLayout
            leftContent={
              <_BackToTopButton href={'/'}>
                <SvgIcon color={Color.MONO_100} height={32} type="ArrowBack" width={32} />
                <Text color={Color.MONO_100} typography={Typography.NORMAL16} weight="bold">
                  トップへ戻る
                </Text>
              </_BackToTopButton>
            }
          />
        }
        path={'/'}
      >
        <Route element={<Suspense fallback={null}><BookDetailPage /></Suspense>} path={'books/:bookId'} />
        <Route element={<Suspense fallback={null}><EpisodeDetailPage /></Suspense>} path={'books/:bookId/episodes/:episodeId'} />
        <Route element={<Suspense fallback={null}><AuthorDetailPage /></Suspense>} path={'authors/:authorId'} />
        <Route element={<Suspense fallback={null}><SearchPage /></Suspense>} path={'search'} />
      </Route>
    </Routes>
  );
};
