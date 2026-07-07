"""Export final-state frames of key scenes as static schematic PNGs for the repo docs."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))
from engine import Frame
import scenes

FIGS = [
    ("fig-capsule-stack.png",   scenes.s02, 17.5),
    ("fig-signal-chain.png",    scenes.s03, 19.5),
    ("fig-replica-wiring.png",  scenes.s04, 21.5),
    ("fig-power-tree.png",      scenes.s05, 17.5),
    ("fig-pulse-budget.png",    scenes.s06, 19.5),
    ("fig-wire-format.png",     scenes.s07, 15.5),
]
outdir = os.path.abspath(os.path.join("..", "figs"))
os.makedirs(outdir, exist_ok=True)
for name, fn, t in FIGS:
    fr = Frame()
    fn(fr, t)
    fr.footer()
    fr.render().save(os.path.join(outdir, name))
    print("fig", name)
print("FIGS DONE ->", outdir)
