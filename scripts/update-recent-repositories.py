"""Rewrite the recently active section of the profile README from the public GitHub API."""

import json
import os
import sys
import urllib.request
from pathlib import Path

OWNER = "tiavelum"
LIMIT = 6
START_MARKER = "<!-- recent-repositories:start -->"
END_MARKER = "<!-- recent-repositories:end -->"
API_URL = (
    "https://api.github.com/users/{owner}/repos"
    "?type=owner&sort=pushed&direction=desc&per_page=100&page={page}"
)


def fetch_page(owner: str, page: int, token: str | None) -> list[dict]:
    request = urllib.request.Request(
        API_URL.format(owner=owner, page=page),
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    # The workflow token only raises the rate limit: it is scoped to this repository,
    # and the /users/{owner}/repos endpoint returns public repositories in any case.
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def is_listed(repo: dict, owner: str) -> bool:
    # Private repositories are excluded here as well as by the endpoint, so that a
    # broader token in the future cannot put one on the public profile.
    return (
        not repo.get("private", True)
        and repo.get("visibility", "public") == "public"
        and not repo.get("fork", False)
        and not repo.get("archived", False)
        and not repo.get("disabled", False)
        and repo.get("name") != owner
    )


def select(pages: list[list[dict]], owner: str, limit: int) -> list[dict]:
    selected = []
    for page in pages:
        for repo in page:
            if is_listed(repo, owner):
                selected.append(repo)
                if len(selected) == limit:
                    return selected
    return selected


def render(repos: list[dict]) -> str:
    lines = []
    for repo in repos:
        line = f"- [{repo['name']}]({repo['html_url']})"
        description = " ".join((repo.get("description") or "").split())
        if description:
            line += f": {description}"
        lines.append(line)
    return "\n".join(lines)


def replace_section(text: str, block: str) -> str:
    start = text.find(START_MARKER)
    end = text.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"README must contain {START_MARKER} followed by {END_MARKER}")
    head = text[: start + len(START_MARKER)]
    return f"{head}\n{block}\n{text[end:]}"


def iter_pages(owner: str, token: str | None):
    page = 1
    while True:
        repos = fetch_page(owner, page, token)
        if not repos:
            return
        yield repos
        page += 1


def collect(owner: str, limit: int, token: str | None) -> list[dict]:
    pages = []
    for page in iter_pages(owner, token):
        pages.append(page)
        if len(select(pages, owner, limit)) == limit:
            break
    return select(pages, owner, limit)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} README.md", file=sys.stderr)
        return 2
    readme = Path(argv[1])
    repos = collect(OWNER, LIMIT, os.environ.get("GITHUB_TOKEN"))
    old = readme.read_text(encoding="utf-8")
    new = replace_section(old, render(repos))
    if new == old:
        print(f"{readme}: list unchanged")
        return 0
    readme.write_text(new, encoding="utf-8")
    print(f"{readme}: list updated with {len(repos)} repositories")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
