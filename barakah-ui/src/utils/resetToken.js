// Run once before React mounts so StrictMode cannot consume the token twice.
// Keep unrelated URL parameters and history state, but never persist the token.
export function consumeResetToken(location, history) {
  const url = new URL(location.href);
  const token = url.searchParams.get("token") || "";
  if (url.searchParams.has("token")) {
    url.searchParams.delete("token");
    history.replaceState(
      history.state,
      "",
      `${url.pathname}${url.search}${url.hash}`,
    );
  }
  return token;
}
