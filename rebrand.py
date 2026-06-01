"""Rebrand site visual branding between alliances.

Re-run safely. Edit the BRAND dict + REPLACEMENTS below, then run:

    python rebrand.py            # apply changes
    python rebrand.py --dry-run  # show diff without writing

Backups land in `.rebrand-backup/<timestamp>/` so accidents are recoverable.

Design intent:
- Single source of truth: BRAND dict at top
- Idempotent: running twice on same input is safe
- Reversible: backups in .rebrand-backup/
- Auditable: --dry-run prints diffs before any write
- Future-proof: next alliance change = edit 4 lines (BRAND dict), run, commit

What it REPLACES:
- Visible UI branding strings (alliance-tag boxes, footers, page titles,
  README headers, hero banners)

What it PRESERVES (intentionally):
- JS localStorage namespace prefixes (e.g. `[OWOW Storage]`, `owow-hero-planner`)
  — changing would orphan users' saved data
- Game-data diplomatic mentions where the old alliance is listed as one
  of many alliances (e.g. friend tables in s1_land_captures.html)
- File extensions, image filenames, and any line containing `# rebrand-skip`
"""

from __future__ import annotations

import argparse
import difflib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ---------- CONFIG ----------

BRAND = {
    "old_tag": "OWOW",
    "old_name": "Old World Order",
    "new_tag": "RGBB",
    "new_name": "Raging Black Bulls",
}

# Replacement patterns — applied in order, most-specific first.
# Format: (find_string, replace_template). {old_tag}/{old_name}/{new_tag}/{new_name}
# are substituted from BRAND at runtime.
REPLACEMENTS = [
    # Most-specific full alliance tag + name
    ("[{old_tag}] {old_name}", "[{new_tag}] {new_name}"),
    # Brand banner combinations
    ("Kristen {old_tag} SKYNET", "Kristen {new_tag} SKYNET"),
    ("{old_tag} SKYNET", "{new_tag} SKYNET"),
    # Doc attribution
    ("{old_tag} Strategic Command", "{new_tag} Strategic Command"),
    # Title bar variants
    (" - {old_tag}</title>", " - {new_tag}</title>"),
    (" - {old_tag} |", " - {new_tag} |"),
    ("{old_tag} |", "{new_tag} |"),
    # README footer
    ("Built by **[{old_tag}] {old_name}**", "Built by **[{new_tag}] {new_name}**"),
    # README header
    ("# [{old_tag}] Last War: Survival", "# [{new_tag}] Last War: Survival"),
    ("![{old_tag} SKYNET]", "![{new_tag} SKYNET]"),
    # Strategic reference footer pattern
    ("for [{old_tag}] {old_name}", "for [{new_tag}] {new_name}"),
    ("reference for [{old_tag}]", "reference for [{new_tag}]"),
    # Attribution patterns (data note headers, source credits)
    ("{old_tag} Strategy Guide", "{new_tag} Strategy Guide"),
    ("{old_tag} strategy guide", "{new_tag} strategy guide"),
    # Spanish escaped-unicode variants in i18n string literals.
    # File content stores accented chars as their 6-char Unicode-escape sequence
    # (e.g. literal backslash-u-0-0-e-9 = é, backslash-u-0-0-f-3 = ó). We use
    # escaped backslashes so the search pattern matches the literal bytes in the file.
    ("estrat\\u00e9gica {old_tag}", "estrat\\u00e9gica {new_tag}"),
    ("Estrat\\u00e9gica {old_tag}", "Estrat\\u00e9gica {new_tag}"),
    ("Recomendaci\\u00f3n {old_tag}", "Recomendaci\\u00f3n {new_tag}"),
    ("miembros de {old_tag}", "miembros de {new_tag}"),
    ("alianza {old_tag}", "alianza {new_tag}"),
    ("{old_tag} Alliance Tools", "{new_tag} Alliance Tools"),
    ("{old_tag} Discord", "{new_tag} Discord"),
    # Page titles + UI labels
    ("{old_tag} Lucky Roll", "{new_tag} Lucky Roll"),
    ("{old_tag} Hero Planner", "{new_tag} Hero Planner"),
    ("{old_tag} Recommendation", "{new_tag} Recommendation"),
    ("{old_tag} alliance", "{new_tag} alliance"),
    ("{old_tag} Alliance", "{new_tag} Alliance"),
    ("{old_tag} palette", "{new_tag} palette"),
    ("{old_tag} nav", "{new_tag} nav"),
    ("{old_tag} NAVIGATION", "{new_tag} NAVIGATION"),
    # Combat data analytics (zombie_boss_chart.html)
    ("{old_tag} RALLY", "{new_tag} RALLY"),
    ("{old_tag} Troops Lost", "{new_tag} Troops Lost"),
    ("{old_tag} Lost", "{new_tag} Lost"),
    ("{old_tag} troops lost", "{new_tag} troops lost"),
    ("{old_tag} troops", "{new_tag} troops"),
    ("{old_tag} win/loss", "{new_tag} win/loss"),
    ("{old_tag} battle reports", "{new_tag} battle reports"),
    ("{old_tag} calibration", "{new_tag} calibration"),
    ("{old_tag}/DOc", "{new_tag}/DOc"),  # rally outcome attribution
    # Discord bot alliance team — OWOW-OFNA → RGBB-OFNA
    ("{old_tag}-OFNA", "{new_tag}-OFNA"),
    ("{old_tag} or OFNA", "{new_tag} or OFNA"),
    ("{old_tag}, OFNA", "{new_tag}, OFNA"),
    ("Member, {old_tag}, OFNA", "Member, {new_tag}, OFNA"),
    # In-game data verification attributions (virus_resistance.html historical refs)
    ("{old_tag} VERIFIED", "{new_tag} VERIFIED"),
    ("{old_tag} verified in-game", "{new_tag} verified in-game"),
    ("{old_tag} in-game verified", "{new_tag} in-game verified"),
    ("{old_tag} In-Game Verified", "{new_tag} In-Game Verified"),
    ("{old_tag} in-game", "{new_tag} in-game"),
    ("by {old_tag} members", "by {new_tag} members"),
    ("{old_tag} members", "{new_tag} members"),
    ("{old_tag} rally data", "{new_tag} rally data"),
    ("{old_tag}-verified", "{new_tag}-verified"),
    # Bracketed tag with no name
    ("[{old_tag}]", "[{new_tag}]"),
    # img alt attribute (some pages have bare alt="OWOW")
    ('alt="{old_tag}"', 'alt="{new_tag}"'),
    # Standalone full name
    ("{old_name}", "{new_name}"),
]

# Lines containing ANY of these markers are skipped entirely (no replacements applied).
# This protects localStorage keys, JS log prefixes, game-data diplomatic refs.
PRESERVE_MARKERS = [
    "[OWOW Storage]",         # JS console log prefix
    "OWOW STORAGE",           # JS comment block header
    "owow-hero-planner",      # localStorage key (would orphan saved data)
    "owow-building-planner",  # localStorage key
    "owow-s1-territory-map",  # localStorage key
    "owow-",                  # any localStorage namespace
    "# rebrand-skip",         # explicit escape hatch
]

# Files to skip outright (binary, vendor, generated)
SKIP_DIRS = {
    ".git", ".github", ".rebrand-backup",
    "tree_data", "battle_reports", "pictures",
    "researchtrees", "__pycache__", ".cache",
    "guides/s2",  # screenshots only
    "guides/s1",  # would have screenshots if added
}

# Process these file extensions only
PROCESS_EXTS = {".html", ".md", ".js"}


# ---------- LOGIC ----------

def compile_patterns() -> list[tuple[str, str]]:
    """Substitute the BRAND vars into each REPLACEMENTS template."""
    out = []
    for find_tpl, repl_tpl in REPLACEMENTS:
        find = find_tpl.format(**BRAND)
        repl = repl_tpl.format(**BRAND)
        out.append((find, repl))
    return out


def should_skip_dir(rel_path: Path) -> bool:
    parts = rel_path.parts
    for part in parts:
        if part in SKIP_DIRS:
            return True
    # Also match guides/s2 etc
    rel_str = str(rel_path).replace("\\", "/")
    for skip in SKIP_DIRS:
        if rel_str.startswith(skip + "/") or rel_str == skip:
            return True
    return False


def should_skip_file(path: Path) -> bool:
    if path.suffix.lower() not in PROCESS_EXTS:
        return True
    # Read first 500 chars to check for `# rebrand-skip` marker
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:500]
        if "# rebrand-skip" in head:
            return True
    except Exception:
        return True
    return False


def line_has_preserve_marker(line: str) -> bool:
    for marker in PRESERVE_MARKERS:
        if marker in line:
            return True
    return False


def transform_text(text: str, patterns: list[tuple[str, str]]) -> tuple[str, int]:
    """Apply replacement patterns line-by-line, skipping protected lines.

    Returns (new_text, line_change_count).
    """
    out_lines = []
    changes = 0
    for line in text.split("\n"):
        if line_has_preserve_marker(line):
            out_lines.append(line)
            continue
        new_line = line
        for find, repl in patterns:
            if find in new_line:
                new_line = new_line.replace(find, repl)
        if new_line != line:
            changes += 1
        out_lines.append(new_line)
    return "\n".join(out_lines), changes


def find_files(root: Path) -> list[Path]:
    out = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if should_skip_dir(rel):
            continue
        if should_skip_file(path):
            continue
        out.append(path)
    return out


def make_diff(old: str, new: str, filename: str) -> str:
    diff_lines = difflib.unified_diff(
        old.splitlines(keepends=False),
        new.splitlines(keepends=False),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=1,
    )
    return "\n".join(diff_lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="Show diff without writing")
    ap.add_argument("--root", default=".", help="Repo root (default: cwd)")
    ap.add_argument("--limit-diff-lines", type=int, default=12,
                    help="Max diff lines per file to print in dry-run")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    print(f"Rebrand from [{BRAND['old_tag']}] {BRAND['old_name']}")
    print(f"           to [{BRAND['new_tag']}] {BRAND['new_name']}")
    print(f"Repo root: {root}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'APPLY'}")
    print()

    patterns = compile_patterns()
    files = find_files(root)
    print(f"Scanning {len(files)} eligible files...")
    print()

    backup_dir = root / ".rebrand-backup" / datetime.now().strftime("%Y%m%d-%H%M%S")
    total_changed_files = 0
    total_changed_lines = 0

    for path in files:
        try:
            old_text = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  SKIP (read error): {path.relative_to(root)} -- {e}")
            continue
        new_text, changes = transform_text(old_text, patterns)
        if changes == 0:
            continue
        total_changed_files += 1
        total_changed_lines += changes
        rel = path.relative_to(root).as_posix()
        print(f"~ {rel}  ({changes} lines changed)")
        if args.dry_run:
            diff = make_diff(old_text, new_text, rel)
            for i, dl in enumerate(diff.split("\n")):
                if i >= args.limit_diff_lines:
                    print(f"    ... (truncated; {changes} line(s) total)")
                    break
                print(f"    {dl}")
        else:
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / rel
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup_path)
            path.write_text(new_text, encoding="utf-8")

    print()
    print(f"=== Summary ===")
    print(f"  Files changed: {total_changed_files}")
    print(f"  Total lines modified: {total_changed_lines}")
    if not args.dry_run and total_changed_files > 0:
        print(f"  Backups: {backup_dir.relative_to(root).as_posix()}")
    if args.dry_run:
        print("  (No files written. Re-run without --dry-run to apply.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
