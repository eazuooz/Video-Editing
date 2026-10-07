"""Read-only exact old-input/timing compatibility check before expensive white rendering."""
from pathlib import Path
import json,sys,re,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[3];PROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
names={'motion-sickness-games':'final-concat.txt','hierarchical-game-outlines':'final-concat.txt','game-reward-planning':'visual-concat.txt','avoid-game-comparisons':'visual-concat.txt','making-game-sequels':'visual-concat.txt','familiar-game-rules':'visual-concat.txt'}
bind='--bind-original-files' in sys.argv
for slug in [x for x in sys.argv[1:] if not x.startswith('--')] or names:
 planpath=ROOT/'motion-canvas/src/projects'/slug/'depth-reel-plan-v1.json';p=json.loads(planpath.read_text('utf-8-sig'));v='final-v2' if slug=='making-game-sequels' else 'final-v1';c=ROOT/'projects'/slug/'production'/v/names[slug]
 if hashlib.sha256((ROOT/p['sourcePlan']).read_bytes()).hexdigest()!=p['sourcePlanSha256']:raise RuntimeError('Preserved source plan changed')
 source=json.loads((ROOT/p['sourcePlan']).read_text('utf-8-sig'))
 if not p.get('finalFrames') and bind:p['finalFrames']=source['finalFrames']
 rows={r['startFrame']:r for r in p['rows']};start=0;matched=[]
 for line in c.read_text('utf-8-sig').splitlines():
  if not line.strip():continue
  m=re.fullmatch(r"file '(.*)'",line.strip());f=Path(m[1]);f=f.resolve() if f.is_absolute() else (c.parent/f).resolve()
  frames=int(json.loads(subprocess.check_output([PROBE,'-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(f)],text=True))['streams'][0]['nb_frames'])
  r=rows.get(start)
  if r:
   if not r['originalFile'] and bind:
    relative=f.relative_to(ROOT).as_posix()
    if not any(t in relative.lower() for t in ['white','explanation']):raise RuntimeError('Original input must be an explicit white explanation')
    r['originalFile']=relative
   if bind and r['originalFile'] and f!=(ROOT/r['originalFile']).resolve():
    relative=f.relative_to(ROOT).as_posix()
    if frames!=r['frames'] or not any(t in relative.lower() for t in ['white','explanation']) or r['id'] not in f.name:raise RuntimeError('Current remux must match exact named white interval')
    r['sourceWhiteFile']=r['originalFile'];r['originalFile']=relative
   if r['frames']!=frames or f!=(ROOT/r['originalFile']).resolve():raise RuntimeError('Exact interval mismatch '+slug+' '+r['id'])
   matched.append(r['id'])
  start+=frames
 if start!=p['finalFrames'] or len(matched)!=len(rows):raise RuntimeError('Missing white interval or final frame mismatch '+slug)
 if bind:
  p['originalInputBinding']='Exact source concat offset and probed frame count, with current source-plan SHA; no timing, narration or sampled visual property changed'
  planpath.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(dict(slug=slug,exactPreservedTiming=True,totalFrames=start,whiteReplacements=len(matched))))
