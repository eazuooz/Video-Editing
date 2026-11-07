"""CPU-only06.02 exact selected96component caption timing. Default Pending.

Reads completed raw PCM/independent blind-ASR proof only. Never starts voice,
ASR, model, stage, GPU, media decoder or encoder. No text-duration ratios or
within-ASR-word interpolation. Missing literal boundaries remain Pending.
"""
from __future__ import annotations
import argparse,copy,difflib,hashlib,importlib.util,json,math,os,re,struct,wave
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PROJECT=ROOT/'projects/shorts-leveldesign-06-02'
MEDIA_ROOT=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106');MEDIA=MEDIA_ROOT/'shorts-leveldesign-06-02'
VOICE=MEDIA_ROOT/'06-02-voice-evidence.json';VOICE_STATE=MEDIA_ROOT/'06-02-voice-progress.json'
BOUNDARY_SUPPORT=PROJECT/'caption-word-boundary-support-v1.json';BOUNDARY_SUPPORT_SHA256='05acc8af9b24bf40a94dc6d0f5539103c81f8d0ce92627afdc6805fec8db4e83'
ASR_ADAPTER=HERE/'run-prospect-refuge-voice-qa.py';ASR_ADAPTER_SHA256='65755e9bf90bbfa52e8cad3ae8b6d2ed053a99a5efe12435a4fe05f666247980'
FPS=60;RATE=24000;TOPIC='06.02';SCHEMA='06.02-selected-caption-timing-v1'
PINS={'build-selected-caption-timing.py':'705f6c3fa3c220b68ea524d24387c9ff399dbbfa9a6dab12a250766051c475fd','build-first-timeline.py':'857ed4ac83a0da9ff7f3bc068be36eeeaf22685968ae590cb619aec128738c56','run-first-asr.py':'7e38f2565fcf44b45ff6a94c68c7a359a497515c28ed462c729a36c7d1e6864e','run-selected-voice-qa.py':'65983206f0e0fa81dd5a5780871605fcc2665816a9f21fc3ea3a43781437e2a9'}
SOURCE_PINS={'narration-draft.json':'dddd4c5787a8d22dfc4cb52cb0eab18d44c53d105d53341f402d3a61480ab7f6','voice-semantic-components-v2.json':'8824510b65db882304ba04ab54320764f47d53fc2f13b34ec97f6ffa7f441132','caption-clauses-v3.json':'1438c3a0047a213598f03af859d17b7736802c46b34e7efdde9a934f174bb27d','translated-caption-anchors-v2.json':'854d2371e6d3a7fd0af7bf0dc84dd2759f3ce93f6d00cb116646255d95d667d4'}
POLICY=dict(rawSampleRate=RATE,fps=FPS,internalFrameRounding='nearest integer frame, half up',finalFrameRounding='ceil exact total PCM',wordBoundary='actual adjacent blind-ASR word offset/onset midpoint, converted to nearest raw sample; no within-word interpolation',captionEdges='first/last actual recognized word inside unchanged raw component; no observation hold',automaticSpeechPass=False)

class Pending(RuntimeError):pass
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def module(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def require(condition,message):
 if not condition:raise Pending(message)
for filename,value in PINS.items():require(sha(HERE/filename)==value,'Reviewed caption/ASR primitive changed: '+filename)
base=module('prospect_caption_selected_primitives',HERE/'build-selected-caption-timing.py');asr=base.asr
def sample(seconds):
 require(type(seconds)in(int,float)and math.isfinite(seconds),'Nonfinite actual word time')
 return int(math.floor(seconds*RATE+.5))
def frame_from_sample(value):
 require(type(value)is int and value>=0,'Nonnegative integer sample boundary required')
 return(value*FPS+RATE//2)//RATE
def ceil_frame(value):return(value*FPS+RATE-1)//RATE
def assert_pin(row):require(Path(row['path']).is_file()and sha(row['path'])==row['sha256'],'Pinned artifact missing/changed: '+row['path'])
def float_wav_clock(path):
 """Read only RIFF header/chunk offsets; never decode or load actual mix PCM."""
 size=Path(path).stat().st_size;fmt=None;data=None
 with Path(path).open('rb')as f:
  header=f.read(12);require(len(header)==12 and header[:4]==b'RIFF'and header[8:]==b'WAVE'and struct.unpack('<I',header[4:8])[0]+8==size,'Actual prepared mix must be complete RIFF WAV')
  while f.tell()+8<=size:
   kind,count=struct.unpack('<4sI',f.read(8));position=f.tell();require(position+count<=size,'Truncated actual WAV chunk')
   if kind==b'fmt ':require(fmt is None and 16<=count<=1024,'Duplicate/invalid WAV format');fmt=f.read(count)
   elif kind==b'data':require(data is None,'Duplicate WAV PCM data chunk');data=count
   f.seek(position+count+(count%2))
 require(fmt is not None and data is not None,'Actual prepared mix format/data missing')
 tag,channels,rate,byteRate,block,bits=struct.unpack('<HHIIHH',fmt[:16]);require(tag==3 and bits==32 and channels==2 and block==8 and byteRate==rate*block and data%block==0,'Actual prepared mix must be stereo IEEE FLOAT32 WAV')
 return rate,channels,data//block,'FLOAT'
def sources():
 for name,value in SOURCE_PINS.items():require((PROJECT/name).is_file()and sha(PROJECT/name)==value,'Current06.02 source changed: '+name)
 return tuple(read(PROJECT/name)for name in SOURCE_PINS)

def voice_binding(voice,review,narration):
 """Verify actual canonical96raw chunks/aggregate without trusting summaries."""
 require(voice.get('topicId')==TOPIC,'Exact selected06.02 raw voice required')
 scenes=voice.get('identity',{}).get('scenes',[]);mapping=voice.get('paragraphMapping',[]);chunks=voice.get('sceneWavs',[])
 require(len(narration.get('narrationKo',[]))==25 and len(scenes)==len(mapping)==len(chunks)==96,'Exactly96 complete components/25 paragraphs required')
 require(digest(voice['identity'])==voice['fingerprint'],'Selected synthesis identity changed')
 expected=[]
 for p,paragraph in enumerate(narration['narrationKo'],1):
  cursor=0
  for index,text in enumerate(re.split(r'(?<=[.!?])\s+',paragraph),1):
   expected.append(dict(sceneId=f'p{p:03}-c{index:02}',paragraph=p,sentenceIndexZeroBased=index-1,canonicalKo=text,paragraphCharRange=[cursor,cursor+len(text)]));cursor+=len(text)+1
 require(len(expected)==96,'Canonical sentence component count changed')
 require([s['id']for s in scenes]==[m['sceneId']for m in mapping]==[e['sceneId']for e in expected],'Selected component IDs/order changed')
 assert_pin(voice['timing']);assert_pin(voice['aggregateWav']);timing=read(voice['timing']['path']);entries=timing.get('entries',[])
 require(timing.get('sample_rate')==RATE and len(entries)==96,'Exact raw24k96-entry timing required')
 aggregateDigest=hashlib.sha256();position=0;sentences=[]
 for scene,mappingRow,chunk,entry,want in zip(scenes,mapping,chunks,entries,expected):
  text=' '.join(scene['lines']);require(text==mappingRow['canonicalText']==entry['text']==want['canonicalKo'],'Raw component text differs from canonical full sentence')
  require(mappingRow['paragraph']==want['paragraph']and mappingRow['sourceCharRange']==want['paragraphCharRange'],'Canonical component paragraph/character mapping changed')
  require(entry['scene_id']==want['sceneId']and abs(entry['start']-position/RATE)<1e-9,'Actual raw component order/start clock changed')
  assert_pin(chunk)
  with wave.open(chunk['path'],'rb')as w:
   require((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,RATE,chunk['frames']),'Exact raw monoPCM16/24k format or sample count changed');data=w.readframes(w.getnframes())
  require(len(data)==chunk['frames']*2 and hashlib.sha256(data).hexdigest()==chunk['pcmSHA256'],'Actual raw component PCM changed')
  start=position;position+=chunk['frames'];aggregateDigest.update(data)
  require(abs(entry['end']-position/RATE)<1e-9,'Actual raw component end clock changed')
  sentences.append(dict(want,startSample=start,endSample=position,startFrame=frame_from_sample(start),endFrameExclusive=frame_from_sample(position),rawWav=chunk))
 with wave.open(voice['aggregateWav']['path'],'rb')as w:
  require((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,RATE,position),'Actual canonical aggregate clock/format changed');actual=hashlib.sha256(w.readframes(position)).hexdigest()
 require(actual==aggregateDigest.hexdigest()==voice['aggregateWav']['pcmSHA256'],'Aggregate is not exact untouched raw component concatenation')
 if review is not None:
  require(review.get('voiceFingerprint')==voice['fingerprint']and review.get('aggregateSHA256')==voice['aggregateWav']['sha256']and review.get('timingSHA256')==voice['timing']['sha256'],'Blind ASR belongs to a different raw voice/clock')
  require(len(review.get('paragraphs',[]))==25,'Complete actual25-paragraph ASR required')
  for p,row in enumerate(review['paragraphs'],1):
   ss=[s for s in sentences if s['paragraph']==p]
   require(row['paragraph']==p and row['sceneIds']==[s['sceneId']for s in ss]and row['expectedLiteral']==narration['narrationKo'][p-1],'Raw ASR paragraph coverage/text order changed')
   require((row['startSample'],row['endSample'])==(ss[0]['startSample'],ss[-1]['endSample'])and abs(row['start']-ss[0]['startSample']/RATE)<1e-9 and abs(row['end']-ss[-1]['endSample']/RATE)<1e-9,'Raw ASR paragraph sample/second envelopes changed')
 sentences[-1]['endFrameExclusive']=ceil_frame(position)
 return dict(voiceFingerprint=voice['fingerprint'],aggregate=voice['aggregateWav'],timing=voice['timing'],sampleRate=RATE,totalSamples=position,totalFrames=ceil_frame(position),rawSelectedTakes=96,canonicalExactConcatVerified=True,sentences=sentences,automaticSpeechPass=False)

def asr_factory():
 require(bool(ASR_ADAPTER_SHA256)and ASR_ADAPTER.is_file(),'Reviewed06.02 blind-ASR adapter/source pin pending')
 require(sha(ASR_ADAPTER)==ASR_ADAPTER_SHA256,'Reviewed06.02 blind-ASR adapter changed')
 return module('prospect_caption_current_blind_asr_adapter',ASR_ADAPTER)
def verified_asr_review(path):
 """Existing current summary + every actual take/join cache, never recognition."""
 qa=asr_factory();job=qa.prepare_job();target=Path(job['output'])/'review.json'
 require(Path(path).resolve()==target.resolve()and target.is_file(),'Current complete06.02 ASR review is not available')
 require(all(qa.cached(job,t)is not None for t in job['identity']['tasks']),'Missing independent blind take/join cache')
 current=read(target);require(qa.summary(job)==current,'Existing blind-ASR summary differs from exact immutable caches')
 require(current.get('aliasesApplied')is False and current.get('expectedPrompt')is None and current.get('automaticSpeechPass')is False,'ASR must retain raw literal differences without aliases/prompts or automatic speech pass')
 return current

def boundary_support(binding):
 """Only the root-authored exact same-PCM display boundary, never an alias."""
 if not BOUNDARY_SUPPORT.exists():return {} # Generic literal alignment still fails closed if its boundary is unsupported.
 require(BOUNDARY_SUPPORT.is_file()and sha(BOUNDARY_SUPPORT)==BOUNDARY_SUPPORT_SHA256,'Explicit accepted raw-word display-boundary proof changed/missing')
 proof=read(BOUNDARY_SUPPORT)
 require(proof.get('schemaVersion')=='06.02-explicit-raw-word-boundary-support-v1'and proof.get('topicId')==TOPIC and proof.get('status')=='root-accepted-exact-word-end-for-display-clock-only'and proof.get('sourceNarration')==pin(PROJECT/'narration-draft.json'),'Wrong current source/display-boundary support')
 require(all(proof.get(k)is False for k in('aliasesApplied','recognitionModified','pcmModified','actualListening','automaticSpeechPass','humanApproval')),'Boundary support must not imply modified speech or listening approval')
 rows=proof.get('bindings',[]);require(len(rows)==1 and rows[0].get('sceneId')=='p014-c03','Only exact approved p014-c03 display boundary supported')
 row=rows[0];ss=next((s for s in binding['sentences']if s['sceneId']==row['sceneId']),None)
 require(ss is not None and ss['canonicalKo']==row['canonicalKo']and row.get('canonicalCharOffsets')==[13,14]and row.get('canonicalLeftWord')=='뒤에는'and row.get('method')=='explicit-one-sided-actual-whole-word-end','Approved boundary canonical text/char scope changed')
 require(all(row.get(k)is True for k in('reuseOnlyIfSameRawWavAndPcm','requireCurrentBlindWordRecordSameLocalTimestamp','noFallbackToCharacterRatio')),'Exact unchanged raw-word policy required')
 for key in('sha256','pcmSHA256','sampleRate','frames'):require(ss['rawWav'][key]==row['rawWav'][key],'Boundary proof raw PCM/format differs: '+key)
 assert_pin(row['rawWav']);assert_pin(row['sourceAsrRecord']);old=read(row['sourceAsrRecord']['path'])
 require(old['task']['sceneId']==row['sceneId']and old['task']['pcmIdentity']['pcmSHA256']==row['rawWav']['pcmSHA256'],'Original boundary ASR proof belongs to another raw take')
 return {row['sceneId']:dict(row,supportProof=pin(BOUNDARY_SUPPORT))}

def apply_boundary_support(sentence,words,ordered,unsupported,row):
 require(sentence['sceneId']==row['sceneId']and sentence['canonicalKo']==row['canonicalKo'],'Explicit display boundary belongs to another sentence')
 for key in('sha256','pcmSHA256','sampleRate','frames'):require(sentence['rawWav'][key]==row['rawWav'][key],'Explicit boundary raw source changed: '+key)
 index=row['recognizedWordIndex'];require(type(index)is int and 0<=index<len(words)-1,'Explicit whole-word index invalid')
 current=words[index];following=words[index+1];start=sentence['startSample'];a,b=row['recognizedWordLocalSeconds'];require(current['text']==row['recognizedWordLiteral']and asr.folded(current['text'])==row['canonicalLeftWord'],'Current blind word literal differs from exact approved whole word')
 require(current['startSample']-start==sample(a)and current['endSample']-start==sample(b)==row['boundaryRawSampleInTake']and following['startSample']==current['endSample'],'Current actual whole-word offset/next onset differs from approved raw sample boundary')
 lexical=list(re.finditer(r'\S+',sentence['canonicalKo']));left=next((i for i,w in enumerate(lexical)if w.group()==row['canonicalLeftWord']),None);require(left is not None and left+1<len(lexical)and [lexical[left].end(),lexical[left+1].start()]==row['canonicalCharOffsets'],'Approved canonical whole-word edge moved')
 offsets=row['canonicalCharOffsets'];point=current['endSample'];existing=[x for x in ordered if x['charOffset']in offsets]
 require(not existing or all(x['sample']==point for x in existing),'Explicit support disagrees with another actual literal boundary')
 ordered=[x for x in ordered if x['charOffset']not in offsets]+[dict(charOffset=offset,canonicalWordBoundaryIndex=left+1,sample=point,frame=frame_from_sample(point),method='Explicit accepted same-PCM exact whole-word end; following spelling discrepancy remains raw',sourceWordIndices=[index,index+1],supportProof=row['supportProof'],supportId=row['id'])for offset in offsets]
 return sorted(ordered,key=lambda x:x['charOffset']),[x for x in unsupported if x['charOffset']not in offsets]

def aligned_sentence(sentence,take,support=None):
 canonical=sentence['canonicalKo'];start=sentence['startSample'];end=sentence['endSample'];words=take.get('globalWords',[])
 require(take['task']['sceneId']==sentence['sceneId']and take['task']['expected']==canonical,'ASR take does not bind exact source sentence')
 require(take['task']['offsetSample']==start and take['task']['endSample']==end,'ASR take sample clock changed')
 require(bool(words),'Actual blind-ASR words required')
 normalized='';owners=[];actualWords=[];lastStart=-1.;timeFlags=[]
 for index,row in enumerate(words):
  a,b=row['timestamp'];require(type(a)in(int,float)and type(b)in(int,float)and math.isfinite(a)and math.isfinite(b),'Missing/nonfinite actual ASR word boundary')
  folded=asr.folded(row['text']);require(a<=b and (not folded or a<b)and a>=lastStart-.000001,'Zero/backward actual speech word window');lastStart=a
  require(a>=start/RATE-.08 and b<=end/RATE+.08,'Actual ASR word outside its canonical PCM component')
  first,last=max(start,min(end,sample(a))),max(start,min(end,sample(b)))
  if a<start/RATE or b>end/RATE:timeFlags.append(dict(index=index,kind='ASR timestamp clipped only for display to exact unchanged PCM envelope'))
  actualWords.append(dict(text=row['text'],start=a,end=b,startSample=first,endSample=last,sourceWordIndex=index))
  normalized+=folded;owners.extend([index]*len(folded))
 require(normalized==asr.folded(take['text']),'Actual word transcript differs from raw blind recognized literal')
 expected=asr.folded(canonical);mapping={};differences=[]
 for kind,a,b,c,d in difflib.SequenceMatcher(None,expected,normalized,autojunk=False).get_opcodes():
  if kind=='equal':mapping.update((a+j,c+j)for j in range(b-a))
  else:differences.append(dict(kind=kind,expected=expected[a:b],recognized=normalized[c:d],expectedRange=[a,b],recognizedRange=[c,d]))
 require(bool(mapping),'No literal ASR anchors; aliases forbidden')
 lexical=list(re.finditer(r'\S+',canonical));boundaries=[];unsupported=[]
 def at_word_boundary(index):
  if index==0:
   used=next((i for i,w in enumerate(words)if asr.folded(w['text'])),None);require(used is not None,'No actual speech words');return actualWords[used]['startSample'],'actual first blind-ASR word onset',[used]
  if index==len(lexical):
   used=next((i for i in reversed(range(len(words)))if asr.folded(words[i]['text'])),None);return actualWords[used]['endSample'],'actual last blind-ASR word offset',[used]
  offset=len(asr.folded(canonical[:lexical[index].start()]))
  if offset-1 not in mapping or offset not in mapping or mapping[offset]!=mapping[offset-1]+1:raise Pending('Boundary crosses unanchored raw recognition difference')
  li,ri=owners[mapping[offset-1]],owners[mapping[offset]]
  if li==ri:raise Pending('Authored word boundary lies inside one actual ASR timestamp; no character interpolation')
  require(all(not asr.folded(words[j]['text'])for j in range(li+1,ri)),'Boundary crosses extra actual ASR words')
  value=max(start,min(end,sample((words[li]['timestamp'][1]+words[ri]['timestamp'][0])/2)))
  return value,'actual adjacent blind-ASR word offset/onset midpoint',[li,ri]
 for index in range(len(lexical)+1):
  offsets={0}if index==0 else{len(canonical)}if index==len(lexical)else{lexical[index-1].end(),lexical[index].start()}
  try:value,method,sourceWords=at_word_boundary(index)
  except Pending as e:
   for offset in sorted(offsets):unsupported.append(dict(charOffset=offset,canonicalWordBoundaryIndex=index,reason=str(e)))
   continue
  for offset in sorted(offsets):boundaries.append(dict(charOffset=offset,canonicalWordBoundaryIndex=index,sample=value,frame=frame_from_sample(value),method=method,sourceWordIndices=sourceWords))
 ordered=sorted(boundaries,key=lambda x:x['charOffset'])
 if support:ordered,unsupported=apply_boundary_support(sentence,actualWords,ordered,unsupported,support)
 require(all(a['sample']<=b['sample']for a,b in zip(ordered,ordered[1:])),'Actual literal word boundary samples reverse')
 return dict(sentence,words=actualWords,canonicalWordBoundaries=ordered,unsupportedWordBoundaries=unsupported,alignmentReview=dict(expectedLiteral=canonical,recognizedLiteral=take['text'],comparison=asr.comparison(canonical,take['text']),alignmentDifferences=differences,wordTimeFlags=timeFlags,explicitDisplayBoundarySupport=support['supportProof']if support else None,aliasesApplied=False,automaticSpeechPass=False,humanListening=False))

def char_boundary(sentence,offset):
 candidates=[b for b in sentence['canonicalWordBoundaries']if b['charOffset']==offset]
 require(len(candidates)==1,'No actual literal word-boundary anchor for '+sentence['sceneId']+' char '+str(offset))
 return candidates[0]
def resolve_literal_start(sentence,phrase):
 text=sentence['canonicalKo'];require(isinstance(phrase,str)and phrase and text.count(phrase)==1,'Timeline phrase must be exact unique literal within one source sentence')
 return dict(char_boundary(sentence,text.index(phrase)),exactSpokenAnchorKo=phrase,sceneId=sentence['sceneId'])
def resolve_literal_interval(sentence,phrase):
 start=resolve_literal_start(sentence,phrase);end=char_boundary(sentence,sentence['canonicalKo'].index(phrase)+len(phrase))
 require(end['sample']>start['sample'],'Literal actual phrase interval has no positive sample duration')
 return dict(sceneId=sentence['sceneId'],exactSpokenAnchorKo=phrase,startSample=start['sample'],endSample=end['sample'],startFrame=start['frame'],endFrameExclusive=end['frame'],startBoundary=start,endBoundary=end)

def display_cue(cue,lang,group,left,right,normal,bold):
 require(len(cue.get('emphasis',[]))<=1,'Only one authored emphasis span allowed')
 for span in cue.get('emphasis',[]):
  require(type(span['start'])is int and type(span['end'])is int and 0<=span['start']<span['end']<=len(cue['text'])and span['role']in('term','result','problem'),'Malformed authored emphasis')
  lineCursor=0;contained=False
  for line in cue['lines']:
   if lineCursor<=span['start']<span['end']<=lineCursor+len(line):contained=True
   lineCursor+=len(line)+1
  require(contained,'Authored emphasis crosses lines; never silently shorten it')
 try:out=base.display_cue(cue,lang,group,left,right,normal,bold)
 except(base.Pending,AssertionError)as e:raise Pending(str(e))from e
 require(out['emphasis']==cue.get('emphasis',[]),'Primitive changed authored emphasis instead of preserving it')
 return out

def build(narration,clauses,translated,review,binding,support=None):
 require(clauses['sourceNarration']['sha256']==SOURCE_PINS['narration-draft.json']and translated['sourceNarration']==clauses['sourceNarration'],'Current canonical caption/translation binding required')
 require(len(review.get('takes',[]))==96 and len(review.get('boundaryWindows',[]))==95,'Complete96take/95join recognition evidence required')
 normal,bold,_=base.base.fonts();require(clauses['style']['fontSizePx']==48 and clauses['style']['maxTextWidthPx']==800 and clauses['style']['maxLines']==2 and clauses['style']['fontWeight']==500 and clauses['style']['emphasisFontWeight']==700,'Fixed48px/800px/two-line caption geometry changed');require(sha(clauses['style']['fontPath'])==clauses['style']['fontSHA256'],'Measured48px font changed')
 groups=clauses['groups'];anchors=translated['groups'];require(len(groups)==len(anchors)==96,'Exactly96 authored semantic groups required')
 takeMap={t['task']['sceneId']:t for t in review['takes']};require(len(takeMap)==96,'Duplicate/missing recognized takes')
 sentences=[];cues={'ko':[],'en':[]};groupRows=[]
 for ss,g,a in zip(binding['sentences'],groups,anchors):
  require(g['ko']==a['ko']==ss['canonicalKo']and a['groupId']==g['id']and g['koSourceCharRange']==ss['paragraphCharRange'],'Sentence/caption/translated semantic mapping changed')
  sentence=aligned_sentence(ss,takeMap[ss['sceneId']],(support or{}).get(ss['sceneId']));sentence['groupId']=g['id'];sentences.append(sentence)
  begin=char_boundary(sentence,0);finish=char_boundary(sentence,len(g['ko']))
  require(finish['frame']>begin['frame'],'Actual source sentence speech has zero frame span')
  groupRows.append(dict(id=g['id'],paragraph=g['paragraph'],beatId=g['beatId'],sceneId=ss['sceneId'],startFrame=begin['frame'],endFrameExclusive=finish['frame'],startSample=begin['sample'],endSample=finish['sample'],koSourceCharRange=g['koSourceCharRange'],enSourceCharRange=g['enSourceCharRange']))
  for cue in g['koCues']:
   x,y=cue['groupCharRange'];left,right=char_boundary(sentence,x),char_boundary(sentence,y)
   require(right['sample']>left['sample'],'Caption has no positive actual sample span')
   out=display_cue(cue,'ko',g,left['frame'],right['frame'],normal,bold);out.update(sceneId=ss['sceneId'],startSample=left['sample'],endSample=right['sample'],literalAlignment=dict(expectedLiteral=cue['text'],canonicalGroupCharRange=[x,y],actualStartBoundary=left,actualEndBoundary=right,aliasesApplied=False),recognitionBasis='blind selected component words',actualListening=False)
   cues['ko'].append(out)
  require([c['enCueId']for c in a['cues']]==[c['id']for c in g['enCues']],'Authored translated cue IDs/order changed')
  coverage=0
  for cue,anchor in zip(g['enCues'],a['cues']):
   x,y=anchor['koGroupCharRange'];require(g['ko'][x:y]==anchor['koLiteralText']and cue['text']==anchor['enText'],'Translated cue literal semantic anchor changed')
   ca,cb=anchor['koCoverageGroupCharRange'];require(ca==coverage and g['ko'][ca:cb]==anchor['koCoverageLiteral'],'Translated semantic partition has a gap/reversal');coverage=cb
   left,right=char_boundary(sentence,x),char_boundary(sentence,y);require(right['sample']>left['sample'],'Translated cue has no positive actual sample span')
   out=display_cue(cue,'en',g,left['frame'],right['frame'],normal,bold);out.update(sceneId=ss['sceneId'],startSample=left['sample'],endSample=right['sample'],timingBasis='Authored monotonic KO word-boundary display slots inside same complete translation group; not English ASR or character ratio',spokenLiteralAnchorKo=anchor['koLiteralText'],semanticWindowKo=anchor['semanticWindowKo'],translationReordered=a['translationReordered'],translatedTimingReviewPending=True,actualListening=False)
   cues['en'].append(out)
  require(coverage==len(g['ko']),'Translated anchors do not cover complete source sentence')
 for lang,rows in cues.items():
  require(all(a['endSample']<=b['startSample']and a['endFrameExclusive']<=b['startFrame']for a,b in zip(rows,rows[1:])),lang+' actual captions overlap')
 require(len(cues['ko'])==190 and len(cues['en'])==234,'Complete190KO/234EN display coverage required')
 paragraphs=[]
 for p in range(1,26):
  ss=[s for s in sentences if s['paragraph']==p];paragraphs.append(dict(paragraph=p,startSample=ss[0]['startSample'],endSample=ss[-1]['endSample'],startFrame=ss[0]['startFrame'],endFrameExclusive=ss[-1]['endFrameExclusive'],sceneIds=[s['sceneId']for s in ss],recognitionBasis='assembled from exact blind selected component caches'))
 paragraphs[-1]['endFrameExclusive']=binding['totalFrames']
 return dict(schemaVersion=SCHEMA,topicId=TOPIC,fps=FPS,totalFrames=binding['totalFrames'],captions=cues,sentences=sentences,groups=groupRows,paragraphs=paragraphs,audioClock=dict(rawSampleRate=RATE,totalRawSamples=binding['totalSamples'],rawAggregate=binding['aggregate'],rawTiming=binding['timing'],visualFinalFrameCeil=True,noAudioTailPadding=True,addedObservationHoldSamples=0,mixedAudioTimingAccepted=False,finalMix=None),voiceBinding={k:v for k,v in binding.items()if k!='sentences'},alignmentReview=dict(aliasesApplied=False,automaticSpeechPass=False,rawLiteralDifferencesPreserved=True,unsupportedWordBoundariesPreserved=True,translationReorderedGroups=26),automaticSpeechPass=False,actualListening=False,actualFinalPlayback=False,humanTimingReviewRequired=True,platformActions=[])

def validate_scalar_clock_reuse(audio_build_path,clock_proof_path,binding):
 require(audio_build_path and clock_proof_path,'Accepted scalar-only prepared-audio timing proof required')
 audio=read(audio_build_path);proof=read(clock_proof_path)
 require(proof.get('schemaVersion')=='06.02-scalar-clock-reuse-proof-v1'and proof.get('topicId')==TOPIC and proof.get('acceptedForTimingReuse')is True,'Exact accepted06.02 scalar-clock proof required')
 require(proof['audioBuild']==pin(audio_build_path)and proof['rawAggregate']==binding['aggregate']and proof['rawTiming']==binding['timing']and proof['voiceFingerprint']==binding['voiceFingerprint'],'Prepared-audio timing reuse pins changed')
 require(proof.get('trimmedSamples')==proof.get('insertedSamples')==0 and proof.get('speechSpeed')==1 and proof.get('offsetRawSamples')==0 and proof.get('scalarOnly')is True and proof.get('numericalClockVerified')is True,'No trims/pads/fades/timewarp or unverified scalar clock reuse')
 require(len(proof.get('components',[]))==96,'Prepared scalar clock must preserve every actual component')
 for row,s in zip(proof['components'],binding['sentences']):
  require(row['sceneId']==s['sceneId']and row['rawSampleRange']==[s['startSample'],s['endSample']]and row['preparedSampleRange']==[s['startSample']*2,s['endSample']*2],'Prepared scalar clock changed component bounds')
  require(type(row['constantGainDb'])in(int,float)and math.isfinite(row['constantGainDb']),'Finite uniform per-component gain required')
 require(audio.get('schemaVersion')=='06-02-audio-build-v1'and audio.get('topicId')==TOPIC and audio.get('rawVoice')==binding['aggregate']and audio.get('canonicalTiming')==binding['timing']and audio.get('rawVoiceFingerprint')==binding['voiceFingerprint'],'Prepared audio must bind exact selected raw voice')
 require(audio.get('selectedComponentCount')==96 and audio.get('voiceOffsetSeconds')==audio.get('insertedSamples')==audio.get('trimmedSamples')==0 and audio.get('wordBoundariesShifted')is False,'Prepared audio changes the unchanged raw component clock')
 lineage=audio.get('pcmLineage',{});require(lineage.get('voiceOffsetSamples')==0 and lineage.get('rawToPreparedSampleRatio')==[2,1]and lineage.get('voiceSpeed')==1,'Prepared PCM lineage must preserve exact2x grid')
 mix=audio['mixWav'];assert_pin(mix);require(mix['sampleRate']==48000 and mix['channels']==2 and mix['frames']==binding['totalSamples']*2 and mix.get('subtype')=='FLOAT','Prepared mix must retain exact2x sample grid')
 require(float_wav_clock(mix['path'])==(48000,2,binding['totalSamples']*2,'FLOAT'),'Actual prepared mix WAV header differs from claimed clock')
 require(proof['mixWav']==mix,'Accepted timing proof refers to different final mix')
 for row in proof.get('supportingProofs',[]):assert_pin(row)
 require(bool(proof.get('supportingProofs')),'Actual numerical/source support for scalar clock reuse missing')
 return dict(finalMix=mix,mixedAudioTimingAccepted=True,scalarClockProof=pin(clock_proof_path),audioBuild=pin(audio_build_path),timestampReuseScope='Only exact sample/clock preserving scalar-only accepted prepared audio; not new recognition/hearing approval')

def prepare(asr_review=None,voice_evidence=None,audio_build=None,clock_proof=None):
 narration,componentPlan,clauses,translated=sources();vp=Path(voice_evidence or VOICE).resolve()
 require(vp.is_file(),'Waiting for exact completed06.02 raw voice evidence')
 if vp==VOICE.resolve():
  require(VOICE_STATE.is_file()and read(VOICE_STATE).get('completed')is True,'06.02 selected voice controller/child still active or incomplete')
 voice=read(vp);expected=(ROOT/'shared/output/architectural-111-20261106/06-02/voice-attempts'/voice['fingerprint'][:24]).resolve()
 require(Path(voice['output']).resolve()==expected,'Selected06.02 voice output scope changed')
 qa=asr_factory();job=qa.prepare_job();rp=Path(asr_review or(Path(job['output'])/'review.json')).resolve();review=verified_asr_review(rp)
 binding=voice_binding(voice,review,narration);require(job['identity']['voiceFingerprint']==voice['fingerprint'],'Current blind ASR is for another raw voice')
 support=boundary_support(binding);result=build(narration,clauses,translated,review,binding,support)
 paths=[('narration',PROJECT/'narration-draft.json'),('semanticComponents',PROJECT/'voice-semantic-components-v2.json'),('captionClauses',PROJECT/'caption-clauses-v3.json'),('translatedAnchors',PROJECT/'translated-caption-anchors-v2.json'),('voiceEvidence',vp),('rawAsrReview',rp),('rawAsrJob',rp.parent/'job.json'),('rawAsrAdapter',ASR_ADAPTER),('font',Path(clauses['style']['fontPath'])),('captionAdapter',Path(__file__))]+[('primitive:'+name,HERE/name)for name in PINS]
 if support:paths.append(('explicitWordBoundarySupport',BOUNDARY_SUPPORT))
 if audio_build or clock_proof:
  result['audioClock'].update(validate_scalar_clock_reuse(audio_build,clock_proof,binding));paths.extend([('audioBuild',Path(audio_build)),('scalarClockProof',Path(clock_proof))])
 result['inputs']=[dict(role=role,**pin(path))for role,path in paths];result['policy']=POLICY;result['fingerprint']=digest(dict(inputs=result['inputs'],policy=POLICY));return result

def verify_existing(path):
 path=Path(path).resolve();actual=read(path);require(actual.get('schemaVersion')==SCHEMA and actual.get('topicId')==TOPIC,'Not selected06.02 caption timing')
 refs={r['role']:r for r in actual.get('inputs',[])}
 for row in refs.values():assert_pin(row)
 fresh=prepare(refs['rawAsrReview']['path'],refs['voiceEvidence']['path'],refs.get('audioBuild',{}).get('path'),refs.get('scalarClockProof',{}).get('path'))
 require(actual==fresh,'Existing caption timing differs from current verified actual voice/ASR/anchors')
 require(path==(MEDIA/'caption-timing'/fresh['fingerprint'][:24]/'caption-timing.json').resolve(),'Caption timing is outside exact content-addressed selected output')
 return dict(timing=actual,voice=read(refs['voiceEvidence']['path']),asr=read(refs['rawAsrReview']['path']))

def write_outputs(result):
 target=MEDIA/'caption-timing'/result['fingerprint'][:24];outputs={'caption-timing.json':json.dumps(result,ensure_ascii=False,indent=2)+'\n','captions.ko.srt':base.srt(result['captions']['ko'],'ko'),'captions.en.srt':base.srt(result['captions']['en'],'en')}
 for name,text in outputs.items():
  p=target/name
  if p.exists():require(p.read_text(encoding='utf8')==text,'Preserve differing existing caption output')
 for row in result['inputs']:assert_pin(row)
 target.mkdir(parents=True,exist_ok=True)
 for name,text in outputs.items():
  p=target/name
  if not p.exists():
   with p.open('x',encoding='utf8')as f:f.write(text)
 return target
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--asr-review');p.add_argument('--voice-evidence');p.add_argument('--audio-build');p.add_argument('--clock-proof');p.add_argument('--write',action='store_true');p.add_argument('--verify-existing');a=p.parse_args()
 try:
  if a.verify_existing:r=verify_existing(a.verify_existing)['timing'];print(json.dumps(dict(verified=True,fingerprint=r['fingerprint'],noModelOrMediaJob=True)));return
  r=prepare(a.asr_review,a.voice_evidence,a.audio_build,a.clock_proof)
  target=str(write_outputs(r))if a.write else None
  print(json.dumps(dict(ready=True,fingerprint=r['fingerprint'],sentences=len(r['sentences']),captions={k:len(v)for k,v in r['captions'].items()},output=target,written=a.write,automaticSpeechPass=False)))
 except(Pending,FileNotFoundError)as e:
  if a.write:raise
  print(json.dumps(dict(ready=False,reason=str(e),written=False,noModelOrMediaJob=True)))
if __name__=='__main__':main()
