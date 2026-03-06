# [OWOW] Last War: Survival — Strategic Tools

![OWOW SKYNET](skynet_banner.png)

## Live Site

**[Open the Tools](https://extremesecrecy.github.io/lastwar-research-trees/)**

## Tools & Guides

| Tool | Description |
|------|-------------|
| [Research Tree Tracker](https://extremesecrecy.github.io/lastwar-research-trees/research_trees_visual.html) | Interactive 16-tree research tracker with recommended path |
| [Building Planner](https://extremesecrecy.github.io/lastwar-research-trees/guides/building_planner.html) | Building progression planner with upgrade paths & power dashboard |
| [Event Calendar](https://extremesecrecy.github.io/lastwar-research-trees/guides/calendar.html) | Daily task reminders + server event timeline with ICS download |
| [VS Weekly Planner](https://extremesecrecy.github.io/lastwar-research-trees/guides/vs_weekly_planner.html) | Arms Race + VS Duel weekly schedule |
| [Waterfall Guide](https://extremesecrecy.github.io/lastwar-research-trees/guides/waterfall_guide.html) | Troop waterfall training method |
| [Radar Guide](https://extremesecrecy.github.io/lastwar-research-trees/guides/radar_guide.html) | Radar mission stacking system |
| [Alliance Support Hub](https://extremesecrecy.github.io/lastwar-research-trees/guides/alliance_support_hub.html) | Alliance Center levels & help mechanics |
| [Capitol Positions](https://extremesecrecy.github.io/lastwar-research-trees/guides/capitol_positions.html) | Capitol officer positions & buffs |
| [Chip Lab](https://extremesecrecy.github.io/lastwar-research-trees/guides/chip_lab_guide.html) | Chip Lab guide with real chip names |
| [Building Reference](https://extremesecrecy.github.io/lastwar-research-trees/guides/building_reference.html) | Building upgrade costs reference |

## Subscribe to the Calendar

Import this URL into Google Calendar, Apple Calendar, or Outlook:

```
https://extremesecrecy.github.io/lastwar-research-trees/guides/lastwar_calendar.ics
```

Or visit the [Event Calendar](https://extremesecrecy.github.io/lastwar-research-trees/guides/calendar.html) to set your server date and download a personalized calendar.

## AI Advisor

Export your progress as CSV, then upload it with the advisor prompt to get personalized strategic advice:

- [Research AI Advisor](https://raw.githubusercontent.com/extremesecrecy/lastwar-research-trees/main/ai_advisor_prompt.md) — Analyzes your research tree progress
- [Building AI Advisor](https://raw.githubusercontent.com/extremesecrecy/lastwar-research-trees/main/ai_building_advisor_prompt.md) — Analyzes your building progression

## For Developers

### Key Files

| File | Purpose |
|------|---------|
| `research_trees_visual.html` | Interactive research tracker (16 trees, recommended path) |
| `build_research_trees.py` | Build script for research tracker |
| `research_trees.csv` | Research progress data (import/export) |
| `recommended_path.json` | 75-step ordered research sequence |
| `tree_data/*.json` | Raw tree structure data (16 files) |
| `guides/*.html` | All guide pages (self-contained) |

### Color Legend

| Color | Meaning |
|-------|---------|
| Green | Maxed (all levels complete) |
| Orange | In Progress |
| Red dashed | Blocked (prerequisites not met) |
| Blue | Available to research |
| Gray | Locked |
| Gold pulsing | Recommended next step |

### Rebuilding

```bash
python build_research_trees.py    # Rebuild research tracker
python build_calendar.py          # Rebuild calendar + ICS
```

---

Built by **[OWOW] Old World Order**

*Kristen OWOW SKYNET. Ready for Judgment Day.*
