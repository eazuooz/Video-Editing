"""Observed female fighters, native first then scoped analytical replay."""
from pathlib import Path
import copy,json
import numpy as np
import audio_pipeline as ap,video_pipeline as vp
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v3';OH=H.parent/'grid-v1'
def rel(p):return p.relative_to(R).as_posix()
# Coordinates read from inspected 384x216 contact frames, transformed to the
# full preserved-aspect viewport. These are editorial targets, not game hitboxes.
TRACKS={
 'punch':[(67.5,145,50,100,110),(68.2,145,45,100,120),(68.4,142,20,80,135),(68.5,145,30,90,130),(68.6,185,50,100,125),(68.8,180,70,100,105),(69.,130,65,90,110),(69.2,60,50,90,125),(69.5,45,50,90,125)],
 'horizontal':[(55.,90,85,105,115),(56.4,80,75,110,130),(56.6,90,80,110,125),(56.8,80,95,165,105),(57.,90,95,165,105),(57.2,130,65,115,140),(57.4,85,90,110,110),(58.,85,85,115,120)],
 'vertical':[(60.,80,80,110,125),(60.6,85,80,110,125),(60.8,105,75,110,130),(61.,135,8,115,198),(61.2,155,65,110,140),(61.4,85,80,110,125),(62.2,90,75,110,130)],
 'spin':[(244.8,60,55,85,120),(245.,60,55,85,120),(245.25,75,90,90,110),(245.5,100,8,100,140),(245.75,190,35,75,130),(246.,185,95,100,110),(246.25,170,70,95,130),(246.5,150,65,90,135),(246.8,145,65,90,135)]}
def tracked(cut,kind,label):
 rows=TRACKS[kind];start=cut['sourceStart'];end=start+cut['frames']/60*.25
 lo=max(start,rows[0][0]);hi=min(end,rows[-1][0]);assert hi>lo
 times=sorted(set([lo,hi]+[v[0] for v in rows if lo<v[0]<hi]));keys=[]
 for t in times:
  values=[float(np.interp(t,[v[0] for v in rows],[v[k] for v in rows])) for k in range(1,5)]
  x,y,w,h=values;keys.append({'t':min(cut['frames']/60,round((t-start)/.25,6)),'x':256+x*1408/384,'y':90+y*792/216,'w':w*1408/384,'h':h*792/216})
 short={'punch':'팔·몸통','horizontal':'실루엣','vertical':'실루엣','spin':'회전'}[kind]
 return {'id':'observed-body','shape':'rect','t0':keys[0]['t'],'t1':keys[-1]['t'],'color':'#F45B63','thickness':9,'label':short,'labelPosition':[32,720],'keyframes':keys,'revealSeconds':.12,'interpretation':'Hand-authored guide around the directly inspected visible movement; no detector or hitbox claim.'}
def build(baseline,inserts,total,body,cues):
 sources={}
 for row in ap.read(H/'source-review.json')['sources']:
  f=R/row['file'];s=vp.video_stream(f);assert s['width']>=1920 and s['height']>=1080
  sources[row['id']]={'sourceFile':rel(f),'sourceSha256':ap.sha(f),'sourceUrl':row['url'],'sourceAttribution':{'publisher':row['recorder'],'url':row['url'],'game':row['game']},'gameLabel':row['game']+' · '+row['character'].split(' / ')[-1],'sourceNativeFps':float(eval(s['avg_frame_rate'],{'__builtins__':{}},{})),'sourceVideoDimensions':[s['width'],s['height']],'sourceAudioEnabled':False}
 def actual(cid,scene,start,frames,src,ss,purpose,speed=1,normal=None,track=None,label=None):
  c={'id':cid,'scene':scene,'startFrame':start,'endFrame':start+frames,'frames':frames,'kind':'independent-gameplay',**sources[src],'sourceStart':ss,'sourceEndExclusive':ss+frames/60*speed,'viewport':[160,90,1600,792],'pictureLabel':('1.0배 · 실제 속도' if speed==1 else '0.25배 · 동작 분석'),'playbackSpeed':speed,'loop':False,'marks':[],'teachingPurpose':purpose,'rightsFinalized':False,'recordingReusePermissionVerified':False,'creditPlacement':'description-bottom'}
  if speed!=1:c['normalSpeedReference']=normal;c['marks']=[tracked(c,track,label)]
  return c
 keep={'A02-'+x for x in ['E004','E005','E006','E011','E013','E014','E015','E021','E022','E024','E025','E026','E027']}
 ue={'A02-'+x for x in ['E004','E005','E011','E013','E014','E015']}
 mapping={'E001':('kof-shermie',244.8),'E002':('kof-shermie',249.5),'E002B':('kof-shermie',67.5),'E003':('gg-giovanna',55.),'E007':('kof-shermie',65.5),'E008':('kof-shermie',68.),'E009':('gg-giovanna',56.),'E010':('gg-giovanna',50.),'E012':('kof-shermie',61.),'E016':('kof-shermie',245.),'E017':('kof-shermie',249.5),'E018':('gg-giovanna',60.),'E019':('kof-shermie',240.),'E020':('gg-giovanna',53.),'E028':('kof-shermie',66.),'E029':('gg-giovanna',59.8),'E030':('kof-shermie',244.8)}
 cuts=[];offset=0
 for old in baseline['cuts']:
  ins=next((x for x in inserts if x['originalAtFrame']==old['startFrame']),None)
  if ins:
   idx=inserts.index(ins);rows=sorted([c for c in cues if c['paragraph']==ins['id']],key=lambda c:c['line']);first=ins['startFrame'];end=first+ins['frames']
   indices=[[3,6,8],[3,6,9],[2,5,7]][idx]
   bs=[first]+[round(rows[n]['start']*60) for n in indices]+[end]
   configs=[
    [('kof-shermie',65.5,1,None,None),('kof-shermie',67.8,.25,'punch','팔과 몸통'),('kof-shermie',68.2,.25,'punch','어깨 → 허리'),('kof-shermie',68.3,1,None,None)],
    [('gg-giovanna',55.4,1,None,None),('gg-giovanna',56.3,.25,'horizontal','가로로 뻗는 실루엣'),('gg-giovanna',60.3,.25,'vertical','위로 향하는 실루엣'),('gg-giovanna',59.7,1,None,None)],
    [('kof-shermie',243.8,1,None,None),('kof-shermie',244.8,.25,'spin','준비 → 도약 → 착지'),('kof-shermie',245.2,.25,'spin','어깨와 골반의 회전'),('kof-shermie',249.5,1,None,None)]][idx]
   for j,(src,ss,speed,track,label) in enumerate(configs):
    c=actual(f'A02-F{idx+1}{j+1}',f'fighter-{idx+1}',bs[j],bs[j+1]-bs[j],src,ss,'Observed normal action → named body-region analysis → whole-motion confirmation',speed,f'A02-F{idx+1}1' if speed!=1 else None,track,label);cuts.append(c)
   offset+=ins['frames']
  if old['id'] in keep or old['id']=='A02-E023':
   c=copy.deepcopy(old);c['startFrame']+=offset;c['endFrame']+=offset
   if c['id'] in ue:
    receipt=L/'unreal'/f"{c['id']}-capture.json"
    j=ap.read(receipt) if receipt.exists() else {'movie':rel(L/'unreal'/f"{c['id']}.mp4"),'movieSha256':None}
    c.pop('nativeCapture',None);c.pop('explanationRender',None);c['renderedSource']=j['movie'];c['renderedSourceSha256']=j['movieSha256'];c['renderedStartFrame']=0;c['unrealCapture']=ap.artifact(receipt) if receipt.exists() else {'status':'pending-native-capture'};c['marks']=[];c['renderer']='Unreal Engine5.8.4, Game Animation Sample mannequin; authored comparison'
  else:
   src,ss=mapping[old['id'][4:]];c=actual(old['id'],old['scene'],old['startFrame']+offset,old['frames'],src,ss,old['teachingPurpose'])
  cuts.append(c)
 choice={'episode':'A02','slug':'animation-exaggeration','revision':'fighters-v3','basis':'recommended-production-choice-v1','defaultContractAcknowledged':'actual60:explanation40','scope':'This explicitly requested revision only','decision':'Preserve all lesson speech and retain meaningful native game demonstrations; report native / analytical replay / authored explanation separately without padding.','reasons':['User explicitly requests normal-speed-first plus slow-motion analysis, superseding the default native-speed rule for these passages.','New paragraph length is measured from local Qwen PCM; no forced speed or extra footage to hit a percentage.']}
 ap.save(H/'ratio-choice.json',choice)
 native=sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay' and c.get('playbackSpeed',1)==1);slow=sum(c['frames'] for c in cuts if c.get('playbackSpeed',1)!=1);actualFrames=native+slow
 p={'episode':'A02','slug':'animation-exaggeration','revision':'fighters-v3','fps':60,'width':1920,'height':1080,'totalFrames':total,'bodyFrames':body,'introFrames':120,'outroFrames':600,'cuts':cuts,'expectedGameplayShare':actualFrames/body,'measuredScreenTime':{'nativeGameplayFrames':native,'analyticalReplayFrames':slow,'authoredExplanationFrames':body-actualFrames},'ratioChoice':ap.artifact(H/'ratio-choice.json'),'ratioToleranceFrames':1,'outputDir':rel(L/'edit'),'outputStem':'animation-exaggeration','captionsAss':rel(L/'edit/captions.ko.ass'),'mixFile':rel(L/'edit/final-mix.wav'),'captionProtectedRect':[150,892,1784,1060],'baseline':ap.artifact(OH/'edit-plan.json'),'insertionMap':ap.artifact(H/'narration-insert-map.json'),'nativeSourceClosure':ap.artifact(OH/'saved-scene-source-manifest.json'),'baselinePreserved':True,'humanFinalReview':False,'platformMutation':False}
 vp.validate_plan(p);ap.save(H/'edit-plan.json',p)
 print('Cut plan',len(cuts),'native / slow / explanation frames',p['measuredScreenTime'])
