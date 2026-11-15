"""Finish axis labels and fallback glyphs on this job's unreviewed intermediates."""
import sys,os,copy,shutil,psutil,io
from PIL import Image
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import render
def frame(path,t):
 raw=render.ff(['-threads','2','-ss',t,'-i',path,'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture=True)
 return Image.open(io.BytesIO(raw)).convert('RGB')
def repair(eid):
 receipt=HERE/'deliveries'/f'{eid}.json';backup=HERE/f'{eid}-before-final-repair.json'
 if receipt.exists() and render.read(receipt).get('correctionsComplete'):return
 if not backup.exists():shutil.copy2(receipt,backup)
 previous=render.read(backup);row=copy.deepcopy(next(r for r in render.read(HERE/'plan.json')['episodes'] if r['id']==eid));row['sources']=previous['files'];row['onlyDirection']=True;e=render.base.EPISODES[eid];p=render.base.work(e)
 intervals=[]
 if eid in ('M25','M26'):
  intervals=[(t['start'],t['end']) for t in render.base.tracks(e) if t['mode']=='motion' and (t['lesson']['motion'].get('positiveYIsDown') if eid=='M25' else t['asset']=='kart' and t['lesson']['motion']['parameters'].get('kind')==2)]
 changes=intervals+([(row['start'],row['end'])] if eid in ('M25','M33') else [])+([(row['recapStart'],row['recapEnd'])] if eid=='M28' else [])
 board=render.base.Board();note='차체 자세 유지 · 아래쪽 +y · 이동 방향은 v' if eid=='M25' else '차체 자세 유지 · v는 궤도의 진행 방향'
 for a,z in intervals:
  board.rectangle(1190,178,715,50,a,z);board.text(1200,181,note,a,z,render.base.TEAL,29,width=690)
 board.write(p/'axis-note.ass');render.direction_ranges=lambda _:changes
 key=p/'keyframes.json';saved=p/'keyframes-before-final-repair.json'
 if key.exists():
  if not saved.exists():key.replace(saved)
  else:key.unlink()
 dest=Path(previous['files']['clean']['path']).parent/'final-repair-staging';dest.mkdir(exist_ok=True);render.destination=lambda _:dest
 def encode(row,s,i):
  a=s['start']/60;z=s['end']/60;frames=s['end']-s['start'];files=[p/f'correction-{i:02}.{kind}.mp4' for kind in ('clean','captioned')]
  graph=f'[0:v]setsar=1,fps=60,setpts=PTS+{a}/TB,ass=axis-note.ass[correct0];';current='correct0';inputs=[];n=1;counter=0
  opening=eid in ('M25','M33') and a<row['end'] and z>row['start'];recap=eid=='M28' and a<row['recapEnd'] and z>row['recapStart']
  if opening or recap:
   x,y,w,h=(1030,300,820,462) if opening else (1030,310,820,388)
   graph+=f'[{current}]split=2[correctbase][insetsrc];[insetsrc]crop={w}:{h}:{x}:{y}[existinginset];';current='correctbase'
   def overlay(file,start,stop):
    nonlocal n,graph,current,counter
    if stop<=start:return
    inputs.extend(['-i',p/file]);target=f'correct{counter+1}';counter+=1;graph+=f"[{current}][{n}:v]overlay=0:0:enable='gte(t,{start})*lt(t,{stop})'[{target}];";n+=1;current=target
   if opening:
    start,stop=row['start'],row['end'];overlay('overview.png',start,stop);overlay('roadmap.png',row['roadmap'],stop)
   else:
    start,stop=row['recapStart'],row['recapEnd'];times=[start]+[max(start,x['at']) for x in row['recap']]+[stop]
    for k,(aa,zz) in enumerate(zip(times,times[1:])):overlay(f'recap-{k}.png',aa,zz)
   # Keep the exact previously verified game/model window. Do not recursively
   # insert an already designed recap page into another recap page.
   graph+=f"[{current}][existinginset]overlay={x}:{y}:enable='gte(t,{start})*lt(t,{stop})'[restoredinset];";current='restoredinset'
  graph+=f'[{current}]setpts=PTS-{a}/TB,split=2[vout][capbase];[capbase]setpts=PTS+{a}/TB,ass=captions.ko.ass,setpts=PTS-{a}/TB[capout]'
  (p/'correction.ffgraph').write_text(graph,encoding='utf8');render.old.prior.prepare_captions(e,p)
  codec=['-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-bf','2','-g','120','-sc_threshold','0','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
  args=['-threads','2','-ss',a,'-i',row['sources']['clean']['path'],*inputs,'-filter_complex_threads','2','-/filter_complex','correction.ffgraph']
  for label,f in zip(('[vout]','[capout]'),files):args+=['-map',label,'-an','-frames:v',frames,*codec,f]
  render.ff(args,p,'correction-'+str(i));return files
 render.encode_span=encode
 stagedReady=receipt.exists() and Path(render.read(receipt)['files']['clean']['path']).parent==dest and all(render.sha(x['path'])==x['sha256'] for x in render.read(receipt)['files'].values())
 if not stagedReady:
  if receipt.exists():receipt.unlink() # Own pre-review receipt is backed up.
  render.episode(row)
 updated=render.read(receipt);proof=[]
 import numpy as np
 for a,z in intervals[:2]:
  t=min(z-.2,a+1.5);before=np.asarray(frame(previous['files']['clean']['path'],t)).astype(float);after=np.asarray(frame(updated['files']['clean']['path'],t)).astype(float);mask=np.ones((1080,1920),bool);mask[175:235,1185:1910]=False;mae=float(np.abs(before-after)[mask].mean());assert mae<3,('Unrelated picture changed',eid,t,mae);proof.append(dict(time=t,meanErrorOutsideChangedLabel=mae))
 approved=[render.ROOT/'output/game-math-direction-overview-20261115/local-masters',Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingOutputs/game-math-direction-overview-20261115']
 for kind,new in updated['files'].items():
  original=Path(previous['files'][kind]['path']);staged=Path(new['path']);assert any(original.resolve().is_relative_to(r.resolve()) for r in approved);assert render.sha(original)==previous['files'][kind]['sha256'];assert render.sha(staged)==new['sha256'];os.replace(staged,original);new['path']=str(original)
 updated.update(correctionsComplete=True,axisLabelCorrection=eid in ('M25','M26'),verticalAxisLabelCorrection=eid=='M25',projectileAxisLabelCorrection=eid=='M26',bookendGlyphCorrection=eid in ('M25','M28','M33'),precedingProof=str(backup),unchangedPictureChecks=proof,intermediateReplacement='Only this job’s unreviewed first pass, after successful new QA. Accepted baseline masters are untouched.',reviewPage=str(Path(updated['files']['clean']['path']).parent/'index.html'));render.save(receipt,updated)
 print(eid+' final correction assembled; exact voice/subtitles, FHD60 and preserved body payloads verified',flush=True)
def main():
 for process in psutil.process_iter(['pid','name','cmdline']):
  if process.pid==os.getpid():continue
  if (process.info['name'] or '').lower().startswith('python') and any(x.replace('\\','/').endswith('revision-direction-overview-20261115/render.py') for x in process.info['cmdline'] or []):raise RuntimeError('Wait for the existing all-13 finite renderer. Do not duplicate or terminate it.')
 for eid in ('M25','M26','M28','M33'):repair(eid)
if __name__=='__main__':main()
