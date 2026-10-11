"""Render eight independent additions with actual narration timing, not preview timing."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,cv2
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
O=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--only');args=parser.parse_args()
source=ROOT/'manim/projects/game-math-part2-teaching-revision/quaternion_four_game_v3.py'
ledger=O/'explanation-render-receipts.json';receipts=read(ledger) if ledger.exists() else {}
for episode in ['foundations','calculations']:
 path=ROOT/f'projects/game-math-quaternion-{episode}-v3/production/timeline.json';timeline=read(path)
 for slot in timeline['scenes']:
  if slot['preservedOriginal'] or slot['classification']!='explanation':continue
  ident=slot['id']
  if args.only and ident not in args.only.split(','):continue
  assert slot['fragmentCues'],'Align actual new voice before rendering'
  voice=ROOT/slot['voice'];assert sha(voice)==slot['voiceSha256']
  target=O/f'explanation-final/videos/quaternion_four_game_v3/1080p60/{ident}.mp4'
  signature=dict(voiceSha256=slot['voiceSha256'],lineStarts=slot['lineStarts'],fragmentCues=slot['fragmentCues'],seconds=slot['seconds'],sourceSha256=sha(source))
  if target.exists() and all(receipts.get(ident,{}).get(k)==v for k,v in signature.items()) and sha(target)==receipts[ident]['videoSha256']:
   print('Preserved current narrated explanation',ident,flush=True);continue
  env=dict(os.environ);env.pop('QUATERNION_COMPARISON_PREVIEW',None);env['QUATERNION_COMPARISON_TIMING']=str(path);env['PYTHONUTF8']='1'
  log=O/f'explanation-final/{ident}-render.log';log.parent.mkdir(parents=True,exist_ok=True)
  with log.open('w',encoding='utf8') as f:
   subprocess.run([str(ROOT/'manim/.venv/Scripts/python.exe'),'-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',str(O/'explanation-final'),str(source),ident],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  cap=cv2.VideoCapture(str(target));frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS);cap.release()
  assert fps==60 and 0<=slot['frames']-frames<=3,(ident,frames,slot['frames'])
  receipts[ident]={**signature,'frames':frames,'videoSha256':sha(target),'silentSceneOnly':True,'finalNarrationAndCaptionMovingReview':False}
  ledger.write_text(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  print('Rendered actual-timing comparison',ident,frames,'frames; direct combined review pending',flush=True)
