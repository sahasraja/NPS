/* NPS — site interactions. No dependencies. */
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

  /* Contact form — graceful handling when no endpoint is wired yet */
  var form = document.querySelector('form[data-contact]');
  if (form) {
    form.addEventListener('submit', function (e) {
      var action = form.getAttribute('action') || '';
      if (action.indexOf('REPLACE_WITH') !== -1 || action === '' || action === '#') {
        e.preventDefault();
        var note = form.querySelector('.form-status');
        if (note) {
          note.textContent =
            'Form endpoint not configured yet. Email info@nilaproservices.com or call (908) 644-0644 in the meantime.';
          note.style.color = 'var(--warn)';
        }
      }
    });
  }

  /* Current year in footer */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
