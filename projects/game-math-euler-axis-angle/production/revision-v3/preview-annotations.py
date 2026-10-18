"""Short native-speed source previews with current editable editorial guides."""
from pathlib import Path
import importlib.util,json,subprocess,sys,hashlib
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v3';D=O/'annotation-preview';D.mkdir(exist_ok=True)
def load(name):
 spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
a=load('annotation-render')
p=json.loads((P/'sources/annotation-plan-v3.json').read_text(encoding='utf8'));sources=json.loads((P/'sources/cut-plan-v3.json').read_text(encoding='utf8'))['sources']
for w in p['windows']:
 if len(sys.argv)>1 and w['id'] not in sys.argv[1:]:continue
 src=sources[w['sourceId']];c=dict(id=w['id'],scene=w['scene'],sourceId=w['sourceId'],sourceStart=w['sourceIn'],frames=round((w['sourceOutExclusive']-w['sourceIn'])*60),credit=src['credit'])
 body,marks=a.cut_ass(c,p);ass=D/(w['id']+'.ass');ass.write_text(body,encoding='utf8');out=D/(w['id']+'.mp4');sig=hashlib.sha256(body.encode()).hexdigest();receipt=D/(w['id']+'.json')
 if out.exists() and receipt.exists() and json.loads(receipt.read_text())['assSha256']==sig:continue
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(c['sourceStart']),'-i',str(R/src['file']),'-an','-vf','fps=60,ass='+ass.relative_to(R).as_posix(),'-frames:v',str(c['frames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(out)]
 subprocess.run(cmd,check=True,cwd=R);receipt.write_text(json.dumps(dict(assSha256=sig,sourceStart=c['sourceStart'],frames=c['frames'])))
 print(w['id'],flush=True)
