/*!
 * Pyramid Systems — Mobile Menu Overlay
 * ======================================
 * Self-contained mobile menu. Loaded site-wide via templates/header.html,
 * but only ACTIVATES at viewport ≤991px. On desktop it does absolutely
 * nothing — the existing header nav is untouched.
 *
 * How it works
 * ------------
 *   1. At page load, builds the overlay HTML and appends to <body>.
 *   2. Hooks the existing .header .menu hamburger button in capture
 *      phase so it runs BEFORE Webflow's IX2 click handler. On mobile
 *      it preventDefault+stopImmediatePropagation, then toggles our
 *      overlay open. On desktop it does nothing — Webflow runs as normal.
 *   3. Dropdowns are accordion-style (Services, Contract Vehicles, About,
 *      Insights). Single-open-at-a-time. Tapping a sub-link closes the
 *      menu and lets the link navigate.
 *   4. Scroll lock uses position:fixed body trick so iOS Safari can't
 *      scroll through the overlay AND the user returns to the exact
 *      scroll position when they close.
 *
 * Rollback
 * --------
 *   Delete this file + remove the <script> tag from templates/header.html
 *   + remove the marked CSS block from css/styles.css + rerun
 *   scripts/apply_templates.py. See MOBILE_MENU_ROLLBACK.md.
 */
(function () {
    "use strict";

    /* Double-load guard — if this script ends up loaded twice for any
       reason (e.g. a page accidentally references it directly in addition
       to the template), only initialise once. */
    if (window.PyramidMobileMenu_initialised) return;
    window.PyramidMobileMenu_initialised = true;

    var BREAKPOINT = 991;

    /* Compute the relative-path prefix needed to reach the site root
       from the current page. Matches the {{PREFIX}} convention used by
       templates/header.html (./ for root, ../ for depth 1, etc.). */
    function computePrefix() {
        var path = window.location.pathname;
        /* Strip trailing /index.html or any /file.html so what's left
           is the containing directory (with a trailing slash). */
        path = path.replace(/\/[^/]*\.html?$/i, "/");
        if (path.charAt(path.length - 1) !== "/") path += "/";
        var depth = path.split("/").filter(Boolean).length;
        return depth === 0 ? "./" : new Array(depth + 1).join("../");
    }

    /* Inline SVG of the diagonal-NE arrow used by the site's Contact
       button. Matches the desktop look. */
    function contactArrowSVG() {
        return '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 14 14" fill="none">' +
               '<path d="M10.5005 3.49997L3.03375 10.9667" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="round"></path>' +
               '<path d="M11.2002 8.79087V2.80003H5.20936" stroke="currentColor" stroke-width="1.2" stroke-miterlimit="10" stroke-linecap="square" stroke-linejoin="bevel"></path>' +
               '</svg>';
    }

    /* +/- accordion icon mirroring .accordion_icon used by FAQ. */
    function accordionIcon() {
        return '<div class="pm-accordion-icon" aria-hidden="true"><div class="pm-h-line"></div><div class="pm-v-line"></div></div>';
    }

    function buildOverlay(prefix) {
        var html = '' +
'<aside class="pm-overlay" aria-hidden="true" id="pmOverlay">' +
    '<div class="pm-overlay-inner">' +
        '<div class="pm-overlay-eyebrow">Menu</div>' +
        '<ul class="pm-overlay-items">' +
            '<li>' +
                '<a class="row" href="' + prefix + 'solutions/air-quire.html">' +
                    '<span class="num">01</span>' +
                    '<span class="label">' +
                        '<img src="' + prefix + 'images/air-quire-Icon.png" alt="" class="pm-label-icon"/>' +
                        'AIR-Quire' +
                    '</span>' +
                '</a>' +
            '</li>' +
            '<li data-has-dropdown="true">' +
                '<button class="row" type="button" aria-expanded="false">' +
                    '<span class="num">02</span>' +
                    '<span class="label">Services</span>' +
                    accordionIcon() +
                '</button>' +
                '<ul class="sub">' +
                    '<li><a href="' + prefix + 'services/index.html">All Services</a></li>' +
                    '<li><a href="' + prefix + 'services/modernization.html">Modernization</a></li>' +
                    '<li><a href="' + prefix + 'services/cloud.html">Cloud</a></li>' +
                    '<li><a href="' + prefix + 'services/cybersecurity.html">Cybersecurity</a></li>' +
                    '<li><a href="' + prefix + 'services/devsecops.html">DevSecOps</a></li>' +
                    '<li><a href="' + prefix + 'services/analytics-ai.html">Analytics &amp; AI</a></li>' +
                '</ul>' +
            '</li>' +
            '<li data-has-dropdown="true">' +
                '<button class="row" type="button" aria-expanded="false">' +
                    '<span class="num">03</span>' +
                    '<span class="label">Contract Vehicles</span>' +
                    accordionIcon() +
                '</button>' +
                '<ul class="sub">' +
                    '<li><a href="' + prefix + 'contract-vehicles/index.html">How to procure us</a></li>' +
                    '<li><a href="' + prefix + 'contract-vehicles/gsa-it-schedule-70.html">GSA IT Schedule 70</a></li>' +
                    '<li><a href="' + prefix + 'contract-vehicles/gsa-oasis-plus.html">GSA OASIS+ Unrestricted</a></li>' +
                    '<li><a href="' + prefix + 'contract-vehicles/hhs-cms-sparc.html">HHS CMS SPARC</a></li>' +
                    '<li><a href="' + prefix + 'contract-vehicles/sec-one-it.html">SEC ONE IT</a></li>' +
                    '<li><a href="' + prefix + 'contract-vehicles/gsa-8a-stars-iii.html">GSA 8(a) STARS III</a></li>' +
                    '<li><a href="' + prefix + 'contract-vehicles/fdic-itas-iii.html">FDIC ITAS III Next Gen BOA</a></li>' +
                    '<li><a href="' + prefix + 'contract-vehicles/hud-om-bpa.html">HUD O&amp;M BPA</a></li>' +
                '</ul>' +
            '</li>' +
            '<li data-has-dropdown="true">' +
                '<button class="row" type="button" aria-expanded="false">' +
                    '<span class="num">04</span>' +
                    '<span class="label">About Pyramid</span>' +
                    accordionIcon() +
                '</button>' +
                '<ul class="sub">' +
                    '<li><a href="' + prefix + 'about-us/index.html">Who We Are</a></li>' +
                    '<li><a href="' + prefix + 'about-us/certifications/index.html">Certifications</a></li>' +
                    '<li><a href="' + prefix + 'about-us/partners/index.html">Partners</a></li>' +
                    '<li><a href="' + prefix + 'careers/index.html">Careers</a></li>' +
                '</ul>' +
            '</li>' +
            '<li data-has-dropdown="true">' +
                '<button class="row" type="button" aria-expanded="false">' +
                    '<span class="num">05</span>' +
                    '<span class="label">Insights</span>' +
                    accordionIcon() +
                '</button>' +
                '<ul class="sub">' +
                    '<li><a href="' + prefix + 'insights/blog/index.html">Blog</a></li>' +
                    '<li><a href="' + prefix + 'insights/case-studies/index.html">Case Studies</a></li>' +
                    '<li><a href="' + prefix + 'insights/news/index.html">News</a></li>' +
                '</ul>' +
            '</li>' +
            '<li>' +
                '<a class="row" href="' + prefix + 'contact/index.html">' +
                    '<span class="num">06</span>' +
                    '<span class="label">Contact</span>' +
                    '<span class="pm-arrow" aria-hidden="true">' + contactArrowSVG() + '</span>' +
                '</a>' +
            '</li>' +
        '</ul>' +
        '<div class="pm-overlay-footer">' +
            '<div class="row">' +
                '<div class="row-label">Get in touch</div>' +
                '<a href="mailto:info@pyramidsystems.com">info@pyramidsystems.com</a>' +
                '<a href="tel:+17035530800">+1 (703) 553-0800</a>' +
            '</div>' +
            '<div class="row">' +
                '<div class="row-label">Headquarters</div>' +
                '<span class="addr">1593 Spring Hill Road, Suite 700<br/>Vienna, VA 22182</span>' +
            '</div>' +
            '<div class="meta">' +
                '<span>&copy; Pyramid Systems</span>' +
                '<span class="legal-links">' +
                    '<a href="' + prefix + 'privacy/index.html">Privacy</a>' +
                    '<span class="sep" aria-hidden="true">·</span>' +
                    '<a href="' + prefix + 'terms-of-use/index.html">Terms of Use</a>' +
                '</span>' +
            '</div>' +
        '</div>' +
    '</div>' +
'</aside>';
        return html;
    }

    function init() {
        var menuBtn = document.querySelector(".header .menu");
        if (!menuBtn) return; /* Page has no header (test pages, etc.) */

        /* Don't add the overlay twice if something else already did. */
        if (document.getElementById("pmOverlay")) return;

        var prefix = computePrefix();
        var wrap = document.createElement("div");
        wrap.innerHTML = buildOverlay(prefix);
        document.body.appendChild(wrap.firstChild);

        var overlay = document.getElementById("pmOverlay");

        function isMobile() {
            return window.matchMedia("(max-width: " + BREAKPOINT + "px)").matches;
        }

        /* Scroll lock with position-fixed body so iOS Safari can't bypass. */
        var lockedScrollY = 0;
        function lockScroll() {
            lockedScrollY = window.pageYOffset || document.documentElement.scrollTop || 0;
            document.body.style.position = "fixed";
            document.body.style.top = (-lockedScrollY) + "px";
            document.body.style.left = "0";
            document.body.style.right = "0";
            document.body.style.width = "100%";
        }
        function unlockScroll() {
            document.body.style.position = "";
            document.body.style.top = "";
            document.body.style.left = "";
            document.body.style.right = "";
            document.body.style.width = "";
            window.scrollTo(0, lockedScrollY);
        }

        function collapseDropdowns() {
            overlay.querySelectorAll("li.is-expanded").forEach(function (li) {
                li.classList.remove("is-expanded");
                var btn = li.querySelector("button.row");
                if (btn) btn.setAttribute("aria-expanded", "false");
            });
        }

        function setOpen(open) {
            if (open) {
                lockScroll();
            } else {
                unlockScroll();
                collapseDropdowns();
            }
            document.body.classList.toggle("pm-menu-open", open);
            overlay.setAttribute("aria-hidden", open ? "false" : "true");
            menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
        }

        /* Hamburger click — capture phase so we run BEFORE Webflow's
           bubbling IX2 handler and can prevent it. */
        menuBtn.addEventListener("click", function (e) {
            if (!isMobile()) return; /* Desktop: let Webflow handler run. */
            e.preventDefault();
            e.stopImmediatePropagation();
            setOpen(!document.body.classList.contains("pm-menu-open"));
        }, true);

        /* Overlay clicks — dropdown toggle, link close. */
        overlay.addEventListener("click", function (e) {
            var dropdownBtn = e.target.closest("button.row");
            if (dropdownBtn) {
                var li = dropdownBtn.parentElement;
                var willOpen = !li.classList.contains("is-expanded");
                /* Single-open-at-a-time. */
                overlay.querySelectorAll("li.is-expanded").forEach(function (other) {
                    if (other !== li) {
                        other.classList.remove("is-expanded");
                        var ob = other.querySelector("button.row");
                        if (ob) ob.setAttribute("aria-expanded", "false");
                    }
                });
                li.classList.toggle("is-expanded", willOpen);
                dropdownBtn.setAttribute("aria-expanded", willOpen ? "true" : "false");
                return;
            }
            var link = e.target.closest("a");
            if (link) setOpen(false);
        });

        /* Close on Escape. */
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && document.body.classList.contains("pm-menu-open")) {
                setOpen(false);
            }
        });

        /* Auto-close if viewport crosses BREAKPOINT while open. */
        window.addEventListener("resize", function () {
            if (!isMobile() && document.body.classList.contains("pm-menu-open")) {
                setOpen(false);
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
