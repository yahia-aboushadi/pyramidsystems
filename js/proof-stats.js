/*
 * Proof-stats counter animation
 * -----------------------------------------------------------------
 * Used on the about-us page's "we don't just talk delivery" section.
 * Each .proof-stat-num > span carries one of two data-anim values:
 *
 *   data-anim="count"  → count up from data-from (default 0) to data-to,
 *                        applying optional data-prefix and data-suffix.
 *                        Triggered when card scrolls into view.
 *
 *   data-anim="fade"   → fade and slide in. No counting (used for year
 *                        labels and pure-text values).
 *
 * Uses IntersectionObserver. Each element animates once, then unobserves.
 * Falls back gracefully if IntersectionObserver is unsupported — values
 * just show as their final state with no animation.
 */
(function () {
    'use strict';

    var COUNT_DURATION = 1500;        // ms
    var THRESHOLD = 0.35;              // fraction of element in view to trigger
    var ROOT_MARGIN = '0px 0px -10% 0px';

    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    function animateCount(el, from, to, duration, prefix, suffix) {
        var start = performance.now();
        function tick(now) {
            var t = Math.min(1, (now - start) / duration);
            var eased = easeOutCubic(t);
            var val = Math.round(from + (to - from) * eased);
            el.textContent = prefix + val + suffix;
            if (t < 1) {
                requestAnimationFrame(tick);
            }
        }
        requestAnimationFrame(tick);
    }

    function init() {
        var nodes = document.querySelectorAll('.proof-stat-num [data-anim]');
        if (!nodes.length) return;

        // No IntersectionObserver? Leave final values in place.
        if (!('IntersectionObserver' in window)) return;

        // Pre-state: set count elements to their starting value,
        // mark fade elements as pending so they don't flash.
        Array.prototype.forEach.call(nodes, function (el) {
            var anim = el.getAttribute('data-anim');
            if (anim === 'count') {
                var from = parseInt(el.getAttribute('data-from') || '0', 10);
                var prefix = el.getAttribute('data-prefix') || '';
                var suffix = el.getAttribute('data-suffix') || '';
                // Decode HTML entities in prefix (e.g., &nbsp;)
                var decoded = decodeEntities(prefix);
                el.textContent = decoded + from + suffix;
            } else if (anim === 'fade') {
                el.classList.add('is--pending');
            }
        });

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var el = entry.target;
                var anim = el.getAttribute('data-anim');
                if (anim === 'count') {
                    var from = parseInt(el.getAttribute('data-from') || '0', 10);
                    var to = parseInt(el.getAttribute('data-to'), 10);
                    var prefix = decodeEntities(el.getAttribute('data-prefix') || '');
                    var suffix = el.getAttribute('data-suffix') || '';
                    var duration = parseInt(el.getAttribute('data-duration') || String(COUNT_DURATION), 10);
                    animateCount(el, from, to, duration, prefix, suffix);
                } else if (anim === 'fade') {
                    el.classList.remove('is--pending');
                    el.classList.add('is--visible');
                }
                observer.unobserve(el);
            });
        }, { threshold: THRESHOLD, rootMargin: ROOT_MARGIN });

        Array.prototype.forEach.call(nodes, function (el) {
            observer.observe(el);
        });
    }

    // Cheap HTML-entity decoder for prefix/suffix attributes (handles &nbsp; etc.)
    var _decoder;
    function decodeEntities(str) {
        if (!str) return '';
        if (!_decoder) _decoder = document.createElement('textarea');
        _decoder.innerHTML = str;
        return _decoder.value;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
