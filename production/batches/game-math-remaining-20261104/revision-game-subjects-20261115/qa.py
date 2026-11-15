"""Encoded evidence, not automatic semantic approval or user viewing."""
import json,subprocess,uuid,os,math
from PIL import Image,ImageDraw
from subject_revision import *

def technical(e):
 p=work(e);enc=read(p/'encoded.json');expected=enc['frames'];source=latest(e);audio=prior.packet_hash(source,'a');findings=[]
 for kind in ('clean','captioned'):
  f=Path(enc['files'][kind]['path']);assert sha(f)==enc['files'][kind]['sha256']
  prior.check_stream(f,expected)
  # One complete decode yields both an actual frame count and display timestamps.
  raw=subprocess.check_output([str(FF.with_name('ffprobe.exe')),'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(f)],creationflags=prior.CREATE)
  frames=json.loads(raw)['frames'];assert len(frames)==expected,(kind,len(frames),expected)
  pts=[float(x['best_effort_timestamp_time']) for x in frames]
  error=max(abs(t-i/60) for i,t in enumerate(pts));assert error<.00004,(kind,error)
  assert prior.packet_hash(f,'a')==audio,(kind,'audio changed')
  findings.append(dict(kind=kind,frames=len(frames),fullDecode=True,maximumPresentationTimestampError=error,audioBitstreamHash=audio))
 for lang in ('ko','en'):assert sha(enc['files'][lang]['path'])==sha(latest(e,lang))
 assert sha(p/'workings.ass')==sha(ROOT/'projects'/e['slug']/'production/local/teaching-sync-v2/workings.ass')
 result=dict(episode=e['id'],status='technical-pass-picture-review-pending',fullDecode=findings,unchangedAudio=True,unchangedKoEnSrt=True,unchangedMathOverlay=True,humanReviewed=False,actualPictureReview=False)
 save(p/'technical-qa.json',result)
 return result

def pictures(e):
 p=work(e);enc=read(p/'encoded.json');movie=Path(enc['files']['captioned']['path']);plan=read(p/'subject-plan.json');out=p/'qa';out.mkdir(exist_ok=True)
 previous=read(p/'picture-evidence.json') if (p/'picture-evidence.json').exists() else {}
 assert not any(out.glob('*.jpg')) or previous.get('movieSha256')==sha(movie),'Archive picture evidence from a different encode before extracting new QA frames'
 # Verify realized locations at multiple moments, not just a successful render.
 sceneids=sorted(set(row['scene'] for row in plan['evidence']));rows=[]
 if e['id']=='M33' and '029' not in sceneids:sceneids.append('029')
 for sid in sceneids:
  s=next(s for s in e['scenes'] if s['scene']==sid)
  for frac in (0,.15,.5,.85):
   t=s['start']+(s['end']-s['start'])*frac;target=out/f'{sid}-{frac:.2f}.jpg'
   frame=round(t*60);prefix=max(0,frame//60-1);local=frame-prefix*60
   if not target.exists():subprocess.run([str(FF),'-v','error','-nostdin','-n','-threads','1','-ss',str(prefix),'-i',str(movie),'-frames:v','1','-vf',f'select=eq(n\\,{local}),scale=480:270','-q:v','2','-threads','1',str(target)],check=True,creationflags=prior.CREATE)
   rows.append(dict(scene=sid,time=frame/60,frame=frame,file=str(target),fraction=frac))
 boards=[]
 for first in range(0,len(rows),18):
  group=rows[first:first+18];im=Image.new('RGB',(1440,294*math.ceil(len(group)/3)),'black');d=ImageDraw.Draw(im)
  for j,row in enumerate(group):
   x=j%3*480;y=j//3*294;im.paste(Image.open(row['file']),(x,y));d.text((x+5,y+274),f'{e["id"]}/{row["scene"]} {row["fraction"]:.0%} @ {row["time"]:.2f}',fill='white')
  target=out/f'board-{first//18+1:02}.jpg';im.save(target,quality=95);boards.append(str(target))
 save(p/'picture-evidence.json',dict(movieSha256=sha(movie),method='Exact 60fps indexed first frame and 15/50/85 percent of every revised scene; full-frame and moving-source checks recorded separately.',rows=rows,boards=boards,actuallyInspected=False))
 return boards

def record(e,notes):
 p=work(e);tech=read(p/'technical-qa.json');pic=read(p/'picture-evidence.json');assert tech['status'].startswith('technical-pass')
 for f in pic['boards']:assert Path(f).exists()
 assert pic['movieSha256']==read(p/'encoded.json')['files']['captioned']['sha256']
 pic.update(actuallyInspected=True,actualHumanViewing=False,reviewNotes=notes);save(p/'picture-evidence.json',pic)
 artifacts={str(f.relative_to(p)):sha(f) for f in p.iterdir() if f.is_file() and (f.suffix in ('.ass','.ffgraph') or f.name.startswith('commands-') or f.name in ('jump-commands.txt','subject-plan.json'))}
 save(p/'render-input-evidence.json',dict(episode=e['id'],inputHashes=artifacts,assetManifestSha256=sha(HERE/'assets.json'),movieSha256=pic['movieSha256']))
 save(p/'qa.json',dict(episode=e['id'],status='pass',technical=tech,actualPictureReview=True,pictureBoards=pic['boards'],pictureEvidenceSha256=sha(p/'picture-evidence.json'),renderInputEvidenceSha256=sha(p/'render-input-evidence.json'),reviewNotes=notes,scope='Revised picture locations, source/model correspondence, captions, motion samples and joins; unchanged audio evidence reused by exact bitstream hash. This is internal sampled visual QA, not a claim of uninterrupted full human viewing.',humanReviewed=False,finalReviewReady=True))
 enc=read(p/'encoded.json');enc.update(status='internal-QA-pass-user-review-pending',finalReviewReady=True,humanReviewed=False);save(p/'encoded.json',enc)
 save(p/'worker.json',dict(status='local-user-review-pending',episode=e['id'],finalReviewReady=True,humanReviewed=False))
 pending_path=HERE/'pending-corrections.json'
 if pending_path.exists():
  pending=read(pending_path)
  if e['id'] in pending.get('episodes',{}):
   pending['episodes'][e['id']].update(status='resolved',reviewedCaptionedSha256=enc['files']['captioned']['sha256'],qaEvidence=str(p/'qa.json'),humanReviewed=False);save(pending_path,pending)

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('episode');ap.add_argument('--technical',action='store_true');ap.add_argument('--pictures',action='store_true');ap.add_argument('--record',type=str);a=ap.parse_args();e=EPISODES[a.episode]
 if a.technical:technical(e)
 if a.pictures:
  for x in pictures(e):print(x,flush=True)
 if a.record:record(e,a.record)
