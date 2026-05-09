import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required for Vercel server actions + image optimization
  images: {
    unoptimized: true,
  },
  // Allow API proxy rewrites in production
  async rewrites() {
    const apiBase = process.env.WR_API_BASE_URL || "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiBase}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
