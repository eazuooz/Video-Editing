"""Create two revised PCM files; retain all original files and unaffected samples."""
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text('utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
request=read(BASE/'targeted-clarity-request.json')
review=read(BASE/'targeted-candidate-direct-review.json')
if (BASE/'targeted-clarity-adoption.json').exists(): raise RuntimeError('Inspect the existing adoption; do not overwrite')
assert review['candidateTextTechnicalReview']
for x in request['protectedInputs']: assert sha(ROOT/x['path'])==x['sha256'],x['path']
measure=read(BASE/'narration-speech-measurements.json')
ko_path=ROOT/'projects/avoid-game-comparisons/script/narration.ko.json'
ko=read(ko_path)
en=read(ROOT/'projects/avoid-game-comparisons/script/narration.en.json')
save(BASE/'script-source-review-v1.json',read(BASE/'script-source-review.json'))
save(BASE/'narration-script-ko-v1.json',ko)
save(BASE/'narration-script-en-v1.json',en)
folder=ROOT/'shared/output/narration/avoid-game-comparisons/qwen3-1.7b-balanced-v2/chunks'
folder.mkdir(parents=True,exist_ok=True)
adoptions=[]
for repair in request['repairs']:
    original=next(x for x in measure['measurements'] if x['scene']==repair['scene'])
    candidate_review=next(x for x in review['results'] if x['id']==repair['id'])
    assert candidate_review['technicalCandidateTextApproved']
    candidate_path=ROOT/repair['candidatePath']
    assert sha(candidate_path)==candidate_review['audioSha256']
    a,rate=sf.read(ROOT/original['path'],dtype='int16',always_2d=True)
    c,cr=sf.read(candidate_path,dtype='int16',always_2d=True)
    assert rate==cr==24000 and a.shape[1]==c.shape[1]==1
    start,end=[round(t*rate) for t in repair['proposedOriginalRangeSeconds']]
    out=np.concatenate([a[:start],c,a[end:]],axis=0)
    target=folder/(repair['scene']+'-scene.wav')
    if target.exists(): raise RuntimeError('Revised PCM already exists')
    sf.write(target,out,rate,subtype='PCM_16')
    z,zr=sf.read(target,dtype='int16',always_2d=True)
    assert np.array_equal(z[:start],a[:start])
    assert np.array_equal(z[start:start+len(c)],c)
    assert np.array_equal(z[start+len(c):],a[end:])
    scene=next(x for x in ko['scenes'] if x['id']==repair['scene'])
    assert scene['lines'][repair['paragraphIndex']]==repair['originalKo']
    assert next(x for x in en['scenes'] if x['id']==repair['scene'])['lines'][repair['paragraphIndex']]==repair['matchingEn']
    scene['lines'][repair['paragraphIndex']]=repair['replacementKo']
    delta=(len(c)-(end-start))/rate
    adoptions.append({'id':repair['id'],'scene':repair['scene'],'paragraphIndex':repair['paragraphIndex'],
      'oldPath':original['path'],'oldSha256':original['sha256'],'replacedOldSampleRange':[start,end],
      'candidatePath':repair['candidatePath'],'candidateSha256':sha(candidate_path),
      'path':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'frames':len(z),'sampleRate':rate,
      'seconds':len(z)/rate,'deltaSeconds':delta,'unaffectedBeforeAndAfterSamplesIdentical':True,
      'candidateSamplesIdentical':True,'joinFadeOrTimeStretchUsed':False,'sourceClaimUnchanged':True,
      'technicalCandidateTextReview':True,'postSpliceFullAndJoinAsrReviewed':False})
save(ko_path,ko)
source_review=read(BASE/'script-source-review.json')
for x in source_review['inputs']: x['sha256']=sha(ROOT/x['path'])
for repair in request['repairs']:
    scene=next(x for x in source_review['scenes'] if x['id']==repair['scene'])
    paragraph=scene['paragraphs'][repair['paragraphIndex']]
    paragraph['koSha256']=hashlib.sha256(repair['replacementKo'].encode()).hexdigest()
    paragraph['targetedClarityReview']='Paired KO/EN reread: clearer lava route / separate edited shots, no new source claim. Approved candidate ASR; revised full-scene/join ASR pending.'
source_review.update(reviewedAt=now(),previousTextReview='projects/avoid-game-comparisons/production/script-source-review-v1.json',voiceAsrReview='revised-06-10-full-scene-and-join-ASR-pending')
save(BASE/'script-source-review.json',source_review)
current=[]
for m in measure['measurements']:
    n=dict(m); r=next((x for x in adoptions if x['scene']==m['scene']),None)
    if r: n.update({k:r[k] for k in ['path','sha256','frames','sampleRate','seconds']},text=' '.join(next(x for x in ko['scenes'] if x['id']==m['scene'])['lines']),fullAsrReview=False)
    else: n.update(fullAsrReview=True,readbackEvidence='projects/avoid-game-comparisons/production/narration-full-script-direct-review.json')
    n['humanListening']='pending';current.append(n)
white=sum(x['seconds'] for x in current if int(x['scene'])%2==1)
actual=sum(x['seconds'] for x in current if int(x['scene'])%2==0)
index={'schemaVersion':1,'createdAt':now(),'version':'v2-targeted-06-10-clarity','measurements':current,
 'originalMeasurementEvidence':'projects/avoid-game-comparisons/production/narration-speech-measurements.json',
 'scriptKoSha256':sha(ko_path),'scriptEnSha256':sha(ROOT/'projects/avoid-game-comparisons/script/narration.en.json'),
 'explanationSpeechSeconds':white,'actualSpeechSeconds':actual,'minimumActualSecondsAt60_40':white*1.5,
 'fullCurrentHashAsrApproved':False,'finalTimingApproved':False,'finalBodyRatioApproved':False,'finalVideoComplete':False,
 'allSixExplanationPcmAndDurationsPreserved':True,'original12PcmFilesPreserved':True}
save(BASE/'narration-current-index.json',index)
record={'schemaVersion':1,'adoptedAt':now(),'adoptions':adoptions,'original12FilesPreserved':True,
 'allSixExplanationPcmAndDurationsPreserved':True,'tenUnaffectedSceneHashesUnchanged':True,
 'onlyTwoKoParagraphsChanged':True,'allEnglishTextUnchanged':True,'postSpliceAsrApproved':False,
 'humanWholeListening':'pending','humanPronunciation':'pending','newGitImages':0,'finalVideoComplete':False}
for x in request['protectedInputs']:
    if x['path']!=ko_path.relative_to(ROOT).as_posix(): assert sha(ROOT/x['path'])==x['sha256'],x['path']
save(BASE/'targeted-clarity-adoption.json',record)
protected=[{'path':x['path'],'sha256':sha(ROOT/x['path'])} for x in request['protectedInputs']]
protected.extend({'path':x['path'],'sha256':x['sha256']} for x in adoptions)
contexts=[]
for n in [x for x in current if x['scene'] in ['06','10']]:
    contexts.append({'id':n['scene']+'-whole-v2','audioPath':n['path'],'audioSha256':n['sha256'],'fromSeconds':0,'toSeconds':n['seconds'],'expectedKo':n['text']})
for r in adoptions:
    n=next(x for x in current if x['scene']==r['scene']);lo,hi=([5.5,13.5] if r['scene']=='06' else [7,24])
    contexts.append({'id':r['scene']+'-join-v2','audioPath':n['path'],'audioSha256':n['sha256'],'fromSeconds':lo,'toSeconds':hi,'expectedKo':'Directly compare this independent joining context against the current whole-scene script.'})
save(BASE/'post-repair-readback-request.json',{'schemaVersion':1,'createdAt':now(),'protectedInputs':protected,'contexts':contexts,'originalPCMChanged':False})
print(json.dumps({'adoptions':adoptions,'whiteSpeech':white,'actualSpeech':actual,'postRepairContexts':len(contexts)},ensure_ascii=False))
