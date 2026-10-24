// 熵逝碑林 / Entropy Epitaph — frontend entrypoint & router.

import "./styles.css";
import { api } from "./api.js";
import { renderLanding } from "./pages/landing.js";
import { renderGraveyard } from "./pages/graveyard.js";
import { renderPublic } from "./pages/public.js";
import { renderArchive } from "./pages/archive.js";

const app = document.getElementById("app");

const routes = {
  "#/": renderLanding,
  "#/graveyard": renderGraveyard,
  "#/public": renderPublic,
  "#/archive": renderArchive,
};

let pollTimer = null;

export function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

export function startPolling(fn, demoMode) {
  stopPolling();
  const interval = demoMode ? 3000 : 30000;
  pollTimer = setInterval(fn, interval);
}

function navBar(active) {
  const nav = document.createElement("nav");
  nav.className = "topnav";
  nav.innerHTML = `
    <a href="#/" class="brand">熵逝碑林<span class="brand-en">Entropy Epitaph</span></a>
    <div class="navlinks">
      <a href="#/graveyard" class="${active === "graveyard" ? "on" : ""}">我的墓园</a>
      <a href="#/public" class="${active === "public" ? "on" : ""}">无名墓区</a>
      <a href="#/archive" class="${active === "archive" ? "on" : ""}">消逝档案</a>
    </div>`;
  return nav;
}

async function render() {
  stopPolling();
  const hash = window.location.hash || "#/";
  const route = routes[hash] || renderLanding;
  app.innerHTML = "";

  const active = hash.replace("#/", "") || "home";
  if (hash !== "#/") {
    app.appendChild(navBar(active));
  }

  const container = document.createElement("main");
  container.className = "page";
  app.appendChild(container);

  await route(container, { api, startPolling, stopPolling });
}

window.addEventListener("hashchange", render);
window.addEventListener("load", render);
