#!/usr/bin/env python3
# screenshot.py — regenerate the README hero (docs/freki-reap.png).
#
# Renders a REPRESENTATIVE `freki reap` (illustrative fake acme-* data, not a live
# run — freki queries GitHub by owner) into a clean terminal-window PNG matching
# the rest of the toolkit's shots.
#
# Dev-only.  pip3 install --user rich cairosvg  &&  python3 docs/screenshot.py
import os, tempfile
from rich.console import Console
from rich.text import Text
import cairosvg

LINES = [
    "",
    "  [bold]freki reap[/]  [dim]· estate cruft summary · ~/github-repos[/]",
    "",
    "  [bold]branches[/]    24 reapable across 6 repo(s)",
    "  [bold]prs[/]         3 abandoned (of 11 open)",
    "  [bold]artifacts[/]   8 reapable (142MB of 210MB across 20 total)",
    "  [bold]releases[/]    2 reapable (of 4 draft/pre)",
    "",
    "  [dim]37 thing(s) reapable across the estate — apply per-command:[/]",
    "  [bold]freki branches|prs|artifacts|releases --apply[/]",
    "",
]

texts = [Text.from_markup(l) for l in LINES]
con = Console(record=True, width=max(t.cell_len for t in texts) + 2)
for t in texts:
    con.print(t)
svg = tempfile.mktemp(suffix=".svg")
con.save_svg(svg, title="freki reap")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "freki-reap.png")
cairosvg.svg2png(url=svg, write_to=out, scale=2)
os.unlink(svg)
print("wrote", out)
