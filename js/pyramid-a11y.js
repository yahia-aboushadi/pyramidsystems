/*!
 * Pyramid Systems Accessibility Widget
 * Custom replacement for UserWay.
 *
 * Architecture:
 *   - Each feature has either a boolean toggle or named "modes" the user cycles through.
 *     Cycling order: off → mode[0] → mode[1] → ... → off.
 *   - Active modes apply `pa11y-{featureId}-{modeName}` classes to <html>.
 *   - Boolean features apply `pa11y-{featureId}` classes to <html>.
 *   - Settings persist in localStorage under 'pyramid-a11y-settings'.
 *
 * Widget protection:
 *   - The widget's own DOM is wrapped in #pyramid-a11y-widget and is exempt from
 *     every feature rule. Feature CSS is scoped to `body :not(#pyramid-a11y-widget):not(...)` patterns
 *     AND the widget UI styles use !important on background-color/color/border-color
 *     to win the cascade no matter what.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'pyramid-a11y-settings';

  /* ---------- Feature definitions ----------
   * `modes`: list of named option keys the user cycles through.
   * `iconActive`: optional alternate icon name used when ANY mode is active.
   * `cycle`: false means this is a simple boolean toggle (one click = on/off).
   */
  /* modeLabels: per-mode display text shown on the tile when that mode is active.
     If a feature has no modeLabels, the default `label` is used.
     Tooltip on the tile (title attr) shows the active mode for screen readers. */
  var FEATURES = [
    { id: 'contrast',   label: 'Contrast +',       icon: 'contrast',     modes: ['inverted', 'dark', 'light'],
      modeLabels: { inverted: 'Inverted Colors', dark: 'Dark Contrast', light: 'Light Contrast' } },
    { id: 'highlight',  label: 'Highlight Links',  icon: 'link' },
    { id: 'bigger',     label: 'Bigger Text',      icon: 'text-size',    modes: ['s', 'm', 'l', 'xl'],
      modeLabels: { s: 'Bigger Text (S)', m: 'Bigger Text (M)', l: 'Bigger Text (L)', xl: 'Bigger Text (XL)' } },
    { id: 'spacing',    label: 'Text Spacing',     icon: 'text-spacing', modes: ['light', 'moderate', 'heavy'],
      modeLabels: { light: 'Light Spacing', moderate: 'Moderate Spacing', heavy: 'Heavy Spacing' } },
    { id: 'pause',      label: 'Pause Animations', icon: 'pause',        iconActive: 'play' },
    { id: 'hideimg',    label: 'Hide Images',      icon: 'image-off' },
    { id: 'dyslexia',   label: 'Dyslexia Friendly',icon: 'dyslexia' },
    { id: 'cursor',     label: 'Cursor',           icon: 'cursor',       modes: ['big', 'mask', 'guide'],
      modeLabels: { big: 'Big Cursor', mask: 'Reading Mask', guide: 'Reading Guide' } },
    { id: 'tooltips',   label: 'Tooltips',         icon: 'tooltip' },
    { id: 'lineheight', label: 'Line Height',      icon: 'line-height',  modes: ['1-5', '1-75', '2'],
      modeLabels: { '1-5': 'Line Height 1.5×', '1-75': 'Line Height 1.75×', '2': 'Line Height 2×' } },
    { id: 'textalign',  label: 'Text Align',       icon: 'text-align',   modes: ['left', 'right', 'center', 'justify'],
      modeLabels: { left: 'Align Left', right: 'Align Right', center: 'Align Center', justify: 'Justify' } },
    { id: 'saturation', label: 'Saturation',       icon: 'saturation',   modes: ['low', 'high', 'desaturate'],
      modeLabels: { low: 'Low Saturation', high: 'High Saturation', desaturate: 'Desaturate' } }
  ];

  /* ---------- State persistence ---------- */
  function loadSettings() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); }
    catch (e) { return {}; }
  }
  function saveSettings(s) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(s)); } catch (e) {}
  }
  function clearSettings() {
    try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
  }

  var settings = loadSettings();

  /* ---------- Apply settings to <html> ---------- */
  /* UI-state classes that applySettings() must NOT strip — they're managed by
     openPanel/closePanel, not by feature toggles. */
  var UI_STATE_CLASSES = ['pa11y-panel-open'];
  function applySettings() {
    var root = document.documentElement;
    var cl = root.classList;
    /* Remove only feature-related pa11y- classes; leave UI state classes alone */
    Array.prototype.slice.call(cl).forEach(function (c) {
      if (c.indexOf('pa11y-') === 0 && UI_STATE_CLASSES.indexOf(c) === -1) cl.remove(c);
    });
    /* Apply each active toggle */
    FEATURES.forEach(function (f) {
      var v = settings[f.id];
      if (!v) return;
      if (f.modes) {
        /* v stores the mode name string */
        cl.add('pa11y-' + f.id + '-' + v);
      } else {
        cl.add('pa11y-' + f.id);
      }
    });
    if (settings.oversized) cl.add('pa11y-oversized');
    /* Manage reading-mask / reading-guide overlays */
    updateCursorOverlay();
    /* Manage tooltip mode */
    updateTooltipMode();
    /* Manage shared backdrop-filter overlay (Inverted Colors + Saturation) */
    updateFxOverlay();
  }
  applySettings();

  /* ---------- Cycle / toggle logic ---------- */
  function toggle(featureId) {
    var f = featureFor(featureId);
    if (!f) {
      /* Simple toggles outside the FEATURES list (e.g., 'oversized') */
      settings[featureId] = !settings[featureId];
    } else if (f.modes) {
      /* Cycle: off → mode[0] → mode[1] → ... → off */
      var cur = settings[featureId];
      if (!cur) {
        settings[featureId] = f.modes[0];
      } else {
        var idx = f.modes.indexOf(cur);
        if (idx === -1 || idx === f.modes.length - 1) delete settings[featureId];
        else settings[featureId] = f.modes[idx + 1];
      }
    } else {
      settings[featureId] = !settings[featureId];
    }
    saveSettings(settings);
    applySettings();
    renderPanel();
    updateFabState();
  }

  function featureFor(id) {
    for (var i = 0; i < FEATURES.length; i++) if (FEATURES[i].id === id) return FEATURES[i];
    return null;
  }

  function reset() {
    settings = {};
    clearSettings();
    applySettings();
    renderPanel();
    updateFabState();
  }

  function hasAnyActive() {
    for (var k in settings) if (settings.hasOwnProperty(k) && settings[k]) return true;
    return false;
  }

  /* ---------- Reading-mask + reading-guide overlays ---------- */
  /* Declared without initializers — see Tooltips section for why. */
  var maskEl, guideEl, mouseHandler;

  function ensureOverlay(kind) {
    if (kind === 'mask' && !maskEl) {
      maskEl = document.createElement('div');
      maskEl.id = 'pa11y-reading-mask';
      maskEl.innerHTML = '<div class="pa11y-mask-top"></div><div class="pa11y-mask-band"></div><div class="pa11y-mask-bottom"></div>';
      document.body.appendChild(maskEl);
    }
    if (kind === 'guide' && !guideEl) {
      guideEl = document.createElement('div');
      guideEl.id = 'pa11y-reading-guide';
      document.body.appendChild(guideEl);
    }
  }
  function removeOverlay(kind) {
    if (kind === 'mask' && maskEl) { maskEl.remove(); maskEl = null; }
    if (kind === 'guide' && guideEl) { guideEl.remove(); guideEl = null; }
  }
  function updateCursorOverlay() {
    var mode = settings.cursor;
    /* Always clean up existing overlays before re-attaching */
    removeOverlay('mask');
    removeOverlay('guide');
    if (mouseHandler) {
      document.removeEventListener('mousemove', mouseHandler);
      mouseHandler = null;
    }
    if (mode === 'mask') {
      ensureOverlay('mask');
      mouseHandler = function (e) {
        if (!maskEl) return;
        var bandH = 100; /* px — reading band thickness */
        var bandTop = Math.max(0, e.clientY - bandH / 2);
        var bandBottom = bandTop + bandH;
        var vh = window.innerHeight;
        var top = maskEl.querySelector('.pa11y-mask-top');
        var band = maskEl.querySelector('.pa11y-mask-band');
        var bottom = maskEl.querySelector('.pa11y-mask-bottom');
        /* Top overlay: from 0 to bandTop */
        top.style.setProperty('top', '0px', 'important');
        top.style.setProperty('height', bandTop + 'px', 'important');
        /* Band: positioned at bandTop, fixed height */
        band.style.setProperty('top', bandTop + 'px', 'important');
        band.style.setProperty('height', bandH + 'px', 'important');
        /* Bottom overlay: from bandBottom to bottom of viewport */
        bottom.style.setProperty('top', bandBottom + 'px', 'important');
        bottom.style.setProperty('height', Math.max(0, vh - bandBottom) + 'px', 'important');
      };
      document.addEventListener('mousemove', mouseHandler);
    } else if (mode === 'guide') {
      ensureOverlay('guide');
      mouseHandler = function (e) {
        if (!guideEl) return;
        /* Center the 28px band on the cursor Y */
        guideEl.style.setProperty('top', Math.max(0, e.clientY - 14) + 'px', 'important');
      };
      document.addEventListener('mousemove', mouseHandler);
    }
  }

  /* ---------- Tooltips ---------- */
  /* CSS-only tooltips using ::after don't work on void elements like <img>.
     We listen for mouseover globally and show a floating div positioned near
     the cursor, with the element's alt or title text.

     NOTE: declare without `= null` initializers — `applySettings()` runs at
     module eval (line above), and if it triggers updateTooltipMode() the
     state will be set on these vars. A `var x = null` assignment at this
     line would wipe out the state when execution reaches it. */
  var tooltipEl, tooltipOver, tooltipMove, tooltipOut;

  function widgetContains(el) {
    if (!el) return false;
    /* Bail out if any ancestor is one of our widget roots */
    var widgetIds = ['pyramid-a11y-widget', 'pyramid-a11y-panel', 'pa11y-backdrop', 'pa11y-reading-mask', 'pa11y-reading-guide', 'pa11y-tooltip'];
    var n = el;
    while (n && n !== document.body && n.nodeType === 1) {
      if (n.id && widgetIds.indexOf(n.id) !== -1) return true;
      n = n.parentNode;
    }
    return false;
  }
  function tooltipTextFor(el) {
    if (!el || el.nodeType !== 1) return '';
    /* Priority: aria-label > title > alt. We exclude empty/whitespace-only values. */
    var s = el.getAttribute && (el.getAttribute('aria-label') || el.getAttribute('title') || el.getAttribute('alt'));
    if (s && s.trim()) return s.trim();
    /* Fallback for interactive elements with no explicit label:
       show visible text content so hovering nav links / CTAs feels active.
       This matches UserWay behavior of "describing" hoverable elements. */
    var tag = (el.tagName || '').toLowerCase();
    if (tag === 'a' || tag === 'button') {
      var t = (el.textContent || '').trim().replace(/\s+/g, ' ');
      if (t) {
        if (t.length > 80) t = t.slice(0, 80) + '…';
        /* For anchors, append href hint so users see where the link goes */
        if (tag === 'a') {
          var href = el.getAttribute && el.getAttribute('href');
          if (href && href !== '#' && href.length < 60) return t + '  →  ' + href;
        }
        return t;
      }
    }
    /* Fallback for inputs: show placeholder */
    if (tag === 'input' || tag === 'textarea' || tag === 'select') {
      var p = el.getAttribute && el.getAttribute('placeholder');
      if (p && p.trim()) return p.trim();
    }
    return '';
  }
  function showTooltip(text, x, y) {
    if (!tooltipEl) {
      tooltipEl = document.createElement('div');
      tooltipEl.id = 'pa11y-tooltip';
      document.body.appendChild(tooltipEl);
    }
    tooltipEl.textContent = text;
    /* Position 14px below + 14px right of cursor, but keep inside viewport. */
    var pad = 14;
    var vw = window.innerWidth;
    var vh = window.innerHeight;
    /* Force measurement */
    tooltipEl.style.setProperty('left', '-9999px', 'important');
    tooltipEl.style.setProperty('top', '0px', 'important');
    var rect = tooltipEl.getBoundingClientRect();
    var w = rect.width, h = rect.height;
    var left = x + pad;
    var top = y + pad;
    if (left + w > vw - 4) left = Math.max(4, vw - w - 4);
    if (top + h > vh - 4) top = Math.max(4, y - h - pad);
    tooltipEl.style.setProperty('left', left + 'px', 'important');
    tooltipEl.style.setProperty('top', top + 'px', 'important');
  }
  function hideTooltip() {
    if (tooltipEl) {
      tooltipEl.remove();
      tooltipEl = null;
    }
  }
  function updateTooltipMode() {
    var on = !!settings.tooltips;
    /* Always tear down existing listeners first */
    if (tooltipOver) { document.removeEventListener('mouseover', tooltipOver); tooltipOver = null; }
    if (tooltipMove) { document.removeEventListener('mousemove', tooltipMove); tooltipMove = null; }
    if (tooltipOut)  { document.removeEventListener('mouseout',  tooltipOut);  tooltipOut  = null; }
    hideTooltip();
    if (!on) return;
    /* Track the element currently being tooltip'd so we don't restyle on every mousemove */
    var currentTarget = null;
    var currentText = '';
    tooltipOver = function (e) {
      var el = e.target;
      if (widgetContains(el)) { hideTooltip(); currentTarget = null; currentText = ''; return; }
      /* Walk up the tree to find the closest element with alt/title/aria-label */
      var n = el, txt = '';
      while (n && n !== document.body && n.nodeType === 1) {
        txt = tooltipTextFor(n);
        if (txt) break;
        n = n.parentNode;
      }
      if (txt) {
        currentTarget = n;
        currentText = txt;
        showTooltip(txt, e.clientX, e.clientY);
      } else {
        currentTarget = null;
        currentText = '';
        hideTooltip();
      }
    };
    tooltipMove = function (e) {
      if (!currentTarget || !currentText) return;
      showTooltip(currentText, e.clientX, e.clientY);
    };
    tooltipOut = function (e) {
      /* Only hide if we've left the bookmarked target */
      if (!currentTarget) return;
      var rel = e.relatedTarget;
      if (!rel || !currentTarget.contains(rel)) {
        hideTooltip();
        currentTarget = null;
        currentText = '';
      }
    };
    document.addEventListener('mouseover', tooltipOver);
    document.addEventListener('mousemove', tooltipMove);
    document.addEventListener('mouseout',  tooltipOut);
  }

  /* ---------- Backdrop-filter FX overlay ----------
     One fixed-positioned div used for BOTH Inverted Colors and Saturation
     modes. Why backdrop-filter and not filter?

     CSS `filter` on an element creates a new stacking context AND a new
     containing block for fixed-positioned descendants. The Pyramid site has
     `.footer { position: sticky; bottom: 0 }` and `.floating-badge { position: fixed }`
     — both lose viewport anchoring the moment any ancestor gets filter applied.
     The old approach applied filter to body > * or body *, which created
     stacking contexts on every ancestor of those elements, sticking the footer
     to the top of the screen and floating the award badge into the wrong place.

     `backdrop-filter` instead filters the pixels BEHIND a transparent overlay
     without modifying any other element's layout, positioning, or stacking.
     The overlay sits at z-index 2147483640 (just below the widget), is
     pointer-events: none, and is added to DOM only when a filter mode is on. */
  var fxOverlay;
  function updateFxOverlay() {
    var filters = [];
    if (settings.contrast === 'inverted') filters.push('invert(1) hue-rotate(180deg)');
    if (settings.saturation === 'low')        filters.push('saturate(0.5)');
    else if (settings.saturation === 'high')  filters.push('saturate(1.6)');
    else if (settings.saturation === 'desaturate') filters.push('grayscale(1)');

    if (filters.length === 0) {
      if (fxOverlay) { fxOverlay.remove(); fxOverlay = null; }
      return;
    }
    if (!fxOverlay) {
      fxOverlay = document.createElement('div');
      fxOverlay.id = 'pa11y-fx-overlay';
      fxOverlay.setAttribute('aria-hidden', 'true');
    }
    /* Always re-append so it ends up on top of any DOM that loaded later */
    if (document.body) document.body.appendChild(fxOverlay);
    var val = filters.join(' ');
    fxOverlay.style.setProperty('backdrop-filter', val, 'important');
    fxOverlay.style.setProperty('-webkit-backdrop-filter', val, 'important');
  }

  /* ---------- DOM ---------- */
  var widget, panel, fab, backdrop;

  function svgIcon(name) {
    var icons = {
      /* Universal accessibility symbol — person with arms outstretched.
         Filled glyph reads cleanly at small sizes (Material Design's
         "accessibility" icon path, normalized to a 24x24 viewBox). */
      'a11y':       '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="3.5" r="2.2"/><path d="M20.5 8.5h-6v13.25c0 .55-.45 1-1 1s-1-.45-1-1V15.5h-1v6.25c0 .55-.45 1-1 1s-1-.45-1-1V8.5h-6c-.55 0-1-.45-1-1s.45-1 1-1h17c.55 0 1 .45 1 1s-.45 1-1 1z"/></svg>',
      'close':      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
      'contrast':   '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20zm0-18v16a8 8 0 0 0 0-16z"/></svg>',
      'link':       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14a3.5 3.5 0 0 0 5 0l4-4a3.5 3.5 0 0 0 -5-5l-.5 .5"/><path d="M14 10a3.5 3.5 0 0 0 -5 0l-4 4a3.5 3.5 0 0 0 5 5l.5 -.5"/></svg>',
      'text-size':  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7v-2h11v2"/><path d="M9 5v14"/><path d="M7 19h4"/><path d="M15 13v-2h6v2"/><path d="M18 11v8"/><path d="M16 19h4"/></svg>',
      'text-spacing':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="7 8 3 12 7 16"/><polyline points="17 8 21 12 17 16"/><line x1="14" y1="4" x2="10" y2="20"/></svg>',
      'pause':      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="5" width="4" height="14"/><rect x="14" y="5" width="4" height="14"/></svg>',
      'play':       '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="7 4 20 12 7 20 7 4"/></svg>',
      'image-off':  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="3" x2="21" y2="21"/><path d="M15 8h.01"/><path d="M11.5 19h-7.5a2 2 0 0 1 -2 -2v-10c0-.55 .22 -1.05 .58 -1.41"/><path d="M5 5h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -.04 .39"/><path d="M3 16l5 -5c.928 -.893 2.072 -.893 3 0l5 5"/></svg>',
      'dyslexia':   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 19l4 -10l4 10"/><path d="M4 17h6"/><path d="M20 16l-4 -8"/><path d="M16 16l4 -8"/></svg>',
      'cursor':     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7.904 17.563a1.2 1.2 0 0 0 2.228 .308l2.09 -3.093l4.907 4.907a1.067 1.067 0 0 0 1.509 0l1.047 -1.047a1.067 1.067 0 0 0 0 -1.509l-4.907 -4.907l3.113 -2.09a1.2 1.2 0 0 0 -.309 -2.228l-13.582 -3.904l3.904 13.563z"/></svg>',
      'tooltip':    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12.01" y2="8"/><polyline points="11 12 12 12 12 16 13 16"/></svg>',
      'line-height':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 8 6 5 9 8"/><polyline points="3 16 6 19 9 16"/><line x1="6" y1="5" x2="6" y2="19"/><line x1="13" y1="6" x2="21" y2="6"/><line x1="13" y1="12" x2="21" y2="12"/><line x1="13" y1="18" x2="21" y2="18"/></svg>',
      'text-align': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="14" y2="12"/><line x1="4" y1="18" x2="18" y2="18"/></svg>',
      'saturation': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l5.5 9a7 7 0 1 1 -11 0z"/></svg>',
      'reset':      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4 -4"/><path d="M21 12a9 9 0 1 1 -18 0a9 9 0 0 1 18 0"/></svg>',
      'check':      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
    };
    return icons[name] || '';
  }

  function buildWidget() {
    /* Backdrop (clickable to close, behind the panel) */
    backdrop = document.createElement('div');
    backdrop.id = 'pa11y-backdrop';
    backdrop.addEventListener('click', closePanel);

    /* Container */
    widget = document.createElement('div');
    widget.id = 'pyramid-a11y-widget';
    widget.setAttribute('aria-live', 'polite');

    /* FAB */
    fab = document.createElement('button');
    fab.id = 'pyramid-a11y-fab';
    fab.type = 'button';
    fab.setAttribute('aria-label', 'Open accessibility menu');
    fab.setAttribute('aria-expanded', 'false');
    fab.innerHTML = svgIcon('a11y') + '<span class="pa11y-fab-check" aria-hidden="true">' + svgIcon('check') + '</span>';
    fab.addEventListener('click', togglePanel);

    /* Panel */
    panel = document.createElement('div');
    panel.id = 'pyramid-a11y-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Accessibility settings');
    /* Lenis smooth-scroll (lenis.min.js) hijacks all wheel events on document
       and preventDefaults them to drive its own page scroll. Without this
       attribute, mouse-wheel inside the panel would scroll the page instead
       of the panel's own overflow. Lenis honors data-lenis-prevent to opt out. */
    panel.setAttribute('data-lenis-prevent', '');
    panel.hidden = true;

    widget.appendChild(fab);
    document.body.appendChild(backdrop);
    document.body.appendChild(widget);
    document.body.appendChild(panel);

    /* Defense-in-depth: even with data-lenis-prevent, some smooth-scroll libs
       attach capture-phase listeners on document/window that fire before the
       panel's own scroll. Manually drive panel scroll on wheel and swallow
       the event so nothing else sees it. Only when the panel can actually
       scroll in the wheel direction — otherwise let it bubble normally. */
    panel.addEventListener('wheel', function (e) {
      var canScrollDown = panel.scrollTop < (panel.scrollHeight - panel.clientHeight - 1);
      var canScrollUp   = panel.scrollTop > 0;
      if ((e.deltaY > 0 && canScrollDown) || (e.deltaY < 0 && canScrollUp)) {
        panel.scrollTop += e.deltaY;
        e.preventDefault();
        e.stopPropagation();
      }
    }, { passive: false, capture: true });

    renderPanel();
    updateFabState();
  }

  function renderPanel() {
    if (!panel) return;
    var header =
      '<div class="pa11y-header">' +
        '<div class="pa11y-title">Accessibility Menu <span class="pa11y-kbd">(Ctrl + U)</span></div>' +
        '<button class="pa11y-close" type="button" aria-label="Close accessibility menu">' + svgIcon('close') + '</button>' +
      '</div>' +
      '<div class="pa11y-row pa11y-oversized-row">' +
        '<span>Oversized Widget</span>' +
        '<button class="pa11y-switch ' + (settings.oversized ? 'is--on' : '') + '" type="button" data-toggle="oversized" aria-pressed="' + (settings.oversized ? 'true' : 'false') + '"><span class="pa11y-switch-knob"></span></button>' +
      '</div>';
    var grid = '<div class="pa11y-grid">';
    FEATURES.forEach(function (f) {
      var active = !!settings[f.id];
      /* Level bars: render one bar per mode, fill bars up to current mode's index */
      var levelBars = '';
      if (f.modes) {
        var idx = active ? f.modes.indexOf(settings[f.id]) : -1;
        levelBars = '<div class="pa11y-level">';
        for (var i = 0; i < f.modes.length; i++) {
          levelBars += '<span class="pa11y-level-bar ' + (idx >= 0 && i <= idx ? 'is--on' : '') + '"></span>';
        }
        levelBars += '</div>';
      }
      var iconName = (active && f.iconActive) ? f.iconActive : f.icon;
      var checkBadge = '<span class="pa11y-tile-check" aria-hidden="true">' + svgIcon('check') + '</span>';
      /* Tile label: if a mode is active AND we have a friendly label for it, show that
         label (e.g. 'Big Cursor', 'Inverted Colors'). Otherwise fall back to the
         feature's default label. */
      var displayLabel = f.label;
      if (active && f.modeLabels && f.modeLabels[settings[f.id]]) {
        displayLabel = f.modeLabels[settings[f.id]];
      }
      grid +=
        '<button class="pa11y-tile ' + (active ? 'is--active' : '') + '" type="button" data-feature="' + f.id + '" aria-pressed="' + (active ? 'true' : 'false') + '" title="' + displayLabel + '">' +
          checkBadge +
          '<div class="pa11y-tile-icon">' + svgIcon(iconName) + '</div>' +
          '<div class="pa11y-tile-label">' + displayLabel + '</div>' +
          levelBars +
        '</button>';
    });
    grid += '</div>';
    var footer =
      '<div class="pa11y-footer">' +
        '<button class="pa11y-reset" type="button">' + svgIcon('reset') + ' Reset all</button>' +
        '<span class="pa11y-brand">Pyramid Systems</span>' +
      '</div>';
    panel.innerHTML = header + grid + footer;

    panel.querySelector('.pa11y-close').addEventListener('click', closePanel);
    panel.querySelector('.pa11y-reset').addEventListener('click', reset);
    panel.querySelectorAll('[data-feature]').forEach(function (b) {
      b.addEventListener('click', function () { toggle(b.getAttribute('data-feature')); });
    });
    panel.querySelectorAll('[data-toggle]').forEach(function (b) {
      b.addEventListener('click', function () { toggle(b.getAttribute('data-toggle')); });
    });
  }

  function updateFabState() {
    if (!fab) return;
    if (hasAnyActive()) fab.classList.add('has--active');
    else fab.classList.remove('has--active');
  }

  function openPanel() {
    if (!panel) return;
    panel.hidden = false;
    document.documentElement.classList.add('pa11y-panel-open');
    if (widget) widget.classList.add('is--open');
    if (backdrop) backdrop.classList.add('is--visible');
    fab.setAttribute('aria-expanded', 'true');
  }
  function closePanel() {
    if (!panel) return;
    panel.hidden = true;
    document.documentElement.classList.remove('pa11y-panel-open');
    if (widget) widget.classList.remove('is--open');
    if (backdrop) backdrop.classList.remove('is--visible');
    fab.setAttribute('aria-expanded', 'false');
  }
  function togglePanel() {
    if (document.documentElement.classList.contains('pa11y-panel-open')) closePanel();
    else openPanel();
  }

  /* Esc to close */
  document.addEventListener('keydown', function (e) {
    if (e.ctrlKey && (e.key === 'u' || e.key === 'U') && !e.shiftKey && !e.altKey && !e.metaKey) {
      e.preventDefault();
      togglePanel();
    } else if (e.key === 'Escape' && document.documentElement.classList.contains('pa11y-panel-open')) {
      closePanel();
    }
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildWidget);
  } else {
    buildWidget();
  }

  window.PyramidA11y = {
    open: openPanel,
    close: closePanel,
    reset: reset,
    settings: function () { return Object.assign({}, settings); }
  };
})();
