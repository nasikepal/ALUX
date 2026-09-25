# ALUX Production OS — notes for Claude Code / agents

**New machine or something missing?** Run the `alux-setup` skill (or `python3 setup/install.py --check`).
Nothing below works until that prints READY.

## Pipeline (per episode, episode data lives outside this repo)

```bash
.venv/bin/python 08_AUTOMATION/Scripts/episode_cli.py build <ep>        # docx + VO -> script/timeline
.venv/bin/python 08_AUTOMATION/Scripts/episode_cli.py transcribe <ep>   # whisper, word timing
.venv/bin/python 08_AUTOMATION/Scripts/episode_cli.py cues <ep>         # graphics cues on the spoken word
.venv/bin/python 08_AUTOMATION/Scripts/episode_cli.py premiere <ep>     # sequence + markers via Claude Bridge
.venv/bin/python 08_AUTOMATION/Scripts/episode_cli.py captions <ep> --words words_final.json --check words_pass2.json --premiere
```

Premiere commands go through the Claude Bridge panel (`08_AUTOMATION/premiere-bridge/`) — Premiere must be open with
the panel showing *connected*.

## Rules

- This repo is **public**: never commit client scripts, VO, episode artwork, fonts or `alux-fill-map/code.js`.
- Captions: `00_SYSTEM/Caption Rules.md` (Gilroy-Bold 72, text rules, timing). Brand: `00_SYSTEM/brand/`.
- Work on a branch, open a PR; a human merges.
