"""Targeted layout variants from existing action samples, never final caption approval."""
import hashlib, json, pathlib, time
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[5]
HERE = pathlib.Path(__file__).resolve().parent
state = json.loads((HERE / 'native-review-v1.json').read_text('utf-8'))
source = next(x for x in state['sources'] if x['videoId'] == 'MXxOg1xuWcI')
out = HERE.parent / 'research-local/omd2-framing-correction-v2'
out.mkdir(parents=True, exist_ok=True)
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 48)
label_font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 25)
targets = [12600, 12705, 17400, 18585, 18765, 32070, 32340, 32490]
variants = [
    ('single', '길과 함정의 위치를 함께 살펴봅니다.'),
    ('double', '같은 방어 행동을 남기면서\n다음 선택을 어디에 더할지 살펴봅니다.'),
]
records = []
for target in targets:
    match = min(source['actionSamples'], key=lambda x: abs(x['frame'] - target))
    original = Image.open(ROOT / match['path']).convert('RGB')
    for name, caption in variants:
        # Top-centered 16:9 crop excludes the lower hotbar; no caption displacement.
        x, y, w, h = 192, 0, 1536, 864
        scale = original.width / 1920
        img = original.crop(tuple(round(v * scale) for v in (x, y, x+w, y+h)))
        img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        box = draw.multiline_textbbox((0, 0), caption, font=font, spacing=7, align='center')
        tw, th = box[2]-box[0], box[3]-box[1]
        left, top = (1920-tw-48)/2, 970-(th+30)/2
        right, bottom = 1920-left, 970+(th+30)/2
        draw.rectangle((left+12, top+12, right+12, bottom+12), fill='#154E39')
        draw.rectangle((left, top, right, bottom), fill='white', outline='black', width=2)
        draw.multiline_text(((1920-tw)/2, top+15-box[1]), caption, fill='black',
                            font=font, spacing=7, align='center')
        fn = out / f"n{match['frame']}-{name}.jpg"
        img.save(fn, quality=94)
        records.append({'sourceId': source['videoId'], 'requestedNativeFrame': target,
                        'nativeFrame': match['frame'], 'sourceFrame': match['path'],
                        'sourceFrameSha256': match['sha256'], 'nativeCrop': [x,y,w,h],
                        'captionCenter': [960,970], 'captionFontPx': 48,
                        'captionLines': 1 if name == 'single' else 2,
                        'captionText': caption, 'captionRole': 'synthetic-layout-test-only',
                        'path': fn.relative_to(ROOT).as_posix(),
                        'sha256': hashlib.sha256(fn.read_bytes()).hexdigest(),
                        'finalCaptionApproval': False})
sheets = []
for offset in range(0, len(records), 4):
    sheet = Image.new('RGB', (1920,1140), '#eeeeee')
    draw = ImageDraw.Draw(sheet)
    for j, r in enumerate(records[offset:offset+4]):
        x, y = (j%2)*960, (j//2)*570
        draw.text((x+5,y+2), f"n{r['nativeFrame']} {r['captionLines']}line crop{r['nativeCrop']}",
                  font=label_font, fill='black')
        sheet.paste(Image.open(ROOT/r['path']).resize((960,540)), (x,y+30))
    fn = out/f'sheet-{offset//4+1:02}.jpg'
    sheet.save(fn, quality=94)
    sheets.append({'path':fn.relative_to(ROOT).as_posix(),
                   'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),
                   'sampleCount':len(records[offset:offset+4])})
record = {'schemaVersion':1, 'createdAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
          'status':'awaiting-direct-targeted-layout-review', 'samples':records, 'sheets':sheets,
          'newSourceDecode':False, 'samePriorLayoutRerun':False,
          'allFinalMotionAndCuesReviewed':False, 'newGitImages':0}
(HERE/'omd2-framing-correction-v2.json').write_text(
    json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'samples':len(records),'sheets':len(sheets),'newSourceDecode':False}))
