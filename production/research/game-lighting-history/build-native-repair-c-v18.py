"""Three directly chosen local inputs; whole-final approval remains separate."""
import importlib.util
from pathlib import Path
p=Path(__file__).with_name('review-media-common-v15.py')
s=importlib.util.spec_from_file_location('review_media',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
pp=m.PROD/'native-repair-c-plan-v18.json';plan=m.read(pp)
assert plan['loops']==0 and plan['rateChanges']==0 and plan['gpuJobs']==0
assert m.sha(m.ROOT/plan['baseline']['path'])==plan['baseline']['sha256']
assert m.sha(m.ROOT/plan['bPlan']['path'])==plan['bPlan']['sha256']
for c in plan['cuts']:assert m.sha(m.ROOT/c['media'])==c['sourceSha256']
resource=m.resources();out=m.ROOT/'production/research/game-lighting-history/local/native-repair-c-v18'
assert not out.exists(),'Preserve existing repair outputs';out.mkdir()
sp=m.PROD/'native-repair-c-execution-v18.json'
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,resourceObservation=resource,results=[],cpuThreads=2,gpuJobs=0,allFinalPixelsReviewed=False)
m.save(sp,state);cp=m.ROOT/'production/research/game-lighting-history/checkpoint.json'
def checkpoint(active):
 x=m.read(cp);x['episode03NativeRepairCExecution']=dict(path=m.rel(sp),status=state['status'],worker=state['worker'],active=active,completed=len(state['results']),total=len(plan['cuts']),allFinalPixelsReviewed=False)
 x['ownedActiveWork']=dict(type='CPU-native-repair-c-v18',execution=m.rel(sp),worker=state['worker'],cpuThreads=2,gpuJobs=0)if active else None
 x['updatedAt']=m.stamp();m.save(cp,x)
checkpoint(state['worker'])
try:
 for c in plan['cuts']:
  output=m.ROOT/c['output'];base='fps=60,scale=1920:1080:flags=lanczos,setsar=1,setpts=N/(60*TB)';font='C\\:/Windows/Fonts/malgun.ttf'
  if c.get('sourceUiLift'):
   f=out/(c['id']+'.filter');f.write_text(f"[0:v]{base},split=2[main][ui];[ui]crop=1920:136:0:850[strip];[main][strip]overlay=0:64,drawtext=fontfile='{font}':text='원본 비교 표기 · 제작사 제공 수치':x=16:y=8:fontsize=32:fontcolor=white:box=1:boxcolor=black:boxborderw=5[out]\n",'utf-8');options=['-filter_complex_script',f,'-map','[out]']
  else:
   base+=f",drawtext=fontfile='{font}':text='{c['sourceEvidenceLabel']}':x=16:y=8:fontsize=30:fontcolor=white:box=1:boxcolor=black:boxborderw=5";options=['-vf',base]
  encode=m.run([m.FF,'-n','-v','error','-threads','2','-filter_complex_threads','2','-ss',f"{c['sourceFromSeconds']:.9f}",'-i',m.ROOT/c['media'],'-an',*options,'-frames:v',str(c['frames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',output],c['id']+'-encode',state,sp,out)
  proof=m.verify_video(output,c['frames'],state,sp,out,c['id']);proof['encode']=encode;proof['cut']=c;rp=output.with_suffix('.verification.json');m.save(rp,proof)
  state['results'].append(dict(id=c['id'],frames=c['frames'],verification=m.rel(rp),sha256=proof['outputSha256']));m.save(sp,state);checkpoint(state['worker']);print(m.json.dumps(dict(done=len(state['results']),total=len(plan['cuts']),id=c['id'],decode=0)),flush=True)
 state.update(status='complete',exitCode=0,completedAt=m.stamp());m.save(sp,state);checkpoint(None)
except BaseException as e:
 state.update(status='failed',exitCode=1,error=str(e),failedAt=m.stamp());m.save(sp,state);checkpoint(None);raise
