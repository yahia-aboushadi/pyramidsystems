/* Pyramid Systems - UTM + Attribution capture (v2)
   ==================================================
   Runs on every page. Captures attribution and engagement data that
   forms read at submit time.

   What it tracks
   --------------
   First touch (locked after first visit, never overwritten):
     first_utm_source / first_utm_medium / first_utm_campaign / first_utm_content
     first_landing_page
     first_referrer_url
     first_visit_ts

   Last touch (refreshed on new session boundary or new UTM-tagged visit):
     last_utm_source / last_utm_medium / last_utm_campaign / last_utm_content
     last_landing_page
     last_referrer_url

   Engagement counters:
     session_count                - new session = 30+ minutes of inactivity
     submission_count             - bumped by forms on successful submit
     days_since_first_visit       - derived on demand (not stored)
     last_activity_ts             - internal; powers session boundary detection

   Persistence
   -----------
   Stored in localStorage under "pyramid_attribution_v2". No expiry.
   B2B sales cycles routinely exceed any sensible client-side window;
   ActiveCampaign is the source of truth for the contact record once a
   submission happens. This module is the form-fill buffer in between.

   Migration
   ---------
   Old v1 records (key "pyramid_attribution", flat utm_source/landing_page
   shape) are migrated on first read: copied into both first_* and last_*
   slots, session_count seeded to 1, then the old key is deleted.

   Referrer policy
   ---------------
   Only external referrers are captured. Same-origin referrers (in-site
   navigation) are stored as empty strings so internal page-to-page hops
   don't pollute attribution.

   Public API
   ----------
     window.PyramidAttribution.getStored()
       -> full state object or null

     window.PyramidAttribution.getCurrentPage()
       -> current page full URL (handy for form hidden inputs)

     window.PyramidAttribution.getDaysSinceFirstVisit()
       -> integer; 0 on the same calendar day as first visit

     window.PyramidAttribution.getStoredAndIncrementSubmission()
       -> full state object with submission_count already bumped and
          persisted. Forms call this at the moment of submit so the
          number sent to AC reflects the submission they're making.

     window.PyramidAttribution.reset()
       -> wipes stored state (v1 and v2 keys both)
*/
(function () {
    "use strict";

    var STORAGE_KEY      = "pyramid_attribution_v2";
    var OLD_STORAGE_KEY  = "pyramid_attribution";
    var SESSION_TIMEOUT_MS = 30 * 60 * 1000; /* 30 minutes */
    var MS_PER_DAY       = 24 * 60 * 60 * 1000;

    function blankState(now) {
        return {
            /* first touch */
            first_utm_source: "",
            first_utm_medium: "",
            first_utm_campaign: "",
            first_utm_content: "",
            first_landing_page: "",
            first_referrer_url: "",
            first_visit_ts: now,

            /* last touch */
            last_utm_source: "",
            last_utm_medium: "",
            last_utm_campaign: "",
            last_utm_content: "",
            last_landing_page: "",
            last_referrer_url: "",

            /* engagement counters */
            session_count: 0,
            submission_count: 0,
            last_activity_ts: 0,

            /* internal */
            ts: now
        };
    }

    function externalReferrer() {
        var r = document.referrer || "";
        if (!r) return "";
        try {
            var refOrigin = new URL(r).origin;
            if (refOrigin === window.location.origin) return "";
        } catch (e) {
            return "";
        }
        return r;
    }

    function migrateFromOld() {
        try {
            var raw = localStorage.getItem(OLD_STORAGE_KEY);
            if (!raw) return null;
            var old = JSON.parse(raw);
            if (!old || typeof old !== "object") {
                localStorage.removeItem(OLD_STORAGE_KEY);
                return null;
            }
            var now = Date.now();
            var seed = blankState(old.ts || now);
            seed.first_utm_source   = old.utm_source   || "";
            seed.first_utm_medium   = old.utm_medium   || "";
            seed.first_utm_campaign = old.utm_campaign || "";
            seed.first_utm_content  = old.utm_content  || "";
            seed.first_landing_page = old.landing_page || "";
            seed.first_referrer_url = old.referrer_url || "";
            seed.last_utm_source    = old.utm_source   || "";
            seed.last_utm_medium    = old.utm_medium   || "";
            seed.last_utm_campaign  = old.utm_campaign || "";
            seed.last_utm_content   = old.utm_content  || "";
            seed.last_landing_page  = old.landing_page || "";
            seed.last_referrer_url  = old.referrer_url || "";
            seed.session_count      = 1;
            seed.last_activity_ts   = now;
            localStorage.removeItem(OLD_STORAGE_KEY);
            return seed;
        } catch (e) {
            try { localStorage.removeItem(OLD_STORAGE_KEY); } catch (e2) {}
            return null;
        }
    }

    function readState() {
        try {
            var raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {
                var s = JSON.parse(raw);
                if (s && typeof s === "object") return s;
            }
            var migrated = migrateFromOld();
            if (migrated) {
                writeState(migrated);
                return migrated;
            }
            return null;
        } catch (e) { return null; }
    }

    function writeState(state) {
        try {
            state.ts = Date.now();
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch (e) { /* private mode / quota - fail silently */ }
    }

    function getUTMsFromURL() {
        try {
            var p = new URLSearchParams(window.location.search);
            return {
                utm_source:   (p.get("utm_source")   || "").trim(),
                utm_medium:   (p.get("utm_medium")   || "").trim(),
                utm_campaign: (p.get("utm_campaign") || "").trim(),
                utm_content:  (p.get("utm_content")  || "").trim()
            };
        } catch (e) {
            return { utm_source: "", utm_medium: "", utm_campaign: "", utm_content: "" };
        }
    }

    function hasAnyUTM(u) {
        return !!(u.utm_source || u.utm_medium || u.utm_campaign || u.utm_content);
    }

    function captureOnLoad() {
        var now      = Date.now();
        var utms     = getUTMsFromURL();
        var pageURL  = window.location.href;
        var referrer = externalReferrer();
        var stored   = readState();

        if (!stored) {
            stored = blankState(now);
            stored.first_utm_source   = utms.utm_source;
            stored.first_utm_medium   = utms.utm_medium;
            stored.first_utm_campaign = utms.utm_campaign;
            stored.first_utm_content  = utms.utm_content;
            stored.first_landing_page = pageURL;
            stored.first_referrer_url = referrer;
            stored.last_utm_source    = utms.utm_source;
            stored.last_utm_medium    = utms.utm_medium;
            stored.last_utm_campaign  = utms.utm_campaign;
            stored.last_utm_content   = utms.utm_content;
            stored.last_landing_page  = pageURL;
            stored.last_referrer_url  = referrer;
            stored.session_count      = 1;
            stored.last_activity_ts   = now;
            writeState(stored);
            return;
        }

        var isNewSession = !stored.last_activity_ts ||
                           (now - stored.last_activity_ts) > SESSION_TIMEOUT_MS;

        if (isNewSession) {
            stored.session_count     = (stored.session_count || 0) + 1;
            stored.last_landing_page = pageURL;
            stored.last_referrer_url = referrer;
        }

        if (hasAnyUTM(utms)) {
            stored.last_utm_source   = utms.utm_source;
            stored.last_utm_medium   = utms.utm_medium;
            stored.last_utm_campaign = utms.utm_campaign;
            stored.last_utm_content  = utms.utm_content;
            /* A returning visitor arriving via a fresh UTM tag mid-session
               is effectively a new entry point - refresh the last landing
               page + referrer so they reflect the campaign that brought
               them back. */
            if (!isNewSession) {
                stored.last_landing_page = pageURL;
                stored.last_referrer_url = referrer;
            }
        }

        stored.last_activity_ts = now;
        writeState(stored);
    }

    function daysSinceFirstVisit() {
        var s = readState();
        if (!s || !s.first_visit_ts) return 0;
        return Math.max(0, Math.floor((Date.now() - s.first_visit_ts) / MS_PER_DAY));
    }

    function getStoredAndIncrementSubmission() {
        var now = Date.now();
        var s = readState();
        if (!s) {
            /* No stored state at all (private mode, just cleared, etc.).
               Seed a minimal record so the form still has something to
               send - first_landing_page reflects the page they're
               submitting from. */
            s = blankState(now);
            s.first_landing_page = window.location.href;
            s.first_referrer_url = externalReferrer();
            s.last_landing_page  = window.location.href;
            s.last_referrer_url  = externalReferrer();
            s.session_count      = 1;
            s.last_activity_ts   = now;
        }
        s.submission_count = (s.submission_count || 0) + 1;
        s.last_activity_ts = now;
        writeState(s);
        return s;
    }

    window.PyramidAttribution = {
        getStored: readState,
        getCurrentPage: function () { return window.location.href; },
        getDaysSinceFirstVisit: daysSinceFirstVisit,
        getStoredAndIncrementSubmission: getStoredAndIncrementSubmission,
        reset: function () {
            try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
            try { localStorage.removeItem(OLD_STORAGE_KEY); } catch (e) {}
        }
    };

    captureOnLoad();
})();
