interface ImageAttributionProps {
  attribution: {
    license: string | null;
    license_url: string | null;
    author: string | null;
    image_page_url: string | null;
    source: string | null;
  } | null;
  className?: string;
}

/**
 * Displays Creative Commons attribution for images.
 * Format: "Image: Author • CC BY-SA 4.0 via Wikimedia Commons"
 */
export default function ImageAttribution({ attribution, className = '' }: ImageAttributionProps) {
  if (!attribution || (!attribution.author && !attribution.license)) {
    return null;
  }

  // Link author to the image page on Wikimedia Commons
  const authorLink = attribution.image_page_url;

  return (
    <figcaption className={`text-xs text-slate-500 ${className}`}>
      {attribution.author && (
        <>
          <span>Image: </span>
          {authorLink ? (
            <a
              href={authorLink}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-indigo-600 underline underline-offset-2"
            >
              {attribution.author}
            </a>
          ) : (
            <span>{attribution.author}</span>
          )}
        </>
      )}
      {attribution.author && attribution.license && <span> • </span>}
      {attribution.license && (
        <>
          {attribution.license_url ? (
            <a
              href={attribution.license_url}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-indigo-600 underline underline-offset-2"
            >
              {attribution.license}
            </a>
          ) : (
            <span>{attribution.license}</span>
          )}
        </>
      )}
      {attribution.source === 'wikimedia' && (
        <span className="text-slate-500"> via Wikimedia Commons</span>
      )}
    </figcaption>
  );
}
