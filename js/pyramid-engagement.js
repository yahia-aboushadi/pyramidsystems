/* Pyramid Systems — Engagement Tracking
   =====================================
   Captures user interactions with site interactive components that aren't
   covered by pyramid-analytics.js (CTA clicks, form lifecycle, attribution).

   What this tracks:
   1. Popup-leave (consultation request) shown / dismissed / submitted
   2. Popup-magnet (PDF download) shown / dismissed / submitted
   3. Cookie consent modal opens, saves, choices
   4. FAQ accordion expand / collapse, with the question text
   5. Mobile menu open / close, section expansion
   6. Site search queries on insights pages (debounced to avoid keystroke spam)
   7. Accessibility widget interactions (font size, contrast, etc.)

   All events push to window.dataLayer in the same format as
   pyramid-analytics.js, so GTM picks them up via Custom Event triggers.

   Listeners use event delegation on document so they work for elements
   added to the DOM after load (e.g., popups injected by build_service_pages).

   Loaded after pyramid-analytics.js. Safe to load on every page — handlers
   no-op if the relevant DOM doesn't exist.
*/
(function () {
    "use strict";

    if (window.PyramidEngagement) return;
    window.dataLayer = window.dataLayer || [];
    function push(payload) {
        try { window.dataLayer.push(payload); } catch (e) {}
    }
    function getText(el) {
        if (!el) return "";
        return ((el.innerText || el.textContent || "").replace(/\s+/g, " ").trim()).slice(0, 200);
    }

    /* ------------- 1. POPUPS (popup-leave + popup-magnet) -------------
       The site has two interrupt popups on service pages:
         .popup-leave   — exit-intent consultation request
         .popup-magnet  — 8s-dwell PDF download offer
       Both are styled with `opacity:0; display:none` and made visible by
       the popup controller in services/<page>.html. We watch for class
       changes (is--open / display style) via MutationObserver. */
    function bindPopupEvents() {
        var POPUP_TYPES = [
            { sel: ".popup-leave",  name: "popup_leave",  intent: "consultation" },
            { sel: ".popup-magnet", name: "popup_magnet", intent: "pdf_download" },
        ];
        POPUP_TYPES.forEach(function (pt) {
            var el = document.querySelector(pt.sel);
            if (!el) return;
            var shown = false;
            function checkVisibility() {
                var visible = el.offsetParent !== null &&
                              getComputedStyle(el).display !== "none" &&
                              parseFloat(getComputedStyle(el).opacity) > 0.1;
                if (visible && !shown) {
                    shown = true;
                    push({
                        event: "popup_shown",
                        popup_name: pt.name,
                        popup_intent: pt.intent,
                        page_path: window.location.pathname,
                    });
                } else if (!visible && shown) {
                    shown = false;
                }
            }
            /* Initial check + observer */
            checkVisibility();
            var observer = new MutationObserver(checkVisibility);
            observer.observe(el, { attributes: true, attributeFilter: ["style", "class"] });

            /* Capture dismiss via close-X buttons */
            var closeButtons = el.querySelectorAll(".pl-popup_icon-close, .pm-popup_icon-close, [data-popup-close]");
            closeButtons.forEach(function (btn) {
                btn.addEventListener("click", function () {
                    push({
                        event: "popup_dismissed",
                        popup_name: pt.name,
                        popup_intent: pt.intent,
                        dismiss_method: "close_button",
                        page_path: window.location.pathname,
                    });
                }, true);
            });

            /* Capture dismiss via overlay click (clicking outside the popup card) */
            el.addEventListener("click", function (ev) {
                if (ev.target === el) {
                    push({
                        event: "popup_dismissed",
                        popup_name: pt.name,
                        popup_intent: pt.intent,
                        dismiss_method: "overlay_click",
                        page_path: window.location.pathname,
                    });
                }
            }, true);

            /* Capture dismiss via Escape key while popup is visible */
            document.addEventListener("keydown", function (ev) {
                if (ev.key === "Escape" && shown) {
                    push({
                        event: "popup_dismissed",
                        popup_name: pt.name,
                        popup_intent: pt.intent,
                        dismiss_method: "escape_key",
                        page_path: window.location.pathname,
                    });
                }
            });
        });
    }

    /* ------------- 2. COOKIE CONSENT MODAL -------------
       Hooks into the existing pyramid-consent.js. That module pushes
       pyramid_consent_default and pyramid_consent_update events itself.
       We add UI interaction events: open, save, accept_all, reject_all,
       so reports show how often the modal is opened and what users choose. */
    function bindConsentEvents() {
        /* Modal open trigger — any [data-pc-action="open-prefs"] */
        document.addEventListener("click", function (ev) {
            var el = ev.target;
            while (el && el !== document) {
                if (el.dataset && el.dataset.pcAction === "open-prefs") break;
                el = el.parentNode;
            }
            if (!el || el === document) return;
            push({
                event: "cookie_modal_open",
                source_element: el.id || getText(el).slice(0, 50),
                page_path: window.location.pathname,
            });
        }, true);

        /* Listen for the consent_update custom event the consent module fires.
           Compute which category changed by comparing to previous state. */
        var lastPrefs = null;
        window.dataLayer.push = (function (orig) {
            return function () {
                for (var i = 0; i < arguments.length; i++) {
                    var arg = arguments[i];
                    if (arg && arg.event === "pyramid_consent_update" && arg.consent_prefs) {
                        var prefs = arg.consent_prefs;
                        var change = "manual_save";
                        if (prefs.analytics && prefs.marketing && prefs.functional) change = "accept_all";
                        else if (!prefs.analytics && !prefs.marketing && !prefs.functional) change = "reject_all";
                        push({
                            event: "cookie_prefs_saved",
                            choice_pattern: change,
                            analytics_granted: !!prefs.analytics,
                            marketing_granted: !!prefs.marketing,
                            functional_granted: !!prefs.functional,
                            page_path: window.location.pathname,
                        });
                        lastPrefs = prefs;
                    }
                }
                return orig.apply(this, arguments);
            };
        })(window.dataLayer.push);
    }

    /* ------------- 3. FAQ ACCORDION -------------
       FAQs use .accordion.is--blogs pattern with click-to-toggle. We watch
       for .is--opened class changes to know which questions get expanded. */
    function bindFAQEvents() {
        document.addEventListener("click", function (ev) {
            var el = ev.target;
            while (el && el !== document) {
                if (el.classList && (el.classList.contains("accordion") || el.classList.contains("accordion_title-wrap"))) break;
                el = el.parentNode;
            }
            if (!el || el === document) return;
            var acc = el.classList.contains("accordion") ? el : el.closest(".accordion");
            if (!acc) return;
            /* Read the question text (usually inside .accordion_title-wrap or .accordion_title) */
            var titleEl = acc.querySelector(".accordion_title, .accordion_title-wrap, h3, h4, .faq_title");
            var question = titleEl ? getText(titleEl) : getText(acc).slice(0, 80);
            /* Read state AFTER the click handler has run (next tick) */
            setTimeout(function () {
                var isOpen = acc.classList.contains("is--opened");
                push({
                    event: isOpen ? "faq_expand" : "faq_collapse",
                    question: question,
                    page_path: window.location.pathname,
                });
            }, 50);
        }, true);
    }

    /* ------------- 4. MOBILE MENU -------------
       The mobile overlay menu has an open button + close X. Internal
       sections expand/collapse via .mm-accordion. Track all three. */
    function bindMobileMenuEvents() {
        /* Open: triggered by any .menu button click on small viewports */
        document.addEventListener("click", function (ev) {
            var el = ev.target;
            while (el && el !== document) {
                if (el.classList && (el.classList.contains("menu") || el.id === "pmOpen" || el.classList.contains("pm-open"))) break;
                el = el.parentNode;
            }
            if (el && el !== document) {
                push({
                    event: "mobile_menu_open",
                    page_path: window.location.pathname,
                });
            }
        }, true);
        /* Close */
        document.addEventListener("click", function (ev) {
            var el = ev.target;
            while (el && el !== document) {
                if (el.classList && (el.id === "pmClose" || el.classList.contains("pm-close"))) break;
                el = el.parentNode;
            }
            if (el && el !== document) {
                push({
                    event: "mobile_menu_close",
                    page_path: window.location.pathname,
                });
            }
        }, true);
        /* Section expand within mobile menu */
        document.addEventListener("click", function (ev) {
            var el = ev.target;
            while (el && el !== document) {
                if (el.classList && el.classList.contains("pm-section-toggle")) break;
                el = el.parentNode;
            }
            if (!el || el === document) return;
            setTimeout(function () {
                var section = el.closest(".pm-section");
                var expanded = section && section.classList.contains("is-open");
                var sectionName = el.querySelector(".pm-section-label");
                push({
                    event: "mobile_menu_section_toggle",
                    section_name: sectionName ? getText(sectionName) : getText(el).slice(0, 50),
                    expanded: !!expanded,
                    page_path: window.location.pathname,
                });
            }, 50);
        }, true);
    }

    /* ------------- 5. SITE SEARCH (insights blog) -------------
       Watches the .pyramid-search-input field. Debounced 500ms so we
       capture finished queries, not every keystroke. */
    function bindSearchEvents() {
        var input = document.querySelector(".pyramid-search-input");
        if (!input) return;
        var lastQuery = "";
        var timer = null;
        input.addEventListener("input", function () {
            clearTimeout(timer);
            timer = setTimeout(function () {
                var q = (input.value || "").trim();
                if (!q || q === lastQuery || q.length < 2) return;
                lastQuery = q;
                push({
                    event: "site_search",
                    search_term: q.slice(0, 100),
                    search_location: window.location.pathname,
                    page_path: window.location.pathname,
                });
            }, 500);
        });
    }

    /* ------------- 6. ACCESSIBILITY WIDGET -------------
       Tracks toggles on the pyramid-a11y widget so we know which
       accessibility tools users actually use (informs which to keep
       investing in). */
    function bindA11yEvents() {
        document.addEventListener("click", function (ev) {
            var el = ev.target;
            while (el && el !== document) {
                if (el.dataset && el.dataset.a11yAction) break;
                if (el.classList && el.classList.contains("a11y-toggle")) break;
                el = el.parentNode;
            }
            if (!el || el === document) return;
            push({
                event: "accessibility_toggle",
                action: (el.dataset && el.dataset.a11yAction) || getText(el).slice(0, 50),
                page_path: window.location.pathname,
            });
        }, true);
    }

    /* ------------- 7. PUBLIC API ------------- */
    window.PyramidEngagement = {
        /* For manual triggering from custom code: */
        trackPopupShown: function (popupName, popupIntent) {
            push({
                event: "popup_shown",
                popup_name: popupName,
                popup_intent: popupIntent,
                page_path: window.location.pathname,
            });
        },
        trackPopupDismissed: function (popupName, dismissMethod) {
            push({
                event: "popup_dismissed",
                popup_name: popupName,
                dismiss_method: dismissMethod,
                page_path: window.location.pathname,
            });
        },
    };

    /* ------------- BOOT ------------- */
    function init() {
        bindPopupEvents();
        bindConsentEvents();
        bindFAQEvents();
        bindMobileMenuEvents();
        bindSearchEvents();
        bindA11yEvents();
    }
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
