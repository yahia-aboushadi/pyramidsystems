/* =====================================================================
   pyramid-analytics.js
   Central analytics layer for Pyramid Systems site.

   What it does:
   1. Initializes window.dataLayer for GTM (no-op if GTM already did it).
   2. Pushes a page_view_attribution event with stored UTMs/landing/referrer
      from PyramidAttribution so every page-load tells GTM the attribution
      context — without each page needing to wire it manually.
   3. Exposes window.PyramidAnalytics with helpers:
        formEvent(name, formName, extra)
          → push form_step / form_submit / generate_lead / form_error
            with consistent shape, automatically including the stored
            attribution + the form's source.
        ctaClick(ctaName, location, destination)
          → push cta_click with the where/what/where-to.
        identifyLead(email, traits)
          → push identify event when we know the email (paired with
            PyramidACTracking.identify which sends to AC).
   4. Auto-binds click handlers on any element with [data-cta] so CTAs
      tagged in HTML emit cta_click events without per-page wiring.
   5. Reads ?inquiry= URL param and pre-checks the matching checkbox
      on the contact form (id="inquiry-<value>").
   6. Reads UTM params from URL and confirms PyramidAttribution stored
      them (defensive — relies on PyramidAttribution running first).

   Why this exists:
   GTM is loaded site-wide but does nothing without dataLayer pushes for
   site-specific events. This module is the single source of truth for
   pyramid-specific events so GTM tags can be configured once against a
   stable event vocabulary.

   Event vocabulary (matches GA4 recommended events where possible):
     page_view_attribution: { event, first_utm_source, first_utm_medium,
                              first_utm_campaign, last_utm_source,
                              last_utm_medium, last_utm_campaign,
                              session_count, submission_count,
                              days_since_first_visit, landing_page,
                              referrer_url }
     form_step:             { event, form_name, step, step_label }
     form_submit:           { event, form_name, form_source }
     generate_lead:         { event, form_name, lead_type,
                              utm_source, utm_medium, utm_campaign,
                              vertical }
     form_error:            { event, form_name, error_type, error_msg }
     cta_click:             { event, cta_name, cta_location,
                              cta_destination, page_path }
     identify:              { event, email_hash }
   ===================================================================== */
(function () {
    "use strict";

    /* Idempotent: don't re-initialize if PyramidAnalytics already exists. */
    if (window.PyramidAnalytics) return;

    /* Make sure dataLayer exists. GTM's head snippet already does this,
       but defensive in case GTM hasn't fired yet at script-load time. */
    window.dataLayer = window.dataLayer || [];

    function push(payload) {
        try {
            window.dataLayer.push(payload);
        } catch (e) { /* defensive */ }
    }

    /* Tiny hash for email so we can push identify events without
       leaking PII into the dataLayer. SHA-256 via SubtleCrypto when
       available; falls back to a non-cryptographic FNV-1a hash if not
       (still good enough for GA4 user_id consistency across sessions). */
    function emailHash(email) {
        if (!email) return "";
        var normalized = String(email).trim().toLowerCase();
        if (window.crypto && window.crypto.subtle && window.TextEncoder) {
            try {
                var bytes = new TextEncoder().encode(normalized);
                return window.crypto.subtle.digest("SHA-256", bytes).then(function (buf) {
                    var arr = new Uint8Array(buf);
                    return Array.prototype.map.call(arr, function (b) {
                        return ("00" + b.toString(16)).slice(-2);
                    }).join("");
                });
            } catch (e) {
                /* fall through to FNV-1a */
            }
        }
        /* FNV-1a fallback — synchronous, non-crypto, stable. */
        var h = 0x811c9dc5;
        for (var i = 0; i < normalized.length; i++) {
            h ^= normalized.charCodeAt(i);
            h = (h * 0x01000193) >>> 0;
        }
        return "fnv-" + h.toString(16);
    }

    function getAttribution() {
        try {
            if (window.PyramidAttribution && window.PyramidAttribution.getStored) {
                return window.PyramidAttribution.getStored() || {};
            }
        } catch (e) {}
        return {};
    }

    function getQueryParam(name) {
        try {
            var url = new URL(window.location.href);
            return url.searchParams.get(name);
        } catch (e) {
            /* Old browsers / weird URLs — manual parse. */
            var qs = window.location.search.replace(/^\?/, "");
            var parts = qs.split("&");
            for (var i = 0; i < parts.length; i++) {
                var kv = parts[i].split("=");
                if (decodeURIComponent(kv[0]) === name) {
                    return kv.length > 1 ? decodeURIComponent(kv[1].replace(/\+/g, " ")) : "";
                }
            }
            return null;
        }
    }

    /* ------------- Public API ------------- */

    var PyramidAnalytics = {
        /* Form lifecycle event.
           name examples: "form_start", "form_step", "form_submit",
                          "generate_lead", "form_error".
           formName: "services" | "contact" | "air_quire" | "popup_leave" |
                     "popup_magnet" | "newsletter".
           extra: any additional fields (step, error_type, lead_type, etc.) */
        formEvent: function (name, formName, extra) {
            var attribution = getAttribution();
            var payload = {
                event: name,
                form_name: formName,
                first_utm_source:   attribution.first_utm_source || "",
                first_utm_medium:   attribution.first_utm_medium || "",
                first_utm_campaign: attribution.first_utm_campaign || "",
                last_utm_source:    attribution.last_utm_source || "",
                last_utm_medium:    attribution.last_utm_medium || "",
                last_utm_campaign:  attribution.last_utm_campaign || "",
            };
            if (extra && typeof extra === "object") {
                for (var k in extra) {
                    if (Object.prototype.hasOwnProperty.call(extra, k)) {
                        payload[k] = extra[k];
                    }
                }
            }
            push(payload);
        },

        /* Convenience: GA4-style generate_lead, used on success. */
        generateLead: function (formName, leadType, extra) {
            var data = { lead_type: leadType };
            if (extra && typeof extra === "object") {
                for (var k in extra) {
                    if (Object.prototype.hasOwnProperty.call(extra, k)) {
                        data[k] = extra[k];
                    }
                }
            }
            this.formEvent("generate_lead", formName, data);
        },

        /* CTA click. Tag the <a>/<button> with data-cta="<name>"
           and optionally data-cta-location="..." in HTML, then this
           module fires cta_click automatically. Or call directly. */
        ctaClick: function (ctaName, location, destination) {
            push({
                event: "cta_click",
                cta_name: ctaName || "",
                cta_location: location || "",
                cta_destination: destination || "",
                page_path: window.location.pathname,
            });
        },

        /* Push identify with hashed email — never the raw address. */
        identifyLead: function (email, traits) {
            var hashed = emailHash(email);
            var send = function (h) {
                var payload = { event: "identify", email_hash: h };
                if (traits && typeof traits === "object") {
                    for (var k in traits) {
                        if (Object.prototype.hasOwnProperty.call(traits, k)) {
                            payload[k] = traits[k];
                        }
                    }
                }
                push(payload);
            };
            if (hashed && typeof hashed.then === "function") {
                hashed.then(send).catch(function () { send(""); });
            } else {
                send(hashed);
            }
        },

        /* Allow callers to read the inquiry param (used by contact form
           to pre-check the right checkbox). */
        getInquiryParam: function () {
            return getQueryParam("inquiry");
        },

        getVerticalParam: function () {
            return getQueryParam("vertical");
        },
    };

    window.PyramidAnalytics = PyramidAnalytics;

    /* ------------- Auto-bind: page_view_attribution ------------- */
    /* On every page load, send the stored attribution so GTM/GA4 has
       context for the entire session — not just at form-submit time. */
    function firePageView() {
        var a = getAttribution();
        push({
            event: "page_view_attribution",
            first_utm_source:   a.first_utm_source || "",
            first_utm_medium:   a.first_utm_medium || "",
            first_utm_campaign: a.first_utm_campaign || "",
            first_landing_page: a.first_landing_page || "",
            first_referrer_url: a.first_referrer_url || "",
            last_utm_source:    a.last_utm_source || "",
            last_utm_medium:    a.last_utm_medium || "",
            last_utm_campaign:  a.last_utm_campaign || "",
            last_landing_page:  a.last_landing_page || "",
            last_referrer_url:  a.last_referrer_url || "",
            session_count:    a.session_count || 0,
            submission_count: a.submission_count || 0,
            page_path: window.location.pathname,
            page_search: window.location.search,
        });
    }

    /* ------------- Helpers for rich click metadata -------------
       getVisibleText: walk the element + descendants pulling textContent,
       collapsing whitespace, capped at 120 chars. Handles links where the
       label is nested inside <span>/<div>/<svg> etc. — e.g. Webflow's
       <a><div class="button_inner-wrap"><div>Connect With Us</div></a>
       pattern, which is everywhere on this site.
       getElementPath: short CSS-like selector showing where the element
       lives in the DOM. Helps debug when many CTAs share the same data-cta.
       getElementClasses: filtered class list, drops Webflow's noise classes
       (w-inline-block etc.) for cleaner reporting. */
    function getVisibleText(el) {
        if (!el) return "";
        var txt = (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim();
        return txt.slice(0, 120);
    }
    function getElementClasses(el) {
        if (!el || !el.className) return "";
        var cls = (typeof el.className === "string" ? el.className : (el.className.baseVal || ""));
        return cls.split(/\s+/).filter(function (c) {
            return c && !c.match(/^w-(inline|w-input|tab|dyn|background|form|nav|widget)/);
        }).join(" ").slice(0, 200);
    }
    function getElementPath(el) {
        if (!el) return "";
        var parts = [];
        var cur = el;
        var depth = 0;
        while (cur && cur !== document.body && depth < 5) {
            var seg = (cur.tagName || "").toLowerCase();
            if (cur.id) { seg += "#" + cur.id; parts.unshift(seg); break; }
            var cls = getElementClasses(cur).split(" ").filter(Boolean).slice(0, 2);
            if (cls.length) seg += "." + cls.join(".");
            parts.unshift(seg);
            cur = cur.parentNode;
            depth++;
        }
        return parts.join(" > ").slice(0, 200);
    }

    /* ------------- Auto-bind: [data-cta] click tracking ------------- */
    /* Enriched: captures the actual visible label, element id, classes,
       and a short DOM path so we can disambiguate even when many CTAs
       share the same data-cta name (e.g. multiple "Federal Civilian"
       buttons across the page). */
    function bindCtaClicks() {
        document.addEventListener("click", function (ev) {
            var el = ev.target;
            while (el && el !== document) {
                if (el.dataset && el.dataset.cta) break;
                el = el.parentNode;
            }
            if (!el || el === document) return;
            push({
                event: "cta_click",
                cta_name: el.dataset.cta || "",
                cta_location: el.dataset.ctaLocation || "",
                cta_destination: el.getAttribute("href") || el.dataset.ctaDestination || "",
                cta_label_visible: getVisibleText(el),
                cta_element_id: el.id || "",
                cta_element_classes: getElementClasses(el),
                cta_element_path: getElementPath(el),
                page_path: window.location.pathname,
            });
        }, true);
    }

    /* ------------- Generic element click fallback -------------
       For any <a> or <button> that does NOT have data-cta but represents
       a meaningful click target, fire `element_click`. Lets you measure
       what users click even when those elements weren't pre-tagged. */
    function bindGenericClicks() {
        document.addEventListener("click", function (ev) {
            var el = ev.target;
            while (el && el !== document) {
                if (el.tagName === "A" || el.tagName === "BUTTON") break;
                el = el.parentNode;
            }
            if (!el || el === document) return;
            /* Skip tagged elements — cta_click already captures those. */
            if (el.dataset && el.dataset.cta) return;
            /* Skip if inside a [data-cta] ancestor — same reason. */
            var p = el.parentNode;
            while (p && p !== document) {
                if (p.dataset && p.dataset.cta) return;
                p = p.parentNode;
            }
            push({
                event: "element_click",
                element_tag: el.tagName.toLowerCase(),
                element_text: getVisibleText(el),
                element_id: el.id || "",
                element_classes: getElementClasses(el),
                element_path: getElementPath(el),
                element_href: el.getAttribute("href") || "",
                page_path: window.location.pathname,
            });
        }, true);
    }

    /* ------------- Form lifecycle tracking -------------
       form_start: fires once per <form> per page when user focuses any
                   field for the first time. Lets you compute true
                   abandonment = form_start - form_submit.
       form_field_abandon: fires when user blurs a field with empty value
                   AFTER they typed something. Tells you WHICH field made
                   them give up. */
    function bindFormLifecycle() {
        var started = new WeakSet();
        var lastTyped = new WeakMap();
        document.addEventListener("focusin", function (ev) {
            var el = ev.target;
            if (!el || !el.form) return;
            var form = el.form;
            if (started.has(form)) return;
            started.add(form);
            push({
                event: "form_start",
                form_name: form.id || form.getAttribute("name") || "unnamed_form",
                form_first_field: el.name || el.id || "",
                page_path: window.location.pathname,
            });
        }, true);
        document.addEventListener("input", function (ev) {
            if (ev.target && ev.target.form) lastTyped.set(ev.target, true);
        }, true);
        document.addEventListener("focusout", function (ev) {
            var el = ev.target;
            if (!el || !el.form) return;
            if (!lastTyped.has(el)) return; /* never typed anything */
            var val = (el.value || "").trim();
            if (val) return; /* still has content — not abandoned */
            push({
                event: "form_field_abandon",
                form_name: el.form.id || el.form.getAttribute("name") || "unnamed_form",
                field_name: el.name || el.id || "",
                field_label: getFieldLabel(el),
                page_path: window.location.pathname,
            });
        }, true);
    }
    function getFieldLabel(el) {
        if (!el) return "";
        if (el.id) {
            var lab = document.querySelector('label[for="' + el.id + '"]');
            if (lab) return getVisibleText(lab);
        }
        var p = el.parentNode;
        var depth = 0;
        while (p && depth < 3) {
            var lab2 = p.querySelector && p.querySelector("label");
            if (lab2) return getVisibleText(lab2);
            p = p.parentNode;
            depth++;
        }
        return el.getAttribute("placeholder") || "";
    }

    /* ------------- JavaScript error tracking -------------
       Catches uncaught errors AND unhandled promise rejections. Without
       this, a regression that breaks form submission can go undetected
       for days because GA4 doesn't surface JS errors. */
    function bindErrorTracking() {
        window.addEventListener("error", function (ev) {
            push({
                event: "js_error",
                error_msg: (ev.message || "").slice(0, 300),
                error_source: ev.filename || "",
                error_line: ev.lineno || 0,
                error_column: ev.colno || 0,
                error_stack: (ev.error && ev.error.stack ? ev.error.stack : "").slice(0, 500),
                page_path: window.location.pathname,
            });
        });
        window.addEventListener("unhandledrejection", function (ev) {
            var reason = ev.reason;
            var msg = (reason && reason.message) || String(reason || "");
            push({
                event: "js_error",
                error_message: ("UnhandledRejection: " + msg).slice(0, 300),
                error_source: "",
                error_line: 0,
                error_column: 0,
                error_stack: (reason && reason.stack ? reason.stack : "").slice(0, 500),
                page_path: window.location.pathname,
            });
        });
    }

    /* ------------- Auto-bind: contact-page inquiry pre-check -------------
       If a contact-page deep link includes ?inquiry=<id>, pre-check the
       matching checkbox so the destination form already has the right
       context. Supports both id-form ("general") and slug-form
       ("contract-vehicles" → "vehicles"). Defensive: only fires on
       /contact/ pages where the checkbox exists. */
    function preCheckInquiry() {
        var inquiry = getQueryParam("inquiry");
        if (!inquiry) return;
        /* Map external slugs to known checkbox IDs. */
        var aliasMap = {
            "briefing": "general",   /* no dedicated briefing checkbox */
            "demo":     "services",
            "vehicles": "vehicles",
            "contracts": "vehicles",
            "partner":  "partnership",
            "partnership": "partnership",
        };
        var id = "inquiry-" + (aliasMap[inquiry] || inquiry);
        var cb = document.getElementById(id);
        if (!cb) return;
        if (!cb.checked) {
            cb.checked = true;
            try {
                cb.dispatchEvent(new Event("change", { bubbles: true }));
            } catch (e) {
                /* IE fallback: synthetic event */
                var evt = document.createEvent("HTMLEvents");
                evt.initEvent("change", true, true);
                cb.dispatchEvent(evt);
            }
        }
        /* Push that this happened so we can measure how many briefing/
           vertical deep-links result in form submits. */
        push({
            event: "inquiry_prefill",
            inquiry_param: inquiry,
            inquiry_resolved: aliasMap[inquiry] || inquiry,
        });
    }

    /* ------------- Run on DOM ready ------------- */
    function init() {
        firePageView();
        bindCtaClicks();
        bindGenericClicks();
        bindFormLifecycle();
        bindErrorTracking();
        preCheckInquiry();
    }
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
