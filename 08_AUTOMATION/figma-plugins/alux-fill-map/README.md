# ALUX — Fill Graphics Map (local Figma plugin)

`code.js` is **generated per episode and not committed**: it embeds the client's script text and episode artwork,
and this repository is public.

```bash
.venv/bin/python 08_AUTOMATION/Scripts/episode/figma_fill.py /path/to/episode   # writes code.js here
```

Then in Figma Desktop: Plugins → Development → Import plugin from manifest → `manifest.json` → run **ALUX — Fill Graphics Map**.
Run **ALUX — Apply brand font** first if new templates were added.
