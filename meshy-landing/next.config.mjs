/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "meshy.ai",
      },
    ],
  },
};

export default nextConfig;
