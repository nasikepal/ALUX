---
type: rules
tags: [system/captions]
---

# Caption Rules

The default ALUX caption style. Set by Rijal in Premiere on EP001 (2026-09-25). Every episode follows it.
The machine-readable copy lives at `00_SYSTEM/brand/caption_style.json` and is what the pipeline reads.

## Style (4K sequence, 3840×2160)

| | |
|---|---|
| Font | **Gilroy-Bold** |
| Size | **72** |
| Text box | 2880 × 648 px, centered horizontally |
| Position | 0.125 : 0.65 (box top-left at 480, 1404 px; box bottom is 108 px above the bottom edge) |
| Alignment | as set in Premiere (raw enum values are in `caption_style.json`) |
| Colour, shadow, background | Premiere defaults, untouched |
| Delivery | graphics on **V3** (captions → *Upgrade Caption to Graphic*), not a caption track |

## Text

- Script spelling wherever the VO matches it (numbers and names are written the way the script writes them).
- Where the narrator changed a word, the VO wins. Tie-breaks go to a second transcription pass, then a 3-model re-listen.
- Punctuation follows how it was **spoken**:
  - When the narrator runs two script sentences together with *but/and/or/so*, the period becomes a comma: "that number, but here's…", "built for, so start…".
  - No comma in "…or not".
  - Openers "Now, / So, / Well," take a comma. "We'll" is not "Well".
- Chapter titles read aloud get their own caption, in title case, with a period: `Chapter 5B: The Company That Invented 60,000 People.`

## Layout and timing

- ≤ 42 characters per line, ≤ 2 lines, balanced line breaks, no line ending on a function word.
- Minimum duration 5/6 s, maximum 6 s, break at pauses ≥ 0.45 s.
- In-point 0.12 s before the first word, 0.25 s tail, 2-frame gap between captions (24 fps).

## Workflow

```bash
python episode_cli.py captions <ep> --words words_final.json --check words_pass2.json --premiere
```

Then in Premiere, select the caption track → *Upgrade Caption to Graphic* → move to V3. The style above is the target.
QC before delivery: `captions_review.md` REVIEW = 0, overlaps = 0, lines > 42 = 0.
