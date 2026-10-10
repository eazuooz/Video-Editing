"""Preserve literal KO cues and balance EN wraps without dangling end words."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math,re
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
src=BASE/'caption-candidate-v3/captions.json';dest=BASE/'caption-candidate-v4';assert not dest.exists()
j=json.loads(src.read_text('utf-8'));j['schemaVersion']=4;j['preparedAt']=datetime.now(timezone.utc).isoformat()
j['previousCandidate']=str(src.relative_to(ROOT)).replace('\\','/');j['previousCandidateSha256']=hashlib.sha256(src.read_bytes()).hexdigest()
new=[];changes=[]
for p in j['paragraphs']:
 old=[r for r in j['en'] if (r['scene'],r['paragraph'])==(p['scene'],p['paragraph'])]
 start,end=old[0]['startSeconds'],old[-1]['endSeconds'];words=p['en'].split();N=len(words)
 greedy=[];part=[]
 for word in words:
  if part and len(' '.join(part+[word]))>78:greedy.append(part);part=[]
  part.append(word)
 if part:greedy.append(part)
 K=len(greedy)
 target=(len(p['en'])-(K-1))/K
 best={(0,0):(0,[])}
 for k in range(1,K+1):
  for b in range(1,N+1):
   opts=[]
   for a in range(b):
    prev=best.get((k-1,a))
    if prev is None:continue
    text=' '.join(words[a:b]);length=len(text)
    if length>78:continue
    score=prev[0]+(length-target)**2-(80 if re.search(r'[.!?]$',text) else 0)
    opts.append((score,prev[1]+[text]))
   if opts:best[(k,b)]=min(opts,key=lambda x:x[0])
 pieces=best[(K,N)][1];total=sum(map(len,pieces));cursor=start
 for piece in pieces:
  stop=cursor+(end-start)*len(piece)/total;assert stop-cursor>=.85,(p['scene'],p['paragraph'],piece,stop-cursor)
  new.append(dict(scene=p['scene'],paragraph=p['paragraph'],en=piece,startSeconds=cursor,endSeconds=stop,placement=old[0]['placement'],timingMethod='Independent translated complete paragraph, measured semantic span with balanced78-character wraps; candidate',timingApproved=False));cursor=stop
 changes.append(dict(scene=p['scene'],paragraph=p['paragraph'],old=[r['en'] for r in old],new=pieces,previousShortestSeconds=min(r['endSeconds']-r['startSeconds'] for r in old),currentShortestSeconds=(end-start)*min(map(len,pieces))/total))
 p['enCues']=len(pieces)
for i,r in enumerate(new,1):r['index']=i
j['en']=new;j['enCueCount']=len(new);j['englishWrapChanges']=changes
j['alignmentArtifactsDirectObservation']=[
 {'scene':'01-overview','paragraph':3,'observation':'Complete-context word selection includes previous sentence tail because a word estimate crosses the quiet paragraph boundary. Only matching literal current paragraph characters receive cue timing; no text repetition.'},
 {'scene':'07-state-not-base','paragraph':1,'observation':'Recognizer percentage glyph is omitted by alphanumeric normalization. Literal 퍼센트는 is retained; complete source transcript/proof remains authoritative, not an omitted-clause diagnosis.'},
 {'scene':'08-resources-and-actions','paragraph':2,'observation':'Preserved original-prefix context contains an old p3 onset estimate; literal matching excludes it. All current p2 cues end before the exact preserved19.86s prefix endpoint. Newp3 starts19.96s after the owned0.1s quiet gap.'}]
assert max(r['sourceSpeechEnd'] for r in j['ko'] if r['scene']=='08-resources-and-actions' and r['paragraph']==2)<=19.86
assert max(r['sourceSpeechEnd'] for r in j['ko'] if r['scene']=='09-condition-and-time' and r['paragraph']==2)<=19.19
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
dest.mkdir()
for lang,rows in [('ko',j['ko']),('en',new)]:(dest/f'candidate.{lang}.srt').write_text('\n\n'.join(f'{r["index"]}\n{stamp(r["startSeconds"])} --> {stamp(r["endSeconds"])}\n{r[lang]}'for r in rows)+'\n','utf-8')
(dest/'captions.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(ko=len(j['ko']),en=len(new),minimumEnglishDuration=min(r['endSeconds']-r['startSeconds']for r in new),koUnchanged=True,approved=False)))
