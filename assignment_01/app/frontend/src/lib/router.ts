import { useEffect, useState } from 'react';

// Minimal client-side router (no extra dependency): tracks window.location.pathname
// and re-renders on pushState/popstate. Enough for two static routes: `/` and `/result/:id`.

export function usePathname() {
  const [pathname, setPathname] = useState(window.location.pathname);

  useEffect(() => {
    const onChange = () => setPathname(window.location.pathname);
    window.addEventListener('popstate', onChange);
    window.addEventListener('pushstate', onChange);
    return () => {
      window.removeEventListener('popstate', onChange);
      window.removeEventListener('pushstate', onChange);
    };
  }, []);

  return pathname;
}

export function navigate(path: string) {
  if (window.location.pathname === path) return;
  window.history.pushState({}, '', path);
  window.dispatchEvent(new Event('pushstate'));
}
