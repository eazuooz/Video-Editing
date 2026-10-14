"""Record the one CPU recognizer's actual identity and immutable completed results."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
ep=BASE/'guided-observation-asr-execution-v107.json';e=read(ep);i=e['actualIdentity'];alive=False;observed=None
try:
 p=psutil.Process(i['pid']);observed=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),exe=p.exe());alive=abs(observed['createTime']-i['createTime'])<.01 and observed['command']==i['command'] and observed['cwd']==i['cwd']
except (psutil.NoSuchProcess,psutil.AccessDenied):pass
for x in e['completed']:
 file=ROOT/x['result']
 if hashlib.sha256(file.read_bytes()).hexdigest()!=x['sha256']:raise RuntimeError('Completed ASR changed '+x['label'])
j=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),sessionId=75723,status=e['status'],expectedWindows=e['expectedWindows'],completedWindows=len(e['completed']),current=e.get('current'),actualIdentity=i,identityMatchedAlive=alive,observedProcess=observed,execution=dict(path=ep.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(ep.read_bytes()).hexdigest()),cpuThreads=2 if alive else 0,gpuJobs=0,allWholeAndIndependentAsrDirectlyReviewed=False,humanWholeListeningApproved=False,finalMixedAsrApproved=False,allFinalPixelsReviewed=False,bodyRatioApproved=False,uploaded=False,next='Read each complete expected/recognized whole and adjacent-context text as results arrive. Resolve omissions, repeats, names and endings without heuristic-only approval; then exact classified native cuts and word-clocked spatial/moving-annotation production.')
out=BASE/'guided-observation-asr-progress-v111.json';out.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=read(cp);c['episode04SelectedAsrV107']={k:j[k] for k in ['sessionId','status','expectedWindows','completedWindows','current','actualIdentity','identityMatchedAlive','cpuThreads','gpuJobs','next']};c['episode04SelectedAsrV107']['record']=out.relative_to(ROOT).as_posix();c['updatedAt']=j['observedAt'];tmp=cp.with_name(cp.name+'.asr-observing-'+str(os.getpid()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,cp)
print(json.dumps(dict(output=out.relative_to(ROOT).as_posix(),completed=j['completedWindows'],expected=j['expectedWindows'],current=j['current'],identityMatchedAlive=alive,uploaded=False)))
