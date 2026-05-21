import type { NextConfig } from "next";
import path from "path";

const isExport = process.env.NODE_ENV === 'production';

const nextConfig: NextConfig = {
  turbopack: {
    root: path.resolve(__dirname),
  },
  
  images: {
    unoptimized: true,
    qualities: [30, 42, 75],
  },

  ...(isExport
    ? {
        output: 'export',
      }
    : {
        rewrites: async () => {
          return {
            beforeFiles: [
              {
                source: '/api-proxy/:path*',
                destination: 'http://localhost:3000/:path*',
              },
            ],
          };
        },
        redirects: async () => {
          return [
            {
              source: '/insights',
              destination: '/dashboard',
              permanent: true,
            },
            {
              source: '/performance',
              destination: '/dashboard',
              permanent: true,
            },
            {
              source: '/sessions',
              destination: '/dashboard',
              permanent: true,
            },
            {
              source: '/settings',
              destination: '/dashboard?tab=settings',
              permanent: true,
            },
            {
              source: '/discovery',
              destination: '/dashboard?tab=market',
              permanent: true,
            },
          ];
        },
      }),
};

export default nextConfig;