"""Plan and extract every encoded cue/cut intersection and spatial transition."""
import argparse, importlib.util, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
_p = Path(__file__).with_name('review-media-common-v15.py')
_s = importlib.util.spec_from_file_location('review_media', _p)
m = importlib.util.module_from_spec(_s); _s.loader.exec_module(m)
ROOT, PROD, FF = m.ROOT, m.PROD, m.FF
a = argparse.ArgumentParser(); a.add_argument('--plan-only', action='store_true'); args = a.parse_args()
ip = PROD / 'review-input-plan-v15.json'
tp = PROD / 'measured-native-timeline-candidate-v15.json'
cap = PROD / 'local/captions-v15/caption-plan.json'
layout = PROD / 'local/captions-v15/caption-layout-measurement.json'
inputs, timeline, tracks, boxes = m.read(ip), m.read(tp), m.read(cap), m.read(layout)
points = {}
def add(frame, reason, cue=None):
    frame = int(frame)
    if not 0 <= frame < timeline['totals']['finalFrames']: return
    p = points.setdefault(frame, dict(frame=frame, reasons=[], cues=[]))
    if reason not in p['reasons']: p['reasons'].append(reason)
    if cue is not None and cue not in p['cues']: p['cues'].append(cue)
for c in boxes['metrics']:
    first, last = c['assFirstFrame'], c['assExclusiveEndFrame'] - 1
    for f in [first, (first + last) // 2, last]: add(f, 'encoded-caption', c['id'])
for c in inputs['inputs']:
    first, last = c['fromFrame'], c['toFrame'] - 1
    for f in [first, (first + last) // 2, last]: add(f, 'input-' + c['id'])
    for q in boxes['metrics']:
        start, end = max(first, q['assFirstFrame']), min(last + 1, q['assExclusiveEndFrame'])
        if end > start: add((start + end - 1) // 2, 'caption/input-' + c['id'], q['id'])
for c in timeline['slots']:
    for offset in [-1,0,1]: add(c['fromFrame'] + offset, 'PCM-placement-' + c['id'])
    if c['role'] != 'explanation': continue
    start_seconds = c['sourceSampleRange'][0] / 24000
    a0, z0 = c['motionSeconds']
    a_frame = c['fromFrame'] + round((a0 - start_seconds) * 60)
    z_frame = c['fromFrame'] + round((z0 - start_seconds) * 60)
    for f in [a_frame - 1, a_frame, (a_frame + z_frame) // 2, z_frame - 1, z_frame]:
        add(min(c['toFrame'] - 1, max(c['fromFrame'], f)), 'spatial-motion-' + c['id'])
for f in [0,119,120,121,timeline['totals']['finalFrames']-601,timeline['totals']['finalFrames']-600,
          timeline['totals']['finalFrames']-300,timeline['totals']['finalFrames']-1]: add(f, 'original-branding/member-edge')
covered = set()
for p in points.values():
    p['visibleCueIds'] = [q['id'] for q in boxes['metrics'] if q['assFirstFrame'] <= p['frame'] < q['assExclusiveEndFrame']]
    p['expectedCaptions'] = [q['text'] for q in tracks['ko'] if q['id'] in p['visibleCueIds']]
    c = next(c for c in inputs['inputs'] if c['fromFrame'] <= p['frame'] < c['toFrame'])
    p.update(input=c['id'], kind=c['kind'], localFrame=p['frame']-c['fromFrame'])
    covered.update(p['visibleCueIds'])
assert covered == set(range(1,357))
request = dict(preparedAt=m.stamp(), inputHashes=[dict(path=m.rel(p), sha256=m.sha(p)) for p in [ip,tp,cap,layout]],
               points=[points[f] for f in sorted(points)], uniqueFrames=len(points), cueCount=356,
               nativeCuts=112, explanationCuts=47, literalParagraphs=104, allCueAndCutIntersectionsIncluded=True,
               allSpatialMotionEndpointsIncluded=True, allImagesLocalOnly=True, newGitImages=0,
               allEncodedPixelsDirectlyRead=False, allFinalPixelsReviewed=False, qaApproved=False)
request_path = PROD / 'encoded-pixel-review-request-v15.json'
if request_path.exists():
    old = m.read(request_path)
    assert old['inputHashes'] == request['inputHashes'] and old['points'] == request['points'], 'Preserve changed review request'
else: m.save(request_path, request)
if args.plan_only:
    print(m.json.dumps(dict(uniqueFrames=len(points), cues=356, native=112, explanation=47, imagesCreated=0, pixelsApproved=False)))
    raise SystemExit(0)
pair_path = PROD / 'review-pair-build-v15.json'
pair = m.read(pair_path)
assert pair['identicalAacPayload'] and pair['captionAssSha256'] == boxes['ass']['sha256']
captioned = ROOT / pair['captioned']['path']
assert m.sha(captioned) == pair['captioned']['sha256'] and pair['captioned']['wholeDecode']['exitCode'] == 0
observation = m.resources()
out = ROOT / 'production/research/game-lighting-history/local/encoded-pixel-qa-v15'
assert not out.exists(), 'Preserve existing QA extraction; inspect completed images before a retry'
out.mkdir(parents=True); frames_dir=out/'frames'; frames_dir.mkdir()
state_path = PROD / 'encoded-pixel-review-execution-v15.json'
state = dict(startedAt=m.stamp(), status='extracting', worker=m.worker(), active=None, resourceObservation=observation,
             commands=[], results=[], images=[], boards=[], newGitImages=0, allFinalPixelsReviewed=False)
m.save(state_path, state)
try:
    # The verified final stream has exact1500PTS/frame. Match absolute timestamps,
    # so a source property change cannot reset a filter-local frame counter.
    expression = '+'.join(f'eq(pts\\,{f * 1500})' for f in sorted(points))
    filters = out / 'exact-frames.filter'
    filters.write_text('select=' + expression + '\n', 'utf-8')
    extraction = m.run([FF,'-n','-v','error','-filter_threads','2','-threads','2','-reinit_filter','0','-i',captioned,'-filter_script:v',filters,
                        '-fps_mode','vfr','-an','-threads','2',frames_dir/'frame-%05d.png'],
                       'encoded-frame-extraction', state, state_path, out)
    files = sorted(frames_dir.glob('frame-*.png')); assert len(files) == len(points)
    ordered = [points[f] for f in sorted(points)]
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 22)
    for i, (file, p) in enumerate(zip(files, ordered)):
        with Image.open(file) as im: assert im.size == (1920,1080)
        state['images'].append(dict(index=i+1, path=m.rel(file), sha256=m.sha(file), **p))
    for i in range(0,len(files),6):
        group = state['images'][i:i+6]
        board = Image.new('RGB',(2880,1204),(25,25,25)); draw=ImageDraw.Draw(board)
        for j,p in enumerate(group):
            x=(j%3)*960; y=(j//3)*602
            with Image.open(ROOT/p['path']) as im:
                board.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,y+62))
            label=f"#{p['index']} / f{p['frame']} / {p['input']} / cue {','.join(map(str,p['visibleCueIds'])) or 'none'}"
            draw.text((x+10,y+6),label,font=font,fill='white')
            draw.text((x+10,y+32),','.join(p['reasons'])[:65],font=font,fill='#e5c873')
        b=out/f'board-{i//6+1:03d}.png'; board.save(b)
        state['boards'].append(dict(path=m.rel(b),sha256=m.sha(b),imageIndices=[p['index'] for p in group],directlyRead=False))
    state.update(status='complete',completedAt=m.stamp(),exitCode=0,active=None,extraction=extraction,
                 source=m.rel(captioned),sourceSha256=m.sha(captioned),pairBuildSha256=m.sha(pair_path),
                 requestSha256=m.sha(request_path),allFinalPixelsReviewed=False,qaApproved=False)
    m.save(state_path,state)
    print(m.json.dumps(dict(images=len(files),boards=len(state['boards']),newGitImages=0,pixelsApproved=False)),flush=True)
except BaseException as e:
    state.update(status='failed',failedAt=m.stamp(),exitCode=1,error=str(e));m.save(state_path,state);raise
