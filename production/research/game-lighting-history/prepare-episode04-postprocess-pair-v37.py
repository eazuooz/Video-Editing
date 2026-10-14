"""Verify the completed two-scene bank and replace only its two chapter cuts."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,psutil
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
D=R/'production/research/game-lighting-history/local/episode04-postprocess-math-repair-v36'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,j):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
plan=read(D/'plan.json');job=plan['jobs'][0];f=R/job['output'];ep=R/job['execution'];e=read(ep)
assert e['status']=='complete' and e['exitCode']==0 and job['frames']==1617
for proc in psutil.process_iter(['pid','name','cmdline']):
 try:
  if 'ffmpeg' in (proc.info['name']or'').lower() and 'game-lighting-history' in ' '.join(proc.info['cmdline']or[]):raise RuntimeError('Owned media slot busy')
 except(psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
cmd=[str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,width,height,r_frame_rate,time_base,nb_read_frames,duration','-of','json',str(f)]
probe=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout);v=next(s for s in probe['streams'] if s['codec_type']=='video')
assert (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',1617)
pkt=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',str(f)],capture_output=True,text=True,check=True).stdout)['packets']
assert sorted(x['pts']for x in pkt)==list(range(0,1617*1500,1500)) and all(x.get('duration',1500)==1500 for x in pkt)
decode=[str(FF),'-v','error','-threads','2','-i',str(f),'-f','null','NUL'];result=subprocess.run(decode,capture_output=True,text=True);assert result.returncode==0,result.stderr
vp=f.with_suffix('.verification.json');write(vp,{'verifiedAt':now(),'output':{'path':rel(f),'sha256':sha(f)},'execution':{'path':rel(ep),'sha256':sha(ep)},'probe':probe,'probeCommand':cmd,'frames':1617,'allPacketPtsAndDurationsApproved':True,'wholeDecodeCommand':decode,'wholeDecodeExitCode':0,'gpuObservation':gpu,'gpuJobs':0,'cpuThreads':2,'allFinalPixelsReviewed':False})
session=D/'session.json';write(session,{'verifiedAt':now(),'serverPid':e['serverPid'],'ffmpegPid':e['ffmpegPid'],'completionObservedFromExporterExecution':True,'execution':{'path':rel(ep),'sha256':sha(ep)},'exitCode':0,'sourceOnly':True})
old=read(P/'postprocess-chapter-review-plan-v34.json');results={x['id']:x for x in read(P/'postprocess-chapter-review-execution-v34.json')['results']}
for c in old['cuts']:
 if c['id'] in ['original-22p-1','original-22p-2']:
  m=next(s for s in job['scenes'] if s['id']==c['id']);c.update(path=rel(f),sha256=sha(f),sourceStart=m['fromFrame']/60,sourceSpanFrames=[m['fromFrame'],m['toFrame']],verification={'path':rel(vp),'sha256':sha(vp)})
 else:
  ref=results[c['id']];assert sha(R/ref['path'])==ref['sha256'];c['reuseEncodedCut']=ref
old.update(preparedAt=now(),supersedesRejectedMath={'path':rel(P/'postprocess-encoded-math-rejection-v34.json'),'sha256':sha(P/'postprocess-encoded-math-rejection-v34.json')},repairedModel={'path':plan['model']['path'],'sha256':plan['model']['sha256']},reusedCleanCuts=9,newSourceScenes=2)
write(P/'postprocess-chapter-review-plan-v37.json',old)
builder=(R/'production/research/game-lighting-history/build-episode04-postprocess-chapter-v34.py').read_text('utf-8').replace('v34','v37')
bp=R/'production/research/game-lighting-history/build-episode04-postprocess-chapter-v37.py';assert not bp.exists();bp.write_text(builder,'utf-8')
cp=R/'production/research/game-lighting-history/checkpoint.json';j=read(cp);j['episode04PostprocessMathRepairV36'].update(rendered=True,framesVerified=1617,wholeDecodeExitCode=0,verification=rel(vp),finalApproved=False);j['ownedActiveWork']={'status':'no-active-owned-media-worker','next':'v37 pair: reuse9 clean cuts and replace2 mathematical scenes; caption review and final allocation pending'};j['updatedAt']=now();temp=cp.with_suffix('.v37.tmp');temp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');temp.replace(cp)
print(json.dumps({'verifiedFrames':1617,'pairPlan':rel(P/'postprocess-chapter-review-plan-v37.json'),'reusedCuts':9,'changedCuts':2,'newTts':0}))
