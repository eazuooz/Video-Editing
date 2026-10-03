"""Source-contact review only, not a new-video render."""
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "game-research/PF5L_2g9UVQ.mp4"
OUT = BASE / "game-research/pws-preview-review"
OUT.mkdir(parents=True, exist_ok=True)
decode = subprocess.run(["ffmpeg", "-v", "error", "-threads", "2", "-i", str(SOURCE),
    "-f", "null", "-"], capture_output=True, text=True)
(OUT / "full-decode.log").write_text(decode.stderr, "utf-8")
if decode.returncode:
    raise RuntimeError(decode.stderr)
times = list(range(0, 601, 20))
for t in times:
    frame = OUT / f"{t:04}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(SOURCE),
        "-frames:v", "1", "-vf", "scale=480:270", "-q:v", "2", "-y", str(frame)], check=True)
for page in range((len(times)+11)//12):
    sheet = Image.new("RGB", (1440, 4*302), "white")
    draw = ImageDraw.Draw(sheet)
    for j,t in enumerate(times[page*12:(page+1)*12]):
        x,y = (j%3)*480, (j//3)*302
        sheet.paste(Image.open(OUT / f"{t:04}.jpg"), (x,y))
        draw.text((x+10,y+276), f"PF5L_2g9UVQ  {t//60:02}:{t%60:02} ({t}s)", fill="black")
    sheet.save(OUT / f"contact-{page+1}.jpg", quality=92)
(OUT / "review.json").write_text(json.dumps({"sourceId":"PF5L_2g9UVQ",
    "fullDecode": {"exitCode":0, "errorBytes":len(decode.stderr)}, "sampleSeconds":times,
    "manualReview":"pending", "finalCutApproval":False}, indent=2)+"\n", "utf-8")
print("Full decode and", len(times), "source preview samples ready", flush=True)
