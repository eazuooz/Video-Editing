"""Lock the whole directly read KOEN guides, opening promise, and preserved inputs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
requestPath=BASE/'observation-guide-tts-request-v1.json';request=read(requestPath)
assert not request['pairedWholeTextReview'] and not (BASE/'observation-guide-tts-execution-v1.json').exists()
ko=read(BASE.parent/'script/narration.ko.json');en=read(BASE.parent/'script/narration.en.json')
assert len(ko['scenes'])==len(en['scenes'])==11 and sum(len(x['lines']) for x in ko['scenes'])==46
m=read(BASE/'current-narration-measurement-v1.json')
assert sha(BASE.parent/'script/narration.ko.json')==m['scriptSha256']
inputs=[ROOT/x['path'] for x in m['measurements']]+[ROOT/m['assembled']['path']]
for row in m['measurements']+[m['assembled']]:assert sha(ROOT/row['path'])==row['sha256']
inputs += [BASE.parent/'script/narration.ko.json',BASE.parent/'script/narration.en.json',
    BASE.parent/'script/observation-guides.ko.json',BASE.parent/'script/observation-guides.en.json',BASE.parent/'planning/outline.md',
    BASE.parent/'planning/chapter-plan.json',BASE.parent/'project.json',BASE/'current-narration-measurement-v1.json',
    ROOT/'shared/voice-reference/reference-15-35s.wav',ROOT/'shared/voice-reference/reference-15-35s.ko.txt',
    PROOF/'source-action-bank-v4.json',PROOF/'source-framing-direct-review-v1.json',
    ROOT/'motion-canvas/src/projects/familiar-game-rules/guide-scene-factory.tsx',ROOT/'motion-canvas/src/projects/familiar-game-rules/guide-scene-plan.json']
inputs += [ROOT/f'motion-canvas/src/projects/familiar-game-rules/scenes/scene{x:02d}.tsx' for x in range(12,20)]
protected=[dict(path=rel(p),sha256=sha(p)) for p in inputs]
review=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=now(),
 scope='Direct full read of original11KOEN/46paragraphs and all8newKOEN paragraphs, paired observations, preserved conclusion11 and original4sentence24.32s overview',
 wholeOriginalKOENRead=True,all8IndependentKOENGuidesRead=True,pairedWholeTextReview=True,overviewPromiseReview=True,
 overviewPromiseChecks=[
  dict(promise='Anger Foot movement/aim/kick first',resolution='02/04 retain original claims;12 compares pink door versus higher escalator target,13 kick versus room aim. Separate trailer shots remain explicit.'),
  dict(promise='Gunbrella actions second',resolution='06 retains five original paragraphs.14 follows market/wire tool state,15 separates rail/market/swamp/container aim. No exact-key/remapping or universal defense claim.'),
  dict(promise='Pedro movement versus direction third',resolution='08/10 retain all10 original paragraphs.16–19 add distinct train heights/opposite guns/downward aim/roof descent. No exact supported-device or input-binding proof.'),
  dict(promise='Conventions, remapping, device functions',resolution='03/05/07/09 and final11 unchanged. New guides illustrate action relationships within the same three-case order and preserve the original final conclusions.')],
 guidanceConnections=[dict(id=g['id'],parentScene=g['parentScene'],afterOriginalParagraph=g['afterOriginalParagraph'],ko=g['ko'],en=g['en'],visibleActionAndConnection=g['visibleActionAndConnection']) for g in request['guides']],
 original11PCMSecondsPreserved=296.72,originalExplanationSecondsPreserved=147.2,overviewSecondsPreserved=24.32,
 originalPcmHashesMatched=True,allPriorScenePcmPreserved=True,allSourceFramingApproved=False,
 finalTimingApproved=False,technicalGuideAsrApproved=False,finalMixedAsrApproved=False,
 humanWholeListening='pending',humanPronunciation='pending',newGitImages=0,protectedInputs=protected)
save(BASE/'observation-guide-text-direct-review-v1.json',review)
request.update(pairedWholeTextReview=True,overviewPromiseReview=True,reviewedAt=now(),protectedInputs=protected,
 textReview=rel(BASE/'observation-guide-text-direct-review-v1.json'),textReviewSha256=sha(BASE/'observation-guide-text-direct-review-v1.json'))
save(requestPath,request);save(BASE.parent/'planning/observation-guides-v1.json',request)
qpath=PROOF.parent/'queue.json';q=read(qpath);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
item.update(stage='independent8-guides-whole-KOEN-reviewed-ready-only-new-TTS',updatedAt=now(),
 observationGuides=dict(request=rel(requestPath),review=request['textReview'],guides=8,measured=False,pairedWholeTextReview=True,technicalAsrApproved=False),
 nextAction='Fresh currentdistinct/resource checks; synthesize only8new guides with approvedQwen1.7B/reference CPU2/GPU0. Preserve original11PCM and147.2white. Then allwhole/independent currentguide ASR and measuredtiming/native/literalcue alignment.')
q['updatedAt']=now();save(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','observationGuides','nextAction']:d[k]=item[k]
    save(p,d)
print(json.dumps(dict(guides=8,pairedRead=True,originalPCM=296.72,whitePreserved=147.2,finalApproved=False,newGitImages=0)))
