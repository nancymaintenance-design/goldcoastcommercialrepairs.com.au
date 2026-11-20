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
    const notice = document.getElementById('enquiry-notice');
    const result = document.getElementById('enquiry-result');
    const summary = document.getElementById('enquiry-summary');
    const photos = form.querySelector('input[name="photos"]');
    const photoList = document.getElementById('photo-list');
    let draft = '';

    const draftStatus = t(
      'Draft prepared in this browser. No enquiry has been sent.',
      '需求草稿已在本浏览器生成，尚未发送。'
    );
    const field = name => form.elements.namedItem(name);
    const value = name => String(field(name)?.value || '').trim();
    const selectedText = name => {
      const element = field(name);
      return element instanceof HTMLSelectElement
        ? element.selectedOptions[0]?.textContent?.trim() || element.value
        : value(name);
    };
    const setNotice = (message, showInForm = false) => {
      // Keep the original preview explanation intact when returning to edit.
      if (showInForm || !result) {
        let feedback = form.querySelector('[data-enquiry-feedback]');
        if (!feedback) {
          feedback = document.createElement('p');
          feedback.dataset.enquiryFeedback = '';
          feedback.className = 'form-note';
          feedback.setAttribute('role', 'status');
          feedback.setAttribute('aria-live', 'polite');
          if (notice) notice.after(feedback);
          else form.prepend(feedback);
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
      }
    };
    const validatePhotos = (report = false) => {
      if (!photos) return true;
      const files = [...(photos.files || [])];
      let message = '';
      if (files.length > 5) {
        message = t('Choose up to 5 photos.', '最多选择5张照片。');
      } else if (files.some(file => file.size > 10 * 1024 * 1024)) {
        message = t('Each photo must be 10 MB or smaller.', '每张照片不能超过10 MB。');
      } else if (files.some(file => {
        const typeValid = ['image/jpeg', 'image/png', 'image/webp'].includes(file.type);
        const extensionValid = /\.(?:jpe?g|png|webp)$/i.test(file.name);
        return file.type ? !typeValid : !extensionValid;
      })) {
        message = t('Choose JPEG, PNG or WebP photos.', '请选择JPEG、PNG或WebP格式的照片。');
      }
      photos.setCustomValidity(message);
      if (photoList) {
        photoList.replaceChildren();
        files.forEach(file => {
          const entry = document.createElement(/^(UL|OL)$/.test(photoList.tagName) ? 'li' : 'p');
          entry.textContent = `${file.name} · ${(file.size / (1024 * 1024)).toFixed(1)} MB`;
          photoList.append(entry);
        });
        if (message) {
          const error = document.createElement(/^(UL|OL)$/.test(photoList.tagName) ? 'li' : 'p');
          error.className = 'field-error';
          error.textContent = message;
          photoList.append(error);
        }
      }
      if (message && report) photos.reportValidity();
      return !message;
    };
    photos?.addEventListener('change', () => validatePhotos(true));

    const requestedService = new URLSearchParams(window.location.search).get('service');
    const serviceField = field('service');
    if (requestedService && serviceField instanceof HTMLSelectElement
      && [...serviceField.options].some(option => option.value === requestedService)) {
      serviceField.value = requestedService;
    }

    form.addEventListener('submit', event => {
      event.preventDefault();
      if (!validatePhotos(true) || !form.reportValidity()) return;
      if (!result || !summary) {
        setNotice(t(
          'The draft preview is unavailable. Your enquiry has not been sent.',
          '目前无法显示草稿，您的需求尚未发送。'
        ), true);
        return;
      }
      const files = [...(photos?.files || [])];
      draft = [
        t('ELLIS — Gold Coast commercial maintenance', 'ELLIS — 黄金海岸商业维护'),
        draftStatus,
        '',
        `${t('Name', '姓名')}: ${value('name')}`,
        `${t('Email', '邮箱')}: ${value('email')}`,
        `${t('Suburb', '地区')}: ${value('suburb')}`,
        `${t('Property type', '物业类型')}: ${selectedText('property')}`,
        `${t('Service', '服务项目')}: ${selectedText('service')}`,
        '',
        `${t('Work required', '需要处理的事项')}:`,
        value('message'),
        '',
        `${t('Selected photo filenames', '选定照片的文件名')}:`,
        files.length ? files.map(file => `• ${file.name}`).join('\n') : t('None selected', '未选择照片'),
        '',
        t(
          'Photo filenames are included for reference only. Photo files are not attached or sent.',
          '这里只记录照片文件名；照片文件尚未附加或发送。'
        )
      ].join('\n');
      if (summary instanceof HTMLInputElement || summary instanceof HTMLTextAreaElement) {
        summary.value = draft;
      } else {
        summary.textContent = draft;
      }
      setNotice(draftStatus);
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
      link.download = 'gold-coast-enquiry-draft.txt';
      document.body.append(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setNotice(t('Draft downloaded. No enquiry has been sent.', '草稿已下载，需求尚未发送。'));
    });

    document.getElementById('copy-enquiry')?.addEventListener('click', async event => {
      event.preventDefault();
      if (!draft) return;
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(draft);
        setNotice(t('Draft copied. No enquiry has been sent.', '草稿已复制，需求尚未发送。'));
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
          'Automatic copying is unavailable. Copy the selected draft text below. No enquiry has been sent.',
          '无法自动复制，请复制下方已选中的草稿文字。需求尚未发送。'
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
