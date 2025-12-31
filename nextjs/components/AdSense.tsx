'use client';

import React, { useEffect, useRef } from 'react';

// Extend Window interface for AdSense
declare global {
  interface Window {
    adsbygoogle: unknown[];
  }
}

export type AdFormat = 'horizontal' | 'vertical' | 'rectangle' | 'auto';

interface AdSenseProps {
  /** Ad format: 'horizontal' (728x90), 'vertical' (160x600), 'rectangle' (300x250), 'auto' (responsive) */
  format?: AdFormat;
  /** Optional custom className for the container */
  className?: string;
  /** Whether to use a full-width responsive layout */
  fullWidth?: boolean;
}

/**
 * Google AdSense component for displaying responsive ads
 * Publisher ID: pub-5508175880003857
 */
const AdSense: React.FC<AdSenseProps> = ({ 
  format = 'auto',
  className = '',
  fullWidth = false
}) => {
  const adRef = useRef<HTMLModElement>(null);
  const isAdPushed = useRef(false);

  useEffect(() => {
    // Only push the ad once per component instance
    if (isAdPushed.current) return;
    
    try {
      // Initialize adsbygoogle array if it doesn't exist
      if (typeof window !== 'undefined') {
        window.adsbygoogle = window.adsbygoogle || [];
        window.adsbygoogle.push({});
        isAdPushed.current = true;
      }
    } catch (error) {
      console.error('AdSense error:', error);
    }
  }, []);

  // Define styles based on format
  const getAdStyle = (): React.CSSProperties => {
    if (fullWidth) {
      return { display: 'block', width: '100%' };
    }

    switch (format) {
      case 'horizontal':
        // Leaderboard style - good for headers/footers
        return { display: 'block', width: '100%', height: '90px' };
      case 'vertical':
        // Skyscraper style - good for sidebars
        return { display: 'block', width: '160px', height: '600px' };
      case 'rectangle':
        // Medium rectangle - versatile, good for sidebars
        return { display: 'block', width: '300px', height: '250px' };
      case 'auto':
      default:
        // Fully responsive - adapts to container
        return { display: 'block' };
    }
  };

  // Container classes based on format
  const getContainerClasses = (): string => {
    const baseClasses = 'overflow-hidden';
    
    switch (format) {
      case 'horizontal':
        return `${baseClasses} w-full min-h-[90px]`;
      case 'vertical':
        return `${baseClasses} w-[160px] min-h-[600px]`;
      case 'rectangle':
        return `${baseClasses} w-full max-w-[300px] min-h-[250px]`;
      case 'auto':
      default:
        return `${baseClasses} w-full min-h-[100px]`;
    }
  };

  return (
    <div className={`adsense-container ${getContainerClasses()} ${className}`}>
      <ins
        ref={adRef}
        className="adsbygoogle"
        style={getAdStyle()}
        data-ad-client="ca-pub-5508175880003857"
        data-ad-format={format === 'auto' ? 'auto' : undefined}
        data-full-width-responsive={fullWidth || format === 'auto' ? 'true' : 'false'}
      />
    </div>
  );
};

export default AdSense;
