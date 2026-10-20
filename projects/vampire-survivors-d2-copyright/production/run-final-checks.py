"""One selected video, sequential expensive jobs, no upload or next-video action."""
from pathlib import Path
import json,subprocess,sys,datetime,os
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';L=P/'production/local';PY=R/'qwen3-tts/.venv/Scripts/python.exe'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
steps=[('encode','finish-local.py','encode'),('whole-final-mix-ASR','prepare-audio.py','final-asr'),('full-decode-and-PTS','finish-local.py','integrity'),('all-caption-cut-and-motion-pixels','finish-local.py','pixels')]
for label,script,arg in steps:
 control=rd(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name and control['newProductionAuthorization']['fullProductionAuthorized']
 command=[str(PY),str(P/'production'/script),arg];print('Starting',label,flush=True)
 child=subprocess.Popen(command,cwd=R,env=dict(os.environ,PYTHONIOENCODING='utf-8'))
 cp=rd(P/'production/checkpoint.json');cp.update(stage=label,status='in-progress',jobs=[{'pid':child.pid,'command':command,'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'heavyJobs':1,'gpuJobs':0}],nextAction='Complete selected local outputs and review actual current text/pixels; no upload or next video.');wr(P/'production/checkpoint.json',cp)
 code=child.wait()
 if code:raise SystemExit(f'{label} failed with{code}; preserve artifacts and inspect before retry')
 print('Completed',label,flush=True)
cp=rd(P/'production/checkpoint.json');cp.update(stage='current-final-text-and-pixel-direct-review',jobs=[],nextAction='Directly compare complete final ASR and all current caption/scene boards; then collect four files, update worklist, selective Git, and local full-version user review.');wr(P/'production/checkpoint.json',cp)
print('Ready for direct current final review',flush=True)
