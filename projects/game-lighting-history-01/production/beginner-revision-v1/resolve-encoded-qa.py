"""Resolve flagged reference timing/colour comparisons and verify changed GOPs only.

The original reference used fractional setpts in each source time base, which
truncated some exact ASS boundaries. Use an integer 1/60 time base. Reference
RGB conversion also explicitly matches the raw-YUV delivery's SMPTE170M decode
convention; this is a mapping check, not a claim of colourimetric calibration.
"""
import pathlib, json, hashlib, datetime, subprocess, shutil, concurrent.futures, math
from fractions import Fraction
import av
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
R=pathlib.Path(__file__).resolve().parents[4]
O=R/'projects/game-lighting-history-01/production/local/continuity-v2'
F=O/'pair-exact-v2'; D=F/'focused-review'; FF=shutil.which('ffmpeg')
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 plan=rd(O/'plan.json'); old=rd(F/'frame-mapping-review.json'); actual=rd(F/'encoded-review/execution.json')
 D.mkdir(exist_ok=True); flagged={r['frame'] for r in old['flags']}
 changed=lambda f:40594<=f<41643 or f>=142538
 rows=[r for r in actual['images'] if r['frame'] in flagged or changed(r['frame'])]
 state=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='running',
  originalEvidence='frame-mapping-review.json',originalFlags=len(flagged),
  originalSourceSha256=actual['sourceSha256'],sourceSha256=sha(F/'captioned-video.mp4'),
  reuseEvidence=['weight-note-removal.json','ending-caption-safe-repair.json'],
  retainedEvidenceReason='Packets and exact PTS outside the two changed GOP ranges are byte-identical. Existing direct visual review and unflagged comparisons are retained.',
  referenceCorrection='settb=1/60,setpts=N+globalFrame fixes truncated ASS boundaries; explicit SMPTE170M RGB decode matches the delivered raw-YUV stream. Original reference and metrics preserved.',
  colourScope='Mapping and visible appearance only; not a calibrated BT709 mastering claim.',rows=[],manualReviewComplete=False)
 wr(D/'resolution.json',state)
 ass=(O/'captions.ko.ass').relative_to(R).as_posix();fonts='projects/game-lighting-history-01/production/local/final-edit-v1/fonts'
 def check(row):
  fr=row['frame'];n=next(n for n in plan['nodes'] if n['startFrame']<=fr<n['endFrame']);sf=n['framedStartFrame']+fr-n['startFrame']
  ref=D/f'reference-{fr:06}.png';out=R/row['path']
  if changed(fr):
   out=D/f'actual-{fr:06}.png'
   with av.open(str(F/'captioned-video.mp4')) as c:
    s=c.streams.video[0];s.codec_context.thread_count=1;c.seek(fr*1500,stream=s)
    for v in c.decode(s):
     if v.pts*s.time_base<Fraction(fr,60):continue
     assert v.pts*s.time_base==Fraction(fr,60)
     v.to_image().save(out);break
  vf=f"trim=start_frame={sf}:end_frame={sf+1},settb=1/60,setpts=N+{fr},setparams=colorspace=smpte170m,ass='{ass}':fontsdir='{fonts}',format=rgb24"
  subprocess.run([FF,'-v','error','-y','-threads','1','-i',str(R/n['framedPath']),'-vf',vf,'-filter_threads','1','-frames:v','1','-fps_mode','passthrough',str(ref)],cwd=R,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  a=Image.open(ref).convert('RGB');b=Image.open(out).convert('RGB');draw=ImageDraw.Draw(a)
  if 120<=fr<438:draw.rectangle((800,819,1119,863),fill='black')
  if 40805<=fr<41643:draw.rectangle((600,850,1319,899),fill='black')
  if 142577<=fr<143201 or 143766<=fr<144448:draw.rectangle((600,858,1319,896),fill='black')
  a.save(ref)
  ar=np.asarray(a,dtype=np.float32);br=np.asarray(b,dtype=np.float32);delta=np.abs(ar-br)
  smalla=np.asarray(a.filter(ImageFilter.GaussianBlur(1)).resize((640,360)),dtype=np.float32);smallb=np.asarray(b.filter(ImageFilter.GaussianBlur(1)).resize((640,360)),dtype=np.float32)
  mask=(ar[875:1060].max(axis=2)-ar[875:1060].min(axis=2)<20)&(ar[875:1060].max(axis=2)>180)
  metrics=dict(mae=float(delta.mean()),blurredDownscaleMae=float(np.abs(smalla-smallb).mean()),captionRoiMae=float(delta[875:1060].mean()),brightCaptionPixelMae=float(delta[875:1060][mask].mean()) if mask.any() else 0)
  fail=metrics['mae']>5 or metrics['blurredDownscaleMae']>3 or metrics['captionRoiMae']>5 or metrics['brightCaptionPixelMae']>8
  return dict(frame=fr,node=n['id'],priorFlag=fr in flagged,changedGop=changed(fr),actual=out.relative_to(R).as_posix(),reference=ref.relative_to(R).as_posix(),**metrics,flagged=fail)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for r in pool.map(check,rows):
   state['rows'].append(r)
   if len(state['rows'])%20==0:wr(D/'resolution.json',state);print('Focused QA',len(state['rows']),'/',len(rows),flush=True)
 state.update(status='complete-awaiting-direct-review',flags=[r for r in state['rows'] if r['flagged']],endedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());wr(D/'resolution.json',state)
 print(json.dumps(dict(checked=len(rows),remainingFlags=state['flags']),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
