import { useEffect, useRef } from "react";
import { getAds, recordAdEvent } from "../services/index.js";
import { observeAdImpression } from "../services/adVisibility.js";
import { useResource } from "../services/useResource.js";
function SponsoredPlacement({ ad }) {
  const ref = useRef(null);
  const impressionRecorded = useRef(false);
  useEffect(() => {
    if (impressionRecorded.current) return;
    return observeAdImpression(ref.current, () => {
      impressionRecorded.current = true;
      // Optional analytics must not block the user's financial workspace.
      recordAdEvent(ad.id, "impression").catch(() => {});
    });
  }, [ad.id]);
  return (
    <aside
      ref={ref}
      className="sponsored-placement"
      aria-label="Sponsored placement"
    >
      <small>Sponsored · Not a Barakah endorsement</small>
      <h3>{ad.title}</h3>
      <p>{ad.body}</p>
      <a
        href={ad.url}
        target="_blank"
        rel="sponsored noopener noreferrer"
        onClick={() => {
          recordAdEvent(ad.id, "click").catch(() => {});
        }}
      >
        Visit sponsor
      </a>
    </aside>
  );
}
export default function SponsoredAd({ context }) {
  const resource = useResource(getAds, context);
  // Ads are optional; an unavailable placement must not block financial records.
  return (
    resource.data
      ?.filter((ad) => ad.sponsored && /^https:\/\//i.test(ad.url))
      .map((ad) => <SponsoredPlacement key={ad.id} ad={ad} />) ?? null
  );
}
