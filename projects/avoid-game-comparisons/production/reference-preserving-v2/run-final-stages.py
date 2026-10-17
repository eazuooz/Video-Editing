"""Sequential costly jobs; recheck selected scope before each one."""
from pathlib import Path
import subprocess,sys,json,datetime
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent;L=R/'projects/avoid-game-comparisons/production/local/reference-preserving-v2';state={'stages':[]}
repair='--repair-audio' in sys.argv
if (repair or '--verify-only' in sys.argv) and (L/'final-stages.json').exists():state['priorRun']=json.loads((L/'final-stages.json').read_text())
stages=[('audio',['build-audio.py'])]+([('audio-remux',['compose-video.py','remux'])] if repair else [('diagram-slices',['compose-video.py','slices']),('master-pair',['compose-video.py','pair'])])+[('whole-final-asr',['review-final-audio.py']),('integrity-and-pixels',['verify-output.py'])]
if '--verify-only' in sys.argv:stages=stages[-2:]
for name,args in stages:
 c=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'));assert c['selectedVideo']=='avoid-game-comparisons'
 row={'stage':name,'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running'};state['stages'].append(row);(L/'final-stages.json').write_text(json.dumps(state,indent=2)+'\n');print('Starting',name,flush=True)
 log=L/(name+'-stage.log')
 with log.open('w',encoding='utf8') as f:r=subprocess.run([sys.executable,'-X','utf8',str(V/args[0]),*args[1:]],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 row.update(status='complete' if r.returncode==0 else 'failed',exitCode=r.returncode,completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());(L/'final-stages.json').write_text(json.dumps(state,indent=2)+'\n')
 if r.returncode:print(log.read_text(encoding='utf8',errors='replace')[-3000:]);sys.exit(r.returncode)
 print('Completed',name,flush=True)
print('Encoded output and technical evidence ready; direct text/pixel/motion review still required',flush=True)
