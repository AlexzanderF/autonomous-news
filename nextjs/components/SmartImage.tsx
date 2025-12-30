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

  const handleLoadingComplete = (img: HTMLImageElement) => {
    if (img.naturalHeight > img.naturalWidth) {
      setIsVertical(true);
    }
    setIsLoaded(true);
    if (props.onLoadingComplete) {
      props.onLoadingComplete(img);
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
        />
      )}

      <Image
        {...props}
        alt={alt}
        className={`${className} ${isLoaded && isVertical ? 'object-contain' : 'object-cover'} transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-0'}`}
        onLoadingComplete={handleLoadingComplete}
      />
    </div>
  );
};

export default SmartImage;
