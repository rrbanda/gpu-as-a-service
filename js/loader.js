(async function () {
  'use strict';

  var config;
  try {
    var resp = await fetch('presentation.json');
    config = await resp.json();
  } catch (e) {
    document.querySelector('main').innerHTML =
      '<p style="color:#ef4444;padding:40px;text-align:center;">Failed to load presentation.json. ' +
      'Make sure you are serving the site over HTTP (e.g. <code>python3 -m http.server</code>).</p>';
    return;
  }

  var nav = document.getElementById('side-nav');
  var main = document.querySelector('main');
  var footer = document.querySelector('footer');
  var sections = config.sections;

  // Build side-nav
  nav.innerHTML = sections.map(function (s, i) {
    var cls = i === 0 ? ' class="active"' : '';
    var label = s.navLabel.replace(/&/g, '&amp;');
    return '<a href="#' + s.id + '" data-label="' + label + '"' + cls + '></a>';
  }).join('\n  ');

  // Fetch all section HTML fragments in parallel
  var fetches = sections.map(function (s) {
    return fetch(s.file).then(function (r) {
      if (!r.ok) throw new Error(s.file + ': ' + r.status);
      return r.text();
    });
  });

  var htmls;
  try {
    htmls = await Promise.all(fetches);
  } catch (e) {
    main.innerHTML = '<p style="color:#ef4444;padding:40px;">Failed to load section: ' + e.message + '</p>';
    return;
  }

  // Assemble sections into <main>
  var mainHTML = '';
  sections.forEach(function (s, i) {
    var isHero = s.id === 'hero';
    var cls = isHero ? 'section visible' : 'section';
    mainHTML += '<section id="' + s.id + '" class="' + cls + '">\n';
    mainHTML += htmls[i];

    // Append navigation link
    if (i < sections.length - 1) {
      var next = sections[i + 1];
      if (isHero) {
        mainHTML += '\n  <a href="#' + next.id + '" class="scroll-indicator" title="Scroll down">&#8595;</a>';
      } else {
        mainHTML += '\n  <a href="#' + next.id + '" class="section-arrow" title="Next: ' +
          next.navLabel.replace(/&/g, '&amp;') + '">&#8595;</a>';
      }
    }
    mainHTML += '\n</section>\n\n';
  });

  main.innerHTML = mainHTML;
  document.body.classList.remove('loading');

  // Populate agenda cards in hero
  var agendaGrid = document.getElementById('agenda-grid');
  if (agendaGrid && config.agenda) {
    agendaGrid.innerHTML = config.agenda.map(function (a) {
      return '<a href="#' + a.target + '" class="agenda-card" style="--card-accent:' + a.accent + ';">' +
        '<span class="agenda-num">' + a.num + '</span>' +
        '<span class="agenda-title">' + a.title + '</span>' +
        '<span class="agenda-desc">' + a.desc + '</span>' +
        '</a>';
    }).join('\n      ');
  }

  // Populate footer
  if (footer && config.footer) {
    footer.innerHTML =
      '<p style="font-size:1.1rem;font-weight:600;color:var(--text);margin-bottom:12px;">' +
      config.footer.title + '</p><p>' + config.footer.text + '</p>';
  }

  // Embed presenter groups config for interactions.js to read
  if (config.presenterGroups) {
    var configScript = document.createElement('script');
    configScript.id = 'presenter-config';
    configScript.type = 'application/json';
    configScript.textContent = JSON.stringify(config.presenterGroups);
    document.body.appendChild(configScript);
  }

  // Initialize interactions after DOM is populated
  var script = document.createElement('script');
  script.src = 'js/interactions.js';
  script.defer = true;
  document.body.appendChild(script);
})();
