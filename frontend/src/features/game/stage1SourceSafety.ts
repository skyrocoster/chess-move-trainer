export function safeSourceUrl(sourceUrl: string | null): string | null {
  if (!sourceUrl) {
    return null;
  }

  try {
    const url = new URL(sourceUrl);
    const isChessCom = url.hostname === "www.chess.com";
    const isGamePath = /^\/game\/(?:live|daily)\/[A-Za-z0-9_-]+\/?$/.test(url.pathname);
    if (url.protocol !== "https:" || !isChessCom || !isGamePath || url.search || url.hash) {
      return null;
    }
    return url.href;
  } catch {
    return null;
  }
}
