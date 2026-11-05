"""Each replay is a frame-matched subset of the immediately preceding native shot."""
from pipeline import H,L,O,OLD,V,R,read,save,artifact,rel,libs
from fractions import Fraction
import copy, math
def build(baseline,inserts,total,body,cues,preflight=False):
 ap,vp=libs()
 if preflight:
  from observed_native import records,normal_map
  evidence={'sources':records(),'nativeCutMap':normal_map(),'moves':[]}
 else:evidence=read(H/'analysis-beats.json')
 sources=evidence['sources'];beats=evidence['moves']
 old={c['id']:c for c in read(OLD/'edit-plan.json')['cuts']}; cuts=[];offset=0
 for s in sources.values():
  f=R/s['file'];probe=vp.video_stream(f);s.update(sha=ap.sha(f),width=probe['width'],height=probe['height'],fps=float(Fraction(probe['avg_frame_rate'])))
  assert s['width']>=1920 and s['height']>=1080
 def actual(cid,scene,start,frames,source,ss,purpose,speed=1,normal=None,track=None):
  s=sources[source];se=ss+frames*speed/60
  c={'id':cid,'scene':scene,'startFrame':start,'endFrame':start+frames,'frames':frames,'kind':'independent-gameplay','sourceFile':s['file'],'sourceSha256':s['sha'],'sourceUrl':s['url'],'sourceAttribution':{'publisher':s['recorder'],'url':s['url'],'game':s['game'],'license':s['license']},'gameLabel':s['label'],'sourceNativeFps':s['fps'],'sourceVideoDimensions':[s['width'],s['height']],'sourceAudioEnabled':False,'sourceStart':ss,'sourceEndExclusive':se,'viewport':[160,90,1600,792],'pictureLabel':'1.0배 · 실제 속도' if speed==1 else '0.25배 · 동작 분석','playbackSpeed':speed,'loop':False,'marks':[],'teachingPurpose':purpose,'creditPlacement':'description-bottom'}
  if track:
   assert speed==.25 and normal and track['keyframes']
   c['normalSpeedReference']=normal
   rows=track['keyframes']
   k=[{'t':round((t-ss)/speed,6),'x':256+x*1408,'y':90+y*792,'w':w*1408,'h':h*792} for t,x,y,w,h in rows if ss-0.0000001<=t<=se+0.0000001]
   assert len(k)>=2,(cid,ss,se,rows)
   k[0]['t']=max(0,k[0]['t']);k[-1]['t']=min(frames/60,k[-1]['t'])
   c['marks']=[{'id':'observed-body','shape':'rect','t0':k[0]['t'],'t1':k[-1]['t'],'color':'#F45B63','thickness':10,'label':track['label'],'labelPosition':[32,710],'keyframes':k,'revealSeconds':.075,'interpretation':'Editorial box tied to actually inspected body motion, not a measured hitbox.'}]
   if track.get('hiddenSourceIntervals'):
    c['marks'][0]['hiddenIntervals']=[[(a-ss)/speed,(b-ss)/speed] for a,b in track['hiddenSourceIntervals'] if a>=ss and b<=se]
  return c
 for base in baseline['cuts']:
  ins=next((i for i in inserts if i['originalAtFrame']==base['startFrame']),None)
  if ins:
   i=inserts.index(ins);beat=beats[i];ref=f'A02-F{i+1}1';scene=f'fighter-{i+1}';beg=ins['startFrame'];end=beg+ins['frames']
   lines=sorted((c for c in cues if c['paragraph']==ins['id']),key=lambda c:c['line'])
   split=round((lines[beat['slowCue']]['start']+beat.get('slowDelay',0))*60);ss=beat['range'][0];n=round((beat['range'][1]-ss)*240)
   assert 0<n<=end-split,(i,n,end-split)
   native_frames=split-beg
   start=ss+(n/240)-native_frames/60+beat.get('nativeTail',0)
   if beat.get('introContext'):
    intro=beat['introContext'];nlead=round(intro['duration']*60)
    cuts.append(actual(ref,scene,beg,nlead,beat['source'],intro['sourceStart'],'Begin on the right-side Kula named in the narration; then return to the observed attack.'))
    beg+=nlead;native_frames-=nlead;start=intro['actionStart'];ref=ref+'N'
   assert 0<=start<=ss and start+native_frames/60>=ss+n/240-1e-5
   cuts.append(actual(ref,scene,beg,native_frames,beat['source'],start,beat['observation']))
   cuts.append(actual(f'A02-F{i+1}2',scene,split,n,beat['source'],ss,beat['observation'],.25,ref,beat))
   if split+n<end:cuts.append(actual(f'A02-F{i+1}3',scene,split+n,end-split-n,beat.get('returnId',beat['source']),beat['returnSource'],beat['returnPurpose']))
   offset+=ins['frames']
  cid=base['id']
  if cid in evidence['nativeCutMap']:
   entry=evidence['nativeCutMap'][cid]
   if isinstance(entry[0],list):
    start=base['startFrame']+offset;used=0
    for z,(src,ss,count,purpose) in enumerate(entry):
     n=count if count is not None else base['frames']-used
     cuts.append(actual(cid if z==0 else cid+'-'+str(z+1),base['scene'],start+used,n,src,ss,purpose));used+=n
    assert used==base['frames'];continue
   src,ss,purpose=entry
   c=actual(cid,base['scene'],base['startFrame']+offset,base['frames'],src,ss,purpose)
  else:
   c=copy.deepcopy(old[cid]);assert c['kind']=='explanation' or cid=='A02-E023',cid
   c.update(startFrame=base['startFrame']+offset,endFrame=base['endFrame']+offset)
   if c.get('unrealCapture'):
    c.update(renderedSource=rel(L/'unreal'/(cid+'.mp4')),renderedSourceSha256=None,unrealCapture={'status':'pending-new-1.8x-capture'},renderer='Unreal Game Animation Sample, 1.0× versus 1.8× authored motion amplitude')
  cuts.append(c)
 native=sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay' and c.get('playbackSpeed',1)==1);slow=sum(c['frames'] for c in cuts if c.get('playbackSpeed',1)!=1)
 choice=read(OLD/'ratio-choice.json');choice['revision']=V;save(H/'ratio-choice.json',choice)
 proto=read(OLD/'edit-plan.json');proto.update(revision=V,totalFrames=total,bodyFrames=body,cuts=cuts,expectedGameplayShare=(native+slow)/body,measuredScreenTime={'nativeGameplayFrames':native,'analyticalReplayFrames':slow,'authoredExplanationFrames':body-native-slow},ratioChoice=artifact(H/'ratio-choice.json'),outputDir=rel(L/'edit'),captionsAss=rel(L/'edit/captions.ko.ass'),mixFile=rel(L/'edit/final-mix.wav'),baseline=artifact(OLD/'edit-plan.json'),insertionMap=None if preflight else artifact(H/'narration-insert-map.json'))
 if preflight:
  vp.validate_plan(proto);return proto
 vp.validate_plan(proto);save(H/'edit-plan.json',proto)
 save(H/'annotation-review.json',{'analyses':[{'id':c['id'],'nativeRef':c['normalSpeedReference'],'source':c['sourceFile'],'slowSourceSeconds':[c['sourceStart'],c['sourceEndExclusive']],'editorialTrack':c['marks']} for c in cuts if c.get('playbackSpeed')==.25],'shape':'Red hollow body-region rectangle. No game hitbox inference.','gameplayAudio':'Muted throughout, including quarter-speed; preserved own voice and licensed Nimbus bed.'})
