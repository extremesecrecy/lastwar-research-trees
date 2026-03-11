#!/usr/bin/env python3
"""
Build the Building Progression Planner HTML page.
Reads building_data_complete.json and generates a self-contained HTML
with embedded CSS, JS, and building data.

Output: guides/building_planner.html
"""
import json
import os


def load_building_data(path):
    """Load the complete building data JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_css():
    return r'''<style>
  @font-face {
    font-family: 'DKCrayonCrumble';
    src: url('DKCrayonCrumble.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --orange: #f4a261;
    --cyan: #5bc0de;
    --yellow: #f4d35e;
    --teal: #7fb3a8;
    --dark: #5a6a6a;
    --text: #333;
    --watermelon: #fc5c65;
    --green: #43a047;
    --red: #e53935;
    --gray: #ccc;
    --light-bg: #fafafa;
  }

  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #fff;
    color: var(--text);
    padding: 8px;
    min-height: 100vh;
  }

  h1, h2, h3, .section-label, .alliance .name {
    font-family: 'DKCrayonCrumble', 'Segoe UI', sans-serif;
  }

  /* Header */
  .top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    flex-wrap: wrap;
    gap: 8px;
  }
  .top-bar h1 {
    font-size: 20px;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--dark);
  }
  .top-bar .sub {
    font-size: 12px;
    color: #888;
  }
  .alliance {
    background: #e8f4f1;
    border: 1px solid var(--teal);
    border-radius: 5px;
    padding: 2px 10px;
    text-align: right;
  }
  .alliance .name {
    font-size: 17px;
    font-weight: 800;
    color: var(--dark);
  }
  .alliance .info {
    font-size: 12px;
    color: #666;
  }

  /* Commander Bar */
  .commander-bar {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
    background: #e8f4f1;
    border: 1.5px solid var(--teal);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 10px;
  }
  .commander-bar label {
    font-size: 13px;
    font-weight: 600;
    color: var(--dark);
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .commander-bar select, .commander-bar input[type="number"] {
    padding: 4px 8px;
    border: 1.5px solid var(--teal);
    border-radius: 5px;
    font-size: 14px;
    background: #fff;
    min-width: 60px;
  }

  /* Power Dashboard */
  .power-dashboard {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    margin-bottom: 10px;
  }
  .power-card {
    border-radius: 8px;
    padding: 10px 12px;
    text-align: center;
  }
  .power-card .label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--dark);
    margin-bottom: 4px;
  }
  .power-card .value {
    font-family: 'DKCrayonCrumble', sans-serif;
    font-size: 22px;
    font-weight: 800;
  }
  .pc-current { background: #e8f4f1; border: 1.5px solid var(--teal); }
  .pc-current .value { color: var(--teal); }
  .pc-target { background: #fef3e2; border: 1.5px solid var(--orange); }
  .pc-target .value { color: var(--orange); }
  .pc-needed { background: #fce4ec; border: 1.5px solid var(--watermelon); }
  .pc-needed .value { color: var(--watermelon); }

  /* Section Labels */
  .section-label {
    font-size: 14px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--dark);
    margin: 10px 0 6px 0;
    padding-bottom: 3px;
    border-bottom: 2px solid var(--teal);
  }

  /* Accordion Categories */
  .category {
    margin-bottom: 6px;
    border: 1.5px solid var(--gray);
    border-radius: 8px;
    overflow: hidden;
  }
  .category.expanded {
    border-color: var(--teal);
  }
  .category-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    background: var(--light-bg);
    cursor: pointer;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
  }
  .category-header:active {
    background: #e8f4f1;
  }
  .category-header .cat-name {
    font-family: 'DKCrayonCrumble', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: var(--dark);
  }
  .category-header .cat-info {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #888;
  }
  .category-header .cat-arrow {
    font-size: 14px;
    transition: transform 0.2s;
  }
  .category.expanded .cat-arrow {
    transform: rotate(90deg);
  }
  .category-body {
    display: none;
    padding: 0 8px 8px;
  }
  .category.expanded .category-body {
    display: block;
  }

  /* Building Rows */
  .building-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 6px;
    border-bottom: 1px solid #eee;
    gap: 8px;
  }
  .building-row:last-child {
    border-bottom: none;
  }
  .building-name {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    flex: 1;
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
  }
  .building-name:hover {
    color: var(--cyan);
  }
  .building-level {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .building-level select {
    padding: 4px 6px;
    border: 1.5px solid var(--gray);
    border-radius: 5px;
    font-size: 14px;
    min-width: 55px;
    background: #fff;
  }
  .status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .status-green { background: var(--green); }
  .status-orange { background: var(--orange); }
  .status-red { background: var(--red); border: 2px dashed var(--red); background: #fce4ec; }
  .status-gray { background: var(--gray); }

  /* Building Detail (expandable) */
  .building-detail {
    display: none;
    padding: 6px 8px;
    background: #f9f9f9;
    border-radius: 5px;
    margin: 4px 0;
    font-size: 12px;
    color: #666;
  }
  .building-detail.show {
    display: block;
  }
  .building-detail .stat-row {
    display: flex;
    justify-content: space-between;
    padding: 2px 0;
  }

  /* Upgrade Path Tabs */
  .tab-bar {
    display: flex;
    gap: 4px;
    margin-bottom: 8px;
  }
  .tab-btn {
    flex: 1;
    padding: 8px 4px;
    border: 1.5px solid var(--gray);
    border-radius: 6px;
    background: #fff;
    font-size: 12px;
    font-weight: 600;
    color: var(--dark);
    cursor: pointer;
    text-align: center;
    transition: all 0.2s;
  }
  .tab-btn.active {
    border-color: var(--watermelon);
    background: var(--watermelon);
    color: #fff;
  }
  .tab-content {
    display: none;
  }
  .tab-content.active {
    display: block;
  }

  /* Upgrade Steps */
  .upgrade-step {
    background: var(--light-bg);
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 6px;
  }
  .upgrade-step.required {
    border-color: var(--orange);
    border-left: 4px solid var(--orange);
  }
  .upgrade-step.hq-upgrade {
    border-color: var(--watermelon);
    border-left: 4px solid var(--watermelon);
  }
  .step-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
  }
  .step-name {
    font-weight: 700;
    font-size: 14px;
    color: var(--dark);
  }
  .step-badge {
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 700;
    text-transform: uppercase;
    white-space: nowrap;
  }
  .badge-req { background: #fef3e2; color: #c47a30; }
  .badge-hq { background: #fce4ec; color: var(--watermelon); }
  .badge-roi { background: #e8f4f1; color: #5a8a7e; }
  .step-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 12px;
    color: #666;
  }
  .step-stats span {
    display: flex;
    align-items: center;
    gap: 3px;
  }

  /* Summary Box */
  .summary-box {
    background: #e8f4f1;
    border: 2px solid var(--teal);
    border-radius: 8px;
    padding: 12px;
    margin-top: 10px;
  }
  .summary-box h4 {
    font-family: 'DKCrayonCrumble', sans-serif;
    color: var(--dark);
    margin-bottom: 6px;
  }
  .summary-row {
    display: flex;
    justify-content: space-between;
    padding: 3px 0;
    font-size: 13px;
  }

  /* Action Bar */
  .action-bar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 12px 0;
  }
  .action-btn {
    flex: 1;
    min-width: 80px;
    padding: 10px 8px;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    text-align: center;
    transition: opacity 0.2s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  .action-btn:active {
    opacity: 0.7;
  }
  .btn-export { background: var(--watermelon); color: #fff; }
  .btn-import { background: var(--orange); color: #fff; }
  .btn-reset { background: var(--gray); color: var(--dark); }
  .btn-ai { background: var(--cyan); color: #fff; }

  /* Hidden file input */
  #csvFileInput { display: none; }

  /* Footer */
  .footer {
    text-align: center;
    padding: 12px 0;
    font-size: 12px;
    color: #888;
    border-top: 1px solid #eee;
    margin-top: 12px;
  }
  .footer .tagline {
    font-family: 'DKCrayonCrumble', sans-serif;
    font-size: 14px;
    color: var(--dark);
  }

  /* Toast notification */
  .toast {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--dark);
    color: #fff;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
  }
  .toast.show {
    opacity: 1;
  }

  /* Speedup Inventory */
  .speedup-section {
    margin-bottom: 10px;
  }
  .speedup-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    background: #e4f3f8;
    border: 1.5px solid var(--cyan);
    border-radius: 8px;
    cursor: pointer;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
    font-size: 13px;
    font-weight: 600;
    color: var(--dark);
  }
  .speedup-toggle:active { opacity: 0.8; }
  .speedup-toggle .arrow {
    font-size: 12px;
    transition: transform 0.2s;
  }
  .speedup-section.expanded .speedup-toggle .arrow {
    transform: rotate(90deg);
  }
  .speedup-toggle .total-hours {
    margin-left: auto;
    font-size: 12px;
    color: var(--cyan);
    font-weight: 700;
  }
  .speedup-body {
    display: none;
    padding: 10px 14px;
    background: #e4f3f8;
    border: 1.5px solid var(--cyan);
    border-top: none;
    border-radius: 0 0 8px 8px;
  }
  .speedup-section.expanded .speedup-body {
    display: block;
  }
  .speedup-section.expanded .speedup-toggle {
    border-radius: 8px 8px 0 0;
  }
  .speedup-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }
  .speedup-field {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }
  .speedup-field label {
    font-size: 11px;
    font-weight: 600;
    color: var(--dark);
    white-space: nowrap;
  }
  .speedup-field input {
    width: 60px;
    padding: 4px 6px;
    border: 1.5px solid var(--cyan);
    border-radius: 5px;
    font-size: 14px;
    text-align: center;
    background: #fff;
  }
  .speedup-field input:focus {
    outline: none;
    border-color: var(--teal);
    box-shadow: 0 0 0 2px rgba(91, 192, 222, 0.2);
  }
  .speedup-summary {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--cyan);
    font-size: 12px;
    color: var(--dark);
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 4px;
  }

  /* Responsive */
  @media (max-width: 480px) {
    body { padding: 4px; }
    .top-bar h1 { font-size: 17px; }
    .power-dashboard { grid-template-columns: 1fr; gap: 6px; }
    .commander-bar { flex-direction: column; gap: 8px; align-items: stretch; }
    .commander-bar label { justify-content: space-between; }
    .tab-btn { font-size: 11px; padding: 8px 2px; }
    .action-bar { flex-direction: column; }
    .action-btn { min-width: 100%; }
    .speedup-grid { grid-template-columns: repeat(2, 1fr); }
  }

  @media (min-width: 481px) and (max-width: 768px) {
    .power-dashboard { grid-template-columns: 1fr 1fr 1fr; }
    .speedup-grid { grid-template-columns: repeat(3, 1fr); }
  }

  @media (min-width: 769px) {
    body { max-width: 800px; margin: 0 auto; padding: 16px; }
    .building-row { padding: 10px 8px; }
  }

  /* Navigation Bar */
  .guide-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 12px;
    align-items: center;
    padding: 6px 16px;
    background: #f0f5f4;
    border-bottom: 2px solid #7fb3a8;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 12px;
    margin: -8px -8px 12px -8px;
    width: 100vw;
    position: relative;
    left: 50%;
    transform: translateX(-50%);
    box-sizing: border-box;
  }
  .guide-nav a {
    color: #5a6a6a;
    text-decoration: none;
    padding: 2px 6px;
    border-radius: 3px;
    white-space: nowrap;
  }
  .guide-nav a:hover {
    color: #f4a261;
    background: #fff;
  }
  .guide-nav a.current {
    color: #f4a261;
    font-weight: bold;
    background: #fff;
    border: 1px solid #f4a261;
  }
  .guide-nav .nav-home {
    font-weight: bold;
    margin-right: 8px;
    padding-right: 12px;
    border-right: 1px solid #7fb3a8;
  }
  @media (max-width: 480px) {
    .guide-nav {
      padding: 4px 10px;
      gap: 3px 8px;
      font-size: 11px;
      margin: -4px -4px 8px -4px;
    }
  }
  @media (min-width: 769px) {
    .guide-nav {
      margin: -16px -16px 12px -16px;
    }
  }

  /* Multi-instance building rows */
  .building-row.instance-locked { opacity: 0.45; background: #f5f5f5; }
  .building-row.instance-locked select { cursor: not-allowed; }
  .lock-note { font-size: 10px; color: #999; margin-left: 4px; }
  .building-row.sub-instance .building-name {
    padding-left: 16px; font-size: 12px; color: #666;
  }
  .building-row.sub-instance .building-name::before {
    content: '\2514  '; color: #ccc;
  }

  /* Info button */
  .info-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--cyan);
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    font-style: italic;
    font-family: Georgia, serif;
    cursor: pointer;
    flex-shrink: 0;
    margin-left: 4px;
    border: none;
    line-height: 1;
    position: relative;
  }
  .info-btn:hover { background: var(--teal); }
  .info-btn:active { transform: scale(0.9); }

  /* Info tooltip popup */
  .info-popup {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: #fff;
    border: 2px solid var(--cyan);
    border-radius: 10px;
    padding: 16px 20px;
    max-width: 340px;
    width: 90vw;
    z-index: 999;
    box-shadow: 0 8px 32px rgba(0,0,0,0.18);
    font-size: 13px;
    color: var(--text);
    line-height: 1.5;
  }
  .info-popup.show { display: block; }
  .info-popup h4 {
    font-family: 'DKCrayonCrumble', sans-serif;
    font-size: 16px;
    color: var(--dark);
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 2px solid var(--cyan);
  }
  .info-popup .info-desc { margin-bottom: 8px; }
  .info-popup .info-meta {
    font-size: 11px;
    color: #888;
    border-top: 1px solid #eee;
    padding-top: 6px;
    margin-top: 6px;
  }
  .info-popup .info-meta span {
    display: block;
    margin-bottom: 2px;
  }
  .info-popup .info-close {
    position: absolute;
    top: 8px;
    right: 12px;
    font-size: 18px;
    cursor: pointer;
    color: #999;
    background: none;
    border: none;
    font-weight: 700;
  }
  .info-popup .info-close:hover { color: var(--watermelon); }
  .info-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.3);
    z-index: 998;
  }
  .info-overlay.show { display: block; }

  /* Research-unlock note */
  .research-note {
    font-size: 10px;
    color: var(--cyan);
    font-style: italic;
    margin-left: 4px;
  }
</style>'''


def generate_js():
    return r'''
/* ========================================
   BUILDING PROGRESSION PLANNER - CORE JS
   ======================================== */

const LS_KEY = 'owow-building-planner';
const buildings = BUILDING_DATA.buildings;
const hqReqs = BUILDING_DATA.hqRequirements;
const categories = BUILDING_DATA.categories;
const displayNames = BUILDING_DATA.buildingDisplayNames;

// State: current levels for each building
let state = {};

// VIP speed bonuses (% construction speed increase)
const VIP_SPEED = {
    0:0, 1:0, 2:0, 3:0, 4:5, 5:10, 6:15, 7:20, 8:25, 9:30,
    10:35, 11:50, 12:55, 13:60, 14:65, 15:70
};

// Speedup types: key -> seconds
const SPEEDUP_TYPES = [
    { key: 'm5',  label: '5 min',  secs: 300 },
    { key: 'm15', label: '15 min', secs: 900 },
    { key: 'm30', label: '30 min', secs: 1800 },
    { key: 'h1',  label: '1 hr',   secs: 3600 },
    { key: 'h3',  label: '3 hr',   secs: 10800 },
    { key: 'h8',  label: '8 hr',   secs: 28800 },
    { key: 'h24', label: '24 hr',  secs: 86400 }
];

// Speedup inventory state
var speedupState = { m5:0, m15:0, m30:0, h1:0, h3:0, h8:0, h24:0 };

/* ---------- MULTI-INSTANCE CONFIG ---------- */
const MULTI_INSTANCE = {};
for (const [bKey, bData] of Object.entries(buildings)) {
    const ul = bData.unlockLevels || [];
    if (ul.length > 1) MULTI_INSTANCE[bKey] = { count: ul.length, unlockHQ: [...ul] };
}
// Overrides for buildings with more instances than cpt-hedge tracks
// Format: { key: { count: N, unlockHQ: [...], researchNote: 'text for research-unlocked instances' } }
const MI_OVERRIDES = {
    'barracks':       { count: 4, unlockHQ: [0, 10, 0, 0], researchNote: 'Barrack Expansion (Development / Special Forces / Siege to Seize research)' },
    'drill ground':   { count: 4, unlockHQ: [1, 16, 21, 0], researchNote: 'Extra Drill Ground (Siege to Seize research, requires HQ 30)' },
    'hospital':       { count: 4, unlockHQ: [2, 13, 0, 0], researchNote: 'Extra Hospitals / Infirmary Expansion (Defense Fort / Development research)' },
    'gold mine':      { count: 5, unlockHQ: [1, 1, 17, 0, 0], researchNote: 'More Gold Mines (Economy research)' },
    'farmland':       { count: 5, unlockHQ: [1, 1, 12, 0, 0], researchNote: 'More Farmlands (Economy research)' },
    'iron mine':      { count: 5, unlockHQ: [0, 0, 12, 0, 0], researchNote: 'More Iron Mines (Economy research)' },
    'smelter':        { count: 5, unlockHQ: [6, 11, 0, 0, 0], researchNote: 'More Smelters (Economy research)' },
    'training base':  { count: 5, unlockHQ: [0, 0, 13, 0, 0], researchNote: 'Economy research' },
    'squad':          { count: 4, unlockHQ: [0, 0, 0, 0], researchNote: 'Linked to Drill Grounds \u2014 each drill ground = one march slot' },
    'recon plane':    { count: 3, unlockHQ: [1, 23, 25], researchNote: '' },
    'material workshop': { count: 5, unlockHQ: [11, 0, 0, 0, 0], researchNote: 'Economy research' }
};
for (const [bKey, override] of Object.entries(MI_OVERRIDES)) {
    MULTI_INSTANCE[bKey] = { count: override.count, unlockHQ: override.unlockHQ.slice(0, override.count) };
    if (override.researchNote) MULTI_INSTANCE[bKey].researchNote = override.researchNote;
}

/* ---------- BUILDING DESCRIPTIONS ---------- */
const BUILDING_INFO = {
    'headquarters': { desc: 'Central building that determines max level for ALL other buildings. Increases power, hero level cap (HQ \u00d7 5 - 1), and unlocks new buildings/features.', instances: '1', unlock: 'Starting building', category: 'Core' },
    'tech center': { desc: 'Research facility for military, development, defense, and special forces upgrades. Higher levels increase research speed. A 2nd Tech Center can be purchased (District 102 + ~$10 pack). A 3rd unlocks via Age of Oil research (Season 2+, free).', instances: '1\u20133', unlock: '1st: HQ 7 | 2nd: District 102 + paid pack | 3rd: HQ 30 + Age of Oil research', category: 'Core' },
    'wall': { desc: 'Reduces damage taken when your base is attacked. Provides defense stats and power. Higher levels = stronger base defense.', instances: '1', unlock: 'Starting building', category: 'Core' },
    'alliance center': { desc: 'Join or create alliances, request construction help, access alliance store, and participate in alliance events. Higher levels increase max helps receivable per task.', instances: '1', unlock: 'HQ 4', category: 'Core' },
    'builders hut': { desc: 'Provides free time reduction on building upgrades. Higher levels automatically shave more seconds off construction timers. Assign survivors here for bonus speed.', instances: '1', unlock: 'HQ 2', category: 'Core' },
    'barracks': { desc: 'Train and upgrade troops. Higher tiers unlock at higher levels: T5 at Lv14, T6 at 17, T7 at 20, T8 at 24, T9 at 27, T10 at 30. Multiple barracks let you train/waterfall simultaneously.', instances: '4', unlock: '1st: Starting | 2nd: HQ 10 | 3rd\u20134th: Barrack Expansion research (Development / Special Forces / Siege to Seize)', category: 'Military' },
    'tank center': { desc: 'Boosts all Tank-type hero stats (HP, ATK, DEF) and Tank march speed. Essential for Tank squad performance.', instances: '1', unlock: 'HQ 6', category: 'Military' },
    'air center': { desc: 'Boosts all Aircraft-type hero stats (HP, ATK, DEF) and Aircraft march speed. Essential for Aircraft squad performance.', instances: '1', unlock: 'HQ 12', category: 'Military' },
    'missile center': { desc: 'Boosts all Missile-type hero stats (HP, ATK, DEF) and Missile march speed. Essential for Missile squad performance.', instances: '1', unlock: 'HQ 11', category: 'Military' },
    'drill ground': { desc: 'Houses troops and increases troop capacity per march. More drill grounds = more marches you can deploy simultaneously. Critical for rallies and gathering.', instances: '4', unlock: '1st: Starting | 2nd: HQ 16 | 3rd: HQ 21 | 4th: Extra Drill Ground (Siege to Seize research, HQ 30+)', category: 'Military' },
    'squad': { desc: 'Parking Lots \u2014 each one represents a deployable march/squad slot. Higher levels increase that squad\'s march speed (+0.5% at Lv1 up to +17.5% at Lv35). Linked 1:1 with Drill Grounds.', instances: '4', unlock: 'Unlocked with each Drill Ground', category: 'Military' },
    'recon plane': { desc: 'Scout other players\' bases. Higher levels increase scout plane flight speed. Plane level cannot exceed Alert Tower level. Up to 35 levels.', instances: '3', unlock: '1st: HQ 1 | 2nd: HQ 23 | 3rd: HQ 25', category: 'Military' },
    'armament institute': { desc: 'Allows research of 4 Armaments to unlock T11 troops. Single-level building that unlocks in late game after Season 4.', instances: '1', unlock: 'HQ 27 + after Season 4 ends', category: 'Military' },
    'training base': { desc: 'Passively generates hero EXP over time (works while offline). Higher levels increase XP output. Note: passive XP does NOT count for Arms Race Hero Advancement points.', instances: '3\u20135', unlock: '1st\u20132nd: Starting | 3rd: HQ 13 | 4th\u20135th: Economy research', category: 'Training & Heroes' },
    'tavern': { desc: 'Recruit heroes and survivors. Higher levels decrease recruitment cooldown time. Check daily for free recruitment and hero fragments in rotation.', instances: '1', unlock: 'Early game', category: 'Training & Heroes' },
    'tactical institute': { desc: 'Passively produces Training Guidebooks for the Overlord (Gorilla). Higher levels increase guidebook output (up to 70/hour at Lv35). Guidebooks used for Joint Attack, Defense Support, and Survival Training paths.', instances: '1', unlock: 'Early game', category: 'Training & Heroes' },
    'hospital': { desc: 'Heals injured troops. Wounded troops go here instead of being permanently lost. Higher levels increase healing capacity. More hospitals = more troops saved in battle.', instances: '2\u20134', unlock: '1st: HQ 2 | 2nd: HQ 13 | 3rd\u20134th: Extra Hospitals / Infirmary Expansion research (Defense Fort / Development)', category: 'Defense' },
    'emergency center': { desc: 'Overflow hospital \u2014 rescues "fainted" troops that would otherwise die permanently when your hospitals are full. Critical for PvP and Enemy Buster day.', instances: '1', unlock: 'HQ 22', category: 'Defense' },
    'alert tower': { desc: 'Early warning and scouting intelligence hub. Defines scout plane levels and what intel is visible when scouting enemies. Higher levels reveal more enemy details (troops, heroes, power).', instances: '1', unlock: 'HQ 10', category: 'Defense' },
    'gold mine': { desc: 'Produces gold for upgrades. Gold is required starting around Lv9+ buildings. Higher levels = more gold/hour. Extra mines unlocked via Economy research.', instances: '3\u20135', unlock: '1st\u20132nd: Starting | 3rd: HQ 17 | 4th\u20135th: More Gold Mines (Economy research)', category: 'Resources' },
    'farmland': { desc: 'Produces food for troop upkeep and building upgrades. Higher levels = more food/hour. Extra farms unlocked via Economy research.', instances: '3\u20135', unlock: '1st\u20132nd: Starting | 3rd: HQ 12 | 4th\u20135th: More Farmlands (Economy research)', category: 'Resources' },
    'iron mine': { desc: 'Produces iron for building and research upgrades. Higher levels = more iron/hour. Extra mines unlocked via Economy research.', instances: '3\u20135', unlock: '1st\u20132nd: Starting | 3rd: HQ 12 | 4th\u20135th: More Iron Mines (Economy research)', category: 'Resources' },
    'smelter': { desc: 'Produces Upgrade Ore, used in the Gear Factory to upgrade hero gear. Higher levels = more ore/hour. Extra smelters unlocked via Economy research.', instances: '2\u20135', unlock: '1st: HQ 6 | 2nd: HQ 11 | 3rd\u20135th: More Smelters (Economy research)', category: 'Resources' },
    'material workshop': { desc: 'Produces Screws \u2014 the base crafting material used in the Gear Factory to create gear components (cannons, shields, chips, radar). Higher levels = more screws/hour. Extra workshops unlocked via Economy research.', instances: '1\u20135', unlock: '1st: HQ 11 | 2nd\u20135th: Economy research', category: 'Resources' },
    'oil well': { desc: 'Produces oil, the primary resource for HQ 31\u201335 upgrades. Oil is THE bottleneck for late-game progression. Build your first one immediately when unlocked!', instances: '5', unlock: 'Season 2+ (Age of Oil) | 2 from research | 3 from HQ 32/33/34', category: 'Resources' },
    'food warehouse': { desc: 'Protects your food from being stolen during enemy raids. Higher levels = more food protected. Upgrade alongside your food production.', instances: '1', unlock: 'Early game', category: 'Resources' },
    'iron warehouse': { desc: 'Protects your iron from being stolen during enemy raids. Higher levels = more iron protected. Upgrade alongside your iron production.', instances: '1', unlock: 'Early game', category: 'Resources' },
    'coin vault': { desc: 'Protects your gold/coins from being stolen during enemy raids. Higher levels = more coins protected. Upgrade alongside your gold production.', instances: '1', unlock: 'Early game', category: 'Resources' },
    'gear factory': { desc: 'Craft hero gear, merge materials (screws into refined modules, super alloys), and dismantle unwanted gear. Hub for all gear management. Higher levels unlock better gear crafting.', instances: '1', unlock: 'HQ 9', category: 'Production & Drones' },
    'chip lab': { desc: 'Craft drone skill chips for your drone\'s Chip Lab slots. Higher levels unlock legendary (UR) chip crafting. Key chips: Memory Ultra Fission, Gravitational Resonance Armor, Lethal Firestorm.', instances: '1', unlock: 'HQ 5', category: 'Production & Drones' },
    'component factory': { desc: 'Produces Level 1 Drone Component Chests for upgrading drone equipment (Radar, Engine, Armor, Missile, Fuel Cell, Thermal Imager). Higher levels = faster production.', instances: '1', unlock: 'HQ 15', category: 'Production & Drones' },
    'drone parts workshop': { desc: 'Passively produces Drone Parts (up to ~6/day). Drone Parts are used every 5 levels for drone upgrades. Late-game building unlocked through Age of Oil.', instances: '1', unlock: 'HQ 30 + Age of Oil (Season 2+) + Base Expansion research', category: 'Production & Drones' }
};

/* ---------- MULTI-INSTANCE HELPERS ---------- */
function getBaseKey(instanceKey) {
    var m = instanceKey.match(/^(.+)_(\d+)$/);
    return m ? m[1] : instanceKey;
}

function getInstanceNum(instanceKey) {
    var m = instanceKey.match(/_(\d+)$/);
    return m ? parseInt(m[1]) : 1;
}

function getAllInstanceKeys(buildingKey) {
    var keys = [buildingKey];
    if (MULTI_INSTANCE[buildingKey]) {
        for (var i = 2; i <= MULTI_INSTANCE[buildingKey].count; i++)
            keys.push(buildingKey + '_' + i);
    }
    return keys;
}

function getMaxInstanceLevel(buildingKey) {
    var maxLvl = state[buildingKey] || 0;
    if (MULTI_INSTANCE[buildingKey]) {
        for (var i = 2; i <= MULTI_INSTANCE[buildingKey].count; i++) {
            var lvl = state[buildingKey + '_' + i] || 0;
            if (lvl > maxLvl) maxLvl = lvl;
        }
    }
    return maxLvl;
}

function isInstanceUnlocked(buildingKey, instanceNum) {
    var mi = MULTI_INSTANCE[buildingKey];
    if (!mi) return instanceNum === 1;
    if (instanceNum < 1 || instanceNum > mi.count) return false;
    var reqHQ = mi.unlockHQ[instanceNum - 1];
    // reqHQ = 0 means research-unlocked (always available to set level, but shown as research-note)
    if (reqHQ === 0) return true;
    return (state['headquarters'] || 0) >= reqHQ;
}

function getInstanceDisplayName(buildingKey, instanceNum) {
    var dName = displayNames[buildingKey] || buildingKey;
    if (MULTI_INSTANCE[buildingKey]) return dName + ' #' + instanceNum;
    return dName;
}

/* ---------- INIT ---------- */
function init() {
    // Init state with 0 for all buildings (including multi-instance)
    for (const bName of Object.keys(buildings)) {
        state[bName] = 0;
        if (MULTI_INSTANCE[bName]) {
            for (var i = 2; i <= MULTI_INSTANCE[bName].count; i++)
                state[bName + '_' + i] = 0;
        }
    }

    // Load from localStorage
    loadProgress();

    // Build UI
    populateHQDropdowns();
    populateVIPDropdown();
    renderBuildingTracker();
    setupTabs();
    loadSpeedupUI();

    // Initial calculations
    recalcAll();
}

/* ---------- LOCALSTORAGE ---------- */
function saveProgress() {
    try {
        const data = {
            levels: state,
            currentHQ: parseInt(document.getElementById('currentHQ').value) || 1,
            targetHQ: parseInt(document.getElementById('targetHQ').value) || 2,
            builders: parseInt(document.getElementById('builderCount').value) || 3,
            vip: parseInt(document.getElementById('vipLevel').value) || 0,
            speedups: speedupState
        };
        localStorage.setItem(LS_KEY, JSON.stringify(data));
    } catch(e) { /* quota exceeded */ }
}

function loadProgress() {
    try {
        const raw = localStorage.getItem(LS_KEY);
        if (!raw) return;
        const data = JSON.parse(raw);
        if (data.levels) {
            for (const [b, lvl] of Object.entries(data.levels)) {
                if (b in state) {
                    var base = getBaseKey(b);
                    const maxLvl = buildings[base] ? buildings[base].levels.length : 0;
                    state[b] = Math.max(0, Math.min(maxLvl, lvl));
                }
            }
        }
        if (data.speedups) {
            for (var k in data.speedups) {
                if (k in speedupState) speedupState[k] = parseInt(data.speedups[k]) || 0;
            }
        }
        if (data.currentHQ) {
            setTimeout(() => {
                const cur = document.getElementById('currentHQ');
                const tgt = document.getElementById('targetHQ');
                const bld = document.getElementById('builderCount');
                const vip = document.getElementById('vipLevel');
                if (cur) cur.value = data.currentHQ;
                if (tgt) tgt.value = data.targetHQ || data.currentHQ + 1;
                if (bld) bld.value = data.builders || 3;
                if (vip) vip.value = data.vip || 0;
                // Sync HQ building row with Current HQ dropdown
                state['headquarters'] = parseInt(data.currentHQ) || 0;
                var hqSelect = document.querySelector('[data-building="headquarters"] select');
                if (hqSelect) hqSelect.value = state['headquarters'];
                loadSpeedupUI();
                recalcAll();
            }, 0);
        }
    } catch(e) { /* parse error */ }
}

/* ---------- DROPDOWNS ---------- */
function populateHQDropdowns() {
    const cur = document.getElementById('currentHQ');
    const tgt = document.getElementById('targetHQ');
    for (let i = 1; i <= 35; i++) {
        cur.innerHTML += '<option value="' + i + '">' + i + '</option>';
        tgt.innerHTML += '<option value="' + i + '">' + i + '</option>';
    }
    cur.value = 24;
    state['headquarters'] = 24;
    tgt.value = 25;
    cur.onchange = function() {
        // Sync HQ building row to match Current HQ dropdown
        var hqLvl = parseInt(this.value) || 0;
        state['headquarters'] = hqLvl;
        var hqSelect = document.querySelector('[data-building="headquarters"] select');
        if (hqSelect) hqSelect.value = hqLvl;
        updateInstanceLocks();
        recalcAll(); saveProgress();
    };
    tgt.onchange = function() { recalcAll(); saveProgress(); };
    document.getElementById('builderCount').onchange = function() { recalcAll(); saveProgress(); };
}

function populateVIPDropdown() {
    const sel = document.getElementById('vipLevel');
    for (let i = 0; i <= 15; i++) {
        const bonus = VIP_SPEED[i] ? ' (+' + VIP_SPEED[i] + '%)' : '';
        sel.innerHTML += '<option value="' + i + '">VIP ' + i + bonus + '</option>';
    }
    sel.value = 0;
    sel.onchange = function() { recalcAll(); saveProgress(); };
}

/* ---------- BUILDING TRACKER ---------- */
function renderBuildingTracker() {
    const container = document.getElementById('buildingTracker');
    container.innerHTML = '';

    for (const [catName, buildingList] of Object.entries(categories)) {
        const catDiv = document.createElement('div');
        catDiv.className = 'category';
        catDiv.dataset.category = catName;

        const catId = catName.replace(/[^a-zA-Z0-9]/g, '');
        const reqCount = countMetRequirements(buildingList);

        let bodyHtml = '';
        for (const b of buildingList) {
            bodyHtml += renderBuildingRow(b, 1);
            if (MULTI_INSTANCE[b]) {
                for (var mi = 2; mi <= MULTI_INSTANCE[b].count; mi++)
                    bodyHtml += renderBuildingRow(b, mi);
            }
        }

        catDiv.innerHTML =
            '<div class="category-header" onclick="toggleCategory(this)">' +
                '<span class="cat-name">' + catName + '</span>' +
                '<span class="cat-info">' +
                    '<span class="cat-progress" id="cat-prog-' + catId + '">' + reqCount.met + '/' + reqCount.total + '</span>' +
                    '<span class="cat-arrow">&#9654;</span>' +
                '</span>' +
            '</div>' +
            '<div class="category-body">' + bodyHtml + '</div>';

        container.appendChild(catDiv);
    }
}

function renderBuildingRow(buildingKey, instanceNum) {
    instanceNum = instanceNum || 1;
    const bData = buildings[buildingKey];
    if (!bData) return '';
    const maxLevel = bData.levels.length;
    const instanceKey = instanceNum === 1 ? buildingKey : buildingKey + '_' + instanceNum;
    const isMulti = !!MULTI_INSTANCE[buildingKey];
    const dName = isMulti ? getInstanceDisplayName(buildingKey, instanceNum) : (displayNames[buildingKey] || buildingKey);
    const currentLevel = state[instanceKey] || 0;
    const safeKey = instanceKey.replace(/\s/g, '-');
    const locked = isMulti && !isInstanceUnlocked(buildingKey, instanceNum);
    const lockHQ = isMulti ? MULTI_INSTANCE[buildingKey].unlockHQ[instanceNum - 1] : 0;

    let options = '<option value="0">--</option>';
    for (let i = 1; i <= maxLevel; i++) {
        const sel = i === currentLevel ? ' selected' : '';
        options += '<option value="' + i + '"' + sel + '>' + i + '</option>';
    }

    var lockNote = '';
    if (locked) {
        if (lockHQ > 0) {
            lockNote = '<span class="lock-note">(HQ ' + lockHQ + ')</span>';
        } else {
            var mi = MULTI_INSTANCE[buildingKey];
            var rn = mi && mi.researchNote ? mi.researchNote : 'Research required';
            lockNote = '<span class="research-note">(' + rn + ')</span>';
        }
    }
    var disabledAttr = locked ? ' disabled' : '';
    var rowClass = 'building-row' + (locked ? ' instance-locked' : '') + (isMulti && instanceNum > 1 ? ' sub-instance' : '');

    // Info button only on primary instance (not sub-instances)
    var infoBtn = '';
    if (instanceNum === 1 && BUILDING_INFO[buildingKey]) {
        infoBtn = '<button class="info-btn" onclick="event.stopPropagation();showBuildingInfo(\'' + buildingKey + '\')" title="Building info">i</button>';
    }

    return '<div class="' + rowClass + '" data-building="' + instanceKey + '">' +
        '<span class="building-name" onclick="toggleBuildingDetail(\'' + instanceKey + '\')">' + dName + lockNote + '</span>' +
        infoBtn +
        '<div class="building-level">' +
            '<select onchange="setBuildingLevel(\'' + instanceKey + '\', parseInt(this.value))"' + disabledAttr + '>' + options + '</select>' +
            '<div class="status-dot status-gray" id="status-' + safeKey + '"></div>' +
        '</div>' +
    '</div>' +
    '<div class="building-detail" id="detail-' + safeKey + '"></div>';
}

function setBuildingLevel(instanceKey, level) {
    state[instanceKey] = level;
    var baseKey = getBaseKey(instanceKey);
    // If HQ building changed, sync the Current HQ dropdown and update instance locks
    if (baseKey === 'headquarters') {
        var curHQ = document.getElementById('currentHQ');
        if (curHQ) curHQ.value = level;
        updateInstanceLocks();
    }
    recalcAll();
    saveProgress();
}

function updateInstanceLocks() {
    for (var bKey in MULTI_INSTANCE) {
        var mi = MULTI_INSTANCE[bKey];
        for (var i = 1; i <= mi.count; i++) {
            var iKey = i === 1 ? bKey : bKey + '_' + i;
            var safeKey = iKey.replace(/\s/g, '-');
            var row = document.querySelector('[data-building="' + iKey + '"]');
            if (!row) continue;
            var sel = row.querySelector('select');
            var unlocked = isInstanceUnlocked(bKey, i);
            if (unlocked) {
                row.classList.remove('instance-locked');
                if (sel) sel.disabled = false;
                var lockNote = row.querySelector('.lock-note');
                if (lockNote) lockNote.style.display = 'none';
            } else {
                row.classList.add('instance-locked');
                if (sel) sel.disabled = true;
                var lockNote2 = row.querySelector('.lock-note');
                if (lockNote2) lockNote2.style.display = '';
            }
        }
    }
}

function toggleCategory(header) {
    header.parentElement.classList.toggle('expanded');
}

function toggleBuildingDetail(instanceKey) {
    var safeKey = instanceKey.replace(/\s/g, '-');
    var el = document.getElementById('detail-' + safeKey);
    if (!el) return;

    if (el.classList.contains('show')) {
        el.classList.remove('show');
        return;
    }

    var baseKey = getBaseKey(instanceKey);
    var bData = buildings[baseKey];
    var currentLevel = state[instanceKey] || 0;

    if (currentLevel >= bData.levels.length) {
        el.innerHTML = '<div style="padding:4px;color:var(--green);font-weight:700;">MAXED!</div>';
    } else {
        var nextLvl = bData.levels[currentLevel];
        var power = nextLvl.power || '?';
        var food = fN(nextLvl.rss ? nextLvl.rss.food || 0 : 0);
        var iron = fN(nextLvl.rss ? nextLvl.rss.iron || 0 : 0);
        var gold = fN(nextLvl.rss ? nextLvl.rss.gold || 0 : 0);
        var time = nextLvl.time || '?';

        el.innerHTML =
            '<div style="font-weight:700;margin-bottom:4px;color:var(--dark);">Next: Level ' + (currentLevel + 1) + '</div>' +
            '<div class="stat-row"><span>Food:</span><span>' + food + '</span></div>' +
            '<div class="stat-row"><span>Iron:</span><span>' + iron + '</span></div>' +
            '<div class="stat-row"><span>Gold:</span><span>' + gold + '</span></div>' +
            '<div class="stat-row"><span>Time:</span><span>' + time + '</span></div>' +
            '<div class="stat-row"><span>Power:</span><span>+' + fN(power) + '</span></div>';
    }

    el.classList.add('show');
}

/* ---------- CALCULATIONS ---------- */
function recalcAll() {
    updateStatusDots();
    updatePowerDashboard();
    updateCategoryProgress();
    computeCheapestPath();
    computeFastestPath();
    computePowerROI();
}

function getRequirementsForHQ(targetHQ) {
    if (!hqReqs || targetHQ < 1 || targetHQ > hqReqs.length) return [];
    var entry = hqReqs[targetHQ - 1];
    return entry ? (entry.requirements || []) : [];
}

function getBuildingPower(instanceKey, level) {
    var base = getBaseKey(instanceKey);
    var bData = buildings[base];
    if (!bData || level <= 0) return 0;
    var idx = Math.min(level, bData.levels.length) - 1;
    return bData.levels[idx].power || 0;
}

function getCostForRange(instanceKey, fromLevel, toLevel) {
    var base = getBaseKey(instanceKey);
    var bData = buildings[base];
    if (!bData) return { food: 0, iron: 0, gold: 0, time: 0, power: 0 };

    var food = 0, iron = 0, gold = 0, totalSeconds = 0;

    for (var i = fromLevel; i < Math.min(toLevel, bData.levels.length); i++) {
        var lvl = bData.levels[i];
        food += lvl.rss ? lvl.rss.food || 0 : 0;
        iron += lvl.rss ? lvl.rss.iron || 0 : 0;
        gold += lvl.rss ? lvl.rss.gold || 0 : 0;
        totalSeconds += parseTime(lvl.time);
    }

    // Power values are cumulative totals, so power gained = end - start
    var endIdx = Math.min(toLevel, bData.levels.length) - 1;
    var startPower = fromLevel > 0 ? (bData.levels[fromLevel - 1].power || 0) : 0;
    var endPower = endIdx >= 0 ? (bData.levels[endIdx].power || 0) : 0;
    var power = endPower - startPower;

    return { food: food, iron: iron, gold: gold, time: totalSeconds, power: power };
}

function parseTime(timeStr) {
    if (!timeStr || timeStr === '?') return 0;
    var days = 0, hours = 0, mins = 0, secs = 0;
    var dayMatch = timeStr.match(/(\d+)d\s*/);
    if (dayMatch) {
        days = parseInt(dayMatch[1]);
        timeStr = timeStr.replace(dayMatch[0], '');
    }
    var parts = timeStr.split(':').map(Number);
    if (parts.length === 3) { hours = parts[0]; mins = parts[1]; secs = parts[2]; }
    else if (parts.length === 2) { mins = parts[0]; secs = parts[1]; }
    return days * 86400 + hours * 3600 + mins * 60 + secs;
}

function formatTime(seconds) {
    if (seconds <= 0) return '0s';
    var d = Math.floor(seconds / 86400);
    var h = Math.floor((seconds % 86400) / 3600);
    var m = Math.floor((seconds % 3600) / 60);
    if (d > 0) return d + 'd ' + h + 'h';
    if (h > 0) return h + 'h ' + m + 'm';
    return m + 'm';
}

function updatePowerDashboard() {
    var currentPower = 0;
    for (var b in state) {
        currentPower += getBuildingPower(b, state[b]);
    }

    var targetHQ = parseInt(document.getElementById('targetHQ').value) || 1;
    var currentHQ = parseInt(document.getElementById('currentHQ').value) || 1;
    var targetPower = currentPower;
    var reqs = getRequirementsForHQ(targetHQ);

    for (var r = 0; r < reqs.length; r++) {
        var req = reqs[r];
        var bKey = normalizeBuildingName(req.building);
        if (bKey && getMaxInstanceLevel(bKey) < req.level) {
            var bestLvl = getMaxInstanceLevel(bKey);
            var extraCost = getCostForRange(bKey, bestLvl, req.level);
            targetPower += extraCost.power;
        }
    }
    if (currentHQ < targetHQ) {
        var hqCost = getCostForRange('headquarters', currentHQ, targetHQ);
        targetPower += hqCost.power;
    }

    document.getElementById('currentPower').textContent = fN(currentPower);
    document.getElementById('targetPower').textContent = fN(targetPower);
    document.getElementById('neededPower').textContent = '+' + fN(targetPower - currentPower);
}

function updateStatusDots() {
    var targetHQ = parseInt(document.getElementById('targetHQ').value) || 1;
    var reqs = getRequirementsForHQ(targetHQ);

    var reqMap = {};
    for (var r = 0; r < reqs.length; r++) {
        var bKey = normalizeBuildingName(reqs[r].building);
        if (bKey) reqMap[bKey] = reqs[r].level;
    }

    // Iterate over all state keys (includes instance keys like barracks_2)
    for (var iKey in state) {
        var safeKey = iKey.replace(/\s/g, '-');
        var dot = document.getElementById('status-' + safeKey);
        if (!dot) continue;

        var baseKey = getBaseKey(iKey);
        var instNum = getInstanceNum(iKey);
        var currentLvl = state[iKey] || 0;
        var requiredLvl = reqMap[baseKey] || 0;
        var anyMet = getMaxInstanceLevel(baseKey) >= requiredLvl;

        dot.className = 'status-dot';

        // Locked instances: show lock message instead of requirement
        var mi = MULTI_INSTANCE[baseKey];
        if (mi && mi.unlockHQ[instNum - 1] > (state['headquarters'] || 0)) {
            dot.classList.add('status-gray');
            dot.title = 'Locked until HQ ' + mi.unlockHQ[instNum - 1];
            continue;
        }

        if (requiredLvl > 0) {
            if (currentLvl >= requiredLvl) {
                dot.classList.add('status-green');
                dot.title = 'Meets HQ ' + targetHQ + ' requirement (needs Lv.' + requiredLvl + ')';
            } else if (anyMet) {
                // Another instance meets it — show gray-green
                dot.classList.add('status-gray');
                dot.title = 'Another instance meets Lv.' + requiredLvl + ' for HQ ' + targetHQ;
            } else if (currentLvl > 0) {
                dot.classList.add('status-orange');
                dot.title = 'Needs Lv.' + requiredLvl + ' for HQ ' + targetHQ + ' (currently Lv.' + currentLvl + ')';
            } else {
                dot.classList.add('status-red');
                dot.title = 'Needs Lv.' + requiredLvl + ' for HQ ' + targetHQ + ' (not started!)';
            }
        } else {
            dot.classList.add('status-gray');
            dot.title = 'Not required for target HQ';
        }
    }
}

function updateCategoryProgress() {
    for (var catName in categories) {
        var prog = countMetRequirements(categories[catName]);
        var id = 'cat-prog-' + catName.replace(/[^a-zA-Z0-9]/g, '');
        var el = document.getElementById(id);
        if (el) el.textContent = prog.met + '/' + prog.total;
    }
}

function countMetRequirements(buildingList) {
    var tgtEl = document.getElementById('targetHQ');
    var targetHQ = tgtEl ? parseInt(tgtEl.value) || 1 : 1;
    var reqs = getRequirementsForHQ(targetHQ);
    var reqMap = {};
    for (var r = 0; r < reqs.length; r++) {
        var bKey = normalizeBuildingName(reqs[r].building);
        if (bKey) reqMap[bKey] = reqs[r].level;
    }

    var met = 0, total = 0;
    for (var i = 0; i < buildingList.length; i++) {
        var b = buildingList[i];
        if (reqMap[b]) {
            total++;
            if (getMaxInstanceLevel(b) >= reqMap[b]) met++;
        }
    }
    return { met: met, total: total };
}

function normalizeBuildingName(name) {
    var nameMap = {
        'Tech Center': 'tech center',
        'Alliance Center': 'alliance center',
        'Wall': 'wall',
        'Barracks': 'barracks',
        'Tank Center': 'tank center',
        'Air Center': 'air center',
        'Aircraft Center': 'air center',
        'Missile Center': 'missile center',
        'Hospital': 'hospital',
        'Drill Ground': 'drill ground',
        'Parking Lots': 'squad'
    };
    if (name in nameMap) return nameMap[name];
    var lower = name.toLowerCase();
    if (lower in buildings) return lower;
    // Handle OR requirements
    if (name.indexOf(' or ') !== -1) return null;
    return null;
}

/* ---------- CHEAPEST PATH ---------- */
function pickBestInstance(bKey, reqLevel, upgradedTo) {
    // Pick the instance with the highest current level (cheapest to upgrade to reqLevel)
    // Skip instances that are locked (HQ too low to unlock them)
    var allKeys = getAllInstanceKeys(bKey);
    var bestKey = null, bestLvl = -1;
    var effectiveHQ = Math.max(state['headquarters'] || 0, upgradedTo['headquarters'] || 0);
    var mi = MULTI_INSTANCE[bKey];
    for (var i = 0; i < allKeys.length; i++) {
        var iKey = allKeys[i];
        var instNum = getInstanceNum(iKey);
        // Skip locked instances that won't be unlocked by the planned HQ level
        if (mi && mi.unlockHQ[instNum - 1] > effectiveHQ) continue;
        var lvl = Math.max(state[iKey] || 0, upgradedTo[iKey] || 0);
        if (lvl >= reqLevel) return null; // already met by this instance
        if (lvl > bestLvl) { bestLvl = lvl; bestKey = iKey; }
    }
    return bestKey;
}

function computeCheapestPath() {
    var container = document.getElementById('tab-cheapest');
    var currentHQ = parseInt(document.getElementById('currentHQ').value) || 1;
    var targetHQ = parseInt(document.getElementById('targetHQ').value) || 1;

    if (targetHQ <= currentHQ) {
        container.innerHTML = '<div style="padding:20px;text-align:center;color:#888;">Target HQ must be higher than current HQ.</div>';
        return;
    }

    var steps = [];
    var upgradedTo = {};

    for (var hq = currentHQ + 1; hq <= targetHQ; hq++) {
        var reqs = getRequirementsForHQ(hq);

        for (var r = 0; r < reqs.length; r++) {
            var req = reqs[r];
            var bKey = normalizeBuildingName(req.building);

            if (!bKey && req.building.indexOf(' or ') !== -1) {
                var orStep = handleOrRequirement(req, upgradedTo, hq);
                if (orStep) {
                    upgradedTo[orStep.buildingKey] = Math.max(upgradedTo[orStep.buildingKey] || 0, orStep.toLevel);
                    steps.push(orStep);
                }
                continue;
            }

            if (!bKey) continue;

            // Check if ANY instance already meets the requirement
            var anyMet = false;
            var allKeys = getAllInstanceKeys(bKey);
            for (var ai = 0; ai < allKeys.length; ai++) {
                if (Math.max(state[allKeys[ai]] || 0, upgradedTo[allKeys[ai]] || 0) >= req.level) { anyMet = true; break; }
            }
            if (anyMet) continue;

            // Pick the best instance to upgrade
            var bestIKey = pickBestInstance(bKey, req.level, upgradedTo);
            if (!bestIKey) continue;

            var currentLvl = Math.max(state[bestIKey] || 0, upgradedTo[bestIKey] || 0);
            var cost = getCostForRange(bestIKey, currentLvl, req.level);
            var instNum = getInstanceNum(bestIKey);
            var stepName = MULTI_INSTANCE[bKey] ? getInstanceDisplayName(bKey, instNum) : (displayNames[bKey] || bKey);

            steps.push({
                buildingKey: bestIKey,
                name: stepName,
                fromLevel: currentLvl,
                toLevel: req.level,
                forHQ: hq,
                cost: cost,
                type: 'req'
            });
            upgradedTo[bestIKey] = req.level;
        }

        var hqFrom = Math.max(currentHQ, upgradedTo['headquarters'] || hq - 1);
        if (hqFrom < hq) {
            var hqCost = getCostForRange('headquarters', hqFrom, hq);
            steps.push({
                buildingKey: 'headquarters',
                name: 'Headquarters',
                fromLevel: hqFrom,
                toLevel: hq,
                forHQ: hq,
                cost: hqCost,
                type: 'hq'
            });
            upgradedTo['headquarters'] = hq;
        }
    }

    steps.sort(function(a, b) {
        var costA = a.cost.food + a.cost.iron + a.cost.gold;
        var costB = b.cost.food + b.cost.iron + b.cost.gold;
        return costA - costB;
    });

    renderSteps(container, steps, 'cheapest');
}

function handleOrRequirement(req, upgradedTo, forHQ) {
    var parts = req.building.split(' or ').map(function(s) { return s.trim(); });
    var bestOption = null;
    var bestCost = Infinity;

    for (var i = 0; i < parts.length; i++) {
        var part = parts[i];
        if (part.indexOf('Center') === -1 && parts[parts.length - 1].indexOf('Center') !== -1) {
            part = part + ' Center';
        }
        var bKey = normalizeBuildingName(part);
        if (!bKey) continue;

        // Check all instances of this building
        var allKeys = getAllInstanceKeys(bKey);
        for (var ai = 0; ai < allKeys.length; ai++) {
            var iKey = allKeys[ai];
            var currentLvl = Math.max(state[iKey] || 0, upgradedTo[iKey] || 0);
            if (currentLvl >= req.level) return null; // already met
        }

        // Pick best instance for this OR option
        var bestIKey = pickBestInstance(bKey, req.level, upgradedTo);
        if (!bestIKey) continue;

        var currentLvl2 = Math.max(state[bestIKey] || 0, upgradedTo[bestIKey] || 0);
        var cost = getCostForRange(bestIKey, currentLvl2, req.level);
        var totalCost = cost.food + cost.iron + cost.gold;
        var instNum = getInstanceNum(bestIKey);
        var stepName = MULTI_INSTANCE[bKey] ? getInstanceDisplayName(bKey, instNum) : (displayNames[bKey] || bKey);

        if (totalCost < bestCost) {
            bestCost = totalCost;
            bestOption = {
                buildingKey: bestIKey,
                name: stepName,
                fromLevel: currentLvl2,
                toLevel: req.level,
                forHQ: forHQ,
                cost: cost,
                type: 'req',
                isChoice: true,
                choices: parts
            };
        }
    }

    return bestOption;
}

/* ---------- FASTEST PATH ---------- */
function computeFastestPath() {
    var container = document.getElementById('tab-fastest');
    var currentHQ = parseInt(document.getElementById('currentHQ').value) || 1;
    var targetHQ = parseInt(document.getElementById('targetHQ').value) || 1;
    var builderCount = parseInt(document.getElementById('builderCount').value) || 3;
    var vipLvl = parseInt(document.getElementById('vipLevel').value) || 0;
    var speedBonus = VIP_SPEED[vipLvl] || 0;

    if (targetHQ <= currentHQ) {
        container.innerHTML = '<div style="padding:20px;text-align:center;color:#888;">Target HQ must be higher than current HQ.</div>';
        return;
    }

    var allSteps = [];
    var upgradedTo = {};
    var totalParallelTime = 0;

    for (var hq = currentHQ + 1; hq <= targetHQ; hq++) {
        var reqs = getRequirementsForHQ(hq);
        var prereqSteps = [];

        for (var r = 0; r < reqs.length; r++) {
            var req = reqs[r];
            var bKey = normalizeBuildingName(req.building);

            if (!bKey && req.building.indexOf(' or ') !== -1) {
                var orStep = handleOrRequirement(req, upgradedTo, hq);
                if (orStep) {
                    upgradedTo[orStep.buildingKey] = Math.max(upgradedTo[orStep.buildingKey] || 0, orStep.toLevel);
                    if (speedBonus > 0) orStep.cost.time = Math.floor(orStep.cost.time / (1 + speedBonus / 100));
                    prereqSteps.push(orStep);
                }
                continue;
            }

            if (!bKey) continue;

            // Check if ANY instance already meets this
            var anyMet = false;
            var allKeys = getAllInstanceKeys(bKey);
            for (var ai = 0; ai < allKeys.length; ai++) {
                if (Math.max(state[allKeys[ai]] || 0, upgradedTo[allKeys[ai]] || 0) >= req.level) { anyMet = true; break; }
            }
            if (anyMet) continue;

            var bestIKey = pickBestInstance(bKey, req.level, upgradedTo);
            if (!bestIKey) continue;

            var currentLvl = Math.max(state[bestIKey] || 0, upgradedTo[bestIKey] || 0);
            var cost = getCostForRange(bestIKey, currentLvl, req.level);
            if (speedBonus > 0) cost.time = Math.floor(cost.time / (1 + speedBonus / 100));

            var instNum = getInstanceNum(bestIKey);
            var stepName = MULTI_INSTANCE[bKey] ? getInstanceDisplayName(bKey, instNum) : (displayNames[bKey] || bKey);

            prereqSteps.push({
                buildingKey: bestIKey,
                name: stepName,
                fromLevel: currentLvl,
                toLevel: req.level,
                forHQ: hq,
                cost: cost,
                type: 'req',
                parallel: true
            });
            upgradedTo[bestIKey] = req.level;
        }

        prereqSteps.sort(function(a, b) { return b.cost.time - a.cost.time; });

        // Simulate parallel execution
        var parallelTime = 0;
        if (prereqSteps.length > 0) {
            if (prereqSteps.length <= builderCount) {
                parallelTime = Math.max.apply(null, prereqSteps.map(function(s) { return s.cost.time; }));
            } else {
                var builderFinishTimes = [];
                for (var bi = 0; bi < builderCount; bi++) builderFinishTimes.push(0);
                for (var si = 0; si < prereqSteps.length; si++) {
                    var earliest = Math.min.apply(null, builderFinishTimes);
                    var idx = builderFinishTimes.indexOf(earliest);
                    builderFinishTimes[idx] += prereqSteps[si].cost.time;
                }
                parallelTime = Math.max.apply(null, builderFinishTimes);
            }
        }

        for (var pi = 0; pi < prereqSteps.length; pi++) {
            allSteps.push(prereqSteps[pi]);
        }

        // HQ upgrade
        var hqFrom = Math.max(currentHQ, upgradedTo['headquarters'] || hq - 1);
        if (hqFrom < hq) {
            var hqCost = getCostForRange('headquarters', hqFrom, hq);
            if (speedBonus > 0) hqCost.time = Math.floor(hqCost.time / (1 + speedBonus / 100));
            allSteps.push({
                buildingKey: 'headquarters',
                name: 'Headquarters',
                fromLevel: hqFrom,
                toLevel: hq,
                forHQ: hq,
                cost: hqCost,
                type: 'hq',
                parallel: false,
                parallelPrereqTime: parallelTime
            });
            upgradedTo['headquarters'] = hq;
            totalParallelTime += parallelTime + hqCost.time;
        }
    }

    renderSteps(container, allSteps, 'fastest', totalParallelTime);
}

/* ---------- POWER ROI ---------- */
function computePowerROI() {
    var container = document.getElementById('tab-powerroi');
    var targetHQ = parseInt(document.getElementById('targetHQ').value) || 1;
    var reqs = getRequirementsForHQ(targetHQ);
    var reqMap = {};
    for (var r = 0; r < reqs.length; r++) {
        var bKey = normalizeBuildingName(reqs[r].building);
        if (bKey) reqMap[bKey] = reqs[r].level;
    }

    var recommendations = [];

    // Iterate all state keys (includes instance keys), skip locked instances
    for (var iKey in state) {
        var baseKey = getBaseKey(iKey);
        var bData = buildings[baseKey];
        if (!bData) continue;
        var instNum = getInstanceNum(iKey);
        var mi = MULTI_INSTANCE[baseKey];
        if (mi && mi.unlockHQ[instNum - 1] > (state['headquarters'] || 0)) continue;
        var currentLvl = state[iKey] || 0;
        if (currentLvl >= bData.levels.length) continue;

        var nextLvl = bData.levels[currentLvl];
        var power = nextLvl.power || 0;
        var totalRss = (nextLvl.rss ? nextLvl.rss.food || 0 : 0) +
                       (nextLvl.rss ? nextLvl.rss.iron || 0 : 0) +
                       (nextLvl.rss ? nextLvl.rss.gold || 0 : 0);

        if (totalRss <= 0 || power <= 0) continue;

        var efficiency = power / totalRss * 1000000;
        var isRequired = reqMap[baseKey] && getMaxInstanceLevel(baseKey) < reqMap[baseKey];
        var instNum = getInstanceNum(iKey);
        var stepName = MULTI_INSTANCE[baseKey] ? getInstanceDisplayName(baseKey, instNum) : (displayNames[baseKey] || baseKey);

        recommendations.push({
            buildingKey: iKey,
            name: stepName,
            fromLevel: currentLvl,
            toLevel: currentLvl + 1,
            cost: {
                food: nextLvl.rss ? nextLvl.rss.food || 0 : 0,
                iron: nextLvl.rss ? nextLvl.rss.iron || 0 : 0,
                gold: nextLvl.rss ? nextLvl.rss.gold || 0 : 0,
                time: parseTime(nextLvl.time),
                power: power
            },
            efficiency: efficiency,
            isRequired: isRequired,
            type: isRequired ? 'req' : 'roi'
        });
    }

    recommendations.sort(function(a, b) {
        if (a.isRequired && !b.isRequired) return -1;
        if (!a.isRequired && b.isRequired) return 1;
        return b.efficiency - a.efficiency;
    });

    var top = recommendations.slice(0, 15);
    renderROISteps(container, top);
}

/* ---------- RENDER STEPS ---------- */
function renderSteps(container, steps, mode, totalParallelTime) {
    if (steps.length === 0) {
        container.innerHTML = '<div style="padding:20px;text-align:center;color:var(--green);font-weight:700;">All requirements met! Ready to upgrade.</div>';
        return;
    }

    var html = '';
    var totalFood = 0, totalIron = 0, totalGold = 0, totalTime = 0, totalPower = 0;

    for (var i = 0; i < steps.length; i++) {
        var step = steps[i];
        var typeClass = step.type === 'hq' ? 'hq-upgrade' : 'required';
        var badgeClass = step.type === 'hq' ? 'badge-hq' : 'badge-req';
        var badgeText = step.type === 'hq' ? 'HQ' : 'REQ HQ' + step.forHQ;
        var choiceNote = step.isChoice ? '<div style="font-size:11px;color:#888;margin-top:4px;">Cheapest of: ' + (step.choices || []).join(', ') + '</div>' : '';

        html += '<div class="upgrade-step ' + typeClass + '">' +
            '<div class="step-header">' +
                '<span class="step-name">' + (i+1) + '. ' + step.name + ' ' + step.fromLevel + ' &rarr; ' + step.toLevel + '</span>' +
                '<span class="step-badge ' + badgeClass + '">' + badgeText + '</span>' +
            '</div>' +
            '<div class="step-stats">' +
                '<span>Food: ' + fN(step.cost.food) + '</span>' +
                '<span>Iron: ' + fN(step.cost.iron) + '</span>' +
                '<span>Gold: ' + fN(step.cost.gold) + '</span>' +
                '<span>Time: ' + formatTime(step.cost.time) + '</span>' +
                '<span>Power: +' + fN(step.cost.power) + '</span>' +
            '</div>' +
            choiceNote +
        '</div>';

        totalFood += step.cost.food;
        totalIron += step.cost.iron;
        totalGold += step.cost.gold;
        totalTime += step.cost.time;
        totalPower += step.cost.power;
    }

    var displayTime = totalTime;
    var timeLabel = '(sequential)';
    if (mode === 'fastest' && totalParallelTime) {
        displayTime = totalParallelTime;
        timeLabel = '(with parallel builders)';
    }

    // Apply speedups to display time
    var speedupTotal = getSpeedupTotalSeconds();
    var speedupResult = applySpeedups(displayTime);
    var hasSpeedups = speedupTotal > 0;

    html += '<div class="summary-box">' +
        '<h4>Total ' + timeLabel + '</h4>' +
        '<div class="summary-row"><span>Food:</span><span>' + fN(totalFood) + '</span></div>' +
        '<div class="summary-row"><span>Iron:</span><span>' + fN(totalIron) + '</span></div>' +
        '<div class="summary-row"><span>Gold:</span><span>' + fN(totalGold) + '</span></div>' +
        '<div class="summary-row"><span>Build Time:</span><span>' + formatTime(displayTime) + ' ' + timeLabel + '</span></div>';

    if (hasSpeedups) {
        html +=
            '<div class="summary-row" style="color:var(--cyan);font-weight:700;"><span>After Speedups:</span><span>' + formatTime(speedupResult.remainingTime) + '</span></div>' +
            '<div class="summary-row" style="font-size:11px;color:#888;"><span>Speedups Used:</span><span>' + formatSpeedupsUsed(speedupResult.used) + '</span></div>';
        var remSp = getRemainingSpeedups(speedupResult.used);
        var remTotal = 0;
        for (var ri = 0; ri < SPEEDUP_TYPES.length; ri++) remTotal += (remSp[SPEEDUP_TYPES[ri].key] || 0) * SPEEDUP_TYPES[ri].secs;
        if (remTotal > 0) {
            html += '<div class="summary-row" style="font-size:11px;color:#888;"><span>Remaining Speedups:</span><span>' + formatTime(remTotal) + '</span></div>';
        }
    }

    html += '<div class="summary-row"><span>Power:</span><span>+' + fN(totalPower) + '</span></div>' +
    '</div>';

    container.innerHTML = html;
}

function renderROISteps(container, steps) {
    if (steps.length === 0) {
        container.innerHTML = '<div style="padding:20px;text-align:center;color:#888;">All buildings maxed or no power data available.</div>';
        return;
    }

    var html = '<div style="font-size:12px;color:#888;margin-bottom:8px;">Ranked by power gained per resource spent. Required buildings for target HQ shown first.</div>';

    for (var i = 0; i < steps.length; i++) {
        var step = steps[i];
        var badgeClass = step.isRequired ? 'badge-req' : 'badge-roi';
        var badgeText = step.isRequired ? 'REQUIRED' : 'ROI';
        var typeClass = step.isRequired ? 'required' : '';

        html += '<div class="upgrade-step ' + typeClass + '">' +
            '<div class="step-header">' +
                '<span class="step-name">' + (i+1) + '. ' + step.name + ' ' + step.fromLevel + ' &rarr; ' + step.toLevel + '</span>' +
                '<span class="step-badge ' + badgeClass + '">' + badgeText + '</span>' +
            '</div>' +
            '<div class="step-stats">' +
                '<span style="color:var(--teal);font-weight:700;">ROI: ' + fN(step.efficiency) + '</span>' +
                '<span>Power: +' + fN(step.cost.power) + '</span>' +
                '<span>Food: ' + fN(step.cost.food) + '</span>' +
                '<span>Iron: ' + fN(step.cost.iron) + '</span>' +
                '<span>Gold: ' + fN(step.cost.gold) + '</span>' +
            '</div>' +
        '</div>';
    }

    container.innerHTML = html;
}

/* ---------- TABS ---------- */
function setupTabs() {
    var btns = document.querySelectorAll('.tab-btn');
    for (var i = 0; i < btns.length; i++) {
        btns[i].onclick = function() {
            var allBtns = document.querySelectorAll('.tab-btn');
            var allContent = document.querySelectorAll('.tab-content');
            for (var j = 0; j < allBtns.length; j++) allBtns[j].classList.remove('active');
            for (var k = 0; k < allContent.length; k++) allContent[k].classList.remove('active');
            this.classList.add('active');
            document.getElementById('tab-' + this.dataset.tab).classList.add('active');
        };
    }
}

/* ---------- CSV EXPORT/IMPORT ---------- */
function exportCSV() {
    var rows = ['# Speedups: m5=' + (speedupState.m5||0) + ',m15=' + (speedupState.m15||0) + ',m30=' + (speedupState.m30||0) + ',h1=' + (speedupState.h1||0) + ',h3=' + (speedupState.h3||0) + ',h8=' + (speedupState.h8||0) + ',h24=' + (speedupState.h24||0)];
    rows.push('Building,Instance,Category,CurrentLevel,MaxLevel,Power,RequiredForHQ,Notes');

    for (var catName in categories) {
        var buildingList = categories[catName];
        for (var i = 0; i < buildingList.length; i++) {
            var bKey = buildingList[i];
            var bData = buildings[bKey];
            if (!bData) continue;

            var reqHQs = [];
            for (var h = 1; h <= 35; h++) {
                var reqs = getRequirementsForHQ(h);
                for (var r = 0; r < reqs.length; r++) {
                    var rKey = normalizeBuildingName(reqs[r].building);
                    if (rKey === bKey) reqHQs.push('HQ' + h + ':' + reqs[r].level);
                }
            }
            var reqStr = csvEsc(reqHQs.join(';'));

            var allKeys = getAllInstanceKeys(bKey);
            for (var ai = 0; ai < allKeys.length; ai++) {
                var iKey = allKeys[ai];
                var instNum = getInstanceNum(iKey);
                var lvl = state[iKey] || 0;
                var maxLvl = bData.levels.length;
                var power = getBuildingPower(iKey, lvl);

                rows.push([
                    csvEsc(bKey),
                    instNum,
                    csvEsc(catName),
                    lvl,
                    maxLvl,
                    power,
                    reqStr,
                    ''
                ].join(','));
            }
        }
    }

    var blob = new Blob([rows.join('\n')], { type: 'text/csv' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'building_planner_export.csv';
    a.click();
    URL.revokeObjectURL(url);
    showToast('CSV exported!');
}

function importCSV(event) {
    var file = event.target.files[0];
    if (!file) return;

    var reader = new FileReader();
    reader.onload = function(e) {
        var lines = e.target.result.split(/\r?\n/);

        // Parse speedup comment header if present
        for (var si = 0; si < lines.length; si++) {
            if (lines[si].indexOf('# Speedups:') === 0) {
                var spPart = lines[si].replace('# Speedups: ', '');
                var spPairs = spPart.split(',');
                for (var sp = 0; sp < spPairs.length; sp++) {
                    var kv = spPairs[sp].split('=');
                    if (kv.length === 2 && kv[0] in speedupState) {
                        speedupState[kv[0]] = parseInt(kv[1]) || 0;
                    }
                }
                loadSpeedupUI();
                break;
            }
        }

        // Find header row (skip comment lines)
        var headerIdx = 0;
        for (var hi = 0; hi < lines.length; hi++) {
            if (lines[hi].charAt(0) !== '#') { headerIdx = hi; break; }
        }
        var header = lines[headerIdx].split(',');
        var buildingIdx = header.indexOf('Building');
        var levelIdx = header.indexOf('CurrentLevel');
        var instanceIdx = header.indexOf('Instance');

        if (buildingIdx < 0 || levelIdx < 0) {
            alert('Invalid CSV format. Need Building and CurrentLevel columns.');
            return;
        }

        var imported = 0;
        for (var i = headerIdx + 1; i < lines.length; i++) {
            var cols = parseCSVRow(lines[i]);
            if (cols.length <= Math.max(buildingIdx, levelIdx)) continue;

            var bKey = cols[buildingIdx].trim();
            var instNum = instanceIdx >= 0 ? (parseInt(cols[instanceIdx]) || 1) : 1;
            var iKey = instNum === 1 ? bKey : bKey + '_' + instNum;
            var lvl = parseInt(cols[levelIdx]) || 0;

            if (iKey in state) {
                var base = getBaseKey(iKey);
                var maxLvl = buildings[base] ? buildings[base].levels.length : 0;
                state[iKey] = Math.max(0, Math.min(maxLvl, lvl));
                imported++;
            }
        }

        renderBuildingTracker();
        recalcAll();
        saveProgress();
        showToast('Imported ' + imported + ' buildings!');
    };
    reader.readAsText(file);
    event.target.value = '';
}

function parseCSVRow(line) {
    var result = [];
    var current = '';
    var inQuotes = false;

    for (var i = 0; i < line.length; i++) {
        var ch = line[i];
        if (inQuotes) {
            if (ch === '"' && line[i+1] === '"') { current += '"'; i++; }
            else if (ch === '"') { inQuotes = false; }
            else { current += ch; }
        } else {
            if (ch === '"') { inQuotes = true; }
            else if (ch === ',') { result.push(current); current = ''; }
            else { current += ch; }
        }
    }
    result.push(current);
    return result;
}

function csvEsc(s) {
    s = String(s);
    if (s.indexOf(',') !== -1 || s.indexOf('"') !== -1 || s.indexOf('\n') !== -1) {
        return '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
}

function resetAll() {
    if (!confirm('Reset all building levels and speedups? You can re-import your CSV to restore.')) return;
    for (var b in state) state[b] = 0;
    for (var k in speedupState) speedupState[k] = 0;
    localStorage.removeItem(LS_KEY);
    renderBuildingTracker();
    loadSpeedupUI();
    recalcAll();
    showToast('All levels reset.');
}

/* ---------- UTILITY ---------- */
function fN(v) {
    if (v === undefined || v === null || v === '?') return '?';
    v = Number(v);
    if (isNaN(v)) return '?';
    if (v >= 1000000000) return (v / 1000000000).toFixed(1) + 'B';
    if (v >= 1000000) return (v / 1000000).toFixed(1) + 'M';
    if (v >= 1000) return (v / 1000).toFixed(1) + 'K';
    if (v !== Math.floor(v)) return v.toFixed(1);
    return v.toString();
}

function showToast(msg) {
    var toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(function() { toast.classList.remove('show'); }, 2000);
}

/* ---------- SPEEDUP INVENTORY ---------- */
function toggleSpeedups() {
    document.getElementById('speedupSection').classList.toggle('expanded');
}

function loadSpeedupUI() {
    for (var i = 0; i < SPEEDUP_TYPES.length; i++) {
        var el = document.getElementById('sp-' + SPEEDUP_TYPES[i].key);
        if (el) el.value = speedupState[SPEEDUP_TYPES[i].key] || 0;
    }
    updateSpeedupDisplay();
}

function onSpeedupChange() {
    for (var i = 0; i < SPEEDUP_TYPES.length; i++) {
        var el = document.getElementById('sp-' + SPEEDUP_TYPES[i].key);
        speedupState[SPEEDUP_TYPES[i].key] = Math.max(0, parseInt(el.value) || 0);
    }
    updateSpeedupDisplay();
    recalcAll();
    saveProgress();
}

function getSpeedupTotalSeconds() {
    var total = 0;
    for (var i = 0; i < SPEEDUP_TYPES.length; i++) {
        total += (speedupState[SPEEDUP_TYPES[i].key] || 0) * SPEEDUP_TYPES[i].secs;
    }
    return total;
}

function updateSpeedupDisplay() {
    var total = getSpeedupTotalSeconds();
    var h = Math.floor(total / 3600);
    var m = Math.floor((total % 3600) / 60);
    var lbl = document.getElementById('speedupTotalLabel');
    if (lbl) lbl.textContent = h + 'h ' + m + 'm total';
    var sum = document.getElementById('speedupSummaryText');
    if (sum) sum.textContent = 'Total: ' + h + 'h ' + m + 'm (' + formatTime(total) + ')';
}

function applySpeedups(totalSeconds) {
    // Greedy: use largest speedups first, don't overshoot
    var remaining = totalSeconds;
    var used = {};
    var inventory = {};
    for (var i = 0; i < SPEEDUP_TYPES.length; i++) {
        inventory[SPEEDUP_TYPES[i].key] = speedupState[SPEEDUP_TYPES[i].key] || 0;
        used[SPEEDUP_TYPES[i].key] = 0;
    }
    // Iterate from largest to smallest
    for (var j = SPEEDUP_TYPES.length - 1; j >= 0; j--) {
        var sp = SPEEDUP_TYPES[j];
        if (remaining <= 0) break;
        var canUse = Math.min(inventory[sp.key], Math.floor(remaining / sp.secs));
        if (canUse > 0) {
            used[sp.key] = canUse;
            remaining -= canUse * sp.secs;
        }
    }
    // Use one more of the largest that fits to finish off remaining (if any)
    if (remaining > 0) {
        for (var k = 0; k < SPEEDUP_TYPES.length; k++) {
            var sp2 = SPEEDUP_TYPES[k];
            if (inventory[sp2.key] > used[sp2.key]) {
                used[sp2.key]++;
                remaining = Math.max(0, remaining - sp2.secs);
                break;
            }
        }
    }
    return { remainingTime: Math.max(0, remaining), used: used };
}

function formatSpeedupsUsed(used) {
    var parts = [];
    for (var i = SPEEDUP_TYPES.length - 1; i >= 0; i--) {
        var sp = SPEEDUP_TYPES[i];
        if (used[sp.key] > 0) parts.push(used[sp.key] + 'x ' + sp.label);
    }
    return parts.length > 0 ? parts.join(', ') : 'none';
}

function getRemainingSpeedups(used) {
    var rem = {};
    for (var i = 0; i < SPEEDUP_TYPES.length; i++) {
        var k = SPEEDUP_TYPES[i].key;
        rem[k] = (speedupState[k] || 0) - (used[k] || 0);
    }
    return rem;
}

/* ---------- BUILDING INFO POPUP ---------- */
function showBuildingInfo(buildingKey) {
    var info = BUILDING_INFO[buildingKey];
    if (!info) return;
    var dName = displayNames[buildingKey] || buildingKey;
    var bData = buildings[buildingKey];
    var maxLvl = bData ? bData.levels.length : '?';

    var popup = document.getElementById('infoPopup');
    var overlay = document.getElementById('infoOverlay');
    popup.querySelector('.info-title').textContent = dName;
    popup.querySelector('.info-desc').textContent = info.desc;

    var metaHtml = '<span><b>Max Level:</b> ' + maxLvl + '</span>' +
        '<span><b>Instances:</b> ' + info.instances + '</span>' +
        '<span><b>Unlock:</b> ' + info.unlock + '</span>';
    popup.querySelector('.info-meta').innerHTML = metaHtml;

    popup.classList.add('show');
    overlay.classList.add('show');
}

function closeBuildingInfo() {
    document.getElementById('infoPopup').classList.remove('show');
    document.getElementById('infoOverlay').classList.remove('show');
}

/* ---------- START ---------- */
document.addEventListener('DOMContentLoaded', init);
'''


def generate_html(data):
    data_json = json.dumps(data, separators=(',', ':'))

    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Building Progression Planner - OWOW</title>
''' + generate_css() + '''
</head>
<body>

<nav class="guide-nav">
  <a href="../" class="nav-home">&#8592; Home</a>
  <a href="ai_advisor.html">AI Advisor</a>
  <a href="alliance_support_hub.html">Alliance Hub</a>
  <a href="building_planner.html" class="current">Building Planner</a>
  <a href="building_reference.html">Building Ref</a>
  <a href="capitol_positions.html">Capitol Positions</a>
  <a href="chip_lab_guide.html">Chip Lab</a>
  <a href="calendar.html">Calendar</a>
  <a href="hero_planner.html">Hero Planner</a>
  <a href="plunder_guide.html">Plunder</a>
  <a href="radar_guide.html">Radar</a>
  <a href="../research_trees_visual.html">Research Trees</a>
  <a href="server_dashboard.html">Server</a>
  <a href="vs_weekly_planner.html">VS Planner</a>
  <a href="waterfall_guide.html">Waterfall</a>
</nav>

<div class="top-bar">
  <div>
    <h1>Building Progression Planner</h1>
    <div class="sub">Last War: Survival</div>
  </div>
  <div class="alliance">
    <div class="name">[OWOW]</div>
    <div class="info">Old World Order</div>
  </div>
</div>

<div class="commander-bar">
  <label>Current HQ: <select id="currentHQ"></select></label>
  <label>Target HQ: <select id="targetHQ"></select></label>
  <label>Builders: <input type="number" id="builderCount" min="1" max="5" value="3"></label>
  <label>VIP Level: <select id="vipLevel"></select></label>
</div>

<div class="speedup-section" id="speedupSection">
  <div class="speedup-toggle" onclick="toggleSpeedups()">
    <span class="arrow">&#9654;</span>
    <span>Speedup Inventory</span>
    <span class="total-hours" id="speedupTotalLabel">0h total</span>
  </div>
  <div class="speedup-body">
    <div class="speedup-grid">
      <div class="speedup-field">
        <label>5 min</label>
        <input type="number" id="sp-m5" min="0" value="0" onchange="onSpeedupChange()" oninput="onSpeedupChange()">
      </div>
      <div class="speedup-field">
        <label>15 min</label>
        <input type="number" id="sp-m15" min="0" value="0" onchange="onSpeedupChange()" oninput="onSpeedupChange()">
      </div>
      <div class="speedup-field">
        <label>30 min</label>
        <input type="number" id="sp-m30" min="0" value="0" onchange="onSpeedupChange()" oninput="onSpeedupChange()">
      </div>
      <div class="speedup-field">
        <label>1 hour</label>
        <input type="number" id="sp-h1" min="0" value="0" onchange="onSpeedupChange()" oninput="onSpeedupChange()">
      </div>
      <div class="speedup-field">
        <label>3 hour</label>
        <input type="number" id="sp-h3" min="0" value="0" onchange="onSpeedupChange()" oninput="onSpeedupChange()">
      </div>
      <div class="speedup-field">
        <label>8 hour</label>
        <input type="number" id="sp-h8" min="0" value="0" onchange="onSpeedupChange()" oninput="onSpeedupChange()">
      </div>
      <div class="speedup-field">
        <label>24 hour</label>
        <input type="number" id="sp-h24" min="0" value="0" onchange="onSpeedupChange()" oninput="onSpeedupChange()">
      </div>
    </div>
    <div class="speedup-summary">
      <span id="speedupSummaryText">Total: 0h 0m</span>
      <span id="speedupRemaining"></span>
    </div>
  </div>
</div>

<div class="power-dashboard">
  <div class="power-card pc-current">
    <div class="label">Current Power</div>
    <div class="value" id="currentPower">0</div>
  </div>
  <div class="power-card pc-target">
    <div class="label">Target Power</div>
    <div class="value" id="targetPower">0</div>
  </div>
  <div class="power-card pc-needed">
    <div class="label">Power Needed</div>
    <div class="value" id="neededPower">0</div>
  </div>
</div>

<div class="section-label">Your Buildings</div>
<div id="buildingTracker"></div>

<div class="section-label">Upgrade Path</div>
<div class="tab-bar">
  <button class="tab-btn active" data-tab="cheapest">Cheapest</button>
  <button class="tab-btn" data-tab="fastest">Fastest</button>
  <button class="tab-btn" data-tab="powerroi">Power ROI</button>
</div>
<div id="tab-cheapest" class="tab-content active"></div>
<div id="tab-fastest" class="tab-content"></div>
<div id="tab-powerroi" class="tab-content"></div>

<div class="action-bar">
  <button class="action-btn btn-export" onclick="exportCSV()">Export CSV</button>
  <button class="action-btn btn-import" onclick="document.getElementById('csvFileInput').click()">Import CSV</button>
  <input type="file" id="csvFileInput" accept=".csv" onchange="importCSV(event)">
  <button class="action-btn btn-reset" onclick="resetAll()">Reset</button>
  <a class="action-btn btn-ai" href="ai_building_advisor_prompt.md" download>AI Advisor</a>
</div>

<div class="footer">
  <div class="tagline">Kristen OWOW SKYNET. Ready for Judgment Day.</div>
  <div>Building data from <a href="https://cpt-hedge.com" style="color:var(--cyan);">cpt-hedge.com</a></div>
</div>

<div class="info-overlay" id="infoOverlay" onclick="closeBuildingInfo()"></div>
<div class="info-popup" id="infoPopup">
  <button class="info-close" onclick="closeBuildingInfo()">&times;</button>
  <h4 class="info-title"></h4>
  <div class="info-desc"></div>
  <div class="info-meta"></div>
</div>

<div class="toast" id="toast"></div>

<script>
const BUILDING_DATA = ''' + data_json + ''';
''' + generate_js() + '''
</script>
</body>
</html>'''


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'building_data_complete.json')
    output_dir = os.path.join(script_dir, 'guides')
    output_path = os.path.join(output_dir, 'building_planner.html')

    os.makedirs(output_dir, exist_ok=True)

    print("Loading building data...")
    data = load_building_data(data_path)

    print("Generating HTML...")
    html = generate_html(data)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    bcount = len(data.get('buildings', {}))
    hqcount = len(data.get('hqRequirements', []))
    catcount = len(data.get('categories', {}))
    print(f"Generated: {output_path}")
    print(f"  Buildings: {bcount}")
    print(f"  HQ Requirements: {hqcount}")
    print(f"  Categories: {catcount}")


if __name__ == "__main__":
    main()
