// All screens remain mounted. A fetched placement is not an impression until visible.
export function observeAdImpression(
  element,
  onVisible,
  Observer = globalThis.IntersectionObserver,
) {
  if (!Observer) return () => {};
  const document = element.ownerDocument;
  let recorded = false;
  const observer = new Observer(
    (entries) => {
      if (
        recorded ||
        document.visibilityState !== "visible" ||
        element.closest("[hidden]") ||
        !element.getClientRects().length
      )
        return;
      if (
        entries.some(
          (entry) =>
            entry.target === element &&
            entry.isIntersecting &&
            entry.intersectionRatio > 0,
        )
      ) {
        recorded = true;
        observer.disconnect();
        onVisible();
      }
    },
    { threshold: 0.01 },
  );
  const onVisibilityChange = () => {
    if (!recorded && document.visibilityState === "visible") {
      observer.unobserve(element);
      observer.observe(element);
    }
  };
  observer.observe(element);
  document.addEventListener("visibilitychange", onVisibilityChange);
  return () => {
    recorded = true;
    observer.disconnect();
    document.removeEventListener("visibilitychange", onVisibilityChange);
  };
}
