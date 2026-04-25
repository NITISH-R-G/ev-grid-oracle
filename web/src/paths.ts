/**
 * Vite `base` is `/ui/` in production; static files from `web/public` live under that prefix.
 * Demo API routes stay at the site root (`/demo/...`), so do not use this for `/demo/*`.
 */
export function staticAssetUrl(path: string): string {
  const base = import.meta.env.BASE_URL;
  const b = base.endsWith("/") ? base : `${base}/`;
  const p = path.startsWith("/") ? path.slice(1) : path;
  return `${b}${p}`;
}
