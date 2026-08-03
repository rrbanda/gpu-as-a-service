'use strict';

document.querySelectorAll('.layer-card').forEach(function(card) {
  card.addEventListener('click', function() {
    var wasExpanded = card.classList.contains('expanded');
    document.querySelectorAll('.layer-card').forEach(function(c) { c.classList.remove('expanded'); });
    if (!wasExpanded) card.classList.add('expanded');
  });
});

document.querySelectorAll('.toggle-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.toggle-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    var pattern = btn.getAttribute('data-pattern');
    document.querySelectorAll('.pattern-view').forEach(function(v) { v.classList.remove('active'); });
    document.getElementById('pattern-' + pattern).classList.add('active');
  });
});
