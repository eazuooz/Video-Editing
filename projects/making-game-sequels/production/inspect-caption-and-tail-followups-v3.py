"""Decode only changed captions, proposed crops and unresolved action contexts.

All images remain local. Previous full extraction and original PCM are untouched.
This is targeted inspection; it cannot approve final pixels or timing by itself.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
WORK = BASE / 'measured-edit-v2'
DEST = WORK / 'caption-and-tail-local-v3'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()
assert not DEST.exists(), 'Preserve prior targeted inspection; inspect actual state.'
DEST.mkdir()
plan = read(WORK / 'plan.json')
compiled = read(WORK / 'native-review-v1/compiled.json')
tracks = read(WORK / 'caption-tracks-v2.json')
layout = read(WORK / 'caption-layout-v2.json')
cuts = {c['id']: c for s in plan['scenes'] for c in s['segments']
        if c['classification'] == 'actual-existing-game'}
media = {c['id']: c for c in compiled['cuts']}
selected = {}

def add(c, f, reason, crop=None):
    f = max(0, min(c['frames'] - 1, f))
    entry = selected.setdefault(c['id'], {'crop': crop, 'frames': {}})
    if crop is not None: entry['crop'] = crop
    entry['frames'].setdefault(f, []).append(reason)

# Cue139 must not appear during the preceding inserted silence. Include exact
# before/at/after anchors and first-word display on its actual native cut.
for seconds in [285.18, 293, 300.9, 301.4, 301.416666667, 301.433333334,
                302.133333333, 302.833333333, 302.85]:
    f = round(seconds * 60)
    c = next(c for c in cuts.values() if c['startFrame'] <= f < c['endFrameExclusive'])
    add(c, f - c['startFrame'], 'cue139-fixed-PCM-boundary')

# Only actual segments affected by the newly clamped paragraph boundaries.
for scene, paragraph in [('06', 3), ('08', 2), ('08', 3)]:
    cue = next(c for c in tracks['koRows'] if c['scene'] == scene and c['paragraph'] == paragraph)
    f = round(cue['startSeconds'] * 60)
    for g in [f - 1, f, f + 1, f + 30]:
        c = next(c for c in cuts.values() if c['startFrame'] <= g < c['endFrameExclusive'])
        add(c, g - c['startFrame'], 'changed-paragraph-caption-edge')

# All existing cue anchors plus 0.25s observation samples for each proposed crop.
for prefix, crop in [('08-p3-action-28', [0, 252, 1472, 828]),
                     ('13-p1-action-49', [192, 270, 1056, 594])]:
    c = next(c for c in cuts.values() if c['id'].startswith(prefix))
    for f in sorted(set(range(0, c['frames'], 15)) | {c['frames'] - 1}):
        add(c, f, 'proposed-crop-continuous-quarter-second-sample', crop)
    for row in layout['rows']:
        if row['segment'] == c['id']:
            add(c, row['localFrame'], 'every-affected-cue-anchor', crop)

# Early rail, stairs/pillar tail, device switches and meaningful guided tails.
prefixes = ['02-p2-action-10', '02-p4-action-12', '02-p4-action-13',
            '06-p1-action-22', '06-p1-action-15', '06-p1-action-26',
            '06-p2-action-20', '06-p4-action-21', '06-p4-action-24',
            '06-p4-action-25', '13-p2-action-57', '13-p2-action-58',
            '13-p2-action-59', '12-p2-action-46', '12-p4-action-40']
for prefix in prefixes:
    c = next(c for c in cuts.values() if c['id'].startswith(prefix))
    frames = set(range(0, c['frames'], 60)) | {c['frames'] - 1}
    if prefix == '02-p2-action-10': frames |= {0, 10, 20, 21, 30}
    if prefix == '06-p1-action-15': frames |= {220, 230, 240, 245}
    for f in sorted(frames): add(c, f, 'unresolved-native-action-and-guided-tail')

state = {'schemaVersion': 1, 'startedAt': now(), 'pid': os.getpid(), 'sessionId': None,
         'status': 'CPU-targeted-caption-crop-and-tail-inspection', 'activeTasks': [],
         'planSha256': sha(WORK/'plan.json'), 'captionLayoutSha256': sha(WORK/'caption-layout-v2.json'),
         'images': [], 'sheets': [], 'completedCuts': 0, 'totalCuts': len(selected),
         'newGitImages': 0, 'finalApproved': False, 'allDirectlyRead': False}

def save():
    state['updatedAt'] = now()
    (DEST/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

save()
try:
    for cid, entry in selected.items():
        c, m = cuts[cid], media[cid]
        assert sha(ROOT/m['video']) == m['sha256']
        crop = entry['crop'] or m['composition']['proposedCrop']
        x,y,w,h = crop
        frames = sorted(entry['frames'])
        selection = '+'.join(f'eq(n\\,{f})' for f in frames)
        vf = (f"crop={w}:{h}:{x}:{y},scale=1920:1080,setsar=1,"
              f"setpts=PTS+{c['startFrame']/60:.9f}/TB,subtitles=captions.ko.candidate.v2.ass,"
              f"select='{selection}'")
        folder=DEST/cid;folder.mkdir()
        cmd=[FF,'-v','error','-nostdin','-threads','2','-filter_threads','1','-i',str(ROOT/m['video']),
             '-vf',vf,'-fps_mode','passthrough','-frames:v',str(len(frames)),str(folder/'sample-%03d.png')]
        with (folder/'extract.log').open('wb') as log:
            proc=subprocess.Popen(cmd,cwd=WORK,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
            state['activeTasks']=[{'pid':proc.pid,'command':cmd}];save();code=proc.wait()
        assert code==0 and not (folder/'extract.log').read_text(encoding='utf-8').strip()
        files=sorted(folder.glob('sample-*.png'));assert len(files)==len(frames)
        for p,f in zip(files,frames):
            g=c['startFrame']+f
            state['images'].append({'path':rel(p),'sha256':sha(p),'cut':cid,'localFrame':f,'globalFrame':g,
                'crop':crop,'reasons':entry['frames'][f],
                'expectedCues':[q['index'] for q in tracks['koRows'] if q['startSeconds']<=g/60<q['endSeconds']],
                'directlyRead':False,'finalApproved':False,'gitStorage':'local-only'})
        state['activeTasks']=[];state['completedCuts']+=1;save()
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
    for offset in range(0,len(state['images']),6):
        subset=state['images'][offset:offset+6];board=Image.new('RGB',(1920,1740),'white');draw=ImageDraw.Draw(board)
        for k,row in enumerate(subset):
            x,y=k%2*960,k//2*580
            with Image.open(ROOT/row['path']) as im:board.paste(im.resize((960,540)),(x,y+40))
            draw.text((x+8,y+8),f"{offset+k+1:03} {row['cut']} n{row['localFrame']} CC{row['expectedCues']}",font=font,fill='black')
        p=DEST/f'board-{offset//6+1:03}.jpg';board.save(p,quality=94)
        state['sheets'].append({'path':rel(p),'sha256':sha(p),'indices':list(range(offset+1,offset+len(subset)+1)),
                                'directlyRead':False,'gitStorage':'local-only'})
    state.update(status='closed-awaiting-direct-targeted-review',endedAt=now(),exitCode=0);save()
    print(json.dumps({'pid':state['pid'],'cuts':len(selected),'images':len(state['images']),'sheets':len(state['sheets']),'newGitImages':0}))
except Exception:
    state.update(status='closed-targeted-inspection-failed',endedAt=now(),exitCode=1,activeTasks=[]);save();raise
