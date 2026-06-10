/* Pyramid Systems — Core Web Vitals tracking
   ==========================================
   Sends Google's three Core Web Vitals metrics to the dataLayer so GTM
   can forward them to GA4:

     LCP (Largest Contentful Paint) — when the biggest above-fold element
          finished loading. Good < 2.5s, needs improvement < 4s, poor > 4s.
     INP (Interaction to Next Paint) — how responsive the page feels when
          a user clicks/taps. Good < 200ms, needs improvement < 500ms.
     CLS (Cumulative Layout Shift)  — how much the page visually jumps
          while loading. Good < 0.1, needs improvement < 0.25, poor > 0.25.

   Loaded from Google's CDN so we don't have to bundle the web-vitals
   library locally. Pushes to dataLayer ONCE per metric per page load.
   GTM has a Custom Event trigger on "web_vitals" that routes to a GA4
   Event tag named "web_vitals" with metric_name + metric_value + rating.

   We use the "attribution" build of web-vitals so each metric also
   carries the responsible element (for LCP) or interaction target (for
   INP) — useful for telling engineers WHICH element to optimize.
*/
(function () {
    "use strict";
    if (window.PyramidWebVitals) return;
    window.dataLayer = window.dataLayer || [];

    function rating(name, value) {
        if (value == null) return "unknown";
        if (name === "LCP") return value <= 2500 ? "good" : value <= 4000 ? "needs_improvement" : "poor";
        if (name === "INP") return value <= 200  ? "good" : value <= 500  ? "needs_improvement" : "poor";
        if (name === "CLS") return value <= 0.1  ? "good" : value <= 0.25 ? "needs_improvement" : "poor";
        if (name === "FCP") return value <= 1800 ? "good" : value <= 3000 ? "needs_improvement" : "poor";
        if (name === "TTFB")return value <= 800  ? "good" : value <= 1800 ? "needs_improvement" : "poor";
        return "unknown";
    }
    function push(name, value, attribution) {
        window.dataLayer.push({
            event: "web_vitals",
            metric_name: name,
            metric_value: typeof value === "number" ? Math.round(value * 1000) / 1000 : value,
            metric_rating: rating(name, value),
            metric_target_element: (attribution && attribution.element) ? String(attribution.element).slice(0, 200) : "",
            page_path: window.location.pathname,
        });
    }

    /* Load web-vitals from Google's CDN. Falls back silently if blocked. */
    var script = document.createElement("script");
    script.src = "https://unpkg.com/web-vitals@4/dist/web-vitals.attribution.iife.js";
    script.async = true;
    script.onload = function () {
        try {
            var wv = window.webVitals;
            if (!wv) return;
            wv.onCLS(function (m) { push("CLS", m.value, m.attribution); });
            wv.onINP(function (m) { push("INP", m.value, m.attribution); });
            wv.onLCP(function (m) { push("LCP", m.value, m.attribution); });
            wv.onFCP(function (m) { push("FCP", m.value, m.attribution); });
            wv.onTTFB(function (m) { push("TTFB", m.value, m.attribution); });
        } catch (e) { /* defensive */ }
    };
    document.head.appendChild(script);

    window.PyramidWebVitals = { loaded: true };
})();
