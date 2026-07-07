"""Concat the 10 tech scenes with crossfades + the existing music track."""
import subprocess, os, json, sys

os.chdir(os.path.dirname(__file__))
FADE = 0.5
NAMES = ["s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10"]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd[:5])); print(r.stderr[-700:]); sys.exit(1)
    return r

def dur(p):
    r = run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", p])
    return float(json.loads(r.stdout)["format"]["duration"])

missing = [n for n in NAMES if not os.path.exists(n + ".mp4")]
if missing:
    print("missing:", missing); sys.exit(2)

durs = [dur(n + ".mp4") for n in NAMES]
inputs = []
for n in NAMES:
    inputs += ["-i", n + ".mp4"]
fc, offset, prev = [], 0.0, "[0:v]"
for i in range(1, len(NAMES)):
    offset += durs[i - 1] - FADE
    label = f"[v{i}]" if i < len(NAMES) - 1 else "[vout]"
    fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={FADE}:offset={offset:.3f}{label}")
    prev = f"[v{i}]"
total = sum(durs) - FADE * (len(NAMES) - 1)
print(f"TOTAL {total:.1f}s = {int(total//60)}:{int(total%60):02d}")

inputs += ["-i", os.path.abspath(os.path.join("..", "audio", "music.m4a"))]
ai = len(NAMES)
fc.append(f"[{ai}:a]atrim=0:{total:.3f},afade=t=in:st=0:d=1,afade=t=out:st={total-4:.3f}:d=4,"
          f"volume=0.85,aformat=sample_rates=48000[aout]")

out = os.path.abspath(os.path.join("..", "final", "opencapsule_tech_explainer.mp4"))
run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc),
     "-map", "[vout]", "-map", "[aout]",
     "-c:v", "libx264", "-preset", "slow", "-crf", "21",
     "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
print("FINAL:", out, os.path.getsize(out) // 1048576, "MB")
