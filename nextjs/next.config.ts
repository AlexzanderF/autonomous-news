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
    // Skip Next.js image optimization for local thumbnails
    // Nginx serves them with proper caching headers already
    unoptimized: process.env.NODE_ENV === 'production',
  },
};

export default nextConfig;
