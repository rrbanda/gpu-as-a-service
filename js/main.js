(function() {
  'use strict';

  // Progress bar
  const progressBar = document.getElementById('progress-bar');
  function updateProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    progressBar.style.width = progress + '%';
  }

  // Section reveal with IntersectionObserver
  const sections = document.querySelectorAll('.section');
  const revealObserver = new IntersectionObserver(function(entries) {
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

  // Active nav tracking
  const navLinks = document.querySelectorAll('#side-nav a');
  const navObserver = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        navLinks.forEach(function(l) { l.classList.remove('active'); });
        const id = entry.target.id;
        const link = document.querySelector('#side-nav a[href="#' + id + '"]');
        if (link) link.classList.add('active');
      }
    });
  }, { threshold: 0.2, rootMargin: '-10% 0px -60% 0px' });

  sections.forEach(function(s) { navObserver.observe(s); });

  // GPU utilization bar animation
  const gpuBars = document.getElementById('gpu-bars');
  let barsAnimated = false;
  const barObserver = new IntersectionObserver(function(entries) {
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

  // MIG slice animation
  const migSlices = document.getElementById('mig-slices');
  let migAnimated = false;
  const migObserver = new IntersectionObserver(function(entries) {
    if (entries[0].isIntersecting && !migAnimated) {
      migAnimated = true;
      var slices = migSlices.querySelectorAll('.mig-slice');
      slices.forEach(function(slice, i) {
        setTimeout(function() { slice.classList.add('revealed'); }, i * 200);
      });
    }
  }, { threshold: 0.3 });
  if (migSlices) migObserver.observe(migSlices);

  // Layer expand/collapse
  document.querySelectorAll('.layer-card').forEach(function(card) {
    card.addEventListener('click', function() {
      var wasExpanded = card.classList.contains('expanded');
      document.querySelectorAll('.layer-card').forEach(function(c) { c.classList.remove('expanded'); });
      if (!wasExpanded) card.classList.add('expanded');
    });
  });

  // Architecture pattern toggle
  document.querySelectorAll('.toggle-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.toggle-btn').forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var pattern = btn.getAttribute('data-pattern');
      document.querySelectorAll('.pattern-view').forEach(function(v) { v.classList.remove('active'); });
      document.getElementById('pattern-' + pattern).classList.add('active');
    });
  });

  // Animated counters
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

  // Scroll event for progress bar
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();
})();

var decisionState = {};
function selectDecision(el, qId, value) {
  var parent = el.parentElement;
  parent.querySelectorAll('.decision-option').forEach(function(o) { o.classList.remove('selected'); });
  el.classList.add('selected');
  decisionState[qId] = value;

  if (decisionState.q1 && decisionState.q2 && decisionState.q3) {
    var result = document.getElementById('decision-result');
    var body = document.getElementById('result-body');
    result.style.display = 'block';

    var shared = decisionState.q1 === 'shared';
    var mixed = decisionState.q2 === 'mixed';
    var finops = decisionState.q3 === 'yes';

    var components = [];
    var html = '';

    if (shared) {
      components.push('<strong>Kueue</strong> (essential — prevents training from starving inference)');
      html += '<p style="margin-bottom:8px;"><strong>Pattern: Shared Cluster with Kueue Governance</strong></p>';
      html += '<p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:12px;">Your training and inference workloads compete for the same GPUs. Kueue provides fair-share scheduling with quotas, borrowing limits, and preemption policies. Inference gets priority; training runs in remaining capacity and can borrow when inference is idle.</p>';
    } else {
      html += '<p style="margin-bottom:8px;"><strong>Pattern: Dedicated Inference Pool</strong></p>';
      html += '<p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:12px;">Your inference runs on dedicated GPU pools with no multi-tenant contention. WVA optimizes scaling directly without Kueue overhead. Simpler, lower latency. Add Kueue later only if you introduce service-tier boundaries.</p>';
    }

    components.push('<strong>llm-d + WVA</strong> (KV-cache routing + inference-aware autoscaling)');
    components.push('<strong>KServe</strong> (model lifecycle + scale-to-zero)');
    components.push('<strong>DRA</strong> (declarative GPU claims)');

    if (mixed) {
      components.push('<strong>MIG</strong> (critical — carve GPUs for small models, 7-on-1 slicing)');
      html += '<p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:12px;">Your fleet of small models (guard rails, embeddings, classifiers) is the biggest waste target. MIG slicing will deliver the fastest ROI — one A100 replaces up to 7 dedicated GPUs.</p>';
    }

    if (finops) {
      components.push('<strong>GPU Credits + DCGM metering</strong> (showback dashboards)');
      html += '<p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:12px;">Start with showback: let teams see their cost. Normalize GPU types into credits (H100=100, A100=60, MIG=10) so teams get budgets, not GPU counts. Transition to chargeback after 1&ndash;2 quarters of data.</p>';
    }

    if (shared) {
      components.push('<strong>KubeRay</strong> (distributed training orchestration)');
    }

    html += '<p style="font-size:0.85rem;font-weight:600;color:var(--text);margin-top:16px;margin-bottom:8px;">Your component stack:</p>';
    html += '<ul style="font-size:0.82rem;color:var(--text-secondary);padding-left:18px;">';
    components.forEach(function(c) { html += '<li style="margin-bottom:4px;">' + c + '</li>'; });
    html += '</ul>';

    body.innerHTML = html;
    result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}
