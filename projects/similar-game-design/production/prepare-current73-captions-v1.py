"""Literal current73 captions from already reviewed whole/independent ASR.
No new recognition/synthesis; timings and pixels remain review candidates.
"""
from pathlib import Path
from datetime import datetime, timezone
from difflib import SequenceMatcher
import hashlib,json,re,math
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
DEST=BASE/'caption-candidate-v1';PLAN=BASE/'measured-allocation-v2/plan.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
norm=lambda s:''.join(c.lower() for c in s if c.isalnum())
assert not DEST.exists(),'Preserve caption candidate'
plan=read(PLAN);assert plan['sourceAllocationApproved'] and plan['allSelectedNativePixelsReviewed']
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
ko=[];en=[];paragraphs=[];scenes=[];artifacts=[];sources={}
reviews=['current-whole-asr-direct-review-v1.json','current-contexts-asr-direct-review-v1.json','current-targets-asr-direct-review-v1.json','current-mining-join-asr-direct-review-v1.json','guides-contexts-asr-direct-review-v3.json','fresh-guides-asr-direct-review-v4.json']
for p in reviews:assert (BASE/p).exists()
for scene in plan['scenes']:
 sid=scene['id'];num=int(sid[:2]);assert sha(ROOT/scene['voicePath'])==scene['voiceSha256']
 def load_asr(name):
  p=BASE/name;j=read(p);assert j['sourceSha256']==scene['voiceSha256'],(sid,name,'voice hash')
  assert not j.get('expectedWasRecognizerPrompt',True)
  pad=j.get('zeroPaddingSamplesEachSide',0)/24000;offset=j.get('startSample',0)/24000-pad
  if j.get('startSample') is not None:assert j['exactSourceSampleBytesMatched']
  provenance=dict(path=rel(p),sha256=sha(p),sourceSha256=j['sourceSha256'],startSample=j.get('startSample',0),zeroPaddingSamplesEachSide=j.get('zeroPaddingSamplesEachSide',0),offsetSeconds=offset,expectedWasRecognizerPrompt=False)
  words=[]
  for w in j['words']:
   a,b=w['timestamp']
   if a is None or b is None or b<=a:
    artifacts.append(dict(scene=sid,path=rel(p),word=w,reason='Recognizer empty/zero-duration timestamp retained as an artifact; no speech claim or listening approval.'));continue
   words.append(dict(text=w['text'],timestamp=[a+offset,b+offset]))
  sources[rel(p)]=provenance
  return words,provenance
 if num==4:
  head=load_asr('current-mining-join-asr-v1/'+sid+'-complete-join.json')
  tail=load_asr('current-mining-join-asr-v1/'+sid+'-complete-tail.json')
 elif num>=23:
  head=tail=load_asr('fresh-guides-asr-v4/'+sid+'-complete-independent.json')
 elif num>=14:
  head=tail=load_asr('guides-contexts-asr-v3/'+sid+'-complete-independent.json')
 else:
  head=load_asr(('current-contexts-asr-v1/'+sid+'-complete-head.json') if num==2 else ('current-whole-asr-v1/'+sid+'.json'))
  tail=load_asr('current-contexts-asr-v1/'+sid+'-complete-tail.json')
 matches=[]
 for pi,p in enumerate(scene['paragraphs'],1):
  use=tail if (num==1 and pi>=2) or (num<=13 and num!=1 and pi>=3) else head
  pa0,pb0=p['sourceInSample']/24000,p['sourceOutSample']/24000
  words=[w for w in use[0] if w['timestamp'][1]>pa0 and w['timestamp'][0]<pb0]
  recognized='';times=[]
  for w in words:
   a,b=w['timestamp'];token=norm(w['text'])
   for i,c in enumerate(token):recognized+=c;times.append((a+(b-a)*i/len(token),a+(b-a)*(i+1)/len(token)))
  expected=norm(p['ko']);m=SequenceMatcher(None,expected,recognized,autojunk=False)
  assert m.ratio()>=.85,(sid,pi,m.ratio(),recognized)
  mapped={a+i:times[b+i] for a,b,n in m.get_matching_blocks() for i in range(n)};exact=set(mapped);keys=sorted(mapped)
  for i in range(len(expected)):
   if i in exact:continue
   lo=max((k for k in keys if k<i),default=-1);hi=min((k for k in keys if k>i),default=len(expected))
   a=mapped[lo][1] if lo>=0 else pa0;b=mapped[hi][0] if hi<len(expected) else pb0
   a,b=min(a,b),max(a,b);width=(b-a)/(hi-lo-1);mapped[i]=(a+(i-lo-1)*width,a+(i-lo)*width)
  pa=max(pa0,min(a for a,b in mapped.values()));pb=min(pb0,max(b for a,b in mapped.values()));assert pb>pa
  convert=lambda t:scene['startFrame']/60+t
  row=dict(scene=sid,paragraph=pi,ko=p['ko'],en=p['en'],sourceSpeechStart=pa,sourceSpeechEnd=pb,startSeconds=convert(pa),endSeconds=convert(pb),evidence=use[1],recognizedCompleteParagraph=recognized,recognizedWords=words,characterMatch=m.ratio(),exactMatchedCharacters=len(exact),scriptCharacters=len(expected),alignmentOpcodes=m.get_opcodes(),timingApproved=False,pixelsApproved=False)
  paragraphs.append(row);matches.append(m.ratio())
  tokens=list(re.finditer(r'\S+',p['ko']));first=0;current=[]
  while first<len(tokens):
   last=first+1
   while last<len(tokens):
    candidate=p['ko'][tokens[first].start():tokens[last].end()]
    if font.getlength(candidate)>620 or re.search(r'[.!?]$',p['ko'][tokens[first].start():tokens[last-1].end()]):break
    last+=1
   text=p['ko'][tokens[first].start():tokens[last-1].end()];assert font.getlength(text)<=620
   a=len(norm(p['ko'][:tokens[first].start()]));b=len(norm(p['ko'][:tokens[last-1].end()]))
   sa=max(pa,min(mapped[k][0] for k in range(a,b)));sb=min(pb,max(mapped[k][1] for k in range(a,b)))
   assert sb>sa,(sid,pi,text,sa,sb)
   cue=dict(scene=sid,paragraph=pi,ko=text,lines=[text],sourceSpeechStart=sa,sourceSpeechEnd=sb,startSeconds=convert(sa),endSeconds=convert(sb),fontPx=48,textWidthPx=font.getlength(text),center=[960,970],style='boxed-white-forest-v1',timingApproved=False,pixelsApproved=False)
   ko.append(cue);current.append(cue);first=last
  assert norm(' '.join(c['ko'] for c in current))==expected
  pieces=[];cur=[]
  for w in p['en'].split():
   if cur and len(' '.join(cur+[w]))>78:pieces.append(' '.join(cur));cur=[]
   cur.append(w)
  if cur:pieces.append(' '.join(cur))
  total=sum(len(t)for t in pieces);cursor=convert(pa)
  for text in pieces:
   stop=cursor+(pb-pa)*len(text)/total;en.append(dict(scene=sid,paragraph=pi,en=text,startSeconds=cursor,endSeconds=stop,timingMethod='paragraph-semantic-span-weighted-wrap-candidate',timingApproved=False));cursor=stop
  assert norm(' '.join(pieces))==norm(p['en'])
 scenes.append(dict(id=sid,voicePath=scene['voicePath'],voiceSha256=scene['voiceSha256'],minimumParagraphMatch=min(matches),allPcmPreserved=True))
for lang,rows in [('ko',ko),('en',en)]:
 rows.sort(key=lambda x:(x['startSeconds'],x['endSeconds']))
 for left,right in zip(rows,rows[1:]):
  assert left['endSeconds']<=right['startSeconds']+.001,(lang,left,right)
 for i,r in enumerate(rows,1):r['index']=i
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
assert len(scenes)==24 and len(paragraphs)==73
DEST.mkdir()
for lang,rows in [('ko',ko),('en',en)]:
 (DEST/f'candidate.{lang}.srt').write_text('\n\n'.join(f'{r["index"]}\n{stamp(r["startSeconds"])} --> {stamp(r["endSeconds"])}\n{r[lang]}'for r in rows)+'\n','utf-8')
record=dict(schemaVersion=1,slug='similar-game-design',preparedAt=datetime.now(timezone.utc).isoformat(),status='current73-literal-reviewed-context-candidate',plan=dict(path=rel(PLAN),sha256=sha(PLAN)),scenes=scenes,paragraphs=paragraphs,ko=ko,en=en,asrProvenance=list(sources.values()),reviewInputs=[dict(path=rel(BASE/p),sha256=sha(BASE/p))for p in reviews],artifacts=artifacts,koCueCount=len(ko),enCueCount=len(en),paragraphCount=73,allLiteralKoEnParagraphsPreserved=True,maxKoWidthPx=620,captionCenter=[960,970],fontPx=48,newTtsJobs=0,newAsrJobs=0,newMedia=0,humanListening='pending',humanPronunciation='pending',allCueTimingApproved=False,allCuePixelsReviewed=False,allFinalPixelsReviewed=False,finalTimingApproved=False,finalMixedAsrApproved=False,render=False,qa=False,uploaded=False)
(DEST/'captions.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(scenes=24,paragraphs=73,koCues=len(ko),enCues=len(en),minimumMatch=min(r['minimumParagraphMatch']for r in scenes),approved=False)))
