(function() {
  'use strict';

  // Progress bar
  var progressBar = document.getElementById('progress-bar');
  function updateProgress() {
    var scrollTop = window.scrollY;
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    var progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    if (progressBar) progressBar.style.width = progress + '%';
  }

  // Section reveal with IntersectionObserver
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

  // Active nav tracking
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

  // GPU utilization bar animation
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

  // MIG slice animation
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

  // Flashcard flip via event delegation
  document.addEventListener('click', function(e) {
    var card = e.target.closest('.flashcard');
    if (card) card.classList.toggle('flipped');
  });

  // Scroll event for progress bar
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();
})();

// ===== PRESENTER MODE =====
(function() {
  var presenterMode = false;
  var revealedIndex = 0;
  var allSections = document.querySelectorAll('.section');

  var editableFields = document.querySelectorAll('.wb-editable');

  // Read presenter groups from config embedded in DOM
  var presenterGroups;
  try {
    presenterGroups = JSON.parse(document.getElementById('presenter-config').textContent);
  } catch (e) {
    presenterGroups = [
      ['challenges', 'layers'],
      ['loops', 'mechanisms'],
      ['governance', 'maas', 'training', 'finops']
    ];
  }

  function enterPresenter() {
    presenterMode = true;
    document.body.classList.add('presenter-mode');
    revealedIndex = 0;
    allSections.forEach(function(s, i) {
      if (i === 0) { s.classList.add('p-revealed'); }
      else { s.classList.remove('p-revealed'); }
    });
    editableFields.forEach(function(el) { el.contentEditable = 'true'; });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function exitPresenter() {
    presenterMode = false;
    document.body.classList.remove('presenter-mode');
    allSections.forEach(function(s) { s.classList.remove('p-revealed'); });
    editableFields.forEach(function(el) { el.contentEditable = 'false'; });
  }

  // Auto-update waste % when fleet size or utilization changes
  editableFields.forEach(function(el) {
    el.addEventListener('input', function() {
      var totalEl = document.querySelector('[data-field="total-gpus"]');
      var utilEl = document.querySelector('[data-field="avg-util"]');
      var idleEl = document.querySelector('[data-field="idle-gpus"]');
      var pctEl = document.getElementById('wb-idle-pct');
      if (!totalEl || !utilEl || !idleEl || !pctEl) return;
      var total = parseInt(totalEl.textContent) || 0;
      var utilText = utilEl.textContent.replace(/[^0-9.]/g, '');
      var util = parseFloat(utilText) || 0;
      var idle = Math.round(total * (1 - util / 100));
      idleEl.textContent = '~' + idle;
      var pct = total > 0 ? Math.round((1 - util / 100) * 100) : 0;
      pctEl.textContent = pct + '% of ' + total + ' fleet';
    });
  });

  var sectionGroupMap = {};
  (function() {
    presenterGroups.forEach(function(group) {
      var leaderIdx = -1;
      for (var i = 0; i < allSections.length; i++) {
        if (allSections[i].id === group[0]) { leaderIdx = i; break; }
      }
      if (leaderIdx < 0) return;
      for (var g = 1; g < group.length; g++) {
        for (var j = 0; j < allSections.length; j++) {
          if (allSections[j].id === group[g]) { sectionGroupMap[j] = leaderIdx; break; }
        }
      }
    });
  })();

  function revealNext() {
    if (revealedIndex < allSections.length - 1) {
      revealedIndex++;
      allSections[revealedIndex].classList.add('p-revealed');
      while (revealedIndex + 1 < allSections.length && sectionGroupMap[revealedIndex + 1] !== undefined) {
        revealedIndex++;
        allSections[revealedIndex].classList.add('p-revealed');
      }
      allSections[revealedIndex].scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function revealPrev() {
    if (revealedIndex > 0) {
      var startIdx = revealedIndex;
      while (startIdx > 0 && sectionGroupMap[startIdx] !== undefined) {
        allSections[startIdx].classList.remove('p-revealed');
        startIdx--;
      }
      allSections[startIdx].classList.remove('p-revealed');
      revealedIndex = startIdx - 1;
      if (revealedIndex < 0) revealedIndex = 0;
      allSections[revealedIndex].scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  document.addEventListener('keydown', function(e) {
    if (e.key === 'p' && !e.ctrlKey && !e.metaKey && e.target.tagName !== 'INPUT' && !e.target.isContentEditable) {
      if (presenterMode) exitPresenter(); else enterPresenter();
    }
    if (!presenterMode) return;
    if (e.target.isContentEditable || e.target.tagName === 'INPUT') return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); revealNext(); }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); revealPrev(); }
  });

  var toggle = document.getElementById('presenter-toggle');
  if (toggle) toggle.addEventListener('click', function() {
    if (presenterMode) exitPresenter(); else enterPresenter();
  });

  // Custom sticky note
  var stickyInput = document.getElementById('wb-sticky-input');
  var stickyAddBtn = document.getElementById('wb-sticky-add');
  var stickyBoard = document.getElementById('wb-sticky-board');

  function addStickyNote(text) {
    if (!stickyBoard) return;
    var note = document.createElement('div');
    note.className = 'wb-sticky-note';
    note.textContent = text;
    stickyBoard.appendChild(note);
  }

  if (stickyAddBtn) stickyAddBtn.addEventListener('click', function() {
    if (stickyInput) {
      var isHidden = stickyInput.style.display === 'none';
      stickyInput.style.display = isHidden ? 'inline-block' : 'none';
      if (isHidden) stickyInput.focus();
    }
  });

  function addCustomSticky() {
    if (!stickyInput || !stickyInput.value.trim()) return;
    addStickyNote(stickyInput.value.trim());
    stickyInput.value = '';
    stickyInput.focus();
  }

  if (stickyInput) stickyInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') { e.preventDefault(); addCustomSticky(); }
  });

  // Inject vote buttons into use case mapping rows
  document.querySelectorAll('.mapping-row:not(.mapping-row-header)').forEach(function(row) {
    var firstCell = row.querySelector('.mapping-cell');
    if (!firstCell) return;
    var btn = document.createElement('button');
    btn.className = 'wb-vote-btn';
    btn.innerHTML = '&#9650; <span class="wb-vote-count">0</span>';
    firstCell.appendChild(btn);
  });

  // Vote button click handlers
  document.querySelectorAll('.wb-vote-btn').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      var countEl = btn.querySelector('.wb-vote-count');
      var count = parseInt(countEl.textContent) + 1;
      countEl.textContent = count;
      btn.classList.add('voted');
      updateVoteSummary();
    });
  });

  function updateVoteSummary() {
    var votes = [];
    document.querySelectorAll('.wb-vote-btn').forEach(function(btn) {
      var count = parseInt(btn.querySelector('.wb-vote-count').textContent);
      var row = btn.closest('.mapping-row');
      var label = row ? row.querySelector('.mapping-cell strong') : null;
      if (count > 0 && label) {
        votes.push({ name: label.textContent, count: count, row: row });
      }
    });
    votes.sort(function(a, b) { return b.count - a.count; });

    document.querySelectorAll('.mapping-row').forEach(function(r) { r.classList.remove('wb-top-voted'); });
    votes.slice(0, 3).forEach(function(v) { v.row.classList.add('wb-top-voted'); });

    var summary = document.getElementById('wb-vote-summary');
    if (!summary) return;
    var list = summary.querySelector('ol');
    if (!list) return;
    list.innerHTML = '';
    if (votes.length === 0) { list.innerHTML = '<li>No votes yet</li>'; return; }
    votes.forEach(function(v) {
      var li = document.createElement('li');
      li.innerHTML = '<strong>' + v.name + '</strong> — ' + v.count + ' vote' + (v.count > 1 ? 's' : '');
      list.appendChild(li);
    });
  }
})();

// ===== DECISION TREE (event delegation) =====
(function() {
  var decisionState = {};

  document.addEventListener('click', function(e) {
    var option = e.target.closest('.decision-option[data-question]');
    if (!option) return;

    var qId = option.getAttribute('data-question');
    var value = option.getAttribute('data-value');
    var parent = option.parentElement;

    parent.querySelectorAll('.decision-option').forEach(function(o) { o.classList.remove('selected'); });
    option.classList.add('selected');
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
        html += '<p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:12px;">Start with showback: let teams see their cost. Normalize GPU types into credits (H100=100, A100=60, MIG=10) so teams get budgets, not GPU counts. Transition to chargeback after 1\u20132 quarters of data.</p>';
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
  });
})();
