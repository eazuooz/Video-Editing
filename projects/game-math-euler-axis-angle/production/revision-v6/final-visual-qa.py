"""Plan final encoded visual samples; derive boards from the caption QA decode.

This module never decodes/renders media. All native frames must already exist
in caption-output-qa.py's one shared extraction. Planning is not pixel review.
"""
from pathlib import Path
import argparse,hashlib,json,math
from PIL import Image,ImageDraw,ImageFont

R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
O=P/'production/local/revision-v6';FONT=Path('C:/Windows/Fonts/malgun.ttf')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def proof(p):return dict(file=rel(p),sha256=sha(p))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def sampling_plan(timeline,sceneplan,captions):
 assert sceneplan['timelineSha256']==captions['timelineSha256']
 targets=[];samples={};total=timeline['totalFrames']
 def add(frame,tag):
  f=max(0,min(total-1,int(frame)));samples.setdefault(f,set()).add(tag);return f
 def cue_mid(c):return max(c['startFrame'],min(c['endFrame']-1,(c['startFrame']+c['endFrame']-1)//2))
 by_scene={s['id']:s for s in timeline['scenes']}
 for s in sceneplan['scenes']:
  source=by_scene[s['id']];beats={b['id']:b for b in [*source['teachingBeats'],*source.get('auxiliaryVisuals',[])]}
  for index,phase in enumerate(s['phases']):
   if phase['kind']!='motion':continue
   a,b=phase['startFrame'],phase['endFrame'];n=b-a;assert n==phase['frames'] and n>0
   ident=phase['beatId'];asset=sceneplan['inputAssets'].get(ident,{})
   file_hash=sceneplan['sourceAssetFiles'].get(phase['file'],asset.get('sha256'))
   assert file_hash and len(file_hash)==64,(ident,'Missing frozen source-asset identity')
   five=[a+((n-1)*numerator)//4 for numerator in range(5)]
   for frac,f in zip(['first','25','50','75','last'],five):add(f,'motion:'+ident+':'+frac)
   beat=beats.get(ident,{});observation=[];confirmation=[]
   hold_end=beat.get('holdEndFrame')
   if hold_end is None and index+1<len(s['phases']):hold_end=s['phases'][index+1]['endFrame']
   if hold_end is not None and hold_end>b:
    observation=sorted({b+(hold_end-b-1)//2,hold_end-1})
    for f in observation:add(f,'observation:'+ident)
   check_lines=beat.get('resultCheckLines',[])
   matching=[c for c in captions['cues'] if c['scene']==s['id'] and c['line'] in check_lines]
   confirmation_basis='explicit resultCheckLines' if matching else 'No separate spoken confirmation inside this source scene; observation state is checked without inventing speech.'
   if not matching and hold_end is not None:
    following_motion=next((p['startFrame'] for p in s['phases'][index+1:] if p['kind']=='motion'),s['startFrame']+s['frames'])
    matching=[c for c in captions['cues'] if c['scene']==s['id'] and c['endFrame']>hold_end and c['startFrame']<following_motion]
    if matching:confirmation_basis='actual next spoken continuation after the hold, before next motion; not relabeled as a new result-check sentence'
   if matching:
    confirmation=sorted({cue_mid(matching[0]),cue_mid(matching[-1])})
    for f in confirmation:add(f,'confirmation:'+ident)
   targets.append(dict(id=ident,scene=s['id'],phaseIndex=index,renderer=phase.get('renderer'),sourceKind=phase['sourceKind'],startFrame=a,endFrameExclusive=b,frames=n,seconds=n/60,sourceFile=phase['file'],sourceSha256=file_hash,motionFrames=five,observationFrames=observation,confirmationFrames=confirmation,confirmationBasis=confirmation_basis,resultCheckLines=check_lines,observationPurpose=beat.get('observationPurpose'),realTimePlayback='pending; five temporal samples are not continuous playback'))
 assert len({t['id'] for t in targets})==len(targets)
 assert sum(t['sourceKind']=='actual' for t in targets)==len(timeline['cuts'])==4
 return dict(schemaVersion=1,revision='article-flow-v6',timelineSha256=sceneplan['timelineSha256'],totalFrames=total,motionCount=len(targets),targets=targets,extraNativeSamples=[dict(frame=f,tags=sorted(tags)) for f,tags in sorted(samples.items())],motionFiveFrames=sorted({f for t in targets for f in t['motionFrames']}),sourceEvidenceReuse='Reuses independently reviewed unchanged source assets by file/hash; the final encoded UI, captions, source labels and joins remain separate actual-output checks.',humanNativeAndMobileReview='pending',realTimeMotionReview='pending',mediaDecodedByThisModule=False)

def derive_motion_boards(plan,out):
 """Only resize existing extracted native PNGs; never open the master."""
 visual=plan['visualReview'];frames=plan['nativeFrames'];lookup={f:i for i,f in enumerate(frames)}
 font=ImageFont.truetype(str(FONT),20);small=ImageFont.truetype(str(FONT),17)
 files=[];targets=[]
 for ti,target in enumerate(visual['targets']):
  native_frames=[out/'native'/f'{lookup[f]:06d}.png' for f in target['motionFrames']]
  assert all(p.is_file() for p in native_frames),'Run the shared one-pass caption extraction first; never independently decode missing frames'
  for mobile in [False,True]:
   w,h,cols,rows=(375,211,5,1) if mobile else (960,540,2,3)
   top=54;board=Image.new('RGB',(w*cols,top+(h+32)*rows),'#111111');draw=ImageDraw.Draw(board)
   draw.text((8,4),f"{target['id']} / {target['renderer']} / {target['sourceKind']}",font=font,fill='white')
   draw.text((8,29),'Final encoded UI/captions. Temporal samples; actual playback remains separate.',font=small,fill='#bbbbbb')
   for j,(frame,file) in enumerate(zip(target['motionFrames'],native_frames)):
    with Image.open(file) as original:
     assert original.size==(1920,1080)
     image=original.convert('RGB').resize((w,h),Image.Resampling.LANCZOS)
    x=(j%cols)*w;y=top+(j//cols)*(h+32);draw.text((x+4,y+3),f"{['first','25%','50%','75%','last'][j]} f{frame} {frame/60:.3f}s",font=small,fill='white');board.paste(image,(x,y+32))
   dest=out/f"motion-{'mobile' if mobile else 'native'}-{ti:03d}.jpg";board.save(dest,quality=94);files.append(proof(dest))
  targets.append({**target,'nativeFrameFiles':[dict(frame=f,**proof(p)) for f,p in zip(target['motionFrames'],native_frames)],'nativeBoard':rel(out/f'motion-native-{ti:03d}.jpg'),'mobileBoard':rel(out/f'motion-mobile-{ti:03d}.jpg'),'humanPixelReview':'pending actual opening'})
 report=dict(inputs=dict(sharedActualExtraction=proof(out/'actual-extraction.json'),sharedSamplePlan=proof(out/'sample-plan.json'),implementation=proof(Path(__file__))),motionCount=len(targets),targets=targets,boards=files,noNewDecode=True,mobileDerivedFromSameNativeFrames=True,humanPixelReview='pending actual opening',realTimeMotionReview='pending; temporal samples cannot establish every intervening frame')
 save(out/'visual-review-targets.json',report);return report

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--derive-from-qa',type=Path);args=ap.parse_args()
 if args.prepare_only:
  t=read(H/'timeline.json');s=read(O/'edit/scene-plan.json');c=read(O/'captions/captions.json');p=sampling_plan(t,s,c)
  p['inputs']=dict(timeline=proof(H/'timeline.json'),scenePlan=proof(O/'edit/scene-plan.json'),captions=proof(O/'captions/captions.json'),implementation=proof(Path(__file__)))
  dest=O/'qa/preparation/final-visual-sampling-plan.json';save(dest,p)
  print(json.dumps(dict(file=rel(dest),sha256=sha(dest),motionCount=p['motionCount'],uniqueExtraFrames=len(p['extraNativeSamples']),mediaOpened=False)))
 elif args.derive_from_qa:derive_motion_boards(read(args.derive_from_qa/'sample-plan.json'),args.derive_from_qa)
 else:ap.error('Choose CPU --prepare-only or derive only from an existing shared extraction')
if __name__=='__main__':main()
