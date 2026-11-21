/*
 * ELLIS Gold Coast V2 motion layer.
 * Colour and transforms belong to CSS; this file supplies progress variables.
 * Native scrolling, links, form controls and app.js remain in charge of input.
 */
(() => {
  'use strict';

  function initialiseMotion() {
    if (!document.body.classList.contains('maximal')) return;

    const html = document.documentElement;
    const clamp = (value, minimum = 0, maximum = 1) => Math.min(maximum, Math.max(minimum, value));
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
    const desktop = window.matchMedia('(min-width: 1024px)');
    const progressBars = [...document.querySelectorAll('.scroll-progress')];
    const heroes = [...document.querySelectorAll('.hero-scroll')].map(section => ({
      section,
      inner: section.querySelector('.hero') || section,
      stickyTop: 0
    }));
    const pinnedGalleries = [...document.querySelectorAll('[data-pin-gallery]')].map(section => ({
      section,
      inner: section.querySelector('.pin-inner') || section,
      track: section.querySelector('[data-track]'),
      stickyTop: 0
    })).filter(gallery => gallery.track);
    const tracks = [...document.querySelectorAll('[data-track]')].map(track => ({
      element: track,
      cards: [...track.children]
    }));
    const parallaxItems = [...document.querySelectorAll('[data-parallax]')];
    const tides = [...document.querySelectorAll('[data-tide]')];
    const tiltableItems = [...document.querySelectorAll('[data-tilt]')];
    const magneticItems = [...document.querySelectorAll('[data-magnetic]')];
    const cursor = document.querySelector('.cursor-orb');

    let paused = true;
    let frameId = 0;
    let dirty = true;
    let pageDirty = true;
    let layoutDirty = true;
    let viewportWidth = window.innerWidth;
    let viewportHeight = window.innerHeight;
    let pageHeight = html.scrollHeight;
    let lastPageY = window.scrollY;
    let pointerSeen = false;
    let pointerX = 0;
    let pointerY = 0;
    let cursorX = 0;
    let cursorY = 0;
    let hoveredControl = false;
    let activeTilt = null;
    let activeMagnet = null;

    function setVariable(element, name, value) {
      if (element.style.getPropertyValue(name) !== value) element.style.setProperty(name, value);
    }

    function resetTilt(element) {
      if (!element) return;
      setVariable(element, '--tilt-x', '0deg');
      setVariable(element, '--tilt-y', '0deg');
    }

    function resetMagnet(element) {
      if (!element) return;
      setVariable(element, '--magnet-x', '0px');
      setVariable(element, '--magnet-y', '0px');
    }

    function stopPointerEffects() {
      resetTilt(activeTilt);
      resetMagnet(activeMagnet);
      activeTilt = null;
      activeMagnet = null;
      hoveredControl = false;
      pointerSeen = false;
      if (cursor) {
        cursor.classList.remove('is-active');
        cursor.style.visibility = 'hidden';
        cursor.style.transform = 'translate3d(-100px, -100px, 0) translate(-50%, -50%)';
      }
    }

    function resetMotionVariables() {
      progressBars.forEach(element => setVariable(element, '--page-progress', '0'));
      heroes.forEach(({ section }) => setVariable(section, '--hero-progress', '0'));
      parallaxItems.forEach(element => setVariable(element, '--parallax', '0'));
      tides.forEach(element => setVariable(element, '--tide-progress', '0'));
      tracks.forEach(({ cards }) => cards.forEach(card => setVariable(card, '--card-focus', '1')));
      tiltableItems.forEach(resetTilt);
      magneticItems.forEach(resetMagnet);
      document.querySelectorAll('[data-reveal]').forEach(element => element.classList.add('is-visible'));
      stopPointerEffects();
    }

    function scheduleFrame({ page = false, layout = false } = {}) {
      dirty = true;
      pageDirty ||= page;
      layoutDirty ||= layout;
      if (paused || document.hidden || frameId) return;
      frameId = window.requestAnimationFrame(renderFrame);
    }

    function applyPreference() {
      paused = reducedMotion.matches;
      html.classList.toggle('motion-paused', paused);
      if (paused) {
        if (frameId) window.cancelAnimationFrame(frameId);
        frameId = 0;
        resetMotionVariables();
      } else {
        scheduleFrame({ page: true, layout: true });
      }
    }

    function measureLayout() {
      viewportWidth = window.innerWidth;
      viewportHeight = Math.max(1, window.innerHeight);
      pageHeight = Math.max(html.scrollHeight, document.body.scrollHeight);
      [...heroes, ...pinnedGalleries].forEach(scene => {
        scene.stickyTop = Number.parseFloat(window.getComputedStyle(scene.inner).top) || 0;
      });
      if (!desktop.matches || !finePointer.matches) stopPointerEffects();
    }

    function pinProgress(scene) {
      const bounds = scene.section.getBoundingClientRect();
      const innerHeight = scene.inner.getBoundingClientRect().height;
      const travel = bounds.height - innerHeight;
      if (travel <= 1) return 0;
      return clamp((scene.stickyTop - bounds.top) / travel);
    }

    function updateScrollScenes(shouldMapGalleries) {
      const scrollY = window.scrollY;
      const progress = clamp(scrollY / Math.max(1, pageHeight - viewportHeight));
      progressBars.forEach(element => setVariable(element, '--page-progress', progress.toFixed(4)));

      heroes.forEach(scene => {
        setVariable(scene.section, '--hero-progress', pinProgress(scene).toFixed(4));
      });

      if (desktop.matches && shouldMapGalleries) {
        pinnedGalleries.forEach(gallery => {
          const bounds = gallery.section.getBoundingClientRect();
          // Outside the scene, avoid unnecessary writes to native scroll tracks.
          if (bounds.bottom < -viewportHeight || bounds.top > viewportHeight * 2) return;
          const maximum = Math.max(0, gallery.track.scrollWidth - gallery.track.clientWidth);
          const desiredLeft = pinProgress(gallery) * maximum;
          if (Math.abs(gallery.track.scrollLeft - desiredLeft) > 0.5) {
            // Do not call smooth scrolling here: the document supplies the motion.
            gallery.track.scrollLeft = desiredLeft;
          }
        });
      }

      parallaxItems.forEach(element => {
        const bounds = element.getBoundingClientRect();
        const middle = bounds.top + bounds.height / 2;
        const distance = (middle - viewportHeight / 2) / Math.max(1, (viewportHeight + bounds.height) / 2);
        setVariable(element, '--parallax', clamp(distance, -1, 1).toFixed(4));
      });

      tides.forEach(element => {
        const bounds = element.getBoundingClientRect();
        const progress = clamp((viewportHeight - bounds.top) / Math.max(1, viewportHeight + bounds.height));
        setVariable(element, '--tide-progress', progress.toFixed(4));
      });
    }

    function updateCardFocus() {
      tracks.forEach(({ element, cards }) => {
        const bounds = element.getBoundingClientRect();
        const left = Math.max(0, bounds.left);
        const right = Math.min(viewportWidth, bounds.right);
        const visibleWidth = Math.max(0, right - left);
        const centre = (left + right) / 2;
        if (visibleWidth === 0 || bounds.bottom < 0 || bounds.top > viewportHeight) return;
        cards.forEach(card => {
          const box = card.getBoundingClientRect();
          const overlap = Math.max(0, Math.min(box.right, right) - Math.max(box.left, left));
          const visible = clamp(overlap / Math.max(1, box.width));
          const nearCentre = 1 - clamp(Math.abs(box.left + box.width / 2 - centre) / Math.max(1, visibleWidth * 0.65));
          const focus = Math.min(visible, 0.4 + nearCentre * 0.6);
          setVariable(card, '--card-focus', focus.toFixed(4));
        });
      });
    }

    function updatePointerEffects() {
      if (!desktop.matches || !finePointer.matches || !pointerSeen) return false;
      if (activeTilt) {
        const bounds = activeTilt.getBoundingClientRect();
        const x = clamp(((pointerX - bounds.left) / Math.max(1, bounds.width)) * 2 - 1, -1, 1);
        const y = clamp(((pointerY - bounds.top) / Math.max(1, bounds.height)) * 2 - 1, -1, 1);
        setVariable(activeTilt, '--tilt-x', `${(-y * 6).toFixed(2)}deg`);
        setVariable(activeTilt, '--tilt-y', `${(x * 6).toFixed(2)}deg`);
      }
      if (activeMagnet) {
        const bounds = activeMagnet.getBoundingClientRect();
        const x = clamp(((pointerX - bounds.left) / Math.max(1, bounds.width)) * 2 - 1, -1, 1);
        const y = clamp(((pointerY - bounds.top) / Math.max(1, bounds.height)) * 2 - 1, -1, 1);
        setVariable(activeMagnet, '--magnet-x', `${(x * 5).toFixed(2)}px`);
        setVariable(activeMagnet, '--magnet-y', `${(y * 5).toFixed(2)}px`);
      }
      if (!cursor) return false;
      cursorX += (pointerX - cursorX) * 0.22;
      cursorY += (pointerY - cursorY) * 0.22;
      const moving = Math.abs(pointerX - cursorX) + Math.abs(pointerY - cursorY) > 0.35;
      if (!moving) {
        cursorX = pointerX;
        cursorY = pointerY;
      }
      cursor.style.visibility = 'visible';
      cursor.classList.toggle('is-active', hoveredControl);
      cursor.style.transform = `translate3d(${cursorX.toFixed(2)}px, ${cursorY.toFixed(2)}px, 0) translate(-50%, -50%)`;
      return moving;
    }

    function renderFrame() {
      frameId = 0;
      if (paused || document.hidden || !dirty) return;
      dirty = false;
      const remeasure = layoutDirty;
      const mapGalleries = pageDirty || remeasure || Math.abs(window.scrollY - lastPageY) > 0.1;
      pageDirty = false;
      layoutDirty = false;
      if (remeasure) measureLayout();
      updateScrollScenes(mapGalleries);
      updateCardFocus();
      lastPageY = window.scrollY;
      if (updatePointerEffects()) dirty = true;
      if (dirty) scheduleFrame();
    }

    // One capture listener observes document AND native horizontal scrolling.
    // A horizontal button/swipe never immediately gets mapped back to page Y.
    document.addEventListener('scroll', event => {
      const target = event.target;
      const isPageScroll = target === document || target === html || target === document.body;
      scheduleFrame({ page: isPageScroll });
    }, { passive: true, capture: true });

    window.addEventListener('resize', () => {
      scheduleFrame({ page: true, layout: true });
    }, { passive: true });

    document.addEventListener('pointermove', event => {
      if (paused || document.hidden || !desktop.matches || !finePointer.matches || event.pointerType === 'touch') return;
      const target = event.target instanceof Element ? event.target : null;
      const nextTilt = target?.closest('[data-tilt]') || null;
      const nextMagnet = target?.closest('[data-magnetic]') || null;
      if (activeTilt !== nextTilt) resetTilt(activeTilt);
      if (activeMagnet !== nextMagnet) resetMagnet(activeMagnet);
      activeTilt = nextTilt;
      activeMagnet = nextMagnet;
      hoveredControl = Boolean(target?.closest('[data-tilt], a, button'));
      pointerX = event.clientX;
      pointerY = event.clientY;
      if (!pointerSeen) {
        cursorX = pointerX;
        cursorY = pointerY;
      }
      pointerSeen = true;
      scheduleFrame();
    }, { passive: true });

    document.addEventListener('pointerout', event => {
      const destination = event.relatedTarget;
      if (!(destination instanceof Node)) {
        stopPointerEffects();
        return;
      }
      if (activeTilt && !activeTilt.contains(destination)) {
        resetTilt(activeTilt);
        activeTilt = null;
      }
      if (activeMagnet && !activeMagnet.contains(destination)) {
        resetMagnet(activeMagnet);
        activeMagnet = null;
      }
    }, { passive: true });

    document.addEventListener('visibilitychange', () => {
      html.classList.toggle('motion-hidden', document.hidden);
      if (document.hidden) {
        if (frameId) window.cancelAnimationFrame(frameId);
        frameId = 0;
        stopPointerEffects();
      } else {
        scheduleFrame({ page: true, layout: true });
      }
    });

    reducedMotion.addEventListener?.('change', applyPreference);
    finePointer.addEventListener?.('change', () => scheduleFrame({ layout: true }));
    document.fonts?.ready.then(() => scheduleFrame({ page: true, layout: true }));
    window.addEventListener('load', () => scheduleFrame({ page: true, layout: true }), { once: true });
    if (cursor) {
      cursor.setAttribute('aria-hidden', 'true');
      cursor.style.pointerEvents = 'none';
      cursor.style.visibility = 'hidden';
    }
    html.classList.toggle('motion-hidden', document.hidden);
    applyPreference();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialiseMotion, { once: true });
  } else {
    initialiseMotion();
  }
})();
