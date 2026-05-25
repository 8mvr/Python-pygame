"One-time helper: convert WAV/MP3 in assets/ to OGG for pygbag / itch.io."
import glob
import os

import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

for path in sorted(glob.glob("assets/**/*.wav", recursive=True) + glob.glob("assets/**/*.mp3", recursive=True)):
    ogg = os.path.splitext(path)[0] + ".ogg"
    try:
        data, sr = sf.read(path)
        sf.write(ogg, data, sr, format="OGG")
        print(f"converted {path} -> {ogg}")
    except Exception as e:
        print(f"FAILED {path}: {e}")
