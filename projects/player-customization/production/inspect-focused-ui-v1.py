"""Focused native review only; images remain local and do not approve final footage."""
import hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path('D:/Github/Video-Editing');P=R/'projects/player-customization/production';src=R/'shared/output/player-customization/research/game-sources/ovxaYxLbUNE-ui-qol-3900-4980.mp4'
out=R/'shared/output/player-customization/research/focused-ui-v1';ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(d):(P/'focused-ui-execution-v1.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=json.loads((P/'native-inspection-v1.json').read_text(encoding='utf-8-sig'))
assert old['boardsDirectlyRead'] and all(x['exitCode']==0 for x in old['operations'])
assert sha(src)==old['sourceSha256']
if out.exists():raise SystemExit('Existing focused evidence preserved; inspect before any resume.')
out.mkdir();(out/'native').mkdir();(out/'boards').mkdir()
times=sorted(set(list(range(0,141,4))+list(range(144,207,2))+list(range(546,581,2))+list(range(630,681,2))))
state={'schemaVersion':1,'startedAt':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'commandLine':[sys.executable,*sys.argv],'status':'extracting','source':src.relative_to(R).as_posix(),'sourceSha256':old['sourceSha256'],'cpuThreads':2,'gpu':0,'sourceAudioUsed':False,'samples':[],'allRasterLocalOnly':True,'directReviewApproved':False,'exactCutBoundariesApproved':False,'cropApproved':False}
save(state)
for j,t in enumerate(times):
 path=out/'native'/f'native-{t:04d}.png'
 cmd=[ff,'-nostdin','-v','error','-threads','2','-ss',str(t),'-i',str(src),'-frames:v','1','-an','-threads','2',str(path)]
 result=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
 if result.returncode:state.update({'status':'failed','failedCommand':cmd,'stderr':result.stderr});save(state);raise SystemExit(result.returncode)
 state['samples'].append({'requestedLocalSecond':t,'requestedSourceSecond':3900+t,'path':path.relative_to(R).as_posix(),'sha256':sha(path),'directlyRead':False,'seekCommand':cmd,'seekExitCode':result.returncode});save(state)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23);state['boards']=[]
for offset in range(0,len(state['samples']),4):
 group=state['samples'][offset:offset+4];canvas=Image.new('RGB',(1920,1170),'white');d=ImageDraw.Draw(canvas)
 for k,row in enumerate(group):
  x=k%2*960;y=k//2*585;img=Image.open(R/row['path']).convert('RGB');canvas.paste(img.resize((960,540)),(x,y+45))
  d.text((x+10,y+8),f"local seek {row['requestedLocalSecond']}s | source {row['requestedSourceSecond']}s",font=font,fill='black')
 path=out/'boards'/f'board-{offset//4+1:02d}.png';canvas.save(path)
 state['boards'].append({'path':path.relative_to(R).as_posix(),'sha256':sha(path),'samples':[r['requestedLocalSecond'] for r in group],'directlyRead':False})
state.update({'status':'focused-native-extraction-complete-direct-review-pending','finishedAt':datetime.now(timezone.utc).isoformat(),'sampleCount':len(times)});save(state)
print(json.dumps({'status':state['status'],'nativeSamples':len(times),'boards':len(state['boards']),'cpu':2,'gpu':0}),flush=True)
