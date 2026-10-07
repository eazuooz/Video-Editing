"""Snapshot the seven explicitly requested visual revisions; never start TTS."""
from pathlib import Path
import json,hashlib,shutil,datetime,psutil
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
SLUGS=['picking-sides','motion-sickness-games','hierarchical-game-outlines','game-reward-planning','avoid-game-comparisons','making-game-sequels','familiar-game-rules']
OLD_IDS=dict(zip(SLUGS,['sXd1RrPlGos','vFhhQXgdeMs','lEwpxP_qsDY','D81WnOMytG4','bCyRB3ksiGo','DWsAfi-fUKw','NLEHMC0XMtg']))
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
assert read(ROOT/'shared/output/GPU_TTS_HOLD.json')['active']
items=[]
for slug in SLUGS:
 d=ROOT/f'projects/{slug}/production/visual-depth-v1'; d.mkdir(parents=True,exist_ok=True)
 m=read(ROOT/f'projects/{slug}/project.json')
 files=[]
 for k in ['script','scriptEn','audioMix','captionsKo','captionsEn','videoClean','videoBurnedCaptions']:
  path=m['paths'].get(k)
  if not path and k=='scriptEn':path=f'projects/{slug}/script/narration.en.json'
  if not path:continue
  p=ROOT/path; assert p.is_file(),str(p)
  files.append(dict(role=k,path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
 for suffix in ['clean.mp4','captioned.mp4','ko.srt','en.srt']:
  p=ROOT/f'output/{slug}/{slug}.{suffix}'; assert p.is_file(),str(p)
  files.append(dict(role='collected-'+suffix,path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
 old_id=m.get('publishing',{}).get('videoId') or OLD_IDS[slug]
 baseline=dict(slug=slug,createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),manifest=m,files=files,existingVideoId=old_id,preserveExistingUpload=True)
 target=d/'baseline.json'
 if target.exists(): assert read(target)['files']==files,'Baseline changed; inspect before modifying'
 else:write(target,baseline)
 items.append(dict(slug=slug,oldVideoId=old_id,stage='baseline-preserved',baseline=target.relative_to(ROOT).as_posix(),newVideoId=None,renderApproved=False,allPixelsReviewed=False,collected=False,uploaded=False,gitDelivered=False))
q=BASE/'queue.json'
if not q.exists():write(q,dict(schemaVersion=1,request='2026-10-07 explicit 2.5D and illustrated thumbnail correction',scope=SLUGS,automation24='PAUSED',newTopicsAllowed=False,newTtsAllowed=False,items=items,current='picking-sides'))
resources=[]
for p in psutil.process_iter(['pid','name','cmdline','create_time']):
 try:
  cmd=p.info['cmdline'] or []; joined=' '.join(cmd)
  if any(s in joined.lower() for s in ['train_multiview','gpu_queue','yam yam','yamyamstudio','ffmpeg','vite','render_narration']):resources.append(p.info)
 except psutil.Error:pass
write(BASE/'resources-before-first-render.json',dict(observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),cpuLogical=psutil.cpu_count(),cpuPercent=psutil.cpu_percent(interval=1),memoryAvailable=psutil.virtual_memory().available,processes=resources,newRenderThreads=2,newGpuTts=0,cimAccess='denied; psutil process command lines read successfully'))
thumb=ROOT/'projects/picking-sides/publishing/thumbnail-depth-v1.png'
src=Path('C:/Users/eazuo/.codex/generated_images/01a0f1af-3710-7742-b7c9-87594dc45400/exec-6c4d2fa2-a57a-4c0f-af82-3d396a2bdff6.png')
if not thumb.exists():shutil.copy2(src,thumb)
write(thumb.with_suffix('.json'),dict(status='generated-directly-reviewed-prepared-not-uploaded',sha256=sha(thumb),references=['projects/deconstruct-analyze-rebuild/publishing/thumbnail-v2.png','shared/assets/branding/yamyamcoding-cats-original.png'],method='builtin-imagegen',headline='남의 게임인데 왜 응원할까?',branding='얌얌코딩 | 게임 디자인',review=dict(legibleHeadline=True,naturalIllustration=True,noVideoInset=True,catIdentity=True),gitEssentialApproved=False))
plan=read(ROOT/'projects/picking-sides/production/final-v1/plan.json')
rows=[];cursor=0
for s in plan['scenes']:
 if s['classification']=='explanation':
  rows.append(dict(id=s['id'],frames=s['frames'],firstFrame=cursor,finalStartFrame=s['startFrame'],paragraphStarts=[round(p['start']*60) for p in s['paragraphs']]))
  cursor+=s['frames']
write(ROOT/'motion-canvas/src/projects/picking-sides/depth-reel-plan-v1.json',dict(fps=60,totalFrames=cursor,rows=rows,sourcePlanSha256=sha(ROOT/'projects/picking-sides/production/final-v1/plan.json'),allPixelsReviewed=False))
print(json.dumps(dict(baselines=len(items),firstWhiteFrames=cursor,whiteScenes=len(rows),gpuTts=0,thumbnail=thumb.relative_to(ROOT).as_posix())))
