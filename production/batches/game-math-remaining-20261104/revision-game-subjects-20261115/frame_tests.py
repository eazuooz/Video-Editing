"""Bounded CPU-only single-frame layout check; no production GPU encode."""
import sys,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
from subject_revision import *

def render(eid,sid,time=None):
 e=EPISODES[eid];s=next(s for s in e['scenes'] if s['scene']==sid);time=time or (s['start']+s['end'])/2
 assert s['start']<=time<s['end'],('Requested frame is outside the named scene',eid,sid,time)
 p=work(e);origin=time-.25;end=time+.05;inputs,g=graph(e,origin,end);prior.prepare_captions(e,p)
 shutil.copy2(ROOT/'projects'/e['slug']/'production/local/teaching-sync-v2/workings.ass',p/'workings.ass')
 g=g.replace('[vout]','[unsub]')+f';[unsub]setpts=PTS+{origin}/TB,ass=captions.ko.ass,setpts=PTS-STARTPTS,select=\'gte(t,0.249)\'[vout]'
 out=HERE/'local/tests-v13';out.mkdir(exist_ok=True);target=out/f'{eid}-{sid}-{time:.2f}.png'
 if not target.exists():
  r=subprocess.run([str(FF),'-hide_banner','-nostdin','-n','-threads','1','-ss',str(origin),'-i',str(e['baselineOutputs']['clean']),*map(str,inputs),'-filter_complex_threads','1','-filter_complex',g,'-map','[vout]','-frames:v','1','-threads','1',str(target)],cwd=p,capture_output=True)
  if r.returncode:raise RuntimeError(r.stderr.decode('utf8',errors='replace')[-3000:])
 return target

if __name__=='__main__':
 args=sys.argv[1:]
 for arg in args:
  fields=arg.split(':');print(render(fields[0],fields[1],float(fields[2]) if len(fields)>2 else None),flush=True)
