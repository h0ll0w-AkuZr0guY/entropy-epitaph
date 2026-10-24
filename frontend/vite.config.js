import { defineConfig } from "vite";

export default defineConfig({
  // GitHub project Pages uses /<repository>/; local and user Pages use /.
  base: process.env.VITE_BASE_PATH || "/",
  server: {
    host: "127.0.0.1",
    port: 5173,
  },
  preview: {
    host: "127.0.0.1",
    port: 4173,
  },
  test: {
    include: ["src/**/*.test.js"],
  },
});
