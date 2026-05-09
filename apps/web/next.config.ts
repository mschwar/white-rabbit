import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required for Vercel server actions + image optimization
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
