"""Draw the README pictures into docs/. Run: python examples/gallery.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from arbrisseau import fcrs, svg  # noqa: E402

BST = (8, (3, 1, (6, 4, 7)), (10, None, (14, 13, None)))
FOREST = [("A", ["B", ("C", ["E", "F"]), "D"])]

PICTURES = {
    "bst": svg(BST),
    "rotation": svg((5, (3, 2, 4), 8), (3, 2, (5, 4, 8)), captions=["before", "after a right rotation"]),
    "heap": svg((9, (7, 3, 5), (8, 1, None)), captions=["max heap"]),
    "general": svg(FOREST[0], general=True, captions=["general tree"]),
    "fcrs": svg(fcrs(FOREST), captions=["first child - right sibling"]),
}

if __name__ == "__main__":
    (ROOT / "docs").mkdir(exist_ok=True)
    for name, text in PICTURES.items():
        (ROOT / "docs" / f"{name}.svg").write_text(text)
        print(f"docs/{name}.svg")
