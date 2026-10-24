// Unified data boundary.
// - Local development defaults to the FastAPI backend.
// - GitHub Pages builds set VITE_DATA_MODE=static and use browser-local data.

import { createStaticApi } from "./static-api.js";

const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

async function req(path, options = {}) {
  const res = await fetch(BASE + path, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (res.status === 204) return null;
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) {}
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

export const backendApi = {
  isStatic: false,
  health: () => req("/health"),
  createMonument: (payload) =>
    req("/monuments", { method: "POST", body: JSON.stringify(payload) }),
  myMonuments: () => req("/monuments/my"),
  getMonument: (id) => req(`/monuments/${id}`),
  maintain: (id) => req(`/monuments/${id}/maintain`, { method: "POST" }),
  publicMonuments: () => req("/public/monuments"),
  condole: (id) => req(`/monuments/${id}/condole`, { method: "POST" }),
  archive: () => req("/certificates"),
  getCertificate: (certId) => req(`/certificates/${certId}`),
  getDemoMode: () => req("/settings/demo-mode"),
  toggleDemoMode: () => req("/settings/demo-mode", { method: "POST" }),
};

export const api =
  import.meta.env.VITE_DATA_MODE === "static" ? createStaticApi() : backendApi;
