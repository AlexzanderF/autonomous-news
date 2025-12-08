'use client';

import { useEffect, useState, useRef } from 'react';

interface TableOfContentsProps {
  headings: string[];
}

export default function TableOfContents({ headings }: TableOfContentsProps) {
  const [activeHeading, setActiveHeading] = useState<string>(headings[0] || '');
  const headingElementsRef = useRef<HTMLElement[]>([]);

  useEffect(() => {
    // Cache heading elements once to avoid querying DOM on every scroll
    const article = document.querySelector('article');
    if (article) {
      const headingTags = Array.from(article.querySelectorAll('h2'));
      headingElementsRef.current = headingTags.filter(tag =>
        headings.includes(tag.textContent?.trim() || '')
      );
    }

    const handleScroll = () => {
      const threshold = window.innerHeight * 0.5;

      // Check if we're at the bottom of the page
      if ((window.innerHeight + window.scrollY) >= document.documentElement.scrollHeight - 50) {
        setActiveHeading(headings[headings.length - 1]);
        return;
      }

      // Find the last heading that is above the threshold
      let currentActive = headings[0];

      for (const el of headingElementsRef.current) {
        const rect = el.getBoundingClientRect();
        if (rect.top < threshold) {
          currentActive = el.textContent?.trim() || currentActive;
        } else {
          break;
        }
      }

      setActiveHeading(currentActive);
    };

    // Initial check
    handleScroll();

    // Throttled scroll handler
    let ticking = false;
    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          handleScroll();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, [headings]);

  if (headings.length === 0) return null;

  return (
    <div className="mb-12">
      <div className="space-y-0">
        {headings.map((heading, index) => (
          <button
            key={index}
            className={`group w-full text-left flex items-start pl-4 border-l-2 py-1 transition-all duration-300 ${activeHeading === heading
              ? 'border-white'
              : 'border-slate-800 hover:border-slate-600'
              }`}
          >
            <span
              className={`text-lg leading-tight transition-colors duration-300 ${activeHeading === heading
                ? 'text-slate-100 font-medium'
                : 'text-slate-500 group-hover:text-slate-300'
                }`}
            >
              {heading}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
