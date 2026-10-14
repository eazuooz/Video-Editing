from pathlib import Path
import hashlib, json
from datetime import datetime, timezone
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
old = json.loads((O / 'space-enlarged-static-plan-v1.json').read_text(encoding='utf-8-sig'))
out = O / 'space-enlarged-static-v3'
assert not out.exists(), 'Preserve previous static files; do not rerun.'
out.mkdir()
rows = []
for row in old['rows']:
    src = ROOT / row['sourceSample']
    assert sha(src) == row['sourceSha256']
    im = Image.open(src).convert('RGB')
    assert im.size == (1280, 720)
    # Source 1920 geometry: x320,y255,w1280,h720. No upward lift.
    focused = im.crop((320/1.5, 255/1.5, (320+1280)/1.5, (255+720)/1.5)).resize((1920,1080), Image.Resampling.LANCZOS)
    # Same exact frame supplies the footer; no black placeholder or unrelated image.
    footer = focused.filter(ImageFilter.GaussianBlur(18)).crop((0,900,1920,1080))
    focused.paste(footer, (0,900))
    dst = out / f"native-{row['nativeFrame']}.png"
    focused.save(dst)
    rows.append({'nativeFrame':row['nativeFrame'], 'pts':row['pts'], 'sourceSample':row['sourceSample'], 'sourceSha256':sha(src), 'path':rel(dst), 'sha256':sha(dst), 'sourceCrop1920':[320,255,1280,720], 'outputLift1920':0, 'sameFrameBlurFooter1920':[0,900,1920,180]})
plan = {'preparedAt':datetime.now(timezone.utc).isoformat(), 'previous':rel(O/'space-enlarged-static-plan-v1.json'), 'v1HeldReason':'10668 upright preview top clipped by x480/y240/960x540 crop and180px lift; v1 preserved.', 'rows':rows, 'exactSourceFramesReused':True, 'newSourceExtraction':False, 'preparedOnly':True, 'movingApproval':False, 'finalCaptionApproval':False, 'imageSource':'1280x720 previously verified exact-native samples; final video must transform original1920x1080.'}
(O/'space-enlarged-static-plan-v3.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':len(rows), 'newSourceExtraction':False, 'movingApproval':False}))
