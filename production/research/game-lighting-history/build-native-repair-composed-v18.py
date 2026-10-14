"""One sequential CPU batch of cropped native footage and same-frame source UI details."""
import importlib.util,sys
from pathlib import Path
p=Path(__file__).with_name('review-media-common-v15.py')
s=importlib.util.spec_from_file_location('review_media',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
suffix=sys.argv[1];assert suffix in ['e5','f']
pp=m.PROD/f'native-repair-{suffix}-plan-v18.json';plan=m.read(pp)
assert plan['loops']==0 and plan['rateChanges']==0 and plan['gpuJobs']==0
assert m.sha(m.ROOT/plan['baseline']['path'])==plan['baseline']['sha256']
for c in plan['cuts']:assert m.sha(m.ROOT/c['media'])==c['sourceSha256']
resource=m.resources();out=m.ROOT/f'production/research/game-lighting-history/local/native-repair-{suffix}-v18'
assert not out.exists(),'Preserve existing outputs';out.mkdir()
sp=m.PROD/f'native-repair-{suffix}-execution-v18.json'
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,resourceObservation=resource,planSha256=m.sha(pp),results=[],cpuThreads=2,gpuJobs=0,allFinalPixelsReviewed=False)
m.save(sp,state);cp=m.ROOT/'production/research/game-lighting-history/checkpoint.json'
def checkpoint(active):
 x=m.read(cp);x[f'episode03NativeRepair{suffix.upper()}Execution']=dict(path=m.rel(sp),status=state['status'],worker=state['worker'],active=active,completed=len(state['results']),total=len(plan['cuts']),allFinalPixelsReviewed=False)
 x['ownedActiveWork']=dict(type=f'CPU-native-repair-{suffix}-v18',execution=m.rel(sp),worker=state['worker'],cpuThreads=2,gpuJobs=0)if active else None
 x['updatedAt']=m.stamp();m.save(cp,x)
checkpoint(state['worker'])
try:
 for c in plan['cuts']:
  output=m.ROOT/c['output'];x,y,w,h=c['crop'];font='C\\:/Windows/Fonts/malgun.ttf'
  base='fps=60,setpts=N/(60*TB)';main=f'crop={w}:{h}:{x}:{y},scale=1920:1080:flags=lanczos,setsar=1'
  label=f"drawtext=fontfile='{font}':text='{c['sourceEvidenceLabel']}':x=16:y=8:fontsize=30:fontcolor=white:box=1:boxcolor=black:boxborderw=5"
  if c.get('sourceUiLift'):
   q=c['sourceUiLift'];ux,uy,uw,uh=q['crop'];dx,dy,dw,dh=q['destination'];enable=q.get('enable','1')
   filters=f"[0:v]{base},split=2[rawmain][rawui];[rawmain]{main}[main];[rawui]crop={uw}:{uh}:{ux}:{uy},scale={dw}:{dh}:flags=lanczos,setsar=1[ui];[main][ui]overlay={dx}:{dy}:enable='{enable}',{label},drawtext=fontfile='{font}':text='{q['label']}':x={dx}:y={dy-42}:fontsize=30:fontcolor=white:box=1:boxcolor=black:boxborderw=5:enable='{enable}'[out]"
  else:filters=f'[0:v]{base},{main},{label}[out]'
  fp=out/(c['id']+'.filter');fp.write_text(filters+'\n','utf-8')
  encode=m.run([m.FF,'-n','-v','error','-threads','2','-filter_complex_threads','2','-ss',f"{c['sourceFromSeconds']:.9f}",'-i',m.ROOT/c['media'],'-an','-filter_complex_script',fp,'-map','[out]','-frames:v',str(c['frames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',output],c['id']+'-encode',state,sp,out)
  proof=m.verify_video(output,c['frames'],state,sp,out,c['id']);proof['encode']=encode;proof['cut']=c;rp=output.with_suffix('.verification.json');m.save(rp,proof)
  state['results'].append(dict(id=c['id'],frames=c['frames'],verification=m.rel(rp),sha256=proof['outputSha256']));m.save(sp,state);checkpoint(state['worker']);print(m.json.dumps(dict(done=len(state['results']),total=len(plan['cuts']),id=c['id'],decode=0)),flush=True)
 state.update(status='complete',exitCode=0,completedAt=m.stamp());m.save(sp,state);checkpoint(None)
except BaseException as e:
 state.update(status='failed',exitCode=1,error=str(e),failedAt=m.stamp());m.save(sp,state);checkpoint(None);raise
