"""Reallocate only selected changed paragraphs and reuse decoded-equivalent existing cuts."""
from pathlib import Path
import json,hashlib,copy,math,os,shutil
from collections import defaultdict
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';B=P/'production/local';L=P/'production/local-ai-copyright-v2';V=P/'production/revision-ai-copyright-v2';MC=R/'motion-canvas/src/projects'/P.name
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def linked(a,b):
 b.parent.mkdir(parents=True,exist_ok=True)
 if not b.exists():os.link(a,b)
 assert sha(a)==sha(b)

def main():
 base=rd(V/'baseline/production/edit-plan.json');t=rd(L/'timing.json');sp=rd(L/'pcm-splice-map.json');changed=rd(V/'revision.json')['changedParagraphs'];groups=defaultdict(list)
 for c in base['cuts']:groups[c['paragraph']].append(c)
 lengths={i:sum(c['frames'] for c in groups[i]) for i in range(1,61)}
 for row in sp['paragraphs']:
  if row['replacement']:
   old=rd(B/'timing.json')['paragraphs'];idx=row['paragraph']-1
   # The splice map records the actual old replacement samples separately.
   oldjoins={x['afterParagraph']:x['sample'] for x in sp['oldJoinEvidence']}
   oldedges=[0]+[oldjoins.get(i,round((old[i-1]['end']+old[i]['start'])/2*24000)) for i in range(1,60)]+[round(rd(B/'timing.json')['duration']*24000)]
   original=oldedges[idx+1]-oldedges[idx]
   lengths[idx+1]+=round((row['destinationEndSample']-row['destinationStartSample']-original)/400)
 lengths[59]+=t['bodyFrames']-sum(lengths.values()) # subframe rounding at changed closing explanation
 actual={i:sum(c['frames'] for c in groups[i] if c['kind']=='actual') for i in range(1,61)}
 for i in changed:
  if all(c['kind']=='actual' for c in groups[i]):actual[i]=lengths[i]
  elif all(c['kind']=='explanation' for c in groups[i]):actual[i]=0
 delta=t['actualFrames']-sum(actual.values());adjustments=[]
 # Meaningful introductory footage can carry the fun comparison before its
 # permission diagram. Do not change preserved gameplay examples or shorten
 # the worked code/art/music checklist merely to meet a ratio.
 for i in ([3,30,57,59] if delta>0 else [38,44,51,58]):
  cap=min(420,lengths[i]-actual[i]-300) if delta>0 else max(0,actual[i]-300)
  n=min(abs(delta),max(0,cap))
  if not n:continue
  actual[i]+=n if delta>0 else -n;adjustments.append({'paragraph':i,'actualFrameChange':n if delta>0 else -n,'reason':'Game appearance demonstrates the narrated playable result before the adjacent rights diagram; no unrelated fill/loop/retime.'});delta+=-n if delta>0 else n
  if delta==0:break
 assert delta==0,('Could not naturally retain60:40',delta)
 # Reserve every retained original range first. New material comes only from
 # inspected unused parts of these already verified FHD60 recordings.
 used=defaultdict(list)
 for c in base['cuts']:
  if c['kind']=='actual':used[c['sourceId']].append((c['sourceStartFrame'],c['sourceStartFrame']+c['frames']))
 def reserve(keys,n):
  out=[]
  for key,start,end in keys:
   free=[(round(start*60),round(end*60))]
   for u,v in used[key]:
    chunks=[]
    for x,y in free:
     if v<=x or u>=y:chunks.append((x,y))
     else:
      if x<u:chunks.append((x,u))
      if v<y:chunks.append((v,y))
    free=chunks
   for x,y in free:
    z=min(n,y-x)
    if z<1:continue
    out.append((key,x,z));used[key].append((x,x+z));n-=z
    if not n:return out
  raise ValueError(('Insufficient reviewed independent footage',n))
 candidates={2:[('d2-02',80,96),('d2-01',54,66)],3:[('d2-developer',17,31)],4:[('vs-02',38.5,45)],30:[('d2-02',96,110)],38:[('vs-02',123.5,139)],44:[('d2-03',92,110),('d2-01',87,108)],51:[('d2-04',54,61),('d2-02',34,48)],57:[('d2-developer',31,46)],58:[('vs-03',104,112),('vs-02',94,110)],59:[('d2-01',87,108)]}
 kinds={3:('overview-ai','AI로 만들면 공개해도 괜찮을까?'),30:('ai-rights','게임이 작동해도, 권리 확인은 남습니다'),38:('ai-rights','새 코드와 기존 자산의 권리는 별개'),44:('ai-rights','AI의 사용량보다, 무엇을 이용했는가'),55:('ai-checklist','공개 전에 출처와 조건을 확인'),57:('ai-rights','AI 개발과 저작권 확인은 다른 질문'),58:('ai-rights','완성과 책임 있는 공개를 나누기'),59:('ai-questions','공개 버튼을 누르기 전에')}
 cuts=[];jobs=[];reuse=[];newsource=[];pos=0;extraid=0
 def add_actual(template,frames):
  nonlocal pos
  c=copy.deepcopy(template);c['frames']=frames;c['startFrame']=pos;cuts.append(c);pos+=frames
 def add_extra(i,n):
  nonlocal pos,extraid
  for key,start,count in reserve(candidates[i],n):
   extraid+=1;receipt=rd(B/'sources'/f'{key}.receipt.json');c={'id':f'a{extraid:03}','paragraph':i,'scene':t['paragraphs'][i-1]['scene'],'kind':'actual','source':rel(B/'sources'/f'{key}.mp4'),'sourceId':key,'sourceSha256':receipt['sha256'],'sourceUrl':receipt['sourceUrl'],'sourceStartFrame':start,'startFrame':pos,'frames':count,'credit':'original source credit retained in description','sourceCrop':None,'audio':'synchronized-game-mix' if key.startswith(('vs','ms')) else 'muted-inseparable-presenter-or-unreviewed-developer-track','observedRole':t['paragraphs'][i-1]['ko'],'annotation':None};cuts.append(c);newsource.append(c);pos+=count
 def add_explain(i,n):
  nonlocal pos
  old=next((c for c in groups[i] if c['kind']=='explanation'),None)
  if i not in changed and old and old['frames']==n:
   c=copy.deepcopy(old);c['startFrame']=pos;cuts.append(c);pos+=n;return
  kind,title=kinds[i];id=old['id'] if old else f'e{i:03}';entry=MC/f'ai-{id}.tsx';project=MC/f'ai-{id}-project.ts';image=B/'source-review/d2-03-24-native.jpg'
  ps=t['paragraphs'][i-1];at=pos/60
  sentences=[c for c in t['cues'] if c['paragraph']==i]
  # Relevant clause starts measured from the actual new speech, clipped to this
  # cut. Further detail appears while the same narrated target remains visible.
  cue=[.05,max(.4,min(n/60*.28,3.5)),max(.8,min(n/60*.58,7))]
  if i==55:
   for term,idx in [('코드와 그림',1),('허락이 불명확',2)]:
    hit=next((q for q in sentences if term in q['ko']),None)
    if hit:cue[idx]=max(.1,min(n/60-.6,hit['start']-at))
  data={'kind':kind,'title':title,'duration':n/60,'image':'/@fs/'+image.resolve().as_posix(),'cueTimes':cue}
  entry.write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {aiLesson} from './ai-visuals';\nexport default makeScene2D(function*(view){yield* aiLesson(view,"+json.dumps(data,ensure_ascii=False)+");});\n",encoding='utf8');project.write_text("import {makeProject} from '@motion-canvas/core';\nimport scene from './ai-"+id+"?scene';\nexport default makeProject({scenes:[scene]});\n",encoding='utf8')
  evidence=[{'path':rel(image),'sha256':sha(image),'purpose':'Inspected independent gameplay screenshot: artwork is actual existing game art, not labeled AI-generated.'}];name=f'vs-d2-ai-{id}-v2'
  c={'id':id,'paragraph':i,'scene':ps['scene'],'kind':'explanation','startFrame':pos,'frames':n,'source':f'shared/output/motion-canvas/{name}.mp4','diagram':data,'entry':rel(entry),'renderer':'Motion Canvas','visualEvidence':evidence,'observedRole':ps['ko']};cuts.append(c);pos+=n
  jobs.append({'id':id,'name':name,'frames':n,'route':'/src/projects/'+P.name+f'/ai-{id}-project.ts','visualInputs':evidence,'visualModule':'ai-visuals.tsx'})
 for i in range(1,61):
  target=actual[i];left=target
  for c in groups[i]:
   if c['kind']!='actual' or left<=0:continue
   n=min(left,c['frames']);add_actual(c,n);left-=n
  if left:add_extra(i,left)
  if lengths[i]>target:add_explain(i,lengths[i]-target)
 assert pos==t['bodyFrames'] and sum(c['frames'] for c in cuts if c['kind']=='actual')==t['actualFrames'],(pos,t['bodyFrames'],sum(c['frames'] for c in cuts if c['kind']=='actual'),t['actualFrames'],sum(lengths.values()),adjustments)
 for a,b in zip(cuts,cuts[1:]):assert a['startFrame']+a['frames']==b['startFrame']
 for c in cuts:c['observedRole']=t['paragraphs'][c['paragraph']-1]['ko']
 usage=[]
 for key in set(c['sourceId'] for c in cuts if c['kind']=='actual'):
  sourcecuts=[c for c in cuts if c.get('sourceId')==key];ranges=sorted((c['sourceStartFrame'],c['sourceStartFrame']+c['frames']) for c in sourcecuts)
  for a,b in zip(ranges,ranges[1:]):assert a[1]<=b[0],('Repeated footage',key,a,b)
  original=next(s for s in base['sourceUsage'] if s['source']==key);s=copy.deepcopy(original);s['rangesFrames']=ranges;s['totalSeconds']=sum(z-a for a,z in ranges)/60;usage.append(s)
 plan={k:v for k,v in base.items() if k not in ['cuts','sourceUsage','visualOnlyRevision','annotationRepair']};plan.update(revision='ai-copyright-awareness-v2',timingSha256=sha(L/'timing.json'),bodyFrames=t['bodyFrames'],actualFrames=t['actualFrames'],explanationFrames=t['explanationFrames'],totalFrames=t['bodyFrames']+720,ratioErrorFrames=abs(t['actualFrames']-t['bodyFrames']*.6),sourceVoiceSha256=t['sourceSha256'],spokenScriptSha256=sha(P/'script/narration.spoken-ko.json'),cuts=cuts,sourceUsage=usage,revisionRatioAdjustments=adjustments,finalHumanReview='pending',allocationLocked=True)
 for c in cuts:
  old=next((x for x in base['cuts'] if x['id']==c['id']),None)
  keys=['kind','source','sourceStartFrame','frames','sourceCrop','annotation']
  if old and all(old.get(k)==c.get(k) for k in keys):
   source=B/'cuts'/(old['id']+'.mp4');dest=L/'cuts'/(c['id']+'.mp4');linked(source,dest)
   signature={'cut':c,'inputSha256':sha(R/c['source']),'codec':'x264-fast-crf18-fhd60-bt709-v1'};wr(dest.with_suffix('.json'),{'signature':signature,'sha256':sha(dest),'geometry':[1920,1080,60],'frames':c['frames'],'reuseEvidence':{'baselineCut':rel(source),'baselineHash':sha(source),'relevantVisualInputsIdentical':keys,'priorReview':'production/visual-direct-review.json before selected revision'},'pixelReview':'identical visual content reused; changed timeline joins reviewed in final'})
   reuse.append(c['id'])
   game=B/'cuts'/(c['id']+'-game.wav')
   if game.exists():linked(game,L/'cuts'/game.name)
 for key in ['branding','membership']:linked(B/'cuts'/(key+'.mp4'),L/'cuts'/(key+'.mp4'))
 wr(L/'edit-plan.json',plan);wr(P/'production/edit-plan.json',plan);wr(L/'diagrams.json',{'jobs':jobs});wr(L/'revision-cut-reuse.json',{'reusedCuts':reuse,'newOrChangedCuts':[c['id'] for c in cuts if c['id'] not in reuse],'newActualSourceRanges':newsource,'bodyFrames':pos,'ratio':{'actual':t['actualFrames'],'explanation':t['explanationFrames']},'noSourceLoopsOrRetiming':True})
 print(json.dumps({'seconds':pos/60,'actual':t['actualFrames']/60,'explanation':t['explanationFrames']/60,'cuts':len(cuts),'reused':len(reuse),'diagrams':len(jobs),'adjustments':adjustments},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
