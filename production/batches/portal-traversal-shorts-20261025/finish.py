from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug,mode=sys.argv[1:];p=R/'projects'/slug
d=json.loads((p/f'production/local/motion-{mode}-execution.json').read_text());assert d['done'] and d['result']==0 and not d['errors']
visual=R/f'shared/output/motion-canvas/{slug}-{mode}.mp4'
for action in ['pair','integrity','qa']:
 cmd=[sys.executable,'-X','utf8',str(p/'production/finish-video.py'),action]
 if action=='pair':cmd+=['--visual',str(visual)]
 with (p/f'production/local/finish-{mode}-{action}.log').open('w',encoding='utf8') as f:subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
 print('DONE',slug,action,flush=True)
subprocess.run([sys.executable,'-X','utf8',str(B/'package.py'),slug],check=True,cwd=R)
