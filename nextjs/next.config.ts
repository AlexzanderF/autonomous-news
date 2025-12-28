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
    // Skip Next.js image optimization when using external thumbnail URLs
    // In production: Nginx serves them with proper caching headers already
    // In development: Next.js server can't reach localhost:8080 for optimization
    unoptimized: process.env.NODE_ENV === 'production' || !!process.env.NEXT_PUBLIC_THUMBNAIL_BASE_URL,
  },
};

export default nextConfig;
