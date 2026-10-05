# Animated poster GIFs (confetti, balloons, glitters)

The birthday and work-anniversary posters can now be rendered as **looping
animated GIFs** instead of static PNGs. The animation adds a professional
celebration feel:

- **Confetti** falls from the top of the poster.
- **Balloons** float upward.
- **Glitters** twinkle across the design.

The static PNG export is **unchanged** — the celebration layer is hidden in
`export-mode`, so the plain, professional poster is preserved for the daily
Teams delivery. The GIF is an opt-in extra.

The scheduled Teams pipeline now stores MP4 videos instead of GIFs. This
document remains for the standalone GIF renderer and historical output.

## How it works

The posters are HTML/CSS templates in `figma-export/`. GIF rendering uses
`figma-export/index-animated.html`; static PNG rendering continues to use
`figma-export/index.html`. The animation is driven by GSAP with elements
injected by `poster-templates.js`:

1. Each poster gets a `.celebration` layer (confetti pieces, balloons,
   glitters) with randomized positions, colors, and stagger delays.
2. The CSS defines `@keyframes` for `confetti-fall`, `balloon-float`, and
   `glitter-twinkle`, all looping over a shared `--anim-duration` (4s).
3. The template accepts a `?frame=0..1` query parameter. When present, the
   page enters `frame-mode`, which **pauses** the animation at that point in
   the loop using a negative `animation-delay` (`--frame-offset`).
4. `scripts/poster_flow/render_gif.py` renders N frames with headless Chrome,
   each frozen at a different progress value, then stitches them into a GIF
   with Pillow.

## Rendering a GIF

### Via the CLI (recommended)

```bash
cd "/home/thansika/Documents/Content creation V2 animation"

# The renderer captures the animated template automatically.

# Birthday
python3 -m scripts.poster_flow \
  --event birthday --name "Ananya" --title "Birthday" --kicker "Happy" \
  --message "May this year bring you even more success and happiness." \
  --gif --frames 20 --fps 10 \
  --out output/posters/birthday-ananya.gif

# Work anniversary
python3 -m scripts.poster_flow \
  --event work_anniversary --name "Ravi" --title "Work Anniversary" \
  --kicker "Happy" --years "Cheers to 5 years!" \
  --message "Wishing you continued success and happiness ahead." \
  --gif --frames 20 --fps 10 \
  --out output/posters/anniversary-ravi.gif
```

Flags:

| Flag | Default | Meaning |
|------|---------|---------|
| `--gif` | off | Render an animated GIF instead of a static PNG |
| `--frames` | 20 | Number of frames (more = smoother, larger file) |
| `--fps` | 10 | Frames per second (higher = faster loop) |
| `--out` | auto | Output GIF path |

### Via the module

```python
from scripts.poster_flow.render_gif import render_gif

out = render_gif(
    "birthday",
    {"name": "Ananya", "title": "Birthday", "kicker": "Happy",
     "message": "May this year bring you even more success and happiness."},
    frames=20,
    fps=10,
)
print(out)
```

Only `birthday` and `anniversary` template keys are supported (they are the
templates that carry celebration animations). Passing any other key raises a
`ValueError`.

## Teams delivery

Teams receives the rendered GIF, not the HTML or JavaScript source. Upload the
generated `.gif` to SharePoint, OneDrive, or hosted storage and send its file
link through the existing Power Automate webhook. Do not use the static WebP
base64 sender for GIFs; its Adaptive Card payload limit is intended for small
static images. For Teams, keep the GIF modest in size (roughly 12–20 frames,
540×675 or smaller) and verify the channel's file-upload permissions.

## Tuning

- **Loop length**: `--anim-duration` in `poster-templates.css` must match the
  GIF's total duration (`frames / fps`). The default 4s matches 20 frames @
  5fps or 40 frames @ 10fps. If you change the duration, update
  `ANIM_DURATION` in `render_gif.py` too.
- **File size**: GIFs are larger than WebP. For Teams delivery, keep the
  frame count modest (12–20) and consider downscaling. The static WebP path
  remains the default for the daily cron delivery.
- **Density**: adjust `CELEBRATION` counts in `poster-templates.js`
  (`confetti`, `balloons`, `glitters`) per poster.

## Notes

- The animation is hidden in `export-mode` (static PNG), so existing PNG
  exports and the daily Teams WebP delivery are unaffected.
- Rendering a GIF launches headless Chrome once per frame, so it is slower
  than a single PNG render. Use a modest `--frames` value for quick previews.
