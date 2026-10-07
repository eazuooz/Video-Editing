"""Bind actual authored render samples to the direct preflight review, then assemble exact replacements.
Encoded final caption pixels remain a separate gate. Existing media and narration are never rewritten.
"""
from pathlib import Path
import json,hashlib,subprocess,sys,re,datetime
ROOT=Path(__file__).resolve().parents[3]
PROBE=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe')
slug=sys.argv[1]; folder=ROOT/'projects'/slug/'production/visual-depth-v1'
revision=sys.argv[2] if len(sys.argv)>2 else 'v1'
if not re.fullmatch(r'v[1-9][0-9]*',revision):raise RuntimeError('Explicit revision required')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
review=read(folder/'white-preflight-direct-review.json')
source=ROOT/'motion-canvas/src/projects'/slug/'depth-explanations-v1.tsx'
if not review['preflightPixelsApproved'] or sha(source)!=review['sourceSha256'] or sha(ROOT/'motion-canvas/src/shared/depth-diagrams.tsx')!=review['sharedGeometrySha256']:raise RuntimeError('Stale preflight review')
execution=read(folder/('white-cpu-execution.json' if revision=='v1' else f'white-cpu-execution-{revision}.json'))
plan=read(ROOT/'motion-canvas/src/projects'/slug/'depth-reel-plan-v1.json')
if execution['status']!='rendered-pending-direct-pixels-and-full-decode' or len(execution['completed'])!=len(plan['rows']):raise RuntimeError('Actual white render incomplete')
if sha(ROOT/plan['sourcePlan'])!=plan['sourcePlanSha256']:raise RuntimeError('Preserved timing plan changed')
matched=[]
for board in review['boards']:
 for frame in board['frames']:
  src=ROOT/frame['path']; rendered=folder/('white-lookdev-local' if revision=='v1' else f'white-lookdev-{revision}-local')/src.name
  if sha(src)!=frame['sha256'] or sha(rendered)!=frame['sha256']:raise RuntimeError('Rendered sample differs from directly read preflight '+src.name)
  matched.append(dict(preflight=frame['path'],rendered=rendered.relative_to(ROOT).as_posix(),sha256=frame['sha256']))
selected=execution['completed']
if any(sha(ROOT/r['file'])!=r['sha256'] for r in selected):raise RuntimeError('Rendered white changed')
if revision!='v1' and (folder/'white-direct-review.json').exists():
 request=read(folder/'caption-safe-repair-request.json');old=folder/'white-direct-review.json';history=folder/'white-direct-review-pre-caption-safe.json'
 expected=next(r['sha256'] for r in request['retainedV1Records'] if r['path'].endswith('/white-direct-review.json'))
 if sha(old)!=expected or history.exists():raise RuntimeError('Inspect changed previous white review')
 history.write_bytes(old.read_bytes())
write(folder/'white-direct-review.json',dict(selectedWhitePixelsApproved=True,revision=revision,reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),selected=selected,matchedDirectlyReadFrames=matched,preflightReview='white-preflight-direct-review.json',scope='Exact authored raw pixels verified equal to directly read preflight; full white decode/probe and encoded final pixels still required',allFinalPixelsReviewed=False))
names={'motion-sickness-games':'final-concat.txt','hierarchical-game-outlines':'final-concat.txt','game-reward-planning':'visual-concat.txt','avoid-game-comparisons':'visual-concat.txt','making-game-sequels':'visual-concat.txt','familiar-game-rules':'visual-concat.txt'}
version='final-v2' if slug=='making-game-sequels' else 'final-v1'
concat=ROOT/'projects'/slug/'production'/version/names[slug]
paths=[]
for line in concat.read_text('utf-8-sig').splitlines():
 if line.strip():
  m=re.fullmatch(r"file '(.*)'",line.strip())
  if not m:raise RuntimeError('Unrecognized concat line')
  p=Path(m[1].replace("'\\''","'"))
  if not p.is_absolute():p=concat.parent/p
  paths.append(p.resolve())
rows={r['startFrame']:r for r in plan['rows']}; selected_map={r['id']:r for r in selected}
segments=[];offset=0; replaced=[]
for original in paths:
 v=json.loads(subprocess.check_output([str(PROBE),'-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,r_frame_rate,time_base','-of','json',str(original)],text=True))['streams'][0]
 frames=int(v['nb_frames'])
 if v['r_frame_rate']!='60/1':raise RuntimeError('Original input fps mismatch')
 row=rows.get(offset); p=original
 if row:
  if row['frames']!=frames or (ROOT/row['originalFile']).resolve()!=original:raise RuntimeError('Replacement interval/file mismatch')
  p=ROOT/selected_map[row['id']]['file'];replaced.append(row['id'])
 segments.append(dict(file=p.relative_to(ROOT).as_posix(),frames=frames,startFrame=offset,sha256=sha(p),replacedWhite=bool(row),originalFile=original.relative_to(ROOT).as_posix(),originalSha256=sha(original)))
 offset+=frames
if offset!=plan['finalFrames'] or len(replaced)!=len(rows):raise RuntimeError('Final assembly timing/replacement mismatch')
target=folder/'assembly-inputs.json'
if target.exists():
 if revision=='v1':raise RuntimeError('Inspect existing assembly; preserve it')
 request=read(folder/'caption-safe-repair-request.json');history=folder/'assembly-inputs-pre-caption-safe.json'
 expected=next(r['sha256'] for r in request['retainedV1Records'] if r['path'].endswith('/assembly-inputs.json'))
 if sha(target)!=expected or history.exists() or request['sourceSha256']!=sha(source):raise RuntimeError('Inspect previous assembly before superseding')
 history.write_bytes(target.read_bytes())
ass_version='measured-edit-v3' if slug=='game-reward-planning' else version
ass=ROOT/'projects'/slug/'production'/ass_version/'captions.ko.ass'
if not ass.is_file():raise RuntimeError('Actual unchanged caption ASS required')
write(target,dict(totalFrames=offset,captionAss=ass.relative_to(ROOT).as_posix(),sourceConcat=concat.relative_to(ROOT).as_posix(),sourceConcatSha256=sha(concat),segments=segments,allFinalPixelsReviewed=False))
print(json.dumps(dict(slug=slug,whiteSegments=len(selected),matchedDirectlyReadSamples=len(matched),finalFrames=offset,encodedFinalApproved=False)))
