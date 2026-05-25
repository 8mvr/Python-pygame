import sys
import soundfile as sf

path = sys.argv[1]
ogg = path.rsplit(".", 1)[0] + ".ogg"
data, sr = sf.read(path)
sf.write(ogg, data, sr, format="OGG")
print(ogg)
