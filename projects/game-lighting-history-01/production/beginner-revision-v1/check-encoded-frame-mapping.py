"""Check every requested cut/caption frame against its source plus current ASS.

This is an encoding/mapping check, not a substitute for visual design review.
"""
import pathlib,json,hashlib,datetime,subprocess,shutil,collections,sys,math
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/continuity-v2';D=O/'pair/reference-frames';FF=shutil.which('ffmpeg')
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 plan=rd(O/'plan.json');request=rd(O/'encoded-review-request.json');assert request['planSha256']==sha(O/'plan.json') and request['assSha256']==sha(O/'captions.ko.ass')
 if '--prepare' in sys.argv:
  if '--resume' in sys.argv:
   state=rd(D/'execution.json');assert state['status']=='running' and state['planSha256']==request['planSha256'] and state['assSha256']==request['assSha256']
  else:
   assert not D.exists();D.mkdir(parents=True)
   state=dict(startedAt=now(),status='running',planSha256=request['planSha256'],assSha256=request['assSha256'],nodes=[],images=[])
  ass=(O/'captions.ko.ass').relative_to(R).as_posix();fonts=(P/'production/local/final-edit-v1/fonts').relative_to(R).as_posix()
  completed=len(state['nodes'])
  for nodeIndex,n in enumerate(plan['nodes']):
   if nodeIndex<completed:continue
   # Retained split nodes may share a logical id; the global interval is unique.
   rows=[(i,row) for i,row in enumerate(request['points'],1) if n['startFrame']<=row['frame']<n['endFrame']]
   folder=D/f"{n['startFrame']:06d}-{n['id']}";reuse=False
   prior=D/n['id']
   if nodeIndex==completed and '--resume' in sys.argv and prior.exists() and len(list(prior.glob('*.png')))==len(rows):folder=prior;reuse=True
   if not reuse:folder.mkdir()
   start=n['framedStartFrame'];sel='+'.join(f"eq(n,{r['frame']-n['startFrame']})" for i,r in rows)
   vf=f"trim=start_frame={start}:end_frame={start+n['frames']},setpts=(N+{n['startFrame']})/(60*TB),ass='{ass}':fontsdir='{fonts}',select='{sel}',setsar=1,format=rgb24"
   cmd=[FF,'-hide_banner','-v','error','-nostdin','-n','-threads','2','-i',str(R/n['framedPath']),'-vf',vf,'-filter_threads','2','-fps_mode','passthrough','-an','-frames:v',str(len(rows)),str(folder/'%04d.png')]
   if not reuse:
    with (folder/'extract.log').open('w') as log:subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
   for j,(i,row) in enumerate(rows,1):
    img=folder/f'{j:04}.png';assert img.exists();state['images'].append(dict(index=i,frame=row['frame'],path=img.relative_to(R).as_posix()))
   state['nodes'].append(n['id']);wr(D/'execution.json',state)
  state.update(status='complete',endedAt=now());wr(D/'execution.json',state);print('Prepared',len(state['images']),'independent source+ASS frame references');return
 ref=rd(D/'execution.json');actual=rd(O/'pair-exact-v2/encoded-review/execution.json');assert ref['status']=='complete' and actual['status']=='complete-awaiting-direct-review'
 references={r['index']:r for r in ref['images']};rows=[]
 for i,r in enumerate(actual['images'],1):
  q=references[i];assert q['frame']==r['frame']
  with Image.open(R/q['path']) as a,Image.open(R/r['path']) as b:
   a=a.convert('RGB');b=b.convert('RGB')
   if 120<=r['frame']<438:ImageDraw.Draw(a).rectangle((800,819,1119,863),fill='black')
   if 142577<=r['frame']<143201 or 143766<=r['frame']<144448:ImageDraw.Draw(a).rectangle((600,858,1319,899),fill='black')
   assert a.size==b.size==(1920,1080)
   ar=np.asarray(a,dtype=np.float32);br=np.asarray(b,dtype=np.float32);delta=np.abs(ar-br)
   smalla=np.asarray(a.filter(ImageFilter.GaussianBlur(1.0)).resize((640,360)),dtype=np.float32);smallb=np.asarray(b.filter(ImageFilter.GaussianBlur(1.0)).resize((640,360)),dtype=np.float32)
   mae=float(delta.mean());mse=float(((ar-br)**2).mean());structural=float(np.abs(smalla-smallb).mean());caption=float(delta[875:1060].mean());mask=(ar[875:1060].max(axis=2)-ar[875:1060].min(axis=2)<20)&(ar[875:1060].max(axis=2)>180);captionBright=float(delta[875:1060][mask].mean()) if mask.any() else 0
   row=dict(index=i,frame=r['frame'],node=r['node'],cueIds=r['cueIds'],mae=mae,psnr=10*math.log10(255**2/max(mse,1e-10)),blurredDownscaleMae=structural,captionRoiMae=caption,brightCaptionPixelMae=captionBright)
   row['flagged']=mae>5 or structural>3 or caption>5 or captionBright>8;rows.append(row)
 result=dict(checkedAt=now(),sourceSha256=actual['sourceSha256'],planSha256=request['planSha256'],assSha256=request['assSha256'],method='Every requested encoded frame is compared with independently decoded exact source frame plus identical timed ASS. Metrics flag mapping/caption failures; manual design and mobile review remains separate.',frames=len(rows),cutCount=len(plan['nodes']),cueCount=request['cueCount'],rows=rows,flags=[r for r in rows if r['flagged']],manualDesignReview=False)
 wr(O/'pair-exact-v2/frame-mapping-review.json',result);print(json.dumps(dict(frames=len(rows),flags=result['flags'],maximumMae=max(r['mae'] for r in rows))))
if __name__=='__main__':main()
