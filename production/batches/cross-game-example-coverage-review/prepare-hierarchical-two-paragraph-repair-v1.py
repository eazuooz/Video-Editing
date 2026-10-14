"""Preserve all4 PCM and diagnostics; request only2 verbatim candidate paragraphs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
whole=read(V/'additions-whole-asr-execution-v1.json');contexts=read(V/'additions-contexts-asr-execution-v1.json')
assert whole['actualExitObserved'] and whole['actualOuterExitCode']==0 and whole['completed']==4
assert contexts['actualExitObserved'] and contexts['actualOuterExitCode']==0 and contexts['completed']==18
tts=read(V/'narration-additions-execution-v1.json');assert tts['actualExitObserved'] and tts['ownedClosureVerified']
ko=read(V/'script/additions.ko.json');en=read(V/'script/additions.en.json')
ko_scene=next(x for x in ko['scenes'] if x['id']=='08a');en_scene=next(x for x in en['scenes'] if x['id']=='08a')
held_path=V/'additions-whole-and-independent-held-review-v1.json';assert not held_path.exists()
notes={
 '08a-p01':'Expected 주민에게 일을 is unrecovered: whole 주민의 기일/independent 주민의 길. Preserve both raw results; one exact original-paragraph repair candidate only, no claim of acoustically proven incorrect pronunciation.',
 '08a-p04':'Expected 맞는 가지 is unrecovered as 만능가지 in both current whole and independent results. Preserve the original PCM; verify one verbatim candidate before any adoption.',
 '04a-p02':'표식의/표시계 persists as a transcription alternative; the assignment1-to2 claim and complete ending recover. No exact pronunciation approval.',
 '10a-p01':'Independent 수무는 differs from 수문은; whole recovers 수문은 with the complete water-height/manual-signal prerequisite. Preserve as recognizer disagreement for current mixed review.',
 '10a-p02':'Independent 숨은 differs from 수문, while whole recovers 수문 설정. Independent Bad Tide recovers the source-name meaning of 배드타이드; whole Bedtide spelling is preserved. Units1m/2m recover. No spelling/phonetic authority inferred from raw recognition.',
 '10a-p04':'Independent 숨은/whole 수문 disagreement preserved. Both height/signal children, separate lever feature, teal reference and document-parent disclaimer recover.',
 '10a-p05':'Independent 선로 recovers the whole 설로 alternative; complete conclusion recovers.',
 '08a-p05':'The complete independent final paragraph has the expected ending and no whole-result extra greeting. Raw whole greeting57.20..57.26/two zero-duration tokens is retained as a timing artifact candidate; do not use it for exact-script cues.'}
rows=[]
for r in contexts['results']:
 w=next(x for x in whole['results'] if x['id']==r['sceneId'])
 rows.append(dict(id=r['id'],expectedKo=r['expectedKo'],currentIndependentText=r['text'],
  correspondingWholeText=w['text'],sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],
  contextSha256=r['contextSha256'],exactSourceSampleBytesMatched=r['exactSourceSampleBytesMatched'],
  firstWords=r['words'][:3],lastWords=r['words'][-4:],
  coreReadbackStatus='held-for-single-verbatim-candidate' if r['id'] in ['08a-p01','08a-p04'] else 'core-content-recovered-with-disclosed-alternatives;currentmixed-review-pending',
  note=notes.get(r['id'],'Full expected content and complete beginning/ending directly compared; whitespace/numeric orthography alternatives only.'),
  humanListeningApproved=False,humanPronunciationApproved=False))
assert len(rows)==18 and all(r['exactSourceSampleBytesMatched'] for r in rows)
stamp=datetime.now(timezone.utc).isoformat()
held=dict(recordedAt=stamp,actualWhole=dict(session=58603,exit=0,completion='31951f',closure='38a4e8 exit0'),
 actualContexts=dict(session=90741,exit=0,completion='55dcf8',closure='a75919 exit0'),
 actualFullExpectedIndependentAndEdgesRead='ab4156 exit0,all18pairs/start/end words',
 all18DirectlyCompared=True,rows=rows,heldParagraphs=['08a-p01','08a-p04'],
 sourceUnmixedFinalContentApproved=False,allOther16CoreClaimsRecovered=True,
 humanWholeListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
 original12AndNew4PcmPreserved=True,originalSourceOrNativeResearchRepeated=False)
repair_ko=dict(title='스톰 두 원문 문단의 독립 교정 후보',scenes=[])
repair_en=dict(title='Two Verbatim Storm Paragraph Repair Candidates',scenes=[])
for index,new_id in [(0,'08r1'),(3,'08r4')]:
 repair_ko['scenes'].append(dict(id=new_id,title='Original08a-p'+str(index+1),lines=[ko_scene['lines'][index]]))
 repair_en['scenes'].append(dict(id=new_id,title='Original08a-p'+str(index+1),lines=[en_scene['lines'][index]]))
ko_path=V/'script/two-paragraph-repair-v1.ko.json';en_path=V/'script/two-paragraph-repair-v1.en.json'
manifest=read(V/'tts-additions-manifest-v1.json')
manifest['paths'].update(script=ko_path.relative_to(ROOT).as_posix(),scriptEn=en_path.relative_to(ROOT).as_posix())
manifest['tts'].update(outputDir='shared/output/narration/hierarchical-game-outlines/two-paragraph-repair-v1',filenameStem='hierarchical-two-paragraph-repair-v1')
manifest['scope']='Only two exact original08a paragraphs as candidates; all original12 and additive4PCM preserved; adoptionfalse.'
manifest_path=V/'tts-two-paragraph-repair-manifest-v1.json'
review_path=V/'two-paragraph-paired-script-direct-review-v1.json';request_path=V/'narration-two-paragraph-repair-request-v1.json'
review=dict(recordedAt=stamp,contentReadyForApprovedVoiceMeasurement=True,originalAllWordingAndOrderPreserved=True,
 pairedWholeTextReview=True,overviewPromiseReview=True,repairOnly=True,
 exactOriginalParagraphIndices=[0,3],all2FullKoEnParagraphsDirectlyCompared=True,
 original12PcmRegenerated=0,original4AdditivePcmRegenerated=0,
 failedDiagnostics=held_path.relative_to(ROOT).as_posix(),candidateAdopted=False,
 humanListeningApproved=False,humanPronunciationApproved=False,finalMixedOrPixelsApproved=False)
protected=tts['protectedInputs']+tts['results']+[dict(path=held_path.relative_to(ROOT).as_posix(),sha256=None)]
assert len(protected)==137
request=dict(schemaVersion=1,recordedAt=stamp,slug='hierarchical-game-outlines',manifest=manifest_path.relative_to(ROOT).as_posix(),
 scriptReview=review_path.relative_to(ROOT).as_posix(),sourceReview='projects/hierarchical-game-outlines/revision-teaching-clarity-v1/source-action-planning-direct-review-v1.json',
 total=2,paragraphs=2,pairedWholeTextReview=True,overviewPromiseReview=True,baselineApprovedPcmRegeneration=0,
 protectedInputs=protected,scenes=[dict(id=s['id'],text=s['lines'][0],path=manifest['tts']['outputDir']+'/chunks/'+s['id']+'-scene.wav') for s in repair_ko['scenes']],
 candidatesAdopted=False,original08aPcmOverwritten=False)
for p in [ko_path,en_path,manifest_path,review_path,request_path]:assert not p.exists()
for s in request['scenes']:assert not (ROOT/s['path']).exists()
save(held_path,held);protected[-1]['sha256']=sha(held_path)
for p,d in [(ko_path,repair_ko),(en_path,repair_en),(manifest_path,manifest),(review_path,review),(request_path,request)]:save(p,d)
# The inspected four-item worker/observer/closure are parameterized into a new
# version, retaining the same20s/600s guards and owned-token closure.
renames={
 'narration-additions-execution-v1.json':'narration-two-paragraph-repair-execution-v1.json',
 'narration-additions-request-v1.json':'narration-two-paragraph-repair-request-v1.json',
 'narration-additions-session-v1.json':'narration-two-paragraph-repair-session-v1.json',
 'narration-additions-waiting-v1.json':'narration-two-paragraph-repair-waiting-v1.json',
 'resource-before-additions-voice-v1.json':'resource-before-two-paragraph-repair-voice-v1.json',
 'additions-owned-idle-guard-v1.json':'two-paragraph-repair-owned-idle-guard-v1.json',
 'additions-voice-closure-verification-v1.json':'two-paragraph-repair-voice-closure-verification-v1.json',
 'narration-additions-v1.log':'narration-two-paragraph-repair-v1.log',
 'causal-paired-script-direct-review-v1.json':'two-paragraph-paired-script-direct-review-v1.json',
 'render-hierarchical-additions-voice-v1.py':'render-hierarchical-two-paragraph-repair-v1.py'}
jobs=[]
for old,new in [('render-hierarchical-additions-voice-v1.py','render-hierarchical-two-paragraph-repair-v1.py'),
 ('observe-hierarchical-additions-voice-resource-v1.py','observe-hierarchical-two-paragraph-repair-resource-v1.py'),
 ('register-hierarchical-additions-voice-v1.py','register-hierarchical-two-paragraph-repair-v1.py'),
 ('verify-hierarchical-additions-voice-exit-v1.py','verify-hierarchical-two-paragraph-repair-exit-v1.py')]:
 src=(B/old).read_text('utf8')
 for x,y in renames.items():src=src.replace(x,y)
 src=src.replace("request['total']==4 and request['paragraphs']==18","request['total']==2 and request['paragraphs']==2")
 src=src.replace('total=4','total=2').replace("state['total']==4","state['total']==2").replace("state['results'])==4","state['results'])==2")
 src=src.replace('len(protected)==129','len(protected)==137')
 src=src.replace('Four additive scenes only','Two verbatim paragraph candidates only').replace('Four items','Two candidates')
 src=src.replace('four-items','two-candidates').replace('four-item','two-candidate').replace('4items/18pairedparagraphs','2items/2pairedparagraphs')
 src=src.replace('whole4 and18independent','whole2 and2independent').replace('wholefour currentPCM','wholetwo currentPCM').replace('allfour currentwhole PCM and18independent','alltwo currentwhole PCM and2independent')
 src=src.replace('wholefour currentPCM ASR once','wholetwo candidatePCM ASR once')
 src=src.replace('original12PcmRegenerated=0,humanListeningApproved','original12PcmRegenerated=0,original4AdditivePcmRegenerated=0,candidateAdopted=False,humanListeningApproved')
 assert not (B/new).exists();compile(src,str(B/new),'exec');jobs.append((B/new,src))
for p,src in jobs:p.write_text(src,'utf8')
cp_path=V/'latest-checkpoint.json';cp=read(cp_path)
cp.update(recordedAt=stamp,stage='two-original08a-paragraphs-held;single-verbatim-candidate-batch-prepared',
 additiveUnmixedReview=held_path.relative_to(ROOT).as_posix(),repairVoiceRequest=request_path.relative_to(ROOT).as_posix(),
 activeOwnedWorkers=0,ownedJob=None,twoRepairCandidatesAdopted=False,
 next='Fresh current duplicate gate/stable20s resource, one2paragraph candidate batch only. Then actualownedclosure/full2+independent2 comparison before byte-preserving08a splice. Original12+new4PCM and complete source/native reviews must not repeat.')
save(cp_path,cp)
print(json.dumps(dict(preparedOnly=True,held2Paragraphs=True,total=2,protected=137,original12AndNew4PcmPreserved=True,candidateAdoption=False,modelRequests=0)))
