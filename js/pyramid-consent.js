/* Pyramid Systems — Cookie Consent (Consent Mode v2)
   ===================================================
   - Soft opt-out US default: Necessary + Analytics + Preferences granted,
     Marketing denied until user opts in. CCPA-aligned.
   - The internal variable name `functional` is retained so existing code
     references keep working, but the user-visible label is "Preferences"
     because users were confused by the term "Functional" (sounded like
     turning it off would break the site).
   - Pushes Consent Mode v2 state to window.dataLayer *before* GTM loads so
     any future GTM tags (GA4, Meta, LinkedIn) respect user choice from the
     first pageview.
   - Persistence: localStorage entry valid for 13 months (CCPA/GDPR aligned).
   - Public API: window.PyramidConsent.open(), .update({...}), .reset()
   - Banner shows only on first visit (or after consent expiry); persists
     choice across all pages.

   To wire a future GTM tag to consent state, in GTM:
     1) Enable Consent Mode v2 in GTM admin
     2) Set tag firing triggers to require the relevant consent type
        (analytics_storage for GA4, ad_storage + ad_user_data + ad_personalization for ads)
*/
(function () {
    "use strict";

    var STORAGE_KEY = "pyramid-consent";
    var EXPIRY_MS = 13 * 30 * 24 * 60 * 60 * 1000; // ~13 months

    var PRIVACY_PATH_FALLBACK = "/privacy/";

    // ---- Helpers ----
    function now() { return Date.now(); }

    function readState() {
        try {
            var raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return null;
            var s = JSON.parse(raw);
            if (!s || !s.ts) return null;
            if (now() - s.ts > EXPIRY_MS) return null;
            return s;
        } catch (e) { return null; }
    }

    function writeState(prefs) {
        var s = {
            ts: now(),
            v: 1,
            prefs: prefs
        };
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(s)); }
        catch (e) { /* private mode etc. */ }
        return s;
    }

    function defaultsForFirstVisit() {
        // Opt-out US-default with federal-contractor sensitivity:
        // - Necessary:   always on (no toggle, required for site to work)
        // - Analytics:   ON (we measure aggregate site behavior; opt-out)
        // - Preferences: ON (low-risk personalization — accessibility widget
        //               font/contrast/reading-mode prefs, dismissed-notice
        //               state. CCPA-compliant default since we don't sell
        //               or share these signals.)
        //   NOTE: internal key stayed `functional` to keep code/CSS refs
        //   intact. User-visible label is "Preferences".
        // - Marketing:   OFF (advertising/retargeting pixels require explicit
        //               opt-in. Conservative federal-contractor posture.)
        return {
            necessary: true,
            analytics: true,
            functional: true,        // user-visible label: "Preferences"
            marketing: false
        };
    }

    // Map our 4 categories → Consent Mode v2 signals.
    function toConsentModeSignals(prefs) {
        return {
            ad_storage:           prefs.marketing  ? "granted" : "denied",
            ad_user_data:         prefs.marketing  ? "granted" : "denied",
            ad_personalization:   prefs.marketing  ? "granted" : "denied",
            analytics_storage:    prefs.analytics  ? "granted" : "denied",
            functionality_storage: prefs.functional ? "granted" : "denied",
            personalization_storage: prefs.functional ? "granted" : "denied",
            security_storage:     "granted" // always on
        };
    }

    // Push to dataLayer. Uses gtag() if present, otherwise raw push.
    function pushConsent(mode, prefs) {
        window.dataLayer = window.dataLayer || [];
        var signals = toConsentModeSignals(prefs);
        // Standard gtag pattern (works whether or not GTM is loaded yet)
        function gtag() { window.dataLayer.push(arguments); }
        gtag("consent", mode, signals);
        // Also emit a high-level custom event so downstream tags can react
        // (e.g., conditionally fire a Meta Pixel once marketing is granted).
        window.dataLayer.push({
            event: "pyramid_consent_" + mode,
            consent_prefs: prefs,
            consent_signals: signals,
            timestamp: new Date().toISOString()
        });
    }

    // ---- Early default push (before banner renders / before GTM loads) ----
    // Read any saved state and push it as default. If none saved, push the
    // opt-out defaults. This is the critical Consent Mode v2 requirement:
    // GTM defaults must be set *before* tags are loaded.
    var existing = readState();
    var initialPrefs = existing ? existing.prefs : defaultsForFirstVisit();
    pushConsent("default", initialPrefs);

    // Determine the root-relative path to /privacy/ from this page.
    function privacyHref() {
        var p = window.location.pathname;
        // /privacy/ at root
        if (/^\/privacy\/?$/.test(p)) return "#"; // already on it
        var depth = (p.match(/\//g) || []).length - 1;
        if (depth < 0) depth = 0;
        if (p.endsWith("/")) depth -= 1;
        var prefix = "";
        for (var i = 0; i < depth; i++) prefix += "../";
        return prefix + "privacy/index.html";
    }

    // ---- DOM rendering ----
    var bannerEl = null;
    var modalEl = null;
    var backdropEl = null;
    var rootEl = null;
    var lastFocus = null;

    function ensureRoot() {
        if (rootEl) return rootEl;
        rootEl = document.createElement("div");
        rootEl.className = "pc-root";
        rootEl.setAttribute("aria-live", "polite");
        document.body.appendChild(rootEl);
        return rootEl;
    }

    function renderBanner() {
        if (bannerEl) return bannerEl;
        ensureRoot();
        bannerEl = document.createElement("div");
        bannerEl.className = "pc-banner";
        bannerEl.setAttribute("role", "region");
        bannerEl.setAttribute("aria-label", "Cookies and tracking notice");
        // v4 layout: small circular icon + title on one row, then body, then
        // three actions. No 2-column split, no external image, no corner ×.
        // Background relies on backdrop-filter blur to read as glassy.
        bannerEl.innerHTML = [
            '<div class="pc-banner-head">',
                '<span class="pc-banner-icon" aria-hidden="true">',
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
                        '<path d="M21.6 12a9.6 9.6 0 1 1-9.6-9.6 5 5 0 0 0 5 5 4.5 4.5 0 0 0 4.5 4.5"/>',
                        '<circle cx="8.5" cy="8.5" r=".5"/>',
                        '<circle cx="15.5" cy="15.5" r=".5"/>',
                        '<circle cx="10" cy="14" r=".5"/>',
                    '</svg>',
                '</span>',
                '<h2 class="pc-banner-title">Cookies &amp; tracking</h2>',
            '</div>',
            '<p class="pc-banner-body">We care about your privacy. We use minimal cookies to operate the site, and with your permission, to understand how visitors use it. We don\'t sell your data. ',
                '<a href="' + privacyHref() + '">Learn more</a>',
            '</p>',
            '<div class="pc-banner-actions">',
                '<button type="button" class="pc-btn pc-btn--primary" data-pc-action="accept-all">Accept all</button>',
                '<button type="button" class="pc-btn pc-btn--ghost" data-pc-action="manage">Manage</button>',
                '<button type="button" class="pc-btn pc-btn--link" data-pc-action="dismiss" aria-label="Dismiss. We will ask again on your next visit.">Dismiss</button>',
            '</div>'
        ].join("");
        rootEl.appendChild(bannerEl);

        bannerEl.addEventListener("click", function (e) {
            var t = e.target.closest("[data-pc-action]");
            if (!t) return;
            var action = t.getAttribute("data-pc-action");
            if (action === "accept-all") { acceptAll(); }
            else if (action === "manage") { openModal(); }
            else if (action === "dismiss") { dismissWithCurrent(); }
        });
        return bannerEl;
    }

    function showBanner() {
        renderBanner();
        // Force reflow then add visible class (so transition runs)
        bannerEl.offsetWidth;
        bannerEl.classList.add("is-visible");
    }
    function hideBanner() {
        if (!bannerEl) return;
        bannerEl.classList.remove("is-visible");
    }

    function renderModal() {
        if (modalEl) return modalEl;
        ensureRoot();
        backdropEl = document.createElement("div");
        backdropEl.className = "pc-modal-backdrop";
        backdropEl.setAttribute("aria-hidden", "true");
        backdropEl.addEventListener("click", closeModal);
        rootEl.appendChild(backdropEl);

        modalEl = document.createElement("div");
        modalEl.className = "pc-modal";
        modalEl.setAttribute("role", "dialog");
        modalEl.setAttribute("aria-modal", "true");
        modalEl.setAttribute("aria-labelledby", "pc-modal-title");
        modalEl.innerHTML = [
            '<div class="pc-modal-head">',
                '<h2 id="pc-modal-title" class="pc-modal-title">Cookie Preferences</h2>',
                '<button type="button" class="pc-modal-close" data-pc-action="close" aria-label="Close preferences">',
                    '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
                        '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
                    '</svg>',
                '</button>',
            '</div>',
            '<p class="pc-modal-intro">Choose which cookies you allow. We don\'t sell your personal information. See our <a href="' + privacyHref() + '">Privacy Policy</a> for full detail.</p>',
            categoryBlock("necessary", "Strictly necessary", "Required for the site to work: accessibility preferences, session security, basic functionality.", true, true),
            categoryBlock("analytics", "Analytics", "Helps us understand how the site is used (page views, time on page) so we can improve it. Anonymized IP, no cross-site tracking.", true, false),
            categoryBlock("functional", "Preferences", "Remembers settings you choose so you don't have to set them again (accessibility widget choices like font size and contrast, dismissed notices). Stored on your device only.", true, false),
            categoryBlock("marketing", "Marketing", "Conversion pixels (when we run paid campaigns) to measure ad effectiveness. We do not run retargeting against federal government IP ranges.", false, false),
            '<div class="pc-modal-actions">',
                '<div class="pc-modal-actions-left">',
                    '<button type="button" class="pc-btn pc-btn--link" data-pc-action="reject-all">Reject all</button>',
                '</div>',
                '<div class="pc-modal-actions-right">',
                    '<button type="button" class="pc-btn pc-btn--ghost" data-pc-action="save">Save preferences</button>',
                    '<button type="button" class="pc-btn pc-btn--primary" data-pc-action="accept-all">Accept all</button>',
                '</div>',
            '</div>'
        ].join("");
        rootEl.appendChild(modalEl);

        modalEl.addEventListener("click", function (e) {
            var t = e.target.closest("[data-pc-action]");
            if (!t) return;
            var action = t.getAttribute("data-pc-action");
            if (action === "close") closeModal();
            else if (action === "accept-all") { acceptAll(); closeModal(); }
            else if (action === "reject-all") { rejectAll(); closeModal(); }
            else if (action === "save") { saveFromModal(); closeModal(); }
        });
        // ESC key to close
        modalEl.addEventListener("keydown", function (e) {
            if (e.key === "Escape") { e.preventDefault(); closeModal(); }
            if (e.key === "Tab") trapFocus(e);
        });
        return modalEl;
    }

    function categoryBlock(id, title, desc, defaultOn, locked) {
        var lockedAttr = locked ? "disabled checked" : (defaultOn ? "checked" : "");
        var lockedNote = locked ? '<div class="pc-category-locked">Always on (cannot be disabled).</div>' : "";
        return [
            '<div class="pc-category">',
                '<div class="pc-category-row">',
                    '<div class="pc-category-text">',
                        '<h3 class="pc-category-title">' + title + '</h3>',
                        '<p class="pc-category-desc">' + desc + '</p>',
                        lockedNote,
                    '</div>',
                    '<label class="pc-toggle" aria-label="' + title + '">',
                        '<input type="checkbox" data-pc-pref="' + id + '" ' + lockedAttr + '/>',
                        '<span class="pc-toggle-slider"></span>',
                    '</label>',
                '</div>',
            '</div>'
        ].join("");
    }

    function syncModalFromPrefs(prefs) {
        if (!modalEl) return;
        ["necessary", "analytics", "functional", "marketing"].forEach(function (k) {
            var input = modalEl.querySelector('input[data-pc-pref="' + k + '"]');
            if (!input) return;
            if (k === "necessary") { input.checked = true; return; }
            input.checked = !!prefs[k];
        });
    }

    function openModal() {
        renderModal();
        var current = readState();
        var prefs = current ? current.prefs : initialPrefs;
        syncModalFromPrefs(prefs);
        backdropEl.classList.add("is-visible");
        modalEl.classList.add("is-visible");
        lastFocus = document.activeElement;
        // Focus the close button so screen readers + keyboard users land in-modal.
        setTimeout(function () {
            var closeBtn = modalEl.querySelector(".pc-modal-close");
            if (closeBtn) closeBtn.focus();
        }, 30);
    }
    function closeModal() {
        if (!modalEl) return;
        modalEl.classList.remove("is-visible");
        backdropEl.classList.remove("is-visible");
        if (lastFocus && typeof lastFocus.focus === "function") {
            try { lastFocus.focus(); } catch (e) {}
        }
    }
    function trapFocus(e) {
        var focusables = modalEl.querySelectorAll('button, input:not([disabled]), a[href]');
        if (!focusables.length) return;
        var first = focusables[0];
        var last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) {
            e.preventDefault(); last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault(); first.focus();
        }
    }

    // ---- Choice handlers ----
    function acceptAll() {
        var prefs = { necessary: true, analytics: true, functional: true, marketing: true };
        writeState(prefs);
        pushConsent("update", prefs);
        hideBanner();
    }
    function rejectAll() {
        var prefs = { necessary: true, analytics: false, functional: false, marketing: false };
        writeState(prefs);
        pushConsent("update", prefs);
        hideBanner();
    }
    function dismissWithCurrent() {
        // Dismiss = "ask me again later". We do NOT persist a choice to
        // localStorage, so the banner will reappear on the next page visit.
        // The page-load default consent state pushed via gtag('consent','default',...)
        // already applies (Necessary + Analytics granted, Marketing denied),
        // so no additional dataLayer update is needed here.
        hideBanner();
    }
    function saveFromModal() {
        var prefs = { necessary: true };
        ["analytics", "functional", "marketing"].forEach(function (k) {
            var input = modalEl.querySelector('input[data-pc-pref="' + k + '"]');
            prefs[k] = !!(input && input.checked);
        });
        writeState(prefs);
        pushConsent("update", prefs);
        hideBanner();
    }

    // ---- Boot ----
    function boot() {
        var saved = readState();
        if (!saved) {
            // First visit OR consent expired — show banner.
            // Delay 600ms so it doesn't compete with page entrance animations.
            setTimeout(showBanner, 600);
        }
    }

    // ---- Public API ----
    window.PyramidConsent = {
        open: function () { openModal(); },
        update: function (prefs) {
            var merged = Object.assign({ necessary: true }, prefs || {});
            writeState(merged);
            pushConsent("update", merged);
        },
        reset: function () {
            try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
            location.reload();
        },
        getPrefs: function () {
            var s = readState();
            return s ? s.prefs : null;
        }
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
