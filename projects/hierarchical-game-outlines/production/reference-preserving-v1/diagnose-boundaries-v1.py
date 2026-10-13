"""Bounded diagnosis after the completed V1 direct pixel review; no media mutation."""
from pathlib import Path
import json, hashlib, subprocess, datetime
from PIL import Image
P=Path(__file__).resolve().parent; ROOT=P.parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
write=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=P/'caption-boundary-diagnosis-v1.json'; assert not out.exists()
pixel=read(P/'final-pixel-plan-v1.json'); plan=read(P/'final-timeline-v1.json')
for row in pixel['samples']+pixel['boards']: assert sha(ROOT/row['path'])==row['sha256']
write(P/'final-direct-review-v1-held.json',dict(at=now(),captionedSha256=pixel['captionedSha256'],samplesReviewed=262,boardsReviewed=66,all48CuesAnd21CutsSampled=True,sampleAndBoardHashesVerified=True,normalPlayback={'tab':146,'startUTC':'2026-10-13T06:01:15.147Z','startSeconds':0.001238,'endUTC':'2026-10-13T06:06:00.877Z','endSeconds':285.666667,'rate':1,'muted':True,'ended':True},findings=['Sound parent/children annotations continue over Options at samples93-94; hide after the sound explanation ends and before returning to other menus.','Caption presence at sample13/f540 and sample32/f2700 needs exact alpha/timestamp diagnosis.'],approvedForPrivateUpload=False,humanFullListening=False,allIntermediateFramesReviewed=False))
frames=[119,120,393,394,539,540,541,671,949,950,951,2687,2688,2700,2707,2708,2709]
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
select='select='+ '+'.join(f'eq(n\\,{n})' for n in frames)+',crop=1920:180:0:900,format=rgba'
r=subprocess.run([FF,'-v','error','-nostdin','-threads','2','-i',str(P/'captions-alpha-local.mov'),'-vf',select,'-fps_mode','vfr','-f','rawvideo','-pix_fmt','rgba','pipe:1'],capture_output=True,creationflags=0x08000000)
assert r.returncode==0,r.stderr.decode(); size=1920*180*4; assert len(r.stdout)==size*len(frames)
images={0:P/'captions-local/blank.png',**{i+1:P/f'captions-local/{i+1:03d}.png' for i in range(len(plan['captionsKo']))}}
hashes={k:hashlib.sha256(Image.open(p).convert('RGBA').crop((0,900,1920,1080)).tobytes()).hexdigest() for k,p in images.items()}
rows=[]
for i,n in enumerate(frames):
 h=hashlib.sha256(r.stdout[i*size:(i+1)*size]).hexdigest(); actual=[k for k,v in hashes.items() if v==h]
 expected=next((j+1 for j,c in enumerate(plan['captionsKo']) if c['startFrame']<=n<c['endFrame']),0)
 rows.append(dict(frame=n,expectedCue=expected,actualMatchingCues=actual,exact=actual==[expected]))
write(out,dict(at=now(),alphaSha256=sha(P/'captions-alpha-local.mov'),rows=rows,allExact=all(x['exact'] for x in rows),scope='lossless alpha RGBA crop exact comparison; no media regenerated'))
print(json.dumps(rows,ensure_ascii=False))
