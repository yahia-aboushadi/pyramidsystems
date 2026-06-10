/* Pyramid Systems — ActiveCampaign Site Tracking wrapper
   =======================================================
   THIN WRAPPER. The actual AC vgo() tracker is now loaded by GTM as
   a Custom HTML tag ("AC - Site Tracker (vgo)") with Consent Mode v2
   gating: it fires only when analytics_storage = granted, and is
   queued by GTM if consent is denied at page load (auto-fires later
   if consent flips to granted).

   What lives here
   ---------------
   Only window.PyramidACTracking.identify(email) — called by every
   form's submit handler to link the anonymous browsing session to
   the AC contact identified by the email they just provided.

   Why a wrapper instead of just calling vgo() directly from form code
   ------------------------------------------------------------------
   1. If consent is denied, vgo never loads. We need identify() to
      silently no-op so form submits don't throw.
   2. The "process identify" pattern + email-key payload is AC's
      documented API — we keep that contract in one place so future
      AC API changes are a one-line edit.
   3. isLoaded() is useful for debugging (e.g., in DevTools console).

   To move AC tracking to a different platform (Segment, RudderStack,
   internal events bus): swap the body of identify() here. Form-submit
   call sites do not change.

   See: gtm-container-pyramid-systems.json → "AC - Site Tracker (vgo)"
        for the consent-gated tag that loads vgo().
   See: GTM_IMPORT_README.md → Consent architecture section.
*/
(function () {
    "use strict";

    function identify(email) {
        if (!email) return;
        try {
            if (typeof window.vgo === "function") {
                /* AC's identify pattern. vgo queues calls before its CDN
                   script has loaded and replays them once ready. */
                window.vgo("process", "identify", { email: String(email).trim() });
            }
            /* If vgo isn't loaded (consent denied, GTM blocked, etc.)
               we silently no-op. The form still submits to AC via JSONP
               and the contact gets created server-side; we just don't
               get the cross-session browsing stitch. */
        } catch (e) { /* defensive */ }
    }

    function isLoaded() {
        return typeof window.vgo === "function";
    }

    window.PyramidACTracking = {
        identify: identify,
        isLoaded: isLoaded,
    };
})();
