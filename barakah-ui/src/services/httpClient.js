export class ApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
    this.code = details?.code;
  }
}

// Tokens never leave this closure. One refresh is shared by all pending requests.
export function createHttpClient({
  baseUrl = "/api/v1",
  fetchImpl = globalThis.fetch,
  getCsrfToken = () =>
    globalThis.document?.cookie
      .split("; ")
      .find((item) => item.startsWith("csrf_token="))
      ?.slice(11),
  onSession = () => {},
} = {}) {
  let accessToken = null;
  let refreshPromise = null;
  let generation = 0;
  const base = baseUrl.replace(/\/$/, "");
  async function transport(path, { method = "GET", body, token, signal } = {}) {
    let response;
    try {
      response = await fetchImpl(`${base}${path}`, {
        method,
        credentials: "include",
        signal,
        headers: {
          Accept: "application/json",
          ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...(getCsrfToken() && method !== "GET"
            ? { "X-CSRF-Token": decodeURIComponent(getCsrfToken()) }
            : {}),
        },
        ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
      });
    } catch (error) {
      if (error.name === "AbortError") throw error;
      throw new ApiError(
        "Cannot reach Barakah. Check your connection and try again.",
        0,
      );
    }
    const data =
      response.status === 204 ? null : await response.json().catch(() => null);
    if (!response.ok) {
      const detail = data?.detail;
      const message =
        response.status >= 500
          ? "Barakah is temporarily unavailable. Please try again."
          : typeof detail === "string"
            ? detail
            : Array.isArray(detail)
              ? detail
                  .map(
                    (item) =>
                      `${item.loc?.slice(1).join(".") || "Input"}: ${item.msg}`,
                  )
                  .join("; ")
              : data?.error?.message ||
                data?.message ||
                "The request could not be completed. Please try again.";
      throw new ApiError(message, response.status, data?.error || detail);
    }
    return data;
  }
  function acceptSession(session) {
    accessToken = session.access_token;
    onSession(session.user);
    return session.user;
  }
  function clearSession() {
    generation += 1;
    accessToken = null;
    onSession(null);
  }
  async function refresh() {
    if (!refreshPromise) {
      const started = generation;
      refreshPromise = transport("/auth/refresh", { method: "POST" })
        .then((session) => {
          if (started !== generation)
            throw new ApiError("Your session has ended. Please sign in.", 401);
          acceptSession(session);
          return session.user;
        })
        .catch((error) => {
          if (started === generation && error.status === 401) clearSession();
          throw error;
        })
        .finally(() => {
          refreshPromise = null;
        });
    }
    return refreshPromise;
  }
  async function request(path, options = {}) {
    const sentToken = accessToken;
    try {
      return await transport(path, { ...options, token: sentToken });
    } catch (error) {
      if (
        error.status !== 401 ||
        options.public ||
        error.code === "invalid_credentials"
      )
        throw error;
      if (!accessToken || accessToken === sentToken) await refresh();
      try {
        return await transport(path, { ...options, token: accessToken });
      } catch (retryError) {
        if (
          retryError.status === 401 &&
          retryError.code !== "invalid_credentials"
        )
          clearSession();
        throw retryError;
      }
    }
  }
  async function authenticate(path, payload) {
    if (refreshPromise) await refreshPromise.catch(() => {});
    const session = await transport(path, { method: "POST", body: payload });
    generation += 1;
    return acceptSession(session);
  }
  async function logout() {
    if (refreshPromise) await refreshPromise.catch(() => {});
    // Keep the session if the server cannot revoke its refresh cookie.
    await transport("/auth/logout", { method: "POST", token: accessToken });
    clearSession();
  }
  return { request, refresh, authenticate, logout, clearSession };
}
export function queryString(filters = {}) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== "" && value !== null && value !== undefined)
      params.set(key, String(value));
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}
