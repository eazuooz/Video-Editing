"""Prepare one four-item additive voice request; no model or media execution."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os

ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
now=datetime.now(timezone.utc).isoformat()
ko_path=V/'script/additions.ko.json';en_path=V/'script/additions.en.json'
ko=read(ko_path);en=read(en_path)
assert [s['id'] for s in ko['scenes']]==[s['id'] for s in en['scenes']]==['01b','04a','08a','10a']
assert [len(s['lines']) for s in ko['scenes']]==[len(s['lines']) for s in en['scenes']]==[3,5,5,5]
pres=read(V/'baseline-preservation-v1.json');protected=pres['protectedInputs']
assert len(protected)==49
for item in protected:assert sha(ROOT/item['path'])==item['sha256'],item['path']
native=read(V/'native-candidate-direct-review-v4.json')
assert native['totalNewBoundSamples']==499 and native['totalCandidateResearchPoints']==870
assert native['nativeWorkerDead'] and native['additionalSourceWorkerDead']
normal=read(V/'candidate-normal-playback-observation-v2.json')
rights=read(V/'source-primary-rights-and-recent-use-v1.json')
selected_sources=[]
for name in ['source-acquisition-execution-v1.json','source-acquisition-execution-v2.json']:
    d=read(V/name);assert d['actualOuterExitCode']==0
    for s in d['results']:
        if s['videoId'] in ['gVkhhrLARU8','qaK2FWQB7DE','6TNjosDftog']:
            assert s['wholeDecode']['actualExitCode']==0
            selected_sources.append(dict(path=s['localMediaPath'],sha256=s['fileSha256'],bytes=s['fileBytes']))
assert len(selected_sources)==3
for item in selected_sources:assert sha(ROOT/item['path'])==item['sha256'],item['path']
protected=protected+selected_sources
orientation=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
promotion=read(orientation/'current34-main-promotion-v1.json')
transition=read(orientation/'current34-main-schedule-update-v1.json')
assert len(promotion['otherProtectedInputs'])==78 and len(promotion['repairCandidates'])==1
current_main=dict(path=promotion['currentMain']['path'],sha256=transition['afterSha256'])
all_protected=protected+promotion['otherProtectedInputs']+promotion['repairCandidates']+[current_main]
by_path={}
for item in all_protected:
    if item['path'] in by_path:assert by_path[item['path']]['sha256']==item['sha256']
    by_path[item['path']]=item
protected=list(by_path.values())
for item in protected:assert sha(ROOT/item['path'])==item['sha256'],item['path']
source_plan=dict(recordedAt=now,sourcePlanningMayProceed=True,
    scope='Pre-TTS visible-action/content planning only; measured allocation and narrated pixels remain pending.',
    nativeReview=dict(path=rel(V/'native-candidate-direct-review-v4.json'),sha256=sha(V/'native-candidate-direct-review-v4.json')),
    normalReview=dict(path=rel(V/'candidate-normal-playback-observation-v2.json'),sha256=sha(V/'candidate-normal-playback-observation-v2.json')),
    rightsContext=dict(path=rel(V/'source-primary-rights-and-recent-use-v1.json'),sha256=sha(V/'source-primary-rights-and-recent-use-v1.json')),
    retainedGame='Two Point Museum',selectedNewGames=['Manor Lords','Against the Storm','Timberborn'],
    selectedSources=selected_sources,
    candidateActionWindows=[
        dict(scene='04a',sourceId='gVkhhrLARU8',intervals=[[18.25,22.25],[22.75,28.25],[28.25,32.75],[80.25,87.25]],
             input='Building preview/worker slot/product dropdown',result='Foundation; Carpenter People1/3 to2/3; Market Hide and0/2 to1/2',
             annotation='Red selected camp or stall; teal assignment/product control; yellow question labels',
             exclusions='33.25fade/black,89.75cart; separate edited shots announced;2022pre-alpha not current rules'),
        dict(scene='08a',sourceId='qaK2FWQB7DE',intervals=[[2930.75,2937.25],[2958.25,2970.25],[2990.25,2993.25],[3080.25,3084.25]],
             explanationWindows=[[2993.25,3006.25],[3084.25,3104.75]],
             input='Shelter rotation/placement; Mine and Fishing Hut placement',result='Foundations and one completed Shelter; Mine/Hut remain under construction',
             annotation='Red moving preview/selected foundation; teal construction requirements; yellow unfinished-result question',
             exclusions='Paused HousingStatus is EX; tooltip-led Fishing analysis is EX; all console injection and unrelated pan excluded'),
        dict(scene='10a',sourceId='6TNjosDftog',intervals=[[2416,2454]],
             potentialSettingWindow=[2366,2386],
             input='Select Badtide in floodgate signal field; select and switch lever',result='Visible field assignment and Off-to-On indicator',
             annotation='Red selected floodgate/lever; teal reference to signal field; label illustrative document link, not measured wire',
             exclusions='2530different-map crossfade is not lever result; no physical flow/safety/engine graph inferred; tooltips/static diagram-led moments classified EX')],
    bodyRatioContract='ACT60:EX40 maximum1frame; all original EX/PCM retained',
    exactFinalAllocationApproved=False,actualCapacityOrTotalSecondsApproved=False,
    insufficientCapacityPolicy='Secure additional relevant unique visible actions if measured speech/EX exceeds qualified ACT capacity; do not shorten useful explanation, loop, slow down or fill with idle/cinematic footage.',
    sourcesVideoOnly=True,sourceAudioForFinal=False,sourceMusicForFinal=False,
    publicRightsApproved=False,allPeopleRightsApproved=False,fourGameTeachingApproved=False)
review=dict(recordedAt=now,contentReadyForApprovedVoiceMeasurement=True,
    originalAllWordingAndOrderPreserved=True,original12PcmRegenerated=0,original60KoEnParagraphsRetained=True,
    koScript=dict(path=rel(ko_path),sha256=sha(ko_path)),enScript=dict(path=rel(en_path),sha256=sha(en_path)),
    all18NewParagraphPairsDirectlyRead=True,
    pairedReviews=[
        dict(id='01b',paragraphs=3,purpose='Natural viewer question, ordered actual examples and first Museum connection after original cat intro',
             overviewSentenceCount=3,targetSeconds=[20,30],measuredLengthPending=True),
        dict(id='04a',paragraphs=5,previous='04 comparable sibling questions',prerequisite='Village buildings and work assignments',
             specificObservation='Carpenter1/3 to2/3; separate Market Hide and0/2 to1/2',
             principle='Workplace and market are sibling features; each owns its own choices',
             difference='Continuous geometry adjustment versus discrete product/person choices',next='05 whole/detail reading and folding',
             limit='Historical pre-alpha UI; our outline not developer document'),
        dict(id='08a',paragraphs=5,previous='08 move a heading with its children and reread meaning',
             prerequisite='Resources build settlement structures; residents assigned work',
             specificObservation='Shelter foundation then one finished roof; Mine construction/recipes; Fishing bait settings',
             principle='Housing/resource-production siblings; different buildings retain different conditions and incomplete-result questions',
             difference='Placement is not completion; mine conditions differ from fishing bait',
             next='09 containment versus cross-branch connections',limit='No completed Mine/Fishing output,all-residents-housed or console-injected result'),
        dict(id='10a',paragraphs=5,previous='10 containment and cross-reference differ',
             prerequisite='Beaver settlement/water management; floodgate adjustable height; lever manual signal',
             specificObservation='Off1m/On2m; Badtide selection; lever Off-to-On indicator',
             principle='Height and signal choice belong under floodgate settings; lever signal sending remains a separate referenced feature',
             difference='Document containment does not imply physical parent/engine graph/control causation',
             next='11 part-to-whole review and12 reader questions',limit='Source1.0 UI values; no different-map waterway success claim')],
    insertionOrder=['intro','01b','01','02','03','04','04a','05','06','07','08','08a','09','10','10a','11','12','membership'],
    palette='research-paper-white-v1',continuousApprovedNimbusPreserved=True,
    all49BaselineInputsShaMatched=True,sourceAudioForFinal=False,
    ownTrackedAnnotationsRequired=True,fixedCaptionCenter=[960,970],
    retainedActualAnnotationGapAudit=rel(V/'retained-gameplay-annotation-gap-audit-v1.json'),
    originalSixExplanationScenesRetained=True,detailedPeopleObjectsPolicyRetained=True,
    referenceReviewReused=rel(V/'current-content-and-studio-direct-review-v1.json'),
    sakuraiReferenceId='ZzCfzwe23kw',copiedScriptOrMedia=False,
    allFourGameTeachingApproved=False,finalMixedOrPixelsApproved=False,
    humanWholeListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False)
original=read(ROOT/'projects/hierarchical-game-outlines/project.json')
tts=dict(original['tts']);tts.update(outputDir='shared/output/narration/hierarchical-game-outlines/teaching-four-game-additions-v1',
    filenameStem='hierarchical-teaching-four-game-additions-v1',renderMode='scene',sceneGapSeconds=.45)
manifest=dict(schemaVersion=1,slug='hierarchical-game-outlines',scope='Four additive scenes only; original12PCM remain untouched',
    paths=dict(script=rel(ko_path),scriptEn=rel(en_path)),tts=tts,
    editing=dict(exampleSeconds=0,narrationPlacement='continuous-across-example-and-explanation',targetGameplayShare=.6,targetExplanationShare=.4),
    visualStyle='research-paper-white-v1',audio=dict(original['audio']),publishReady=False)
manifest_path=V/'tts-additions-manifest-v1.json';review_path=V/'causal-paired-script-direct-review-v1.json'
source_path=V/'source-action-planning-direct-review-v1.json';request_path=V/'narration-additions-request-v1.json'
scenes=[dict(id=s['id'],text=' '.join(s['lines']),path=tts['outputDir']+'/chunks/'+s['id']+'-scene.wav') for s in ko['scenes']]
request=dict(schemaVersion=1,recordedAt=now,slug='hierarchical-game-outlines',manifest=rel(manifest_path),
    scriptReview=rel(review_path),sourceReview=rel(source_path),total=4,paragraphs=18,
    pairedWholeTextReview=True,overviewPromiseReview=True,baselineApprovedPcmRegeneration=0,
    protectedInputs=protected,scenes=scenes,original60KoEnAndOrderPreserved=True,
    finalRatioOrAudioPixelsApproved=False,humanListeningApproved=False,publicRightsApproved=False)
for p in [manifest_path,review_path,source_path,request_path]:assert not p.exists(),p
for s in scenes:assert not (ROOT/s['path']).exists()
for p,d in [(manifest_path,manifest),(review_path,review),(source_path,source_plan),(request_path,request)]:save(p,d)
cp_path=V/'latest-checkpoint.json';cp=read(cp_path)
cp.update(recordedAt=now,stage='four-additive-causal-scripts-reviewed;single-voice-prepared-only',newNarrationWritten=True,
    crossGameVoiceRequest=rel(request_path),causalScriptReview=rel(review_path),sourceActionPlanning=rel(source_path),
    newTtsStarted=False,activeOwnedWorkers=0,
    next='Fresh current duplicate gate and one read-only stable20s resource observation, then one guarded4scene18paragraph voice batch. Original12PCM/49inputs unchanged; measured timing/ratio/annotation/render pending.')
save(cp_path,cp)
print(json.dumps(dict(preparedOnly=True,items=4,newKoEnParagraphs=18,protectedInputs=len(protected),sourcePlanningOnly=True,newTtsStarted=False)))
