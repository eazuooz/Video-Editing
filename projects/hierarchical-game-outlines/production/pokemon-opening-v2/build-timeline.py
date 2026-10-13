"""Changed narration only; exact retained paragraph PCM and visual assets."""
from pathlib import Path
import json,re,hashlib,datetime,difflib,copy,math
import numpy as np,soundfile as sf
from captions import wrap
P=Path(__file__).resolve().parent;R=P.parents[3];N=P.parent/'reference-preserving-v1';MC=R/'motion-canvas/src/projects/hierarchical-game-outlines'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (P/'final-timeline-v1.json').exists()
assert read(P/'voice-direct-review.json')['generatedAudioCompleteForEditing']
old=read(N/'final-timeline-v1.json');ko=read(P/'narration.ko.json')['scenes'];en=read(P/'narration.en.json')['scenes'];whole=read(P/'voice-current-asr.json')
assert whole['exitCode']==0
norm=lambda s:re.sub(r'[^가-힣a-zA-Z0-9]','',s).lower()
generated={r['key']:r for r in read(P/'voice-current-inputs.json')['completed']}
asr={r['id']:r for r in whole['results']}
scenes={r['id']:r for r in old['scenes']}
def split_text(text):
 out=[]
 for part in re.split(r'(?<=[.!?])\s+',text):
  if len(wrap(part))<=2:out.append(part);continue
  cur=''
  for word in part.split():
   test=(cur+' '+word).strip()
   if len(wrap(test))>2:out.append(cur);cur=word
   else:cur=test
  if cur:out.append(cur)
 return out
def align(key,lines):
 ar=asr[key];actual='';times=[]
 for w in ar['words']:
  z=norm(w['text']);actual+=z;times += [w['timestamp']]*len(z)
 expected=''.join(map(norm,lines));mapped={}
 for b in difflib.SequenceMatcher(None,expected,actual,autojunk=False).get_matching_blocks():
  for i in range(b.size):mapped[b.a+i]=times[b.b+i]
 assert len(mapped)/len(expected)>.96,(key,len(mapped),len(expected))
 for i in range(len(expected)):
  if i not in mapped:
   left=max((k for k in mapped if k<i),default=min(mapped));right=min((k for k in mapped if k>i),default=max(mapped));mapped[i]=[mapped[left][1],mapped[right][0]] if mapped[left][1]<=mapped[right][0] else mapped[left]
 off=0;ps=[]
 for line in lines:
  z=len(norm(line));ps.append(dict(start=mapped[off][0],end=mapped[off+z-1][1],offset=off));off+=z
 return mapped,ps
alignments={};voiceRows={};splice=[];d=P/'current-narration';d.mkdir()
for s in ko:
 sid=s['id'];prev=scenes.get(sid)
 if sid in ['01','01a']:
  f=R/generated[sid+'-scene']['path'] if sid+'-scene' in generated else R/next(r['path'] for r in generated.values() if r['path'].endswith('/'+sid+'-scene.wav'))
  x,sr=sf.read(f,dtype='int16');m,pp=align(sid,s['lines']);alignments[sid]=(m,pp)
  voiceRows[sid]=dict(path=f,samples=len(x),sourceParagraphs=[(q['start'],q['end']) for q in pp],boundaries=[0,len(x)],placements=[dict(sourceStartSample=0,sourceEndSample=len(x),outputStartSample=0,additionalShiftSeconds=0)])
 elif sid in ['03','04','05','06']:
  f=R/prev['voicePath'];assert sha(f)==prev['voiceSha256'];voiceRows[sid]=dict(path=f,samples=prev['voiceSamples'],placements=copy.deepcopy(prev['placements']),sourceParagraphs=[(q['sourceStart'],q['sourceEnd']) for q in prev['paragraphs']])
 else:
  idx=1 if sid=='02' else 0;key=sid+'p'+str(idx+1).zfill(2);g=R/next(r['path'] for r in generated.values() if r['path'].endswith('/'+key+'-scene.wav'))
  orig=R/prev['voicePath'];x,sr=sf.read(orig,dtype='int16');y,yr=sf.read(g,dtype='int16');assert sr==yr==24000
  assert sha(orig)==prev['voiceSha256']
  a=prev['placements'][idx]['sourceStartSample'];b=prev['placements'][idx]['sourceEndSample'];gap=np.zeros(2880,dtype='int16')
  pieces=[x[:a],gap if a else np.zeros(0,dtype='int16'),y,gap,x[b:]];z=np.concatenate(pieces);startNew=a+(2880 if a else 0);startRetained=startNew+len(y)+2880;delta=startRetained-b
  dest=d/f'{sid}-scene.wav';sf.write(dest,z,24000,subtype='PCM_16');verify,vr=sf.read(dest,dtype='int16');assert np.array_equal(verify[:a],x[:a]) and np.array_equal(verify[startRetained:],x[b:])
  m,pp=align(key,[s['lines'][idx]]);alignments[sid]=(m,pp)
  sourceParagraphs=[];boundaries=[0]
  for i,q in enumerate(prev['paragraphs']):
   if i==idx:sourceParagraphs.append((startNew/24000+pp[0]['start'],startNew/24000+pp[0]['end']))
   else:sourceParagraphs.append((q['sourceStart']+(delta/24000 if i>idx else 0),q['sourceEnd']+(delta/24000 if i>idx else 0)))
  for i in [1,2]:
   oldB=prev['placements'][i]['sourceStartSample'];boundaries.append(startNew if i==idx else oldB+delta if i>idx else oldB)
  boundaries.append(len(z));placements=[]
  for i,(pa,pb) in enumerate(sourceParagraphs):
   desired=prev['paragraphs'][i]['startSeconds']
   shift=max(0,desired-pa) if i!=idx else 0
   # Keep earlier observed paragraphs fixed when the shorter replacement permits it.
   if sid=='08' and i==1:shift=0
   placements.append(dict(sourceStartSample=boundaries[i],sourceEndSample=boundaries[i+1],outputStartSample=boundaries[i]+round(shift*24000),additionalShiftSeconds=round(shift*24000)/24000))
  for i in range(1,3):assert placements[i]['outputStartSample']>=placements[i-1]['outputStartSample']+placements[i-1]['sourceEndSample']-placements[i-1]['sourceStartSample'],(sid,placements)
  assert max(a['outputStartSample']+a['sourceEndSample']-a['sourceStartSample'] for a in placements)<=prev['frames']*400,(sid,len(z))
  voiceRows[sid]=dict(path=dest,samples=len(z),placements=placements,sourceParagraphs=sourceParagraphs,newParagraph=idx,newStartSeconds=startNew/24000)
  splice.append(dict(scene=sid,oldPath=orig.relative_to(R).as_posix(),oldSha256=sha(orig),newRequest=g.relative_to(R).as_posix(),newRequestSha256=sha(g),oldReplacedRange=[a,b],newRange=[startNew,startNew+len(y)],oldPrefixSamples=a,oldSuffixSamples=len(x)-b,unchangedPrefixExact=True,unchangedSuffixExact=True,quietInsertedSamples=(2880 if a else 0)+2880,combinedPath=dest.relative_to(R).as_posix(),combinedSha256=sha(dest)))
timeline=dict(createdAt=now(),fps=60,timebase=90000,introFrames=120,outroFrames=600,sources=copy.deepcopy(old['sources']),scenes=[],pieces=[],captionsKo=[],captionsEn=[],paragraphs=[],humanListening=False,publicRightsApproved=False,ratioScope='body only',sourceClassification='independent-gameplay only; research reference media excluded',previousTimelineSha256=sha(N/'final-timeline-v1.json'))
pokemon='shared/assets/game-footage/hierarchical-pokemon/D1SrSFZrV7A-480-1500.mp4';timeline['sources']['pokemon']=dict(path=pokemon,sha256=sha(R/pokemon),nativeFps='60000/1001',originalWindowStartSeconds=480)
newcuts={'01':[('pokemon',524,240),('ex',0,360),('pokemon',528,660)],'01a':[('ex',0,540),('pokemon',539,480),('ex',9,300),('pokemon',547,990)]}
visuals={x['cut']:x['path'] for x in read(N/'visuals-execution-v1.json')['completed'] if 'cut' in x}
visuals[8]=(N/'pieces-local/08-03-menu-v2.mp4').relative_to(R).as_posix()
frame=120
for sc,es in zip(ko,en):
 sid=sc['id'];v=voiceRows[sid];prev=scenes.get(sid);local=0
 if sid in newcuts:
  for kind,src,n in newcuts[sid]:
   path=pokemon if kind=='pokemon' else (P/f'white-{sid}.mp4').relative_to(R).as_posix();cut=dict(scene=sid,kind=kind,startFrame=frame+local,localStartFrame=local,frames=n,sourceStart=src,path=path)
   if kind=='pokemon':cut['sourceEnd']=src+n/60
   timeline['pieces'].append(cut);local+=n
 else:
  for i,cut0 in enumerate(old['pieces']):
   if cut0['scene']!=sid:continue
   cut=copy.deepcopy(cut0);cut['startFrame']=frame+cut['localStartFrame'];render=visuals.get(i,cut['path']);cut.update(reuseVisual=render,reuseVisualSha256=sha(R/render),previousCut=i);timeline['pieces'].append(cut);local+=cut['frames']
 row=dict(id=sid,title=sc['title'],startFrame=frame,frames=local,voicePath=v['path'].relative_to(R).as_posix(),voiceSha256=sha(v['path']),voiceSamples=v['samples'],voiceRate=24000,placements=v['placements'],paragraphs=[])
 for pi,(line,eline) in enumerate(zip(sc['lines'],es['lines'])):
  pa,pb=v['sourceParagraphs'][pi];shift=v['placements'][pi if len(v['placements'])>1 else 0]['additionalShiftSeconds'];ps=pa+shift;pe=pb+shift
  row['paragraphs'].append(dict(startSeconds=ps,endSeconds=pe,sourceStart=pa,sourceEnd=pb))
  pr=dict(scene=sid,paragraph=pi+1,start=round(frame/60+ps,3),end=round(frame/60+pe,3),koText=line,enText=eline,koCues=[],enCues=[])
  changed=sid in newcuts or pi==v.get('newParagraph',-1)
  if changed:
   m,pars=alignments[sid];para=pars[pi] if sid in newcuts else pars[0];offset=para['offset'];base=0 if sid in newcuts else v['newStartSeconds']
   for part in split_text(line):
    n=len(norm(part));ca=frame+round((base+m[offset][0]+shift)*60);cb=frame+round((base+m[offset+n-1][1]+shift)*60);assert cb>ca
    timeline['captionsKo'].append(dict(scene=sid,paragraph=pi+1,text=part,startFrame=ca,endFrame=cb));pr['koCues'].append(len(timeline['captionsKo']));offset+=n
   first=timeline['captionsKo'][pr['koCues'][0]-1]['startFrame'];last=timeline['captionsKo'][pr['koCues'][-1]-1]['endFrame'];parts=split_text(eline);weights=[len(t) for t in parts];run=0
   for part,w in zip(parts,weights):
    a=round(first+(last-first)*run/sum(weights));run+=w;b=round(first+(last-first)*run/sum(weights));timeline['captionsEn'].append(dict(scene=sid,paragraph=pi+1,text=part,startFrame=a,endFrame=b));pr['enCues'].append(len(timeline['captionsEn']))
  else:
   delta=frame-prev['startFrame']+round((ps-prev['paragraphs'][pi]['startSeconds'])*60)
   for lang in ['Ko','En']:
    for cc in old['captions'+lang]:
     if cc['scene']==sid and cc['paragraph']==pi+1:
      c=copy.deepcopy(cc);c['startFrame']+=delta;c['endFrame']+=delta;timeline['captions'+lang].append(c);pr[lang.lower()+'Cues'].append(len(timeline['captions'+lang]))
  timeline['paragraphs'].append(pr)
 assert max(p['outputStartSample']+p['sourceEndSample']-p['sourceStartSample'] for p in row['placements'])<=local*400
 timeline['scenes'].append(row);frame+=local
timeline.update(bodyFrames=frame-120,totalFrames=frame+600,actualFrames=sum(c['frames'] for c in timeline['pieces'] if not c['kind'].startswith('ex')),explanationFrames=sum(c['frames'] for c in timeline['pieces'] if c['kind'].startswith('ex')))
assert abs(timeline['actualFrames']-.6*timeline['bodyFrames'])<=1
for key in ['captionsKo','captionsEn']:
 for i,c in enumerate(timeline[key]):
  if i:assert c['startFrame']>=timeline[key][i-1]['endFrame'],(key,i)
  assert c['endFrame']>c['startFrame'] and len(wrap(c['text']))<=2
  assert not any(n in c['text'].lower() for n in ['사쿠라이','sakurai','마사히로','桜井'])
write(P/'current-voice-splice.json',dict(at=now(),splices=splice,unchangedWholeScenes=['03','04','05','06'],noNewTtsForUnchangedContent=True))
write(P/'final-timeline-v1.json',timeline)
a01=alignments['01'];ball=norm(ko[0]['lines'][0]).index('몬스터볼');flatHighlight=max(0,min(270,round((a01[0][ball][0]-4)*60)))
pp=alignments['01a'][1]
write(MC/'pokemon-opening-plan-v2.json',dict(scope='measured changed voice; source-time9..14 of document resumes at scene17..22 across native demonstration',timelineSha256=sha(P/'final-timeline-v1.json'),rows=[dict(id='01',frames=360,paragraphStarts=[0,flatHighlight,300]),dict(id='01a',frames=840,paragraphStarts=[0,round(pp[1]['start']*60),round((9+max(0,pp[2]['start']-17))*60)])]))
def tc(frame):
 ms=round(frame*1000/60);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
for lang,key in [('ko','captionsKo'),('en','captionsEn')]:
 (P/f'captions.{lang}.srt').write_text('\n\n'.join(f'{i+1}\n{tc(c["startFrame"])} --> {tc(c["endFrame"])}\n'+'\n'.join(wrap(c['text'])) for i,c in enumerate(timeline[key]))+'\n',encoding='utf-8')
print(json.dumps({k:timeline[k] for k in ['bodyFrames','totalFrames','actualFrames','explanationFrames']}));print('Cues',len(timeline['captionsKo']),len(timeline['captionsEn']));print('Current voice samples and unchanged retained regions verified.')
