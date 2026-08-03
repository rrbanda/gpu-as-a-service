'use strict';

var gpuBars = document.getElementById('gpu-bars');
var barsAnimated = false;
var barObserver = new IntersectionObserver(function(entries) {
  if (entries[0].isIntersecting && !barsAnimated) {
    barsAnimated = true;
    document.querySelectorAll('.gpu-bar-mem').forEach(function(bar) {
      bar.style.width = bar.getAttribute('data-w') + '%';
    });
    document.querySelectorAll('.gpu-bar-req').forEach(function(bar) {
      bar.style.width = bar.getAttribute('data-w') + '%';
    });
  }
}, { threshold: 0.3 });
if (gpuBars) barObserver.observe(gpuBars);

var migSlices = document.getElementById('mig-slices');
var migAnimated = false;
var migObserver = new IntersectionObserver(function(entries) {
  if (entries[0].isIntersecting && !migAnimated) {
    migAnimated = true;
    var slices = migSlices.querySelectorAll('.mig-slice');
    slices.forEach(function(slice, i) {
      setTimeout(function() { slice.classList.add('revealed'); }, i * 200);
    });
  }
}, { threshold: 0.3 });
if (migSlices) migObserver.observe(migSlices);

function animateCounter(el) {
  var target = parseFloat(el.getAttribute('data-target'));
  var suffix = el.getAttribute('data-suffix') || '';
  var prefix = el.getAttribute('data-prefix') || '';
  var decimals = parseInt(el.getAttribute('data-decimals')) || 0;
  var range = el.getAttribute('data-range') || '';
  var duration = 2000;
  var start = performance.now();

  function update(now) {
    var elapsed = now - start;
    var progress = Math.min(elapsed / duration, 1);
    var eased = 1 - Math.pow(1 - progress, 3);
    var current = target * eased;

    var display = decimals > 0 ? current.toFixed(decimals) : Math.round(current);
    el.textContent = (range ? range : '') + prefix + display + suffix;

    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

var statNumbers = document.querySelectorAll('.stat-number[data-target]');
var counterObserver = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      animateCounter(entry.target);
      counterObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

statNumbers.forEach(function(el) { counterObserver.observe(el); });
