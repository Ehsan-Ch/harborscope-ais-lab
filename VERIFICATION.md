# Release verification — 17 November 2026

## Research release

Code/data release: `d8e1dcee1e8433e4153e24c00a3e49dc803b0e76`. All 27 release files matched local Git blob hashes. The nationwide raw archive is excluded.

[Research checks](https://github.com/Ehsan-Ch/harborscope-ais-lab/actions/runs/44096726529) succeeded on Python 3.11, Python 3.12 and Node 22. There are 12 Python tests and 4 JavaScript tests. The retained-data reconciliation reproduced all 38 episodes, all sensitivity summaries, 12,506 observations and protocol/source/point integrity checks.

The initial release's Python 3.11 verification exposed an exact-float comparison issue: one mean latitude differed by 2.13e-14 degrees because Python versions sum floats differently. Verification now uses relative tolerance 1e-12/absolute 1e-9 for numeric results; IDs, counts, states, timestamps and cryptographic checks remain exact. The segmentation and data artifacts were unchanged. The corrected release passed both versions.

## Browser evidence

The [public lab](https://ehsan-ch.github.io/harborscope-ais-lab/) loaded the full study. Cargo/reported-moored filters selected 13 episodes across 13 vessels (232.5 observed vessel-hours). Every exported episode ID, duration, start and end timestamp matched the saved report. Local tanker/reported-anchor selection similarly reconciled 12 episodes across 10 vessels.

The public V001 track replay showed zero sampled positions at 00:00:59UTC and 10 positions at 01:00:59UTC. The local V004 replay showed the same 0→10 visibility progression. Full-day episode statistics remained explicitly retrospective. Desktop plot, controls and the ledger were visually inspected. Mobile and exhaustive cross-browser checks are not claimed.

## Deployment

The [Pages deployment](https://github.com/Ehsan-Ch/harborscope-ais-lab/actions/runs/44096727904) succeeded for the research release above. The public report, filters, replay and CSV export were verified after deployment.

## Limits

CI reconstructs episodes from included retained points, not from a fresh download of the national archive. Local extraction did stream the full downloaded archive. The SHA256 is a local integrity pin, not an independent publisher checksum. The data comprise one holiday and one rectangle; observed dwell is not validated berth occupation, port turnaround or waiting time. See RESEARCH.md.
