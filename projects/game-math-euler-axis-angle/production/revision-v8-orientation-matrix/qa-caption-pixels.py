"""Finite current-master caption and transition image evidence; never human approval.

--plan-only is safe before source alignment and creates no media.
--build-plan binds all475 caption midpoints, paragraph transitions, gameplay
cuts, manual source anchors and actual planned guide-hide boundaries to60fps.
--extract --max-new N selects at most N missing FHD frames in one CPU decode.
Use --max-new all only inside an explicitly authorized finite CPU handoff.
--contacts reuses existing FHD/mobile images and never decodes the movie.

Root qa.py's76 representative images are reused when master SHA and exact frame
match. This samples encoded pixels; it does not prove continuous motion/audio.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,subprocess
from PIL import Image,ImageDraw,ImageFont

H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v8_caption_pixel_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
D=c.O/'qa';MASTER=c.O/'orientation-matrix.captioned.mp4';PLAN=D/'caption-pixels-plan.json'
REVIEW=D/'caption-pixels-review.json'

def evidence(file):return dict(file=c.rel(file),sha256=c.sha(file))
def required():
 return [H/'timeline.json',H/'edit-plan.json',c.O/'captions/captions.json',H/'annotations-manifest.json',MASTER,D/'orientation-matrix.captioned-decode.json']
def ready():return all(x.exists() for x in required())
def plan_only():
 c.authorized();p=c.read(H/'caption-plan.json');assert len(p['cues'])==475
 result=dict(schemaVersion=1,revision='orientation-matrix-v8',status='sampler-design-ready;actual-clock-and-current-master-required',
   implementation=evidence(Path(__file__)),captionPlan=evidence(H/'caption-plan.json'),intendedCaptionCueCount=475,
   sampling=['Every caption: one exact active midpoint frame',
     'Every paragraph start/end: preceding/current/following frame, deduplicated',
     'Gameplay pane source cuts: two frames before/after',
     'Verified gameplay source anchors: one frame before/after',
     'Planned guide visible/hidden transitions: two frames before/after',
     'Exactly two endcap proofs: intro frame60 and member start+300'],
   reusePolicy='Root qa/visual-proof.json and own prior samples only with exact current master SHA and same frame. Do not re-extract such frames.',
   extraction=dict(decoder='ffmpeg software',decoderThreads=1,filterThreads=1,concurrency=1,maxNewFrames='required explicit bound',resolution=[1920,1080]),
   mobile=[375,211],fixedCaptionCenter=[960,970],mediaCreated=False,
   waitingFor=[c.rel(x) for x in required() if not x.exists()],
   generatedPixelsAreNotApproval=True,actualPixelReview='pending',continuousMotionReview='pending',wholeListening='pending')
 c.save(D/'caption-pixels-preflight.json',result)
 if not PLAN.exists():c.save(PLAN,result)
 print(json.dumps(dict(status=result['status'],captionCues=475,missingInputs=len(result['waitingFor']),mediaCreated=False)))

def root_reuse(master_sha):
 p=D/'visual-proof.json';out={}
 if not p.exists():return out,None
 report=c.read(p)
 if report.get('masterSha256')!=master_sha:return out,None
 for row in report['rows']:
  if row.get('verifiedSourcePts')!=row['frame']*1000 or row.get('sourceTimeBase')!='1/60000':continue
  if not row.get('exactFrameEvidence') or not (c.R/row['exactFrameEvidence']).exists():continue
  exact=c.read(c.R/row['exactFrameEvidence'])
  if exact.get('masterSha256')!=master_sha or exact.get('sourceFrame')!=row['frame'] or exact.get('verifiedSourcePts')!=row['frame']*1000 or exact.get('sha256')!=row['sha256']:continue
  file=c.R/row['file']
  if not file.exists() or c.sha(file)!=row['sha256']:continue
  with Image.open(file)as im:
   assert im.size==(1920,1080),('Root representative must be current FHD pixels',file,im.size)
  reuse=dict(file=row['file'],sha256=row['sha256'],origin='root qa.py representative',rootId=row['id'])
  if row.get('mobile') and (c.R/row['mobile']).exists():
   with Image.open(c.R/row['mobile'])as im:assert im.size==(375,211)
   reuse.update(mobile=row['mobile'],mobileSha256=c.sha(c.R/row['mobile']))
  out.setdefault(row['frame'],reuse)
 return out,evidence(p)

def build_plan():
 c.authorized();assert ready(),'Use --plan-only until actual timed captions, edit-plan, annotations and master exist'
 timeline=c.read(H/'timeline.json');edit=c.read(H/'edit-plan.json');caps=c.read(c.O/'captions/captions.json')
 assert edit['timelineSha256']==c.sha(H/'timeline.json')
 assert caps['inputs']['timeline']['sha256']==c.sha(H/'timeline.json')
 anno=c.read(H/'annotations-manifest.json');assert anno['inputs']['editPlan']['sha256']==c.sha(H/'edit-plan.json')
 assert len(caps['cues'])==475 and len(edit['paragraphs'])==76
 master_sha=c.sha(MASTER);total=timeline['totalFrames'];items={}
 clockproof=D/'orientation-matrix.captioned-decode.json';decoded=c.read(clockproof)
 assert decoded['sha256']==master_sha and decoded['frames']==total and decoded['exactFrameClock'] and decoded['completeSoftwareDecode'],'Current master exact frame-clock proof is required before indexed extraction'
 assert decoded['timeBase']=='1/60000' and decoded['width']==1920 and decoded['height']==1080
 def add(frame,kind,**detail):
  if not 0<=frame<total:return
  reason=dict(kind=kind,**detail);row=items.setdefault(frame,dict(frame=frame,reasons=[]))
  if reason not in row['reasons']:row['reasons'].append(reason)
 def nearby(frame,radius,kind,**detail):
  for delta in range(-radius,radius+1):add(frame+delta,kind,edgeFrame=frame,delta=delta,**detail)
 branding_sources={name:evidence(c.R/row['file'])for name,row in timeline['branding'].items()}
 assert timeline['branding']['intro']['frames']==120 and timeline['branding']['membership']['frames']==600
 add(60,'branding-proof',sourceClip=branding_sources['intro'],sourceFrame=60,meaning='Actual final master intro pixels; approved clip hash is provenance, not a substitute for final encoding/audio proof')
 add(timeline['branding']['membership']['startFrame']+300,'membership-proof',sourceClip=branding_sources['membership'],sourceFrame=300,meaning='Actual final master member pixels; approved clip hash is provenance, not a substitute for final encoding/audio proof')
 for cue in caps['cues']:
  a,b=cue['startFrame'],cue['endFrame'];assert 0<=a<b<=total
  add((a+b-1)//2,'caption-midpoint',cueId=cue['id'],scene=cue['scene'],line=cue['line'],ko=cue['ko'],startFrame=a,endFrameExclusive=b)
 for p in edit['paragraphs']:
  assert p['frames']==p['endFrame']-p['startFrame']>0
  for edge in ('startFrame','endFrame'):nearby(p[edge],1,'paragraph-transition',paragraphId=p['id'],edge=edge,layout=p['layout'])
 annotations=c.module('v8_caption_pixel_guide_design',H/'annotations.py');game=c.read(H/'game-cut-plan.json');keys=game['annotations']['keys']
 for p in edit['paragraphs']:
  if p['layout']!='game-model':continue
  for n,row in enumerate(p['left']):
   a,b=row['startFrame'],row['endFrameExclusive'];nearby(a,2,'game-pane-cut',paragraphId=p['id'],segment=n,kindAfter=row['kind'],sourceStartFrame=row.get('sourceStartFrame'),sourceFrameForGuide=row.get('sourceFrameForGuide'))
   nearby(b,2,'game-pane-cut-end',paragraphId=p['id'],segment=n,kindBefore=row['kind'])
   if row['kind']!='video':continue
   first=row['sourceStartFrame'];last=first+b-a
   for key in keys:
    f=key['sourceFrame']
    if first<=f<last:nearby(a+f-first,1,'game-manual-source-anchor',paragraphId=p['id'],sourceFrame=f,anchorVisible=key['visible'])
   previous=None
   for start,end in annotations.windows(row,keys):
    ga=annotations.at(keys,first+start);gb=annotations.at(keys,first+end-1)
    active=bool(ga) and [(x['label'],x['colorRole'])for x in ga]==[(x['label'],x['colorRole'])for x in gb]
    active=active and any(annotations.bracket(g['point']) for g in ga)
    if previous is None or active!=previous:
     nearby(a+start,2,'game-guide-planned-visibility',paragraphId=p['id'],sourceFrame=first+start,guideVisible=bool(active),semantics='Actual ASS design boundary; encoded pixels still need review')
    previous=active
 reuse,rootproof=root_reuse(master_sha);folder=D/'caption-pixels'/master_sha[:12];rows=[]
 previous=c.read(REVIEW) if REVIEW.exists() else None
 prior={x['frame']:x for x in previous['rows']if x.get('extracted')}if previous and previous.get('masterSha256')==master_sha else {}
 for f,row in sorted(items.items()):
  row['file']=c.rel(folder/'frames'/f'f-{f:07}.png');row['mobile']=c.rel(folder/'frames'/f'f-{f:07}.375.png')
  if f in reuse:row.update(reuse[f])
  elif f in prior:
   row.update({k:prior[f][k]for k in ('file','mobile','sha256','mobileSha256','decodedPts')if k in prior[f]})
   row['origin']='same-master prior finite extraction'
  else:row['origin']='current encoded master software extraction'
  rows.append(row)
 result=dict(schemaVersion=1,revision='orientation-matrix-v8',status='exact-frame-plan-ready;pixel-review-pending',
   master=evidence(MASTER),masterSha256=master_sha,totalFrames=total,fps=60,
   inputs=dict(implementation=evidence(Path(__file__)),timeline=evidence(H/'timeline.json'),editPlan=evidence(H/'edit-plan.json'),captions=evidence(c.O/'captions/captions.json'),annotations=evidence(H/'annotations-manifest.json'),gameGuideDesign=evidence(H/'game-cut-plan.json'),rootRepresentativeProof=rootproof,currentMasterExactFrameClock=evidence(clockproof),approvedBrandingSources=branding_sources),
   captionCueCount=475,captionCueMidpointsCovered=sum(1 for r in rows for x in r['reasons']if x['kind']=='caption-midpoint'),uniqueFrames=len(rows),deduplicated=True,
   reusedRootFrames=sum(r['origin']=='root qa.py representative' for r in rows),rows=rows,
   decodeConcurrency=1,decoderThreads=1,decodePassesForNewFrames=1,
   nativeRaster=[1920,1080],mobileRaster=[375,211],contactNativePreviewRaster=[960,540],frameExtraction='One finite software decode; select only required absolute PTS=frame*1000. Verify complete selected PTS array, PNG count and order before reuse/commit.',
   actualPixelReview='pending',continuousMotionReview='not established by still samples',wholeListening='not performed by this sampler',humanApproval=False)
 assert result['captionCueMidpointsCovered']==475
 c.save(PLAN,result);return result

def extract(limit):
 plan=build_plan();expected=plan['masterSha256'];made=0;rows=[]
 flags=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0)
 missing=[r for r in plan['rows']if not (c.R/r['file']).exists()]
 selected=missing if limit is None else missing[:limit]
 if selected:
  c.authorized();wanted=[r['frame']*1000 for r in selected]
  key=hashlib.sha256(json.dumps(wanted).encode()).hexdigest()[:12]
  batch=D/'caption-pixels'/expected[:12]/'batches'/key;batch.mkdir(parents=True,exist_ok=True);receipt=batch/'selected-frames.json'
  if receipt.exists():
   recorded=c.read(receipt);assert recorded['masterSha256']==expected and recorded['verifiedSelectedPts']==wanted
  else:
   assert not list(batch.glob('selected-*.png')),'Preserve an interrupted unverified extraction batch; inspect it before retrying'
   terms=[f'eq(pts\\,{pts})'for pts in wanted]
   # A flat681-term sum exceeds av_expr's recursive parser depth. The same
   # positive equality tests in a balanced tree keep depth logarithmic.
   while len(terms)>1:terms=['('+terms[i]+'+'+terms[i+1]+')'if i+1<len(terms)else terms[i] for i in range(0,len(terms),2)]
   vf=batch/'selection.filter.txt';vf.write_text('select='+terms[0]+',showinfo',encoding='utf-8')
   command=['ffmpeg','-hide_banner','-loglevel','info','-nostats','-nostdin','-n','-copyts','-threads','1','-filter_threads','1','-i',str(MASTER),'-map','0:v:0','-/vf',str(vf),'-frames:v',str(len(wanted)),'-fps_mode','vfr','-threads:v','1','-start_number','0',str(batch/'selected-%05d.png')]
   result=subprocess.run(command,capture_output=True,cwd=c.R,creationflags=flags);log=batch/'decode.log';log.write_bytes(result.stderr)
   assert result.returncode==0,(batch,result.stderr.decode(errors='replace')[-2000:])
   pts=[int(x)for x in re.findall(rb'\bn:\s*\d+\s+pts:\s*(-?\d+)\s+pts_time:',result.stderr)]
   pngs=sorted(batch.glob('selected-*.png'));assert pts==wanted and len(pngs)==len(wanted),('Selected PTS/count/order differs',len(pts),len(wanted),len(pngs))
   recorded=dict(masterSha256=expected,verifiedSelectedPts=pts,pngCount=len(pngs),sourceTimeBase='1/60000',oneSequentialSoftwareDecode=True,decoderThreads=1,pngEncoderThreads=1,files=[])
   for i,(row,png)in enumerate(zip(selected,pngs)):
    assert png.name==f'selected-{i:05d}.png'
    with Image.open(png)as im:assert im.size==(1920,1080)
    recorded['files'].append(dict(sourceFrame=row['frame'],verifiedSourcePts=wanted[i],file=c.rel(png),sha256=c.sha(png)))
   c.save(receipt,recorded)
  for row,png in zip(selected,recorded['files']):
   target=c.R/row['file'];stage=c.R/png['file'];target.parent.mkdir(parents=True,exist_ok=True)
   if target.exists():assert c.sha(target)==png['sha256']
   else:assert stage.exists() and c.sha(stage)==png['sha256'];stage.rename(target)
   exact=dict(masterSha256=expected,sourceFrame=row['frame'],verifiedSourcePts=row['frame']*1000,sourceTimeBase='1/60000',sha256=png['sha256'],batchEvidence=evidence(receipt))
   c.save(target.with_suffix('.exact-frame.json'),exact);row['decodedPts']=row['frame']*1000;made+=1
 for row in plan['rows']:
  file=c.R/row['file'];mobile=c.R/row['mobile'];present=file.exists()
  if present and row.get('sha256'):assert c.sha(file)==row['sha256'],('Changed cached current sample',file)
  if not present:
   rows.append(dict(row,extracted=False));continue
  if row['origin']!='root qa.py representative':
   proof=file.with_suffix('.exact-frame.json');assert proof.exists(),('Preserve cached image without exact PTS proof',file)
   exact=c.read(proof);assert exact['masterSha256']==expected and exact['verifiedSourcePts']==row['frame']*1000 and exact['sha256']==c.sha(file)
   row['decodedPts']=exact['verifiedSourcePts']
  with Image.open(file)as im:
   assert im.size==(1920,1080),('Native sample dimensions',file,im.size)
   if not mobile.exists():mobile.parent.mkdir(parents=True,exist_ok=True);im.resize((375,211),Image.Resampling.LANCZOS).save(mobile)
  with Image.open(mobile)as im:assert im.size==(375,211)
  rows.append(dict(row,sha256=c.sha(file),mobileSha256=c.sha(mobile),extracted=True))
 assert c.sha(MASTER)==expected,'Current master changed during this bounded extraction; do not mix versions'
 result=dict(plan,rows=rows,status='current-frame-images-extracted;human-review-pending'if all(x['extracted']for x in rows)else'bounded-extraction-partial;human-review-pending',newFramesThisRun=made,extractedFrames=sum(x['extracted']for x in rows),missingFrames=sum(not x['extracted']for x in rows),actualPixelReview='pending actual image inspection',continuousMotionReview='not established by these still samples',wholeListening='not performed',humanApproval=False)
 c.save(REVIEW,result);print(json.dumps({k:result[k]for k in ('status','newFramesThisRun','extractedFrames','missingFrames','reusedRootFrames')}));return result

def white_box_pixels(image,expected,mobile=False):
 import numpy as np
 from scipy import ndimage
 sx,sy=(375/1920,211/1080)if mobile else(1,1)
 region=(int(128*sx),int(880*sy),int(1792*sx),min(image.height,int(1070*sy)+1))
 a=np.asarray(image.convert('RGB').crop(region));mask=(a.min(axis=2)>210)&((a.max(axis=2).astype(int)-a.min(axis=2))<32)
 labels,count=ndimage.label(mask)
 if not count:return dict(passed=False,reason='No connected white caption background in reserved region')
 counts=np.bincount(labels.ravel());counts[0]=0;index=int(counts.argmax());obj=ndimage.find_objects(labels)[index-1]
 y,x=obj;actual=[x.start+region[0],y.start+region[1],x.stop+region[0],y.stop+region[1]]
 ex,ey,w,h=expected;want=[ex*sx,ey*sy,(ex+w)*sx,(ey+h)*sy];error=max(abs(a-b)for a,b in zip(actual,want));ratio=int(counts[index])/(w*h*sx*sy)
 tolerance=2.5 if mobile else 6
 return dict(passed=error<=tolerance and ratio>.4,actualWhiteBounds=actual,expectedBoxBounds=want,maxEdgeDifferencePixels=round(error,3),connectedWhiteAreaRatio=round(ratio,3),edgeTolerance=tolerance,meaning='Pixel-presence and clipping screen; not OCR or a human readability claim')

def contacts():
 c.authorized();report=c.read(REVIEW);assert c.sha(MASTER)==report['masterSha256']
 folder=D/'caption-pixels'/report['masterSha256'][:12]/'contacts';folder.mkdir(parents=True,exist_ok=True)
 rows=[r for r in report['rows']if r.get('extracted')];pages=[];caption_pages=[];checks=[]
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
 caption_data=c.read(c.O/'captions/captions.json');geometry=c.read(c.O/'captions/geometry.ko.json');boxes={r['id']:r for r in geometry['rows']};caption_rows=[]
 assert len(boxes)==len(caption_data['cues'])==475
 assert report['inputs']['captions']['sha256']==c.sha(c.O/'captions/captions.json')
 for row in rows:
  cue_reasons=[r for r in row['reasons']if r['kind']=='caption-midpoint']
  if not cue_reasons:continue
  with Image.open(c.R/row['file'])as native,Image.open(c.R/row['mobile'])as mobile:
   for reason in cue_reasons:
    g=boxes[reason['cueId']];x,y,w,h=g['box'];geometry_ok=x>=150 and y>=880 and y+h+14<=1060 and max(g['widths'])<=1570
    native_pixels=white_box_pixels(native,g['box']);mobile_pixels=white_box_pixels(mobile,g['box'],True)
    checks.append(dict(cueId=reason['cueId'],frame=row['frame'],geometryPassed=geometry_ok,nativePixels=native_pixels,mobilePixels=mobile_pixels,passed=geometry_ok and native_pixels['passed']and mobile_pixels['passed'],humanReadability='pending native strip/375 contact inspection'))
    caption_rows.append((row,reason))
 for start in range(0,len(caption_rows),12):
  group=caption_rows[start:start+12];canvas=Image.new('RGB',(2070,242*len(group)),'#202020');draw=ImageDraw.Draw(canvas)
  for n,(row,reason)in enumerate(group):
   y=n*242;file=c.R/row['file'];mobile=c.R/row['mobile'];assert c.sha(file)==row['sha256']and c.sha(mobile)==row['mobileSha256']
   with Image.open(file)as im:canvas.paste(im.crop((128,880,1792,1070)),(0,y+35))
   with Image.open(mobile)as im:canvas.paste(im,(1680,y+25))
   draw.text((8,y+2),f'{reason["cueId"]} / F{row["frame"]} / native caption crop + actual375px',font=font,fill='white')
  file=folder/f'caption-strips-{start//12:03}.jpg';canvas.save(file,quality=96);caption_pages.append(dict(evidence(file),cueIds=[r['cueId']for _,r in group],frames=[r['frame']for r,_ in group]))
 game_kinds={'game-pane-cut','game-pane-cut-end','game-manual-source-anchor','game-guide-planned-visibility'}
 game_rows=[r for r in rows if any(q['kind']in game_kinds for q in r['reasons'])]
 for start in range(0,len(game_rows),4):
  group=game_rows[start:start+4];canvas=Image.new('RGB',(1365,600*len(group)),'#202020');draw=ImageDraw.Draw(canvas)
  for n,row in enumerate(group):
   y=n*600;file=c.R/row['file'];mobile=c.R/row['mobile'];assert c.sha(file)==row['sha256'] and c.sha(mobile)==row['mobileSha256']
   with Image.open(file)as im:canvas.paste(im.resize((960,540),Image.Resampling.LANCZOS),(0,y+50))
   with Image.open(mobile)as im:canvas.paste(im,(980,y+50))
   kinds=', '.join(dict.fromkeys(r['kind']for r in row['reasons']));cueids=', '.join(r['cueId']for r in row['reasons']if r.get('cueId'))
   draw.text((8,y+2),f'F{row["frame"]} / {row["frame"]/60:.3f}s  {cueids}',font=font,fill='white')
   draw.text((980,y+276),'375px 실제 축소',font=font,fill='#e8cf83')
   draw.text((980,y+310),kinds[:28],font=font,fill='white')
  file=folder/f'game-boundaries-{start//4:03}.jpg';canvas.save(file,quality=94);pages.append(dict(evidence(file),frames=[r['frame']for r in group]))
 pixel_review=dict(masterSha256=report['masterSha256'],geometryReport=evidence(c.O/'captions/geometry.ko.json'),checkedCueCount=len(checks),expectedCueCount=475,all475Checked=len(checks)==475,issues=[r for r in checks if not r['passed']],checks=checks,pixelChecksAreNotHumanReading=True,actualHumanInspection='pending')
 c.save(D/'caption-pixels-bounds.json',pixel_review)
 endcaps=[dict(frame=r['frame'],file=r['file'],mobile=r['mobile'],reasons=[q for q in r['reasons']if q['kind']in ('branding-proof','membership-proof')])for r in rows if any(q['kind']in ('branding-proof','membership-proof')for q in r['reasons'])]
 result=dict(masterSha256=report['masterSha256'],sampleReview=evidence(REVIEW),captionStripPages=caption_pages,gameBoundaryPages=pages,endcapProofFrames=endcaps,pixelBounds=evidence(D/'caption-pixels-bounds.json'),captionCuesIncluded=len(caption_rows),gameBoundaryFramesIncluded=len(game_rows),imagesAvailable=len(rows),remainingMissingFrames=report['missingFrames'],nativeCaptionPreview='Unscaled1664x190 crop from actual1920x1080 frame,12cues/page; whole FHD PNG remains linked',gameNativePreview='960x540 preview; original1920x1080 PNG linked per sample row',mobilePreview='375x211 actual downscale',paragraphTransitions='Exact PNG evidence retained; whole composition reviewed separately in root76representatives',actualHumanInspection='pending targeted caption strips, game boundary pages and exactly two endcap frames; not every full FHD image',continuousMotionReview='not established',humanApproval=False)
 c.save(D/'caption-pixels-contact-pages.json',result);print(json.dumps(dict(captionStripPages=len(caption_pages),gameBoundaryPages=len(pages),captionCues=len(caption_rows),pixelIssues=len(pixel_review['issues']),remainingMissingFrames=report['missingFrames'])))

def main():
 a=argparse.ArgumentParser(description=__doc__);g=a.add_mutually_exclusive_group(required=True)
 for name in ('plan-only','build-plan','extract','contacts'):g.add_argument('--'+name,action='store_true')
 a.add_argument('--max-new',help='Required for --extract: positive integer or explicit all under finite CPU handoff');x=a.parse_args()
 if x.plan_only:plan_only()
 elif x.build_plan:r=build_plan();print(json.dumps(dict(uniqueFrames=r['uniqueFrames'],captionMidpoints=r['captionCueMidpointsCovered'],reusedRootFrames=r['reusedRootFrames'])))
 elif x.extract:
  assert x.max_new is not None,'Supply an explicit finite --max-new bound; extraction never starts from a preflight command'
  limit=None if x.max_new=='all'else int(x.max_new);assert limit is None or limit>0
  extract(limit)
 else:contacts()

if __name__=='__main__':main()
