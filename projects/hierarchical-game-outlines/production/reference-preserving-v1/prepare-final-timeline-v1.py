"""One measured cut, voice placement, caption and animation timeline."""
from pathlib import Path
import json,re,hashlib,datetime,difflib,math
import numpy as np,soundfile as sf,psutil
from captions import wrap,FONT
P=Path(__file__).resolve().parent;ROOT=P.parents[3];MC=ROOT/'motion-canvas/src/projects/hierarchical-game-outlines'
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (P/'final-timeline-v1.json').exists()
whole=read(P/'voice-asr-v1.json');ctx=read(P/'voice-contexts-v1.json')
for s in [whole,ctx]:
 assert s['exitCode']==0
 try:assert abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.01
 except psutil.NoSuchProcess:pass
ko=read(P/'narration.ko.json')['scenes'];en=read(P/'narration.en.json')['scenes']
norm=lambda s:re.sub(r'[^가-힣a-zA-Z0-9]','',s).lower()
sources={'menu':dict(path='shared/assets/game-footage/hierarchical-game-outlines-smash/bkH5znXN2WQ.mp4',sha256='1f92af66df55ca423dea728a0b2656ec52963242ce9faa52e96baa399eef5740',nativeFps=60),
 'play':dict(path='shared/assets/game-footage/hierarchical-game-outlines-smash/EyaXufIsK48.mp4',sha256='1f1ff2ad29fe3ff271c9bd612e50d62f982a68510310cc05349f4f6c51bfedee',nativeFps=30)}
# All intervals are unique and normal speed. Recorded menu manipulation counts as action;
# the diagram-dominated in-game How To Play guide is explicitly excluded.
cuts={
'01':[('ex',0,420),('menu',270,1200)],
'02':[('menu',294,780),('ex',0,450),('menu',327,1020)],
'03':[('menu',474,300),('menu',503,540),('ex',0,660),('menu',512,1171)],
'04':[('menu',559,720),('ex',0,480),('play',25,1080)],
'05':[('ex',0,1887)],'06':[('ex',0,1565)],
'07':[('play',48,648),('ex',0,480),('play',58.8,822)],
'08':[('menu',403,1442),('ex',0,540)]}
# Place complete paragraphs at these scene-relative seconds; untouched samples between
# paragraphs are retained and only an additional quiet observation gap is inserted.
requested={'01':[0,4.56,14.24],'02':[0,11.58,20.7],'03':[0,14.0,22.0],
 '04':[0,12.0,21.1],'05':None,'06':None,'07':None,'08':[0,8.16,1442/60]}
timeline=dict(createdAt=now(),fps=60,timebase=90000,introFrames=120,outroFrames=600,sources=sources,scenes=[],pieces=[],captionsKo=[],captionsEn=[],paragraphs=[],humanListening=False,publicRightsApproved=False,ratioScope='body only',sourceClassification='independent-gameplay only; research reference media excluded')
animation=[];frame=120
for sc,es,ar in zip(ko,en,whole['results']):
 sid=sc['id'];voice=P/f'narration/chunks/{sid}-scene.wav';x,sr=sf.read(voice,dtype='float32');assert sr==24000
 words=ar['words']
 if sid=='05':words=[w for w in words if not(w['text'].strip()=='확인' and w['timestamp'][0]==25.18)]
 if sid=='06':words=[dict(w,text=w['text'].replace('개어','개요')) for w in words]
 actual='';times=[]
 for w in words:
  z=norm(w['text']);actual+=z;times += [w['timestamp']]*len(z)
 expected=''.join(map(norm,sc['lines']));mapped={}
 for b in difflib.SequenceMatcher(None,expected,actual,autojunk=False).get_matching_blocks():
  for i in range(b.size):mapped[b.a+i]=times[b.b+i]
 assert len(mapped)/len(expected)>.96,(sid,len(mapped),len(expected))
 # Fill only ASR orthographic alternatives between nearby matched words.
 for i in range(len(expected)):
  if i not in mapped:
   left=max((k for k in mapped if k<i),default=min(mapped));right=min((k for k in mapped if k>i),default=max(mapped))
   mapped[i]=[mapped[left][1],mapped[right][0]] if mapped[left][1]<=mapped[right][0] else mapped[left]
 off=0;paragraphs=[]
 for line in sc['lines']:
  n=len(norm(line));paragraphs.append(dict(text=line,start=mapped[off][0],end=mapped[off+n-1][1],charStart=off));off+=n
 desired=requested[sid] or [p['start'] for p in paragraphs]
 shifts=[round((want-p['start'])*sr)/sr for want,p in zip(desired,paragraphs)]
 assert shifts[0]==0 and shifts==sorted(shifts),(sid,shifts)
 boundaries=[0]
 for i in [1,2]:
  a,b=paragraphs[i-1]['end'],paragraphs[i]['start'];mid=round((a+b)/2*sr)
  # A 4ms RMS minimum strictly inside the observed complete-paragraph gap.
  lo=max(round(a*sr),mid-600);hi=min(round(b*sr),mid+600)
  candidates=list(range(lo+48,hi-48,24)) or [mid]
  k=min(candidates,key=lambda z:float(np.mean(x[z-48:z+48]**2)))
  boundaries.append(k)
 boundaries.append(len(x))
 frames=sum(n for _,_,n in cuts[sid]);duration=frames/60
 assert len(x)/sr+shifts[-1]<=duration+.001,(sid,duration,len(x)/sr,shifts)
 placements=[]
 for i in range(3):placements.append(dict(sourceStartSample=boundaries[i],sourceEndSample=boundaries[i+1],outputStartSample=boundaries[i]+round(shifts[i]*sr),additionalShiftSeconds=shifts[i]))
 row=dict(id=sid,title=sc['title'],startFrame=frame,frames=frames,voicePath=voice.relative_to(ROOT).as_posix(),voiceSha256=sha(voice),voiceSamples=len(x),voiceRate=sr,placements=placements,paragraphs=[])
 local=0;exstart=None;exframes=0
 for kind,start,n in cuts[sid]:
  piece=dict(scene=sid,kind=kind,startFrame=frame+local,localStartFrame=local,frames=n,sourceStart=start)
  if kind=='ex':exstart=local;exframes=n;piece['path']=f'projects/hierarchical-game-outlines/production/reference-preserving-v1/white-{sid}-v6.mp4'
  else:piece['path']=sources[kind]['path'];piece['sourceEnd']=start+n/60
  timeline['pieces'].append(piece);local+=n
 for pi,(p,eline) in enumerate(zip(paragraphs,es['lines'])):
  start=(frame/60+p['start']+shifts[pi]);end=frame/60+p['end']+shifts[pi]
  pr=dict(scene=sid,paragraph=pi+1,start=round(start,3),end=round(end,3),koText=p['text'],enText=eline,koCues=[],enCues=[])
  # Prefer sentence/clause endings, splitting only to fit the fixed font and width.
  def split_text(text):
   parts=re.split(r'(?<=[.!?])\s+',text);out=[]
   for part in parts:
    if len(wrap(part))<=2:out.append(part);continue
    ws=part.split();cur=''
    for word in ws:
     test=(cur+' '+word).strip()
     if len(wrap(test))>2:out.append(cur);cur=word
     else:cur=test
    if cur:out.append(cur)
   return out
  kparts=split_text(p['text']);offset=p['charStart']
  for part in kparts:
   n=len(norm(part));a=frame/60+mapped[offset][0]+shifts[pi];b=frame/60+mapped[offset+n-1][1]+shifts[pi]
   cue=dict(scene=sid,paragraph=pi+1,text=part,startFrame=max(frame,round(a*60)),endFrame=min(frame+frames,round(b*60)))
   assert cue['endFrame']>cue['startFrame'];timeline['captionsKo'].append(cue);pr['koCues'].append(len(timeline['captionsKo']));offset+=n
  # Independent English phrasing spans the same complete semantic paragraph.
  eparts=split_text(eline);weights=[len(p) for p in eparts];total=sum(weights);run=0
  ka=timeline['captionsKo'][pr['koCues'][0]-1]['startFrame'];kb=timeline['captionsKo'][pr['koCues'][-1]-1]['endFrame']
  pr['start']=round(ka/60,3);pr['end']=round(kb/60,3)
  for part,w in zip(eparts,weights):
   a=round(ka+(kb-ka)*run/total);run+=w;b=round(ka+(kb-ka)*run/total)
   timeline['captionsEn'].append(dict(scene=sid,paragraph=pi+1,text=part,startFrame=a,endFrame=b));pr['enCues'].append(len(timeline['captionsEn']))
  row['paragraphs'].append(dict(startSeconds=p['start']+shifts[pi],endSeconds=p['end']+shifts[pi],sourceStart=p['start'],sourceEnd=p['end']))
  timeline['paragraphs'].append(pr)
 # The displayed explanation may accompany part of a paragraph. Keep reveals inside it
 # and align to observed current speech; no generic fixed nine-second scene timing.
 animstarts=[max(0,min(exframes-90,round((p['start']+shifts[i])*60)-exstart)) for i,p in enumerate(paragraphs)]
 if sid in ['02','03','04','07','08']:animstarts=[0,round(exframes*.30),round(exframes*.70)]
 anim=dict(id=sid,frames=exframes,paragraphStarts=animstarts,sceneStartFrame=frame,explanationStartFrame=frame+exstart)
 if sid=='05':anim.update(foldAt=5.5,expandAt=8.02,moveAt=14.36,levelAt=19.2)
 animation.append(anim);timeline['scenes'].append(row);frame+=frames
timeline['bodyFrames']=frame-120;timeline['totalFrames']=frame+600;timeline['actualFrames']=sum(p['frames'] for p in timeline['pieces'] if p['kind']!='ex');timeline['explanationFrames']=sum(p['frames'] for p in timeline['pieces'] if p['kind']=='ex')
assert abs(timeline['actualFrames']-.6*timeline['bodyFrames'])<=1
for key in ['captionsKo','captionsEn']:
 for i,c in enumerate(timeline[key]):
  if i:assert c['startFrame']>=timeline[key][i-1]['endFrame']
  assert len(wrap(c['text']))<=2
write(P/'final-timeline-v1.json',timeline)
old=MC/'reference-reel-plan-v1.json';backup=P/'reference-reel-plan-preflight-backup.json';assert not backup.exists();backup.write_bytes(old.read_bytes())
write(old,dict(scope='measured current eight-scene final explanation timing',timelineSha256=sha(P/'final-timeline-v1.json'),rows=animation))
def tc(frame):
 ms=round(frame*1000/60);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
for lang,key in [('ko','captionsKo'),('en','captionsEn')]:
 (P/f'captions.{lang}.srt').write_text('\n\n'.join(f'{i+1}\n{tc(c["startFrame"])} --> {tc(c["endFrame"])}\n'+ '\n'.join(wrap(c['text'])) for i,c in enumerate(timeline[key]))+'\n',encoding='utf-8')
print(json.dumps({k:timeline[k] for k in ['bodyFrames','totalFrames','actualFrames','explanationFrames']},ensure_ascii=False))
print('KO/EN cues',len(timeline['captionsKo']),len(timeline['captionsEn']))
for s in timeline['scenes']:print(s['id'],s['startFrame']/60,s['frames']/60,[(p['sourceStartSample'],p['sourceEndSample'],p['additionalShiftSeconds']) for p in s['placements']])
