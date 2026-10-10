"""Literal current37-paragraph KOEN cue candidates from reviewed ASR clocks.

Current PCM bounds and placements are authoritative. Recognizer estimates
provide word timing only; this neither reruns recognition nor approves cues.
"""
from pathlib import Path
from datetime import datetime,timezone
from difflib import SequenceMatcher
from PIL import ImageFont
import hashlib,json,re,math
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
norm=lambda s:''.join(c.lower() for c in s if c.isalnum())
DEST=BASE/'caption-candidate-v3';assert not DEST.exists()
PP=BASE/'measured-timeline-candidate-v3.json';plan=read(PP);voices=read(ROOT/plan['currentVoiceSelection'])
assert sha(ROOT/plan['currentVoiceSelection'])==plan['currentVoiceSelectionSha256']
scripts={lang:{s['id']:s for s in read(ROOT/plan['current'+lang.title()+'Script'])['scenes']}for lang in ('ko','en')}
boundaries={r['id']:r['paragraphStarts'] for r in read(BASE/'measured-paragraph-boundary-direct-review-v2.json')['rows']}
boundaries['08-resources-and-actions']=[0,9.57,19.96];boundaries['09-condition-and-time']=[0,9.97,19.29]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
paragraphs=[];ko=[];en=[];provenance=[];artifacts=[];short=[]
def words_for(sid,pi):
 if sid.startswith(('08-','09-')) and pi==3:
  path=BASE/'voice-clarity-v2/asr'/f'{sid}-p3-independent.json';j=read(path)
  offset=boundaries[sid][2]-.25;assert j['exactWholeReplacementBytesMatched']
 elif pi>=2:
  path=BASE/'current-contexts-asr-v1'/f'{sid}-complete-p2-to-end.json';j=read(path)
  offset=j['startSample']/24000-j['zeroPaddingSamplesEachSide']/24000
  assert sha(ROOT/j['sourcePath'])==j['sourceSha256'] and j['exactSourceSampleBytesMatched']
 else:
  path=BASE/'current-whole-asr-v1'/f'{sid}.json';j=read(path);offset=0
  assert sha(ROOT/j['sourcePath'])==j['sourceSha256']
 assert j.get('expectedWasRecognizerPrompt') is False
 ev=dict(path=rel(path),sha256=sha(path),sourcePath=j['sourcePath'],sourceSha256=j['sourceSha256'],offsetSeconds=offset,expectedWasRecognizerPrompt=False)
 provenance.append(ev);words=[]
 for w in j['words']:
  a,b=w['timestamp']
  if a is None or b is None or b<=a or not norm(w['text']):artifacts.append(dict(scene=sid,paragraph=pi,path=rel(path),word=w));continue
  words.append(dict(text=w['text'],timestamp=[a+offset,b+offset]))
 return words,ev
def seq(words):
 raw='';times=[]
 for w in words:
  tok=norm(w['text']);a,b=w['timestamp']
  for i,c in enumerate(tok):raw+=c;times.append((a+(b-a)*i/len(tok),a+(b-a)*(i+1)/len(tok)))
 # Number spelling is alignment-only; literal script remains unchanged.
 out='';clocks=[];pos=0
 for m in re.finditer(r'\d+',raw):
  out+=raw[pos:m.start()];clocks+=times[pos:m.start()]
  expanded={'2':'두','6':'여섯'}.get(m.group(),m.group());a,b=times[m.start()][0],times[m.end()-1][1]
  for i,c in enumerate(expanded):out+=c;clocks.append((a+(b-a)*i/len(expanded),a+(b-a)*(i+1)/len(expanded)))
  pos=m.end()
 out+=raw[pos:];clocks+=times[pos:];return out,clocks
def output_time(sid,seconds,edge):
 n=seconds*24000;parts=sorted([p for p in plan['voicePlacements']if p['voiceId']==sid],key=lambda p:p['sourceStartSample'],reverse=edge=='start')
 for p in parts:
  if p['sourceStartSample']-1e-4<=n<=p['sourceEndSampleExclusive']+1e-4:return (p['startSample']+n-p['sourceStartSample'])/24000,p['id']
 raise RuntimeError((sid,seconds,'Outside exact PCM placement'))
for voice in voices['scenes']:
 sid=voice['id'];starts=boundaries[sid];bounds=starts+[voice['samples']/24000]
 for pi,(literal,english) in enumerate(zip(scripts['ko'][sid]['lines'],scripts['en'][sid]['lines']),1):
  pa,pb=bounds[pi-1:pi+1];words,ev=words_for(sid,pi)
  use=[w for w in words if w['timestamp'][1]>pa and w['timestamp'][0]<pb]
  recognized,times=seq(use);expected=norm(literal);matcher=SequenceMatcher(None,expected,recognized,autojunk=False)
  assert matcher.ratio()>=.87,(sid,pi,matcher.ratio(),recognized)
  mapped={a+i:times[b+i]for a,b,n in matcher.get_matching_blocks()for i in range(n)};keys=sorted(mapped)
  for i in range(len(expected)):
   if i in mapped:continue
   lo=max((k for k in keys if k<i),default=-1);hi=min((k for k in keys if k>i),default=len(expected))
   a=mapped[lo][1]if lo>=0 else pa;b=mapped[hi][0]if hi<len(expected)else pb
   a,b=sorted((a,b));step=(b-a)/(hi-lo-1);mapped[i]=(a+(i-lo-1)*step,a+(i-lo)*step)
  mapped={i:(max(pa,min(a,pb)),max(pa,min(b,pb)))for i,(a,b)in mapped.items()}
  tokens=list(re.finditer(r'\S+',literal));N=len(tokens)
  def piece(a,b):
   text=literal[tokens[a].start():tokens[b-1].end()]
   ia=len(norm(literal[:tokens[a].start()]));ib=len(norm(literal[:tokens[b-1].end()]))
   t0=min(mapped[k][0]for k in range(ia,ib));t1=max(mapped[k][1]for k in range(ia,ib))
   return text,t0,t1
  # A measured width and18 raw characters conservatively protect every game
  # HUD. Dynamic partitioning avoids a short trailing word when a balanced
  # split can retain the exact text and respect those same limits.
  cost=[math.inf]*(N+1);choice=[None]*(N+1);cost[N]=0
  for a in range(N-1,-1,-1):
   for b in range(a+1,N+1):
    txt,t0,t1=piece(a,b)
    if len(txt)>18 or font.getlength(txt)>880:
     if b==a+1:raise RuntimeError(('Unbreakable wide token',sid,pi,txt))
     break
    if t1<=t0:continue
    dur=t1-t0
    crossing=len(re.findall(r'[.!?]\s',txt))*18
    ending_bonus=2 if re.search(r'[.!?]$',txt) else 0
    penalty=10+max(0,.75-dur)*50+max(0,dur-3.8)*3+crossing-ending_bonus+cost[b]
    if penalty<cost[a]:cost[a]=penalty;choice[a]=b
  assert choice[0]is not None
  cues=[];a=0
  while a<N:
   b=choice[a];txt,t0,t1=piece(a,b);sa,pl=output_time(sid,t0,'start');sb,ple=output_time(sid,t1,'end');assert pl==ple and sb>sa,(sid,pi,txt,pl,ple)
   cue=dict(scene=sid,paragraph=pi,ko=txt,lines=[txt],sourceSpeechStart=t0,sourceSpeechEnd=t1,startSeconds=sa,endSeconds=sb,placement=pl,
            textWidthPx=font.getlength(txt),characters=len(txt),center=[960,970],fontPx=48,style='boxed-white-forest-v1',timingApproved=False,pixelsApproved=False)
   ko.append(cue);cues.append(cue)
   if sb-sa<.65:short.append(dict(scene=sid,paragraph=pi,text=txt,seconds=sb-sa,needsDirectReadabilityReview=True))
   a=b
  assert norm(' '.join(c['ko']for c in cues))==expected
  para_start=min(c['startSeconds']for c in cues);para_end=max(c['endSeconds']for c in cues)
  enpieces=[];cur=[]
  for word in english.split():
   if cur and len(' '.join(cur+[word]))>78:enpieces.append(' '.join(cur));cur=[]
   cur.append(word)
  if cur:enpieces.append(' '.join(cur))
  total=sum(len(x)for x in enpieces);cursor=para_start
  for part in enpieces:
   stop=cursor+(para_end-para_start)*len(part)/total;en.append(dict(scene=sid,paragraph=pi,en=part,startSeconds=cursor,endSeconds=stop,placement=cues[0]['placement'],timingMethod='Independent translated complete paragraph, measured semantic span weighted wrap; candidate',timingApproved=False));cursor=stop
  assert norm(' '.join(enpieces))==norm(english)
  paragraphs.append(dict(scene=sid,paragraph=pi,ko=literal,en=english,sourceStartSeconds=pa,sourceEndSeconds=pb,characterMatch=matcher.ratio(),recognizedCompleteParagraph=recognized,
    recognizedWords=use,alignmentOpcodes=matcher.get_opcodes(),evidence=ev,sourceWordTimestampsAreEstimates=True,currentPcmBoundsAuthoritative=True,koCues=len(cues),enCues=len(enpieces),literalTextsRetained=True,allCueTimingApproved=False))
repairs=[]
for lang,rows in [('ko',ko),('en',en)]:
 rows.sort(key=lambda r:(r['startSeconds'],r['endSeconds']))
 for left,right in zip(rows,rows[1:]):
  if left['endSeconds']>right['startSeconds']+.001:
   assert left['scene']==right['scene'] and left['paragraph']==right['paragraph']
   old=(left['endSeconds'],right['startSeconds']);mid=sum(old)/2
   assert left['startSeconds']<mid<right['endSeconds']
   left['endSeconds']=right['startSeconds']=mid;repairs.append(dict(language=lang,scene=left['scene'],paragraph=left['paragraph'],left=left[lang],right=right[lang],original=old,repairedBoundary=mid,needsDirectClockReview=True))
 for i,row in enumerate(rows,1):row['index']=i
assert len(paragraphs)==37
for p in paragraphs:
 for lang,rows in [('ko',ko),('en',en)]:assert norm(' '.join(r[lang]for r in rows if r['scene']==p['scene'] and r['paragraph']==p['paragraph']))==norm(p[lang])
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
DEST.mkdir()
for lang,rows in [('ko',ko),('en',en)]:(DEST/f'candidate.{lang}.srt').write_text('\n\n'.join(f'{r["index"]}\n{stamp(r["startSeconds"])} --> {stamp(r["endSeconds"])}\n{r[lang]}'for r in rows)+'\n','utf-8')
proof=dict(schemaVersion=3,preparedAt=datetime.now(timezone.utc).isoformat(),plan=rel(PP),planSha256=sha(PP),paragraphs=paragraphs,ko=ko,en=en,koCueCount=len(ko),enCueCount=len(en),
 asrProvenance=provenance,artifacts=artifacts,shortCueCandidates=short,overlapClockRepairs=repairs,alignmentOnlyNumberSpelling={'2':'두','6':'여섯'},
 allCurrent37KoEnParagraphsRetained=True,all35UnchangedParagraphsPreserved=True,captionCenter=[960,970],fontPx=48,maxLines=1,maxRawCharacters=18,maxMeasuredTextWidthPx=880,
 allCueTimingApproved=False,allCuePixelsReviewed=False,finalTimingApproved=False,mixedAsrApproved=False,finalQa=False,newTtsJobs=0,newAsrJobs=0,newMedia=0,newRasterGitAdditions=0,
 humanListening='pending',humanPronunciation='pending')
(DEST/'captions.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(paragraphs=37,ko=len(ko),en=len(en),minimumMatch=min(p['characterMatch']for p in paragraphs),short=short,clockRepairs=repairs,approved=False),ensure_ascii=False))
