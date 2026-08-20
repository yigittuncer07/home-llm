import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { Toaster } from 'sonner';
import { router } from './router';
import { useAuthStore } from './store/authStore';
import { useUIStore } from './store/uiStore';
import './index.css';

function Bootstrap() {
  const initFromStorage = useAuthStore((s) => s.initFromStorage);
  const initTheme = useUIStore((s) => s.initTheme);

  React.useLayoutEffect(() => {
    initFromStorage();
    initTheme();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <>
      <RouterProvider router={router} />
      <Toaster position="top-right" richColors closeButton />
    </>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Bootstrap />
  </React.StrictMode>,
);
