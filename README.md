# [OWOW] Research Tree Visualizer

Interactive research tree tracker for **Last War: Survival**. Built for [OWOW] Old World Order, Server #2013.

## Quick Start

1. Open `research_trees_visual.html` in any modern browser (Chrome, Edge, Firefox)
2. That's it — no install, no server, no internet required

## Features

- **16 research trees** displayed in three horizontal bands with SVG connection lines
- **Click any node** to adjust your current level (+/-, MAX)
- **Color-coded states**: green = maxed, orange = in progress, blue = available, gray = locked
- **Recommended path**: gold pulsing badge = your next research, gray badges = future steps
- **Hover tooltips** show costs, prerequisites, remaining resources, and recommended step info
- **Auto-saves** to browser localStorage — your progress persists between sessions
- **Import/Export CSV** to share progress or back up data

## Color Legend

| Color | Meaning |
|-------|---------|
| Green border | Maxed (fully researched) |
| Orange border | In progress (partially researched) |
| Red dashed border | Blocked (in progress but next level prerequisites not met) |
| Blue border | Available (prerequisites met, ready to research) |
| Gray border | Locked (prerequisites not met) |
| Gold badge (pulsing) | Recommended next research |
| Gray badge | Future recommended research |

## Editing Progress

- **Click** any node to open the editor popup
- Use **-** / **+** to adjust level one at a time
- Use **MAX** to set the node to its maximum level
- Click outside or press **Escape** to close the editor
- Changes auto-save to your browser

## Recommended Path

The gold numbered badges show the universal "best research order" based on pro guides:

1. **Alliance Duel core** (Duel Expert doubles VS points!)
2. **Extra Hospitals** (save troops)
3. **Development tree** (build/research/train faster)
4. **Squad 1 tree** (main squad buffs)
5. **Hero tree Tier I** (all three branches)
6. **Special Forces start** (path to T10 troops)
7. **Defense Fort combat** (base defense)
8. **Squad 2 start** (secondary squad)

As you max nodes, the gold "UP NEXT" badge automatically moves to the next step.

## Import / Export

- **Export CSV**: Downloads your current progress as `research_trees.csv`
- **Import CSV**: Upload a CSV file to load progress (must have Tree, Node, Level, HaveIt columns)
- **Reset**: Reverts to the original CSV values baked into the HTML

## For Alliance Officers: Rebuilding

If you edit `research_trees.csv` or `recommended_path.json`, regenerate the HTML:

```bash
cd researchtrees
python build_research_trees.py
```

Requirements: Python 3.6+, no external packages needed.

### Files

| File | Purpose |
|------|---------|
| `research_trees_visual.html` | The app (open in browser) |
| `research_trees.csv` | Research progress data |
| `recommended_path.json` | Ordered research sequence |
| `build_research_trees.py` | Build script (generates HTML) |
| `tree_data/*.json` | Raw tree structure data |
| `DKCrayonCrumble.ttf` | Display font |
| `crayon.png` | OWOW logo |

## Sharing

To share with alliance members: zip the entire `researchtrees/` folder and send. They just unzip and open the HTML file.

## localStorage Note

Progress is saved per-browser. If you clear browser data or switch browsers, you'll revert to the CSV baseline baked into the HTML. Use **Export CSV** to back up your progress.
