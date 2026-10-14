"""Tests for the script that rewrites the recently active list in the profile README."""

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "update-recent-repositories.py"
spec = importlib.util.spec_from_file_location("update_recent_repositories", SCRIPT)
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


def repo(name, description=None, **flags):
    return {
        "name": name,
        "html_url": f"https://github.com/tiavelum/{name}",
        "description": description,
        "private": flags.get("private", False),
        "visibility": "private" if flags.get("private") else "public",
        "fork": flags.get("fork", False),
        "archived": flags.get("archived", False),
    }


PAGE = [
    repo("tiavelum"),
    repo("job-search", private=True),
    repo("claude-setup"),
    repo(
        "engineering-standards",
        "engineering standards for the development of git repository content",
    ),
    repo("some-fork", fork=True),
    repo("claude-mechanics"),
    repo("old-project", archived=True),
    repo("claude-pacer"),
    repo("claude-roadmap"),
    repo("git-autosync"),
    repo("claude-project-harness-scratch"),
]


class SelectTest(unittest.TestCase):
    def test_keeps_six_public_own_repositories_in_order(self):
        names = [r["name"] for r in script.select([PAGE], "tiavelum", 6)]
        self.assertEqual(
            names,
            [
                "claude-setup",
                "engineering-standards",
                "claude-mechanics",
                "claude-pacer",
                "claude-roadmap",
                "git-autosync",
            ],
        )

    def test_never_lists_a_private_repository(self):
        leaked = dict(repo("job-search"), private=True)
        self.assertFalse(script.is_listed(leaked, "tiavelum"))
        missing_flag = {k: v for k, v in repo("job-search").items() if k != "private"}
        self.assertFalse(script.is_listed(missing_flag, "tiavelum"))

    def test_continues_across_pages(self):
        first = [repo("a", fork=True)] * 3
        second = [repo("b"), repo("c")]
        names = [r["name"] for r in script.select([first, second], "tiavelum", 6)]
        self.assertEqual(names, ["b", "c"])


class RenderTest(unittest.TestCase):
    def test_renders_link_and_optional_description(self):
        block = script.render([repo("a", "  one\n two "), repo("b")])
        self.assertEqual(
            block,
            "- [a](https://github.com/tiavelum/a): one two\n- [b](https://github.com/tiavelum/b)",
        )


class ReplaceSectionTest(unittest.TestCase):
    def test_replaces_only_between_markers(self):
        text = f"intro\n{script.START_MARKER}\nold\n{script.END_MARKER}\noutro\n"
        expected = f"intro\n{script.START_MARKER}\nnew\n{script.END_MARKER}\noutro\n"
        self.assertEqual(script.replace_section(text, "new"), expected)

    def test_is_stable_when_list_unchanged(self):
        text = f"{script.START_MARKER}\nsame\n{script.END_MARKER}\n"
        self.assertEqual(script.replace_section(text, "same"), text)

    def test_rejects_missing_markers(self):
        with self.assertRaises(ValueError):
            script.replace_section("no markers here", "new")


if __name__ == "__main__":
    unittest.main()
