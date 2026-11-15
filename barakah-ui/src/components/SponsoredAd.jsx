import { getAds } from "../services/index.js";
import { useResource } from "../services/useResource.js";
export default function SponsoredAd({ context }) {
  const resource = useResource(getAds, context);
  // Ads are optional; an unavailable placement must not block financial records.
  return (
    resource.data
      ?.filter((ad) => ad.sponsored && /^https:\/\//i.test(ad.url))
      .map((ad) => (
        <aside
          className="sponsored-placement"
          key={ad.id}
          aria-label="Sponsored placement"
        >
          <small>Sponsored · Not a Barakah endorsement</small>
          <h3>{ad.title}</h3>
          <p>{ad.body}</p>
          <a href={ad.url} target="_blank" rel="sponsored noopener noreferrer">
            Visit sponsor
          </a>
        </aside>
      )) ?? null
  );
}
