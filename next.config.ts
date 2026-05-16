import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
    qualities: [30, 42, 75],
  },
  /* 
     Note: redirects and rewrites are server-side features and are disabled for static export.
     Ensure your API calls in lib/api point to a full production URL.
  */
};

export default nextConfig;
