/**
 * Experiences showcase – icon tabs + autoswipe detail cards (all activities)
 */
(function () {
  'use strict';

  const AUTOPLAY_MS = 5500;
  const TAB_ICONS_PER_PAGE = 10;

  let experiences = [];
  let activeIndex = 0;
  let autoplayTimer = null;
  let tabPage = 0;
  let rootEl = null;
  let isAnimating = false;

  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function imgPath(path) {
    return path.replace(/ /g, '%20');
  }

  async function fetchExperiences() {
    const url = new URL('data/experiences.json', document.baseURI).href;
    const res = await fetch(url, { cache: 'no-cache' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    return data.experiences || [];
  }

  function buildMedia(exp) {
    return `
      <div class="exp-showcase__media">
        <img src="${imgPath(exp.image)}" alt="${esc(exp.alt || exp.title)}" class="exp-showcase__img" loading="lazy" decoding="async" width="720" height="540">
        <div class="exp-showcase__media-gold" aria-hidden="true"></div>
        <div class="exp-showcase__media-scrim" aria-hidden="true"></div>
      </div>`;
  }

  function buildCardContent(exp) {
    const highlights = (exp.highlights || [])
      .map((h) => `<li><i class="fa-solid fa-star" aria-hidden="true"></i>${esc(h)}</li>`)
      .join('');
    return `
      <div class="exp-showcase__content">
        <h4 class="exp-showcase__title">${esc(exp.title)}</h4>
        <p class="exp-showcase__desc">${esc(exp.desc)}</p>
        <ul class="exp-showcase__highlights">${highlights}</ul>
      </div>
      ${buildMedia(exp)}`;
  }

  function buildTab(exp, index) {
    const selected = index === activeIndex;
    return `
      <button type="button" class="exp-showcase__tab${selected ? ' exp-showcase__tab--active' : ''}"
              role="tab" data-index="${index}" aria-selected="${selected}">
        <span class="exp-showcase__tab-icon"><i class="fa-solid ${exp.icon}" aria-hidden="true"></i></span>
        <span class="exp-showcase__tab-label">${esc(exp.tab || exp.title)}</span>
      </button>`;
  }

  function renderTabs(root, skipTabScroll) {
    const tabsEl = root.querySelector('#expShowcaseTabs');
    const tabDotsEl = root.querySelector('#expShowcaseTabDots');
    if (!tabsEl) return;

    const totalTabPages = Math.max(1, Math.ceil(experiences.length / TAB_ICONS_PER_PAGE));
    tabPage = Math.min(tabPage, totalTabPages - 1);
    const tabStart = tabPage * TAB_ICONS_PER_PAGE;
    const tabSlice = experiences.slice(tabStart, tabStart + TAB_ICONS_PER_PAGE);

    tabsEl.innerHTML = tabSlice.map((exp, i) => buildTab(exp, tabStart + i)).join('');

    if (tabDotsEl) {
      tabDotsEl.innerHTML = '';
      if (totalTabPages > 1) {
        for (let p = 0; p < totalTabPages; p += 1) {
          const dot = document.createElement('button');
          dot.type = 'button';
          dot.className = 'exp-showcase__tab-dot' + (p === tabPage ? ' exp-showcase__tab-dot--active' : '');
          dot.setAttribute('aria-label', 'Activity icons page ' + (p + 1));
          dot.addEventListener('click', () => {
            tabPage = p;
            renderTabs(root);
            bindTabClicks(root);
          });
          tabDotsEl.appendChild(dot);
        }
      }
    }

    bindTabClicks(root);
    if (!skipTabScroll) scrollActiveTabIntoView(root);
  }

  function renderCard(root, exp, animate) {
    const cardEl = root.querySelector('#expShowcaseCard');
    if (!cardEl || !exp) return;

    if (!animate) {
      cardEl.innerHTML = buildCardContent(exp);
      cardEl.classList.remove('exp-showcase__card--leaving', 'exp-showcase__card--entering');
      isAnimating = false;
      return;
    }

    cardEl.classList.add('exp-showcase__card--leaving');
    window.setTimeout(() => {
      cardEl.innerHTML = buildCardContent(exp);
      cardEl.classList.remove('exp-showcase__card--leaving');
      cardEl.classList.add('exp-showcase__card--entering');
      window.setTimeout(() => {
        cardEl.classList.remove('exp-showcase__card--entering');
        isAnimating = false;
      }, 420);
    }, 300);
  }

  function bindTabClicks(root) {
    root.querySelectorAll('.exp-showcase__tab').forEach((btn) => {
      btn.addEventListener('click', () => {
        goTo(parseInt(btn.dataset.index, 10), root, true);
      });
    });
  }

  function scrollActiveTabIntoView(root) {
    const active = root.querySelector('.exp-showcase__tab--active');
    const scrollParent = root.querySelector('.exp-showcase__tabs-scroll');
    if (!active || !scrollParent) return;
    const parentRect = scrollParent.getBoundingClientRect();
    const tabRect = active.getBoundingClientRect();
    const tabCenter = tabRect.left - parentRect.left + scrollParent.scrollLeft + tabRect.width / 2;
    scrollParent.scrollTo({
      left: Math.max(0, tabCenter - scrollParent.clientWidth / 2),
      behavior: 'smooth',
    });
  }

  function updateProgress(root) {
    const bar = root.querySelector('.exp-showcase__progress-bar');
    if (!bar) return;
    bar.style.animation = 'none';
    void bar.offsetWidth;
    bar.style.animation = '';
  }

  function goTo(index, root, userTriggered) {
    if (!experiences.length || isAnimating) return;

    const nextIndex = (index + experiences.length) % experiences.length;
    if (nextIndex === activeIndex && !userTriggered) return;

    isAnimating = true;
    activeIndex = nextIndex;

    const tabPageNeeded = Math.floor(activeIndex / TAB_ICONS_PER_PAGE);
    if (tabPageNeeded !== tabPage) {
      tabPage = tabPageNeeded;
      renderTabs(root);
    } else {
      root.querySelectorAll('.exp-showcase__tab').forEach((tab) => {
        const i = parseInt(tab.dataset.index, 10);
        const on = i === activeIndex;
        tab.classList.toggle('exp-showcase__tab--active', on);
        tab.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      scrollActiveTabIntoView(root);
    }

    renderCard(root, experiences[activeIndex], true);
    updateProgress(root);

    if (userTriggered) resetAutoplay(root);
  }

  function next(root) {
    goTo(activeIndex + 1, root, false);
  }

  function prev(root) {
    goTo(activeIndex - 1, root, true);
  }

  function startAutoplay() {
    stopAutoplay();
    if (!rootEl || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    autoplayTimer = window.setInterval(() => {
      if (!isAnimating) next(rootEl);
    }, AUTOPLAY_MS);
  }

  function stopAutoplay() {
    if (autoplayTimer) {
      window.clearInterval(autoplayTimer);
      autoplayTimer = null;
    }
  }

  function resetAutoplay() {
    stopAutoplay();
    startAutoplay();
  }

  function initOffscreenPause(root) {
    if (!('IntersectionObserver' in window)) {
      startAutoplay();
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) startAutoplay();
          else stopAutoplay();
        });
      },
      { threshold: 0.12 }
    );
    observer.observe(root);
  }

  async function init() {
    rootEl = document.getElementById('expShowcase');
    if (!rootEl) return;

    try {
      experiences = await fetchExperiences();
    } catch (e) {
      console.warn('Experiences data unavailable', e);
      return;
    }

    if (!experiences.length) return;

    document.documentElement.style.setProperty('--exp-autoplay-ms', AUTOPLAY_MS + 'ms');

    const track = rootEl.querySelector('#expShowcaseTrack');
    if (track) {
      track.innerHTML = `
        <article class="exp-showcase__card" id="expShowcaseCard" aria-live="polite"></article>
        <div class="exp-showcase__progress" aria-hidden="true">
          <div class="exp-showcase__progress-bar"></div>
        </div>`;
    }

    renderTabs(rootEl, true);
    renderCard(rootEl, experiences[0], false);
    updateProgress(rootEl);

    rootEl.querySelector('.exp-showcase__arrow--prev')?.addEventListener('click', () => prev(rootEl));
    rootEl.querySelector('.exp-showcase__arrow--next')?.addEventListener('click', () => {
      goTo(activeIndex + 1, rootEl, true);
    });

    rootEl.addEventListener('mouseenter', stopAutoplay);
    rootEl.addEventListener('mouseleave', startAutoplay);

    let touchStartX = 0;
    rootEl.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    rootEl.addEventListener('touchend', (e) => {
      const diff = e.changedTouches[0].screenX - touchStartX;
      if (Math.abs(diff) < 48) return;
      if (diff < 0) goTo(activeIndex + 1, rootEl, true);
      else prev(rootEl);
    }, { passive: true });

    initOffscreenPause(rootEl);
    startAutoplay();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
