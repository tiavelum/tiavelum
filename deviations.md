# Deviations

This file lists, for anyone checking this repository against tiavelum/engineering-standards, the rules it sets aside and why.

## RL-1: README does not conform to the README contract

GitHub renders `README.md` of this repository as the tiavelum profile page, so it holds only what a profile visitor reads. How the repository works is described in `scripts/README.md`.
Recorded 2026-10-14.

## RM-1: no "Getting started", "Content and structure" or "License" section in the README

Same reason as RL-1: these sections would appear on the profile page. `scripts/README.md` answers them for this repository, and the licence is in `LICENSE`.
Recorded 2026-10-14.

## RM-3: the README opens with a greeting rather than a summary of the repository

The first paragraph is the profile's introduction to its visitors, not a description of the repository.
Recorded 2026-10-14.

## DOC-7: the README's first sentence does not state what it covers and for whom

Same reason as RM-3.
Recorded 2026-10-14.

## GW-2: the update workflow commits to main without a branch

The workflow rewrites the recently active list every week. A pull request for each change would need a manual merge and defeat the automation. It only ever changes the lines between the two marker comments in `README.md`.
Recorded 2026-10-14.
