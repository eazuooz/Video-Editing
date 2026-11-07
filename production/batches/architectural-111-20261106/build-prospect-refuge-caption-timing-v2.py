"""06.02 V2 CPU caption clock:103physical raw takes ->96logical teaching groups.

No synthesis/ASR/decoder/model/render job. Every time is an actual sample or
blind word boundary. Physical source IDs and all raw literal differences remain.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,re,sys,wave
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PROJECT=ROOT/'projects/shorts-leveldesign-06-02'
MEDIA_ROOT=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106');MEDIA=MEDIA_ROOT/PROJECT.name
VOICE=MEDIA_ROOT/'06-02-voice-evidence.json';VOICE_STATE=MEDIA_ROOT/'06-02-voice-progress.json'
NARRATION=PROJECT/'narration-expanded-draft-v4.json';COMPONENTS=PROJECT/'voice-semantic-components-v3.json'
CLAUSES=PROJECT/'caption-clauses-v4.json';ANCHORS=PROJECT/'translated-caption-anchors-v3.json'
ASR_PATH=HERE/'run-prospect-refuge-voice-qa-v2.py';ASR_SHA='f190897764f2088fe8de425c622444a75ec6f5a4185763af5a02faa4a0caf4b1'
OLD_PATH=HERE/'build-prospect-refuge-caption-timing.py';OLD_SHA='e5cfcc3994a2d52bced9ee66b9ff6213355acbaef45286d31aa3e1461d7ef609'
SOURCE_PINS={NARRATION:'80efff7c8d0b875130e8a28597542db349133cc4e26f873f4dfbbd85d8ce5ff0',COMPONENTS:'200f34b502021233679f0f78f75bf2f7783c6b07d5a6f447e853d7c06f4d559d',CLAUSES:'ab455130843e1e3d13c1cb5de0e827dfb412213c1ac00147a5914aa99d3aba27',ANCHORS:'046207954a2c2720701b1ca293554f903f6573774a6105e1847ece5b7c992dfd'}
SUPPORT=PROJECT/'caption-word-boundary-support-v2.json';SUPPORT_SHA='6afd6a653e3453b38d6cf86c4248d924c62208cc8922f75bf64264cd0364f44c'
FPS=60;RATE=24000;SCHEMA='06.02-selected-caption-timing-v2'

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
 with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(path):return dict(path=str(Path(path).resolve()),sha256=sha(path))
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(name,path):
 old_path=list(sys.path)
 try:
  sys.path.insert(0,str(HERE));sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
 finally:sys.path[:]=old_path
if sha(OLD_PATH)!=OLD_SHA:raise RuntimeError('Frozen V1 literal/font primitives changed')
old=load('prospect_caption_v2_pinned_v1_primitives',OLD_PATH);Pending=old.Pending;asr=old.asr
sample=old.sample;frame_from_sample=old.frame_from_sample;ceil_frame=old.ceil_frame;require=old.require;assert_pin=old.assert_pin
char_boundary=old.char_boundary;resolve_literal_start=old.resolve_literal_start;resolve_literal_interval=old.resolve_literal_interval
POLICY=dict(old.POLICY,physicalComponents=103,logicalTeachingGroups=96,logicalAssembly='Exact current paragraph/group character ranges; one/two raw units, no text-duration interpolation',physicalJoin='Keep actual raw lead/tail samples; caption left/right word edges remain separately measured')

def asr_factory():
 require(ASR_SHA and sha(ASR_PATH)==ASR_SHA,'New103 ASR adapter source freeze changed/pending')
 return load('prospect_caption_v2_actual103_asr',ASR_PATH)
def sources():
 for path,want in SOURCE_PINS.items():require(want and path.is_file()and sha(path)==want,'New103/96 source freeze pending/changed: '+path.name)
 return read(NARRATION),read(COMPONENTS),read(CLAUSES),read(ANCHORS)
def current_job(qa):
 try:return qa.prepare_job()
 except qa.Pending as error:raise Pending(str(error))from error
def verified_asr_review(path):
 qa=asr_factory();job=current_job(qa);target=Path(job['output'])/'review.json'
 require(Path(path).resolve()==target.resolve()and target.is_file(),'Exact completed103take/102join review is not available')
 require(len(job['identity']['tasks'])==205 and all(qa.cached(job,t)is not None for t in job['identity']['tasks']),'All205 actual independent caches required')
 actual=read(target);require(qa.summary(job)==actual,'Current103 ASR summary differs from immutable blind caches')
 require(actual.get('aliasesApplied')is False and actual.get('expectedPrompt')is None and actual.get('automaticSpeechPass')is False,'Blind literals must remain raw without prompts/aliases or automatic speech pass')
 return actual

def voice_binding(voice,review,narration,component_plan=None):
 plan=component_plan if component_plan is not None else read(COMPONENTS)
 narration_sha=plan['sourceNarrationSHA256']if component_plan is not None else sha(NARRATION)
 qa=asr_factory()
 try:groups,logical=qa.component_groups(narration,plan,narration_sha)
 except qa.Pending as error:raise Pending(str(error))from error
 script,mapping=qa.qa.voice.prep.make_scenes(narration,groups)
 expected=[dict(id=s['id'],lines=s['lines'])for s in script['scenes']]
 require(voice.get('topicId')=='06.02'and voice.get('identity',{}).get('scenes')==expected and len(expected)==103,'Current exact103 raw scene/text/order required')
 require(digest(voice['identity'])==voice['fingerprint']and voice.get('paragraphMapping')==mapping,'Current103 synthesis identity/source character mapping differs')
 assert_pin(voice['timing']);assert_pin(voice['aggregateWav']);timing=read(voice['timing']['path']);entries=timing.get('entries',[]);chunks=voice.get('sceneWavs',[])
 require(timing.get('sample_rate')==RATE and len(entries)==len(chunks)==103,'Exact103 mono24k source timing required')
 parts=[];position=0;pcm=hashlib.sha256()
 for source,maprow,chunk,entry in zip(expected,mapping,chunks,entries):
  assert_pin(chunk)
  with wave.open(chunk['path'],'rb')as w:
   require((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,RATE,chunk['frames']),'Actual raw103 format/frame count differs');data=w.readframes(w.getnframes())
  require(len(data)==chunk['frames']*2 and hashlib.sha256(data).hexdigest()==chunk['pcmSHA256'],'Actual physical raw PCM changed')
  require(entry['scene_id']==source['id']and entry['text']==maprow['canonicalText']==source['lines'][0]and entry['start']==position/RATE,'Physical103 exact text/start clock changed')
  start=position;position+=chunk['frames'];pcm.update(data);require(entry['end']==position/RATE,'Physical103 end sample clock changed')
  rich=next(p for p in groups[maprow['paragraph']]if p['physicalSceneId']==source['id'])
  parts.append(dict(sceneId=source['id'],paragraph=maprow['paragraph'],componentIndexZeroBased=maprow['component']-1,canonicalKo=source['lines'][0],paragraphCharRange=maprow['sourceCharRange'],logicalSceneId=rich['logicalSceneId'],logicalSentenceIndexZeroBased=rich['logicalSentenceIndexZeroBased'],logicalPartIndex=rich['logicalPartIndex'],logicalPartCount=rich['logicalPartCount'],logicalSourceCharRange=rich['logicalSourceCharRange'],canonicalJoinerAfter=rich['canonicalJoinerAfter'],startSample=start,endSample=position,startFrame=frame_from_sample(start),endFrameExclusive=frame_from_sample(position),rawWav=chunk))
 with wave.open(voice['aggregateWav']['path'],'rb')as w:
  require((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,RATE,position),'Actual full103 canonical aggregate grid changed');actual=hashlib.sha256(w.readframes(position)).hexdigest()
 require(actual==pcm.hexdigest()==voice['aggregateWav']['pcmSHA256'],'Canonical aggregate is not exact untouched103 raw concatenation')
 if review is not None:
  require(review.get('voiceFingerprint')==voice['fingerprint']and review.get('aggregateSHA256')==voice['aggregateWav']['sha256']and review.get('timingSHA256')==voice['timing']['sha256'],'ASR belongs to another103 voice/sample clock')
  require(len(review.get('takes',[]))==103 and len(review.get('boundaryWindows',[]))==102 and len(review.get('paragraphs',[]))==25,'Full103/102/25 actual ASR scope required')
  for n,row in enumerate(review['paragraphs'],1):
   pp=[p for p in parts if p['paragraph']==n]
   require(row['paragraph']==n and row['sceneIds']==[p['sceneId']for p in pp]and row['expectedLiteral']==narration['narrationKo'][n-1],'ASR physical paragraph identity/prose differs')
   require((row['startSample'],row['endSample'])==(pp[0]['startSample'],pp[-1]['endSample'])and row['start']==pp[0]['startSample']/RATE and row['end']==pp[-1]['endSample']/RATE,'ASR25 paragraph sample clock differs')
 byid={p['sceneId']:p for p in parts};sentences=[]
 for g in logical:
  pp=[byid[sid]for sid in g['physicalSceneIds']];a,b=pp[0]['startSample'],pp[-1]['endSample']
  sentences.append(dict(sceneId=g['logicalSceneId'],logicalSceneId=g['logicalSceneId'],paragraph=g['paragraph'],sentenceIndexZeroBased=g['logicalSentenceIndexZeroBased'],logicalSentenceIndexZeroBased=g['logicalSentenceIndexZeroBased'],canonicalKo=g['canonicalText'],paragraphCharRange=g['sourceCharRange'],physicalSceneIds=g['physicalSceneIds'],startSample=a,endSample=b,startFrame=frame_from_sample(a),endFrameExclusive=frame_from_sample(b),rawWav=pp[0]['rawWav']if len(pp)==1 else None))
 sentences[-1]['endFrameExclusive']=ceil_frame(position)
 return dict(voiceFingerprint=voice['fingerprint'],aggregate=voice['aggregateWav'],timing=voice['timing'],sampleRate=RATE,totalSamples=position,totalFrames=ceil_frame(position),rawSelectedTakes=103,logicalGroupCount=96,canonicalExactConcatVerified=True,physicalComponents=parts,sentences=sentences,automaticSpeechPass=False)

def boundary_support(binding):
 if not SUPPORT.exists():return {}
 require(SUPPORT_SHA and sha(SUPPORT)==SUPPORT_SHA,'New current-source p14 display-boundary proof freeze pending/changed')
 proof=read(SUPPORT);require(proof.get('schemaVersion')=='06.02-explicit-raw-word-boundary-support-v2'and proof.get('topicId')=='06.02'and proof.get('sourceNarration')==pin(NARRATION)and proof.get('status')=='root-accepted-exact-word-end-for-display-clock-only','Current V4 p14 word-proof source binding differs')
 require(all(proof.get(k)is False for k in('aliasesApplied','recognitionModified','pcmModified','actualListening','automaticSpeechPass','humanApproval')),'Word proof is display-only, never speech/hearing approval')
 rows=proof.get('bindings',[]);require(len(rows)==1 and rows[0].get('sceneId')=='p014-c03','Only exact one-unit p14 display support permitted')
 row=rows[0];ss=next(s for s in binding['sentences']if s['sceneId']=='p014-c03');require(len(ss['physicalSceneIds'])==1 and ss['physicalSceneIds'][0]==row['sceneId']and ss['canonicalKo']==row['canonicalKo']and row.get('canonicalCharOffsets')==[13,14]and row.get('canonicalLeftWord')=='뒤에는'and row.get('method')=='explicit-one-sided-actual-whole-word-end','P14 physical/logical/char scope changed')
 require(all(row.get(k)is True for k in('reuseOnlyIfSameRawWavAndPcm','requireCurrentBlindWordRecordSameLocalTimestamp','noFallbackToCharacterRatio')),'P14 display proof must retain its exact unchanged raw-word policy')
 for k in('sha256','pcmSHA256','sampleRate','frames'):require(ss['rawWav'][k]==row['rawWav'][k],'P14 support requires same exact physical raw take: '+k)
 assert_pin(row['rawWav']);assert_pin(row['sourceAsrRecord']);origin=read(row['sourceAsrRecord']['path']);require(origin['task']['sceneId']==row['sceneId']and origin['task']['pcmIdentity']['pcmSHA256']==row['rawWav']['pcmSHA256'],'Original p14 ASR record belongs to another physical PCM')
 return {row['sceneId']:dict(row,supportProof=pin(SUPPORT))}

def assemble_logical(sentence,parts,aligned):
 """Translate exact source char/sample coordinates; no character-to-time scale."""
 words=[];boundaries=[];unsupported=[];reviews=[];word_offset=0;lexical_offset=0
 for p in parts:
  a=aligned[p['sceneId']];offset=p['logicalSourceCharRange'][0]
  require(sentence['canonicalKo'][offset:p['logicalSourceCharRange'][1]]==p['canonicalKo'],'Physical/logical literal char placement changed')
  words.extend(dict(w,sourcePhysicalSceneId=p['sceneId'],sourcePhysicalWordIndex=w['sourceWordIndex'],logicalSceneId=sentence['sceneId'])for w in a['words'])
  for row in a['canonicalWordBoundaries']:
   boundaries.append(dict(row,charOffset=offset+row['charOffset'],canonicalWordBoundaryIndex=lexical_offset+row['canonicalWordBoundaryIndex'],sourceWordIndices=[i+word_offset for i in row['sourceWordIndices']],sourcePhysicalSceneId=p['sceneId'],physicalCharOffset=row['charOffset']))
  unsupported.extend(dict(row,charOffset=offset+row['charOffset'],sourcePhysicalSceneId=p['sceneId'])for row in a['unsupportedWordBoundaries'])
  reviews.append(dict(sourcePhysicalSceneId=p['sceneId'],logicalSourceCharRange=p['logicalSourceCharRange'],**a['alignmentReview']));word_offset+=len(a['words']);lexical_offset+=len(re.findall(r'\S+',p['canonicalKo']))
 boundaries.sort(key=lambda r:r['charOffset']);require(len({r['charOffset']for r in boundaries})==len(boundaries)and all(a['sample']<=b['sample']for a,b in zip(boundaries,boundaries[1:])),'Logical actual word boundaries duplicate/reverse')
 recognized=' '.join(a['recognizedLiteral'].strip()for a in reviews)
 return dict(sentence,words=words,canonicalWordBoundaries=boundaries,unsupportedWordBoundaries=unsupported,physicalComponents=parts,alignmentReview=dict(expectedLiteral=sentence['canonicalKo'],recognizedLiteral=recognized,comparison=asr.comparison(sentence['canonicalKo'],recognized),physicalLiteralReviews=reviews,aliasesApplied=False,automaticSpeechPass=False,humanListening=False,physicalSpeechGapPolicy='Unchanged actual component lead/tail PCM retained; each side of a physical join uses its own measured word edge'))

def build(narration,component_plan,clauses,translated,review,binding,support=None):
 require(clauses['sourceNarration']['sha256']==component_plan['sourceNarrationSHA256']and translated['sourceNarration']==clauses['sourceNarration'],'V4 caption/translated current-source binding differs')
 require(len(review.get('takes',[]))==103 and len(review.get('boundaryWindows',[]))==102,'All103 raw take/102join records required')
 normal,bold,_=old.base.base.fonts();style=clauses['style'];require((style['fontSizePx'],style['maxTextWidthPx'],style['maxLines'],style['fontWeight'],style['emphasisFontWeight'])==(48,800,2,500,700)and sha(style['fontPath'])==style['fontSHA256'],'Approved48px/800/2line font geometry changed')
 takes={t['task']['sceneId']:t for t in review['takes']};require(len(takes)==103,'Duplicate/missing103 raw take IDs')
 parts={p['sceneId']:p for p in binding['physicalComponents']};aligned={sid:old.aligned_sentence(p,takes[sid],(support or{}).get(sid))for sid,p in parts.items()}
 groups=clauses['groups'];anchors=translated['groups'];require(len(groups)==len(anchors)==len(binding['sentences'])==96,'Exactly96 logical caption/translated groups required')
 sentences=[];cues=dict(ko=[],en=[]);group_rows=[]
 for ss,g,a in zip(binding['sentences'],groups,anchors):
  require(g['ko']==a['ko']==ss['canonicalKo']and g['paragraph']==ss['paragraph']and g['koSourceCharRange']==ss['paragraphCharRange']and a['groupId']==g['id'],'Current96 logical caption/source-char mapping differs')
  sentence=assemble_logical(ss,[parts[sid]for sid in ss['physicalSceneIds']],aligned);sentence['groupId']=g['id'];sentences.append(sentence);begin,end=char_boundary(sentence,0),char_boundary(sentence,len(g['ko']))
  group_rows.append(dict(id=g['id'],paragraph=g['paragraph'],beatId=g['beatId'],sceneId=ss['sceneId'],physicalSceneIds=ss['physicalSceneIds'],startFrame=begin['frame'],endFrameExclusive=end['frame'],startSample=begin['sample'],endSample=end['sample'],koSourceCharRange=g['koSourceCharRange'],enSourceCharRange=g['enSourceCharRange']))
  for cue in g['koCues']:
   x,y=cue['groupCharRange'];left,right=char_boundary(sentence,x),char_boundary(sentence,y);require(right['sample']>left['sample'],'Caption lacks positive actual word sample span')
   row=old.display_cue(cue,'ko',g,left['frame'],right['frame'],normal,bold);row.update(sceneId=ss['sceneId'],physicalSceneIds=ss['physicalSceneIds'],startSample=left['sample'],endSample=right['sample'],literalAlignment=dict(expectedLiteral=cue['text'],canonicalGroupCharRange=[x,y],actualStartBoundary=left,actualEndBoundary=right,aliasesApplied=False),actualListening=False);cues['ko'].append(row)
  require([c['enCueId']for c in a['cues']]==[c['id']for c in g['enCues']],'Translated logical cue ID order differs');coverage=0
  for cue,anchor in zip(g['enCues'],a['cues']):
   x,y=anchor['koGroupCharRange'];ca,cb=anchor['koCoverageGroupCharRange'];require(g['ko'][x:y]==anchor['koLiteralText']and cue['text']==anchor['enText']and ca==coverage and g['ko'][ca:cb]==anchor['koCoverageLiteral'],'Translated exact logical semantic anchor coverage differs');coverage=cb
   left,right=char_boundary(sentence,x),char_boundary(sentence,y);require(right['sample']>left['sample'],'English display slot lacks positive actual KO-word span')
   row=old.display_cue(cue,'en',g,left['frame'],right['frame'],normal,bold);row.update(sceneId=ss['sceneId'],physicalSceneIds=ss['physicalSceneIds'],startSample=left['sample'],endSample=right['sample'],timingBasis='Exact authored logical KO-word display partition; not English ASR or character ratio',spokenLiteralAnchorKo=anchor['koLiteralText'],semanticWindowKo=anchor['semanticWindowKo'],translationReordered=a['translationReordered'],translatedTimingReviewPending=True,actualListening=False);cues['en'].append(row)
  require(coverage==len(g['ko']),'Translated anchors omit logical source text')
 for lang,rows in cues.items():require(all(a['endSample']<=b['startSample']and a['endFrameExclusive']<=b['startFrame']for a,b in zip(rows,rows[1:])),lang+' actual caption intervals overlap')
 require((len(cues['ko']),len(cues['en']))==(190,234),'Exact190KO/234EN retained display IDs required')
 paragraphs=[]
 for n in range(1,26):
  ss=[s for s in sentences if s['paragraph']==n];paragraphs.append(dict(paragraph=n,startSample=ss[0]['startSample'],endSample=ss[-1]['endSample'],startFrame=ss[0]['startFrame'],endFrameExclusive=ss[-1]['endFrameExclusive'],sceneIds=[s['sceneId']for s in ss],physicalSceneIds=[p['sceneId']for p in binding['physicalComponents']if p['paragraph']==n],recognitionBasis='Exact103component raw clocks assembled into96logical teaching groups'))
 paragraphs[-1]['endFrameExclusive']=binding['totalFrames']
 return dict(schemaVersion=SCHEMA,topicId='06.02',fps=FPS,totalFrames=binding['totalFrames'],captions=cues,sentences=sentences,physicalComponents=binding['physicalComponents'],groups=group_rows,paragraphs=paragraphs,audioClock=dict(rawSampleRate=RATE,totalRawSamples=binding['totalSamples'],rawAggregate=binding['aggregate'],rawTiming=binding['timing'],visualFinalFrameCeil=True,noAudioTailPadding=True,addedObservationHoldSamples=0,mixedAudioTimingAccepted=False,finalMix=None),voiceBinding={k:v for k,v in binding.items()if k not in('sentences','physicalComponents')},alignmentReview=dict(physicalTakeCount=103,logicalGroupCount=96,aliasesApplied=False,automaticSpeechPass=False,rawLiteralDifferencesPreserved=True,unsupportedWordBoundariesPreserved=True),automaticSpeechPass=False,actualListening=False,actualFinalPlayback=False,humanTimingReviewRequired=True,platformActions=[])

def prepare(asr_review=None,voice_evidence=None,audio_build=None,clock_proof=None):
 narration,plan,clauses,translated=sources();vp=Path(voice_evidence or VOICE).resolve();require(vp.is_file(),'Exact103 physical voice is not complete')
 if vp==VOICE.resolve():require(VOICE_STATE.is_file()and read(VOICE_STATE).get('completed')is True,'103 physical voice controller remains active/incomplete')
 voice=read(vp);require(len(voice.get('sceneWavs',[]))==103,'Waiting exact103 proof; previous96 evidence preserved')
 expected=(ROOT/'shared/output/architectural-111-20261106/06-02/voice-attempts'/voice['fingerprint'][:24]).resolve();require(Path(voice['output']).resolve()==expected,'Current103 voice output escaped exact selected scope')
 require(all(Path(row['path']).resolve()==expected/'chunks'/(scene['id']+'-scene.wav')for scene,row in zip(voice['identity']['scenes'],voice['sceneWavs'])),'Physical103 raw paths differ from exact selected chunks')
 qa=asr_factory();job=current_job(qa);rp=Path(asr_review or(Path(job['output'])/'review.json')).resolve();review=verified_asr_review(rp);binding=voice_binding(voice,review,narration,plan);support=boundary_support(binding);result=build(narration,plan,clauses,translated,review,binding,support)
 require(job['identity']['voiceFingerprint']==voice['fingerprint'],'Current205 ASR belongs to another raw voice')
 if audio_build or clock_proof:raise Pending('V2 scalar-clock acceptance must be separately verified against the new103 mix; raw timestamps remain unchanged, no implicit reuse')
 paths=[('narration',NARRATION),('semanticComponents',COMPONENTS),('captionClauses',CLAUSES),('translatedAnchors',ANCHORS),('voiceEvidence',vp),('rawAsrReview',rp),('rawAsrJob',rp.parent/'job.json'),('rawAsrAdapter',ASR_PATH),('font',Path(clauses['style']['fontPath'])),('captionAdapter',Path(__file__)),('previousLiteralPrimitives',OLD_PATH)]
 if support:paths.append(('explicitWordBoundarySupport',SUPPORT))
 result['inputs']=[dict(role=role,**pin(path))for role,path in paths];result['policy']=POLICY;result['fingerprint']=digest(dict(inputs=result['inputs'],policy=POLICY));return result
def verify_existing(path):
 path=Path(path).resolve();actual=read(path);require(actual.get('schemaVersion')==SCHEMA and actual.get('topicId')=='06.02','Not selected06 captionV2 timing')
 refs={r['role']:r for r in actual.get('inputs',[])}
 for row in refs.values():assert_pin(row)
 fresh=prepare(refs['rawAsrReview']['path'],refs['voiceEvidence']['path']);require(actual==fresh,'Existing captionV2 artifact differs from current exact103/96 source/ASR clocks')
 require(path==(MEDIA/'caption-timing-v2'/fresh['fingerprint'][:24]/'caption-timing.json').resolve(),'CaptionV2 timing escaped its immutable selected output')
 return dict(timing=actual,voice=read(refs['voiceEvidence']['path']),asr=read(refs['rawAsrReview']['path']))
def write_outputs(result):
 target=MEDIA/'caption-timing-v2'/result['fingerprint'][:24];files={'caption-timing.json':json.dumps(result,ensure_ascii=False,indent=2)+'\n','captions.ko.srt':old.base.srt(result['captions']['ko'],'ko'),'captions.en.srt':old.base.srt(result['captions']['en'],'en')}
 for name,text in files.items():
  if(target/name).exists():require((target/name).read_text(encoding='utf8')==text,'Preserve different prior captionV2 output')
 for row in result['inputs']:assert_pin(row)
 target.mkdir(parents=True,exist_ok=True)
 for name,text in files.items():
  if not(target/name).exists():
   with(target/name).open('x',encoding='utf8')as f:f.write(text)
 return target
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--asr-review');p.add_argument('--voice-evidence');p.add_argument('--write',action='store_true');p.add_argument('--verify-existing');a=p.parse_args()
 try:
  result=verify_existing(a.verify_existing)['timing']if a.verify_existing else prepare(a.asr_review,a.voice_evidence);output=str(write_outputs(result))if a.write else None;print(json.dumps(dict(ready=True,fingerprint=result['fingerprint'],physicalComponents=103,logicalGroups=96,output=output,written=a.write,modelStarted=False)))
 except(Pending,FileNotFoundError)as e:
  if a.write:raise
  print(json.dumps(dict(ready=False,reason=str(e),written=False,modelStarted=False,rendererStarted=False)))
if __name__=='__main__':main()
