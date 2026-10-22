"""Rebuild every hand-made SVG in assets/.  Usage: python scripts/build_art.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import art_cards  # noqa: E402
import art_hero  # noqa: E402
import art_sections  # noqa: E402
from art_common import write  # noqa: E402

if __name__ == "__main__":
    write("hero.svg", art_hero.build())
    write("terminal.svg", art_sections.terminal())
    write("neofetch.svg", art_sections.neofetch())
    write("divider.svg", art_sections.divider())
    write("footer.svg", art_sections.footer())
    for name, content in art_cards.build_all():
        write(f"cards/{name}.svg", content)
