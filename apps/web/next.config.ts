import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required for Vercel server actions + image optimization
  images: {
    unoptimized: true,
  },
  // Allow API proxy rewrites in production
  async rewrites() {
    const apiBase = process.env.WR_API_BASE_URL || "https://white-rabbit-api.fly.dev";
    return [
      {
        source: "/api/:path*",
        destination: `${apiBase}/:path*`,
      },
    ];
  },
};

export default nextConfig;
