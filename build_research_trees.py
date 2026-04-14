#!/usr/bin/env python3
"""Generate research_trees_visual.html — interactive research tree visualizer.

Reads tree_data/*.json + research_trees.csv, outputs a self-contained HTML page
with all 11 research trees laid out in two horizontal bands, SVG connection lines,
and hover tooltips showing costs/prerequisites/progress.
"""

import json
import csv
import os
import sys
import html as html_mod

# === CONFIGURATION ===

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TREE_DIR = os.path.join(SCRIPT_DIR, 'tree_data')
CSV_FILE = os.path.join(SCRIPT_DIR, 'research_trees.csv')
OUTPUT = os.path.join(SCRIPT_DIR, 'research_trees_visual.html')
RECOMMENDED_PATH_FILE = os.path.join(SCRIPT_DIR, 'recommended_path.json')

BAND1 = ['alliance-duel', 'defense-fortifications', 'siege-to-seize',
         'intercity-truck', 'special-forces']
BAND2 = ['development', 'hero', 'squad-1', 'squad-2', 'squad-3', 'squad-4']

DISPLAY_NAMES = {
    'alliance-duel': 'Alliance Duel',
    'defense-fortifications': 'Defense Fort',
    'siege-to-seize': 'Siege to Seize',
    'intercity-truck': 'Intercity Truck',
    'special-forces': 'Special Forces',
    'development': 'Development',
    'hero': 'Hero',
    'squad-1': 'Squad 1',
    'squad-2': 'Squad 2',
    'squad-3': 'Squad 3',
    'squad-4': 'Squad 4',
}

# Abbreviation rules — applied in order (multi-word first, then single-word)
ABBREV_RULES = [
    # Multi-word (longest/most specific first)
    ("Incentive - Secret Mobile Squad", "Inc. SMS"),
    ("Incentive - Survivor Recruit", "Inc. Surv.R"),
    ("Incentive - Intercity Trade", "Inc. IC Trade"),
    ("Incentive - Enemy Kills", "Inc. E.Kills"),
    ("Incentive - Recruitment", "Inc. Recruit"),
    ("Incentive - Speed-up", "Inc. Speedup"),
    ("Incentive - ", "Inc. "),
    ("Rapid Field Dressing", "Rapid FD"),
    ("Physical Suppression", "Phys. Supp."),
    ("Vigilant Formation", "Vig. Form."),
    ("Defense Fortifications", "Def. Fort."),
    ("Drill Ground", "DG"),
    ("Hold the Line", "Hold Line"),
    ("Counter Defense", "Ctr. Def."),
    ("Solid Defense", "Solid Def."),
    ("Reindeer Sleigh Ride", "Sleigh Ride"),
    # Single-word replacements
    ("Expansion", "Exp."),
    ("Enhancement", "Enh."),
    ("Fortification", "Fort."),
    ("Training", "Trn."),
    ("Suppression", "Supp."),
    ("Resistance", "Res."),
    ("Exploration", "Expl."),
    ("Craftsman", "Craft."),
    ("Terminator", "Term."),
    ("Infirmary", "Inf."),
    ("Barracks", "Barr."),
    ("Barrack", "Barr."),
    ("Precision", "Prec."),
    ("Targeting", "Targ."),
    ("Aircraft", "Air."),
    ("Airborne", "Air."),
    ("Missile", "Miss."),
    ("Formation", "Form."),
]


def abbreviate(name):
    """Apply abbreviation rules to shorten node display names."""
    result = name
    for pattern, replacement in ABBREV_RULES:
        result = result.replace(pattern, replacement)
    return result

# === DATA LOADING ===

def load_trees():
    trees = {}
    for fname in os.listdir(TREE_DIR):
        if fname.endswith('.json'):
            with open(os.path.join(TREE_DIR, fname), encoding='utf-8') as f:
                trees[fname[:-5]] = json.load(f)
    return trees


def load_csv():
    """Load CSV progress, priority, and notes data."""
    progress = {}   # (tree_name, node_name) → current_level
    priority = {}   # (tree_name, node_name) → 'S'/'A'/'B'/'C'
    notes = {}      # (tree_name, node_name) → first non-empty note
    with open(CSV_FILE, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            k = (row['Tree'], row['Node'])
            lv = int(row['Level'])
            if int(row['HaveIt']) == 1:
                progress[k] = max(progress.get(k, 0), lv)
            elif k not in progress:
                progress[k] = 0
            if k not in priority and row.get('Priority', '').strip():
                priority[k] = row['Priority'].strip()
            if k not in notes and row.get('Notes', '').strip():
                notes[k] = row['Notes'].strip()
    return progress, priority, notes


def load_recommended_path():
    """Load recommended research path from JSON."""
    if not os.path.exists(RECOMMENDED_PATH_FILE):
        return []
    with open(RECOMMENDED_PATH_FILE, encoding='utf-8') as f:
        return json.load(f)


# === PROCESSING ===

def build_element_map(tree):
    emap = {}
    for row in tree['rows']:
        for el in row['elements']:
            emap[el['id']] = el
    return emap


def get_node_state(element, current_level, emap, progress, tree_name):
    if current_level >= element['maxLevel']:
        return 'maxed'
    # Get requirements for the NEXT level (levels array is 0-indexed)
    next_idx = current_level
    reqs = element['levels'][next_idx].get('requirements', []) if next_idx < len(element['levels']) else []
    if current_level > 0:
        for req in reqs:
            if req.get('external'):
                return 'progress'
            req_el = emap.get(req['elementId'])
            if not req_el:
                return 'progress'
            req_k = (tree_name, req_el['name'])
            if progress.get(req_k, 0) < req['minLevel']:
                return 'blocked'
        return 'progress'
    # Level 0: check if can start
    for req in reqs:
        if req.get('external'):
            return 'locked'
        req_el = emap.get(req['elementId'])
        if not req_el:
            return 'locked'
        req_k = (tree_name, req_el['name'])
        if progress.get(req_k, 0) < req['minLevel']:
            return 'locked'
    return 'available'


def get_line_state(from_state, to_state):
    if to_state == 'maxed':
        return 'done'
    if to_state in ('progress', 'available', 'blocked'):
        return 'next'
    return 'locked'


def process_tree(tree_key, tree, progress, priority_map, notes_map):
    tree_name = tree['name']
    emap = build_element_map(tree)
    max_width = max(len(r['elements']) for r in tree['rows'])

    # All nodes start at level 0 — users load their own progress via Import CSV
    # (CSV HaveIt data is personal; the published HTML must start fresh for all visitors)
    levels = {}
    for eid, el in emap.items():
        levels[eid] = 0

    # Compute states
    states = {}
    for eid, el in emap.items():
        states[eid] = get_node_state(el, levels[eid], emap, progress, tree_name)

    # Tree stats
    total = sum(el['maxLevel'] for el in emap.values())
    done = sum(levels[eid] for eid in emap)
    pct = round(done / total * 100) if total else 0

    # Flatten connections (raw from/to for JS recomputation)
    conns = []
    for row in tree['rows']:
        for c in row.get('connections', []):
            for to_id in c['to']:
                conns.append({'from': c['from'], 'to': to_id})

    # Track which row each element belongs to
    row_map = {}
    for ri, row in enumerate(tree['rows']):
        for el in row['elements']:
            row_map[el['id']] = ri + 1

    # Full node data for JS (supports live updates)
    nodes_js = {}
    for eid, el in emap.items():
        k = (tree_name, el['name'])
        cur = levels[eid]

        # Full per-level cost array (including per-level requirements)
        lv_costs = []
        for lv_data in el['levels']:
            lv_reqs = []
            for req in lv_data.get('requirements', []):
                if req.get('external'):
                    lv_reqs.append({'elementId': req['elementId'], 'minLevel': 0, 'external': True})
                else:
                    lv_reqs.append({'elementId': req['elementId'], 'minLevel': req['minLevel']})
            entry = {
                'level': lv_data['level'],
                'gold': lv_data.get('gold', 0),
                'food': lv_data.get('food', 0),
                'iron': lv_data.get('iron', 0),
                'valor': lv_data.get('valor', 0),
            }
            if lv_reqs:
                entry['requirements'] = lv_reqs
            lv_costs.append(entry)

        # Raw requirements from level 1
        requirements = []
        if el['levels']:
            for req in el['levels'][0].get('requirements', []):
                if req.get('external'):
                    requirements.append({
                        'elementId': req['elementId'],
                        'minLevel': 0,
                        'external': True,
                    })
                else:
                    requirements.append({
                        'elementId': req['elementId'],
                        'minLevel': req['minLevel'],
                    })

        nodes_js[eid] = {
            'name': el['name'],
            'abbrev': abbreviate(el['name']),
            'maxLevel': el['maxLevel'],
            'currentLevel': cur,
            'state': states[eid],
            'row': row_map.get(eid, 0),
            'levels': lv_costs,
            'requirements': requirements,
            'priority': priority_map.get(k, ''),
            'notes': notes_map.get(k, ''),
        }

    return {
        'tree_name': tree_name,
        'max_width': max_width,
        'stats': {'total': total, 'done': done, 'pct': pct},
        'connections': conns,
        'nodes_js': nodes_js,
        'is_complete': tree.get('isComplete', True),
        'rows': tree['rows'],
        'states': states,
        'levels': levels,
    }


# === HTML GENERATION ===

def generate_tree_html(tree_key, data):
    mw = data['max_width']
    col_w = mw * 104 + (mw - 1) * 12 + 32
    s = data['stats']
    display_name = DISPLAY_NAMES.get(tree_key, data['tree_name'])
    incomplete = '' if data['is_complete'] else ' <span class="tree-incomplete">*</span>'

    lines = []
    lines.append(f'<div class="tree-col" id="tree-{tree_key}" style="width:{col_w}px">')
    lines.append(f'  <div class="tree-header">{html_mod.escape(display_name)}{incomplete}<br>'
                 f'<span class="tree-pct">{s["done"]}/{s["total"]} &mdash; {s["pct"]}%</span>'
                 f'<div class="tree-progress-bar"><div class="tree-progress-fill" style="width:{s["pct"]}%"></div></div></div>')
    lines.append(f'  <div class="tree-body">')
    lines.append(f'    <svg class="tree-svg" id="svg-{tree_key}"></svg>')

    for row in data['rows']:
        lines.append(f'    <div class="tree-row">')
        for el in row['elements']:
            eid = el['id']
            state = data['states'][eid]
            cur = data['levels'][eid]
            mx = el['maxLevel']
            bar_pct = round(cur / mx * 100) if mx else 0
            full_name = html_mod.escape(el['name'])
            short_name = html_mod.escape(abbreviate(el['name']))
            extra = ' locked-pad' if state == 'locked' else ''

            lines.append(
                f'      <div class="node {state}{extra}" id="n-{tree_key}-{eid}" '
                f'data-tree="{tree_key}" data-id="{eid}">'
                f'<div class="node-top">'
                f'<span class="node-name" title="{full_name}">{short_name}</span>'
                f'<span class="node-pill">{cur}/{mx}</span>'
                f'</div>'
                f'<div class="node-bar"><div class="node-bar-fill {state}" '
                f'style="width:{bar_pct}%"></div></div>'
                f'</div>'
            )
        lines.append(f'    </div>')

    lines.append(f'  </div>')
    lines.append(f'</div>')
    return '\n'.join(lines)


# === CSS ===

CSS = r'''
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    background: #fff;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    color: #333;
    min-height: 100vh;
    padding-bottom: 24px;
}

/* Page header */
.page-header {
    text-align: center;
    padding: 16px 24px 12px;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-bottom: 3px solid #f4a261;
    margin-bottom: 12px;
    color: #fff;
}
.game-badge {
    display: inline-block;
    background: rgba(244,162,97,0.15);
    border: 1px solid rgba(244,162,97,0.4);
    color: #f4a261;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    padding: 2px 12px;
    border-radius: 12px;
    margin-bottom: 6px;
}
.page-header .logo { height: 60px; vertical-align: middle; margin-right: 8px; }
.page-header h1 {
    font-family: 'Fredoka', sans-serif;
    font-size: 26px;
    color: #fff;
    display: inline;
    vertical-align: middle;
}
.page-header .subtitle {
    font-size: 11px;
    color: rgba(255,255,255,0.6);
    margin-top: 3px;
}
.header-actions {
    margin-top: 6px;
    display: flex;
    justify-content: center;
    gap: 10px;
}
.header-btn {
    padding: 5px 16px;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 6px;
    background: rgba(255,255,255,0.08);
    font-size: 12px;
    cursor: pointer;
    color: rgba(255,255,255,0.85);
    transition: all 0.2s ease;
    font-weight: 500;
}
.header-btn:hover { background: rgba(255,255,255,0.15); border-color: rgba(255,255,255,0.35); color: #fff; }
.header-btn.export { border-color: rgba(91,192,222,0.5); color: #8dd8ee; }
.header-btn.export:hover { background: rgba(91,192,222,0.15); border-color: rgba(91,192,222,0.7); }
.header-btn.import { border-color: rgba(127,179,168,0.5); color: #a8d8cc; }
.header-btn.import:hover { background: rgba(127,179,168,0.15); border-color: rgba(127,179,168,0.7); }
.header-btn.reset { border-color: rgba(231,76,60,0.4); color: #e8a09a; }
.header-btn.reset:hover { background: rgba(231,76,60,0.15); border-color: rgba(231,76,60,0.6); color: #f5b7b1; }
.import-msg {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #e6f0ed;
    border: 1px solid #7fb3a8;
    color: #3a6b5e;
    padding: 8px 20px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    z-index: 9999;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: opacity 0.3s;
}

/* Legend */
.legend {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
    padding: 8px 16px;
    font-size: 12px;
    color: #555;
    border: 1px solid #e8e8e8;
    border-radius: 6px;
    margin: 8px 20px 4px;
    background: #fafafa;
}
.legend-label {
    font-weight: 600;
    color: #777;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
}
.legend-swatch {
    width: 18px; height: 18px;
    border-radius: 3px;
    display: inline-block;
}
.sw-maxed  { border: 2px solid #7fb3a8; background: #e6f0ed; }
.sw-progress { border: 2px solid #f4a261; background: #fdf1dc; }
.sw-blocked  { border: 2px dashed #e57373; background: #fdf1dc; }
.sw-available { border: 2px solid #5bc0de; background: #e8f4f8; }
.sw-locked { border: 1px solid #ccc; background: #f5f5f5; }

/* Bands */
.band-label {
    font-family: 'Fredoka', sans-serif;
    font-size: 15px;
    color: #aaa;
    text-align: center;
    margin: 8px 0 2px;
}
.band {
    display: flex;
    justify-content: flex-start;
    gap: 20px;
    padding: 4px 12px 12px;
    align-items: flex-start;
    overflow-x: auto;
    min-width: 0;
}

/* Tree column */
.tree-col {
    flex-shrink: 0;
}
.tree-header {
    font-family: 'Fredoka', sans-serif;
    font-size: 15px;
    color: #5a6a6a;
    text-align: center;
    padding: 6px 10px 5px;
    background: #f8f9fa;
    border: 1px solid #e8e8e8;
    border-radius: 6px 6px 0 0;
    margin-bottom: 6px;
    line-height: 1.3;
    font-weight: 700;
}
.tree-pct {
    font-family: 'Segoe UI', sans-serif;
    font-size: 10px;
    color: #999;
}
.tree-progress-bar {
    height: 3px;
    background: #e8e8e8;
    border-radius: 2px;
    margin-top: 3px;
    overflow: hidden;
}
.tree-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #7fb3a8, #5bc0de);
    border-radius: 2px;
    transition: width 0.3s;
}
.tree-incomplete {
    color: #e74c3c;
    font-size: 11px;
}
.tree-body {
    position: relative;
}
.tree-svg {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: visible;
}

/* Tree rows */
.tree-row {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-bottom: 20px;
    position: relative;
    z-index: 1;
}

/* Nodes */
.node {
    width: 104px;
    height: 38px;
    border-radius: 5px;
    padding: 2px 5px 0;
    cursor: pointer;
    transition: box-shadow 0.15s, transform 0.15s;
    position: relative;
    overflow: visible;
    flex-shrink: 0;
}
.node:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    transform: translateY(-1px);
    z-index: 10;
}
.node.locked-pad { padding: 3px 6px 0; }
.node-top {
    display: flex;
    align-items: center;
    gap: 2px;
    height: 28px;
}
.node-name {
    font-size: 11px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
    min-width: 0;
    line-height: 28px;
}
.node-pill {
    font-size: 10px;
    font-weight: 600;
    white-space: nowrap;
    opacity: 0.6;
    line-height: 28px;
}
.node-bar {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    background: rgba(0,0,0,0.07);
}
.node-bar-fill {
    height: 100%;
    transition: width 0.3s;
}

/* State colors */
.node.maxed     { border: 2px solid #7fb3a8; background: #e6f0ed; }
.node.progress  { border: 2px solid #f4a261; background: #fdf1dc; }
.node.blocked   { border: 2px dashed #e57373; background: #fdf1dc; }
.node.available { border: 2px solid #5bc0de; background: #e8f4f8; }
.node.locked    { border: 1px solid #ccc; background: #f5f5f5; }
.node.locked .node-name,
.node.locked .node-pill { color: #aaa; }

.node-bar-fill.maxed     { background: #7fb3a8; }
.node-bar-fill.progress  { background: #f4a261; }
.node-bar-fill.blocked   { background: #e57373; }
.node-bar-fill.available { background: #5bc0de; }
.node-bar-fill.locked    { background: #d0d0d0; }

/* Tooltip (shown on hover when editor is NOT open) */
.tooltip {
    display: none;
    position: fixed;
    background: #fff;
    border: 1px solid #ccc;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 11px;
    line-height: 1.55;
    max-width: 280px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    z-index: 1000;
    pointer-events: none;
}
.tt-name { font-weight: 700; font-size: 12px; margin-bottom: 2px; }
.tt-badge {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    margin-left: 6px;
    vertical-align: middle;
}
.tt-badge.maxed     { background: #e6f0ed; color: #5a8a7e; }
.tt-badge.progress  { background: #fdf1dc; color: #c07b30; }
.tt-badge.blocked   { background: #fce4ec; color: #c62828; }
.tt-badge.available { background: #e8f4f8; color: #3a8ca0; }
.tt-badge.locked    { background: #f0f0f0; color: #999; }
.tt-sep { border-top: 1px solid #eee; margin: 5px 0; }
.tt-label { font-weight: 600; color: #666; font-size: 10px; margin-top: 3px; }
.tt-cost span { margin-right: 8px; }
.tt-notes { font-style: italic; color: #888; margin-top: 4px; font-size: 10px; }
.tt-pri { font-weight: 700; }
.tt-pri.S { color: #e74c3c; }
.tt-pri.A { color: #e67e22; }
.tt-pri.B { color: #3498db; }
.tt-pri.C { color: #999; }

/* Recommended path badges */
.rec-badge {
    position: absolute;
    top: -6px; right: -6px;
    min-width: 16px; height: 16px;
    padding: 0 2px;
    border-radius: 8px;
    font-size: 8px; font-weight: 700;
    line-height: 16px; text-align: center;
    z-index: 5; pointer-events: none;
    box-shadow: 0 1px 3px rgba(0,0,0,0.25);
}
.rec-badge.rec-next {
    background: #f59e0b; color: #fff;
    animation: rec-pulse 2s ease-in-out infinite;
}
.rec-badge.rec-future {
    background: #9ca3af; color: #fff; opacity: 0.7;
}
.node.rec-next {
    box-shadow: 0 0 8px 2px rgba(245,158,11,0.4);
}
@keyframes rec-pulse {
    0%,100% { transform: scale(1); }
    50% { transform: scale(1.15); box-shadow: 0 0 8px rgba(245,158,11,0.6); }
}
.sw-rec {
    min-width: 14px; height: 14px;
    border-radius: 7px;
    background: #f59e0b; color: #fff;
    font-size: 7px; font-weight: 700;
    line-height: 14px; text-align: center;
    display: inline-block;
}
.tt-rec { color: #d97706; font-weight: 600; font-size: 10px; margin-top: 4px; }
.ep-rec { font-size: 10px; color: #d97706; text-align: center; margin-top: 4px; font-weight: 600; }

/* Editor popup */
.editor-popup {
    display: none;
    position: fixed;
    background: #fff;
    border: 1px solid #bbb;
    border-radius: 8px;
    padding: 12px 14px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.18);
    z-index: 2000;
    min-width: 220px;
    font-size: 12px;
}
.editor-popup .ep-close {
    position: absolute;
    top: 6px; right: 8px;
    cursor: pointer;
    font-size: 16px;
    color: #999;
    line-height: 1;
    border: none;
    background: none;
    padding: 2px 4px;
}
.editor-popup .ep-close:hover { color: #333; }
.editor-popup .ep-title {
    font-weight: 700;
    font-size: 13px;
    margin-bottom: 6px;
    padding-right: 20px;
    color: #333;
}
.editor-popup .ep-level {
    font-size: 14px;
    font-weight: 600;
    text-align: center;
    margin: 8px 0;
    color: #444;
}
.editor-popup .ep-controls {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 6px;
}
.editor-popup .ep-btn {
    width: 36px;
    height: 30px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: #f8f8f8;
    font-size: 16px;
    font-weight: 700;
    cursor: pointer;
    color: #555;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.1s;
}
.editor-popup .ep-btn:hover:not(:disabled) { background: #e8e8e8; }
.editor-popup .ep-btn:disabled { opacity: 0.3; cursor: default; }
.editor-popup .ep-btn.max-btn {
    width: auto;
    padding: 0 10px;
    font-size: 11px;
    font-weight: 600;
}
.editor-popup .ep-cost {
    font-size: 10px;
    color: #888;
    text-align: center;
    margin-top: 4px;
    min-height: 14px;
}
.editor-popup .ep-cost span { margin-right: 6px; }
.editor-popup .ep-pri {
    font-size: 10px;
    color: #888;
    text-align: center;
    margin-top: 2px;
}

/* Footer */
.page-footer {
    text-align: center;
    padding: 16px 20px;
    margin-top: 20px;
    font-size: 11px;
    color: #999;
    border-top: 1px solid #e8e8e8;
}
.page-footer a { color: #5bc0de; text-decoration: none; }
.page-footer a:hover { text-decoration: underline; }

/* Mobile detail section (hidden on desktop) */
.ep-detail { display: none; }

/* Backdrop overlay for mobile editor */
.editor-backdrop {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.35);
    z-index: 1999;
}

/* ===== TABLET + PHONE (max-width: 768px) ===== */
@media (max-width: 768px) {
    /* Stack trees vertically */
    .band { flex-direction: column; gap: 4px; padding: 4px 0 8px; overflow-x: visible; }
    .tree-col { width: 100% !important; overflow-x: auto; -webkit-overflow-scrolling: touch; padding: 0 8px; }
    .tree-body { min-width: fit-content; }

    /* Collapsible tree headers */
    .tree-header { cursor: pointer; position: sticky; top: 0; background: #fff; z-index: 5; padding: 8px 0 6px; border-bottom: 1px solid #e0e0e0; }
    .tree-header::after { content: ' \u25BC'; font-size: 10px; color: #aaa; }
    .tree-col.collapsed .tree-header::after { content: ' \u25B6'; }
    .tree-col.collapsed .tree-body { display: none; }

    /* Header compact */
    .page-header { padding: 12px 16px 10px; }
    .page-header h1 { font-size: 20px; }
    .page-header .subtitle { font-size: 10px; }
    .game-badge { font-size: 9px; padding: 2px 10px; margin-bottom: 4px; }

    /* Legend wraps */
    .legend { flex-wrap: wrap; gap: 6px 12px; padding: 6px 12px; margin: 6px 12px 4px; font-size: 11px; }
    .legend-label { font-size: 10px; }

    /* Band labels compact */
    .band-label { font-size: 14px; padding: 8px 12px; position: sticky; top: 0; z-index: 4; background: #fff; margin: 4px 0 1px; }

    /* Tree headers tappable */
    .tree-header { padding: 8px 12px 6px; }

    /* Editor -> bottom sheet */
    .editor-popup {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        top: auto !important;
        width: 100% !important;
        min-width: unset !important;
        border-radius: 12px 12px 0 0;
        padding: 16px 20px 24px;
        box-shadow: 0 -4px 24px rgba(0,0,0,0.2);
        max-height: 60vh;
        overflow-y: auto;
    }
    .ep-btn { width: 48px; height: 44px; font-size: 20px; }
    .ep-btn.max-btn { padding: 0 16px; height: 44px; font-size: 13px; }
    .ep-close { font-size: 24px; padding: 8px 12px; }
    .ep-title { font-size: 16px; }
    .ep-level { font-size: 18px; }

    /* Hide hover tooltip on touch */
    .tooltip { display: none !important; }

    /* Show detail section in editor on mobile */
    .ep-detail { display: block; margin-top: 8px; font-size: 12px; line-height: 1.5; }
    .ep-detail .tt-sep { border-top: 1px solid #eee; margin: 5px 0; }
    .ep-detail .tt-label { font-weight: 600; color: #666; font-size: 10px; margin-top: 3px; }
    .ep-detail .tt-cost span { margin-right: 6px; }
    .ep-detail .tt-notes { font-style: italic; color: #888; margin-top: 4px; font-size: 10px; }
    .ep-detail .tt-rec { color: #d97706; font-weight: 600; font-size: 10px; margin-top: 4px; }

    /* Show backdrop on mobile */
    .editor-backdrop.active { display: block; }
}

/* ===== PHONE ONLY (max-width: 480px) ===== */
@media (max-width: 480px) {
    /* Slightly smaller nodes, taller for better touch targets */
    .node { width: 92px; height: 40px; }
    .node-top { height: 30px; }
    .node-name { font-size: 9.5px; line-height: 30px; }
    .node-pill { font-size: 9px; line-height: 30px; }
    .tree-row { gap: 8px; margin-bottom: 16px; }
    .page-header h1 { font-size: 18px; }
    .page-header .logo { height: 44px; }
    .header-btn { padding: 6px 12px; font-size: 12px; }
    .header-actions { gap: 6px; flex-wrap: wrap; }
    .legend-swatch { width: 14px; height: 14px; }
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
    }
}
'''

# === JAVASCRIPT ===

JS = r'''
const LS_KEY = 'owow-research-progress';
let editorOpen = false;
const isMobile = () => window.innerWidth <= 768;

document.addEventListener('DOMContentLoaded', () => {
    loadProgress();
    recomputeAll();
    drawAllLines();
    renderRecommendedBadges();
    setupTooltips();
    setupEditor();
    if (isMobile()) setupCollapsibleTrees();
    window.addEventListener('resize', () => { clearAllLines(); drawAllLines(); });
    window.addEventListener('orientationchange', () => {
        setTimeout(() => { clearAllLines(); drawAllLines(); }, 100);
    });
    document.getElementById('btn-export')?.addEventListener('click', exportCSV);
    document.getElementById('csv-file-input')?.addEventListener('change', importCSV);
    document.getElementById('btn-reset')?.addEventListener('click', resetProgress);
});

// ============ COLLAPSIBLE TREES (MOBILE) ============

function setupCollapsibleTrees() {
    // Find the tree containing the next recommended step (gold badge)
    const steps = computeRecommendedPath();
    const nextStep = steps.find(s => s.status === 'next');
    const expandTreeKey = nextStep ? nextStep.treeKey : null;

    document.querySelectorAll('.tree-col').forEach(col => {
        const treeKey = col.id.replace('tree-', '');
        const header = col.querySelector('.tree-header');
        if (!header) return;

        // Collapse all except the tree with the next recommended step
        if (treeKey !== expandTreeKey) {
            col.classList.add('collapsed');
        }

        header.addEventListener('click', () => {
            col.classList.toggle('collapsed');
            if (!col.classList.contains('collapsed')) {
                // Redraw SVG lines after expand animation
                setTimeout(() => drawTreeLines(treeKey), 50);
            }
        });
    });
}

// ============ DRAWING ============

function drawAllLines() {
    for (const [tk, data] of Object.entries(TREE_DATA)) {
        drawTreeLines(tk);
    }
}

function drawTreeLines(tk) {
    const data = TREE_DATA[tk];
    if (!data) return;
    const svg = document.getElementById('svg-' + tk);
    const body = svg?.parentElement;
    if (!svg || !body) return;

    svg.innerHTML = '';
    const bw = body.scrollWidth;
    const bh = body.scrollHeight;
    svg.setAttribute('width', bw);
    svg.setAttribute('height', bh);
    svg.setAttribute('viewBox', '0 0 ' + bw + ' ' + bh);

    const defs = ns('defs');
    [['done','#7fb3a8'],['next','#f4a261'],['locked','#ccc']].forEach(([cls,col]) => {
        const m = ns('marker');
        m.id = 'a-' + cls + '-' + tk;
        m.setAttribute('viewBox','0 0 10 10');
        m.setAttribute('refX','9'); m.setAttribute('refY','5');
        m.setAttribute('markerWidth','5'); m.setAttribute('markerHeight','5');
        m.setAttribute('orient','auto');
        const p = ns('path');
        p.setAttribute('d','M 0 1 L 9 5 L 0 9 z');
        p.setAttribute('fill', col);
        m.appendChild(p);
        defs.appendChild(m);
    });
    svg.appendChild(defs);

    const bRect = body.getBoundingClientRect();
    for (const conn of data.connections) {
        const fromNode = data.nodes[conn.from];
        const toNode = data.nodes[conn.to];
        if (!fromNode || !toNode) continue;
        const fe = document.getElementById('n-' + tk + '-' + conn.from);
        const te = document.getElementById('n-' + tk + '-' + conn.to);
        if (!fe || !te) continue;

        const lineState = getLineState(fromNode.state, toNode.state);
        const fR = fe.getBoundingClientRect();
        const tR = te.getBoundingClientRect();
        const x1 = fR.left + fR.width / 2 - bRect.left;
        const y1 = fR.bottom - bRect.top;
        const x2 = tR.left + tR.width / 2 - bRect.left;
        const y2 = tR.top - bRect.top;

        const path = ns('path');
        let d;
        if (Math.abs(x1 - x2) < 3) {
            d = `M ${x1} ${y1} L ${x2} ${y2}`;
        } else {
            const my = (y1 + y2) / 2;
            d = `M ${x1} ${y1} C ${x1} ${my}, ${x2} ${my}, ${x2} ${y2}`;
        }
        const colors = { done: '#7fb3a8', next: '#f4a261', locked: '#ccc' };
        path.setAttribute('d', d);
        path.setAttribute('stroke', colors[lineState] || '#ccc');
        path.setAttribute('stroke-width', lineState === 'locked' ? '1.2' : '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('marker-end', `url(#a-${lineState}-${tk})`);
        svg.appendChild(path);
    }
}

function getLineState(fromState, toState) {
    if (toState === 'maxed') return 'done';
    if (toState === 'progress' || toState === 'available' || toState === 'blocked') return 'next';
    return 'locked';
}

function clearAllLines() {
    for (const tk of Object.keys(TREE_DATA)) {
        const svg = document.getElementById('svg-' + tk);
        if (svg) svg.innerHTML = '';
    }
}

function ns(tag) {
    return document.createElementNS('http://www.w3.org/2000/svg', tag);
}

// ============ STATE RECOMPUTATION ============

function getNodeState(node, nodes) {
    if (node.currentLevel >= node.maxLevel) return 'maxed';
    // Get requirements for the NEXT level to research (levels array is 0-indexed)
    const nextIdx = node.currentLevel;
    const nextLv = node.levels[nextIdx];
    const reqs = (nextLv && nextLv.requirements) ? nextLv.requirements : node.requirements;
    if (node.currentLevel > 0) {
        for (const req of reqs) {
            if (req.external) return 'progress';
            const reqNode = nodes[req.elementId];
            if (!reqNode || reqNode.currentLevel < req.minLevel) return 'blocked';
        }
        return 'progress';
    }
    for (const req of reqs) {
        if (req.external) return 'locked';
        const reqNode = nodes[req.elementId];
        if (!reqNode || reqNode.currentLevel < req.minLevel) return 'locked';
    }
    return 'available';
}

function recomputeTree(tk) {
    const data = TREE_DATA[tk];
    if (!data) return;
    const nodes = data.nodes;
    for (const [eid, node] of Object.entries(nodes)) {
        node.state = getNodeState(node, nodes);
        updateNodeDOM(tk, eid, node);
    }
    updateTreeStats(tk);
}

function recomputeAll() {
    for (const tk of Object.keys(TREE_DATA)) {
        recomputeTree(tk);
    }
    updateGrandStats();
}

function updateNodeDOM(tk, eid, node) {
    const el = document.getElementById('n-' + tk + '-' + eid);
    if (!el) return;

    // Update classes
    el.className = 'node ' + node.state + ((node.state === 'locked') ? ' locked-pad' : '');

    // Update pill
    const pill = el.querySelector('.node-pill');
    if (pill) pill.textContent = node.currentLevel + '/' + node.maxLevel;

    // Update bar
    const barFill = el.querySelector('.node-bar-fill');
    if (barFill) {
        const pct = node.maxLevel ? Math.round(node.currentLevel / node.maxLevel * 100) : 0;
        barFill.style.width = pct + '%';
        barFill.className = 'node-bar-fill ' + node.state;
    }
}

function updateTreeStats(tk) {
    const data = TREE_DATA[tk];
    if (!data) return;
    let total = 0, done = 0;
    for (const node of Object.values(data.nodes)) {
        total += node.maxLevel;
        done += node.currentLevel;
    }
    const pct = total ? Math.round(done / total * 100) : 0;
    data.stats = { total, done, pct };

    const header = document.querySelector('#tree-' + tk + ' .tree-pct');
    if (header) {
        header.innerHTML = done + '/' + total + ' &mdash; ' + pct + '%';
    }
    const progFill = document.querySelector('#tree-' + tk + ' .tree-progress-fill');
    if (progFill) {
        progFill.style.width = pct + '%';
    }
}

function updateGrandStats() {
    let gDone = 0, gTotal = 0;
    for (const data of Object.values(TREE_DATA)) {
        if (data.stats) {
            gDone += data.stats.done;
            gTotal += data.stats.total;
        }
    }
    const gPct = gTotal ? Math.round(gDone / gTotal * 100) : 0;
    const sub = document.getElementById('grand-stats');
    if (sub) sub.textContent = `Overall: ${gDone}/${gTotal} (${gPct}%)`;
}

// ============ TOOLTIPS ============

function setupTooltips() {
    const tip = document.getElementById('tooltip');
    document.querySelectorAll('.node').forEach(node => {
        node.addEventListener('mouseenter', e => {
            if (editorOpen) return;
            const d = TREE_DATA[node.dataset.tree]?.nodes?.[node.dataset.id];
            if (!d) return;
            let h = `<div class="tt-name">${esc(d.name)} <span class="tt-badge ${d.state}">${d.state}</span></div>`;
            h += `<div>Level: <b>${d.currentLevel}/${d.maxLevel}</b></div>`;
            if (d.priority) {
                h += `<div>Priority: <span class="tt-pri ${d.priority}">${d.priority}-Tier</span></div>`;
            }
            // Show prerequisites for the NEXT level to research
            const nextIdx = d.currentLevel;
            const nextLv = d.levels[nextIdx];
            const ttReqs = (nextLv && nextLv.requirements) ? nextLv.requirements : d.requirements;
            if (ttReqs.length) {
                const label = d.currentLevel > 0
                    ? `Prerequisites (for Lv.${d.currentLevel + 1}):`
                    : `Prerequisites:`;
                h += `<div class="tt-sep"></div><div class="tt-label">${label}</div>`;
                const nodes = TREE_DATA[node.dataset.tree]?.nodes;
                ttReqs.forEach(req => {
                    if (req.external) {
                        h += `<div style="color:#c00;font-size:10px">${esc(req.elementId)}</div>`;
                    } else {
                        const rn = nodes?.[req.elementId];
                        const rName = rn ? rn.name : req.elementId;
                        const met = rn && rn.currentLevel >= req.minLevel;
                        const color = met ? '#2e7d32' : '#c00';
                        h += `<div style="font-size:10px;color:${color}">${esc(rName)} Lv.${req.minLevel} ${met ? '✓' : '✗'}</div>`;
                    }
                });
            }
            // Next level cost
            const nextCost = getNextCost(d);
            if (nextCost && d.state !== 'maxed') {
                h += `<div class="tt-sep"></div>`;
                h += `<div class="tt-label">Next Level (${d.currentLevel + 1}):</div>`;
                h += fmtCost(nextCost);
            }
            // Total remaining
            const rem = getTotalRemaining(d);
            if (d.state !== 'maxed' && (rem.gold || rem.food || rem.iron || rem.valor)) {
                h += `<div class="tt-label">Total Remaining:</div>`;
                h += fmtCost(rem);
            }
            if (d.notes) {
                h += `<div class="tt-sep"></div><div class="tt-notes">${esc(d.notes)}</div>`;
            }
            // Recommended path info
            const recKey = node.dataset.tree + '-' + node.dataset.id;
            const recStep = window._recLookup?.[recKey];
            if (recStep) {
                h += `<div class="tt-sep"></div>`;
                h += `<div class="tt-rec">Recommended Step #${recStep.stepNum}`;
                if (recStep.status === 'next') h += ' (UP NEXT!)';
                h += `</div>`;
                h += `<div class="tt-rec" style="font-weight:400">${esc(recStep.reason)}</div>`;
            }
            tip.innerHTML = h;
            tip.style.display = 'block';
            pos(e, tip);
        });
        node.addEventListener('mousemove', e => { if (!editorOpen) pos(e, tip); });
        node.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
    });
}

function getNextCost(d) {
    for (const lv of d.levels) {
        if (lv.level > d.currentLevel) return lv;
    }
    return null;
}

function getTotalRemaining(d) {
    const r = { gold: 0, food: 0, iron: 0, valor: 0 };
    for (const lv of d.levels) {
        if (lv.level > d.currentLevel) {
            r.gold += lv.gold || 0;
            r.food += lv.food || 0;
            r.iron += lv.iron || 0;
            r.valor += lv.valor || 0;
        }
    }
    return r;
}

function fmtCost(c) {
    let p = [];
    if (c.gold) p.push(`<span style="color:#b8860b">Gold: ${fN(c.gold)}</span>`);
    if (c.food) p.push(`<span style="color:#5a8a3c">Food: ${fN(c.food)}</span>`);
    if (c.iron) p.push(`<span style="color:#7a8a9a">Iron: ${fN(c.iron)}</span>`);
    if (c.valor) p.push(`<span style="color:#8b5cf6">Valor: ${fN(c.valor)}</span>`);
    return `<div class="tt-cost">${p.join(' ')}</div>`;
}

function fN(v) {
    if (v >= 1e6) return (v / 1e6).toFixed(1) + 'M';
    if (v >= 1e3) return (v / 1e3).toFixed(0) + 'K';
    return '' + v;
}

function esc(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}

function pos(e, tip) {
    let x = e.clientX + 14, y = e.clientY + 14;
    if (x + tip.offsetWidth > window.innerWidth - 10) x = e.clientX - tip.offsetWidth - 10;
    if (y + tip.offsetHeight > window.innerHeight - 10) y = e.clientY - tip.offsetHeight - 10;
    tip.style.left = x + 'px';
    tip.style.top = y + 'px';
}

// ============ CLICK-TO-EDIT ============

function setupEditor() {
    const popup = document.getElementById('editor-popup');
    const epTitle = popup.querySelector('.ep-title');
    const epLevel = popup.querySelector('.ep-level');
    const epMinus = popup.querySelector('.ep-minus');
    const epPlus = popup.querySelector('.ep-plus');
    const epMax = popup.querySelector('.ep-max');
    const epCost = popup.querySelector('.ep-cost');
    const epPri = popup.querySelector('.ep-pri');
    const epClose = popup.querySelector('.ep-close');

    let curTree = null, curId = null;

    function openEditor(tk, eid, anchorEl) {
        curTree = tk;
        curId = eid;
        editorOpen = true;
        document.getElementById('tooltip').style.display = 'none';
        renderEditor();
        popup.style.display = 'block';

        if (isMobile()) {
            // Bottom sheet: clear inline positioning, let CSS handle it
            popup.style.left = '';
            popup.style.top = '';
            // Show backdrop
            const backdrop = document.getElementById('editor-backdrop');
            if (backdrop) backdrop.classList.add('active');
        } else {
            // Position near clicked node (desktop)
            const r = anchorEl.getBoundingClientRect();
            let x = r.right + 8;
            let y = r.top - 10;
            // Keep on screen
            const pw = 230, ph = 160;
            if (x + pw > window.innerWidth - 10) x = r.left - pw - 8;
            if (y + ph > window.innerHeight - 10) y = window.innerHeight - ph - 10;
            if (y < 10) y = 10;
            popup.style.left = x + 'px';
            popup.style.top = y + 'px';
        }
    }

    function closeEditor() {
        popup.style.display = 'none';
        editorOpen = false;
        curTree = null;
        curId = null;
        const backdrop = document.getElementById('editor-backdrop');
        if (backdrop) backdrop.classList.remove('active');
    }

    function renderEditor() {
        if (!curTree || !curId) return;
        const d = TREE_DATA[curTree]?.nodes?.[curId];
        if (!d) return;
        epTitle.textContent = d.name;
        epLevel.textContent = `Lv. ${d.currentLevel} / ${d.maxLevel}`;
        const locked = d.state === 'locked';
        const blocked = d.state === 'blocked';
        epMinus.disabled = d.currentLevel <= 0;
        epPlus.disabled = d.currentLevel >= d.maxLevel || locked;
        epMax.disabled = d.currentLevel >= d.maxLevel || locked;

        // Show next level cost and prerequisites
        if (locked || blocked) {
            // Show which prereqs are missing for the next level
            const nextIdx = d.currentLevel;
            const nextLv = d.levels[nextIdx];
            const edReqs = (nextLv && nextLv.requirements) ? nextLv.requirements : d.requirements;
            const nodes = TREE_DATA[curTree]?.nodes;
            const missing = edReqs.filter(r => {
                if (r.external) return true;
                const rn = nodes?.[r.elementId];
                return !rn || rn.currentLevel < r.minLevel;
            }).map(r => {
                if (r.external) return r.elementId;
                const rn = nodes?.[r.elementId];
                return (rn ? rn.name : r.elementId) + ' Lv.' + r.minLevel;
            });
            const prefix = blocked ? 'Blocked — need: ' : 'Prereqs not met: ';
            epCost.innerHTML = '<span style="color:#c00">' + prefix + missing.map(esc).join(', ') + '</span>';
        } else {
            const nc = getNextCost(d);
            if (nc && d.currentLevel < d.maxLevel) {
                let parts = [];
                if (nc.gold) parts.push(`<span style="color:#b8860b">G:${fN(nc.gold)}</span>`);
                if (nc.food) parts.push(`<span style="color:#5a8a3c">F:${fN(nc.food)}</span>`);
                if (nc.iron) parts.push(`<span style="color:#7a8a9a">I:${fN(nc.iron)}</span>`);
                if (nc.valor) parts.push(`<span style="color:#8b5cf6">V:${fN(nc.valor)}</span>`);
                epCost.innerHTML = parts.length ? `Next: ${parts.join(' ')}` : '';
            } else {
                epCost.innerHTML = d.currentLevel >= d.maxLevel ? 'MAXED' : '';
            }
        }

        // Show priority
        if (d.priority) {
            epPri.innerHTML = `Priority: <span class="tt-pri ${d.priority}">${d.priority}-Tier</span>`;
        } else {
            epPri.innerHTML = '';
        }

        // Show recommended path info
        const epRec = popup.querySelector('.ep-rec');
        if (epRec) {
            const recKey = curTree + '-' + curId;
            const recStep = window._recLookup?.[recKey];
            if (recStep) {
                epRec.innerHTML = `Step #${recStep.stepNum}${recStep.status === 'next' ? ' (UP NEXT!)' : ''}: ${esc(recStep.reason)}`;
            } else {
                epRec.innerHTML = '';
            }
        }

        // Populate ep-detail on mobile (replaces tooltip info)
        const epDetail = popup.querySelector('.ep-detail');
        if (epDetail && isMobile()) {
            let dh = '';
            // Prerequisites
            const nextIdx = d.currentLevel;
            const nextLv = d.levels[nextIdx];
            const detReqs = (nextLv && nextLv.requirements) ? nextLv.requirements : d.requirements;
            if (detReqs.length) {
                const label = d.currentLevel > 0
                    ? `Prerequisites (for Lv.${d.currentLevel + 1}):`
                    : `Prerequisites:`;
                dh += `<div class="tt-sep"></div><div class="tt-label">${label}</div>`;
                const nodes = TREE_DATA[curTree]?.nodes;
                detReqs.forEach(req => {
                    if (req.external) {
                        dh += `<div style="color:#c00;font-size:10px">${esc(req.elementId)}</div>`;
                    } else {
                        const rn = nodes?.[req.elementId];
                        const rName = rn ? rn.name : req.elementId;
                        const met = rn && rn.currentLevel >= req.minLevel;
                        const color = met ? '#2e7d32' : '#c00';
                        dh += `<div style="font-size:11px;color:${color}">${esc(rName)} Lv.${req.minLevel} ${met ? '\u2713' : '\u2717'}</div>`;
                    }
                });
            }
            // Next level cost (if not already shown in ep-cost)
            if (d.state !== 'maxed' && d.state !== 'locked' && d.state !== 'blocked') {
                const nc = getNextCost(d);
                if (nc) {
                    dh += `<div class="tt-sep"></div>`;
                    dh += `<div class="tt-label">Next Level (${d.currentLevel + 1}):</div>`;
                    dh += fmtCost(nc);
                }
            }
            // Total remaining
            const rem = getTotalRemaining(d);
            if (d.state !== 'maxed' && (rem.gold || rem.food || rem.iron || rem.valor)) {
                dh += `<div class="tt-label">Total Remaining:</div>`;
                dh += fmtCost(rem);
            }
            // Notes
            if (d.notes) {
                dh += `<div class="tt-sep"></div><div class="tt-notes">${esc(d.notes)}</div>`;
            }
            epDetail.innerHTML = dh;
        } else if (epDetail) {
            epDetail.innerHTML = '';
        }
    }

    function changeLevel(delta) {
        if (!curTree || !curId) return;
        const d = TREE_DATA[curTree].nodes[curId];
        if (!d) return;
        const newLv = Math.max(0, Math.min(d.maxLevel, d.currentLevel + delta));
        if (newLv === d.currentLevel) return;
        d.currentLevel = newLv;
        recomputeTree(curTree);
        drawTreeLines(curTree);
        updateGrandStats();
        saveProgress();
        renderRecommendedBadges();
        renderEditor();
    }

    function setMax() {
        if (!curTree || !curId) return;
        const d = TREE_DATA[curTree].nodes[curId];
        if (!d || d.currentLevel >= d.maxLevel) return;
        d.currentLevel = d.maxLevel;
        recomputeTree(curTree);
        drawTreeLines(curTree);
        updateGrandStats();
        saveProgress();
        renderRecommendedBadges();
        renderEditor();
    }

    // Wire events
    epMinus.addEventListener('click', e => { e.stopPropagation(); changeLevel(-1); });
    epPlus.addEventListener('click', e => { e.stopPropagation(); changeLevel(1); });
    epMax.addEventListener('click', e => { e.stopPropagation(); setMax(); });
    epClose.addEventListener('click', e => { e.stopPropagation(); closeEditor(); });

    // Click on any node opens editor
    document.querySelectorAll('.node').forEach(node => {
        node.addEventListener('click', e => {
            e.stopPropagation();
            openEditor(node.dataset.tree, node.dataset.id, node);
        });
    });

    // Click outside closes editor
    document.addEventListener('click', e => {
        if (editorOpen && !popup.contains(e.target) && !e.target.closest('.node')) {
            closeEditor();
        }
    });

    // Backdrop click closes editor (mobile)
    document.getElementById('editor-backdrop')?.addEventListener('click', () => {
        if (editorOpen) closeEditor();
    });

    // Escape closes editor
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && editorOpen) closeEditor();
    });
}

// ============ LOCALSTORAGE ============

function saveProgress() {
    const data = {};
    for (const [tk, tree] of Object.entries(TREE_DATA)) {
        data[tk] = {};
        for (const [eid, node] of Object.entries(tree.nodes)) {
            data[tk][eid] = node.currentLevel;
        }
    }
    try {
        localStorage.setItem(LS_KEY, JSON.stringify(data));
    } catch (e) { /* quota exceeded — ignore */ }
}

function loadProgress() {
    let saved;
    try {
        const raw = localStorage.getItem(LS_KEY);
        if (!raw) return;
        saved = JSON.parse(raw);
    } catch (e) { return; }
    if (!saved || typeof saved !== 'object') return;

    for (const [tk, levels] of Object.entries(saved)) {
        if (!TREE_DATA[tk]) continue;
        for (const [eid, lv] of Object.entries(levels)) {
            const node = TREE_DATA[tk].nodes?.[eid];
            if (node && typeof lv === 'number') {
                node.currentLevel = Math.max(0, Math.min(node.maxLevel, lv));
            }
        }
    }
}

// ============ EXPORT CSV ============

function exportCSV() {
    const rows = ['Tree,Row,Node,MaxLevel,Level,Gold,Food,Iron,Valor,Prerequisite,HaveIt,Priority,Notes'];
    // Maintain consistent order: iterate trees in DOM order
    const treeOrder = TREE_ORDER;
    for (const tk of treeOrder) {
        const data = TREE_DATA[tk];
        if (!data) continue;
        const treeName = data.treeName;
        // Sort nodes by row number
        const nodeList = Object.entries(data.nodes).sort((a, b) => a[1].row - b[1].row);
        for (const [eid, node] of nodeList) {
            // Build prerequisite string from requirements
            let prereqStr = 'None';
            if (node.requirements.length) {
                const parts = node.requirements.map(r => {
                    if (r.external) return r.elementId;
                    const rn = data.nodes[r.elementId];
                    return (rn ? rn.name : r.elementId) + ' Lv.' + r.minLevel;
                });
                prereqStr = parts.join('; ');
            }
            for (const lv of node.levels) {
                const haveIt = lv.level <= node.currentLevel ? 1 : 0;
                const csvRow = [
                    csvEsc(treeName), node.row, csvEsc(node.name), node.maxLevel, lv.level,
                    lv.gold || 0, lv.food || 0, lv.iron || 0, lv.valor || 0,
                    csvEsc(prereqStr), haveIt,
                    csvEsc(node.priority || ''), csvEsc(node.notes || '')
                ].join(',');
                rows.push(csvRow);
            }
        }
    }
    const blob = new Blob([rows.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'research_trees.csv';
    a.click();
    URL.revokeObjectURL(url);
}

function csvEsc(s) {
    s = String(s);
    if (s.includes(',') || s.includes('"') || s.includes('\n')) {
        return '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
}

// ============ IMPORT CSV ============

function importCSV(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(ev) {
        const text = ev.target.result;
        const lines = text.split(/\r?\n/);
        if (lines.length < 2) return;

        // Parse header to find column indices
        const header = parseCSVRow(lines[0]);
        const iTree = header.indexOf('Tree');
        const iNode = header.indexOf('Node');
        const iLevel = header.indexOf('Level');
        const iHaveIt = header.indexOf('HaveIt');
        if (iTree < 0 || iNode < 0 || iLevel < 0 || iHaveIt < 0) {
            alert('CSV must have columns: Tree, Node, Level, HaveIt');
            return;
        }

        // Build map: {treeName: {nodeName: maxHaveItLevel}}
        const parsed = {};
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            const cols = parseCSVRow(line);
            const treeName = cols[iTree];
            const nodeName = cols[iNode];
            const level = parseInt(cols[iLevel], 10);
            const haveIt = parseInt(cols[iHaveIt], 10);
            if (!treeName || !nodeName || isNaN(level)) continue;
            if (!parsed[treeName]) parsed[treeName] = {};
            if (haveIt === 1) {
                parsed[treeName][nodeName] = Math.max(parsed[treeName][nodeName] || 0, level);
            } else if (!(nodeName in parsed[treeName])) {
                parsed[treeName][nodeName] = 0;
            }
        }

        // Build reverse lookup: treeName → treeKey
        const nameToKey = {};
        for (const [tk, data] of Object.entries(TREE_DATA)) {
            nameToKey[data.treeName] = tk;
        }

        // Apply levels
        let updated = 0;
        for (const [treeName, nodeMap] of Object.entries(parsed)) {
            const tk = nameToKey[treeName];
            if (!tk || !TREE_DATA[tk]) continue;
            const nodes = TREE_DATA[tk].nodes;
            // Build nodeName → nodeId lookup
            const nameToId = {};
            for (const [eid, node] of Object.entries(nodes)) {
                nameToId[node.name] = eid;
            }
            for (const [nodeName, level] of Object.entries(nodeMap)) {
                const eid = nameToId[nodeName];
                if (!eid || !nodes[eid]) continue;
                const node = nodes[eid];
                const newLv = Math.max(0, Math.min(node.maxLevel, level));
                node.currentLevel = newLv;
                updated++;
            }
        }

        // Refresh everything
        recomputeAll();
        clearAllLines();
        drawAllLines();
        updateGrandStats();
        saveProgress();
        renderRecommendedBadges();

        // Show confirmation
        showImportMsg('Imported ' + updated + ' nodes');

        // Reset file input so same file can be re-imported (setTimeout avoids double-trigger)
        setTimeout(() => { e.target.value = ''; }, 100);
    };
    reader.readAsText(file);
}

function parseCSVRow(line) {
    // Handle quoted fields with commas and escaped quotes
    const result = [];
    let i = 0;
    while (i < line.length) {
        if (line[i] === '"') {
            // Quoted field
            let val = '';
            i++; // skip opening quote
            while (i < line.length) {
                if (line[i] === '"') {
                    if (i + 1 < line.length && line[i + 1] === '"') {
                        val += '"';
                        i += 2;
                    } else {
                        i++; // skip closing quote
                        break;
                    }
                } else {
                    val += line[i];
                    i++;
                }
            }
            result.push(val);
            if (i < line.length && line[i] === ',') i++; // skip comma
        } else {
            // Unquoted field
            let j = line.indexOf(',', i);
            if (j < 0) j = line.length;
            result.push(line.substring(i, j));
            i = j + 1;
        }
    }
    return result;
}

function showImportMsg(text) {
    const msg = document.createElement('div');
    msg.className = 'import-msg';
    msg.textContent = text;
    document.body.appendChild(msg);
    setTimeout(() => { msg.style.opacity = '0'; }, 2000);
    setTimeout(() => { msg.remove(); }, 2400);
}

// ============ RESET ============

function resetProgress() {
    if (!confirm('Reset ALL research progress to zero? This clears everything. You can re-import your CSV to restore your data.')) return;
    try { localStorage.removeItem(LS_KEY); } catch(e) {}
    // Set every node to level 0
    for (const [tk, tree] of Object.entries(TREE_DATA)) {
        for (const [eid, node] of Object.entries(tree.nodes)) {
            node.currentLevel = 0;
        }
    }
    recomputeAll();
    clearAllLines();
    drawAllLines();
    updateGrandStats();
    renderRecommendedBadges();
    // Close editor if open (closeEditor is scoped inside setupEditor)
    const ep = document.querySelector('.editor-popup');
    if (ep) ep.style.display = 'none';
    editorOpen = false;
    const bd = document.getElementById('editor-backdrop');
    if (bd) bd.classList.remove('active');
}

// ============ RECOMMENDED PATH ============

window._recLookup = {};

function computeRecommendedPath() {
    if (typeof RECOMMENDED_PATH === 'undefined' || !RECOMMENDED_PATH.length) return [];
    // Build treeName → treeKey lookup
    const nameToKey = {};
    for (const [tk, data] of Object.entries(TREE_DATA)) {
        nameToKey[data.treeName] = tk;
    }
    const results = [];
    let foundNext = false;
    for (let i = 0; i < RECOMMENDED_PATH.length; i++) {
        const entry = RECOMMENDED_PATH[i];
        const tk = nameToKey[entry.tree];
        if (!tk || !TREE_DATA[tk]) continue;
        const nodes = TREE_DATA[tk].nodes;
        // Find node by name
        let nodeId = null;
        for (const [eid, nd] of Object.entries(nodes)) {
            if (nd.name === entry.node) { nodeId = eid; break; }
        }
        if (!nodeId) continue;
        const nd = nodes[nodeId];
        const maxed = nd.currentLevel >= nd.maxLevel;
        let status;
        if (maxed) {
            status = 'done';
        } else if (!foundNext) {
            status = 'next';
            foundNext = true;
        } else {
            status = 'future';
        }
        results.push({
            treeKey: tk, nodeId: nodeId,
            reason: entry.reason, stepNum: i + 1, status: status,
        });
    }
    return results;
}

function renderRecommendedBadges() {
    // Remove existing badges and classes
    document.querySelectorAll('.rec-badge').forEach(b => b.remove());
    document.querySelectorAll('.node.rec-next').forEach(n => n.classList.remove('rec-next'));
    window._recLookup = {};

    const steps = computeRecommendedPath();
    for (const step of steps) {
        if (step.status === 'done') continue;
        window._recLookup[step.treeKey + '-' + step.nodeId] = step;
        const el = document.getElementById('n-' + step.treeKey + '-' + step.nodeId);
        if (!el) continue;
        const badge = document.createElement('span');
        badge.className = 'rec-badge ' + (step.status === 'next' ? 'rec-next' : 'rec-future');
        badge.textContent = step.stepNum;
        el.appendChild(badge);
        if (step.status === 'next') {
            el.classList.add('rec-next');
        }
    }
}
'''


# === MAIN ===

def main():
    public_mode = '--public' in sys.argv
    trees = load_trees()
    if public_mode:
        print('  PUBLIC MODE: stripping personal progress data')
        progress, priority, notes = {}, {}, {}
    else:
        progress, priority, notes = load_csv()
    rec_path = load_recommended_path()

    # Process all trees
    processed = {}
    for tk in BAND1 + BAND2:
        if tk in trees:
            processed[tk] = process_tree(tk, trees[tk], progress, priority, notes)
        else:
            print(f'  WARNING: {tk}.json not found in {TREE_DIR}/')

    # Generate tree HTML for each band
    band1_html = '\n'.join(generate_tree_html(tk, processed[tk])
                           for tk in BAND1 if tk in processed)
    band2_html = '\n'.join(generate_tree_html(tk, processed[tk])
                           for tk in BAND2 if tk in processed)

    # Build JS data object (nodes + connections + metadata)
    tree_order = [tk for tk in BAND1 + BAND2 if tk in processed]
    js_data = {}
    original_levels = {}
    for tk, d in processed.items():
        js_data[tk] = {
            'treeName': d['tree_name'],
            'nodes': d['nodes_js'],
            'connections': d['connections'],
            'stats': d['stats'],
        }
        original_levels[tk] = {eid: node['currentLevel']
                                for eid, node in d['nodes_js'].items()}

    # Resolve recommended path entries to JS-friendly format
    rec_path_js = []
    if rec_path:
        # Build tree name → key lookup
        tree_name_to_key = {}
        for tk, d in processed.items():
            tree_name_to_key[d['tree_name']] = tk

        for entry in rec_path:
            tk = tree_name_to_key.get(entry['tree'])
            if not tk or tk not in processed:
                print(f'  WARNING: recommended path tree "{entry["tree"]}" not found')
                continue
            # Find node by name
            node_id = None
            for eid, nd in processed[tk]['nodes_js'].items():
                if nd['name'] == entry['node']:
                    node_id = eid
                    break
            if not node_id:
                print(f'  WARNING: recommended path node "{entry["node"]}" not found in {entry["tree"]}')
                continue
            rec_path_js.append({
                'tree': entry['tree'],
                'node': entry['node'],
                'reason': entry.get('reason', ''),
            })

    # Compute grand totals
    grand_done = sum(d['stats']['done'] for d in processed.values())
    grand_total = sum(d['stats']['total'] for d in processed.values())
    grand_pct = round(grand_done / grand_total * 100) if grand_total else 0

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=3">
<title>Last War: Research Tree Tracker</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%231a1a2e'/><text x='16' y='23' text-anchor='middle' font-size='20'>🔬</text></svg>">
<style>
@import url("https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&display=swap");
{CSS}
</style>
</head>
<body>

<nav class="guide-nav">
  <a href="./" class="nav-home current">&#8592; Home</a>
  <a href="guides/alliance_support_hub.html">Alliance Hub</a>
  <a href="guides/building_planner.html">Building Planner</a>
  <a href="guides/building_reference.html">Building Ref</a>
  <a href="guides/capitol_positions.html">Capitol Positions</a>
  <a href="guides/chip_lab_guide.html">Chip Lab</a>
  <a href="guides/radar_guide.html">Radar</a>
  <a href="guides/vs_weekly_planner.html">VS Planner</a>
  <a href="guides/waterfall_guide.html">Waterfall</a>
</nav>

<div class="page-header">
    <div class="game-badge">Last War: Survival</div>
    <img src="skynet_logo.png" class="logo" alt="">
    <h1>Research Tree Tracker</h1>
    <p class="subtitle">Interactive Tech Tree Progress Tracker &bull; All Servers &bull; <span id="grand-stats">Overall: {grand_done}/{grand_total} ({grand_pct}%)</span></p>
    <div class="header-actions">
        <button class="header-btn export" id="btn-export">Export CSV</button>
        <label for="csv-file-input" class="header-btn import" style="cursor:pointer;display:inline-block">Import CSV</label>
        <input type="file" id="csv-file-input" accept=".csv" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);opacity:0">
        <button class="header-btn reset" id="btn-reset">Reset</button>
    </div>
</div>

<div class="legend">
    <span class="legend-label">Legend:</span>
    <div class="legend-item"><span class="legend-swatch sw-maxed"></span> Maxed</div>
    <div class="legend-item"><span class="legend-swatch sw-progress"></span> In Progress</div>
    <div class="legend-item"><span class="legend-swatch sw-blocked"></span> Blocked</div>
    <div class="legend-item"><span class="legend-swatch sw-available"></span> Available</div>
    <div class="legend-item"><span class="legend-swatch sw-locked"></span> Locked</div>
    <div class="legend-item"><span class="legend-swatch sw-rec">1</span> Recommended</div>
</div>

<div class="band-label">Strategy &amp; Support Trees</div>
<div class="band" id="band1">
{band1_html}
</div>

<div class="band-label">Combat &amp; Squad Trees</div>
<div class="band" id="band2">
{band2_html}
</div>

<div class="page-footer">Built for Last War: Survival players &bull; Data from <a href="https://cpt-hedge.com/calculators/research" target="_blank">cpt-hedge.com</a> &bull; Created by Extremesecrecy</div>

<div id="tooltip" class="tooltip"></div>

<div class="editor-backdrop" id="editor-backdrop"></div>
<div class="editor-popup" id="editor-popup">
    <button class="ep-close">&times;</button>
    <div class="ep-title"></div>
    <div class="ep-level"></div>
    <div class="ep-controls">
        <button class="ep-btn ep-minus">&minus;</button>
        <button class="ep-btn ep-plus">+</button>
        <button class="ep-btn max-btn ep-max">MAX</button>
    </div>
    <div class="ep-cost"></div>
    <div class="ep-pri"></div>
    <div class="ep-rec"></div>
    <div class="ep-detail"></div>
</div>

<script>
const TREE_DATA = {json.dumps(js_data, separators=(',', ':'))};
const TREE_ORDER = {json.dumps(tree_order)};
const ORIGINAL_LEVELS = {json.dumps(original_levels, separators=(',', ':'))};
const RECOMMENDED_PATH = {json.dumps(rec_path_js, separators=(',', ':'))};
{JS}
</script>

</body>
</html>'''

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Wrote {OUTPUT} ({len(html):,} bytes)')
    print(f'  Grand total: {grand_done}/{grand_total} levels ({grand_pct}%)')
    for tk in BAND1 + BAND2:
        if tk in processed:
            s = processed[tk]['stats']
            print(f'  {DISPLAY_NAMES.get(tk, tk):20s}: {s["done"]:4d}/{s["total"]:4d} ({s["pct"]}%)')


if __name__ == '__main__':
    main()
