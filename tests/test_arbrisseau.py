import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arbrisseau import fcrs, svg  # noqa: E402


class ArbrisseauTest(unittest.TestCase):
    def test_one_circle_per_node(self):
        self.assertEqual(svg((1, (2, 4, None), 3)).count("<circle"), 4)
        self.assertEqual(svg(("A", ["B", "C", "D"]), general=True).count("<circle"), 4)

    def test_empty_tree(self):
        self.assertIn(">empty<", svg(None))

    def test_keys_are_escaped(self):
        self.assertIn("a&lt;b", svg("a<b"))

    def test_fcrs(self):
        self.assertEqual(fcrs([("A", ["B", "C"]), "D"]), ("A", ("B", None, "C"), "D"))

    def test_wraps_on_narrow_screens(self):
        wide = svg(*[(1, (2, 3, 4), (5, 6, 7))] * 3, captions=["t"] * 3)
        self.assertLess(int(wide.split('width="')[1].split('"')[0]), 400)


if __name__ == "__main__":
    unittest.main()
