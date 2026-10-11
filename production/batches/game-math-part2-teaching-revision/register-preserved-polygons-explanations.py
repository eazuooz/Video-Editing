"""Keep eleven successful renders; two retake-anchor failures are rerendered."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
source=ROOT/'manim/projects/game-math-part2-teaching-revision/polygons_additions.py'
before=source.read_text(encoding='utf8').replace("sentence('균일한 종이')","sentence('종이 삼각형을')").replace("sentence('모든 변까지')","sentence('변이나 꼭짓점까지')").replace("sentence('이번에는 이웃한')","sentence('이번에는 세 이웃')")
old_sha=hashlib.sha256(before.encode('utf8')).hexdigest();timing=read(O/'combined-addition-timing.json')
for slug in ['game-math-polygon-centers-v2','game-math-polygon-partition-v2']:
 for slot in read(ROOT/f'projects/{slug}/production/timeline.json')['scenes']:
  if not slot['preservedOriginal'] and slot['classification']=='explanation':timing[slot['id']]=slot
p=O/'caption-safe-polygons_additions-receipts.json';records=read(p) if p.exists() else {};kept=[]
for ident,t in timing.items():
 if t['sourceType']=='actual-footage' or ident in ['QB01','QB07']:continue
 video=O/f'caption-safe-v2/videos/polygons_additions/1080p60/{ident}.mp4'
 assert video.exists(),ident
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(video)],text=True,creationflags=subprocess.CREATE_NO_WINDOW));v=next(s for s in info['streams'] if s['codec_type']=='video')
 assert v['r_frame_rate']=='60/1' and (v['width'],v['height'])==(1920,1080)
 assert 0<=t['frames']-int(v['nb_frames'])<=3
 records[ident]={'sourceSha256':old_sha,'unchangedActiveBranchWithCurrentSource':True,'retainedReason':'The only source edits are sentence anchors withinQB01 andQB07; this successful scene branch and its measured timing were unchanged.','voiceSha256':t['voiceSha256'],'lineStarts':t['lineStarts'],'seconds':t['seconds'],'frames':int(v['nb_frames']),'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'pixelApproval':False};kept.append(ident)
p.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(B/'polygons-explanation-render-reuse.json').write_text(json.dumps({'retained':kept,'rerenderRequired':['QB01','QB07'],'previousRuntimeSourceSha256':old_sha,'currentSourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'originalRenderLog':'shared/output/game-math-part2-teaching-revision/polygons/explanations-render.log','finalPixelsApproved':False},indent=2)+'\n',encoding='utf8')
print('Retained',len(kept),'successful explanations; two updated anchors still need render.')
