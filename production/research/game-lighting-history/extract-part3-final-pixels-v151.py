"""Plan all final cue/cut pixels; extract only the sealed reviewed pair."""
from pathlib import Path
import argparse, importlib.util
from PIL import Image, ImageDraw, ImageFont
spec = importlib.util.spec_from_file_location('common', Path(__file__).with_name('review-media-common-v15.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ROOT = m.ROOT; P = ROOT / 'projects/game-lighting-history-04/production'
ap = argparse.ArgumentParser(); ap.add_argument('--plan-only', action='store_true'); args = ap.parse_args()
PP = P / 'part3-final-input-plan-v145.json'; LP = P / 'part3-caption-layout-v147.json'
plan, layout = m.read(PP), m.read(LP)
points = {}
def add(frame, reason):
 frame = int(frame)
 if not 0 <= frame < plan['finalFrames']: return
 p = points.setdefault(frame, {'frame': frame, 'reasons': []})
 if reason not in p['reasons']: p['reasons'].append(reason)
cuts = [dict(id='original-branding', kind='branding', fromFrame=0, toFrame=120), *plan['cuts'],
        dict(id='original-membership', kind='membership', fromFrame=plan['finalFrames']-600, toFrame=plan['finalFrames'])]
assert all(a['toFrame'] == b['fromFrame'] for a, b in zip(cuts, cuts[1:]))
for q in layout['metrics']:
 a, b = q['assFirstFrame'], q['assExclusiveEndFrame'] - 1
 for f in [a-1, a, (a+b)//2, b, b+1]: add(f, 'cue-' + str(q['id']))
for c in cuts:
 a, b = c['fromFrame'], c['toFrame']-1
 for f in [a-1, a, a+1, (a+b)//2, b]: add(f, 'cut-' + c['id'])
 for q in layout['metrics']:
  lo, hi = max(a, q['assFirstFrame']), min(b+1, q['assExclusiveEndFrame'])
  if hi > lo: add((lo+hi-1)//2, 'cue/cut-' + c['id'])
 if c['kind'] == 'explanation':
  for fraction in [.2, .4, .6, .8]: add(a+round((b-a)*fraction), 'spatial-motion-' + c['id'])
for p in plan['paragraphs']:
 a = min(q['fromFrame'] for q in p['koCues'])
 for offset in [-1, 0, 1]: add(a+offset, 'narration-onset-' + p['id'])
for target in ['hogwarts-terrace-reference', 'hogwarts-courtyard-ui', 'grade-shared-reference']:
 c = next(c for c in plan['cuts'] if c['id'] == target)
 for f in range(c['fromFrame'], c['toFrame'], 30): add(f, 'moving-marker-' + target)
for target in ['resource-viewer-context', 'resource-name-limits', 'resource-upload-control', 'resource-budget-to-measure']:
 c = next(c for c in plan['cuts'] if c['id'] == target)
 for offset in [0, 60, 300, 600, 900, c['toFrame']-c['fromFrame']-1]: add(c['fromFrame']+offset, 'editor-crop-' + target)
for f in [0, 119, 120, plan['finalFrames']-601, plan['finalFrames']-600, plan['finalFrames']-300, plan['finalFrames']-1]: add(f, 'branding/membership-edge')
covered = set()
for p in points.values():
 p['visibleCueIds'] = [q['id'] for q in layout['metrics'] if q['assFirstFrame'] <= p['frame'] < q['assExclusiveEndFrame']]
 p['expectedCaptions'] = [q['text'] for q in layout['metrics'] if q['id'] in p['visibleCueIds']]
 c = next(c for c in cuts if c['fromFrame'] <= p['frame'] < c['toFrame'])
 p.update(input=c['id'], kind=c['kind'], localFrame=p['frame']-c['fromFrame'])
 covered.update(p['visibleCueIds'])
assert covered == set(range(1,331))
request = {'preparedAt': m.stamp(), 'planSha256': m.sha(PP), 'captionLayoutSha256': m.sha(LP),
 'points': [points[f] for f in sorted(points)], 'uniqueFrames': len(points), 'cueCount': 330,
 'paragraphs': 85, 'inputCuts': len(cuts), 'allCueCutIntersectionsIncluded': True,
 'allImagesLocalOnly': True, 'newGitImages': 0, 'allFinalPixelsReviewed': False, 'qaApproved': False}
RP = P / 'part3-final-pixel-review-request-v151.json'
if RP.exists():
 old = m.read(RP); assert old['points'] == request['points'] and old['planSha256'] == request['planSha256']
else: m.save(RP, request)
if args.plan_only:
 print(m.json.dumps({'framesPlanned': len(points), 'allCues': 330, 'allCuts': len(cuts), 'imagesCreated': 0, 'approved': False})); raise SystemExit
BP = P / 'part3-reviewed-pair-build-v149.json'; pair = m.read(BP)
assert pair['planSha256'] == m.sha(PP) and pair['captionAssSha256'] == layout['ass']['sha256']
assert pair['identicalAacPayloadPtsDuration'] and pair['captioned']['wholeDecode']['exitCode'] == 0
video = ROOT / pair['captioned']['path']; assert m.sha(video) == pair['captioned']['sha256']
resources = m.resources(); OUT = ROOT / 'production/research/game-lighting-history/local/part3-final-pixel-qa-v151'
SP = P / 'part3-final-pixel-review-execution-v151.json'
assert not OUT.exists() and not SP.exists(), 'Preserve prior execution/images; explicit resume required'
OUT.mkdir(parents=True); FD = OUT / 'frames'; FD.mkdir()
state = {'startedAt': m.stamp(), 'status': 'extracting', 'worker': m.worker(), 'active': None,
 'resourceObservation': resources, 'commands': [], 'results': [], 'images': [], 'boards': [],
 'newGitImages': 0, 'allFinalPixelsReviewed': False, 'qaApproved': False}
m.save(SP, state)
def checkpoint():
 cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
 j['episode04Part3FinalPixelExtractionV151']={'execution':m.rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'images':len(state['images']),'boards':len(state['boards']),'allFinalPixelsReviewed':False}
 j['ownedActiveWork']={'type':'part3-final-caption-cue-cut-extraction','execution':m.rel(SP),'worker':state['worker'],'cpuThreads':2,'gpuJobs':0,'next':'Directly read all 362 encoded boards and normal-speed final motion; then QA/collection/private settings'} if state['status']=='extracting' else {'status':'no-active-owned-media-worker','execution':m.rel(SP),'next':'Directly read all encoded boards and final motion'}
 m.save(cp,j)
checkpoint()
try:
 filt = OUT / 'exact-frames.filter'
 filt.write_text('select=' + '+'.join(f'eq(pts\\,{f*1500})' for f in sorted(points)) + '\n', 'utf-8')
 extraction = m.run([m.FF, '-n', '-v', 'error', '-threads', '2', '-filter_threads', '2', '-reinit_filter', '0', '-i', video,
   '-filter_script:v', filt, '-fps_mode', 'vfr', '-an', '-threads', '2', FD / 'frame-%05d.png'], 'final-frame-extraction', state, SP, OUT)
 files = sorted(FD.glob('frame-*.png')); assert len(files) == len(points)
 for i, (file, p) in enumerate(zip(files, request['points'])):
  with Image.open(file) as im: assert im.size == (1920,1080)
  state['images'].append({'index': i+1, 'path': m.rel(file), 'sha256': m.sha(file), **p})
 font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 22)
 for i in range(0, len(files), 6):
  group = state['images'][i:i+6]; board = Image.new('RGB', (2880,1204), (25,25,25)); draw = ImageDraw.Draw(board)
  for j, p in enumerate(group):
   x, y = j%3*960, j//3*602
   with Image.open(ROOT/p['path']) as im: board.paste(im.resize((960,540), Image.Resampling.LANCZOS), (x,y+62))
   draw.text((x+10,y+6), f"#{p['index']} f{p['frame']} {p['input']} cue {p['visibleCueIds']}", font=font, fill='white')
   draw.text((x+10,y+32), ','.join(p['reasons'])[:67], font=font, fill='#e5c873')
  file = OUT / f'board-{i//6+1:03d}.png'; board.save(file)
  state['boards'].append({'path': m.rel(file), 'sha256': m.sha(file), 'imageIndices': [p['index'] for p in group], 'directlyRead': False})
 state.update(status='complete', exitCode=0, completedAt=m.stamp(), active=None,
   extraction=extraction, source=m.rel(video), sourceSha256=m.sha(video), pairBuildSha256=m.sha(BP), requestSha256=m.sha(RP))
 m.save(SP,state); checkpoint(); print(m.json.dumps({'images': len(files), 'boards': len(state['boards']), 'newGitImages': 0, 'approved': False}))
except BaseException as e:
 state.update(status='failed', exitCode=1, failedAt=m.stamp(), error=repr(e)); m.save(SP,state); checkpoint(); raise
