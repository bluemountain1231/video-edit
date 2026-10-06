# video-talkcraft bridge catalog

This directory contains the pinned, machine-readable card catalog from
`video-talkcraft`. It is used by `scripts/semantic-plan.py` and
`scripts/talkcraft-match.py` to improve shot planning for koubo-edit.

The bridge intentionally excludes upstream TSX, HTML demos, audio, and runtime
dependencies. Those remain in the upstream checkout because
video-talkcraft is licensed under PolyForm Noncommercial 1.0.0. Read
[`LICENSE`](LICENSE), [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md), and
[`manifest.json`](manifest.json) before using any upstream implementation.

Refresh the catalog with:

```bash
python3 skills/koubo-edit/scripts/sync-video-talkcraft-catalog.py \
  --source /path/to/video-talkcraft \
  --destination skills/koubo-edit/assets/talkcraft-bridge
```
