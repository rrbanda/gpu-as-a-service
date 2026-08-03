'use strict';

var progressBar = document.getElementById('progress-bar');

function updateProgress() {
  var scrollTop = window.scrollY;
  var docHeight = document.documentElement.scrollHeight - window.innerHeight;
  var progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
  progressBar.style.width = progress + '%';
}

window.addEventListener('scroll', updateProgress, { passive: true });
updateProgress();
