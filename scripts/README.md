# scripts

This directory holds the script that keeps the "Recently active" list on the tiavelum profile current; it is for anyone maintaining this repository.

## Getting started

Requires Python 3.13 and network access to `api.github.com`. Run from the repository root:

```bash
python3 scripts/update-recent-repositories.py README.md
```

```
README.md: list unchanged
```

When a repository has been pushed since the last run, the output is `README.md: list updated with 6 repositories` and the lines between the marker comments in `README.md` change.

## What it lists

The six most recently pushed repositories of tiavelum that are public, not forks, not archived and not this repository. Each line holds the name, a link and the description where the repository has one. A repository without a description is listed by name only.

## Content and structure

| Path | Contains |
|---|---|
| `scripts/update-recent-repositories.py` | The script; it uses only the Python standard library |
| `tests/test-update-recent-repositories.py` | Its tests, run with `python3 tests/test-update-recent-repositories.py` |
| `.github/workflows/update-recent-repositories.yml` | Runs the script every Monday at 06:47 Europe/Zurich and on manual dispatch, and commits `README.md` when the list changed |
| `.github/workflows/checks.yml` | Runs Ruff and the tests on every pull request and push to `main` |
| `deviations.md` | The engineering standards this repository sets aside, with reasons |

## How it works

The script reads `/users/tiavelum/repos` sorted by push date, keeps the first six repositories that pass the filter, and replaces everything between `<!-- recent-repositories:start -->` and `<!-- recent-repositories:end -->` in `README.md`. It writes the file only when the list differs, so the workflow's `git diff` finds nothing to commit on an unchanged week. The endpoint returns only public repositories, and the script rejects any repository marked private as well.

## Known limits

GitHub disables a scheduled workflow in a public repository after 60 days without activity in it. Since the workflow commits only when the list changes, a long pause in pushing switches the schedule off; re-enable it under Actions in this repository.
