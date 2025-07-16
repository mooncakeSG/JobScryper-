import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/auth/:path*',
        destination: 'http://localhost:8000/api/auth/:path*',
      },
      {
        source: '/api/analytics',
        destination: 'http://localhost:8000/api/analytics',
      },
      {
        source: '/api/saved-jobs',
        destination: 'http://localhost:8000/api/saved-jobs',
      },
      {
        source: '/api/applications/:path*',
        destination: 'http://localhost:8000/api/applications/:path*',
      },
      {
        source: '/api/resume/:path*',
        destination: 'http://localhost:8000/api/resume/:path*',
      },
      {
        source: '/api/users/:path*',
        destination: 'http://localhost:8000/api/users/:path*',
      },
      {
        source: '/api/preferences',
        destination: 'http://localhost:8000/api/preferences',
      },
      {
        source: '/api/recommendations',
        destination: 'http://localhost:8000/api/recommendations',
      },
      {
        source: '/api/interview/:path*',
        destination: 'http://localhost:8000/api/interview/:path*',
      },
      {
        source: '/api/market/:path*',
        destination: 'http://localhost:8000/api/market/:path*',
      },
      {
        source: '/api/salary/:path*',
        destination: 'http://localhost:8000/api/salary/:path*',
      },
      {
        source: '/health',
        destination: 'http://localhost:8000/health',
      },
    ];
  },
};

export default nextConfig;
