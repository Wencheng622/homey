import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Match /api/... with OR without a trailing slash (Next dev normalizes away
    // trailing slashes by default, so `/api/auth/login/` becomes `/api/auth/login`).
    // Django expects trailing slashes on its routes.
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/v1/:path*/`,
      },
    ];
  },
  
  async redirects() {
    return [
      {
        source: '/',
        destination: '/login',
        permanent: false,
      },
    ];
  },
  
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
};

export default nextConfig;