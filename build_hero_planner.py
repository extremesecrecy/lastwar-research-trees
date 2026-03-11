#!/usr/bin/env python3
"""
Build the Hero Planner HTML page.
Reads hero_registry.json, cpt_hedge_all_data.json, cpt_hedge_supplemental.json,
and hero screenshots to generate a self-contained HTML with embedded CSS, JS,
images, and cost data.

Output: guides/hero_planner.html
"""
import json
import os
import base64


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_hero_images(registry, image_dir):
    """Load and base64-encode hero screenshots."""
    images = {}
    for name, hero in registry['heroes'].items():
        img_file = hero.get('imageFile', '')
        if not img_file:
            continue
        img_path = os.path.join(image_dir, img_file)
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                data = f.read()
            images[name] = base64.b64encode(data).decode('ascii')
    return images


def build_cost_data(all_data, supplemental):
    """Extract and restructure cost tables for embedding in JS."""
    # XP table: level -> cost
    xp_table = {}
    for entry in all_data['/calculators/hero-exp'][0]:
        if entry['experience'] > 0:
            xp_table[str(entry['heroLevel'])] = entry['experience']

    # Skill medals: rarity -> [cost_per_level]
    skill_medals = all_data['/calculators/skill-medals'][0]

    # Gear upgrade costs: rarity -> [{level, gold, ore}]
    gear_upgrades = all_data['/calculators/gear'][0]

    # Gear star promotion: [{stars, tier, gold, ore, dielectric_ceramic, gear_blueprint?}]
    gear_stars = all_data['/calculators/gear'][1]

    # Weapon shards: segments with minLevel, maxLevel, shardsPerLevel
    weapon_data = all_data['/calculators/weapon-shards'][0]

    # Hero shard costs for starring up
    hero_shards = supplemental['hero_shards']

    return {
        'xpTable': xp_table,
        'skillMedals': skill_medals,
        'gearUpgrades': gear_upgrades,
        'gearStars': gear_stars,
        'weaponData': weapon_data,
        'heroShards': hero_shards,
    }


def generate_css():
    return r'''<style>
  @font-face {
    font-family: 'DKCrayonCrumble';
    src: url('DKCrayonCrumble.ttf') format('truetype');
    font-weight: normal; font-style: normal;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  :root {
    --orange: #f4a261; --cyan: #5bc0de; --yellow: #f4d35e;
    --teal: #7fb3a8; --dark: #5a6a6a; --text: #333;
    --watermelon: #fc5c65; --green: #43a047; --red: #e53935;
    --gray: #ccc; --light-bg: #fafafa;
    --ur-gold: #d4a017; --ssr-purple: #9b59b6; --sr-blue: #3498db;
  }
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #fff; color: var(--text); padding: 8px; min-height: 100vh;
  }
  h1, h2, h3, .section-label, .alliance .name {
    font-family: 'DKCrayonCrumble', 'Segoe UI', sans-serif;
  }

  /* Navigation Bar */
  .guide-nav {
    display: flex; flex-wrap: wrap; gap: 4px 12px; align-items: center;
    padding: 6px 16px; background: #f0f5f4; border-bottom: 2px solid #7fb3a8;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 12px;
    margin: -8px -8px 12px -8px; width: 100vw; position: relative;
    left: 50%; transform: translateX(-50%); box-sizing: border-box;
  }
  .guide-nav a { color: #5a6a6a; text-decoration: none; padding: 2px 6px; border-radius: 3px; white-space: nowrap; }
  .guide-nav a:hover { color: #f4a261; background: #fff; }
  .guide-nav a.current { color: #f4a261; font-weight: bold; background: #fff; border: 1px solid #f4a261; }
  .guide-nav .nav-home { font-weight: bold; margin-right: 8px; padding-right: 12px; border-right: 1px solid #7fb3a8; }
  @media (max-width: 480px) {
    .guide-nav { padding: 4px 10px; gap: 3px 8px; font-size: 11px; margin: -4px -4px 8px -4px; }
  }
  @media (min-width: 769px) { .guide-nav { margin: -16px -16px 12px -16px; } }

  /* Header */
  .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px; }
  .top-bar h1 { font-size: 20px; letter-spacing: 1px; text-transform: uppercase; color: var(--dark); }
  .top-bar .sub { font-size: 12px; color: #888; }
  .alliance { background: #e8f4f1; border: 1px solid var(--teal); border-radius: 5px; padding: 2px 10px; text-align: right; }
  .alliance .name { font-size: 17px; font-weight: 800; color: var(--dark); }
  .alliance .info { font-size: 12px; color: #666; }

  /* Commander Bar */
  .commander-bar {
    display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
    background: #e8f4f1; border: 1.5px solid var(--teal); border-radius: 8px;
    padding: 10px 14px; margin-bottom: 10px;
  }
  .commander-bar label { font-size: 13px; font-weight: 600; color: var(--dark); display: flex; align-items: center; gap: 6px; }
  .commander-bar select, .commander-bar input[type="number"] {
    padding: 4px 8px; border: 1.5px solid var(--teal); border-radius: 5px; font-size: 14px; background: #fff; min-width: 60px;
  }

  /* Tab Bar */
  .tab-bar { display: flex; gap: 4px; margin-bottom: 10px; }
  .tab-btn {
    flex: 1; padding: 10px 4px; border: 1.5px solid var(--gray); border-radius: 6px;
    background: #fff; font-size: 13px; font-weight: 600; color: var(--dark);
    cursor: pointer; text-align: center; transition: all 0.2s;
  }
  .tab-btn.active { border-color: var(--watermelon); background: var(--watermelon); color: #fff; }
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* Filter Bar */
  .filter-bar {
    display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
    margin-bottom: 10px; padding: 8px 12px;
    background: var(--light-bg); border: 1px solid #eee; border-radius: 8px;
  }
  .filter-bar label { font-size: 12px; font-weight: 600; color: var(--dark); display: flex; align-items: center; gap: 4px; }
  .filter-bar select { padding: 3px 6px; border: 1px solid var(--gray); border-radius: 4px; font-size: 12px; }
  .filter-bar .sort-btn {
    margin-left: auto; padding: 3px 10px; border: 1px solid var(--cyan);
    border-radius: 4px; background: #fff; color: var(--cyan); font-size: 11px;
    font-weight: 600; cursor: pointer;
  }
  .filter-bar .sort-btn:hover { background: var(--cyan); color: #fff; }

  /* Power Dashboard */
  .power-dashboard { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 10px; }
  .power-card { border-radius: 8px; padding: 10px 12px; text-align: center; }
  .power-card .label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--dark); margin-bottom: 4px; }
  .power-card .value { font-family: 'DKCrayonCrumble', sans-serif; font-size: 22px; font-weight: 800; }
  .pc-squad1 { background: #e8f4f1; border: 1.5px solid var(--teal); }
  .pc-squad1 .value { color: var(--teal); }
  .pc-squad2 { background: #fef3e2; border: 1.5px solid var(--orange); }
  .pc-squad2 .value { color: var(--orange); }
  .pc-total { background: #f3e8f9; border: 1.5px solid var(--ssr-purple); }
  .pc-total .value { color: var(--ssr-purple); }

  /* Hero Cards */
  .hero-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 10px;
  }
  .hero-card {
    border: 1.5px solid var(--gray); border-radius: 10px;
    padding: 12px; background: #fff; transition: border-color 0.2s;
  }
  .hero-card:hover { border-color: var(--teal); }
  .hero-card.squad-assigned { border-left: 4px solid var(--teal); }
  .hero-card.bench { opacity: 0.7; }

  .hero-card-header {
    display: flex; gap: 10px; align-items: center; margin-bottom: 8px;
  }
  .hero-portrait {
    width: 60px; height: 60px; border-radius: 8px;
    object-fit: cover; object-position: left center;
    border: 2px solid var(--gray); flex-shrink: 0;
  }
  .hero-portrait.rarity-UR { border-color: var(--ur-gold); }
  .hero-portrait.rarity-SSR { border-color: var(--ssr-purple); }
  .hero-portrait.rarity-SR { border-color: var(--sr-blue); }

  .hero-info { flex: 1; min-width: 0; }
  .hero-name-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .hero-name { font-weight: 700; font-size: 15px; color: var(--dark); }
  .rarity-badge {
    font-size: 10px; font-weight: 700; padding: 1px 6px;
    border-radius: 3px; color: #fff; letter-spacing: 0.5px;
  }
  .rarity-UR { background: var(--ur-gold); }
  .rarity-SSR { background: var(--ssr-purple); }
  .rarity-SR { background: var(--sr-blue); }
  .hero-meta { font-size: 11px; color: #888; margin-top: 2px; }
  .type-icon { font-weight: 600; }
  .type-Aircraft { color: #2196f3; }
  .type-Tank { color: #4caf50; }
  .type-Missile { color: #ff5722; }

  /* Hero card body */
  .hero-card-body { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 12px; }
  .field-group { display: flex; flex-direction: column; gap: 2px; }
  .field-label { font-size: 10px; font-weight: 600; color: var(--dark); text-transform: uppercase; letter-spacing: 0.5px; }
  .field-row { display: flex; gap: 4px; align-items: center; }
  .field-row select, .field-row input[type="number"] {
    padding: 2px 4px; border: 1px solid var(--gray); border-radius: 4px;
    font-size: 13px; min-width: 48px; background: #fff;
  }
  .field-row input[type="number"] { width: 54px; }
  .field-row select:focus, .field-row input:focus { outline: none; border-color: var(--teal); }

  /* Star display */
  .star-row { display: flex; gap: 2px; }
  .star { cursor: pointer; font-size: 16px; color: var(--gray); transition: color 0.15s; user-select: none; }
  .star.filled { color: var(--ur-gold); }
  .star:hover { color: var(--yellow); }

  /* Skill inputs */
  .skill-inputs { display: flex; gap: 4px; align-items: center; }
  .skill-inputs input {
    width: 38px; padding: 2px; border: 1px solid var(--gray); border-radius: 4px;
    font-size: 12px; text-align: center;
  }
  .skill-inputs .sep { color: #ccc; font-size: 10px; }

  /* Gear grid */
  .gear-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
  .gear-slot {
    display: flex; align-items: center; gap: 4px;
    padding: 3px 6px; background: var(--light-bg); border-radius: 4px; font-size: 11px;
  }
  .gear-slot .gear-icon { font-size: 13px; width: 18px; text-align: center; }
  .gear-slot input {
    width: 36px; padding: 1px 3px; border: 1px solid var(--gray);
    border-radius: 3px; font-size: 11px; text-align: center;
  }

  /* Squad assignment */
  .squad-select { margin-top: 6px; display: flex; align-items: center; gap: 6px; }
  .squad-select select {
    padding: 3px 6px; border: 1px solid var(--gray); border-radius: 4px;
    font-size: 12px; flex: 1;
  }
  .hero-power-est {
    font-family: 'DKCrayonCrumble', sans-serif;
    font-size: 14px; color: var(--teal); font-weight: 700;
    text-align: right; margin-top: 4px;
  }

  /* Squad View Tab */
  .squad-tabs { display: flex; gap: 4px; margin-bottom: 10px; }
  .squad-tab-btn {
    flex: 1; padding: 8px; border: 1.5px solid var(--gray); border-radius: 6px;
    background: #fff; font-size: 12px; font-weight: 600; color: var(--dark);
    cursor: pointer; text-align: center;
  }
  .squad-tab-btn.active { border-color: var(--teal); background: var(--teal); color: #fff; }

  .synergy-bar {
    display: flex; align-items: center; gap: 8px; padding: 8px 12px;
    background: #e8f4f1; border: 1.5px solid var(--teal); border-radius: 8px;
    margin-bottom: 10px; font-size: 13px;
  }
  .synergy-bar .bonus { font-weight: 700; color: var(--green); }
  .synergy-bar .warning { font-weight: 700; color: var(--watermelon); }

  .squad-hero-row {
    display: flex; gap: 10px; overflow-x: auto; padding-bottom: 8px;
  }
  .squad-hero-card {
    flex: 0 0 180px; border: 1.5px solid var(--gray); border-radius: 10px;
    padding: 10px; text-align: center; background: #fff;
  }
  .squad-hero-card .portrait-wrap { display: flex; justify-content: center; margin-bottom: 6px; }
  .squad-hero-card .hero-portrait { width: 70px; height: 70px; }
  .squad-hero-card .hero-name { font-weight: 700; font-size: 14px; margin-bottom: 4px; }
  .squad-hero-card .stat-line { font-size: 11px; color: #666; margin: 2px 0; }
  .squad-hero-card .stat-line strong { color: var(--dark); }

  .squad-summary {
    background: #e8f4f1; border: 2px solid var(--teal); border-radius: 8px;
    padding: 12px; margin-top: 10px;
  }
  .squad-summary h4 { font-family: 'DKCrayonCrumble', sans-serif; color: var(--dark); margin-bottom: 6px; }
  .squad-summary .row { display: flex; justify-content: space-between; padding: 3px 0; font-size: 13px; }

  .recommendations {
    margin-top: 10px; padding: 12px;
    background: #fef3e2; border: 1.5px solid var(--orange); border-radius: 8px;
  }
  .recommendations h4 { font-family: 'DKCrayonCrumble', sans-serif; color: var(--dark); margin-bottom: 8px; }
  .rec-item {
    padding: 6px 8px; margin-bottom: 4px;
    background: #fff; border-radius: 6px; font-size: 12px; border-left: 3px solid var(--orange);
  }
  .rec-item .rec-action { font-weight: 700; color: var(--dark); }
  .rec-item .rec-detail { color: #666; margin-top: 2px; }

  /* Planner Tab */
  .planner-controls {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 8px; margin-bottom: 12px; padding: 12px;
    background: var(--light-bg); border: 1px solid #eee; border-radius: 8px;
  }
  .planner-field { display: flex; flex-direction: column; gap: 3px; }
  .planner-field label { font-size: 11px; font-weight: 600; color: var(--dark); text-transform: uppercase; }
  .planner-field input {
    padding: 6px 8px; border: 1.5px solid var(--gray); border-radius: 5px;
    font-size: 14px; background: #fff;
  }
  .planner-field input:focus { outline: none; border-color: var(--teal); }
  .planner-field .helper-text { font-size: 10px; color: #999; line-height: 1.3; }
  .plan-info-box { background: #fef3e2; border: 1.5px solid var(--orange); border-radius: 8px; padding: 12px; }
  .plan-info-box h4 { font-family: 'DKCrayonCrumble', sans-serif; color: var(--dark); margin-bottom: 8px; font-size: 14px; }
  .plan-info-box .rec-item { margin-bottom: 6px; padding: 6px 8px; border-left: 3px solid var(--cyan); }
  .thursday-toggle {
    display: flex; align-items: center; gap: 8px; padding: 8px 12px;
    background: #fef3e2; border: 1.5px solid var(--orange); border-radius: 8px;
    margin-bottom: 10px; cursor: pointer; user-select: none;
  }
  .thursday-toggle input[type="checkbox"] { width: 18px; height: 18px; accent-color: var(--orange); }
  .thursday-toggle .label { font-weight: 600; color: var(--dark); font-size: 13px; }
  .thursday-toggle .info { font-size: 11px; color: #888; }

  .shard-inventory {
    display: flex; flex-wrap: wrap; gap: 6px; padding: 8px 12px;
    background: #f9f5ff; border: 1px solid #d4a017; border-radius: 8px;
    margin-bottom: 10px;
  }
  .shard-inventory:empty { display: none; }
  .shard-inventory h4 {
    width: 100%; font-family: 'DKCrayonCrumble', sans-serif;
    font-size: 13px; color: var(--dark); margin-bottom: 2px;
  }
  .shard-hero {
    display: flex; align-items: center; gap: 4px;
    background: #fff; border: 1px solid #eee; border-radius: 6px;
    padding: 4px 8px; font-size: 12px;
  }
  .shard-hero .name { font-weight: 600; color: var(--dark); }
  .shard-hero input {
    width: 60px; padding: 3px 5px; border: 1px solid var(--gray);
    border-radius: 4px; font-size: 12px; text-align: center;
  }
  .phase-header {
    font-family: 'DKCrayonCrumble', sans-serif;
    font-size: 14px; color: var(--dark); padding: 8px 0 4px 0;
    border-bottom: 1px solid #eee; margin-top: 10px; margin-bottom: 6px;
  }
  .plan-leftovers {
    background: #fef3e2; border: 1.5px solid var(--orange);
    border-radius: 8px; padding: 10px 12px; margin-top: 10px;
  }
  .plan-leftovers h4 {
    font-family: 'DKCrayonCrumble', sans-serif;
    font-size: 13px; color: var(--dark); margin-bottom: 4px;
  }
  .leftover-line { font-size: 12px; color: #666; padding: 2px 0; }

  .plan-output { margin-top: 10px; }
  .plan-step {
    padding: 10px 12px; margin-bottom: 6px;
    background: var(--light-bg); border: 1px solid #ddd; border-radius: 8px;
    border-left: 4px solid var(--teal);
  }
  .plan-step .step-num { font-size: 10px; color: var(--cyan); font-weight: 700; text-transform: uppercase; }
  .plan-step .step-action { font-weight: 700; font-size: 13px; color: var(--dark); margin: 2px 0; }
  .plan-step .step-cost { font-size: 12px; color: #666; }
  .plan-step .step-pts { font-size: 11px; color: var(--orange); font-weight: 600; }
  .plan-step.highlight { border-left-color: var(--orange); background: #fef3e2; }

  .plan-summary {
    background: #e8f4f1; border: 2px solid var(--teal); border-radius: 8px;
    padding: 12px; margin-top: 10px;
  }
  .plan-summary h4 { font-family: 'DKCrayonCrumble', sans-serif; color: var(--dark); margin-bottom: 6px; }
  .plan-summary .row { display: flex; justify-content: space-between; padding: 3px 0; font-size: 13px; }
  .plan-summary .row.total { font-weight: 700; border-top: 1px solid var(--teal); padding-top: 6px; margin-top: 4px; }

  /* Action Bar */
  .action-bar { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
  .action-btn {
    flex: 1; min-width: 80px; padding: 10px 8px; border: none; border-radius: 8px;
    font-size: 13px; font-weight: 700; cursor: pointer; text-align: center;
    transition: opacity 0.2s; text-decoration: none;
    display: inline-flex; align-items: center; justify-content: center;
  }
  .action-btn:active { opacity: 0.7; }
  .btn-export { background: var(--watermelon); color: #fff; }
  .btn-import { background: var(--orange); color: #fff; }
  .btn-reset { background: var(--gray); color: var(--dark); }
  .btn-generate { background: var(--teal); color: #fff; }
  #csvFileInput { display: none; }

  /* Footer */
  .footer { text-align: center; padding: 12px 0; font-size: 12px; color: #888; border-top: 1px solid #eee; margin-top: 12px; }
  .footer .tagline { font-family: 'DKCrayonCrumble', sans-serif; font-size: 14px; color: var(--dark); }

  /* Toast */
  .toast {
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    background: var(--dark); color: #fff; padding: 10px 20px; border-radius: 8px;
    font-size: 13px; font-weight: 600; z-index: 1000; opacity: 0;
    transition: opacity 0.3s; pointer-events: none;
  }
  .toast.show { opacity: 1; }

  /* Responsive */
  @media (max-width: 480px) {
    body { padding: 4px; }
    .top-bar h1 { font-size: 17px; }
    .power-dashboard { grid-template-columns: 1fr; }
    .commander-bar { flex-direction: column; gap: 8px; align-items: stretch; }
    .hero-grid { grid-template-columns: 1fr; }
    .hero-card-body { grid-template-columns: 1fr; }
    .tab-btn { font-size: 11px; padding: 8px 2px; }
    .action-bar { flex-direction: column; }
    .action-btn { min-width: 100%; }
    .squad-hero-card { flex: 0 0 150px; }
    .planner-controls { grid-template-columns: 1fr 1fr; }
    .filter-bar { flex-direction: column; align-items: stretch; }
    .filter-bar .sort-btn { margin-left: 0; }
  }
  @media (min-width: 769px) {
    body { max-width: 960px; margin: 0 auto; padding: 16px; }
  }
</style>'''


def generate_js(cost_data, registry, images):
    # Embed data as JS objects
    cost_json = json.dumps(cost_data, separators=(',', ':'))
    registry_json = json.dumps(registry, separators=(',', ':'))
    images_json = json.dumps(images, separators=(',', ':'))

    return f'''
const COST_DATA = {cost_json};
const HERO_REGISTRY = {registry_json};
const HERO_IMAGES = {images_json};
''' + r'''
const LS_KEY = 'owow-hero-planner';

/* ===== STAR CAPS ===== */
const STAR_SKILL_CAP = { 0:1, 1:3, 2:6, 3:10, 4:20, 5:30 };
const STAR_SHARD_COST = [25, 50, 100, 300, 500]; // 0->1, 1->2, ..., 4->5

/* ===== STATE ===== */
let state = {
  hqLevel: 24,
  vipLevel: 13,
  heroes: {}
};

function initState() {
  for (const [name, meta] of Object.entries(HERO_REGISTRY.heroes)) {
    if (!state.heroes[name]) {
      state.heroes[name] = {
        level: 0, stars: 0,
        skills: new Array(meta.skillCount || 3).fill(1),
        gear: [
          { level: 0, stars: 0 },
          { level: 0, stars: 0 },
          { level: 0, stars: 0 },
          { level: 0, stars: 0 }
        ],
        weaponLevel: 0,
        shards: 0,
        squad: 0
      };
    }
  }
}

/* ===== LOCALSTORAGE ===== */
function saveState() {
  try { localStorage.setItem(LS_KEY, JSON.stringify(state)); } catch(e) {}
}

function loadState() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return;
    const saved = JSON.parse(raw);
    if (saved.hqLevel) state.hqLevel = saved.hqLevel;
    if (saved.vipLevel !== undefined) state.vipLevel = saved.vipLevel;
    if (saved.heroes) {
      for (const [name, data] of Object.entries(saved.heroes)) {
        if (HERO_REGISTRY.heroes[name]) {
          state.heroes[name] = data;
        }
      }
    }
  } catch(e) {}
}

/* ===== COST CALCULATIONS ===== */
function calcXpCost(fromLv, toLv) {
  let total = 0;
  for (let lv = fromLv; lv < toLv; lv++) {
    const cost = COST_DATA.xpTable[String(lv)];
    if (cost) total += cost;
  }
  return total;
}

function calcSkillCost(rarity, fromLv, toLv) {
  const table = COST_DATA.skillMedals[rarity];
  if (!table) return 0;
  let total = 0;
  for (let lv = fromLv; lv < toLv; lv++) {
    const idx = lv - 1; // Lv1->2 is index 0
    if (idx >= 0 && idx < table.length) total += table[idx];
  }
  return total;
}

function calcGearCost(rarity, fromLv, toLv) {
  const table = COST_DATA.gearUpgrades[rarity];
  if (!table) return { gold: 0, ore: 0 };
  let gold = 0, ore = 0;
  for (let lv = fromLv; lv < toLv; lv++) {
    const entry = table.find(e => e.level === lv);
    if (entry) { gold += entry.gold; ore += entry.ore; }
  }
  return { gold, ore };
}

function calcWeaponShards(fromLv, toLv) {
  const segments = COST_DATA.weaponData['A0'];
  if (!segments) return 0;
  let total = 0;
  for (const seg of segments) {
    const lo = Math.max(fromLv, seg.minLevel);
    const hi = Math.min(toLv, seg.maxLevel);
    if (lo < hi) total += (hi - lo) * seg.shardsPerLevel;
  }
  return total;
}

function calcStarShards(rarity, fromStar, toStar) {
  const data = rarity === 'SSR' ? COST_DATA.heroShards.ssr : COST_DATA.heroShards.regular;
  let total = 0;
  for (const tier of data) {
    if (tier.starFrom >= fromStar && tier.starTo <= toStar) {
      total += tier.totalShards;
    }
  }
  return total;
}

/* ===== POWER ESTIMATION ===== */
const AVG_POWER_PER_LEVEL = 8588;
function estimatePower(heroName) {
  const h = state.heroes[heroName];
  if (!h || h.level === 0) return 0;
  // Base power from level
  let power = h.level * AVG_POWER_PER_LEVEL;
  // Star bonus: +5% per star
  power *= (1 + h.stars * 0.05);
  // Skill bonus: each skill level adds ~0.5%
  const totalSkill = h.skills.reduce((a, b) => a + b, 0);
  power *= (1 + totalSkill * 0.005);
  // Gear bonus: each gear level adds ~0.3%
  const totalGear = h.gear.reduce((a, g) => a + g.level + g.stars * 8, 0);
  power *= (1 + totalGear * 0.003);
  return Math.round(power);
}

function heroLevelCap() {
  return state.hqLevel * 5 - 1;
}

/* ===== FORMATTING ===== */
function fmt(n) {
  if (n >= 1e9) return (n/1e9).toFixed(1) + 'B';
  if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n/1e3).toFixed(1) + 'K';
  return String(n);
}
function fmtN(n) { return n.toLocaleString(); }

/* ===== TOAST ===== */
function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}

/* ===== RENDER: ROSTER TAB ===== */
let currentSort = 'name';
let sortDir = 1; // 1 = asc (for name default)

function getFilteredHeroes() {
  const typeF = document.getElementById('filterType').value;
  const rarityF = document.getElementById('filterRarity').value;
  const squadF = document.getElementById('filterSquad').value;

  let heroes = Object.entries(HERO_REGISTRY.heroes).map(([name, meta]) => ({
    name, ...meta, state: state.heroes[name]
  }));

  if (typeF !== 'All') heroes = heroes.filter(h => h.type === typeF);
  if (rarityF !== 'All') heroes = heroes.filter(h => h.rarity === rarityF);
  if (squadF !== 'All') {
    const sq = parseInt(squadF);
    if (squadF === 'Bench') heroes = heroes.filter(h => !h.state || h.state.squad === 0);
    else heroes = heroes.filter(h => h.state && h.state.squad === sq);
  }

  heroes.sort((a, b) => {
    let va, vb;
    switch (currentSort) {
      case 'power': va = estimatePower(a.name); vb = estimatePower(b.name); break;
      case 'level': va = (a.state?.level || 0); vb = (b.state?.level || 0); break;
      case 'name': va = a.name; vb = b.name;
        return sortDir * va.localeCompare(vb);
      case 'squad': va = (a.state?.squad || 99); vb = (b.state?.squad || 99); break;
      default: va = 0; vb = 0;
    }
    return sortDir * ((va > vb ? 1 : va < vb ? -1 : 0));
  });

  return heroes;
}

function renderRoster() {
  const grid = document.getElementById('heroGrid');
  const heroes = getFilteredHeroes();
  const cap = heroLevelCap();
  const gearSlotNames = ['Cannon', 'Shield', 'Chip', 'Radar'];
  const gearIcons = ['\u2694', '\u26e8', '\u2699', '\u{1f4e1}'];

  let html = '';
  for (const h of heroes) {
    const s = h.state || state.heroes[h.name];
    const power = estimatePower(h.name);
    const squadClass = s.squad > 0 ? 'squad-assigned' : 'bench';
    const imgSrc = HERO_IMAGES[h.name]
      ? 'data:image/png;base64,' + HERO_IMAGES[h.name]
      : '';
    const skillCap = STAR_SKILL_CAP[s.stars] || 1;

    html += `<div class="hero-card ${squadClass}" data-hero="${h.name}">
      <div class="hero-card-header">
        ${imgSrc ? `<img class="hero-portrait rarity-${h.rarity}" src="${imgSrc}" alt="${h.name}">` :
          `<div class="hero-portrait rarity-${h.rarity}" style="display:flex;align-items:center;justify-content:center;font-size:24px;background:#f0f0f0;">${h.name[0]}</div>`}
        <div class="hero-info">
          <div class="hero-name-row">
            <span class="hero-name">${h.name}</span>
            <span class="rarity-badge rarity-${h.rarity}">${h.rarity}</span>
          </div>
          <div class="hero-meta">
            <span class="type-icon type-${h.type}">${h.type}</span> &middot; ${h.role}
            ${s.squad > 0 ? ` &middot; <strong>Squad ${s.squad}</strong>` : ''}
          </div>
        </div>
      </div>
      <div class="hero-card-body">
        <div class="field-group">
          <div class="field-label">Level (cap ${cap})</div>
          <div class="field-row">
            <input type="number" min="0" max="${cap}" value="${s.level}"
              onchange="updateHero('${h.name}','level',parseInt(this.value)||0)"
>
          </div>
        </div>
        <div class="field-group">
          <div class="field-label">Stars</div>
          <div class="star-row" data-hero="${h.name}">
            ${[1,2,3,4,5].map(i =>
              `<span class="star ${i <= s.stars ? 'filled' : ''}"
                onclick="updateHero('${h.name}','stars',${i === s.stars ? i-1 : i})">&#9733;</span>`
            ).join('')}
          </div>
        </div>
        <div class="field-group">
          <div class="field-label">Skills (cap Lv${skillCap})</div>
          <div class="skill-inputs">
            ${s.skills.map((sk, i) =>
              `<input type="number" min="1" max="${skillCap}" value="${sk}"
                onchange="updateSkill('${h.name}',${i},parseInt(this.value)||1)"
>`
            ).join('<span class="sep">/</span>')}
          </div>
        </div>
        <div class="field-group">
          <div class="field-label">Gear</div>
          <div class="gear-grid">
            ${[0,1,2,3].map(gi => `
              <div class="gear-slot">
                <span class="gear-icon">${gearIcons[gi]}</span>
                <span style="font-size:10px">${gearSlotNames[gi]}</span>
                <input type="number" min="0" max="40" value="${s.gear[gi].level}"
                  onchange="updateGear('${h.name}',${gi},'level',parseInt(this.value)||0)">
              </div>
            `).join('')}
          </div>
        </div>
        <div class="field-group">
          <div class="field-label">Weapon Lv</div>
          <div class="field-row">
            <input type="number" min="0" max="30" value="${s.weaponLevel}"
              onchange="updateHero('${h.name}','weaponLevel',parseInt(this.value)||0)">
          </div>
        </div>
        <div class="field-group">
          <div class="field-label">Shards</div>
          <div class="field-row">
            <input type="number" min="0" max="9999" value="${s.shards || 0}"
              onchange="updateHero('${h.name}','shards',parseInt(this.value)||0)">
          </div>
        </div>
        <div class="field-group">
          <div class="field-label">Squad</div>
          <div class="field-row">
            <select onchange="updateHero('${h.name}','squad',parseInt(this.value))">
              <option value="0" ${s.squad===0?'selected':''}>Bench</option>
              <option value="1" ${s.squad===1?'selected':''}>Squad 1</option>
              <option value="2" ${s.squad===2?'selected':''}>Squad 2</option>
              <option value="3" ${s.squad===3?'selected':''}>Squad 3</option>
              <option value="4" ${s.squad===4?'selected':''}>Squad 4</option>
            </select>
          </div>
        </div>
      </div>
      <div class="hero-power-est">Power: ~${fmt(power)}</div>
    </div>`;
  }
  grid.innerHTML = html;
  updatePowerDashboard();
}

function updateHero(name, field, value) {
  if (!state.heroes[name]) return;
  const cap = heroLevelCap();
  if (field === 'level') value = Math.max(0, Math.min(cap, value));
  if (field === 'stars') value = Math.max(0, Math.min(5, value));
  state.heroes[name][field] = value;
  saveState();
  if (field === 'squad') {
    renderRoster();
  } else {
    refreshCard(name);
  }
}

function updateSkill(name, idx, value) {
  if (!state.heroes[name]) return;
  const cap = STAR_SKILL_CAP[state.heroes[name].stars] || 1;
  state.heroes[name].skills[idx] = Math.max(1, Math.min(cap, value));
  saveState();
  refreshCard(name);
}

function updateGear(name, slotIdx, field, value) {
  if (!state.heroes[name]) return;
  if (field === 'level') value = Math.max(0, Math.min(40, value));
  if (field === 'stars') value = Math.max(0, Math.min(5, value));
  state.heroes[name].gear[slotIdx][field] = value;
  saveState();
  refreshCard(name);
}

function refreshCard(name) {
  const card = document.querySelector(`.hero-card[data-hero="${name}"]`);
  if (!card) return;
  const power = estimatePower(name);
  const powerEl = card.querySelector('.hero-power-est');
  if (powerEl) powerEl.textContent = 'Power: ~' + fmt(power);
  // Update skill cap display if stars changed
  const s = state.heroes[name];
  if (s) {
    const skillCap = STAR_SKILL_CAP[s.stars] || 1;
    const skillLabel = card.querySelector('.field-group:nth-child(3) .field-label');
    if (skillLabel) skillLabel.textContent = 'Skills (cap Lv' + skillCap + ')';
    // Clamp skill inputs to new cap
    const skillInputs = card.querySelectorAll('.skill-inputs input');
    skillInputs.forEach((inp, i) => {
      inp.max = skillCap;
      if (s.skills[i] > skillCap) {
        s.skills[i] = skillCap;
        inp.value = skillCap;
      }
    });
    // Update star display
    const stars = card.querySelectorAll('.star');
    stars.forEach((star, i) => {
      star.classList.toggle('filled', i < s.stars);
    });
  }
  updatePowerDashboard();
}

function updatePowerDashboard() {
  let sq1 = 0, sq2 = 0, total = 0;
  for (const [name, h] of Object.entries(state.heroes)) {
    const p = estimatePower(name);
    total += p;
    if (h.squad === 1) sq1 += p;
    if (h.squad === 2) sq2 += p;
  }
  document.getElementById('pwrSquad1').textContent = fmt(sq1);
  document.getElementById('pwrSquad2').textContent = fmt(sq2);
  document.getElementById('pwrTotal').textContent = fmt(total);
}

function cycleSort() {
  const sorts = ['power', 'level', 'name', 'squad'];
  const btn = document.getElementById('sortBtn');
  let idx = sorts.indexOf(currentSort);
  idx = (idx + 1) % sorts.length;
  currentSort = sorts[idx];
  sortDir = currentSort === 'name' ? 1 : -1;
  btn.textContent = 'Sort: ' + currentSort.charAt(0).toUpperCase() + currentSort.slice(1);
  renderRoster();
}

/* ===== RENDER: SQUAD VIEW TAB ===== */
let activeSquadView = 1;

function renderSquadView(squadNum) {
  if (squadNum !== undefined) activeSquadView = squadNum;
  const sq = activeSquadView;

  // Update tab buttons
  document.querySelectorAll('.squad-tab-btn').forEach(b => {
    b.classList.toggle('active', parseInt(b.dataset.squad) === sq);
  });

  const members = [];
  for (const [name, h] of Object.entries(state.heroes)) {
    if (h.squad === sq) members.push({ name, ...h, meta: HERO_REGISTRY.heroes[name] });
  }

  const container = document.getElementById('squadViewContent');
  const gearSlotNames = ['Cannon', 'Shield', 'Chip', 'Radar'];

  // Synergy calc
  const typeCounts = {};
  members.forEach(m => {
    if (m.meta) {
      typeCounts[m.meta.type] = (typeCounts[m.meta.type] || 0) + 1;
    }
  });
  const maxType = Object.entries(typeCounts).sort((a,b) => b[1] - a[1])[0];
  const synergyBonus = maxType && maxType[1] === 5 ? 20 : (maxType ? maxType[1] * 4 : 0);
  const fullSynergy = maxType && maxType[1] === 5;

  let html = `<div class="synergy-bar">
    Vehicle Synergy: ${Object.entries(typeCounts).map(([t,c]) => `${t} x${c}`).join(', ') || 'Empty squad'}
    &mdash; <span class="${fullSynergy ? 'bonus' : 'warning'}">
      ${fullSynergy ? '+20% damage bonus!' : synergyBonus > 0 ? `+${synergyBonus}% (need 5 same for +20%)` : 'No heroes assigned'}
    </span>
  </div>`;

  html += '<div class="squad-hero-row">';
  for (let slot = 0; slot < 5; slot++) {
    const m = members[slot];
    if (m) {
      const imgSrc = HERO_IMAGES[m.name] ? 'data:image/png;base64,' + HERO_IMAGES[m.name] : '';
      const power = estimatePower(m.name);
      const avgSkill = (m.skills.reduce((a,b) => a+b, 0) / m.skills.length).toFixed(1);
      const avgGear = (m.gear.reduce((a,g) => a+g.level, 0) / 4).toFixed(0);
      html += `<div class="squad-hero-card">
        <div class="portrait-wrap">
          ${imgSrc ? `<img class="hero-portrait rarity-${m.meta.rarity}" src="${imgSrc}" alt="${m.name}">` :
            `<div class="hero-portrait rarity-${m.meta.rarity}" style="display:flex;align-items:center;justify-content:center;font-size:28px;background:#f0f0f0;width:70px;height:70px;">${m.name[0]}</div>`}
        </div>
        <div class="hero-name">${m.name}</div>
        <span class="rarity-badge rarity-${m.meta.rarity}">${m.meta.rarity}</span>
        <div class="stat-line"><strong>Lv ${m.level}</strong> &middot; ${m.stars} stars</div>
        <div class="stat-line">Skills: ${m.skills.join('/')}</div>
        <div class="stat-line">Gear avg: Lv${avgGear}</div>
        <div class="stat-line">Weapon: Lv${m.weaponLevel}</div>
        <div class="stat-line">Shards: ${m.shards || 0}</div>
        <div class="stat-line" style="color:var(--teal);font-weight:700;">~${fmt(power)}</div>
      </div>`;
    } else {
      html += `<div class="squad-hero-card" style="opacity:0.4;">
        <div class="portrait-wrap"><div class="hero-portrait" style="display:flex;align-items:center;justify-content:center;font-size:28px;background:#f0f0f0;width:70px;height:70px;">?</div></div>
        <div class="hero-name">Empty Slot</div>
        <div class="stat-line">Assign a hero in the Roster tab</div>
      </div>`;
    }
  }
  html += '</div>';

  // Squad summary
  const totalPower = members.reduce((s, m) => s + estimatePower(m.name), 0);
  const avgLevel = members.length ? (members.reduce((s, m) => s + m.level, 0) / members.length).toFixed(0) : 0;

  html += `<div class="squad-summary">
    <h4>Squad ${sq} Summary</h4>
    <div class="row"><span>Total Power</span><strong>${fmt(totalPower)}</strong></div>
    <div class="row"><span>Heroes</span><strong>${members.length}/5</strong></div>
    <div class="row"><span>Avg Level</span><strong>${avgLevel}</strong></div>
  </div>`;

  // Recommendations
  if (members.length > 0) {
    const recs = generateSquadRecs(members);
    if (recs.length > 0) {
      html += `<div class="recommendations"><h4>Recommendations</h4>`;
      for (const rec of recs) {
        html += `<div class="rec-item">
          <div class="rec-action">${rec.action}</div>
          <div class="rec-detail">${rec.detail}</div>
        </div>`;
      }
      html += '</div>';
    }
  }

  container.innerHTML = html;
}

function generateSquadRecs(members) {
  const recs = [];
  const cap = heroLevelCap();
  const slotNames = ['Cannon', 'Shield', 'Chip', 'Radar'];

  // Weakest link by level
  const lowest = members.reduce((min, m) => m.level < min.level ? m : min, members[0]);
  const highest = members.reduce((max, m) => m.level > max.level ? m : max, members[0]);
  if (highest.level - lowest.level > 3) {
    recs.push({
      action: `Level up ${lowest.name} (Lv${lowest.level})`,
      detail: `${highest.level - lowest.level} levels behind ${highest.name}. Equalizing levels gives more power per XP.`
    });
  }

  // Next level cost for lowest hero
  if (lowest.level < cap) {
    const nextCost = COST_DATA.xpTable[String(lowest.level)];
    if (nextCost) {
      recs.push({
        action: `Next level-up: ${lowest.name} Lv${lowest.level} → ${lowest.level + 1}`,
        detail: `Costs ${fmt(nextCost)} XP.`
      });
    }
  }

  // Skill upgrade opportunities (skills below star cap)
  for (const m of members) {
    const skillCap = STAR_SKILL_CAP[m.stars] || 1;
    const belowCap = m.skills.map((s, i) => ({ skill: i + 1, lv: s, gap: skillCap - s })).filter(x => x.gap > 0);
    if (belowCap.length > 0) {
      const worst = belowCap.sort((a, b) => b.gap - a.gap)[0];
      const rarity = HERO_REGISTRY.heroes[m.name]?.rarity || 'UR';
      const table = COST_DATA.skillMedals[rarity];
      const cost = table && worst.lv >= 1 && (worst.lv - 1) < table.length ? table[worst.lv - 1] : null;
      recs.push({
        action: `${m.name} Skill ${worst.skill}: Lv${worst.lv} → ${worst.lv + 1}`,
        detail: `${worst.gap} levels below cap (Lv${skillCap}).${cost ? ' Costs ' + fmtN(cost) + ' medals.' : ''}`
      });
    }
  }

  // Skill cap warnings — suggest star up
  for (const m of members) {
    const skillCap = STAR_SKILL_CAP[m.stars] || 1;
    const atCap = m.skills.filter(s => s >= skillCap).length;
    if (atCap === m.skills.length && m.stars < 5) {
      recs.push({
        action: `Star up ${m.name} (${m.stars}★ → ${m.stars + 1}★)`,
        detail: `All skills at cap Lv${skillCap}. Needs ${STAR_SHARD_COST[m.stars]} shards to unlock higher skill levels.`
      });
    }
  }

  // Gear imbalance (compare each hero's slots to their highest slot)
  for (const m of members) {
    const meta = HERO_REGISTRY.heroes[m.name];
    if (!meta) continue;
    const gearLevels = m.gear.map(g => g.level);
    const maxGear = Math.max(...gearLevels);
    const minGear = Math.min(...gearLevels);
    const gap = maxGear - minGear;
    if (gap > 5 && maxGear >= 10) {
      const minIdx = gearLevels.indexOf(minGear);
      recs.push({
        action: `${m.name}: ${slotNames[minIdx]} Lv${minGear} (${gap} levels behind highest)`,
        detail: `Highest slot is Lv${maxGear}. ${meta.role === 'DPS' ? 'DPS priority: Cannon > Chip > Shield > Radar.' : meta.role === 'Buffer' ? 'Buffer priority: Radar > Chip > Shield > Cannon.' : 'Defense priority: Shield > Radar > Cannon > Chip.'}`
      });
    } else if (minGear < 10 && m.level >= 50) {
      const minIdx = gearLevels.indexOf(minGear);
      recs.push({
        action: `Upgrade ${m.name}'s ${slotNames[minIdx]} (Lv${minGear})`,
        detail: `Lowest gear slot. ${meta.role === 'DPS' ? 'DPS heroes need Cannon+Chip first.' : 'Defense heroes need Shield+Radar first.'}`
      });
    }
  }

  return recs.slice(0, 8);
}

/* ===== RENDER: PLANNER TAB ===== */
function updateShardInventory() {
  const squadNum = parseInt(document.getElementById('planSquad').value);
  const container = document.getElementById('shardInventory');
  const members = [];
  for (const [name, h] of Object.entries(state.heroes)) {
    if (h.squad === squadNum) members.push({ name, shards: h.shards || 0, stars: h.stars || 0 });
  }
  if (members.length === 0) { container.innerHTML = ''; return; }

  let html = '<h4>Hero-Specific Shards (editable, synced with Roster)</h4>';
  for (const m of members) {
    const needed = m.stars < 5 ? STAR_SHARD_COST[m.stars] : 0;
    html += `<div class="shard-hero">
      <span class="name">${m.name}</span>
      <input type="number" min="0" value="${m.shards}"
        onchange="updateHero('${m.name}','shards',parseInt(this.value)||0); updateShardInventory();">
      ${needed > 0 ? `<span style="color:#999;font-size:10px;">(need ${needed} for ${m.stars+1}\u2605)</span>` : '<span style="color:var(--green);font-size:10px;">MAX\u2605</span>'}
    </div>`;
  }
  container.innerHTML = html;
}

function renderStep(s, num) {
  return `<div class="plan-step ${s.highlight ? 'highlight' : ''}">
    <div class="step-num">Step ${num}</div>
    <div class="step-action">${s.action}</div>
    <div class="step-cost">${s.cost}</div>
    ${s.pts > 0 ? `<div class="step-pts">+${fmtN(s.pts)} pts</div>` : ''}
  </div>`;
}

function generatePlan() {
  const squadNum = parseInt(document.getElementById('planSquad').value);
  const xpBudget = parseInt(document.getElementById('planXP').value) || 0;
  const medalBudget = parseInt(document.getElementById('planMedals').value) || 0;
  const universalShards = parseInt(document.getElementById('planShards').value) || 0;
  const thursdayMode = document.getElementById('thursdayMode').checked;
  const cap = heroLevelCap();

  const members = [];
  for (const [name, h] of Object.entries(state.heroes)) {
    if (h.squad === squadNum) {
      members.push({
        name, ...JSON.parse(JSON.stringify(h)),
        heroShards: h.shards || 0,
        meta: HERO_REGISTRY.heroes[name]
      });
    }
  }

  if (members.length === 0) {
    document.getElementById('planOutput').innerHTML = '<div class="rec-item"><div class="rec-action">No heroes in Squad ' + squadNum + '</div><div class="rec-detail">Assign heroes in the Roster tab first.</div></div>';
    return;
  }

  const steps = [];
  let xpLeft = xpBudget;
  let medalsLeft = medalBudget;
  let uniShardsLeft = universalShards;
  let totalPts = 0;

  // ========== PHASE 1: STAR UPGRADES (first — unlocks higher skill caps) ==========
  const starOrder = [...members].sort((a, b) => a.stars - b.stars);
  for (const m of starOrder) {
    while (m.stars < 5) {
      const cost = STAR_SHARD_COST[m.stars];
      const fromHero = Math.min(m.heroShards, cost);
      const fromUni = cost - fromHero;
      if (fromUni > uniShardsLeft) break;

      m.heroShards -= fromHero;
      uniShardsLeft -= fromUni;
      const sources = [];
      if (fromHero > 0) sources.push(fromHero + ' ' + m.name);
      if (fromUni > 0) sources.push(fromUni + ' universal');

      steps.push({
        action: `Star up ${m.name} ${m.stars}\u2605 \u2192 ${m.stars + 1}\u2605`,
        cost: `${cost} shards (${sources.join(' + ')})`,
        pts: 0,
        type: 'star',
        highlight: true
      });
      m.stars++;
    }
  }

  // ========== PHASE 2: SKILL UPGRADES (cheapest first, loop until medals exhausted) ==========
  let keepUpgrading = true;
  while (keepUpgrading && medalsLeft > 0) {
    keepUpgrading = false;
    let cheapest = null;

    for (const m of members) {
      const rarity = m.meta?.rarity || 'UR';
      const skillCap = STAR_SKILL_CAP[m.stars] || 1;
      const table = COST_DATA.skillMedals[rarity];
      if (!table) continue;
      for (let si = 0; si < m.skills.length; si++) {
        if (m.skills[si] < skillCap) {
          const idx = m.skills[si] - 1;
          if (idx >= 0 && idx < table.length) {
            const cost = table[idx];
            if (cost <= medalsLeft && (!cheapest || cost < cheapest.cost)) {
              cheapest = { name: m.name, skillIdx: si, fromLv: m.skills[si], cost, member: m };
            }
          }
        }
      }
    }

    if (cheapest) {
      medalsLeft -= cheapest.cost;
      const pts = thursdayMode ? Math.floor(cheapest.cost / 2) : 0;
      totalPts += pts;
      steps.push({
        action: `${cheapest.name} Skill ${cheapest.skillIdx + 1}: Lv${cheapest.fromLv} \u2192 ${cheapest.fromLv + 1}`,
        cost: `${fmtN(cheapest.cost)} medals`,
        pts: pts,
        type: 'skill'
      });
      cheapest.member.skills[cheapest.skillIdx]++;
      keepUpgrading = true;
    }
  }

  // ========== PHASE 3: LEVEL-UPS (round-robin, lowest first) ==========
  let leveling = true;
  while (leveling && xpLeft > 0) {
    members.sort((a, b) => a.level - b.level);
    const lowest = members[0];
    if (lowest.level >= cap) break;

    const cost = COST_DATA.xpTable[String(lowest.level)];
    if (!cost || cost > xpLeft) { leveling = false; break; }

    xpLeft -= cost;
    const pts = thursdayMode ? Math.floor(cost / 2000) : 0;
    totalPts += pts;
    steps.push({
      action: `Level ${lowest.name} Lv${lowest.level} \u2192 ${lowest.level + 1}`,
      cost: `${fmt(cost)} XP`,
      pts: pts,
      type: 'level'
    });
    lowest.level++;
  }

  // ========== RENDER ==========
  let html = '';
  if (steps.length === 0) {
    let hints = [];
    const levelable = members.filter(m => m.level < cap);
    if (levelable.length > 0) {
      const cheapestLvl = levelable
        .map(m => ({ name: m.name, level: m.level, cost: COST_DATA.xpTable[String(m.level)] || 0 }))
        .filter(x => x.cost > 0)
        .sort((a, b) => a.cost - b.cost)[0];
      if (cheapestLvl) {
        hints.push(`<div class="rec-item"><div class="rec-action">Cheapest level-up: ${cheapestLvl.name} Lv${cheapestLvl.level} \u2192 ${cheapestLvl.level + 1}</div><div class="rec-detail">Costs ${fmt(cheapestLvl.cost)} XP. At Lv${cheapestLvl.level}+, each level = ${fmt(cheapestLvl.cost)} XP.</div></div>`);
      }
    }
    const skillCandidates = members.flatMap(m => {
      const skillCap = STAR_SKILL_CAP[m.stars] || 1;
      const table = COST_DATA.skillMedals[m.meta?.rarity || 'UR'];
      if (!table) return [];
      return m.skills.map((s, i) => s < skillCap && s >= 1 && (s - 1) < table.length ? { name: m.name, skill: i + 1, fromLv: s, cost: table[s - 1] } : null).filter(Boolean);
    }).sort((a, b) => a.cost - b.cost);
    if (skillCandidates.length > 0) {
      const cs = skillCandidates[0];
      hints.push(`<div class="rec-item"><div class="rec-action">Cheapest skill upgrade: ${cs.name} Skill ${cs.skill} Lv${cs.fromLv} \u2192 ${cs.fromLv + 1}</div><div class="rec-detail">Costs ${fmtN(cs.cost)} medals.</div></div>`);
    }
    const starCandidates = members
      .filter(m => m.stars < 5)
      .map(m => {
        const totalAvail = (m.heroShards || 0) + uniShardsLeft;
        return { name: m.name, stars: m.stars, cost: STAR_SHARD_COST[m.stars], avail: totalAvail };
      })
      .sort((a, b) => a.cost - b.cost);
    if (starCandidates.length > 0) {
      const sc = starCandidates[0];
      hints.push(`<div class="rec-item"><div class="rec-action">Cheapest star-up: ${sc.name} ${sc.stars}\u2605 \u2192 ${sc.stars + 1}\u2605</div><div class="rec-detail">Costs ${sc.cost} shards (you have ${sc.avail} available: hero + universal).</div></div>`);
    }
    if (hints.length > 0) {
      html = `<div class="plan-info-box"><h4>Budget insufficient \u2014 here\u2019s what upgrades cost:</h4>${hints.join('')}</div>`;
    } else {
      html = '<div class="rec-item"><div class="rec-action">All heroes maxed!</div><div class="rec-detail">Squad is at maximum level, stars, and skills.</div></div>';
    }
  } else {
    const starSteps = steps.filter(s => s.type === 'star');
    const skillSteps = steps.filter(s => s.type === 'skill');
    const levelSteps = steps.filter(s => s.type === 'level');
    let stepNum = 0;

    if (starSteps.length > 0) {
      html += '<div class="phase-header">Phase 1: Star Upgrades</div>';
      for (const s of starSteps) { stepNum++; html += renderStep(s, stepNum); }
    }
    if (skillSteps.length > 0) {
      html += '<div class="phase-header">Phase 2: Skill Upgrades</div>';
      for (const s of skillSteps) { stepNum++; html += renderStep(s, stepNum); }
    }
    if (levelSteps.length > 0) {
      html += '<div class="phase-header">Phase 3: Level-Ups</div>';
      for (const s of levelSteps) { stepNum++; html += renderStep(s, stepNum); }
    }
  }

  // ========== SUMMARY ==========
  const levelsGained = steps.filter(s => s.type === 'level').length;
  const skillsGained = steps.filter(s => s.type === 'skill').length;
  const starsGained = steps.filter(s => s.type === 'star').length;

  // Leftover explanations
  let leftovers = [];
  if (xpLeft > 0 && steps.length > 0) {
    const lowestAfter = [...members].sort((a,b) => a.level - b.level)[0];
    if (lowestAfter.level >= cap) {
      leftovers.push('XP: ' + fmt(xpLeft) + ' remaining \u2014 all heroes at level cap (' + cap + ')');
    } else {
      const nextCost = COST_DATA.xpTable[String(lowestAfter.level)];
      if (nextCost) leftovers.push('XP: ' + fmt(xpLeft) + ' remaining \u2014 next level (' + lowestAfter.name + ' Lv' + lowestAfter.level + '\u2192' + (lowestAfter.level+1) + ') costs ' + fmt(nextCost));
    }
  }
  if (medalsLeft > 0 && steps.length > 0) {
    const anyUpgradeable = members.some(m => {
      const skillCap = STAR_SKILL_CAP[m.stars] || 1;
      return m.skills.some(s => s < skillCap);
    });
    if (!anyUpgradeable) {
      const needsStar = members.find(m => m.stars < 5);
      leftovers.push('Medals: ' + fmtN(medalsLeft) + ' remaining \u2014 all skills at star cap' + (needsStar ? '. Star up to unlock higher caps!' : ''));
    } else {
      let cheapestRemaining = Infinity;
      for (const m of members) {
        const table = COST_DATA.skillMedals[m.meta?.rarity || 'UR'];
        const skillCap = STAR_SKILL_CAP[m.stars] || 1;
        if (!table) continue;
        for (const s of m.skills) {
          if (s < skillCap && (s-1) < table.length) cheapestRemaining = Math.min(cheapestRemaining, table[s-1]);
        }
      }
      if (cheapestRemaining < Infinity) leftovers.push('Medals: ' + fmtN(medalsLeft) + ' remaining \u2014 next skill costs ' + fmtN(cheapestRemaining));
    }
  }
  if (uniShardsLeft > 0 && steps.length > 0) {
    const needsStar = members.find(m => m.stars < 5);
    if (needsStar) {
      leftovers.push('Universal shards: ' + uniShardsLeft + ' remaining \u2014 ' + needsStar.name + ' needs ' + STAR_SHARD_COST[needsStar.stars] + ' total for next star');
    } else {
      leftovers.push('Universal shards: ' + uniShardsLeft + ' remaining \u2014 all heroes at 5\u2605');
    }
  }

  if (steps.length > 0) {
    html += `<div class="plan-summary">
      <h4>Plan Summary</h4>
      <div class="row"><span>Star-ups</span><strong>${starsGained}</strong></div>
      <div class="row"><span>Skill upgrades</span><strong>${skillsGained}</strong></div>
      <div class="row"><span>Level-ups</span><strong>${levelsGained}</strong></div>
      <div class="row"><span>XP remaining</span><strong>${fmt(xpLeft)}</strong></div>
      <div class="row"><span>Medals remaining</span><strong>${fmtN(medalsLeft)}</strong></div>
      <div class="row"><span>Universal shards remaining</span><strong>${uniShardsLeft}</strong></div>
      ${thursdayMode ? `<div class="row total"><span>Est. Thursday Points</span><strong>${fmtN(totalPts)}</strong></div>` : ''}
    </div>`;
  }

  if (leftovers.length > 0) {
    html += '<div class="plan-leftovers"><h4>Why resources remain</h4>';
    for (const l of leftovers) html += '<div class="leftover-line">' + l + '</div>';
    html += '</div>';
  }

  document.getElementById('planOutput').innerHTML = html;
}

/* ===== CSV EXPORT / IMPORT ===== */
function exportCSV() {
  const lines = ['Hero,Rarity,Type,Role,Level,Stars,Skill1,Skill2,Skill3,GearCannon,GearShield,GearChip,GearRadar,WeaponLv,Squad,Shards'];
  for (const [name, meta] of Object.entries(HERO_REGISTRY.heroes)) {
    const h = state.heroes[name] || {};
    const skills = h.skills || [1,1,1];
    const gear = h.gear || [{level:0},{level:0},{level:0},{level:0}];
    lines.push([
      name, meta.rarity, meta.type, meta.role,
      h.level || 0, h.stars || 0,
      skills[0], skills[1], skills[2],
      gear[0].level, gear[1].level, gear[2].level, gear[3].level,
      h.weaponLevel || 0, h.squad || 0, h.shards || 0
    ].join(','));
  }

  const header = `# OWOW Hero Planner Export\n# HQ: ${state.hqLevel} | VIP: ${state.vipLevel}\n# Date: ${new Date().toISOString().split('T')[0]}\n`;
  const csv = header + lines.join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'owow_hero_planner.csv';
  a.click();
  URL.revokeObjectURL(url);
  toast('CSV exported!');
}

function importCSV() {
  document.getElementById('csvFileInput').click();
}

function handleCSVImport(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    const lines = e.target.result.split('\n').filter(l => l.trim() && !l.startsWith('#'));
    const headerLine = lines.shift();
    if (!headerLine) return;

    for (const line of lines) {
      const cols = line.split(',');
      if (cols.length < 15) continue;
      const name = cols[0].trim();
      if (!HERO_REGISTRY.heroes[name]) continue;

      state.heroes[name] = {
        level: parseInt(cols[4]) || 0,
        stars: parseInt(cols[5]) || 0,
        skills: [parseInt(cols[6]) || 1, parseInt(cols[7]) || 1, parseInt(cols[8]) || 1],
        gear: [
          { level: parseInt(cols[9]) || 0, stars: 0 },
          { level: parseInt(cols[10]) || 0, stars: 0 },
          { level: parseInt(cols[11]) || 0, stars: 0 },
          { level: parseInt(cols[12]) || 0, stars: 0 }
        ],
        weaponLevel: parseInt(cols[13]) || 0,
        squad: parseInt(cols[14]) || 0,
        shards: cols.length > 15 ? (parseInt(cols[15]) || 0) : 0
      };
    }
    saveState();
    renderRoster();
    renderSquadView();
    toast('CSV imported! ' + lines.length + ' heroes loaded.');
  };
  reader.readAsText(file);
  event.target.value = '';
}

function resetAll() {
  if (!confirm('Reset all hero data? This cannot be undone.')) return;
  localStorage.removeItem(LS_KEY);
  state = { hqLevel: 24, vipLevel: 13, heroes: {} };
  initState();
  document.getElementById('hqSelect').value = 24;
  document.getElementById('vipSelect').value = 13;
  renderRoster();
  renderSquadView();
  toast('All data reset.');
}

/* ===== TAB SWITCHING ===== */
function switchTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tabName));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.toggle('active', c.id === 'tab-' + tabName));
  if (tabName === 'squad') renderSquadView();
  if (tabName === 'roster') renderRoster();
  if (tabName === 'planner') updateShardInventory();
}

/* ===== INIT ===== */
function init() {
  initState();
  loadState();

  // Set commander bar values
  const hqSel = document.getElementById('hqSelect');
  const vipSel = document.getElementById('vipSelect');
  hqSel.value = state.hqLevel;
  vipSel.value = state.vipLevel;
  hqSel.onchange = function() { state.hqLevel = parseInt(this.value); saveState(); renderRoster(); };
  vipSel.onchange = function() { state.vipLevel = parseInt(this.value); saveState(); };

  // Filter handlers
  document.getElementById('filterType').onchange = renderRoster;
  document.getElementById('filterRarity').onchange = renderRoster;
  document.getElementById('filterSquad').onchange = renderRoster;

  // Tab handlers
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.onclick = () => switchTab(b.dataset.tab);
  });

  // Squad view tabs
  document.querySelectorAll('.squad-tab-btn').forEach(b => {
    b.onclick = () => renderSquadView(parseInt(b.dataset.squad));
  });

  renderRoster();
}

window.addEventListener('DOMContentLoaded', init);
'''


def generate_html(registry, cost_data, images):
    css = generate_css()
    js = generate_js(cost_data, registry, images)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hero Planner - OWOW</title>
{css}
</head>
<body>

<nav class="guide-nav">
  <a href="../" class="nav-home">&#8592; Home</a>
  <a href="alliance_support_hub.html">Alliance Hub</a>
  <a href="building_planner.html">Building Planner</a>
  <a href="building_reference.html">Building Ref</a>
  <a href="capitol_positions.html">Capitol Positions</a>
  <a href="chip_lab_guide.html">Chip Lab</a>
  <a href="calendar.html">Calendar</a>
  <a href="hero_planner.html" class="current">Hero Planner</a>
  <a href="plunder_guide.html">Plunder</a>
  <a href="radar_guide.html">Radar</a>
  <a href="../research_trees_visual.html">Research Trees</a>
  <a href="server_dashboard.html">Server</a>
  <a href="vs_weekly_planner.html">VS Planner</a>
  <a href="waterfall_guide.html">Waterfall</a>
</nav>

<div class="top-bar">
  <div>
    <h1>Hero Planner</h1>
    <div class="sub">Last War: Survival</div>
  </div>
  <div class="alliance">
    <div class="name">[OWOW]</div>
    <div class="info">Old World Order</div>
  </div>
</div>

<div class="commander-bar">
  <label>HQ Level:
    <select id="hqSelect">
      {"".join(f'<option value="{i}">{i}</option>' for i in range(1, 36))}
    </select>
  </label>
  <label>VIP Level:
    <select id="vipSelect">
      {"".join(f'<option value="{i}">VIP {i}</option>' for i in range(0, 16))}
    </select>
  </label>
</div>

<div class="power-dashboard">
  <div class="power-card pc-squad1">
    <div class="label">Squad 1 Power</div>
    <div class="value" id="pwrSquad1">0</div>
  </div>
  <div class="power-card pc-squad2">
    <div class="label">Squad 2 Power</div>
    <div class="value" id="pwrSquad2">0</div>
  </div>
  <div class="power-card pc-total">
    <div class="label">Total Hero Power</div>
    <div class="value" id="pwrTotal">0</div>
  </div>
</div>

<div class="tab-bar">
  <button class="tab-btn active" data-tab="roster">Hero Roster</button>
  <button class="tab-btn" data-tab="squad">Squad View</button>
  <button class="tab-btn" data-tab="planner">Upgrade Planner</button>
</div>

<!-- TAB 1: ROSTER -->
<div class="tab-content active" id="tab-roster">
  <div class="filter-bar">
    <label>Type:
      <select id="filterType">
        <option>All</option><option>Aircraft</option><option>Tank</option><option>Missile</option>
      </select>
    </label>
    <label>Rarity:
      <select id="filterRarity">
        <option>All</option><option>UR</option><option>SSR</option><option>SR</option>
      </select>
    </label>
    <label>Squad:
      <select id="filterSquad">
        <option>All</option><option value="1">Squad 1</option><option value="2">Squad 2</option>
        <option value="3">Squad 3</option><option value="4">Squad 4</option><option value="Bench">Bench</option>
      </select>
    </label>
    <button class="sort-btn" id="sortBtn" onclick="cycleSort()">Sort: Power</button>
  </div>
  <div class="hero-grid" id="heroGrid"></div>
</div>

<!-- TAB 2: SQUAD VIEW -->
<div class="tab-content" id="tab-squad">
  <div class="squad-tabs">
    <button class="squad-tab-btn active" data-squad="1">Squad 1</button>
    <button class="squad-tab-btn" data-squad="2">Squad 2</button>
    <button class="squad-tab-btn" data-squad="3">Squad 3</button>
    <button class="squad-tab-btn" data-squad="4">Squad 4</button>
  </div>
  <div id="squadViewContent"></div>
</div>

<!-- TAB 3: UPGRADE PLANNER -->
<div class="tab-content" id="tab-planner">
  <div class="thursday-toggle" onclick="document.getElementById('thursdayMode').click()">
    <input type="checkbox" id="thursdayMode">
    <div>
      <div class="label">Thursday Mode</div>
      <div class="info">Optimize for Thursday VS scoring (1pt per 2,000 XP)</div>
    </div>
  </div>
  <div class="planner-controls">
    <div class="planner-field">
      <label>Squad</label>
      <select id="planSquad" onchange="updateShardInventory()">
        <option value="1">Squad 1</option><option value="2">Squad 2</option>
        <option value="3">Squad 3</option><option value="4">Squad 4</option>
      </select>
    </div>
    <div class="planner-field">
      <label>Hero XP</label>
      <input type="number" id="planXP" min="0" value="0" placeholder="e.g. 1300000000">
      <div class="helper-text" id="xpHelper">Lv100→101 = 35M, Lv110→111 = 51M, Lv120→121 = 75M</div>
    </div>
    <div class="planner-field">
      <label>Skill Medals</label>
      <input type="number" id="planMedals" min="0" value="0" placeholder="e.g. 5000">
    </div>
    <div class="planner-field">
      <label>Universal Shards</label>
      <input type="number" id="planShards" min="0" value="0" placeholder="e.g. 100">
      <div class="helper-text">Shared across all heroes</div>
    </div>
  </div>
  <div class="shard-inventory" id="shardInventory"></div>
  <div class="action-bar">
    <button class="action-btn btn-generate" onclick="generatePlan()">Generate Plan</button>
  </div>
  <div class="plan-output" id="planOutput"></div>
</div>

<div class="action-bar">
  <button class="action-btn btn-export" onclick="exportCSV()">Export CSV</button>
  <button class="action-btn btn-import" onclick="importCSV()">Import CSV</button>
  <button class="action-btn btn-reset" onclick="resetAll()">Reset</button>
</div>
<input type="file" id="csvFileInput" accept=".csv" onchange="handleCSVImport(event)">

<div class="footer">
  <div class="tagline">Kristen OWOW SKYNET. Ready for Judgment Day.</div>
  <div>Hero Planner v1.0 | Data: cpt-hedge.com</div>
</div>

<div class="toast" id="toast"></div>

<script>
{js}
</script>
</body>
</html>'''


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Load data
    registry = load_json(os.path.join(base_dir, 'hero_registry.json'))
    all_data = load_json(os.path.join(base_dir, 'cpt_hedge_all_data.json'))
    supplemental = load_json(os.path.join(base_dir, 'cpt_hedge_supplemental.json'))

    # Load hero images
    image_dir = os.path.join(base_dir, 'pictures', 'all_heros')
    images = load_hero_images(registry, image_dir)
    print(f"Loaded {len(images)} hero images")

    # Build cost data
    cost_data = build_cost_data(all_data, supplemental)
    print(f"XP table: {len(cost_data['xpTable'])} levels")
    print(f"Skill medals: UR={len(cost_data['skillMedals']['UR'])}, SSR={len(cost_data['skillMedals']['SSR'])}, SR={len(cost_data['skillMedals']['SR'])}")

    # Generate HTML
    html = generate_html(registry, cost_data, images)

    # Write output
    output_path = os.path.join(base_dir, 'guides', 'hero_planner.html')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated: {output_path} ({len(html):,} bytes)")


if __name__ == '__main__':
    main()
