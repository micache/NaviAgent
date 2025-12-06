import type { NextConfig } from "next";
import { config } from "dotenv";
import path from "path";

// Load .env from root directory
config({ path: path.resolve(__dirname, "../.env") });

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
