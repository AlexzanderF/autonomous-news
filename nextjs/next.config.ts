import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: '**',
      },
    ],
    // Enable Next.js image optimization in production for caching benefits
    // Only disable in development when using external thumbnail base URL
    // (Next.js server can't reach localhost:8080 for optimization)
    // unoptimized: process.env.NODE_ENV === 'development' && !!process.env.NEXT_PUBLIC_THUMBNAIL_BASE_URL,
  },
};

export default nextConfig;
