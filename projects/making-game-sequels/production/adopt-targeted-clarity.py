"""Splice only five reviewed paragraphs into four new files; retain original PCM."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import soundfile as sf
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
if (BASE/'targeted-clarity-adoption.json').exists():raise RuntimeError('Do not duplicate completed adoption')
request=read(BASE/'targeted-clarity-request.json');review=read(BASE/'targeted-candidate-direct-review.json');ranges=read(BASE/'original-clarity-splice-proposal.json')
assert review['candidateTextTechnicalReview'] and len(review['results'])==5
for p in request['protectedInputs']:assert sha(ROOT/p['path'])==p['sha256'],p['path']
old=read(BASE/'narration-tts-execution.json')['measurements']
ko_path=BASE.parent/'script/narration.ko.json';en_path=BASE.parent/'script/narration.en.json';chapter_path=BASE.parent/'planning/chapter-plan.json'
ko=read(ko_path);en=read(en_path);chapter=read(chapter_path)
for name,value in [('narration-script-ko-v1.json',ko),('narration-script-en-v1.json',en),('chapter-plan-pre-clarity.json',chapter),('script-source-review-v1.json',read(BASE/'script-source-review.json'))]:
    assert not (BASE/name).exists();save(BASE/name,value)
folder=ROOT/'shared/output/narration/making-game-sequels/qwen3-1.7b-balanced-v2/chunks';folder.mkdir(parents=True,exist_ok=True)
adoptions=[];revised={}
for row in ranges['scenes']:
    assert row['directRangesApproved']
    sid=row['scene'];m=next(x for x in old if x['scene']==sid)
    audio,rate=sf.read(ROOT/m['path'],dtype='int16',always_2d=True);assert sha(ROOT/m['path'])==m['sha256']
    pieces=[];cursor=0;output_cursor=0;segments=[]
    for r in sorted([x for x in request['repairs'] if x['scene']==sid],key=lambda x:x['paragraphIndex']):
        v=next(x for x in review['results'] if x['id']==r['id']);assert v['technicalCandidateTextApproved']
        span=next(x for x in row['repairs'] if x['id']==r['id']);a,b=span['originalSampleRange'];assert a>=cursor
        candidate,cr=sf.read(ROOT/r['candidatePath'],dtype='int16',always_2d=True)
        assert cr==rate==24000 and candidate.shape[1]==audio.shape[1]==1 and sha(ROOT/r['candidatePath'])==v['audioSha256']
        retained=audio[cursor:a];pieces.append(retained);segments.append(dict(kind='retained',originalSampleRange=[cursor,a],outputSampleRange=[output_cursor,output_cursor+len(retained)]));output_cursor+=len(retained)
        pieces.append(candidate);segments.append(dict(kind='candidate',id=r['id'],path=r['candidatePath'],outputSampleRange=[output_cursor,output_cursor+len(candidate)]))
        adoptions.append(dict(id=r['id'],scene=sid,paragraphIndex=r['paragraphIndex'],originalSampleRange=[a,b],candidatePath=r['candidatePath'],candidateSha256=v['audioSha256'],outputSampleRange=[output_cursor,output_cursor+len(candidate)],deltaSeconds=(len(candidate)-(b-a))/rate,postSpliceAsrReviewed=False))
        output_cursor+=len(candidate);cursor=b
        s=next(s for s in ko['scenes'] if s['id']==sid);assert s['lines'][r['paragraphIndex']]==r['originalKo'];s['lines'][r['paragraphIndex']]=r['replacementKo']
        assert next(s for s in en['scenes'] if s['id']==sid)['lines'][r['paragraphIndex']]==r['matchingEn']
    retained=audio[cursor:];pieces.append(retained);segments.append(dict(kind='retained',originalSampleRange=[cursor,len(audio)],outputSampleRange=[output_cursor,output_cursor+len(retained)]))
    out=np.concatenate(pieces);target=folder/(sid+'-scene.wav');assert not target.exists()
    sf.write(target,out,rate,subtype='PCM_16');z,zr=sf.read(target,dtype='int16',always_2d=True)
    for p in segments:
        a,b=p['outputSampleRange']
        if p['kind']=='retained':x,y=p['originalSampleRange'];assert np.array_equal(z[a:b],audio[x:y])
        else:c,cr=sf.read(ROOT/p['path'],dtype='int16',always_2d=True);assert np.array_equal(z[a:b],c)
    if sid in ['01','07','11']:assert len(z)>=len(audio),'Do not reduce useful explanation duration'
    revised[sid]=dict(scene=sid,path=target.relative_to(ROOT).as_posix(),sha256=sha(target),frames=len(z),sampleRate=rate,seconds=len(z)/rate,text=' '.join(next(s for s in ko['scenes'] if s['id']==sid)['lines']),fullAsrReview=False,humanListening='pending',originalPath=m['path'],originalSha256=m['sha256'],retainedSegments=segments,allUnaffectedSamplesIdentical=True,noFadeOrTimeStretch=True)
chapter['overview']['historicalKoDraftBeforeClarity']=chapter['overview']['koDraft'][:]
chapter['overview']['koDraft']=ko['scenes'][0]['lines'][:]
chapter['overview']['clarityChange']='Only phrase for trap placement/combat made clearer; question, promised steps and first example retained.'
save(ko_path,ko);save(chapter_path,chapter)
source_review=read(BASE/'script-source-review.json')
for p in source_review['inputs']:p['sha256']=sha(ROOT/p['path'])
for r in request['repairs']:
    s=next(s for s in source_review['scenes'] if s['id']==r['scene']);p=s['paragraphs'][r['paragraphIndex']]
    p['koSha256']=hashlib.sha256(r['replacementKo'].encode()).hexdigest();p['targetedClarityReview']='Independent candidate paragraph readback directly compared with matching English and source limits; only wording clarity changed. Revised whole/join ASR pending.'
source_review.update(reviewedAt=now(),previousTextReview='projects/making-game-sequels/production/script-source-review-v1.json',voiceAsrReview='post-splice-four-whole-scenes-and-five-joins-pending')
save(BASE/'script-source-review.json',source_review)
current=[]
for m in old:
    if m['scene'] in revised:n=dict(revised[m['scene']])
    else:n={**m,'fullAsrReview':True,'readbackEvidence':'projects/making-game-sequels/production/whole-narration-direct-review-pre-context.json','humanListening':'pending'}
    current.append(n)
white=sum(m['seconds'] for m in current if int(m['scene'])%2==1);actual=sum(m['seconds'] for m in current if int(m['scene'])%2==0)
index=dict(schemaVersion=1,createdAt=now(),version='v2-five-paragraph-clarity-four-scenes',measurements=current,originalMeasurementEvidence='projects/making-game-sequels/production/narration-tts-execution.json',scriptKoSha256=sha(ko_path),scriptEnSha256=sha(en_path),speechSeconds=white+actual,explanationSpeechSeconds=white,actualSpeechSeconds=actual,originalSixExplanationMinimumSeconds=219.68,minimumActualSecondsAt60_40=white*1.5,allOriginal12FilesPreserved=True,eightUnaffectedSceneHashesUnchanged=True,allUnchangedParagraphSamplesIdentical=True,allSixExplanationMinimumDurationsPreserved=True,fullCurrentHashAsrApproved=False,finalTimingApproved=False,finalVideoComplete=False)
save(BASE/'narration-current-index.json',index)
for p in request['protectedInputs']:
    if p['path'] not in [ko_path.relative_to(ROOT).as_posix(),chapter_path.relative_to(ROOT).as_posix()]:assert sha(ROOT/p['path'])==p['sha256'],p['path']
save(BASE/'targeted-clarity-adoption.json',dict(schemaVersion=1,adoptedAt=now(),adoptions=adoptions,revisedScenes=list(revised.values()),allOriginal12FilesPreserved=True,eightUnaffectedScenesUnchanged=True,allUnchangedParagraphSamplesIdentical=True,allEnglishTextUnchanged=True,fiveKoParagraphsOnly=True,allSixExplanationMinimumDurationsPreserved=True,postSpliceAsrApproved=False,humanWholeListening='pending',humanPronunciation='pending',newGitImages=0,finalVideoComplete=False))
protected=[dict(path=p['path'],sha256=sha(ROOT/p['path'])) for p in request['protectedInputs']]
protected += [dict(path=m['path'],sha256=m['sha256']) for m in revised.values()]
contexts=[]
for sid,m in revised.items():contexts.append(dict(id=sid+'-whole-v2',audioPath=m['path'],audioSha256=m['sha256'],fromSeconds=0,toSeconds=m['seconds'],expectedKo=m['text']))
for r in adoptions:
    m=revised[r['scene']];a,b=r['outputSampleRange']
    contexts.append(dict(id=r['id']+'-join-v2',audioPath=m['path'],audioSha256=m['sha256'],fromSeconds=max(0,a/24000-1.5),toSeconds=min(m['seconds'],b/24000+1.5),expectedKo='Compare both neighbouring clause fragments and the whole repaired paragraph directly against the current scene script; context clipping is intentional.'))
save(BASE/'post-repair-readback-request.json',dict(schemaVersion=1,createdAt=now(),protectedInputs=protected,contexts=contexts,originalPCMChanged=False))
print(json.dumps(dict(revisedScenes=[{'scene':m['scene'],'seconds':m['seconds'],'sha256':m['sha256']} for m in revised.values()],adoptedParagraphs=5,totalSeconds=white+actual,whiteSpeechSeconds=white,actualSpeechSeconds=actual,postSpliceContexts=len(contexts),allUnaffectedSamplesIdentical=True),ensure_ascii=False))
