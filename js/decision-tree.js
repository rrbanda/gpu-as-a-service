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
}
