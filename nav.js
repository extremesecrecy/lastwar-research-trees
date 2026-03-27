/* OWOW SKYNET — Shared Navigation Bar
   Include on any page: <script src="nav.js"></script> (root) or <script src="../nav.js"></script> (guides/)
   Auto-detects current page and highlights it. */
(function() {
  var links = [
    { href: 'index.html', label: '\u2190 Home', root: true },
    { href: 'guides/ai_advisor.html', label: 'AI Advisor' },
    { href: 'guides/alliance_support_hub.html', label: 'Alliance Hub' },
    { href: 'guides/alliance_tech.html', label: 'Alliance Tech' },
    { href: 'guides/building_planner.html', label: 'Building Planner' },
    { href: 'guides/building_reference.html', label: 'Building Ref' },
    { href: 'guides/capitol_positions.html', label: 'Capitol Positions' },
    { href: 'guides/chip_lab_guide.html', label: 'Chip Lab' },
    { href: 'guides/calendar.html', label: 'Calendar' },
    { href: 'guides/drone_guide.html', label: 'Drone' },
    { href: 'guides/hero_planner.html', label: 'Hero Planner' },
    { href: 'guides/plunder_guide.html', label: 'Plunder' },
    { href: 'guides/radar_guide.html', label: 'Radar' },
    { href: 'research_trees_visual.html', label: 'Research Trees', root: true },
    { href: 'guides/server_dashboard.html', label: 'Server' },
    { href: 'guides/vs_weekly_planner.html', label: 'VS Planner' },
    { href: 'guides/interior_test_report.html', label: 'Interior Test' },
    { href: 'guides/training_optimization.html', label: 'Training' },
    { href: 'guides/wall_of_honor.html', label: 'Wall of Honor' },
    { href: 'guides/waterfall_guide.html', label: 'Waterfall' }
  ];

  // Detect if we're in a subdirectory (guides/)
  var path = window.location.pathname;
  var inGuides = path.indexOf('/guides/') !== -1;
  var currentFile = path.split('/').pop() || 'index.html';

  var nav = document.getElementById('guide-nav');
  if (!nav) {
    // Create nav element if not present
    nav = document.createElement('nav');
    nav.className = 'guide-nav';
    nav.id = 'guide-nav';
    document.body.insertBefore(nav, document.body.firstChild);
  }

  var html = '';
  for (var i = 0; i < links.length; i++) {
    var link = links[i];
    var href = link.href;

    // Adjust paths based on current location
    if (inGuides) {
      if (link.root) {
        href = '../' + href;
      } else {
        // Strip 'guides/' prefix — we're already in guides/
        href = href.replace('guides/', '');
      }
    }

    // Determine if this is the current page
    var linkFile = link.href.split('/').pop();
    var isCurrent = (currentFile === linkFile);
    // Special case: index.html or empty path
    if (link.root && link.href === 'index.html' && (currentFile === '' || currentFile === 'index.html')) {
      isCurrent = true;
    }

    var classes = [];
    if (link.root && link.href === 'index.html') classes.push('nav-home');
    if (isCurrent) classes.push('current');

    html += '<a href="' + href + '"' + (classes.length ? ' class="' + classes.join(' ') + '"' : '') + '>' + link.label + '</a>';
  }

  nav.innerHTML = html;
})();
