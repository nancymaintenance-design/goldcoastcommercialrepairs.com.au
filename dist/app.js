/* ELLIS Gold Coast: progressive, browser-local interactions. */
(() => {
  'use strict';

  function init() {
    const root = document.documentElement;
    const zh = /^zh(?:-|$)/i.test(root.lang);
    const t = (en, cn) => (zh ? cn : en);
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const scrollBehaviour = () => ((motion.matches || root.classList.contains('motion-paused')) ? 'auto' : 'smooth');
    root.classList.add('js');

    // The mobile navigation stays a normal, keyboard-accessible navigation.
    const menuToggle = document.querySelector('.menu-toggle');
    const navigation = document.getElementById('primary-nav');
    if (menuToggle && navigation) {
      const setMenuOpen = (open, returnFocus = false) => {
        menuToggle.setAttribute('aria-expanded', String(open));
        menuToggle.setAttribute('aria-label', open
          ? t('Close navigation menu', '关闭导航菜单')
          : t('Open navigation menu', '打开导航菜单'));
        navigation.classList.toggle('is-open', open);
        menuToggle.classList.toggle('is-open', open);
        if (returnFocus) menuToggle.focus();
      };
      setMenuOpen(false);
      menuToggle.addEventListener('click', () => {
        setMenuOpen(menuToggle.getAttribute('aria-expanded') !== 'true');
      });
      navigation.addEventListener('click', event => {
        if (event.target.closest('a')) setMenuOpen(false);
      });
      document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
          setMenuOpen(false, true);
        }
      });
      window.addEventListener('resize', () => {
        if (window.getComputedStyle(menuToggle).display === 'none') setMenuOpen(false);
      }, { passive: true });
    }

    // Content remains visible without JavaScript or with reduced motion.
    const revealItems = [...document.querySelectorAll('[data-reveal]')];
    let revealObserver;
    const revealAll = () => {
      revealObserver?.disconnect();
      revealItems.forEach(item => item.classList.add('is-visible'));
    };
    if (motion.matches || !('IntersectionObserver' in window)) {
      revealAll();
    } else {
      revealObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        });
      }, { threshold: 0.08, rootMargin: '0px 0px -24px 0px' });
      revealItems.forEach(item => revealObserver.observe(item));
    }
    motion.addEventListener?.('change', event => {
      if (event.matches) revealAll();
    });

    // Native horizontal scrolling supports swipe, keyboard and named buttons.
    document.querySelectorAll('[data-carousel]').forEach(carousel => {
      const track = carousel.querySelector('[data-track]');
      const previous = carousel.querySelector('[data-prev]');
      const next = carousel.querySelector('[data-next]');
      if (!track) return;

      const setDisabled = (button, disabled) => {
        if (!button) return;
        button.disabled = disabled;
        button.setAttribute('aria-disabled', String(disabled));
      };
      const updateControls = () => {
        const maximum = Math.max(0, track.scrollWidth - track.clientWidth);
        setDisabled(previous, maximum <= 2 || track.scrollLeft <= 2);
        setDisabled(next, maximum <= 2 || track.scrollLeft >= maximum - 2);
      };
      const stepSize = () => {
        const first = [...track.children].find(child => !child.hidden);
        if (!first) return track.clientWidth;
        const style = window.getComputedStyle(track);
        const gap = Number.parseFloat(style.columnGap || style.gap) || 0;
        return first.getBoundingClientRect().width + gap;
      };
      const move = direction => {
        track.scrollBy({ left: direction * stepSize(), behavior: scrollBehaviour() });
      };
      previous?.addEventListener('click', () => move(-1));
      next?.addEventListener('click', () => move(1));
      let scheduled = false;
      track.addEventListener('scroll', () => {
        if (scheduled) return;
        scheduled = true;
        requestAnimationFrame(() => {
          updateControls();
          scheduled = false;
        });
      }, { passive: true });
      if ('ResizeObserver' in window) {
        const resizeObserver = new ResizeObserver(updateControls);
        resizeObserver.observe(track);
      } else {
        window.addEventListener('resize', updateControls, { passive: true });
      }
      track.querySelectorAll('img').forEach(img => {
        if (!img.complete) img.addEventListener('load', updateControls, { once: true });
      });
      if ('IntersectionObserver' in window) {
        const cardObserver = new IntersectionObserver(entries => {
          entries.forEach(entry => {
            entry.target.classList.toggle('is-in-view', entry.intersectionRatio >= 0.5);
          });
        }, { root: track, threshold: [0, 0.5, 1] });
        [...track.children].forEach(card => cardObserver.observe(card));
      } else {
        [...track.children].forEach(card => card.classList.add('is-in-view'));
      }
      updateControls();
    });

    // Category filters and FAQ search share one visibility decision per item.
    const search = document.getElementById('faq-search');
    const normalise = value => String(value || '').normalize('NFKC').toLocaleLowerCase().trim();
    const matchesSearch = item => {
      if (!search || !(item.matches('[data-faq]') || item.querySelector('[data-faq]'))) return true;
      const terms = normalise(search.value).split(/\s+/).filter(Boolean);
      const content = normalise(item.textContent);
      return terms.every(term => content.includes(term));
    };
    const groups = [];
    document.querySelectorAll('[data-filter-group]').forEach(group => {
      const buttons = [...group.querySelectorAll('[data-filter]')]
        .filter(button => button.closest('[data-filter-group]') === group);
      const items = [...group.querySelectorAll('[data-filter-item]')]
        .filter(item => item.closest('[data-filter-group]') === group);
      const initiallyActive = buttons.find(button => button.getAttribute('aria-pressed') === 'true');
      let active = initiallyActive?.dataset.filter || 'all';
      const applyFilter = () => {
        let visible = 0;
        items.forEach(item => {
          const tags = (item.dataset.tags || '').split(/\s+/).filter(Boolean);
          const show = (active === 'all' || tags.includes(active)) && matchesSearch(item);
          item.hidden = !show;
          if (show) visible += 1;
        });
        buttons.forEach(button => {
          const selected = button.dataset.filter === active;
          button.setAttribute('aria-pressed', String(selected));
          button.classList.toggle('is-active', selected);
        });
        const count = group.querySelector('[data-result-count]');
        if (count) {
          const faqGroup = items.some(item => item.matches('[data-faq]') || item.querySelector('[data-faq]'));
          const label = faqGroup
            ? t(`${visible} ${visible === 1 ? 'question' : 'questions'}`, `${visible} 个问题`)
            : t(`${visible} ${visible === 1 ? 'result' : 'results'}`, `${visible} 项结果`);
          count.textContent = label;
          count.setAttribute('aria-label', label);
        }
        const empty = group.querySelector('[data-no-results]');
        if (empty) empty.hidden = visible > 0;
      };
      buttons.forEach(button => {
        button.addEventListener('click', () => {
          active = button.dataset.filter || 'all';
          applyFilter();
        });
      });
      groups.push(applyFilter);
      applyFilter();
    });
    if (search) {
      const applySearch = () => {
        groups.forEach(applyFilter => applyFilter());
        document.querySelectorAll('[data-faq]').forEach(item => {
          if (!item.closest('[data-filter-group]')) item.hidden = !matchesSearch(item);
        });
      };
      search.addEventListener('input', applySearch);
      search.addEventListener('search', applySearch);
      applySearch();
    }

    // Enquiries are prepared locally. No network request or persistent storage.
    const form = document.getElementById('enquiry-form');
    if (!form) return;
    const result = document.getElementById('enquiry-result');
    const summary = document.getElementById('enquiry-summary');
    let draft = '';

    const field = name => form.elements.namedItem(name);
    const value = name => String(field(name)?.value || '').trim();
    const selectedText = name => {
      const element = field(name);
      return element instanceof HTMLSelectElement
        ? element.selectedOptions[0]?.textContent?.trim() || element.value
        : value(name);
    };
    const setNotice = (message, showInForm = false) => {
      if (showInForm || !result) {
        let feedback = form.querySelector('[data-enquiry-feedback]');
        if (!feedback) {
          feedback = document.createElement('p');
          feedback.dataset.enquiryFeedback = '';
          feedback.className = 'form-note';
          feedback.setAttribute('role', 'status');
          feedback.setAttribute('aria-live', 'polite');
          form.prepend(feedback);
        }
        feedback.textContent = message;
      }
      if (result) {
        let status = result.querySelector('[data-enquiry-status]');
        if (!status) {
          status = document.createElement('p');
          status.dataset.enquiryStatus = '';
          status.className = 'enquiry-status';
          status.setAttribute('role', 'status');
          status.setAttribute('aria-live', 'polite');
          result.prepend(status);
        }
        status.textContent = message;
        status.hidden = !message;
      }
    };
    const requested = new URLSearchParams(window.location.search);
    for (const name of ['service', 'property', 'article']) {
      const select = field(name);
      const requestedValue = requested.get(name);
      if (select instanceof HTMLSelectElement && requestedValue
        && [...select.options].some(option => option.value === requestedValue)) {
        select.value = requestedValue;
        if (name === 'article') select.closest('[data-enquiry-article]').hidden = false;
      }
    }

    form.addEventListener('submit', event => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      if (!result || !summary) {
        setNotice(t(
          'Refresh the page and try opening the work summary again.',
          '请刷新页面后重新查看需求清单。'
        ), true);
        return;
      }
      draft = [
        t('ELLIS — Gold Coast commercial maintenance', 'ELLIS — 黄金海岸商业维护'),
        '',
        `${t('Name', '姓名')}: ${value('name')}`,
        `${t('Email', '邮箱')}: ${value('email')}`,
        `${t('Suburb', '地区')}: ${value('suburb')}`,
        `${t('Property type', '物业类型')}: ${selectedText('property')}`,
        ...(value('service') ? [`${t('Service', '服务项目')}: ${selectedText('service')}`] : []),
        ...(value('article') ? [`${t('Related guide', '相关指南')}: ${selectedText('article')}`] : []),
        ...(value('access-window') ? [`${t('Preferred access window', '期望的进场时段')}: ${value('access-window')}`] : []),
        '',
        `${t('Work required', '需要处理的事项')}:`,
        value('message')
      ].join('\n');
      if (summary instanceof HTMLInputElement || summary instanceof HTMLTextAreaElement) {
        summary.value = draft;
      } else {
        summary.textContent = draft;
      }
      setNotice('');
      result.hidden = false;
      result.setAttribute('tabindex', '-1');
      if (!form.contains(result)) form.hidden = true;
      result.focus({ preventScroll: true });
      result.scrollIntoView({ behavior: scrollBehaviour(), block: 'start' });
    });

    document.getElementById('download-enquiry')?.addEventListener('click', event => {
      event.preventDefault();
      if (!draft) return;
      const blob = new Blob([draft], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'gold-coast-work-summary.txt';
      document.body.append(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setNotice(t('Work summary downloaded.', '清单已下载。'));
    });

    document.getElementById('copy-enquiry')?.addEventListener('click', async event => {
      event.preventDefault();
      if (!draft) return;
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(draft);
        setNotice(t('Work summary copied.', '清单已复制。'));
      } catch {
        if (summary instanceof HTMLInputElement || summary instanceof HTMLTextAreaElement) {
          summary.focus();
          summary.select();
        } else if (summary) {
          summary.setAttribute('tabindex', '-1');
          summary.focus();
          const selection = window.getSelection();
          const range = document.createRange();
          range.selectNodeContents(summary);
          selection?.removeAllRanges();
          selection?.addRange(range);
        }
        setNotice(t(
          'Copy the selected work summary.',
          '请复制已选中的清单内容。'
        ));
      }
    });

    document.getElementById('edit-enquiry')?.addEventListener('click', event => {
      event.preventDefault();
      if (result) result.hidden = true;
      form.hidden = false;
      const firstField = form.querySelector('input:not([type="hidden"]), select, textarea');
      firstField?.focus({ preventScroll: true });
      form.scrollIntoView({ behavior: scrollBehaviour(), block: 'start' });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
