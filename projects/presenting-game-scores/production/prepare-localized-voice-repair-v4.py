"""Preserve all completed voices; prepare only two exact-text localized takes."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, os, psutil, subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,value):
    t=p.with_name(p.name+'.preparing')
    t.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
    os.replace(t,p)
stamp=datetime.now(timezone.utc).isoformat()
sp=BASE/'observation-candidates-targets-asr-execution-v3.json';state=read(sp)
assert state['exitCode']==0 and state['completed']==state['total']==2
try:assert abs(psutil.Process(state['pid']).create_time()-state['createTime'])>=.01
except psutil.NoSuchProcess:pass
state.update(actualExitObserved=True,actualOuterExitCode=0,actualOuterSessionId=43584,
    actualWorkerAlive=False,actualExitObservedAt=stamp);save(sp,state)
sessionp=sp.with_name(sp.stem+'.session.json');s=read(sessionp)
assert s['sessionId']==43584 and s['pid']==state['pid']
s.update(actualExitObserved=True,exitCode=0,workerExpectedRunning=False,observedAt=stamp);save(sessionp,s)
targets=read(BASE/'observation-candidates-targets-asr-v3/asr.json');assert targets['complete']
notes=[
 'The complete preceding first paragraph, remaining full guide and ending are recognized. 지금은 is again absent from the recognized guide, including inside the preceding semantic context. Preserve the source and uncertainty; do not assert an audible error or modify the script to the transcription.',
 'Both complete original p2 and candidate p3 represented; 배점표 remains correct. 점수의 is again represented as 점수. Preserve this function-word uncertainty and compare another full exact-text candidate, without changing the original claim or redoing the original ten voices.'
]
rows=[]
for d,note in zip(targets['results'],notes):
    p=BASE/'observation-candidates-targets-asr-v3'/(d['id']+'.json')
    assert read(p)==d and d['exactSourceSampleBytesMatched'] and not d['expectedWasRecognizerPrompt']
    assert sha(ROOT/d['contextPath'])==d['contextSha256'] and sha(ROOT/d['sourcePath'])==d['sourceSha256']
    rows.append(dict(id=d['id'],path=rel(p),sha256=sha(p),expectedKo=d['expectedKo'],actualText=d['text'],
        allExpectedAndEntireActualTextDirectlyRead=True,wordsAndFinalSoundDirectlyRead=True,
        exactCurrentSourcePcmMatched=True,observation=note))
targetreview=BASE/'observation-candidates-targets-direct-review-v3.json';assert not targetreview.exists()
save(targetreview,dict(schemaVersion=1,reviewedAt=stamp,allWholeTextsDirectlyCompared=True,
    allIndependentContextsDirectlyCompared=True,rows=rows,actualOuterExitCode=0,sessionId=43584,
    newCandidateWindowsDirectlyRead=26,wholeCount=11,independentAndJoinCount=13,targetCount=2,
    currentVoiceApproved=False,candidateParagraphsAdopted=False,actualSynthesisErrorConfirmed=False,
    finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending',
    resolvedRecognitionVariants=['04 배점표', '08 기여', '21 읽게 in independent and full join'],
    unresolvedRecognitionVariants=['17 missing 지금은 recognition','20 점수의/점수','16 왼쪽의/왼쪽에'],
    endingHeuristicUsedForApproval=False))

old_request=read(BASE/'observation-candidates-tts-request-v3.json')
old_review=read(ROOT/old_request['scriptReview'])
scripts={lang:read(ROOT/f'projects/presenting-game-scores/script/observation-candidates-v3.{lang}.json') for lang in ['ko','en']}
id_map=[('17-observe-named-fields','22-named-fields-guide-repair'),
        ('20-candidate-evaluation-p3','23-evaluation-p3-particle-candidate')]
paths={}
for lang in ['ko','en']:
    doc=copy.deepcopy(scripts[lang]);doc['scenes']=[]
    for old,new in id_map:
        scene=copy.deepcopy(next(x for x in scripts[lang]['scenes'] if x['id']==old))
        scene['id']=new;doc['scenes'].append(scene)
    p=ROOT/f'projects/presenting-game-scores/script/localized-voice-repair-v4.{lang}.json'
    assert not p.exists();save(p,doc);paths[lang]=p
manifest_path=BASE/'localized-voice-repair-voice-manifest-v4.json'
assert not manifest_path.exists()
manifest=json.loads((BASE/'observation-candidates-voice-manifest-v3.json').read_text('utf-8').replace('observation-candidates','localized-voice-repair').replace('-v3','-v4'))
save(manifest_path,manifest)
review_path=BASE/'localized-voice-repair-paired-direct-review-v4.json';assert not review_path.exists()
review_rows=[]
for old,new in id_map:
    detail=copy.deepcopy(next(x for x in old_review['rows'] if x['id']==old));detail.update(id=new,priorCandidateId=old)
    detail['ko']=next(x for x in read(paths['ko'])['scenes'] if x['id']==new)['lines']
    detail['en']=next(x for x in read(paths['en'])['scenes'] if x['id']==new)['lines']
    detail.update(fullKoEnDirectlyRead=True,originalWordsUnchanged=True,sourceConnectionUnchanged=True)
    review_rows.append(detail)
save(review_path,dict(schemaVersion=1,reviewedAt=stamp,contentReadyForApprovedVoiceMeasurement=True,
    pairedWholeTextReview=True,overviewPromiseReview=True,fullIndependentKoEnDirectlyCompared=True,
    sourceBank=old_review['sourceBank'],sourceBankSha256=old_review['sourceBankSha256'],rows=review_rows,
    priorDirectReview=rel(targetreview),priorDirectReviewSha256=sha(targetreview),
    purpose='Only one guide with persistent recognized onset omission and one exact-text paragraph with persistent function-word variation. Preserve the completed11 and original10 voices; no script shortening or transcript substitution.',
    preparedOnly=True,currentVoiceApproved=False,replacementsAdopted=False))

request=copy.deepcopy(old_request)
request.update(preparedAt=stamp,scriptReview=rel(review_path),manifestOverride=rel(manifest_path),total=2,
    originalElevenCandidatePcmRegenerated=False,purpose='Two complete localized takes only; all original arguments and candidate words preserved.')
new_scenes=[]
for old,new in id_map:
    row=copy.deepcopy(next(x for x in old_request['scenes'] if x['id']==old));row['id']=new
    row['path']=f'shared/output/narration/presenting-game-scores/qwen3-localized-voice-repair-v4/chunks/{new}-scene.wav'
    row['priorCandidateId']=old;new_scenes.append(row)
request['scenes']=new_scenes
protected=[ROOT/x['path'] for x in old_request['protectedInputs']]
protected += [paths['ko'],paths['en'],manifest_path,review_path,targetreview,
    BASE/'observation-candidates-whole-direct-review-v3.json',BASE/'observation-candidates-contexts-direct-review-v3.json',
    BASE/'candidate-complete-joins-pcm-verification-v3.json']
protected += [ROOT/x['path'] for x in read(BASE/'observation-candidates-tts-execution-v3.json')['results']]
request['protectedInputs']=[dict(path=rel(p),sha256=sha(p)) for p in dict.fromkeys(protected)]
request_path=BASE/'localized-voice-repair-tts-request-v4.json';assert not request_path.exists();save(request_path,request)

producer=(BASE/'render-observation-candidates-v3.py').read_text('utf-8').replace('observation-candidates','localized-voice-repair').replace('-v3','-v4')
producer=producer.replace('len(request[\'scenes\'])==11','len(request[\'scenes\'])==2').replace('total=11','total=2').replace("len(state['results'])==11","len(state['results'])==2")
producer=producer.replace('Nine fresh observation guides and two unadopted exact-text paragraph takes','Two localized exact-text takes; completed11 candidate PCM and original10 PCM are preserved')
producer=producer.replace('Prepared9 guides/9 paired paragraphs plus2 exact-text candidates','Prepared2 full exact-text localized takes only')
needle="sys.path.insert(0,str(ROOT/'qwen3-tts'))\nfrom gpu_tts_hold import check_gpu_tts_hold"
assert needle in producer
producer=producer.replace(needle,"for mode in ['whole','contexts','targets']:\n    r=read(BASE/f'observation-candidates-{mode}-asr-execution-v3.json')\n    assert r['exitCode']==0 and r['actualExitObserved'],mode\n"+needle)
producer_path=BASE/'render-localized-voice-repair-v4.py';assert not producer_path.exists();producer_path.write_text(producer,'utf-8')
asr=(BASE/'review-observation-candidates-voice-v3.py').read_text('utf-8').replace('observation-candidates','localized-voice-repair').replace('-v3','-v4')
asr=asr.replace('for11 unadopted current candidates','for2 complete unadopted localized takes').replace("len(tts['results']) == 11","len(tts['results']) == 2").replace("len(script['scenes']) == 11","len(script['scenes']) == 2").replace("for x in script['scenes']) == 11","for x in script['scenes']) == 2").replace("len(plan['contexts']) >= 11","len(plan['contexts']) >= 2").replace('eleven-voice','localized-two-voice')
asr_path=BASE/'review-localized-voice-repair-v4.py';assert not asr_path.exists();asr_path.write_text(asr,'utf-8')
verifier=(BASE/'verify-observation-candidates-research-resume-v3.py').read_text('utf-8').replace('observation-candidates','localized-voice-repair').replace('-v3','-v4')
verifier=verifier.replace("state['total']==11","state['total']==2").replace('allElevenCandidatePcmHashesMatched','allTwoLocalizedPcmHashesMatched').replace('eleven-item candidate voice','two-item localized voice')
verifier_path=BASE/'verify-localized-voice-repair-research-resume-v4.py';assert not verifier_path.exists();verifier_path.write_text(verifier,'utf-8')
observer=(BASE/'observe-candidate-resources-v3.py').read_text('utf-8')
observer=observer.replace("'observation-candidates-targets-asr-execution-v3.json']:","'observation-candidates-targets-asr-execution-v3.json',\n             'localized-voice-repair-tts-execution-v4.json', 'localized-voice-repair-whole-asr-execution-v4.json',\n             'localized-voice-repair-contexts-asr-execution-v4.json', 'localized-voice-repair-targets-asr-execution-v4.json']:")
observer_path=BASE/'observe-localized-resources-v4.py';assert not observer_path.exists();observer_path.write_text(observer,'utf-8')
subprocess.run([os.sys.executable,'-m','py_compile',str(producer_path),str(asr_path),str(verifier_path),str(observer_path)],check=True)
save(BASE/'prepared-localized-voice-repair-v4.json',dict(schemaVersion=1,preparedAt=stamp,request=rel(request_path),
    requestSha256=sha(request_path),total=2,producer=rel(producer_path),wholeContextAsrWorker=rel(asr_path),
    researchResumeVerifier=rel(verifier_path),resourceObserver=rel(observer_path),pyCompileExitCode=0,
    actualTtsStarted=False,modelLoaded=False,originalTenPcmChanged=False,originalElevenCandidatePcmChanged=False,
    currentVoiceApproved=False,actualID=None,private=False,allFinalPixels=False))
print(json.dumps(dict(preparedOnly=True,totalLocalizedTakes=2,originalTenAndElevenCandidatePcmPreserved=True,
                     pyCompileExitCode=0,currentVoiceApproved=False)))
