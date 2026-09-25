---
name: alux-setup
description: Set up or repair the ALUX production environment on a machine — Claude Bridge panel for Premiere, whisper + models, ffmpeg/ImageMagick/gh/uv, Python .venv, Gilroy fonts, Figma MCP and Figma plugins. Use when someone opens this repo on a new PC, says "setup", "install", "PC baru", "laptop baru", or when a pipeline command fails because a tool, model, font or the Premiere bridge is missing.
---

# ALUX setup

One installer does the whole machine: `setup/install.py` (macOS + Windows, stdlib only, idempotent).

## Steps

1. **Check first** — never install blind:
   ```bash
   python3 setup/install.py --check        # Windows: py setup\install.py --check
   ```
   Show the user the ✓/✗ table in a few lines. If it says READY, stop at step 4.

2. **Install what is missing.** Say what will happen in one sentence first — it downloads ~1.8 GB of whisper models,
   installs packages with Homebrew (macOS) or winget (Windows), copies the Claude Bridge panel into Adobe's CEP folder,
   and sets Adobe's `PlayerDebugMode=1` (needed for unsigned panels). Then run:
   ```bash
   python3 setup/install.py
   ```
   Long step (model download): run it in the background and report progress, don't block.

3. **Fonts** are licensed and never in this public repo. The installer searches Google Drive for the folder
   `Gilroy_fixed (INSTALL INI)`. If it isn't found, ask the user to make that Drive folder available offline, then:
   ```bash
   python3 setup/install.py --only fonts --fonts "<path to Gilroy_fixed (INSTALL INI)>"
   ```
   Only that folder — the original Gilroy files have broken names and break Figma/Premiere text.

4. **Manual steps** — walk the user through what the installer printed under "Still to do by hand", one at a time,
   and verify each where you can:
   - **Premiere:** restart → Window › Extensions › Claude Bridge → panel says *connected*. Verify:
     ```bash
     .venv/bin/python -c "import sys; sys.path.insert(0,'08_AUTOMATION/Scripts'); from episode import premiere; print(premiere.bridge_alive())"
     ```
     Then a round trip: write `app.version;` to a .jsx and pass it to `premiere.run()` — it must return the version.
   - **Figma MCP:** `/mcp` → figma → Authenticate. `.mcp.json` in the repo already declares the server.
   - **Figma plugins:** Figma desktop → Plugins → Development → Import plugin from manifest → each
     `08_AUTOMATION/figma-plugins/*/manifest.json`. `alux-fill-map/code.js` is generated per episode by
     `08_AUTOMATION/Scripts/episode/figma_fill.py` (client data — never commit it).
   - **GitHub:** `gh auth login` with an account that has contributor access to `nasikepal/ALUX`.

5. **Finish** with `python3 setup/install.py --check` → must print READY. Report in one short block: what was installed,
   what the user still has to do.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `TIMEOUT: bridge tidak merespon` | Panel closed, or a dialog is open in Premiere (the panel only runs scripts when Premiere is idle). Close dialogs, reopen the panel. |
| Panel missing from Window › Extensions | PlayerDebugMode not set for this Premiere's CSXS version — re-run `--only bridge`, restart Premiere. |
| Windows: tool installed but still ✗ | winget changes PATH only for new terminals — open a new one and re-run `--check`. |
| whisper very slow | Model on a network drive, or Windows without GPU build — expected; transcription of 1 h VO ≈ 4 min on Apple Silicon. |
| Gilroy shows as missing in Figma | Figma desktop must be restarted after installing fonts; web Figma needs the Figma font helper. |

Style and caption rules the pipeline follows live in `00_SYSTEM/Caption Rules.md` and `00_SYSTEM/brand/`.
