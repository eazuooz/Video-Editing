"""Exact final-frame review evidence, including every overlapping caption cue.
Run only after the parent grants the QA decode slot and both final masters pass
the full structural verifier. Outputs are new local media; no approval inferred.
"""
from pathlib import Path
import argparse,json,math,subprocess
from PIL import Image,ImageDraw,ImageFont
import audio_pipeline as a
H=Path(__file__).resolve().parent
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--plan',default=str(H/'edit-plan.json'));ap.add_argument('--revision',default='v1');args=ap.parse_args()
 a.require_authorized('exact-final-frame-review')
 plan=a.read(args.plan);out=a.repo_path(plan['outputDir']);verification=a.read(out/'structural-verification.json')
 if verification['status']!='pass':raise ValueError('Full structural verification is required')
 movie=out/(plan['outputStem']+'-captioned.mp4');caption=a.read(out/'captions.json')['cues']
 sourceHash=a.sha(movie);root=out/'qa'/args.revision
 if root.exists():raise FileExistsError('Preserve earlier QA evidence; use a fresh revision')
 root.mkdir(parents=True);frames=root/'frames';frames.mkdir()
 byCut={};allFrames={0,119,120,plan['totalFrames']-601,plan['totalFrames']-600,plan['totalFrames']-1}
 cueConfig={x['cutId']:x for x in a.read(H/'unity-cues.json')['cuts']}
 for cut in plan['cuts']:
  start,end=cut['startFrame'],cut['endFrame'];n=end-start
  keep={start,start+n//4,start+n//2,start+3*n//4,end-1}
  overlapping=[]
  for cue in caption:
   begin,finish=round(cue['start']*60),round(cue['end']*60)
   if begin<end and finish>start:
    overlapping.append(cue['cue'])
    for f in [begin,begin+1,(max(start,begin)+min(end,finish))//2,finish-1]:
     if start<=f<end:keep.add(f)
  for cue in cueConfig.get(cut['id'],{}).get('cues',[]):
   for t in [cue['start'],cue['end']]:
    f=start+round(t*60)
    for g in [f-1,f,f+1]:
     if start<=g<end:keep.add(g)
  for mark in cut.get('marks',[]):
   for f in range(math.ceil(mark['t0']*60),math.ceil(mark['t1']*60),15):
    if start<=start+f<end:keep.add(start+f)
   for key in mark.get('keyframes',[]):
    f=start+round(key['t']*60)
    for g in [f-1,f,f+1]:
     if start<=g<end:keep.add(g)
  for f in [start-1,end]:
   if 0<=f<plan['totalFrames']:keep.add(f)
  byCut[cut['id']]={'frames':sorted(keep),'overlappingCaptionCues':overlapping,'sourceKind':cut['kind'],'variant':cut.get('variant')};allFrames.update(keep)
 ordered=sorted(allFrames)
 # A flat sum of >1,000 frame tests exceeds FFmpeg's expression recursion.
 # Balance the exact same membership tests; no sample frames are dropped.
 def balanced_sum(terms):
  if len(terms)==1:return terms[0]
  midpoint=len(terms)//2
  return '('+balanced_sum(terms[:midpoint])+'+'+balanced_sum(terms[midpoint:])+')'
 expr=balanced_sum([f'eq(n\\,{f})' for f in ordered])
 command=[a.tool('ffmpeg'),'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(movie),'-vf','select='+expr,'-fps_mode','vfr','-q:v','2','-n',str(frames/'%05d.jpg')]
 result=subprocess.run(command,capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 (root/'decode.log').write_bytes(result.stderr)
 if result.returncode:raise RuntimeError(result.stderr.decode('utf8','replace')[-3000:])
 files=sorted(frames.glob('*.jpg'))
 if len(files)!=len(ordered):raise ValueError('Exact selected frame count differs')
 lookup={frame:file for frame,file in zip(ordered,files)};font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
 for cid,row in byCut.items():
  row['mobileSheets']=[];values=row['frames']
  for batch in range(0,len(values),10):
   part=values[batch:batch+10];sheet=Image.new('RGB',(750,math.ceil(len(part)/2)*240),'#151515');draw=ImageDraw.Draw(sheet)
   for j,f in enumerate(part):
    x,y=(j%2)*375,(j//2)*240
    im=Image.open(lookup[f]);assert im.size==(1920,1080)
    sheet.paste(im.resize((375,211),Image.Resampling.LANCZOS),(x,y+26));draw.text((x+5,y+3),f'{cid} | frame {f} | {f/60:.3f}s',font=font,fill='white')
   dest=root/f'{cid}-375-{batch//10+1:02d}.jpg';sheet.save(dest,quality=94);row['mobileSheets'].append(a.relative(dest))
  row['nativeFrames']=[{'frame':f,'path':a.relative(lookup[f])} for f in values]
 a.save(root/'evidence.json',{'status':'extracted-not-viewed','captionedMp4':a.artifact(movie),'initialCaptionedSha256':sourceHash,'unchangedAfterDecode':a.sha(movie)==sourceHash,'frameSelection':'exact decoded n, no approximate seek','resolution':[1920,1080],'mobileWidth':375,'frameCount':len(ordered),'cutCount':len(byCut),'allCaptionCuesCovered':sorted(set(c for row in byCut.values() for c in row['overlappingCaptionCues']))==[c['cue'] for c in caption],'cuts':byCut,'humanWholeReview':'pending','agentPixelReview':'pending direct viewing of generated evidence'})
 print(f'{len(ordered)} exact frames / {len(byCut)} cuts extracted; direct visual review still required')
if __name__=='__main__':main()
