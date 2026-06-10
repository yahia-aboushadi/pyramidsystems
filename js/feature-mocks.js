/* Feature Mocks v11 — opacity-based trigger + count-up + global parallax.

   How the trigger works
   ---------------------
   On the live page each card sits inside a .services_window.is--N element.
   GSAP/Webflow fades that wrapper's inline-style opacity from 0 → 1 as the
   sticky-scroll carousel reveals each card. The most accurate "user is
   actually looking at this card" signal is therefore that opacity value.

   - For each .feature-mock we walk up to the nearest .services_window.
   - A MutationObserver watches that wrapper's `style` attribute. When the
     parsed opacity crosses OPACITY_VISIBLE we startLoop(); below it we
     stopLoop() and reset state so the next reveal plays cleanly from zero.
   - On preview-mocks.html (no .services_window ancestor) we fall back to an
     IntersectionObserver-based trigger so the preview still animates.

   While running
   -------------
   - Loop interval: LOOP_MS (active animation + brief reset).
   - Counters initialize to 0 synchronously on page load so the final values
     never flash before .is-active is applied.
   - Parallax: a single document-level mousemove listener tilts every mock
     currently in the viewport (separate IO that only tracks intersection
     for parallax purposes). Disabled on touch and prefers-reduced-motion.
*/
(function () {
  if (typeof window === "undefined" || typeof document === "undefined") return;

  var REDUCE = window.matchMedia
    && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var HAS_HOVER = window.matchMedia
    && window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  var LOOP_MS = 13000;
  var RESET_MS = 600;
  var TILT_MAX_X = 7;
  var TILT_MAX_Y = 11;
  var OPACITY_VISIBLE = 0.3; // .services_window opacity at/above this = "card is on screen"

  function init() {
    var mocks = Array.prototype.slice.call(
      document.querySelectorAll(".feature-mock")
    );
    if (!mocks.length) return;

    for (var i = 0; i < mocks.length; i++) initCounters(mocks[i]);

    if (REDUCE) {
      mocks.forEach(function (el) {
        el.classList.add("is-active");
        finalizeCounters(el);
      });
      return;
    }

    var visibleMocks = []; // for parallax — not the same as "loop is running"
    var loops = new WeakMap();

    function startLoop(el) {
      if (loops.get(el)) return;

      el.classList.remove("is-active");
      initCounters(el);

      var firstFire = window.setTimeout(function () {
        el.classList.add("is-active");
        playCounters(el);
      }, 60);

      var intervalId = window.setInterval(function () {
        el.classList.remove("is-active");
        initCounters(el);
        window.setTimeout(function () {
          el.classList.add("is-active");
          playCounters(el);
        }, RESET_MS);
      }, LOOP_MS);

      loops.set(el, { interval: intervalId, firstFire: firstFire });
    }

    function stopLoop(el) {
      var entry = loops.get(el);
      if (entry) {
        window.clearTimeout(entry.firstFire);
        window.clearInterval(entry.interval);
        loops.delete(el);
      }
      el.classList.remove("is-active");
      initCounters(el);
    }

    // === Animation trigger — prefer opacity watching on .services_window ===
    mocks.forEach(function (mock) {
      var serviceWindow = mock.closest && mock.closest(".services_window");

      if (serviceWindow && typeof MutationObserver !== "undefined") {
        setupOpacityTrigger(mock, serviceWindow, startLoop, stopLoop);
      } else {
        setupViewportTrigger(mock, startLoop, stopLoop);
      }
    });

    // === Parallax visibility tracking — its own IntersectionObserver ===
    if (HAS_HOVER && "IntersectionObserver" in window) {
      var parallaxIO = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          var el = entry.target;
          if (entry.isIntersecting) {
            if (!findVisible(visibleMocks, el)) {
              visibleMocks.push({ el: el, rect: el.getBoundingClientRect() });
            }
          } else {
            var idx = findVisibleIndex(visibleMocks, el);
            if (idx !== -1) {
              visibleMocks.splice(idx, 1);
              el.style.removeProperty("--rx");
              el.style.removeProperty("--ry");
            }
          }
        });
      }, { threshold: 0 });

      mocks.forEach(function (el) { parallaxIO.observe(el); });
      initGlobalParallax(visibleMocks);
    }

    // === Trust bento — play-once when scrolled into view ===
    initTrustBento();
  }

  function initTrustBento() {
    var bento = document.querySelector(".trust-bento");
    if (!bento) return;

    initCounters(bento);

    if (REDUCE) {
      bento.classList.add("is-active");
      finalizeCounters(bento);
      return;
    }

    if (!("IntersectionObserver" in window)) {
      bento.classList.add("is-active");
      playCounters(bento);
      return;
    }

    var played = false;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!played && entry.intersectionRatio >= 0.3) {
          played = true;
          bento.classList.add("is-active");
          playCounters(bento);
          io.disconnect();
        }
      });
    }, { threshold: [0, 0.15, 0.3, 0.5] });

    io.observe(bento);
  }

  /* === Trigger strategies =================================================== */

  function setupOpacityTrigger(mock, serviceWindow, startLoop, stopLoop) {
    var wasVisible = false;

    function readOpacity() {
      // Inline style first (GSAP / Webflow set it there). Fall back to
      // computed style so cards without an inline opacity also work.
      var raw = serviceWindow.style && serviceWindow.style.opacity;
      var op = raw !== "" && raw != null ? parseFloat(raw) : NaN;
      if (isNaN(op)) {
        var computed = window.getComputedStyle(serviceWindow);
        op = parseFloat(computed.opacity);
      }
      if (isNaN(op)) op = 1;
      return op;
    }

    function check() {
      var opacity = readOpacity();
      var isVisible = opacity >= OPACITY_VISIBLE;
      if (isVisible && !wasVisible) {
        startLoop(mock);
      } else if (!isVisible && wasVisible) {
        stopLoop(mock);
      }
      wasVisible = isVisible;
    }

    check(); // initial state

    var observer = new MutationObserver(check);
    observer.observe(serviceWindow, {
      attributes: true,
      attributeFilter: ["style", "class"]
    });
  }

  function setupViewportTrigger(mock, startLoop, stopLoop) {
    if (!("IntersectionObserver" in window)) {
      startLoop(mock);
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.intersectionRatio >= 0.5) {
          startLoop(mock);
        } else if (!entry.isIntersecting) {
          stopLoop(mock);
        }
      });
    }, { threshold: [0, 0.5, 0.85], rootMargin: "0px 0px -5% 0px" });

    io.observe(mock);
  }

  function findVisible(list, el) {
    for (var i = 0; i < list.length; i++) if (list[i].el === el) return list[i];
    return null;
  }
  function findVisibleIndex(list, el) {
    for (var i = 0; i < list.length; i++) if (list[i].el === el) return i;
    return -1;
  }

  /* === Counters ============================================================ */

  function initCounters(scope) {
    var counters = scope.querySelectorAll("[data-count-to]");
    for (var i = 0; i < counters.length; i++) {
      var el = counters[i];
      var raw = el.getAttribute("data-count-to") || "0";
      var suffix = el.getAttribute("data-count-suffix") || "";
      var dot = raw.indexOf(".");
      var decimals = dot === -1 ? 0 : (raw.length - dot - 1);
      el._fm_to = parseFloat(raw);
      el._fm_decimals = decimals;
      el._fm_suffix = suffix;
      el._fm_run = (el._fm_run || 0) + 1;
      el.textContent = (0).toFixed(decimals) + suffix;
    }
  }

  function playCounters(scope) {
    var counters = scope.querySelectorAll("[data-count-to]");
    for (var i = 0; i < counters.length; i++) animateCounter(counters[i]);
  }

  function animateCounter(el) {
    var to = el._fm_to;
    var suffix = el._fm_suffix;
    var decimals = el._fm_decimals;
    var delay = parseFloat(el.getAttribute("data-count-delay") || "0") * 1000;
    var duration = parseFloat(el.getAttribute("data-count-duration") || "1.5") * 1000;
    var run = el._fm_run;

    window.setTimeout(function () {
      if (el._fm_run !== run) return;
      var startTs = null;
      function step(ts) {
        if (el._fm_run !== run) return;
        if (startTs === null) startTs = ts;
        var t = (ts - startTs) / duration;
        if (t > 1) t = 1;
        var eased = 1 - Math.pow(1 - t, 3);
        el.textContent = (eased * to).toFixed(decimals) + suffix;
        if (t < 1) window.requestAnimationFrame(step);
      }
      window.requestAnimationFrame(step);
    }, delay);
  }

  function finalizeCounters(scope) {
    var counters = scope.querySelectorAll("[data-count-to]");
    for (var i = 0; i < counters.length; i++) {
      var el = counters[i];
      el.textContent = el._fm_to.toFixed(el._fm_decimals) + el._fm_suffix;
    }
  }

  /* === Global parallax ===================================================== */

  function initGlobalParallax(visibleMocks) {
    var pending = false;
    var lastX = -1;
    var lastY = -1;

    function refreshRects() {
      for (var i = 0; i < visibleMocks.length; i++) {
        visibleMocks[i].rect = visibleMocks[i].el.getBoundingClientRect();
      }
    }

    function applyTilt() {
      if (lastX < 0) return;
      var vw = window.innerWidth;
      var vh = window.innerHeight;
      for (var i = 0; i < visibleMocks.length; i++) {
        var m = visibleMocks[i];
        var rect = m.rect;
        if (!rect.width || !rect.height) continue;
        var cx = rect.left + rect.width / 2;
        var cy = rect.top + rect.height / 2;
        var dx = (lastX - cx) / vw;
        var dy = (lastY - cy) / vh;
        if (dx < -0.5) dx = -0.5; else if (dx > 0.5) dx = 0.5;
        if (dy < -0.5) dy = -0.5; else if (dy > 0.5) dy = 0.5;
        var ry = dx * 2 * TILT_MAX_Y;
        var rx = -dy * 2 * TILT_MAX_X;
        m.el.style.setProperty("--rx", rx.toFixed(2) + "deg");
        m.el.style.setProperty("--ry", ry.toFixed(2) + "deg");
      }
    }

    function schedule() {
      if (pending) return;
      pending = true;
      window.requestAnimationFrame(function () {
        pending = false;
        applyTilt();
      });
    }

    function onMove(e) {
      lastX = e.clientX;
      lastY = e.clientY;
      schedule();
    }

    function onScroll() {
      refreshRects();
      schedule();
    }

    function resetAll() {
      for (var i = 0; i < visibleMocks.length; i++) {
        visibleMocks[i].el.style.setProperty("--rx", "0deg");
        visibleMocks[i].el.style.setProperty("--ry", "0deg");
      }
    }

    document.addEventListener("mousemove", onMove, { passive: true });
    document.addEventListener("mouseleave", resetAll, { passive: true });
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", function () { refreshRects(); schedule(); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
