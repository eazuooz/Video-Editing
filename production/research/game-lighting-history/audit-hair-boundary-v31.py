"""Decode exact presentation-frame samples outside captions; no new images."""
from pathlib import Path
from datetime import datetime, timezone
import json, subprocess, hashlib, numpy as np, psutil
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
b=read(P/'hair-chapter-review-build-v29.json'); plan=read(R/b['plan']['path'])
points=sorted({n for c in plan['cuts'][1:] for n in range(max(0,c['fromFrame']-2),min(8577,c['fromFrame']+3))})
frames={}; commands=[]
for ref in b['outputs']:
 assert hashlib.sha256((R/ref['path']).read_bytes()).hexdigest()==ref['sha256']
 expr='+'.join(f'eq(n\\,{f})' for f in points)
 cmd=[str(FF),'-v','error','-threads','2','-i',str(R/ref['path']),'-filter_threads','2','-vf',f'select={expr},crop=1920:800:0:0,scale=320:134','-fps_mode','passthrough','-frames:v',str(len(points)),'-pix_fmt','rgb24','-f','rawvideo','-threads','2','pipe:1']
 t=subprocess.run(cmd,capture_output=True,check=True)
 arr=np.frombuffer(t.stdout,np.uint8).reshape(len(points),134,320,3).astype(np.int16)
 frames['captioned' if 'captioned' in ref['path'] else 'clean']={n:v for n,v in zip(points,arr)};commands.append(cmd)
results=[]
for c in plan['cuts'][1:]:
 n=c['fromFrame']; rows=[]
 for capN in range(n-1,n+2):
  scores=[{'cleanFrame':cleanN,'meanAbsolutePixelDifference':float(np.abs(frames['captioned'][capN]-frames['clean'][cleanN]).mean())} for cleanN in range(n-2,n+3)]
  rows.append({'captionedFrame':capN,'matches':sorted(scores,key=lambda x:x['meanAbsolutePixelDifference'])})
 results.append({'cut':c['id'],'expectedFirstFrame':n,'comparison':rows})
dest=P/'hair-clean-captioned-boundary-audit-v31.json';assert not dest.exists()
dest.write_text(json.dumps({'auditedAt':datetime.now(timezone.utc).isoformat(),'worker':{'pid':psutil.Process().pid,'createTime':psutil.Process().create_time()},'scope':'Exact decoded presentation-frame audit excluding fixed caption area; numerical pixel matching aids direct review, not moving approval','build':b['plan'],'commands':commands,'results':results,'newImages':0,'allMovingPixelsReviewed':False},ensure_ascii=False,indent=2)+'\n','utf-8')
for x in results:print(json.dumps({'cut':x['cut'],'frame':x['expectedFirstFrame'],'matches':[{'cap':y['captionedFrame'],'best':y['matches'][0]} for y in x['comparison']]}),flush=True)
