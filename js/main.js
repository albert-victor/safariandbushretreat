/**
 * Safari and Bush Retreats - Main JavaScript
 * Luxury Tanzanian Tourism Website
 */

(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const BOOKING_HASHES = new Set(['#bookingForm', '#contact']);
  const PACKAGE_CIRCUIT_ORDER = [
    'Northern Circuit',
    'Southern Circuit',
    'Eastern Circuit',
    'Western Circuit',
    'Oceanic Islands',
    'Mafia Island',
    'Southern Highlands & Culture'
  ];

  let applyPackageSelection = null;
  let packagesBySlug = {};

  if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
  }

  /* ============================================
     DOM Ready
     ============================================ */
  document.addEventListener('DOMContentLoaded', init);

  const REVEAL_STAGGER_SELECTORS = '.section__header, .intro-brief__inner, .experiences__header';
  const REVEAL_SELECTORS = [
    '.destination-card',
    '.exp-showcase',
    '.package-card',
    '.accommodation-card',
    '.packages__cta',
    '.gallery__filters',
    '.gallery__item',
    '.about__image-wrap',
    '.about__content',
    '.testimonials__rating',
    '.testimonials__slider-wrap',
    '.testimonials__countries',
    '.contact__form',
    '.contact__info',
    '.footer__cert-badge'
  ].join(',');

  function init() {
    if (!window.location.hash) {
      window.scrollTo(0, 0);
    }
    initTheme();
    initNavigation();
    initHeroSwiper();
    initHeroVisibility();
    initDestinationsSwiper();
    initDestinationCardReveal();
    initTestimonialsSwiper();
    initOffscreenSwipers();
    initSafarisPagination();
    initGalleryPagination();
    initHeroAnimations();
    initScrollProgress();
    initReveal();
    initGallery();
    initLightbox();
    initAboutGallery();
    initBookingForm();
    initContactLinks();
    initSmoothScroll();
    initHashScroll();
    initActiveNavLinks();
    initImageFallbacks();
    initImageDecoding();
    initWhatsappVisibility();
    initPaintOptimizations();
    initSiteSearch();
  }

  function getScrollY() {
    return window.scrollY;
  }

  function siteBasePath() {
    const script = document.querySelector('script[src*="js/main.js"]');
    if (script) {
      return (script.getAttribute('src') || '').replace(/js\/main\.js(?:\?.*)?$/, '');
    }
    const link = document.querySelector('link[href*="css/style.css"]');
    if (link) {
      return (link.getAttribute('href') || '').replace(/css\/style\.css(?:\?.*)?$/, '');
    }
    return '';
  }

  function getPackageSlugFromUrl() {
    return new URLSearchParams(window.location.search).get('package') || '';
  }

  function buildBookingHashUrl(packageSlug) {
    const q = packageSlug ? '?package=' + encodeURIComponent(packageSlug) : '';
    return q + '#bookingForm';
  }

  function safariPackagesUrl() {
    return siteBasePath() + 'data/safari-packages.json';
  }

  /* ============================================
     NAVIGATION
     ============================================ */
  function initNavigation() {
    const navbar = document.getElementById('navbar');
    const toggle = document.getElementById('navbarToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileClose = document.getElementById('mobileMenuClose');
    const overlay = document.getElementById('mobileMenuOverlay');
    const mobileLinks = document.querySelectorAll('.mobile-menu__link:not(.mobile-menu__dest-trigger)');

    if (!navbar) return;

    const isSolidNav = navbar.classList.contains('navbar--solid');

    function updateNavbarState() {
      if (isSolidNav) {
        navbar.classList.add('navbar--scrolled');
        return;
      }
      navbar.classList.toggle('navbar--scrolled', getScrollY() > 80);
    }

    updateNavbarState();
    window.addEventListener('scroll', updateNavbarState, { passive: true });

    function openMenu() {
      mobileMenu.classList.add('active');
      mobileMenu.setAttribute('aria-hidden', 'false');
      toggle.classList.add('active');
      toggle.setAttribute('aria-expanded', 'true');
      document.body.classList.add('menu-open');
    }

    function closeMenu() {
      mobileMenu.classList.remove('active');
      mobileMenu.setAttribute('aria-hidden', 'true');
      toggle.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('menu-open');
    }

    toggle?.addEventListener('click', () => {
      mobileMenu.classList.contains('active') ? closeMenu() : openMenu();
    });

    mobileClose?.addEventListener('click', closeMenu);
    overlay?.addEventListener('click', closeMenu);

    mobileLinks.forEach(link => {
      link.addEventListener('click', closeMenu);
    });

    document.querySelectorAll('.mobile-menu__dest-trigger').forEach(trigger => {
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const item = trigger.closest('.mobile-menu__item--dest');
        if (!item) return;
        const isOpen = item.classList.toggle('is-open');
        trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });
    });

    document.querySelectorAll('.mobile-menu__dest-grid a, .mobile-menu__dest-overview, .mobile-menu__nested-panel a').forEach(link => {
      link.addEventListener('click', closeMenu);
    });

    document.querySelectorAll('.mobile-menu__nested-trigger').forEach(trigger => {
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const item = trigger.closest('.mobile-menu__nested');
        if (!item) return;
        const isOpen = item.classList.toggle('is-open');
        trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });
    });

    document.querySelectorAll('.mobile-menu__cta').forEach(link => {
      link.addEventListener('click', closeMenu);
    });

    /* Desktop destinations dropdown - hover bridge + touch tap */
    document.querySelectorAll('.navbar__item--has-dropdown').forEach(item => {
      const trigger = item.querySelector('.navbar__link');
      let closeTimer;

      item.addEventListener('mouseenter', () => {
        clearTimeout(closeTimer);
        item.classList.add('is-open');
      });

      item.addEventListener('mouseleave', () => {
        closeTimer = setTimeout(() => item.classList.remove('is-open'), 120);
      });

      trigger?.addEventListener('click', (e) => {
        if (window.matchMedia('(hover: none)').matches) {
          e.preventDefault();
          item.classList.toggle('is-open');
        }
      });

      document.addEventListener('click', (e) => {
        if (!item.contains(e.target)) item.classList.remove('is-open');
      });
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
        closeMenu();
      }
    });
  }

  /* ============================================
     HERO SWIPER
     ============================================ */
  function initHeroSwiper() {
    if (typeof Swiper === 'undefined') return;

    const progressBar = document.getElementById('heroProgressBar');
    const SLIDE_DELAY = 8000;

    const heroSection = document.getElementById('home');

    window.heroSwiper = new Swiper('#heroSwiper', {
      effect: 'fade',
      fadeEffect: { crossFade: true },
      speed: 2000,
      autoplay: {
        delay: SLIDE_DELAY,
        disableOnInteraction: false,
        pauseOnMouseEnter: true
      },
      loop: true,
      allowTouchMove: true,
      watchSlidesProgress: true,
      pagination: {
        el: '.hero-pagination',
        clickable: true
      },
      on: {
        autoplayTimeLeft(_swiper, _time, progress) {
          if (progressBar) {
            progressBar.style.width = (progress * 100) + '%';
          }
        },
        init(swiper) {
          swiper.slides.forEach((slide, i) => {
            const img = slide.querySelector('.hero-slide__img');
            if (!img) return;
            if (i > 0) {
              img.loading = 'lazy';
              img.fetchPriority = 'low';
            }
          });
        },
        slideChangeTransitionStart() {
          heroSection?.classList.add('hero--transitioning');
        },
        slideChangeTransitionEnd() {
          heroSection?.classList.remove('hero--transitioning');
        }
      }
    });
  }

  function initHeroVisibility() {
    const hero = document.getElementById('home');
    if (!hero || !window.heroSwiper) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const inView = entry.isIntersecting;
        if (inView) {
          window.heroSwiper.autoplay?.start();
        } else {
          window.heroSwiper.autoplay?.stop();
        }
      },
      { threshold: 0.12 }
    );

    observer.observe(hero);
  }

  /* ============================================
     DESTINATIONS SWIPER - homepage iconic picks
     ============================================ */
  function initDestinationsSwiper() {
    if (typeof Swiper === 'undefined' || !document.getElementById('destinationsSwiper')) return;

    window.destinationsSwiper = new Swiper('#destinationsSwiper', {
      slidesPerView: 1.15,
      spaceBetween: 16,
      loop: true,
      speed: 700,
      grabCursor: true,
      autoplay: {
        delay: 4000,
        disableOnInteraction: false,
        pauseOnMouseEnter: true
      },
      pagination: {
        el: '.destinations-pagination',
        clickable: true,
        dynamicBullets: true
      },
      breakpoints: {
        640: {
          slidesPerView: 2.2,
          spaceBetween: 20
        },
        1024: {
          slidesPerView: 3.2,
          spaceBetween: 24
        },
        1280: {
          slidesPerView: 4,
          spaceBetween: 28
        }
      }
    });
  }

  function initDestinationCardReveal() {
    var cards = document.querySelectorAll('.destination-card');
    if (!cards.length) return;

    var touchQuery = window.matchMedia('(hover: none), (pointer: coarse)');

    function closeAll(except) {
      cards.forEach(function (card) {
        if (card !== except) card.classList.remove('destination-card--revealed');
      });
    }

    cards.forEach(function (card) {
      card.addEventListener('click', function (e) {
        if (!touchQuery.matches) return;

        if (card.classList.contains('destination-card--revealed')) return;

        e.preventDefault();
        closeAll(card);
        card.classList.add('destination-card--revealed');
      });
    });

    document.addEventListener('click', function (e) {
      if (!touchQuery.matches) return;
      if (e.target.closest('.destination-card')) return;
      closeAll();
    });
  }

  /* ============================================
     EXPERIENCES SWIPER
     ============================================ */
  /* Experiences showcase handled by js/experiences-showcase.js */

  /* ============================================
     TESTIMONIALS SWIPER - auto-sliding reviews
     ============================================ */
  function initTestimonialsSwiper() {
    if (typeof Swiper === 'undefined') return;

    window.testimonialsSwiper = new Swiper('#testimonialsSwiper', {
      slidesPerView: 'auto',
      spaceBetween: 20,
      centeredSlides: true,
      loop: true,
      speed: 900,
      autoplay: {
        delay: 3500,
        disableOnInteraction: false,
        pauseOnMouseEnter: true
      },
      grabCursor: true,
      breakpoints: {
        768: {
          centeredSlides: false,
          spaceBetween: 24
        },
        1024: {
          spaceBetween: 28
        }
      }
    });
  }

  function initOffscreenSwipers() {
    const pairs = [
      [document.getElementById('destinations'), window.destinationsSwiper],
      [document.getElementById('testimonials'), window.testimonialsSwiper]
    ];

    pairs.forEach(([el, swiper]) => {
      if (!el || !swiper) return;

      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            swiper.autoplay?.start();
          } else {
            swiper.autoplay?.stop();
          }
        },
        { threshold: 0.08 }
      );

      observer.observe(el);
    });
  }

  /* ============================================
     HERO ANIMATIONS
     ============================================ */
  function initHeroAnimations() {
    const elements = document.querySelectorAll('.hero-animate');
    if (!elements.length) return;

    if (prefersReducedMotion) {
      elements.forEach(el => el.classList.add('visible'));
      animateCounters();
      return;
    }

    elements.forEach((el, i) => {
      const delay = parseInt(el.dataset.delay || i, 10) * 150;
      setTimeout(() => {
        el.classList.add('visible');
        if (i === elements.length - 1) {
          setTimeout(animateCounters, 200);
        }
      }, 300 + delay);
    });
  }

  function easeOutExpo(t) {
    return t >= 1 ? 1 : 1 - Math.pow(2, -10 * t);
  }

  function animateCounters() {
    const counters = document.querySelectorAll('.hero__stat-number[data-count]');
    if (prefersReducedMotion) {
      counters.forEach(c => { c.textContent = c.dataset.count; });
      return;
    }

    const DURATION = 1000;
    const STAGGER = 90;

    counters.forEach((counter, index) => {
      const target = parseInt(counter.dataset.count, 10);
      const startAt = performance.now() + index * STAGGER;
      let lastShown = -1;

      function update(now) {
        if (now < startAt) {
          requestAnimationFrame(update);
          return;
        }

        const progress = Math.min((now - startAt) / DURATION, 1);
        const eased = easeOutExpo(progress);
        const value = progress === 1 ? target : Math.round(eased * target);

        if (value !== lastShown) {
          counter.textContent = value;
          lastShown = value;
        }

        if (progress < 1) {
          requestAnimationFrame(update);
        } else {
          counter.textContent = target;
        }
      }

      requestAnimationFrame(update);
    });
  }

  /* ============================================
     SCROLL PROGRESS
     ============================================ */
  function initScrollProgress() {
    const bar = document.getElementById('scrollProgressBar');
    if (!bar) return;

    let ticking = false;

    function updateProgress() {
      ticking = false;
      const scrollTop = getScrollY();
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.width = progress + '%';
    }

    function scheduleUpdate() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(updateProgress);
    }

    scheduleUpdate();
    window.addEventListener('scroll', scheduleUpdate, { passive: true });
  }

  function scrollToY(top) {
    window.scrollTo({ top, behavior: 'auto' });
  }

  function isBookingHash(hash) {
    return BOOKING_HASHES.has(hash);
  }

  function scrollToBookingForm() {
    const form = document.getElementById('bookingForm');
    if (!form) return false;
    form.scrollIntoView({ block: 'start', behavior: 'auto' });
    return true;
  }

  function scrollToHash(hash) {
    if (!hash || hash === '#') return false;

    if (hash === '#home') {
      scrollToY(0);
      return true;
    }

    if (isBookingHash(hash)) {
      const scrolled = scrollToBookingForm();
      if (scrolled && hash === '#contact') {
        history.replaceState(null, '', '#bookingForm');
      }
      return scrolled;
    }

    const target = document.querySelector(hash);
    if (!target) return false;

    const scrollTarget = getAnchorScrollTarget(target) || target;
    scrollTarget.scrollIntoView({ block: 'start', behavior: 'auto' });
    return true;
  }

  function scheduleHashScroll(hash) {
    if (!hash || hash === '#') return;

    const run = () => scrollToHash(hash);

    if (document.readyState === 'complete') {
      run();
      return;
    }

    window.addEventListener('load', run, { once: true });
  }

  function getNavbarScrollOffset() {
    const navbar = document.getElementById('navbar');
    if (navbar) return navbar.offsetHeight;
    const root = getComputedStyle(document.documentElement);
    const height = parseFloat(root.getPropertyValue('--navbar-height'));
    return Number.isFinite(height) ? height : 80;
  }

  function getAnchorScrollTarget(element) {
    if (!element) return null;
    if (element.id === 'home') return null;

    if (element.id === 'contact') {
      return (
        document.getElementById('bookingForm') ||
        element.querySelector('.contact__form') ||
        element
      );
    }

    if (element.id === 'bookingForm') {
      return element;
    }

    if (element.classList.contains('section')) {
      return (
        element.querySelector(':scope > .container > .section__header') ||
        element.querySelector('.section__header') ||
        element.querySelector('[id$="-heading"]') ||
        element
      );
    }

    if (element.id === 'experiences') {
      return element.querySelector('.experiences__header') || element;
    }

    if (element.id === 'about') {
      return document.getElementById('about-heading') || element.querySelector('.about__content') || element;
    }

    if (element.classList.contains('safaris-circuit-block')) {
      return element.querySelector('.safaris-circuit-block__title') || element;
    }

    return (
      element.querySelector('.section__header, .experiences__header, [id$="-heading"]') || element
    );
  }

  function getScrollPositionForElement(el) {
    return Math.max(0, el.getBoundingClientRect().top + getScrollY() - getNavbarScrollOffset());
  }

  /* ============================================
     GALLERY FILTERS
     ============================================ */
  let galleryPaginationGoTo = null;

  function initGallery() {
    const filters = document.querySelectorAll('.gallery__filter');
    const items = document.querySelectorAll('.gallery__item');
    const masonry = document.getElementById('galleryMasonry');

    if (!filters.length || !items.length) return;

    function scrollToGalleryContent() {
      const target =
        document.querySelector('#gallery .section__header') ||
        document.getElementById('gallery-heading') ||
        masonry;
      if (!target) return;
      scrollToY(getScrollPositionForElement(target));
    }

    filters.forEach(filter => {
      filter.addEventListener('click', () => {
        const category = filter.dataset.filter;

        filters.forEach(f => {
          f.classList.remove('active');
          f.setAttribute('aria-selected', 'false');
        });
        filter.classList.add('active');
        filter.setAttribute('aria-selected', 'true');

        items.forEach(item => {
          const show = category === 'all' || item.dataset.category === category;
          if (show) {
            item.classList.remove('hidden');
            item.classList.add('is-visible');
          } else {
            item.classList.add('hidden');
            item.classList.remove('gallery__item--page-hidden');
          }
        });

        if (masonry) {
          masonry.classList.toggle('gallery__masonry--filtered', category !== 'all');
        }

        if (galleryPaginationGoTo) {
          galleryPaginationGoTo(1);
        }

        requestAnimationFrame(() => {
          scrollToGalleryContent();
        });
      });
    });

  }

  function getPackageGridCols() {
    const w = window.innerWidth;
    if (w < 768) return 1;
    if (w < 1024) return 2;
    return 4;
  }

  function packageCardCells(card) {
    const cols = getPackageGridCols();
    if (cols >= 2 && card.classList.contains('package-card--featured')) {
      return Math.min(2, cols);
    }
    return 1;
  }

  function buildPackagePages(cards) {
    const cols = getPackageGridCols();
    const pages = [];
    let current = [];
    let used = 0;

    cards.forEach((card) => {
      const need = packageCardCells(card);
      if (used + need > cols && current.length) {
        pages.push(current);
        current = [];
        used = 0;
      }
      current.push(card);
      used += need;
      if (used >= cols) {
        pages.push(current);
        current = [];
        used = 0;
      }
    });

    if (current.length) pages.push(current);
    return pages;
  }

  function getGalleryPerPage() {
    const w = window.innerWidth;
    if (w < 768) return 4;
    if (w < 1024) return 6;
    return 6;
  }

  function initSafarisPagination() {
    const blocks = document.querySelectorAll('.safaris-circuit-block');
    if (!blocks.length) return;

    blocks.forEach((block) => {
      const grid = block.querySelector('.packages__grid');
      if (!grid) return;

      const cards = Array.from(grid.querySelectorAll('.package-card'));
      let pages = buildPackagePages(cards);
      if (pages.length <= 1) return;

      let page = 1;

      const nav = document.createElement('nav');
      nav.className = 'packages__pagination';
      nav.setAttribute('aria-label', 'Package pages for ' + (block.querySelector('.safaris-circuit-block__title span')?.textContent || 'circuit'));

      const prevBtn = document.createElement('button');
      prevBtn.type = 'button';
      prevBtn.className = 'packages__page-btn';
      prevBtn.setAttribute('aria-label', 'Previous packages page');
      prevBtn.innerHTML = '<i class="fa-solid fa-chevron-left" aria-hidden="true"></i>';

      const pagesEl = document.createElement('div');
      pagesEl.className = 'packages__pages';

      const nextBtn = document.createElement('button');
      nextBtn.type = 'button';
      nextBtn.className = 'packages__page-btn';
      nextBtn.setAttribute('aria-label', 'Next packages page');
      nextBtn.innerHTML = '<i class="fa-solid fa-chevron-right" aria-hidden="true"></i>';

      const statusEl = document.createElement('span');
      statusEl.className = 'packages__status';
      statusEl.setAttribute('aria-live', 'polite');

      nav.append(prevBtn, pagesEl, nextBtn, statusEl);
      grid.after(nav);

      function totalPages() {
        return Math.max(1, pages.length);
      }

      function renderPageButtons() {
        const tp = totalPages();
        pagesEl.innerHTML = '';
        for (let i = 1; i <= tp; i += 1) {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'packages__page-num' + (i === page ? ' packages__page-num--active' : '');
          btn.textContent = String(i);
          btn.setAttribute('aria-label', 'Packages page ' + i);
          if (i === page) btn.setAttribute('aria-current', 'page');
          btn.addEventListener('click', () => goToPage(i));
          pagesEl.appendChild(btn);
        }
      }

      function goToPage(next) {
        pages = buildPackagePages(cards);
        const tp = totalPages();
        page = Math.min(Math.max(1, next), tp);
        const visible = new Set(pages[page - 1] || []);
        cards.forEach((card) => {
          card.classList.toggle('package-card--page-hidden', !visible.has(card));
        });
        prevBtn.disabled = page <= 1;
        nextBtn.disabled = page >= tp;
        const shown = pages[page - 1]?.length || 0;
        const startIdx = cards.indexOf(pages[page - 1][0]) + 1;
        const endIdx = cards.indexOf(pages[page - 1][shown - 1]) + 1;
        statusEl.textContent = 'Page ' + page + ' of ' + tp + ' · packages ' + startIdx + '–' + endIdx + ' of ' + cards.length;
        renderPageButtons();
      }

      prevBtn.addEventListener('click', () => goToPage(page - 1));
      nextBtn.addEventListener('click', () => goToPage(page + 1));

      let resizeTimer;
      window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => goToPage(page), 150);
      });

      goToPage(1);
    });
  }

  function initGalleryPagination() {
    const root = document.getElementById('galleryPagination');
    const masonry = document.getElementById('galleryMasonry');
    if (!root || !masonry) return;

    const items = Array.from(masonry.querySelectorAll('.gallery__item'));
    const prevBtn = root.querySelector('[data-gallery-prev]');
    const nextBtn = root.querySelector('[data-gallery-next]');
    const pagesEl = root.querySelector('[data-gallery-pages]');
    const statusEl = root.querySelector('[data-gallery-status]');
    let page = 1;

    function visibleItems() {
      return items.filter((item) => !item.classList.contains('hidden'));
    }

    function totalPages() {
      const vis = visibleItems();
      return Math.max(1, Math.ceil(vis.length / getGalleryPerPage()));
    }

    function renderPageButtons() {
      if (!pagesEl) return;
      const tp = totalPages();
      pagesEl.innerHTML = '';
      for (let i = 1; i <= tp; i += 1) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'gallery__page-num' + (i === page ? ' gallery__page-num--active' : '');
        btn.textContent = String(i);
        btn.setAttribute('aria-label', 'Gallery page ' + i);
        if (i === page) btn.setAttribute('aria-current', 'page');
        btn.addEventListener('click', () => goToPage(i));
        pagesEl.appendChild(btn);
      }
    }

    function goToPage(next) {
      const perPage = getGalleryPerPage();
      const vis = visibleItems();
      const tp = Math.max(1, Math.ceil(vis.length / perPage));
      page = Math.min(Math.max(1, next), tp);
      const start = (page - 1) * perPage;

      vis.forEach((item, index) => {
        item.classList.toggle('gallery__item--page-hidden', index < start || index >= start + perPage);
      });

      if (prevBtn) prevBtn.disabled = page <= 1;
      if (nextBtn) nextBtn.disabled = page >= tp;
      if (statusEl) {
        statusEl.textContent =
          vis.length > perPage
            ? 'Page ' + page + ' of ' + tp + ' · ' + vis.length + ' photos'
            : '';
      }
      root.hidden = vis.length <= perPage;
      renderPageButtons();
    }

    galleryPaginationGoTo = goToPage;

    if (prevBtn) prevBtn.addEventListener('click', () => goToPage(page - 1));
    if (nextBtn) nextBtn.addEventListener('click', () => goToPage(page + 1));

    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => goToPage(page), 150);
    });

    goToPage(1);
  }

  /* ============================================
     LIGHTBOX
     ============================================ */
  function initLightbox() {
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightboxImage');
    const lightboxCaption = document.getElementById('lightboxCaption');
    const closeBtn = document.getElementById('lightboxClose');
    const prevBtn = document.getElementById('lightboxPrev');
    const nextBtn = document.getElementById('lightboxNext');
    const items = document.querySelectorAll('.gallery__item');

    if (!lightbox) return;

    let currentIndex = 0;
    let visibleItems = [];

    function getVisibleItems() {
      return Array.from(items).filter(
        (item) => !item.classList.contains('hidden') && !item.classList.contains('gallery__item--page-hidden')
      );
    }

    function openLightbox(index) {
      visibleItems = getVisibleItems();
      currentIndex = index;
      showImage();
      lightbox.classList.add('active');
      lightbox.setAttribute('aria-hidden', 'false');
      document.body.classList.add('menu-open');
    }

    function closeLightbox() {
      lightbox.classList.remove('active');
      lightbox.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('menu-open');
    }

    function showImage() {
      const item = visibleItems[currentIndex];
      if (!item) return;
      const img = item.querySelector('img');
      const caption = item.querySelector('.gallery__item-overlay span');
      const fullSrc = img.dataset.full || img.dataset.src || img.currentSrc || img.src;
      if (lightboxImg.src !== fullSrc) {
        lightboxImg.src = fullSrc;
      }
      lightboxImg.alt = img.alt;
      lightboxCaption.textContent = caption?.textContent || img.alt;
    }

    function nextImage() {
      currentIndex = (currentIndex + 1) % visibleItems.length;
      showImage();
    }

    function prevImage() {
      currentIndex = (currentIndex - 1 + visibleItems.length) % visibleItems.length;
      showImage();
    }

    items.forEach((item, index) => {
      item.addEventListener('click', () => {
        visibleItems = getVisibleItems();
        currentIndex = visibleItems.indexOf(item);
        openLightbox(currentIndex);
      });
    });

    closeBtn?.addEventListener('click', closeLightbox);
    prevBtn?.addEventListener('click', prevImage);
    nextBtn?.addEventListener('click', nextImage);

    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) closeLightbox();
    });

    document.addEventListener('keydown', (e) => {
      if (!lightbox.classList.contains('active')) return;
      if (e.key === 'Escape') closeLightbox();
      if (e.key === 'ArrowRight') nextImage();
      if (e.key === 'ArrowLeft') prevImage();
    });
  }

  /* ============================================
     ABOUT PAGE GALLERY PAGINATION
     ============================================ */
  function initAboutGallery() {
    const root = document.getElementById('aboutGallery');
    if (!root) return;

    const items = Array.from(root.querySelectorAll('.about-gallery__item'));
    const perPage = 5;
    const totalPages = Math.max(1, Math.ceil(items.length / perPage));
    let page = 1;

    const grid = root.querySelector('.about-gallery__grid');
    const prevBtn = root.querySelector('[data-about-gallery-prev]');
    const nextBtn = root.querySelector('[data-about-gallery-next]');
    const pagesEl = root.querySelector('.about-gallery__pages');
    const statusEl = root.querySelector('.about-gallery__status');

    function renderPageButtons() {
      if (!pagesEl) return;
      pagesEl.innerHTML = '';
      for (let i = 1; i <= totalPages; i += 1) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'about-gallery__page' + (i === page ? ' about-gallery__page--active' : '');
        btn.textContent = String(i);
        btn.setAttribute('aria-label', 'Page ' + i);
        if (i === page) btn.setAttribute('aria-current', 'page');
        btn.addEventListener('click', () => goToPage(i));
        pagesEl.appendChild(btn);
      }
    }

    function goToPage(next) {
      page = Math.min(Math.max(1, next), totalPages);
      const start = (page - 1) * perPage;
      items.forEach((item, index) => {
        const visible = index >= start && index < start + perPage;
        item.hidden = !visible;
        item.classList.toggle('about-gallery__item--visible', visible);
      });
      if (prevBtn) prevBtn.disabled = page <= 1;
      if (nextBtn) nextBtn.disabled = page >= totalPages;
      if (statusEl) {
        statusEl.textContent = 'Page ' + page + ' of ' + totalPages;
      }
      renderPageButtons();
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', () => goToPage(page - 1));
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', () => goToPage(page + 1));
    }

    goToPage(1);
  }

  /* ============================================
     CONTACT LINKS
     ============================================ */
  function initContactLinks() {
    const cfg = window.SITE_CONFIG;
    if (!cfg) return;

    const waUrl = window.siteWhatsAppUrl ? window.siteWhatsAppUrl() : null;
    if (waUrl) {
      document.querySelectorAll('[data-whatsapp]').forEach((el) => {
        el.href = waUrl;
      });
      const float = document.getElementById('whatsappFloat');
      if (float) float.href = waUrl;
    }

    document.querySelectorAll('[data-contact-email]').forEach((el) => {
      el.href = 'mailto:' + cfg.email;
      if (el.tagName === 'A' && !el.textContent.trim()) {
        el.textContent = cfg.email;
      }
    });

    document.querySelectorAll('[data-contact-phone]').forEach((el) => {
      el.href = 'tel:' + cfg.phoneTel;
      if (el.tagName === 'A' && !el.textContent.trim()) {
        el.textContent = cfg.phoneDisplay;
      }
    });

    document.querySelectorAll('[data-contact-location]').forEach((el) => {
      el.textContent = cfg.location;
    });

    document.querySelectorAll('[data-footer-credit]').forEach((el) => {
      el.textContent = cfg.footerCredit;
    });
  }

  /* ============================================
     BOOKING FORM
     ============================================ */
  function initBookingForm() {
    const form = document.getElementById('bookingForm');
    if (!form) return;

    const packageSelect = document.getElementById('safariPackage');
    const packageHint = document.getElementById('safariPackageHint');

    const fields = {
      name: { required: true, minLength: 2 },
      email: { required: true, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
      country: { required: true, minLength: 2 },
      phone: { required: false },
      adults: { required: true, min: 1, max: 24 },
      children: { required: false, min: 0, max: 16 },
      travelStyle: { required: false },
      safariPackage: { required: false },
      travelDate: { required: true },
      destination: { required: true }
    };

    function updatePackageHint(slug) {
      if (!packageHint) return;
      const pkg = packagesBySlug[slug];
      if (!pkg) {
        packageHint.hidden = true;
        packageHint.textContent = '';
        return;
      }
      packageHint.hidden = false;
      packageHint.textContent = 'Enquiring about: ' + pkg.name + (pkg.duration ? ' · ' + pkg.duration : '');
    }

    function populatePackageSelect(packages) {
      if (!packageSelect) return;

      const byCircuit = {};
      packages.forEach((pkg) => {
        const circuit = pkg.circuit === 'Coastal & Islands' ? 'Zanzibar & Islands' : pkg.circuit;
        if (!byCircuit[circuit]) byCircuit[circuit] = [];
        byCircuit[circuit].push(pkg);
        packagesBySlug[pkg.slug] = pkg;
      });

      PACKAGE_CIRCUIT_ORDER.forEach((circuit) => {
        const groupPackages = byCircuit[circuit];
        if (!groupPackages?.length) return;

        const optgroup = document.createElement('optgroup');
        optgroup.label = circuit;
        groupPackages.forEach((pkg) => {
          const option = document.createElement('option');
          option.value = pkg.slug;
          option.textContent = pkg.name + (pkg.duration ? ' · ' + pkg.duration : '');
          optgroup.appendChild(option);
        });
        packageSelect.appendChild(optgroup);
      });

      Object.keys(byCircuit).forEach((circuit) => {
        if (PACKAGE_CIRCUIT_ORDER.includes(circuit)) return;
        const groupPackages = byCircuit[circuit];
        const optgroup = document.createElement('optgroup');
        optgroup.label = circuit;
        groupPackages.forEach((pkg) => {
          const option = document.createElement('option');
          option.value = pkg.slug;
          option.textContent = pkg.name + (pkg.duration ? ' · ' + pkg.duration : '');
          optgroup.appendChild(option);
        });
        packageSelect.appendChild(optgroup);
      });
    }

    applyPackageSelection = function applyPackageSelection(slug) {
      if (!packageSelect || !slug) return;
      const hasOption = [...packageSelect.options].some((option) => option.value === slug);
      if (!hasOption) return;
      packageSelect.value = slug;
      updatePackageHint(slug);
    };

    if (packageSelect) {
      fetch(safariPackagesUrl())
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          if (!data?.packages?.length) return;
          populatePackageSelect(data.packages);
          applyPackageSelection(getPackageSlugFromUrl());
          if (isBookingHash(window.location.hash)) {
            scrollToBookingForm();
          }
        })
        .catch(() => { /* dropdown keeps default options */ });

      packageSelect.addEventListener('change', () => {
        updatePackageHint(packageSelect.value);
      });
    }

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (validateForm()) {
        submitForm();
      }
    });

    Object.keys(fields).forEach(name => {
      const input = form.querySelector(`[name="${name}"]`);
      if (input) {
        input.addEventListener('blur', () => validateField(name));
        input.addEventListener('input', () => clearError(name));
        if (input.tagName === 'SELECT') {
          input.addEventListener('change', () => clearError(name));
        }
      }
    });

    function validateField(name) {
      const config = fields[name];
      const input = form.querySelector(`[name="${name}"]`);
      const errorEl = document.getElementById(name + 'Error');
      if (!input || !errorEl) return true;

      let valid = true;
      let message = '';

      const value = input.value.trim();

      if (config.required && !value) {
        valid = false;
        message = 'This field is required';
      } else if (config.minLength && value.length < config.minLength) {
        valid = false;
        message = `Minimum ${config.minLength} characters required`;
      } else if (config.pattern && !config.pattern.test(value)) {
        valid = false;
        message = 'Please enter a valid email address';
      } else if (name === 'adults' && value) {
        const n = Number(value);
        if (!Number.isFinite(n) || n < (config.min || 1) || n > (config.max || 24)) {
          valid = false;
          message = `Enter adults between ${config.min || 1} and ${config.max || 24}`;
        }
      } else if (name === 'children' && value !== '') {
        const n = Number(value);
        if (!Number.isFinite(n) || n < 0 || n > 16) {
          valid = false;
          message = 'Enter children between 0 and 16';
        }
      } else if (name === 'travelDate' && value) {
        const selected = new Date(value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (selected < today) {
          valid = false;
          message = 'Travel date must be in the future';
        }
      }

      if (!valid) {
        input.classList.add('error');
        errorEl.textContent = message;
      } else {
        input.classList.remove('error');
        errorEl.textContent = '';
      }

      return valid;
    }

    function clearError(name) {
      const input = form.querySelector(`[name="${name}"]`);
      const errorEl = document.getElementById(name + 'Error');
      input?.classList.remove('error');
      if (errorEl) errorEl.textContent = '';
    }

    function validateForm() {
      return Object.keys(fields).every(name => validateField(name));
    }

    function getSelectedPackageLabel(slug) {
      if (!slug) return '';
      const pkg = packagesBySlug[slug];
      return pkg ? pkg.name : slug;
    }

    function submitForm() {
      const btn = document.getElementById('submitBtn');
      const btnText = btn.querySelector('.contact__submit-text');
      const btnLoading = btn.querySelector('.contact__submit-loading');
      const success = document.getElementById('formSuccess');
      const cfg = window.SITE_CONFIG || { email: 'info@safariandbushretreats.com', businessName: 'Safari and Bush Retreats' };
      const data = new FormData(form);

      const name = (data.get('name') || '').toString().trim();
      const email = (data.get('email') || '').toString().trim();
      const phone = (data.get('phone') || '').toString().trim();
      const country = (data.get('country') || '').toString().trim();
      const adults = (data.get('adults') || '').toString().trim();
      const children = (data.get('children') || '').toString().trim();
      const travelStyle = (data.get('travelStyle') || '').toString().trim();
      const safariPackage = (data.get('safariPackage') || '').toString().trim();
      const safariPackageLabel = getSelectedPackageLabel(safariPackage);
      const travelDate = (data.get('travelDate') || '').toString().trim();
      const destination = (data.get('destination') || '').toString().trim();
      const message = (data.get('message') || '').toString().trim();

      const subject = safariPackageLabel
        ? 'Safari Inquiry - ' + safariPackageLabel + ' - ' + name
        : 'Safari Inquiry - ' + name;
      const body = [
        'New safari inquiry via Safari & Bush Retreats website',
        '',
        'Name: ' + name,
        'Email: ' + email,
        phone ? 'Phone: ' + phone : null,
        'Country: ' + country,
        'Adults: ' + adults,
        children ? 'Children: ' + children : null,
        travelStyle ? 'Travel style: ' + travelStyle : null,
        safariPackageLabel ? 'Safari package: ' + safariPackageLabel : null,
        'Travel date: ' + travelDate,
        'Destination: ' + destination,
        message ? '\nMessage:\n' + message : null,
        '',
        '- ' + cfg.businessName + ' inquiry'
      ].filter(Boolean).join('\n');

      btnText.hidden = true;
      btnLoading.hidden = false;
      btn.disabled = true;

      const endpoint = cfg.formSubmitEndpoint;
      const payload = {
        _subject: subject,
        _template: 'table',
        name: name,
        email: email,
        phone: phone || '-',
        country: country,
        adults: adults,
        children: children || '0',
        travelStyle: travelStyle || 'Flexible',
        safariPackage: safariPackageLabel || 'Custom / not selected',
        travelDate: travelDate,
        destination: destination,
        message: message || '-'
      };

      function showSuccess(msg) {
        btnText.hidden = false;
        btnLoading.hidden = true;
        btn.disabled = false;
        success.hidden = false;
        const successText = success.querySelector('p');
        if (successText) successText.textContent = msg;
        form.reset();
        if (packageHint) {
          packageHint.hidden = true;
          packageHint.textContent = '';
        }
        setTimeout(() => { success.hidden = true; }, 12000);
      }

      function mailtoFallback() {
        window.location.href = 'mailto:' + cfg.email
          + '?subject=' + encodeURIComponent(subject)
          + '&body=' + encodeURIComponent(body);
        showSuccess('Your email app should open now - send the message and our safari experts will reply within 24 hours. Prefer WhatsApp? Use the button on the right.');
      }

      if (!endpoint) {
        mailtoFallback();
        return;
      }

      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload)
      })
        .then((res) => {
          if (!res.ok) throw new Error('submit failed');
          return res.json();
        })
        .then(() => {
          showSuccess('Thank you! Your inquiry was sent successfully. Our safari experts will reply within 24 hours.');
        })
        .catch(() => {
          mailtoFallback();
        });
    }
  }

  /* ============================================
     SCROLL REVEAL - single CSS + IntersectionObserver (Selcom-style)
     ============================================ */
  function initReveal() {
    const staggerParents = document.querySelectorAll(REVEAL_STAGGER_SELECTORS);
    const targets = document.querySelectorAll(REVEAL_SELECTORS);
    const all = [...staggerParents, ...targets];

    staggerParents.forEach((parent) => {
      parent.classList.add('reveal-stagger');
      Array.from(parent.children).forEach((child, i) => {
        child.style.setProperty('--reveal-delay', `${i * 0.07}s`);
      });
    });

    targets.forEach((el) => el.classList.add('reveal'));

    if (prefersReducedMotion) {
      all.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: '0px 0px -6% 0px', threshold: 0.05 }
    );

    function mount(el) {
      if (el.classList.contains('hidden')) return;
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight * 0.94 && rect.bottom > 0) {
        el.classList.add('is-visible');
      } else {
        observer.observe(el);
      }
    }

    all.forEach(mount);
    window.__revealObserver = observer;
  }

  /* ============================================
     THEME TOGGLE
     ============================================ */
  function initTheme() {
    const STORAGE_KEY = 'sbr-theme';
    const root = document.documentElement;
    const toggles = [
      document.getElementById('themeToggle'),
      document.getElementById('themeToggleMobile')
    ].filter(Boolean);

    function getTheme() {
      return root.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
    }

    function applyTheme(theme, persist) {
      const isLight = theme === 'light';
      if (isLight) {
        root.setAttribute('data-theme', 'light');
      } else {
        root.removeAttribute('data-theme');
      }

      toggles.forEach((btn) => {
        btn.setAttribute('aria-pressed', isLight ? 'true' : 'false');
        btn.setAttribute(
          'aria-label',
          isLight ? 'Switch to dark theme' : 'Switch to light theme'
        );
      });

      if (persist) {
        try {
          localStorage.setItem(STORAGE_KEY, isLight ? 'light' : 'dark');
        } catch (e) { /* ignore */ }
      }
    }

    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'light') {
        applyTheme('light', false);
      } else if (!saved && window.matchMedia('(prefers-color-scheme: light)').matches) {
        /* dark remains default - only explicit saved light applies */
      }
    } catch (e) { /* ignore */ }

    toggles.forEach((btn) => {
      btn.addEventListener('click', () => {
        applyTheme(getTheme() === 'light' ? 'dark' : 'light', true);
      });
    });
  }

  function initImageDecoding() {
    const hero = document.getElementById('home');
    const firstHeroImg = hero?.querySelector('.hero-slide__img');

    document.querySelectorAll('img').forEach((img) => {
      if (!img.hasAttribute('decoding')) {
        img.decoding = 'async';
      }

      const isFirstHero = img === firstHeroImg;
      const inHero = img.closest('.hero-swiper');

      if (isFirstHero) {
        img.loading = 'eager';
        img.fetchPriority = 'high';
        return;
      }

      if (!img.hasAttribute('loading') && !inHero) {
        img.loading = 'lazy';
      }

      if (inHero && !isFirstHero && !img.hasAttribute('loading')) {
        img.loading = 'lazy';
      }
    });
  }

  /* ============================================
     IN-PAGE ANCHOR NAV (instant jump, no smooth scroll)
     ============================================ */
  function initSmoothScroll() {
    document.querySelectorAll('a[href*="#"]').forEach(anchor => {
      anchor.addEventListener('click', (e) => {
        const rawHref = anchor.getAttribute('href');
        if (!rawHref || rawHref === '#') return;

        let url;
        try {
          url = new URL(anchor.href, window.location.href);
        } catch (err) {
          return;
        }

        const targetId = url.hash;
        if (!targetId || targetId === '#') return;

        const sameDocument =
          url.pathname === window.location.pathname ||
          (url.pathname.endsWith('/index.html') && window.location.pathname.endsWith('/')) ||
          (url.pathname.endsWith('/') && window.location.pathname.endsWith('index.html'));

        if (!sameDocument) return;

        if (isBookingHash(targetId)) {
          e.preventDefault();
          const pkg = url.searchParams.get('package');
          if (pkg && applyPackageSelection) {
            applyPackageSelection(pkg);
          }
          scrollToHash(targetId);
          history.pushState(null, '', buildBookingHashUrl(pkg));
          return;
        }

        const target = document.querySelector(targetId);
        if (!target) return;

        e.preventDefault();

        if (targetId === '#home') {
          scrollToY(0);
          history.pushState(null, '', targetId);
          return;
        }

        const scrollTarget = getAnchorScrollTarget(target);
        if (!scrollTarget) return;

        scrollTarget.scrollIntoView({ block: 'start', behavior: 'auto' });
        history.pushState(null, '', targetId);
      });
    });

    window.addEventListener('hashchange', () => {
      scheduleHashScroll(window.location.hash);
    });
  }

  function initHashScroll() {
    scheduleHashScroll(window.location.hash);
  }

  /* ============================================
     ACTIVE NAV LINKS
     ============================================ */
  function initActiveNavLinks() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.navbar__link, .mobile-menu__link');

    if (!sections.length) return;

    let activeId = '';
    let framePending = false;

    function applyActiveNav(id) {
      if (!id || id === activeId) return;
      activeId = id;
      navLinks.forEach(link => {
        link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
      });
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            if (!framePending) {
              framePending = true;
              requestAnimationFrame(() => {
                framePending = false;
                applyActiveNav(id);
              });
            }
          }
        });
      },
      { rootMargin: '-40% 0px -55% 0px', threshold: 0 }
    );

    sections.forEach(section => observer.observe(section));
  }

  /* ============================================
     PAINT - pause expensive layers off-screen
     ============================================ */
  function initPaintOptimizations() {
    const hero = document.getElementById('home');
    if (!hero) return;

    const glassLayers = hero.querySelectorAll(
      '.hero__overlay, .hero__gold-tint, .hero__vignette, .hero__text-backdrop, .hero-slide__gold-wash, .hero-slide__shade'
    );

    const observer = new IntersectionObserver(
      ([entry]) => {
        const hidden = !entry.isIntersecting;
        glassLayers.forEach((layer) => {
          layer.style.visibility = hidden ? 'hidden' : '';
        });
      },
      { threshold: 0.05 }
    );

    observer.observe(hero);
  }

  /* ============================================
     WHATSAPP - hide during hero for clean view
     ============================================ */
  function initWhatsappVisibility() {
    const float = document.getElementById('whatsappFloat');
    const hero = document.getElementById('home');
    if (!float || !hero) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const show = !entry.isIntersecting;
        float.classList.toggle('is-visible', show);
        float.setAttribute('aria-hidden', show ? 'false' : 'true');
      },
      { threshold: 0.15, rootMargin: '0px 0px -80px 0px' }
    );

    observer.observe(hero);
  }

  /* ============================================
     IMAGE FALLBACKS
     ============================================ */
  function initImageFallbacks() {
    const inDestinations = /\/destinations\//.test(window.location.pathname);
    const fallback = inDestinations
      ? '../assets/images/serengeti3.jpg'
      : 'assets/images/serengeti3.jpg';

    document.querySelectorAll('img').forEach(img => {
      img.addEventListener('error', function onError() {
        const resolved = new URL(this.src, window.location.href).href;
        const resolvedFallback = new URL(fallback, window.location.href).href;
        if (resolved !== resolvedFallback) {
          this.src = fallback;
        }
        this.removeEventListener('error', onError);
      }, { once: true });
    });
  }

  /* ============================================
     SITE SEARCH (AJAX index)
     ============================================ */
  function initSiteSearch() {
    const tools = document.querySelector('.navbar__tools');
    if (!tools || document.getElementById('searchToggle')) return;

    const modal = document.createElement('div');
    modal.className = 'site-search';
    modal.id = 'siteSearch';
    modal.setAttribute('aria-hidden', 'true');
    modal.innerHTML = `
      <div class="site-search__backdrop" id="searchBackdrop"></div>
      <div class="site-search__panel" role="dialog" aria-modal="true" aria-labelledby="searchHeading">
        <div class="site-search__head">
          <h2 class="site-search__title" id="searchHeading">Search Safari &amp; Bush</h2>
          <button type="button" class="site-search__close" id="searchClose" aria-label="Close search">
            <i class="fa-solid fa-xmark" aria-hidden="true"></i>
          </button>
        </div>
        <div class="site-search__field">
          <i class="fa-solid fa-magnifying-glass site-search__icon" aria-hidden="true"></i>
          <input type="search" class="site-search__input" id="searchInput" placeholder="Destinations, safaris, circuits, Kenya…" autocomplete="off" aria-controls="searchResults">
        </div>
        <p class="site-search__hint" id="searchHint">Type to search our destinations and packages</p>
        <ul class="site-search__results" id="searchResults" role="listbox"></ul>
      </div>
    `;
    document.body.appendChild(modal);

    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'navbar__search-toggle';
    toggle.id = 'searchToggle';
    toggle.setAttribute('aria-label', 'Search website');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-controls', 'siteSearch');
    toggle.innerHTML = '<i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>';
    tools.insertBefore(toggle, tools.firstChild);

    const backdrop = document.getElementById('searchBackdrop');
    const closeBtn = document.getElementById('searchClose');
    const input = document.getElementById('searchInput');
    const results = document.getElementById('searchResults');
    const hint = document.getElementById('searchHint');

    let indexItems = [];
    let indexLoaded = false;
    let indexPromise = null;
    let activeIndex = -1;

    function siteBasePath() {
      const script = document.querySelector('script[src*="js/main.js"]');
      if (script) {
        return (script.getAttribute('src') || '').replace(/js\/main\.js(?:\?.*)?$/, '');
      }
      const link = document.querySelector('link[href*="css/style.css"]');
      if (link) {
        return (link.getAttribute('href') || '').replace(/css\/style\.css(?:\?.*)?$/, '');
      }
      return '';
    }

    function searchIndexUrl() {
      return siteBasePath() + 'data/search-index.json';
    }

    function loadIndex(force) {
      if (!force && indexLoaded && indexItems.length) {
        return Promise.resolve(indexItems);
      }
      if (indexPromise) {
        return indexPromise;
      }

      indexPromise = fetch(searchIndexUrl())
        .then((res) => {
          if (!res.ok) throw new Error('Search index not found');
          return res.json();
        })
        .then((data) => {
          indexItems = Array.isArray(data.items) ? data.items : [];
          indexLoaded = indexItems.length > 0;
          return indexItems;
        })
        .catch(() => {
          if (!indexItems.length) indexLoaded = false;
          return indexItems;
        })
        .finally(() => {
          indexPromise = null;
        });

      return indexPromise;
    }

    function scoreItem(item, query) {
      const q = query.toLowerCase().trim();
      const title = (item.title || '').toLowerCase();
      const search = (item.search || item.keywords || '').toLowerCase();
      let score = 0;
      if (title === q) score += 100;
      else if (title.startsWith(q)) score += 60;
      else if (title.includes(q)) score += 40;
      if (search.includes(q)) score += 20;
      const words = q.split(/\s+/).filter(Boolean);
      words.forEach((w) => {
        if (title.includes(w)) score += 8;
        if (search.includes(w)) score += 4;
      });
      return score;
    }

    function renderResults(query, retried) {
      results.innerHTML = '';
      activeIndex = -1;

      if (!query || query.length < 2) {
        hint.textContent = indexItems.length
          ? 'Type at least 2 characters to search'
          : 'Type to search our destinations and packages';
        return;
      }

      if (!indexItems.length) {
        if (retried) {
          hint.textContent = 'Search index unavailable. Use a local server (npx serve .) and refresh the page.';
          return;
        }
        hint.textContent = 'Loading search index…';
        loadIndex(true).then(() => renderResults(query, true));
        return;
      }

      const ranked = indexItems
        .map((item) => ({ item, score: scoreItem(item, query) }))
        .filter((r) => r.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 12);

      if (!ranked.length) {
        hint.textContent = `No results for “${query}”`;
        return;
      }

      hint.textContent = `${ranked.length} result${ranked.length === 1 ? '' : 's'}`;
      ranked.forEach(({ item }) => {
        const li = document.createElement('li');
        li.className = 'site-search__result';
        li.setAttribute('role', 'option');
        const a = document.createElement('a');
        a.href = siteBasePath() + item.url;
        a.innerHTML = `
          <span class="site-search__result-type">${item.type}</span>
          <span class="site-search__result-title">${item.title}</span>
          ${item.subtitle ? `<span class="site-search__result-sub">${item.subtitle}</span>` : ''}
        `;
        a.addEventListener('click', closeSearch);
        li.appendChild(a);
        results.appendChild(li);
      });
    }

    function openSearch() {
      modal.classList.add('is-open');
      modal.setAttribute('aria-hidden', 'false');
      toggle.setAttribute('aria-expanded', 'true');
      document.body.classList.add('search-open');
      loadIndex().then(() => {
        input.value = '';
        renderResults('');
        input.focus();
      });
    }

    function closeSearch() {
      modal.classList.remove('is-open');
      modal.setAttribute('aria-hidden', 'true');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('search-open');
      input.value = '';
      results.innerHTML = '';
      hint.textContent = 'Type to search our destinations and packages';
    }

    toggle.addEventListener('click', openSearch);
    closeBtn.addEventListener('click', closeSearch);
    backdrop.addEventListener('click', closeSearch);

    input.addEventListener('input', () => {
      renderResults(input.value.trim());
    });

    input.addEventListener('keydown', (e) => {
      const links = results.querySelectorAll('.site-search__result a');
      if (e.key === 'Escape') {
        closeSearch();
        toggle.focus();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIndex = Math.min(activeIndex + 1, links.length - 1);
        links[activeIndex]?.focus();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIndex = Math.max(activeIndex - 1, 0);
        links[activeIndex]?.focus();
      } else if (e.key === 'Enter' && activeIndex >= 0 && links[activeIndex]) {
        links[activeIndex].click();
      }
    });

    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        openSearch();
      }
    });

    loadIndex();
  }

})();
