/* Adds .is-active to each .aq-mock when it scrolls into view, which
   triggers all the CSS keyframe animations and transitions defined in
   air-quire-mocks.css. Reduced-motion users get the active state on
   load with all transitions disabled (handled in the CSS itself). */
(function () {
  if (typeof window === "undefined" || typeof document === "undefined") return;

  function init() {
    var mocks = Array.prototype.slice.call(
      document.querySelectorAll(".aq-mock, .aq-form-mock, .aq-hero-mock")
    );
    if (!mocks.length) return;

    var REDUCE = window.matchMedia
      && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (REDUCE || !("IntersectionObserver" in window)) {
      mocks.forEach(function (m) { m.classList.add("is-active"); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.intersectionRatio >= 0.25) {
          entry.target.classList.add("is-active");
          // Once activated, keep it active — these mocks tell a story
          // and replaying them on every scroll-up is distracting.
          io.unobserve(entry.target);
        }
      });
    }, { threshold: [0, 0.25, 0.5] });

    mocks.forEach(function (m) { io.observe(m); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
