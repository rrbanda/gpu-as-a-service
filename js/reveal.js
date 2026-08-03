'use strict';

var sections = document.querySelectorAll('.section');

var revealObserver = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.08, rootMargin: '0px 0px -50px 0px' });

sections.forEach(function(s) {
  if (!s.classList.contains('visible')) {
    revealObserver.observe(s);
  }
});

var navLinks = document.querySelectorAll('#side-nav a');
var navObserver = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      navLinks.forEach(function(l) { l.classList.remove('active'); });
      var id = entry.target.id;
      var link = document.querySelector('#side-nav a[href="#' + id + '"]');
      if (link) link.classList.add('active');
    }
  });
}, { threshold: 0.2, rootMargin: '-10% 0px -60% 0px' });

sections.forEach(function(s) { navObserver.observe(s); });
