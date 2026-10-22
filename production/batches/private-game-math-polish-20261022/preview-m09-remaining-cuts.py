"""Inspect four native-speed candidates against the immutable M09 speech clock."""
import datetime, os, sys
from PIL import Image, ImageDraw, ImageFont
from polish_common import *

e = Episode('M09'); e.authorized()
source = read(B/'uncle-fhd-scene-candidates.json')['source']
src = R/source['path']; assert sha(src) == source['sha256']
cases = {
    '05': [(503, 660), (523, 1020), (540, 1431)],
    'LG02': [(467, 1624), (382, 693)],
    'LG03': [(237, 960), (394, 235), (263, 1099)],
    '08': [(298, 1560), (357, 1020), (565, 660)],
}
job = B/'m09-remaining-cuts-job.json'
state = {'pid': os.getpid(), 'stage': 'candidate-previews', 'completed': [],
         'fullMasterReady': False, 'newTts': False, 'platformMutation': False}
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 17)
selected = sys.argv[1:] or list(cases)
for sid in selected:
    e.authorized(); cuts = cases[sid]
    slot = next(s for s in e.T['scenes'] if s['id'] == sid)
    assert sum(n for _, n in cuts) == slot['frames']
    for i, (start, frames) in enumerate(cuts):
        for other, count in cuts[i+1:]:
            assert start+frames/60 <= other or other+count/60 <= start
    state.update(scene=sid, updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat()); save(job, state)
    revision = '-v2' if sid in ['LG02', 'LG03'] else ''
    out = e.O/f'uncle-remaining-candidates/{sid}{revision}'; out.mkdir(parents=True, exist_ok=True)
    manifest = e.H/f'uncle-remaining-candidate-{sid}.json'
    previous = read(manifest) if manifest.exists() else {}
    if previous and revision and previous['rawClip'] != rel(out/'raw.mp4'):
        archive = e.H/f'uncle-remaining-candidate-{sid}-v1.json'
        if not archive.exists(): save(archive, previous)
        previous = {}
    parts = []; segments = []; offset = 0
    for i, (start, frames) in enumerate(cuts):
        part = out/f'part-{i}.mp4'
        seg = {'in': start, 'frames': frames, 'sourceFile': rel(src), 'localStart': offset}
        cache = previous.get('segments', [])
        if not (part.exists() and i < len(cache) and cache[i] == seg):
            e.ff(['-ss', start, '-i', src, '-frames:v', frames, '-an', *ENC, part], f'm09-{sid}-candidate.log')
        e.verify(part, frames); parts.append(part); segments.append(seg); offset += frames/60
    listing = out/'parts.txt'
    listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in parts)+'\n', encoding='utf8')
    raw = out/'raw.mp4'; preview = out/'captioned.mp4'
    e.ff(['-f', 'concat', '-safe', '0', '-i', listing, '-c', 'copy', raw], f'm09-{sid}-candidate.log')
    e.verify(raw, slot['frames'])
    vf = f'scale=1600:900,pad=1920:1080:160:0:black,settb=1/60,setpts=PTS+{slot["start"]}/TB,ass=captions.ko.ass,setpts=PTS-STARTPTS'
    e.ff(['-i', raw, '-ss', slot['start'], '-i', e.O/'baseline-audio.m4a', '-map', '0:v', '-map', '1:a',
          '-vf', vf, '-frames:v', slot['frames'], '-t', slot['seconds'], '-c:a', 'aac', '-b:a', '160k', *ENC, preview],
         f'm09-{sid}-candidate.log', e.O)
    e.verify(preview, slot['frames'])
    framesdir = out/'frames'; framesdir.mkdir(exist_ok=True)
    e.ff(['-i', preview, '-vf', 'fps=1,scale=640:360:flags=lanczos', '-q:v', 2, framesdir/'%04d.jpg'], f'm09-{sid}-candidate.log')
    samples = []; sheets = []; tiles = []
    for i, path in enumerate(sorted(framesdir.glob('*.jpg'))):
        tile = Image.new('RGB', (640, 390), '#222222'); tile.paste(Image.open(path), (0, 30))
        ImageDraw.Draw(tile).text((6, 4), f'M09 {sid} +{i+.5:.1f}s', font=font, fill='white')
        tiles.append(tile); samples.append({'localTimeApprox': i+.5, 'path': rel(path), 'sha256': sha(path)})
    for i in range(0, len(tiles), 9):
        sheet = Image.new('RGB', (1920, 1170), '#222222')
        for j, tile in enumerate(tiles[i:i+9]): sheet.paste(tile, (j%3*640, j//3*390))
        path = out/f'sheet-{i//9+1:02d}.jpg'; sheet.save(path, quality=94); sheets.append(rel(path))
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#151515;color:white;font:18px system-ui}video{width:min(96vw,1280px)}</style><p>기존 대사와 대체 화면 후보 검수 · 완성본 아님</p><video controls src="captioned.mp4"></video>', encoding='utf8')
    save(manifest, {'episode':'M09', 'scene':sid, 'status':'candidate-await-direct-review',
         'originalTimelineSha256':sha(e.P/'production/timeline.json'), 'source':source,
         'segments':segments, 'frames':slot['frames'], 'rawClip':rel(raw), 'rawClipSha256':sha(raw),
         'preview':rel(preview), 'previewSha256':sha(preview), 'samples':samples, 'sheets':sheets,
         'internalCutsChanged':True, 'originalSceneOrderAndDurationPreserved':True,
         'fullMasterReady':False, 'sourceSpeed':1})
    state['completed'].append(sid); save(job, state)
    print(sid, 'candidate ready for direct review', flush=True)
state.update(stage='finished-await-direct-review', updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat()); save(job, state)
