import { defineConfig } from "vite";

// Proxy /demo/* to the local FastAPI server.
export default defineConfig({
  // When deployed inside the FastAPI server, the Phaser UI is served at /ui/
  base: "/ui/",
  server: {
    port: 5173,
    proxy: {
      "/demo": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});

