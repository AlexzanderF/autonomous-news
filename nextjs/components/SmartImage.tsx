'use client';

import React, { useState } from 'react';
import Image, { ImageProps } from 'next/image';

interface SmartImageProps extends ImageProps {
  containerClassName?: string;
}

const SmartImage: React.FC<SmartImageProps> = ({ 
  containerClassName = "", 
  className = "",
  alt,
  ...props 
}) => {
  const [isVertical, setIsVertical] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  // Disable Next.js image optimization for:
  // 1. Wikimedia URLs - they block server-side fetches with 429 errors
  // 2. Localhost URLs in development - Next.js blocks private IP resolution
  const srcString = typeof props.src === 'string' ? props.src : '';
  const isWikimediaUrl = srcString.includes('wikimedia.org');
  const isLocalhostUrl = srcString.includes('localhost') || srcString.includes('127.0.0.1');
  const shouldSkipOptimization = isWikimediaUrl || isLocalhostUrl || props.unoptimized;

  const handleLoad = (event: React.SyntheticEvent<HTMLImageElement>) => {
    const img = event.currentTarget;
    if (img.naturalHeight > img.naturalWidth) {
      setIsVertical(true);
    }
    setIsLoaded(true);
    if (props.onLoad) {
      props.onLoad(event);
    }
  };

  return (
    <div className={`relative w-full h-full overflow-hidden ${containerClassName}`}>
      {/* 
        Only show blur background if it's vertical.
        We use isLoaded to avoid flickering or showing the background before we know the ratio.
      */}
      {isLoaded && isVertical && (
        <Image
          {...props}
          alt=""
          className="w-full h-full object-cover blur-xl opacity-50 scale-110"
          fill
          aria-hidden="true"
          unoptimized={shouldSkipOptimization}
        />
      )}

      <Image
        {...props}
        alt={alt}
        className={`${className} ${isLoaded && isVertical ? 'object-contain' : 'object-cover'} transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-0'}`}
        onLoad={handleLoad}
        unoptimized={shouldSkipOptimization}
      />
    </div>
  );
};

export default SmartImage;
