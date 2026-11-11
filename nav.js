/* RGBB SKYNET — Shared Navigation Bar
   Include on any page: <script src="nav.js"></script> (root) or <script src="../nav.js"></script> (guides/)
   Pages are grouped into dropdown categories; the current page and its category are highlighted.
   To add a page: put it in the right group below (href is relative to the site root). */
(function() {
  var HOME = { href: 'index.html', label: '← Home', root: true };
  var groups = [
    { label: 'Land Plans', items: [
      { href: 'guides/s3_territory_map.html', label: 'S3 Map' },
      { href: 'guides/s2_territory_map.html', label: 'S2 Map' },
      { href: 'guides/s1_territory_map.html', label: 'S1 Map' },
      { href: 'guides/s1_land_captures.html', label: 'S1 Captures' }
    ]},
    { label: 'Season Guides', items: [
      { href: 'guides/s3_golden_kingdom.html', label: 'S3 Golden Kingdom' },
      { href: 'guides/curse_resistance_s3.html', label: 'S3 Curse Resist' },
      { href: 'guides/s2_polar_storm.html', label: 'S2 Polar Storm' },
      { href: 'guides/virus_resistance_s2.html', label: 'S2 Virus Resist' },
      { href: 'guides/virus_resistance.html', label: 'S1 Virus Resist' },
      { href: 'guides/zombie_boss_chart.html', label: 'Zombie Boss' }
    ]},
    { label: 'Planners', items: [
      { href: 'research_trees_visual.html', label: 'Research Trees', root: true },
      { href: 'guides/building_planner.html', label: 'Building Planner' },
      { href: 'guides/hero_planner.html', label: 'Hero Planner' },
      { href: 'guides/budget_planner.html', label: 'Budget Planner' },
      { href: 'guides/vs_weekly_planner.html', label: 'VS Planner' },
      { href: 'guides/training_optimization.html', label: 'Training' },
      { href: 'guides/ai_advisor.html', label: 'AI Advisor' }
    ]},
    { label: 'Technical Guides', items: [
      { href: 'guides/building_reference.html', label: 'Building Ref' },
      { href: 'guides/chip_lab_guide.html', label: 'Chip Lab' },
      { href: 'guides/drone_guide.html', label: 'Drone' },
      { href: 'guides/radar_guide.html', label: 'Radar' },
      { href: 'guides/waterfall_guide.html', label: 'Waterfall' },
      { href: 'guides/plunder_guide.html', label: 'Plunder' },
      { href: 'guides/profession_hall.html', label: 'Professions' },
      { href: 'guides/interior_test_report.html', label: 'Interior Test' }
    ]},
    { label: 'Alliance & Server', items: [
      { href: 'guides/calendar.html', label: 'Calendar' },
      { href: 'guides/server_dashboard.html', label: 'Server' },
      { href: 'guides/alliance_support_hub.html', label: 'Alliance Hub' },
      { href: 'guides/alliance_tech.html', label: 'Alliance Tech' },
      { href: 'guides/capitol_positions.html', label: 'Capitol Positions' },
      { href: 'guides/wall_of_honor.html', label: 'Wall of Honor' }
    ]}
  ];

  var path = window.location.pathname;
  var inGuides = path.indexOf('/guides/') !== -1;
  var currentFile = path.split('/').pop() || 'index.html';

  function resolve(link) {
    if (!inGuides) return link.href;
    return link.root ? '../' + link.href : link.href.replace('guides/', '');
  }
  function isCurrent(link) { return currentFile === link.href.split('/').pop(); }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }

  // Styles: scoped to #guide-nav so they win over each page's own .guide-nav rules.
  if (!document.getElementById('skynet-nav-style')) {
    var css =
      '#guide-nav{position:relative;z-index:1000;display:flex;flex-wrap:wrap;align-items:center;gap:4px 6px;}' +
      '#guide-nav .nav-home{margin-right:4px;}' +
      '#guide-nav .nav-group{position:relative;}' +
      '#guide-nav .nav-btn{font:inherit;font-size:inherit;color:#5a6a6a;background:transparent;border:1px solid transparent;' +
        'border-radius:3px;padding:2px 8px;cursor:pointer;white-space:nowrap;line-height:1.4;-webkit-tap-highlight-color:transparent;}' +
      '#guide-nav .nav-btn:hover,#guide-nav .nav-group.open>.nav-btn{background:#fff;color:#f4a261;}' +
      '#guide-nav .nav-group.has-current>.nav-btn{color:#f4a261;font-weight:bold;background:#fff;border-color:#f4a261;}' +
      '#guide-nav .nav-btn .nav-caret{font-size:.8em;margin-left:3px;opacity:.7;}' +
      '#guide-nav .nav-menu{display:none;position:absolute;top:calc(100% + 4px);left:0;min-width:190px;max-width:calc(100vw - 24px);' +
        'background:#fff;border:1px solid #7fb3a8;border-radius:6px;box-shadow:0 6px 18px rgba(0,0,0,.15);padding:4px;}' +
      '#guide-nav .nav-group.open>.nav-menu{display:block;}' +
      '#guide-nav .nav-group.align-right>.nav-menu{left:auto;right:0;}' +
      '#guide-nav .nav-menu a{display:block;padding:6px 10px;margin:0;border:0;border-radius:4px;color:#333;' +
        'text-decoration:none;white-space:nowrap;font-size:13px;font-weight:normal;}' +
      '#guide-nav .nav-menu a:hover{background:#f0f5f4;color:#f4a261;}' +
      '#guide-nav .nav-menu a.current{background:#fff4ec;color:#f4a261;font-weight:bold;border:0;}' +
      '@media (max-width:600px){#guide-nav .nav-btn{padding:4px 7px;}' +
        '#guide-nav .nav-menu a{padding:9px 12px;font-size:14px;}}';
    var st = document.createElement('style');
    st.id = 'skynet-nav-style';
    st.textContent = css;
    document.head.appendChild(st);
  }

  var nav = document.getElementById('guide-nav');
  if (!nav) {
    nav = document.createElement('nav');
    nav.className = 'guide-nav';
    nav.id = 'guide-nav';
    document.body.insertBefore(nav, document.body.firstChild);
  }

  var homeCurrent = currentFile === '' || currentFile === 'index.html';
  var html = '<a href="' + resolve(HOME) + '" class="nav-home' + (homeCurrent ? ' current' : '') + '">' + HOME.label + '</a>';
  for (var g = 0; g < groups.length; g++) {
    var grp = groups[g], items = '', has = false;
    for (var i = 0; i < grp.items.length; i++) {
      var link = grp.items[i], cur = isCurrent(link);
      if (cur) has = true;
      items += '<a href="' + resolve(link) + '"' + (cur ? ' class="current" aria-current="page"' : '') + '>' + esc(link.label) + '</a>';
    }
    html += '<div class="nav-group' + (has ? ' has-current' : '') + '">' +
      '<button type="button" class="nav-btn" aria-haspopup="true" aria-expanded="false">' + esc(grp.label) +
      '<span class="nav-caret">▾</span></button>' +
      '<div class="nav-menu" role="menu">' + items + '</div></div>';
  }
  nav.innerHTML = html;

  var groupsEls = nav.querySelectorAll('.nav-group');
  function closeAll(except) {
    for (var k = 0; k < groupsEls.length; k++) {
      if (groupsEls[k] === except) continue;
      groupsEls[k].classList.remove('open');
      groupsEls[k].querySelector('.nav-btn').setAttribute('aria-expanded', 'false');
    }
  }
  function open(el) {
    if (!el.classList.contains('open')) el._openedAt = Date.now();
    closeAll(el);
    el.classList.add('open');
    el.querySelector('.nav-btn').setAttribute('aria-expanded', 'true');
    el.classList.remove('align-right');
    var r = el.querySelector('.nav-menu').getBoundingClientRect();
    if (r.right > window.innerWidth - 8) el.classList.add('align-right');
  }
  var canHover = window.matchMedia && window.matchMedia('(hover: hover)').matches;
  for (var k = 0; k < groupsEls.length; k++) {
    (function(el) {
      el.querySelector('.nav-btn').addEventListener('click', function(e) {
        e.stopPropagation();
        // a click right after hover-open keeps it open (otherwise hover + click would toggle it shut)
        if (el.classList.contains('open') && Date.now() - (el._openedAt || 0) > 500) closeAll(); else open(el);
      });
      if (canHover) {
        var t;
        el.addEventListener('mouseenter', function() { clearTimeout(t); open(el); });
        el.addEventListener('mouseleave', function() { t = setTimeout(function() { el.classList.remove('open'); }, 200); });
      }
    })(groupsEls[k]);
  }
  document.addEventListener('click', function(e) { if (!nav.contains(e.target)) closeAll(); });
  document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeAll(); });
})();
