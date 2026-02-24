import type { NextConfig } from "next";

const isDev = process.env.NODE_ENV === "development";

const nextConfig: NextConfig = {
  output: isDev ? undefined : "export",
  images: { unoptimized: true },
  async rewrites() {
    if (isDev) {
      return [
        {
          source: "/chat",
          destination: "http://127.0.0.1:8000/chat",
        },
        {
          source: "/agents",
          destination: "http://127.0.0.1:8000/agents",
        },
        {
          source: "/agents/:path*",
          destination: "http://127.0.0.1:8000/agents/:path*",
        },
        {
          source: "/config",
          destination: "http://127.0.0.1:8000/config",
        },
        {
          source: "/heartbeat",
          destination: "http://127.0.0.1:8000/heartbeat",
        },
        {
          source: "/auth/status",
          destination: "http://127.0.0.1:8000/auth/status",
        },
        {
          source: "/auth/google/login",
          destination: "http://127.0.0.1:8000/auth/google/login",
        },
        {
          source: "/auth/qwen/login",
          destination: "http://127.0.0.1:8000/auth/qwen/login",
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
