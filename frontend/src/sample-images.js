// Synthetic sample images for 图片碑 / Image monuments.
// Each is an inline SVG data-URI — no external files, works offline and on Pages.
// They stand in for "deleted photos / lost screenshots" without using real people's images.

function svgDataUri(svg) {
  return "data:image/svg+xml;utf8," + encodeURIComponent(svg);
}

// A faded sunset over water — "the last photo we took together"
const SUNSET = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3a2f3a"/>
      <stop offset="55%" stop-color="#7a5a4a"/>
      <stop offset="75%" stop-color="#b08a5a"/>
      <stop offset="100%" stop-color="#1e1a18"/>
    </linearGradient>
  </defs>
  <rect width="320" height="200" fill="url(#sky)"/>
  <circle cx="160" cy="118" r="34" fill="#d8a860" opacity="0.85"/>
  <rect y="130" width="320" height="70" fill="#1a1512" opacity="0.6"/>
  <rect y="138" width="320" height="4" fill="#c8a060" opacity="0.5"/>
  <rect y="150" width="320" height="3" fill="#a07840" opacity="0.4"/>
</svg>`);

// A pixelated room — "the apartment after everyone moved out"
const ROOM = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200">
  <rect width="320" height="200" fill="#242018"/>
  <rect x="0" y="0" width="320" height="130" fill="#2e2a22"/>
  <rect x="40" y="40" width="80" height="60" fill="#1a1714" stroke="#4a4236"/>
  <rect x="46" y="46" width="68" height="48" fill="#3a3024"/>
  <rect x="200" y="30" width="90" height="70" fill="#1a1714" stroke="#4a4236"/>
  <rect x="150" y="150" width="60" height="30" fill="#3a332a"/>
  <line x1="0" y1="130" x2="320" y2="130" stroke="#4a4236" stroke-width="2"/>
</svg>`);

// An abstract portrait silhouette — "a face I'm starting to forget"
const PORTRAIT = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200">
  <rect width="320" height="200" fill="#201d1a"/>
  <ellipse cx="160" cy="92" rx="58" ry="72" fill="#4a4038"/>
  <ellipse cx="160" cy="82" rx="46" ry="56" fill="#6a5c4e"/>
  <circle cx="142" cy="78" r="6" fill="#201d1a"/>
  <circle cx="178" cy="78" r="6" fill="#201d1a"/>
  <path d="M146 104 Q160 114 174 104" stroke="#201d1a" stroke-width="3" fill="none"/>
  <rect y="160" width="320" height="40" fill="#2a251f"/>
</svg>`);

// A chat screenshot — "the conversation I screenshotted before deleting"
const SCREENSHOT = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200">
  <rect width="320" height="200" fill="#16130f"/>
  <rect x="0" y="0" width="320" height="26" fill="#2a251f"/>
  <circle cx="16" cy="13" r="5" fill="#5a5244"/>
  <rect x="30" y="9" width="90" height="8" rx="4" fill="#4a4236"/>
  <rect x="16" y="44" width="150" height="26" rx="8" fill="#3a332a"/>
  <rect x="24" y="52" width="110" height="5" rx="2" fill="#6a6254"/>
  <rect x="154" y="86" width="150" height="40" rx="8" fill="#5a4a38"/>
  <rect x="162" y="94" width="130" height="5" rx="2" fill="#8a7a5a"/>
  <rect x="162" y="106" width="90" height="5" rx="2" fill="#8a7a5a"/>
  <rect x="16" y="140" width="120" height="26" rx="8" fill="#3a332a"/>
  <rect x="24" y="148" width="80" height="5" rx="2" fill="#6a6254"/>
</svg>`);

// A map pin — "a place that no longer exists"
const MAP = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200">
  <rect width="320" height="200" fill="#1a1d18"/>
  <path d="M0 60 L120 40 L200 90 L320 70" stroke="#3a4036" stroke-width="2" fill="none"/>
  <path d="M40 160 L140 120 L240 170 L320 140" stroke="#3a4036" stroke-width="2" fill="none"/>
  <path d="M90 0 L110 200" stroke="#2e342a" stroke-width="2"/>
  <path d="M220 0 L205 200" stroke="#2e342a" stroke-width="2"/>
  <path d="M160 70 C142 70 130 84 130 100 C130 122 160 146 160 146 C160 146 190 122 190 100 C190 84 178 70 160 70 Z" fill="#a04030"/>
  <circle cx="160" cy="100" r="11" fill="#1a1d18"/>
</svg>`);

export const SAMPLE_IMAGES = {
  sunset: SUNSET,
  room: ROOM,
  portrait: PORTRAIT,
  screenshot: SCREENSHOT,
  map: MAP,
};

// Ordered list used by the fixture builder / create flow fallback.
export const SAMPLE_IMAGE_KEYS = ["sunset", "room", "portrait", "screenshot", "map"];
