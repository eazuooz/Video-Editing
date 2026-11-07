"""One local poster layout using an immutable, decoded actual-game frame."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

C = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
BASE = C / 'shorts-leveldesign-06-02'
SOURCE = BASE / 'source-game-guide-preparation-v1/96d40dbb2506/D/sample-004.png'
EXPECTED = '7cfaa155c47acb9e8bd81eb2c837b50d30dbf83b6367d58eaf98b6c2d413bfd3'
OUT = BASE / 'cover-v1'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

assert sha(SOURCE) == EXPECTED
assert not OUT.exists(), 'Preserve any earlier cover attempt'
font_path = Path('C:/Windows/Fonts/malgunbd.ttf')
assert font_path.is_file()
source = Image.open(SOURCE).convert('RGB')
assert source.size == (1920, 1080)
OUT.mkdir(parents=True)
canvas = Image.new('RGB', (1080, 1920), '#000000')
draw = ImageDraw.Draw(canvas)
for text, y, color in [('보이는데', 136, '#ffffff'), ('안전할까?', 340, '#ffdb79')]:
    font = ImageFont.truetype(str(font_path), 168)
    box = draw.textbbox((0, 0), text, font=font)
    assert box[2] - box[0] <= 980
    draw.text(((1080 - (box[2] - box[0])) / 2 - box[0], y - box[1]), text, font=font, fill=color)

# A focus crop keeps both guards, the window frame, and the original game caption.
# There is no pixel synthesis, object removal, relighting, or claimed detection.
crop = (300, 0, 1450, 1080)
picture = source.crop(crop)
height = round(picture.height * 1080 / picture.width)
picture = picture.resize((1080, height), Image.Resampling.LANCZOS)
picture_y = 666
canvas.paste(picture, (0, picture_y))
draw = ImageDraw.Draw(canvas)
scale = 1080 / (crop[2] - crop[0])
rect_source = (730, 170, 1160, 700)
rect = ((rect_source[0]-crop[0])*scale, picture_y+rect_source[1]*scale,
        (rect_source[2]-crop[0])*scale, picture_y+rect_source[3]*scale)
draw.rectangle(rect, outline='#48d8b4', width=10)
label = '시야와 은신처'
font = ImageFont.truetype(str(font_path), 78)
box = draw.textbbox((0, 0), label, font=font)
draw.text(((1080-(box[2]-box[0]))/2-box[0], 1775-box[1]), label, font=font, fill='#ffffff')
cover = OUT / 'cover.png'
canvas.save(cover)
mobile = OUT / 'cover-375.png'
canvas.resize((375, round(1920*375/1080)), Image.Resampling.LANCZOS).save(mobile)
proof = dict(schemaVersion='06-02-cover-provenance-v1', topicId='06.02',
    cover=dict(path=str(cover), sha256=sha(cover)), mobile=dict(path=str(mobile), sha256=sha(mobile)),
    sourceFrame=dict(path=str(SOURCE), sha256=EXPECTED, sourceFrame=450, sourceTimeSeconds=7.5,
        decodedDimensions=[1920,1080], sourceMediaSHA256='ab05db86e66490dfaafb9a3a2d6c1a29478a45c0591b7bcae4ccde8185975fca',
        originalURL='https://www.youtube.com/watch?v=hnFolbxwQb0'),
    font=dict(path=str(font_path), sha256=sha(font_path)), script=dict(path=str(Path(__file__)), sha256=sha(__file__)),
    pictureCrop=list(crop), picturePosition=[0,picture_y,1080,height], preservedAspectRatio=True,
    marker=dict(sourceRect=list(rect_source), meaning='Editorial focus on the two visible guards; not a visibility/detection measurement'),
    headline=['보이는데','안전할까?'], actualGameImage=True, mascotUsed=False, sourcePixelsSynthesized=False,
    originalGameSubtitlePreserved=True, actualAgentVisualInspection=False, humanApproval=False, platformActions=[])
(OUT / 'provenance.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
print(json.dumps(proof['cover'], ensure_ascii=False))
