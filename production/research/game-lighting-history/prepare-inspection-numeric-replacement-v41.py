"""Verify v40 source; prepare two-cut replacement while reusing 24 encoded cuts."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess
R=Path(__file__).resolve().parents[3]
P=R/'projects/game-lighting-history-04/production'
D=R/'production/research/game-lighting-history/local/episode04-inspection-math-repair-v40'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
def write(p,j):
 assert not p.exists(),p
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
job=read(D/'plan.json')['jobs'][0];source=R/job['output'];ex=read(R/job['execution'])
assert ex['status']=='complete' and ex['exitCode']==0 and job['frames']==1636
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';FF=FP.replace('ffprobe','ffmpeg')
cmd=[FP,'-v','error','-threads','2','-count_frames','-show_streams','-of','json',str(source)]
probe=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
v=next(x for x in probe['streams'] if x['codec_type']=='video')
assert (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',1636)
pkt=json.loads(subprocess.run([FP,'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',str(source)],capture_output=True,text=True,check=True).stdout)['packets']
assert sorted(x['pts'] for x in pkt)==list(range(0,1636*1500,1500))
assert all(x.get('duration',1500)==1500 for x in pkt)
decode=subprocess.run([FF,'-v','error','-threads','2','-i',str(source),'-f','null','NUL'],capture_output=True,text=True)
assert decode.returncode==0,decode.stderr
proof=source.with_suffix('.verification.json')
write(proof,{'verifiedAt':stamp(),'path':rel(source),'sha256':sha(source),'frames':1636,'probeCommand':cmd,'probe':probe,'wholeDecodeExitCode':decode.returncode,'allPacketPtsAndDurationsApproved':True,'allMovingPixelsReviewed':False,'allFinalPixelsReviewed':False})
old=read(P/'inspection-chapter-review-plan-v38.json');oldExec=read(P/'inspection-chapter-review-execution-v38.json')
assert oldExec['status']=='technical-review-pair-ready' and len(oldExec['results'])==26
scene={x['id']:x for x in job['scenes']};replaced=[];reused=[]
for i,c in enumerate(old['cuts']):
 if c['id'] in scene:
  s=scene[c['id']];assert c['frames']==s['frames']
  c.pop('reuseEncodedCut',None);c.update({'path':rel(source),'sha256':sha(source),'sourceStart':s['fromFrame']/60,'sourceSpanFrames':[s['fromFrame'],s['toFrame']],'verification':{'path':rel(proof),'sha256':sha(proof)}})
  replaced.append(c['id'])
 else:
  ref=oldExec['results'][i];assert sha(R/ref['path'])==ref['sha256'];assert ref['frames']==c['frames']
  c['reuseEncodedCut']={'id':c['id'],'path':ref['path'],'sha256':ref['sha256'],'frames':ref['frames'],'kind':c['kind']};reused.append(c['id'])
assert len(replaced)==2 and len(reused)==24
old['preparedAt']=stamp();old['numericReplacement']={'source':{'path':rel(source),'sha256':sha(source)},'replaced':replaced,'reusedByteIdentical':reused,'originalPcmAndCaptionsPreserved':True};old['scope']='Two numeric geometry repairs only; 24 unchanged encoded cuts, full original PCM and all69 captions retained. Final interleaving and upload remain pending.'
write(P/'inspection-chapter-review-plan-v41.json',old)
t=(R/'production/research/game-lighting-history/build-episode04-inspection-chapter-v38.py').read_text('utf-8').replace('v38','v41').replace("j['episode04InspectionChapterV34']","j['episode04InspectionChapterV41']")
file=R/'production/research/game-lighting-history/build-episode04-inspection-chapter-v41.py';assert not file.exists();file.write_text(t,'utf-8')
cp=R/'production/research/game-lighting-history/checkpoint.json';j=read(cp);j['episode04InspectionMathRepairV40'].update({'rendered':True,'framesVerified':1636,'wholeDecodeExitCode':0,'verification':rel(proof),'renderExecution':job['execution'],'renderWorkerAlive':False});j['episode04InspectionChapterV41']={'status':'prepared','plan':rel(P/'inspection-chapter-review-plan-v41.json'),'newCuts':2,'reusedCuts':24,'finalApproved':False};j['updatedAt']=stamp();tmp=cp.with_suffix('.v41.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
print(json.dumps({'verifiedFrames':1636,'newCuts':2,'reusedCuts':24,'finalApproved':False}))
