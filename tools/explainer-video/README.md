# Explainer-video generator

The technical explainer video and all `docs/media/fig-*.png` schematics are
generated entirely by code — no video-editing software, no AI generation.

- `engine.py` — tiny PIL-based diagram-animation engine (boxes, chips, wires,
  packets, ripples, reveal timing) rendering 1920x1080 @ 30 fps frames to mp4
  scenes via ffmpeg
- `scenes.py` — the 10 scenes (content lives here; edit and re-run)
- `export_figs.py` — exports final-state frames of key scenes as the static
  schematics embedded in the docs
- `assemble_tech.py` — crossfades the scenes and adds the music track

Requirements: Python 3 + Pillow, ffmpeg on PATH, Windows Segoe UI fonts
(edit `engine.font()` for other platforms).

```
python scenes.py          # render all scenes (or: python scenes.py s04)
python export_figs.py     # regenerate the static schematics
python assemble_tech.py   # build the final mp4
```

Translating the video = translating the strings in `scenes.py`.
