"""Single CPU inspection, only after the saved source acquisition succeeds."""
import hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path('D:/Github/Video-Editing');P=R/'projects/player-customization';B=R/'production/batches/sakurai-planning-game-design/proof-player-customization'
local=R/'shared/output/player-customization/research';src=local/'game-sources/ovxaYxLbUNE-ui-qol-3900-4980.mp4'
out=local/'warframe-native-inspection-v1';ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';fp='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
acq=load(B/'official-source-acquisition-v1.json')
if acq.get('downloadExitCode')!=0 or not src.exists():raise SystemExit('Source still incomplete/failed: inspect the acquisition and do not launch another job.')
if out.exists():raise SystemExit('Existing native inspection preserved: read its results before resuming; do not repeat.')
out.mkdir();(out/'frames').mkdir();(out/'boards').mkdir()
statepath=P/'production/native-inspection-v1.json'
state={'schemaVersion':1,'startedAt':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'commandLine':[sys.executable,*sys.argv],'cpuThreads':2,'gpu':0,'status':'probe','source':'shared/output/player-customization/research/game-sources/ovxaYxLbUNE-ui-qol-3900-4980.mp4','sourceSha256':sha(src),'framesDirectlyRead':False,'actualGameIntervalsApproved':False,'cropApproved':False,'finalQaApproved':False}
save(statepath,state)
probe=subprocess.run([fp,'-v','error','-show_streams','-show_format','-of','json',str(src)],capture_output=True,text=True)
state['probeExitCode']=probe.returncode
if probe.returncode:save(statepath,state);raise SystemExit(probe.stderr)
state['probe']=json.loads(probe.stdout);save(statepath,state)
commands=[('whole-native-decode',[ff,'-nostdin','-v','error','-threads','2','-i',str(src),'-an','-f','null','-']),('sample-native-10sec',[ff,'-nostdin','-v','error','-threads','2','-i',str(src),'-vf','fps=1/10,scale=960:-1','-fps_mode','vfr','-threads','2',str(out/'frames/native-%03d.png')])]
state['operations']=[]
for name,cmd in commands:
 state['status']=name;state['operations'].append({'name':name,'commandLine':cmd});save(statepath,state)
 with (out/(name+'.log')).open('w',encoding='utf-8') as log:
  child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);state['childPid']=child.pid;save(statepath,state);code=child.wait()
 state['operations'][-1]['exitCode']=code;save(statepath,state)
 if code:state['status']='failed-'+name;save(statepath,state);raise SystemExit(code)
frames=sorted((out/'frames').glob('native-*.png'));boards=[]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26)
for offset in range(0,len(frames),4):
 group=frames[offset:offset+4];canvas=Image.new('RGB',(1920,1170),'white');draw=ImageDraw.Draw(canvas)
 for k,path in enumerate(group):
  n=offset+k;x=(k%2)*960;y=(k//2)*585
  img=Image.open(path).convert('RGB');canvas.paste(img,(x,y+45))
  # fps picks the center of each ten-second window; source timestamp is an approximate navigation aid, not a verified cut boundary.
  draw.text((x+12,y+5),f'{n+1:03d} | interval {n*10:04d}-{n*10+10:04d}s | source approx {3900+n*10}s',font=font,fill='black')
 path=out/'boards'/f'board-{offset//4+1:02d}.png';canvas.save(path);boards.append({'path':path.relative_to(R).as_posix(),'sha256':sha(path),'frames':[p.name for p in group],'directlyRead':False})
state.update({'status':'native-decode-and-sample-extraction-complete-direct-review-pending','finishedAt':datetime.now(timezone.utc).isoformat(),'sampleCount':len(frames),'boards':boards,'sampleFrames':[{'path':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in frames],'allRasterLocalOnly':True,'sourceAudioUsed':False})
save(statepath,state)
print(json.dumps({'status':state['status'],'samples':len(frames),'boards':len(boards),'decodeExit':state['operations'][0]['exitCode']}),flush=True)
