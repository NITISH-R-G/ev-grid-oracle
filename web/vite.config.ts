import { defineConfig } from "vite";

// Proxy /demo/* to the local FastAPI server.
export default defineConfig({
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

