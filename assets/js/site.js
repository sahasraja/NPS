/* NPS, site interactions. No dependencies. */
(function () {
  'use strict';

  /* Sticky header shadow */
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-stuck', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* Mobile nav */
  var toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = document.body.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* Mobile dropdown groups */
  document.querySelectorAll('.has-menu > .nav-link').forEach(function (link) {
    link.addEventListener('click', function (e) {
      if (window.matchMedia('(max-width: 1080px)').matches) {
        e.preventDefault();
        link.parentElement.classList.toggle('is-open');
      }
    });
  });

  /* Close mobile nav on resize up */
  window.addEventListener('resize', function () {
    if (!window.matchMedia('(max-width: 1080px)').matches) {
      document.body.classList.remove('nav-open');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    }
  });

  /* Reveal on scroll */
  var targets = document.querySelectorAll('.reveal');
  if (targets.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    targets.forEach(function (el, i) {
      el.style.transitionDelay = (Math.min(i % 4, 3) * 70) + 'ms';
      io.observe(el);
    });
  } else {
    targets.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* Animate metric bars when hero enters */
  document.querySelectorAll('.bar > i').forEach(function (el) {
    var w = el.getAttribute('data-w') || '70%';
    el.style.width = '0%';
    el.style.transition = 'width 1.1s cubic-bezier(.22,.8,.3,1)';
    setTimeout(function () { el.style.width = w; }, 220);
  });

  /* Contact form, graceful handling when no endpoint is wired yet */
  var form = document.querySelector('form[data-contact]');
  if (form) {
    form.addEventListener('submit', function (e) {
      var action = form.getAttribute('action') || '';
      if (action.indexOf('REPLACE_WITH') !== -1 || action === '' || action === '#') {
        e.preventDefault();
        var note = form.querySelector('.form-status');
        if (note) {
          note.textContent =
            'Form endpoint not configured yet. Email info@nilaproservices.com in the meantime.';
          note.style.color = 'var(--warn)';
        }
      }
    });
  }

  /* ------------------------------------------------------------------
     Analytics. Everything below is inert unless a GA4 Measurement ID is
     set in build.py, because the gtag stub only exists when it is.
     ------------------------------------------------------------------ */
  var GA_ON = typeof window.gtag === 'function';
  var CONSENT_KEY = 'nps-analytics-consent';

  function readConsent() {
    try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; }
  }
  function writeConsent(v) {
    try { localStorage.setItem(CONSENT_KEY, v); } catch (e) {}
  }
  function track(name, params) {
    if (GA_ON) window.gtag('event', name, params || {});
  }

  /* Consent banner. Shown once, remembered per browser. */
  var consent = document.getElementById('consent');
  if (consent && GA_ON) {
    if (!readConsent()) {
      setTimeout(function () { consent.hidden = false; }, 900);
    }
    consent.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-consent]');
      if (!btn) return;
      var choice = btn.getAttribute('data-consent');
      writeConsent(choice);
      window.gtag('consent', 'update', { analytics_storage: choice });
      consent.hidden = true;
    });
  }

  /* KPI 1: booking clicks, with the page and the CTA that produced them */
  document.querySelectorAll('a[href*="bookwithme"]').forEach(function (a) {
    a.addEventListener('click', function () {
      track('book_call_click', {
        cta_location: a.getAttribute('data-cta') || 'other',
        page_path: location.pathname,
        page_title: document.title
      });
    });
  });

  /* KPI 2: contact form, started vs completed */
  var cform = document.querySelector('form[data-contact]');
  if (cform) {
    var started = false;
    cform.addEventListener('input', function () {
      if (started) return;
      started = true;
      track('form_start', { form_id: 'contact' });
    }, { once: false });
    cform.addEventListener('submit', function () {
      track('generate_lead', {
        form_id: 'contact',
        topic: (cform.querySelector('#topic') || {}).value || '',
        timeline: (cform.querySelector('#timeline') || {}).value || ''
      });
    });
  }

  /* KPI 3: did they actually read the service page, or bounce off the top */
  if (GA_ON && /\/services\//.test(location.pathname)) {
    var fired = {};
    var onDepth = function () {
      var doc = document.documentElement;
      var pct = (window.scrollY + window.innerHeight) / doc.scrollHeight * 100;
      [50, 90].forEach(function (mark) {
        if (pct >= mark && !fired[mark]) {
          fired[mark] = true;
          track('read_depth', { percent: mark, page_path: location.pathname });
        }
      });
      if (fired[90]) window.removeEventListener('scroll', onDepth);
    };
    window.addEventListener('scroll', onDepth, { passive: true });
  }

  /* Current year in footer */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
