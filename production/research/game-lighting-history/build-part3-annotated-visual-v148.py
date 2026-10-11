"""Repair seven evidenced native shots; keep narration/timing and other cuts intact."""
from pathlib import Path
import json, hashlib, os, subprocess, argparse, importlib.util
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT;P=ROOT/'projects/game-lighting-history-04/production';OUT=ROOT/'production/research/game-lighting-history/local/part3-annotations-v148'
PP=P/'part3-final-input-plan-v145.json';plan=m.read(PP);base=m.read(P/'part3-final-visual-build-v146.json')
assert base['planSha256']==m.sha(PP) and base['frames']==92038
ap=argparse.ArgumentParser();ap.add_argument('--prepare-only',action='store_true');args=ap.parse_args()
OUT.mkdir(parents=True,exist_ok=True)
# Encoded 1920x1080 points, directly observed through CUA at the listed times.
# Labels describe screen observation regions, not game-world distances or internals.
tracks={
 'hogwarts-terrace-reference':[
  {'role':'near-rail','color':'red','kind':'line','windows':[[4.4833,9.1],[11,12.4],[15.8,16.3]],'knots':[[4.4833,1039,267,224,9],[7,728,311,258,17],[8,772,349,149,6],[9,719,384,271,9],[11,800,416,311,13],[12.4,752,415,367,22],[15.8,708,319,334,113],[16.3,708,319,334,113]]},
  {'role':'distant-landscape','color':'teal','kind':'brackets','windows':[[7,9.1],[11,12.4]],'knots':[[7,1230,76,440,196],[9,785,24,443,187],[11,310,63,650,180],[12.4,330,60,530,220]]}
 ],
 'hogwarts-courtyard-ui':[
  {'role':'player-clothing','color':'red','kind':'brackets','windows':[[3.7333,15.8]],'knots':[[3.7333,575,382,205,310],[6,575,391,205,310],[8,580,366,195,325],[10,565,379,185,301],[12,538,388,175,288],[14,528,394,203,314],[15.8,540,389,160,305]]},
  {'role':'actual-Talk-prompt','color':'teal','kind':'brackets','windows':[[14,15.8]],'knots':[[14,860,151,207,44],[15.8,824,140,206,39]]}
 ],
 'grade-shared-reference':[
  {'role':'same-lowest-front-cube-face','color':'red','kind':'brackets','windows':[[4.2333,10.05],[13,16.9333]],'knots':[[4.2333,535,716,60,60],[8,535,716,60,60],[10.05,552,675,58,49],[13,591,701,68,54],[14,591,701,68,54],[15,516,703,64,58],[16.9333,516,703,64,58]]},
  {'role':'Tonemapper-heading','color':'teal','kind':'brackets','windows':[[8,11.8],[13,16.9333]],'knots':[[8,1140,476,240,32],[11.8,1140,476,240,32],[13,1140,527,240,32],[16.9333,1140,527,240,32]]}
 ]
}
colors={'red':'&H004B48EF&','teal':'&H00C2C773&','white':'&H00F5F5F5&','yellow':'&H0083CFE8&'}
def timing(t):
 cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
def interp(knots,t):
 if t<=knots[0][0]:return knots[0][1:]
 for a,b in zip(knots,knots[1:]):
  if t<=b[0]:
   f=(t-a[0])/(b[0]-a[0]);return [round(x+(y-x)*f) for x,y in zip(a[1:],b[1:])]
 return knots[-1][1:]
def shape(kind,w,h):
 if kind=='line':return f'm 0 0 l {w} {h} l {w} {h+5} l 0 5'
 d=4;k=min(18,round(min(w,h)*.3));boxes=[(0,0,k,d),(0,0,d,k),(w-k,0,k,d),(w-d,0,d,k),(0,h-d,k,d),(0,h-k,d,k),(w-k,h-d,k,d),(w-d,h-k,d,k)]
 return ' '.join(f'm {x} {y} l {x+ww} {y} l {x+ww} {y+hh} l {x} {y+hh}' for x,y,ww,hh in boxes)
def event(lo,hi,text,layer=0):return f'Dialogue: {layer},{timing(lo)},{timing(hi)},Base,,0,0,0,,{text}'
def label(lo,hi,text,x,y,col='white'):
 return event(lo,hi,'{\\an7\\pos('+str(x)+','+str(y)+')\\fs28\\bord3\\shad0\\1c'+colors[col]+'\\3c&H000000&}'+text,2)
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,Malgun Gothic,28,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
prepared=[]
for key,ts in tracks.items():
 lines=[]
 for tr in ts:
  for lo,hi in tr['windows']:
   frame=round(lo*60);end=round(hi*60)
   while frame<end:
    nxt=min(frame+3,end);t=frame/60;x,y,w,h=interp(tr['knots'],t)
    assert 0<=x<=1900 and 0<=y<900 and x+w<=1920 and y+h<900,(key,tr['role'],x,y,w,h)
    lines.append(event(t,nxt/60,'{\\an7\\pos('+str(x)+','+str(y)+')\\p1\\bord2\\shad0\\1c'+colors[tr['color']]+'\\3c&H000000&}'+shape(tr['kind'],w,h)+'{\\p0}',1));frame=nxt
 if key=='hogwarts-terrace-reference':
  lines += [label(4.4833,16.3,'빨강: 가까운 난간',50,100,'red'),label(7,12.4,'청록: 먼 풍경',50,140,'teal'),label(12.4,16.3,'카메라 이동 · 가림에 따라 다시 관찰',50,140)]
 elif key=='hogwarts-courtyard-ui':
  lines += [label(3.7333,15.8,'빨강: 관찰하는 옷',1170,110,'red'),label(3.7333,14,'게임의 Talk 안내는 접근 후 나타납니다',1050,150),label(14,15.8,'청록: 실제 Talk 안내',1170,150,'teal')]
 else:
  lines += [label(4.2333,16.9333,'빨강: 같은 면 · 화면 관찰 기준',55,130,'red'),label(8,16.9333,'청록: 설정 이름',55,170,'teal'),label(10.05,13,'카메라 이동 후 같은 면을 다시 잡습니다',55,210)]
 path=OUT/(key+'.ass');path.write_text(header+'\n'.join(lines)+'\n','utf8');prepared.append({'id':key,'path':m.rel(path),'sha256':m.sha(path),'events':len(lines),'tracking':ts})
request={'preparedAt':m.stamp(),'planSha256':m.sha(PP),'baseVisualSha256':base['sha256'],'nativeRepairs':prepared,'resourceWindowCrop':{'x':64,'y':112,'width':1500,'height':838,'source':'production/research/game-lighting-history/local/episode04-additional-action-v47/virtual-texture-editor-goldcoast2024.mp4','nativeIntervalsSeconds':[[862,884],[884,906],[906,928],[928,950]],'observedVia':'CUA normal-speed entire intervals and endpoint screenshots','reason':'Keep actual editor window, exclude presenter and conference backdrop/logo. Fit within 1920x960 without aspect distortion; reserve fixed-caption margin.'},'delayedTalkUiNote':'Narration identifies the forthcoming Talk prompt. A separate external label explicitly says it appears after approach; no quest marker is relabelled as Talk. Highlight only directly observed actual Talk pixels at native175–176.8.','cameraReacquisition':'Hide marks across fast turns/UI scroll, then re-anchor to directly observed same face/near rail; never leave a detached arrow.','allOriginalCutFramesPreserved':True,'mixChanged':False,'sourceAudioStreams':0,'allMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,'newGitImages':0}
RQ=P/'part3-annotation-repair-request-v148.json';m.save(RQ,request)
if args.prepare_only:
 print(json.dumps({'annotations':len(prepared),'presenterCrops':4,'preparedOnly':True,'rendered':False}));raise SystemExit
resources=m.resources();SP=P/'part3-annotation-repair-execution-v148.json';assert not SP.exists()
import psutil
ancestors={p.pid for p in psutil.Process().parents()}|{os.getpid()}
for proc in psutil.process_iter(['pid','cmdline','name','create_time']):
 d=proc.info;cmd=' '.join(d['cmdline'] or [])
 if d['pid'] not in ancestors and any(s in cmd for s in ['review-part3-final-mix-v147.py','review-part3-chunk-artifact-contexts-v152.py','build-part3-final-media-v146.py','build-part3-annotated-visual-v148.py','build-part3-reviewed-pair-v149.py']):
  raise RuntimeError('Owned single-job slot active: '+str(d))
state={'startedAt':m.stamp(),'status':'running','worker':m.worker(),'active':None,'resourceObservation':resources,'commands':[],'results':[],'cpuThreads':2,'gpuJobs':0,'allMovingPixelsReviewed':False,'uploaded':False};m.save(SP,state)
def checkpoint():
 cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp();j['episode04Part3AnnotationsV148']={'execution':m.rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'results':len(state['results']),'finalApproved':False};j['ownedActiveWork']={'type':'part3-native-annotation-repair','execution':m.rel(SP),'worker':state['worker'],'cpuThreads':2,'gpuJobs':0,'next':'Review seven changed moving shots, current ASR and final pair'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':m.rel(SP),'next':'Direct moving annotation review and gated final pair'};m.save(cp,j)
def run(cmd,label):
 checkpoint();r=m.run(cmd,label,state,SP,OUT);checkpoint();return r
files=[ROOT/plan['branding']['path']];records=[];byid={r['id']:r for r in base['cuts']};byass={r['id']:r for r in prepared}
try:
 for i,c in enumerate(plan['cuts']):
  old=byid[c['id']];src=ROOT/old['path'];assert m.sha(src)==old['sha256'];dest=src;changed=False
  if c['id'] in byass:
   ass=ROOT/byass[c['id']]['path'];dest=OUT/f'cut-{i+1:03d}-annotated.mp4';vf=f"settb=1/90000,setpts=N*1500,ass=filename='{m.rel(ass)}'"
   cmd=[m.FF,'-n','-hide_banner','-nostdin','-threads','2','-i',src,'-filter_threads','2','-vf',vf]
   changed=True
  elif c['id'].startswith('resource-') and i+1 in [75,76,83,84]:
   dest=OUT/f'cut-{i+1:03d}-editor-only.mp4';start=c['proposedCuts'][0]['inFrame']/60
   vf="fps=60,setpts=PTS-STARTPTS,crop=1500:838:64:112,scale=1920:960:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:0:black,setsar=1,settb=1/90000,setpts=N*1500"
   label=OUT/f'cut-{i+1:03d}-identity.txt';label.write_text('Unreal Engine · 2024 실제 자원/설정 시연','utf8')
   vf+=f",drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{m.rel(label)}':expansion=none:x=32:y=22:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.82:boxborderw=8"
   cmd=[m.FF,'-n','-hide_banner','-nostdin','-threads','2','-ss',f'{start:.9f}','-i',ROOT/c['video']['path'],'-filter_threads','2','-vf',vf];changed=True
  if changed:
   run([*cmd,'-frames:v',str(c['frames']),'-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','fast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',dest],f'repair-{i+1:03d}')
   pr=json.loads(subprocess.run(list(map(str,[m.FP,'-v','error','-count_frames','-show_entries','stream=nb_read_frames,time_base','-of','json',dest])),capture_output=True,text=True,check=True).stdout)
   assert int(pr['streams'][0]['nb_read_frames'])==c['frames'] and pr['streams'][0]['time_base']=='1/90000'
  files.append(dest);records.append({**old,'path':m.rel(dest),'sha256':m.sha(dest),'repairedNative':changed,'timingChanged':False});state['results']=records;m.save(SP,state)
 files.append(ROOT/plan['membership']['path']);concat=OUT/'annotated.concat.txt';concat.write_text('\n'.join("file '"+str(p).replace('\\','/')+"'" for p in files)+'\n','utf8');visual=OUT/'annotated-silent-visual.mp4'
 run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-f','concat','-safe','0','-i',concat,'-map','0:v:0','-an','-c','copy','-video_track_timescale','90000','-movflags','+faststart',visual],'concat')
 decode=run([m.FF,'-v','error','-nostdin','-threads','2','-i',visual,'-f','null','NUL'],'whole-decode')
 probe=json.loads(subprocess.run(list(map(str,[m.FP,'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,width,height,r_frame_rate,time_base,nb_read_frames','-of','json',visual])),capture_output=True,text=True,check=True).stdout)
 assert len(probe['streams'])==1;v=probe['streams'][0];assert (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',plan['finalFrames'])
 proof={'builtAt':m.stamp(),'path':m.rel(visual),'sha256':m.sha(visual),'planSha256':m.sha(PP),'repairRequestSha256':m.sha(RQ),'frames':plan['finalFrames'],'wholeDecodeExitCode':decode['exitCode'],'probe':probe,'cuts':records,'repairedCutCount':7,'allOriginalCutFramesPreserved':True,'unchangedCurrentMix':True,'allMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,'qaApproved':False,'uploaded':False,'newGitImages':0};m.save(P/'part3-annotated-visual-build-v148.json',proof)
 state.update(status='complete-awaiting-moving-pixel-review',exitCode=0,completedAt=m.stamp(),active=None);m.save(SP,state);checkpoint();print(json.dumps({'sevenNativeRepairs':7,'frames':plan['finalFrames'],'decode':0,'pixelsApproved':False}))
except BaseException as e:
 state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
