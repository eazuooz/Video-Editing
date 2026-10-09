"""Candidate literal KOEN39 captions from existing reviewed ASR, no new model."""
from pathlib import Path
from datetime import datetime,timezone
from difflib import SequenceMatcher
from PIL import ImageFont
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix();norm=lambda s:''.join(c.lower() for c in s if c.isalnum())
DEST=BASE/'revision-balatro60-v2/caption-candidate-v3';assert not DEST.exists()
PLAN=BASE/'revision-balatro60-v2/measured-editorial-candidate-v3.json';plan=read(PLAN);voices=read(ROOT/plan['voiceSelection'])
assert sha(ROOT/plan['voiceSelection'])==plan['voiceSelectionSha256']
assert voices['currentCompleteVoiceApproved'] and not voices['finalMixedAsrApproved']
scripts={lang:{s['id']:s for s in read(BASE/f'revision-balatro60-v2/script/narration-v2.{lang}.json')['scenes']} for lang in ('ko','en')}
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
numeric={'27':'스물일곱','14096':'만사천구십육','17016':'만칠천십육','2920':'이천구백이십','141':'백사십일','7':'칠','3':'세','6':'육','560':'오백육십','1327':'천삼백이십칠','704':'칠백사','1200':'천이백'}
paragraphs=[];chunks=[];ko=[];en=[];provenance=[];artifacts=[];changes=[]
def asr(sid,voice):
 if sid.startswith('01-'):p=BASE/'revision-balatro60-v2/voice-whole-asr-v3/r01-overview.json'
 elif sid.startswith('10-'):p=BASE/'revision-balatro60-v2/voice-joined-asr-v3'/f'{sid}.json'
 elif sid.startswith(('04-','05-','07-','09-')):p=BASE/'revision-balatro60-v2/voice-joined-asr-v1'/f'{sid}.json'
 elif sid.startswith(('13-','14-','18-','19-','24-')):p=BASE/'revision-balatro60-v2/voice-whole-asr-v1'/f'r{sid}-p1.json'
 elif sid.startswith('08-'):p=BASE/'observation-candidates-contexts-asr-v3'/f'{sid}-complete-candidate-join.json'
 elif int(sid[:2])>=11:p=BASE/'observation-candidates-contexts-asr-v3'/f'{sid}-complete-independent.json'
 else:p=BASE/'current-whole-asr-v1'/f'{sid}.json'
 j=read(p);assert j['sourceSha256']==voice['sha256']
 assert j.get('expectedWasRecognizerPrompt') is False
 offset=j.get('startSample',0)/24000-j.get('zeroPaddingSamplesEachSide',0)/24000
 words=[]
 for w in j['words']:
  a,b=w['timestamp']
  if a is None or b is None or b<=a:
   artifacts.append(dict(scene=sid,path=rel(p),word=w,reason='Recognizer zero/empty timestamp; preserved, no actual-speech claim'));continue
  words.append(dict(text=w['text'],timestamp=[a+offset,b+offset]))
 provenance.append(dict(path=rel(p),sha256=sha(p),sourceSha256=j['sourceSha256'],offsetSeconds=offset,expectedWasRecognizerPrompt=False))
 return words,provenance[-1]
def sequence(words):
 raw='';clock=[]
 for w in words:
  token=norm(w['text']);a,b=w['timestamp']
  for i,c in enumerate(token):raw+=c;clock.append((a+(b-a)*i/len(token),a+(b-a)*(i+1)/len(token)))
 out='';times=[];pos=0
 for match in re.finditer(r'\d+',raw):
  out+=raw[pos:match.start()];times+=clock[pos:match.start()]
  token=match.group();expanded=numeric.get(token,token)
  a,b=clock[match.start()][0],clock[match.end()-1][1]
  for i,c in enumerate(expanded):out+=c;times.append((a+(b-a)*i/len(expanded),a+(b-a)*(i+1)/len(expanded)))
  pos=match.end()
 out+=raw[pos:];times+=clock[pos:]
 for token,literal in [('tspindouble','티스핀더블'),('backtoback','백투백')]:
  while token in out:
   a=out.index(token);b=a+len(token);ta,tb=times[a][0],times[b-1][1]
   expanded=[(ta+(tb-ta)*i/len(literal),ta+(tb-ta)*(i+1)/len(literal))for i in range(len(literal))]
   out=out[:a]+literal+out[b:];times=times[:a]+expanded+times[b:]
 return out,times
def convert(sid,t,edge='start'):
 sample=t*24000
 parts=sorted([p for p in plan['voicePlacements'] if p['voiceId']==sid],key=lambda p:p['sourceStartSample'],reverse=edge=='start')
 for p in parts:
  if p['sourceStartSample']-1e-4<=sample<=p['sourceEndSampleExclusive']+1e-4:
   return (p['startSample']+sample-p['sourceStartSample'])/24000,p['id']
 raise RuntimeError((sid,t,'outside placements'))
for voice in voices['scenes']:
 sid=voice['id'];words,evidence=asr(sid,voice)
 bounds=plan['paragraphBoundaries'].get(sid,[0,voice['samples']])
 assert len(bounds)==len(scripts['ko'][sid]['lines'])+1
 for pi,(literal,english) in enumerate(zip(scripts['ko'][sid]['lines'],scripts['en'][sid]['lines']),1):
  pa0,pb0=bounds[pi-1]/24000,bounds[pi]/24000
  use=[w for w in words if w['timestamp'][1]>pa0 and w['timestamp'][0]<pb0]
  recognized,times=sequence(use);expected=norm(literal);matcher=SequenceMatcher(None,expected,recognized,autojunk=False)
  assert matcher.ratio()>=.84,(sid,pi,matcher.ratio(),recognized)
  mapped={a+i:times[b+i] for a,b,n in matcher.get_matching_blocks() for i in range(n)};keys=sorted(mapped);exact=len(keys)
  for i in range(len(expected)):
   if i in mapped:continue
   lo=max((k for k in keys if k<i),default=-1);hi=min((k for k in keys if k>i),default=len(expected))
   a=mapped[lo][1] if lo>=0 else pa0;b=mapped[hi][0] if hi<len(expected) else pb0
   a,b=sorted((a,b));step=(b-a)/(hi-lo-1);mapped[i]=(a+(i-lo-1)*step,a+(i-lo)*step)
  mapped={i:(max(pa0,min(a,pb0)),max(pa0,min(b,pb0))) for i,(a,b) in mapped.items()}
  # Complete p2 sentences use separate exact PCM placements in chapter06.
  if sid in ['06-relative-gap','09-feedback-hierarchy','10-audit-and-close'] and pi==2:
   parts=literal.split('. ',1);parts[0]+='.'
   eparts=english.split('. ',1);eparts[0]+='.';assert len(eparts)==2
  else:parts=[literal];eparts=[english]
  charpos=0;para_chunks=[]
  for ci,(text,etext) in enumerate(zip(parts,eparts)):
   aidx=charpos;bidx=aidx+len(norm(text));charpos=bidx
   source_a=min(mapped[k][0] for k in range(aidx,bidx));source_b=max(mapped[k][1] for k in range(aidx,bidx));assert source_b>source_a
   start,placement=convert(sid,source_a);end,placement_end=convert(sid,source_b,'end')
   assert placement==placement_end,(sid,pi,text,placement,placement_end)
   chunk=dict(scene=sid,paragraph=pi,chunk=ci+1,ko=text,en=etext,sourceSpeechStart=source_a,sourceSpeechEnd=source_b,startSeconds=start,endSeconds=end,placement=placement,evidence=evidence,characterMatch=matcher.ratio(),exactMatchedCharacters=exact,scriptCharacters=len(expected),alignmentOpcodes=matcher.get_opcodes(),recognizedCompleteParagraph=recognized,recognizedWords=use,timingApproved=False,pixelsApproved=False)
   chunks.append(chunk);para_chunks.append(chunk)
   tokens=list(re.finditer(r'\S+',text));first=0;current=[]
   while first<len(tokens):
    last=first+1
    while last<len(tokens):
     trial=text[tokens[first].start():tokens[last].end()]
     if font.getlength(trial)>620 or re.search(r'[.!?]$',text[tokens[first].start():tokens[last-1].end()]):break
     last+=1
    cue_text=text[tokens[first].start():tokens[last-1].end()]
    ai=aidx+len(norm(text[:tokens[first].start()]));bi=aidx+len(norm(text[:tokens[last-1].end()]))
    a=min(mapped[k][0]for k in range(ai,bi));b=max(mapped[k][1]for k in range(ai,bi))
    sa,pa=convert(sid,a);sb,pb=convert(sid,b,'end');assert pa==pb and sb>sa,(sid,pi,cue_text,sa,sb)
    cue=dict(scene=sid,paragraph=pi,chunk=ci+1,ko=cue_text,lines=[cue_text],startSeconds=sa,endSeconds=sb,sourceSpeechStart=a,sourceSpeechEnd=b,placement=pa,textWidthPx=font.getlength(cue_text),center=[960,970],fontPx=48,style='boxed-white-forest-v1',timingApproved=False,pixelsApproved=False)
    ko.append(cue);current.append(cue);first=last
   assert norm(' '.join(c['ko']for c in current))==norm(text)
   pieces=[];cur=[]
   for w in etext.split():
    if cur and len(' '.join(cur+[w]))>78:pieces.append(' '.join(cur));cur=[]
    cur.append(w)
   if cur:pieces.append(' '.join(cur))
   total=sum(len(x)for x in pieces);cursor=start
   for piece in pieces:
    stop=cursor+(end-start)*len(piece)/total;en.append(dict(scene=sid,paragraph=pi,chunk=ci+1,en=piece,startSeconds=cursor,endSeconds=stop,placement=placement,timingMethod='Complete semantic chunk span, weighted wrap; candidate',timingApproved=False));cursor=stop
   assert norm(' '.join(pieces))==norm(etext)
  assert charpos==len(expected)
  paragraphs.append(dict(scene=sid,paragraph=pi,ko=literal,en=english,chunks=len(para_chunks),characterMatch=matcher.ratio(),allLiteralTextsRetained=True))
for lang,rows in [('ko',ko),('en',en)]:
 rows.sort(key=lambda r:(r['startSeconds'],r['endSeconds']))
 for left,right in zip(rows,rows[1:]):assert left['endSeconds']<=right['startSeconds']+.001,(lang,left,right)
 # Merge a sub.65-second KO ending only when it stays within a complete chunk
 # and the fixed-width result fits one line, preserving Balatro's one-line UI.
 if lang=='ko':
  i=0
  while i<len(rows):
   cue=rows[i]
   if cue['endSeconds']-cue['startSeconds']>=.65 or i==0:i+=1;continue
   prev=rows[i-1];merged=(prev['ko']+' '+cue['ko']).strip()
   if (prev['scene'],prev['paragraph'],prev['chunk'],prev['placement'])!=(cue['scene'],cue['paragraph'],cue['chunk'],cue['placement']) or cue['startSeconds']-prev['endSeconds']>.4 or font.getlength(merged)>1250:
    changes.append(dict(scene=cue['scene'],paragraph=cue['paragraph'],text=cue['ko'],seconds=cue['endSeconds']-cue['startSeconds'],needsDirectReadabilityReview=True));i+=1;continue
   changes.append(dict(scene=cue['scene'],paragraph=cue['paragraph'],previous=prev['ko'],short=cue['ko'],merged=merged,previousDuration=cue['endSeconds']-cue['startSeconds'],needsDirectReadabilityReview=False))
   prev.update(ko=merged,lines=[merged],endSeconds=cue['endSeconds'],sourceSpeechEnd=cue['sourceSpeechEnd'],textWidthPx=font.getlength(merged));rows.pop(i)
 for i,r in enumerate(rows,1):r['index']=i
for p in paragraphs:
 for lang,rows in [('ko',ko),('en',en)]:
  actual=[r for r in rows if r['scene']==p['scene'] and r['paragraph']==p['paragraph']]
  assert norm(''.join(r[lang]for r in actual))==norm(p[lang])
assert len(paragraphs)==39 and len(chunks)==42
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
DEST.mkdir()
for lang,rows in [('ko',ko),('en',en)]:
 (DEST/f'candidate.{lang}.srt').write_text('\n\n'.join(f'{r["index"]}\n{stamp(r["startSeconds"])} --> {stamp(r["endSeconds"])}\n{r[lang]}'for r in rows)+'\n','utf-8')
record=dict(schemaVersion=7,preparedAt=datetime.now(timezone.utc).isoformat(),plan=rel(PLAN),planSha256=sha(PLAN),paragraphs=paragraphs,chunks=chunks,ko=ko,en=en,koCueCount=len(ko),enCueCount=len(en),asrProvenance=provenance,artifacts=artifacts,numericNormalizationForAlignmentOnly=numeric,readabilityChanges=changes,allLiteralKoEn39ParagraphsPreserved=True,unchangedApprovedParagraphPcmRetained=True,allCurrent39ParagraphsPreserved=True,captionCenter=[960,970],fontPx=48,maxLines=1,allCueTimingApproved=False,allCuePixelsReviewed=False,finalTimingApproved=False,finalMixedAsrApproved=False,allFinalPixels=False,qa=False,collected=False,private=False,newTtsJobs=0,newAsrJobs=0,newMedia=0,newImagesGitAdded=0,humanListening='pending',humanPronunciation='pending')
(DEST/'captions.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(paragraphs=39,semanticChunks=len(chunks),ko=len(ko),en=len(en),minimumMatch=min(p['characterMatch']for p in paragraphs),shortKoCues=[dict(text=r['ko'],seconds=r['endSeconds']-r['startSeconds'])for r in ko if r['endSeconds']-r['startSeconds']<.65],approved=False),ensure_ascii=False))
