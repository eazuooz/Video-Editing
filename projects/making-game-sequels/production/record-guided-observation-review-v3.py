"""Record direct full-text/word comparisons; never infer human listening approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
whole=read(BASE/'guided-observation-asr-execution-v3.json')
ctx=read(BASE/'guide-onset-context-asr-execution-v3.json')
assert whole['exitCode']==ctx['exitCode']==0 and len(whole['results'])==8 and len(ctx['results'])==2
request=read(BASE/'guided-observation-tts-request-v3.json')
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
uncertainty={
 '06-g2':'Whole ASR wrote 뒤에 rather than 뒤의 and split 미리보기. Both complete sentences retain the separate-preparation, preview rotation/movement and blocked-versus-completed distinction. Particle/pronunciation approval remains pending.',
 '13-g1':'Whole isolated ASR wrote 자쩍이 at the onset. Both an independently padded complete guide and the complete preceding paragraph plus1.8s pause/current guide read 적이 and the entire intended sentence. Retain the original discrepancy; this is technical meaning support, not a human pronunciation or arbitrary-greeting approval.',
 '12-g1':'Recognizer split 미리보기; selection/orientation and the full final verb remain present.',
 '02-g1':'Recognizer joined 벽 장치; the wall-side approach, player turning and direct attack remain in order.'}
rows=[]
for r in whole['results']:
    p=BASE/'asr-guided-observation-local-v3'/(r['id']+'.json')
    assert sha(ROOT/r['audioPath'])==r['audioSha256']
    rows.append({'id':r['id'],'audio':r['audioPath'],'audioSha256':r['audioSha256'],'samples':r['samples'],'seconds':r['seconds'],'expectedKo':r['expectedKo'],'observedText':r['text'],'fullWordsDirectlyCompared':True,'wholeResult':p.relative_to(ROOT).as_posix(),'wholeResultSha256':sha(p),'meaningAndOrderTechnicallySupported':True,'missingSentenceObserved':False,'repeatedSentenceObserved':False,'endVerbPresent':True,'independentContextNeeded':r['id']=='13-g1','uncertainty':uncertainty.get(r['id'],'Whole readback matches both complete meaning and order; human whole listening/pronunciation remain pending.'),'expectedWasRecognizerPrompt':False})
contexts=[]
for r in ctx['results']:
    p=BASE/'asr-guide-onset-context-local-v3'/(r['id']+'.json')
    assert sha(ROOT/r['audio'])==r['sha256']
    contexts.append({**r,'resultPath':p.relative_to(ROOT).as_posix(),'resultSha256':sha(p),'directReview':True,'guideOnsetAndWholeSentenceCompared':True})
d={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),'rows':rows,'independentContexts':contexts,'allEightGuidesTechnicallyCompared':True,'newGuideSeconds':44.96,'baselineCurrent13Seconds':509.624,'allCurrentComponentSeconds':554.584,'wholeVoiceScope':'13 previously technically reviewed current PCM plus8 new guide files; final mixed13 chapters are not yet built or approved.','recognizerExpectedPrompt':False,'arbitraryGreetingInNewGuideObserved':False,'contextArtifact':'The broad preceding13p1 context wrote an extra 자 and a zero-duration 같은 at its own clip beginning. Prior current13 full/context evidence remains authoritative for that unchanged base PCM; do not silently copy the context artifact into captions or claim human word approval.','allProtectedInputsUnchanged':True,'allBaselinePcmPreserved':True,'humanWholeListening':'pending','humanPronunciation':'pending','finalMixAsrApproved':False,'newJoinAsrApproved':False,'finalTimingApproved':False,'rendered':False,'newGitImages':0}
save(BASE/'guided-observation-direct-review-v3.json',d)
print(json.dumps({'newGuides':8,'independentContexts':2,'technicalOnly':True,'currentComponentSeconds':554.584,'humanListening':'pending'}))
