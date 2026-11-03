/**
 * WORKFLOW — Phase 4 dev server
 * Proxies API paths to FastAPI (port 8000) so fetch('/telemetry/summary') works without CORS setup in dev.
 * RUN backend: cd backend && PYTHONPATH=. uvicorn app.main:app --reload --port 8000
 * RUN frontend: cd frontend && npm run dev → http://127.0.0.1:5173
 */
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/health": "http://127.0.0.1:8000",
      "/telemetry": "http://127.0.0.1:8000",
      "/forecast": "http://127.0.0.1:8000",
    },
  },
});
