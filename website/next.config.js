/** @type {import('next').NextConfig} */
const nextConfig = {
  // Using server-side rendering for API routes
  images: {
    unoptimized: true,
  },
}

module.exports = nextConfig
