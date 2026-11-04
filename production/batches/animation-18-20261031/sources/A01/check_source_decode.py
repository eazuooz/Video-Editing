from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent
j=json.loads((P/'selected-footage.json').read_text(encoding='utf-8'))
out={'scope':'Full continuous CPU video decode of selected source files. No audio listening or final editorial QA claimed.','sources':{}}
for key,s in j['sources'].items():
 r=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-i',s['path'],'-map','0:v:0','-f','null','NUL'],capture_output=True,text=True)
 out['sources'][key]={'sha256':s['sha256'],'returnCode':r.returncode,'stderr':r.stderr.strip(),'status':'pass' if r.returncode==0 and not r.stderr.strip() else 'review-required'}
 print(key,out['sources'][key]['status'],flush=True)
(P/'continuous-decode-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
