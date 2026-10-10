"""Read-only baseline audit and exact-frame pilot review; no baseline rebuild."""
from pathlib import Path
import json, hashlib, subprocess, os
from datetime import datetime, timezone
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-math-polar-3d'
OUT=BASE/'revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar'
RAW=ROOT/'shared/assets/presenting-game-scores/raw'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def write(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True)
 assert not p.exists(),f'Preserve existing evidence: {p}'
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p): return p.relative_to(ROOT).as_posix()
OUT.mkdir(parents=True,exist_ok=True);LOCAL.mkdir(parents=True,exist_ok=True)
timeline=json.loads((BASE/'production/timeline.json').read_text(encoding='utf-8-sig'))
protected=[BASE/'project.json',BASE/'production/timeline.json',BASE/'script/narration.ko.json',BASE/'script/narration.en.json',BASE/'script/final.ko.srt',BASE/'script/final.en.srt',BASE/'script/final.ko.ass',BASE/'sources/gameplay-cuts.json',BASE/'sources/game-candidates.json',BASE/'production/delivery-output.json']
protected += [ROOT/s['voice'] for s in timeline['scenes']]
protected += [ROOT/'shared/output/game-math-polar-3d/clips/02.mp4']
snapshot=[{'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in protected]
write(OUT/'baseline-protected-sha-v1.json',{'observedAt':datetime.now(timezone.utc).isoformat(),'files':snapshot,'baselineVideoId':'ZLOewk8JHXA','baselineMutations':0})
clip=ROOT/'shared/output/game-math-polar-3d/clips/02.mp4'
frames=list(range(0,721,60))
records=[]
for frame in frames:
 target=LOCAL/f'scene02-f{frame:04d}.png'
 assert not target.exists()
 command=[str(FF),'-hide_banner','-nostdin','-loglevel','error','-threads','2','-filter_threads','1','-i',str(clip),'-vf',f'select=eq(n\\,{frame})','-frames:v','1','-fps_mode','passthrough',str(target)]
 subprocess.run(command,check=True)
 records.append({'frame':frame,'seconds':frame/60,'path':rel(target),'sha256':sha(target),'sourceSegmentInSeconds':152,'nativeSourcePtsNotAssertedFromConvertedClip':True})
for n in range(0,len(records),6):
 group=records[n:n+6];board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
 for j,r in enumerate(group):
  x=(j%3)*640;y=(j//3)*390
  with Image.open(ROOT/r['path']) as im: board.paste(im.resize((640,360)),(x,y+30))
  d.text((x+8,y+7),f"scene02 f{r['frame']} / {r['seconds']:.3f}s",fill='white')
 path=LOCAL/f'pilot-source-board-{n//6+1:02d}.png';assert not path.exists();board.save(path)
link=RAW/'polar-3d-baseline-scene02-v1.mp4'
if not link.exists(): os.link(clip,link)
assert os.path.samefile(link,clip)
assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot)
write(OUT/'source-pilot-extraction-v1.json',{'observedAt':datetime.now(timezone.utc).isoformat(),'records':records,'ffmpegExitCodes':[0]*len(records),'samplingScope':'first12seconds of preserved scene02 only','allContinuousPixelsReviewed':False,'sourceSelectionApproved':False,'annotationApproved':False,'originalFilesUnchanged':True,'hardlink':rel(link),'newSourceCopy':False,'newServer':False,'localOnlyImages':True})
print(json.dumps({'samples':len(records),'boards':3,'allBaselineProtectedFilesUnchanged':True,'nativeSourceExactPtsApproval':False,'newSourceCopy':False,'newServer':False}),flush=True)
