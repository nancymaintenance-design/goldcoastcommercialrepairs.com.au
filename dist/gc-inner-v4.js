/* Ellis Gold Coast inner pages V4 — progressive enhancement only.
 * Native links and document scrolling remain in charge. No network requests.
 */
(() => {
  'use strict';

  const publicKey = '__ellisGoldCoastInnerV4';
  if (window[publicKey]) {
    window[publicKey].init(document);
    return;
  }

  const html = document.documentElement;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const states = new Set();
  const initialised = new WeakMap();
  let layoutTimer = null;
  let header = null;
  let headerObserver = null;
  let documentEventsReady = false;

  const clamp = (value, low, high) => Math.min(high, Math.max(low, value));
  const paused = () => reduced.matches || html.classList.contains('motion-paused') ||
    html.classList.contains('motion-hidden') || document.hidden;
  function showAll(state) {
    state.reveal.forEach(node => node.classList.add('gc-in-view'));
    state.observer?.disconnect();
  }

  function applyMotion(state) {
    const stop = paused();
    state.root.classList.toggle('gc-motion-paused', stop);
    if (stop || !state.observer) {
      showAll(state);
    } else {
      state.reveal.forEach(node => {
        if (!node.classList.contains('gc-in-view')) state.observer.observe(node);
      });
    }
  }

  function syncMotion() {
    states.forEach(applyMotion);
  }

  function updateTrack(state) {
    if (!state.track) return;
    const maximum = Math.max(0, state.track.scrollWidth - state.track.clientWidth);
    const left = clamp(state.track.scrollLeft, 0, maximum);
    if (state.previous) {
      state.previous.disabled = left <= 1;
      state.previous.setAttribute('aria-disabled', String(state.previous.disabled));
    }
    if (state.next) {
      state.next.disabled = maximum <= 1 || left >= maximum - 1;
      state.next.setAttribute('aria-disabled', String(state.next.disabled));
    }
  }

  function keepTocVisible(state, link) {
    if (!state.track || !link) return;
    const viewport = state.track.getBoundingClientRect();
    const item = link.getBoundingClientRect();
    if (item.left < viewport.left + 8) {
      state.track.scrollLeft += item.left - viewport.left - 8;
    } else if (item.right > viewport.right - 8) {
      state.track.scrollLeft += item.right - viewport.right + 8;
    }
    updateTrack(state);
  }

  function paintScroll() {
    const y = window.scrollY || window.pageYOffset || 0;
    states.forEach(state => {
      if (!state.root.isConnected) return;
      const travel = Math.max(1, state.height - window.innerHeight + state.headerHeight);
      const progress = clamp((y + state.headerHeight - state.top) / travel, 0, 1);
      const percent = `${(progress * 100).toFixed(2)}%`;
      if (percent !== state.progress) {
        state.root.style.setProperty('--gc-progress', percent);
        state.progress = percent;
      }
      // Use the same resolved CSS offset as native hash navigation. The small
      // tolerance accounts for fractional layout and integer scroll rounding.
      const readLine = y + state.anchorOffset + 2;
      let active = null;
      for (const chapter of state.chapters) {
        if (chapter.top <= readLine) active = chapter.link;
        else break;
      }
      if (active !== state.activeLink) {
        state.links.forEach(link => {
          if (link === active) link.setAttribute('aria-current', 'true');
          else link.removeAttribute('aria-current');
        });
        state.activeLink = active;
        keepTocVisible(state, active);
      }
    });
  }

  function measure() {
    layoutTimer = null;
    const y = window.scrollY || window.pageYOffset || 0;
    const hostPadding = Number.parseFloat(getComputedStyle(html).scrollPaddingTop) || 0;
    const actualHeader = header?.isConnected ? Math.max(0, Math.ceil(header.getBoundingClientRect().height)) : 0;
    states.forEach(state => {
      if (!state.root.isConnected) return;
      state.headerHeight = actualHeader;
      state.root.style.setProperty('--gc-host-scroll-padding', `${hostPadding}px`);
      state.root.style.setProperty('--gc-host-header-height', `${actualHeader}px`);
      const rootBounds = state.root.getBoundingClientRect();
      state.top = rootBounds.top + y;
      state.height = rootBounds.height;
      state.navHeight = Math.max(0, Math.ceil(state.nav?.getBoundingClientRect().height || 0));
      state.root.style.setProperty('--gc-toc-height', `${state.navHeight}px`);
      const anchorStyle = state.chapters[0]
        ? window.getComputedStyle(state.chapters[0].element)
        : null;
      const cssAnchorOffset = Number.parseFloat(anchorStyle?.scrollMarginTop || '');
      state.anchorOffset = Number.isFinite(cssAnchorOffset)
        ? hostPadding + cssAnchorOffset
        : state.headerHeight + state.navHeight + 24;
      state.chapters.forEach(chapter => {
        chapter.top = chapter.element.getBoundingClientRect().top + y;
      });
      state.chapters.sort((a, b) => a.top - b.top);
      updateTrack(state);
    });
    // Also establish the correct state after resize, font loading or a hash load.
    paintScroll();
  }

  function scheduleMeasure() {
    if (layoutTimer === null) layoutTimer = window.setTimeout(measure, 0);
  }

  function observeHeader() {
    const candidate = document.querySelector('.site-header');
    if (candidate === header) return;
    headerObserver?.disconnect();
    header = candidate;
    if (header && 'ResizeObserver' in window) {
      headerObserver = new ResizeObserver(scheduleMeasure);
      headerObserver.observe(header);
    }
    scheduleMeasure();
  }

  function initialiseRoot(root) {
    if (initialised.has(root)) return;
    const nav = root.querySelector('.gc-topic-nav');
    const links = [...root.querySelectorAll('[data-gc-toc]')];
    const elements = new Map([...root.querySelectorAll('[data-gc-chapter][id]')].map(node => [node.id, node]));
    const chapters = [];
    links.forEach(link => {
      const href = link.getAttribute('href') || '';
      if (!href.startsWith('#')) return;
      let id;
      try { id = decodeURIComponent(href.slice(1)); } catch (_) { return; }
      const element = elements.get(id);
      if (element) chapters.push({ element, link, top: 0 });
      // No click cancellation: the browser retains URL hashes, history and anchors.
      link.addEventListener('click', scheduleMeasure);
    });
    const state = {
      root, nav, links, chapters, reveal: [...root.querySelectorAll('[data-gc-reveal]')],
      track: root.querySelector('.gc-toc-track'), previous: root.querySelector('[data-gc-toc-prev]'),
      next: root.querySelector('[data-gc-toc-next]'), observer: null, resizeObserver: null,
      headerHeight: 0, navHeight: 0, anchorOffset: 0, top: 0, height: 1, progress: null, activeLink: null
    };
    initialised.set(root, state);
    states.add(state);

    if ('IntersectionObserver' in window) {
      try {
        state.observer = new IntersectionObserver(entries => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.classList.add('gc-in-view');
              state.observer.unobserve(entry.target);
            }
          });
        }, { threshold: 0.06, rootMargin: '0px 0px -28px 0px' });
      } catch (_) {
        state.observer = null;
      }
    }
    applyMotion(state);
    // Hide reveal targets only after their observer or visible fallback is ready.
    root.classList.add('gc-motion-ready');

    if (state.track) {
      state.track.addEventListener('scroll', () => updateTrack(state), { passive: true });
      const move = direction => {
        const distance = Math.max(120, state.track.clientWidth * 0.75) * direction;
        state.track.scrollBy({ left: distance, behavior: paused() ? 'auto' : 'smooth' });
        updateTrack(state);
      };
      state.previous?.addEventListener('click', () => move(-1));
      state.next?.addEventListener('click', () => move(1));
    }
    if ('ResizeObserver' in window) {
      state.resizeObserver = new ResizeObserver(scheduleMeasure);
      state.resizeObserver.observe(root);
      if (nav) state.resizeObserver.observe(nav);
      if (state.track) state.resizeObserver.observe(state.track);
    }
  }

  function init(scope = document) {
    if (scope.matches?.('.gc-v4[data-gc-v4]')) initialiseRoot(scope);
    scope.querySelectorAll?.('.gc-v4[data-gc-v4]').forEach(initialiseRoot);
    observeHeader();
    syncMotion();
    scheduleMeasure();
    if (documentEventsReady) return;
    documentEventsReady = true;
    window.addEventListener('scroll', paintScroll, { passive: true });
    window.addEventListener('resize', scheduleMeasure, { passive: true });
    window.addEventListener('hashchange', scheduleMeasure);
    window.addEventListener('pageshow', scheduleMeasure);
    document.addEventListener('visibilitychange', syncMotion);
    if (reduced.addEventListener) reduced.addEventListener('change', syncMotion);
    else reduced.addListener(syncMotion);
    if ('MutationObserver' in window) {
      new MutationObserver(syncMotion).observe(html, { attributes: true, attributeFilter: ['class'] });
    }
    document.fonts?.ready.then(scheduleMeasure).catch(() => {});
  }

  window[publicKey] = { init };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => init(document), { once: true });
  } else {
    init(document);
  }
})();
