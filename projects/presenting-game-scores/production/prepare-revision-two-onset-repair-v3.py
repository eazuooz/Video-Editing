"""Preserve every earlier PCM/script; prepare two local pronunciation repairs only."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).parent;B=P/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def fresh(p,j):
 assert not p.exists(),f'Preserve existing {p}'
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')

state=read(B/'voice-decoding-asr-execution-v2.json')
assert state['exitCode']==0 and state['actualExitObserved']
beam=read(B/'voice-decoding-asr-v2/asr.json');assert beam['complete'] and len(beam['results'])==4
findings={
 'audit-complete-leading-sentence':'Persistent 스테트리스 onset in complete padded sentence, whole exact join, greedy and independent beam5. Hold the current new p2; prepend the natural contextual phrase 앞서 본 in a new candidate rather than cutting consonants or fabricating approval.',
 'overview-complete-p2':'Persistent 기어가 for intended 기여가 in independent sentence, whole overview and beam5. Preserve the viewer question, example order and outcome; clarify this clause as 카드가 점수에 반영되는 과정과 손패 결과가 누적되는 모습.',
 'events-complete-last-sentence':'중의/중에 remains a recognizer/particle pronunciation alternative; the complete sentence and its meaning are retained. Human pronunciation stays pending; no synthesis solely for this particle.',
 'audit-whole-joined':'Same onset persists inside retained p1/new p2/retained p3, so zero-duration leading 자 in a different recognition cannot account for the persistent onset. All other clauses/endings are present. Preserve this join as held history.'}
for x in beam['results']:
 assert sha(ROOT/x['sourcePath'])==x['sourceSha256']
 x['directReview']=True;x['finding']=findings[x['id']]
fresh(B/'voice-decoding-direct-review-v2.json',dict(schemaVersion=1,reviewedAt=now(),allFourFullTextsAndWordTimestampsDirectlyCompared=True,results=beam['results'],currentCompleteVoiceApproved=False,onsetUnresolved=True,humanListening='pending',humanPronunciation='pending',noNewRecognitionOrAudioFromReview=True))

oldreq=read(B/'narration-tts-request-v1.json')
for x in oldreq['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
ko=read(B/'script/narration.ko.json');en=read(B/'script/narration.en.json')
oldko=copy.deepcopy(ko);olden=copy.deepcopy(en)
ko1=next(x for x in ko['scenes'] if x['id']=='01-overview')
en1=next(x for x in en['scenes'] if x['id']=='01-overview')
ko1['lines'][1]='먼저 테트리스의 줄 수와 점수를 구분하고, 발라트로에서 카드가 점수에 반영되는 과정과 손패 결과가 누적되는 모습을 보겠습니다.'
en1['lines'][1]='We will first separate line counts from points in Tetris, then examine how cards contribute to scoring and how hand results accumulate in Balatro.'
ko10=next(x for x in ko['scenes'] if x['id']=='10-audit-and-close')
en10=next(x for x in en['scenes'] if x['id']=='10-audit-and-close')
assert ko10['lines'][1].startswith('테트리스에서는')
ko10['lines'][1]='앞서 본 '+ko10['lines'][1]
en10['lines'][1]=en10['lines'][1].replace('In Tetris,','In the Tetris examples,',1)
changes=[]
for a,b,c,d in zip(oldko['scenes'],ko['scenes'],olden['scenes'],en['scenes']):
 assert a['id']==b['id']==c['id']==d['id']
 assert len(a['lines'])==len(b['lines'])==len(c['lines'])==len(d['lines'])
 for i,(ak,bk,ae,be) in enumerate(zip(a['lines'],b['lines'],c['lines'],d['lines'])):
  if ak!=bk or ae!=be:
   changes.append(dict(scene=a['id'],paragraph=i,oldKo=ak,newKo=bk,oldEn=ae,newEn=be))
assert [(x['scene'],x['paragraph']) for x in changes]==[('01-overview',1),('10-audit-and-close',1)]
fresh(B/'script/narration-v2.ko.json',ko);fresh(B/'script/narration-v2.en.json',en)
smallko=dict(title=ko['title'],scenes=[copy.deepcopy(ko1),dict(id='r10-audit-and-close-p2',title=ko10['title'],lines=[ko10['lines'][1]])])
smallen=dict(title=en['title'],scenes=[copy.deepcopy(en1),dict(id='r10-audit-and-close-p2',title=en10['title'],lines=[en10['lines'][1]])])
smallko['scenes'][0]['id']='r01-overview';smallen['scenes'][0]['id']='r01-overview'
fresh(B/'script/onset-repair-v3.ko.json',smallko);fresh(B/'script/onset-repair-v3.en.json',smallen)
review=dict(schemaVersion=1,reviewedAt=now(),allNineteenKoEnScenesDirectlyCompared=True,allThirtyNineParagraphsPreserved=True,changes=changes,contentReadyForApprovedVoiceMeasurement=True,overviewPromiseReview=True,overviewQuestion=ko1['lines'][0],overviewOrder=['Tetris quantities/evaluation','Balatro cards/hand results/round total','opponent comparison','labels/feedback/action decision'],targetOverviewSeconds=[20,30],actualOverviewSeconds=None,oldP1P3AndOtherPcmRemainExact=True,currentUnmixedVoiceApproved=False,humanListening='pending',humanPronunciation='pending',reason='Two unresolved new-voice recognition onsets; scope is localized refinement before approval, not regeneration of approved passages.')
fresh(B/'onset-repair-paired-direct-review-v3.json',review)
manifest=read(B/'voice-manifest-v1.json')
manifest['status']='two-local-onset-candidates-prepared-only'
manifest['tts'].update(outputDir='shared/output/narration/presenting-game-scores/qwen3-balatro60-onset-repair-v3',filenameStem='balatro60-onset-repair-v3')
manifest['paths']['script']=rel(B/'script/onset-repair-v3.ko.json');manifest['paths']['scriptEn']=rel(B/'script/onset-repair-v3.en.json')
manifest['approvals']={k:(False if isinstance(v,bool) else v) for k,v in manifest['approvals'].items()}
manifest['editing']['timingStatus']='pending-real-two-candidate-voice-measurement'
fresh(B/'voice-manifest-v3.json',manifest)
protected=list(oldreq['protectedInputs'])
extra=[B/'narration-tts-request-v1.json',B/'voice-decoding-direct-review-v2.json',B/'preserved-pcm-complete-joins-v1.json',B/'measured-editorial-candidate-v2.json',B/'script/narration-v2.ko.json',B/'script/narration-v2.en.json',B/'script/onset-repair-v3.ko.json',B/'script/onset-repair-v3.en.json',B/'voice-manifest-v3.json',B/'onset-repair-paired-direct-review-v3.json']
extra += [ROOT/x['path'] for x in read(B/'narration-tts-execution-v2.json')['results']]
extra += [ROOT/x['path'] for x in read(B/'preserved-pcm-complete-joins-v1.json')['scenes'] if x.get('assembled')]
known={x['path'] for x in protected}
for p in extra:
 if rel(p) not in known:protected.append(dict(path=rel(p),sha256=sha(p)));known.add(rel(p))
scenes=[dict(id=x['id'],path=manifest['tts']['outputDir']+'/chunks/'+x['id']+'-scene.wav',text=' '.join(x['lines']),paragraphs=len(x['lines'])) for x in smallko['scenes']]
request=dict(schemaVersion=1,preparedAt=now(),slug='presenting-game-scores',revision='balatro60-tetris40-two-onset-v3',manifestOverride=rel(B/'voice-manifest-v3.json'),pairedWholeTextReview=True,overviewPromiseReview=True,scriptReview=rel(B/'onset-repair-paired-direct-review-v3.json'),protectedInputs=protected,scenes=scenes,unchangedSelectedPcmRegenerated=False,ttsStarted=False,humanListening='pending',humanPronunciation='pending',publicRights='pending',gpuResearchPolicy=oldreq['gpuResearchPolicy'])
fresh(B/'narration-tts-request-v3.json',request)
src=P/'render-balatro60-revision-voice-v2.py';dst=P/'render-balatro60-revision-voice-v3.py';assert not dst.exists()
t=src.read_text('utf-8')
for a,b in [('narration-tts-execution-v2.json','narration-tts-execution-v3.json'),('narration-tts-request-v1.json','narration-tts-request-v3.json'),('narration-tts-session-v2.json','narration-tts-session-v3.json'),('narration-tts-waiting-v2.json','narration-tts-waiting-v3.json'),('voice-resource-before-v2.json','voice-resource-before-v3.json'),('==11','==2'),("'total':11","'total':2"),('eleven','two'),('11 changed','2 local'),('31 protected','all protected'),('all11','both2'),('Only11','Only2')]:t=t.replace(a,b)
dst.write_text(t,'utf-8')
verify=P/'verify-revision-voice-research-resume-v3.py';assert not verify.exists()
t=(P/'verify-revision-voice-research-resume-v2.py').read_text('utf-8')
for a,b in [('narration-tts-session-v2.json','narration-tts-session-v3.json'),('narration-tts-execution-v2.json','narration-tts-execution-v3.json'),('research-handoff-verification-v2.json','research-handoff-verification-v3.json'),('==11','==2'),('allElevenCurrentPcmHashesMatched','allTwoCurrentPcmHashesMatched'),('eleven-item','two-item'),('11-item','2-item')]:t=t.replace(a,b)
verify.write_text(t,'utf-8')
print(json.dumps(dict(preparedOnly=True,changedParagraphs=2,ttsItems=2,protectedInputs=len(protected),newVoiceStarted=False,oldPcmPreserved=True),ensure_ascii=False))
