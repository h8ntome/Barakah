// Run once before React mounts so StrictMode cannot consume the token twice.
// Keep unrelated URL parameters and history state, but never persist the token.
export function consumeResetToken(location, history) {
  const url = new URL(location.href);
  const fragment = new URLSearchParams(url.hash.slice(1));
  const token = fragment.get("token") || url.searchParams.get("token") || "";
  if (url.searchParams.has("token") || fragment.has("token")) {
    url.searchParams.delete("token");
    if (fragment.has("token")) {
      fragment.delete("token");
      url.hash = fragment.toString();
    }
    history.replaceState(
      history.state,
      "",
      `${url.pathname}${url.search}${url.hash}`,
    );
  }
  return token;
}
