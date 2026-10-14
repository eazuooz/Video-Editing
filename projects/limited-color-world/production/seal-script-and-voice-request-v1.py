"""Seal directly read paired text and prepare one approved voice measurement."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;PROJECT=BASE.parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-limited-color-world'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
 tmp=p.with_name(p.name+f'.{os.getpid()}.writing');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,p)
review_path=BASE/'paired-script-direct-review-v1.json';request_path=BASE/'narration-tts-request-v1.json'
assert not review_path.exists() and not request_path.exists()
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','limited-color-world','--check'],cwd=ROOT,check=True)
ko=read(PROJECT/'script/narration.ko.json');en=read(PROJECT/'script/narration.en.json');intents=read(PROJECT/'planning/scene-intents-v1.json');bank=read(PROOF/'source-action-bank-v1.json')
assert bank['sourceAdoptionApproved'] and len(ko['scenes'])==len(en['scenes'])==len(intents['scenes'])==8
assert sum(len(s['lines']) for s in ko['scenes'])==24
for a,b,c in zip(ko['scenes'],en['scenes'],intents['scenes']):
 assert a['id']==b['id']==c['id'] and len(a['lines'])==len(b['lines'])==c['paragraphs']
 assert all(t.strip() for t in a['lines']+b['lines'])
checks=[
 ('01-overview','Four natural sentences in three paired paragraphs. Central question is reading the next action when colors differ; promise order is house outlines, plant height/motion, dark-space contrast, with a direct connection to the first house. 20–30s remains a plan.'),
 ('02-contours','Observed house/path/window/roof boundaries remain under changing fills. Our diagram explicitly compares outline removal with outline retention, not a claim about every viewer.'),
 ('03-pattern-and-erasing','Hatching persists under painting/partial erasure. No complete removal claim. Round/angular handles are explicitly hypothetical design examples, not observed Chicory devices.'),
 ('04-height-and-motion','Observed differently colored mushrooms rise and support bouncing, then compress. Height/top surface/motion supplement hue. No correct-hue requirement, optimal route or all-color guarantee.'),
 ('05-state-not-hue','Separate painting/erasing shots and plants returning tall illustrate current state. Explicitly rejects permanent-unlock inference and conflation into one uninterrupted action.'),
 ('06-route-information','Player, top surfaces and destination edge are foreground priorities. Reducing color count alone is insufficient; outlines/shapes help distinguish important roles. Background obscuring the path is a diagram comparison.'),
 ('07-local-contrast','Cave has limited pale circle and dark surroundings; no whole-scene brightening claim. Lightness is distinct from hue; diagram compares foreground/background rather than medical thresholds.'),
 ('08-check-and-conclusion','Grayscale/color-perception preview helps find problems but does not prove every player can read the screen. Actual target/state/next-action checks and the promised outline/height/contrast cues recur in the conclusion.')]
overview=ko['scenes'][0]
review=dict(schemaVersion=1,slug='limited-color-world',reviewedAt=now(),method='Directly read all24 current KO paragraphs and all24 EN partners, complete outline/intents, current original-source concept notes and sealed source action observations.',
 scenes=8,pairedParagraphs=24,koCharacters=sum(len(t) for s in ko['scenes'] for t in s['lines']),wholeExpectedKoEnDirectlyRead=True,
 independentOriginalScript=True,sourceLectureReplication=False,overviewPromiseReview=True,
 overview=dict(sentences=4,paragraphs=3,characters=sum(map(len,overview['lines'])),targetSeconds=[20,30],measuredSeconds=None),
 sceneReviews=[dict(id=i,allPairedParagraphsRead=True,reason=r) for i,r in checks],
 currentScripts=[dict(path=rel(PROJECT/f'script/narration.{lang}.json'),sha256=sha(PROJECT/f'script/narration.{lang}.json')) for lang in ['ko','en']],
 sourceActionBank=dict(path=rel(PROOF/'source-action-bank-v1.json'),sha256=sha(PROOF/'source-action-bank-v1.json')),
 contentReadyForApprovedVoiceMeasurement=True,sourceWindowAllocationMeasured=False,finalCueUiApproved=False,
 trimmedDynamicFramingPlaybackApproved=False,allNativeFramesReviewed=False,continuousWholeViewingApproved=False,
 humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,narrationCreated=False,finalMixCreated=False,actualVideoId=None)
save(review_path,review)
mp=PROJECT/'project.json';m=read(mp);m['status']='script-reviewed-ready-for-approved-voice-measurement';m['review']['script']=True
m['editing']['exampleInterleaving']['reviewStatus']='bounded-source-actions-and-script-connections-reviewed; measured allocation and continuous final cue/UI pending'
save(mp,m)
protected=[mp,PROJECT/'script/narration.ko.json',PROJECT/'script/narration.en.json',PROJECT/'planning/outline.md',PROJECT/'planning/scene-intents-v1.json',PROJECT/'sources/game-candidates.json',PROOF/'source-action-bank-v1.json',review_path,ROOT/'shared/voice-reference/reference-15-35s.wav',ROOT/'shared/voice-reference/reference-15-35s.ko.txt']
request=dict(schemaVersion=1,slug='limited-color-world',preparedAt=now(),pairedWholeTextReview=True,overviewPromiseReview=True,
 scriptReview=rel(review_path),queueDir='C:/Users/eazuo/renderformer/tmp/placement_focus_20261008',device='cuda:0',cpuThreads=2,batchSize=1,total=8,paragraphs=24,
 model=m['tts']['model'],voiceApproval='Existing approved Qwen3-TTS1.7B and exact channel reference; no new speaker/style.',
 researchHandoff='Current training final checkpoint/validation/done, owned cooperative job-boundary pause, exclusive single TTS, restore exact original command/cwd/queue on success or failure and verify actual resume.',
 protectedInputs=[dict(path=rel(p),sha256=sha(p)) for p in protected],
 scenes=[dict(id=s['id'],title=s['title'],paragraphs=len(s['lines']),text=' '.join(s['lines']),path=m['tts']['outputDir']+'/chunks/'+s['id']+'-scene.wav') for s in ko['scenes']],
 currentWholeAsrDirectReview=False,finalMixedAsrApproved=False,heuristicIsApproval=False)
save(request_path,request)
checkpoint=dict(schemaVersion=1,slug='limited-color-world',recordedAt=now(),stage='script-reviewed-approved-voice-request-prepared',
 scriptReview=rel(review_path),sourceBank=rel(PROOF/'source-action-bank-v1.json'),ttsRequest=rel(request_path),scenes=8,pairedParagraphs=24,
 ttsStarted=False,voiceMeasured=False,motionCanvasCreated=False,finalTimingApproved=False,mixedAsrApproved=False,allFinalPixelsApproved=False,
 qa=False,collected=False,uploaded=False,actualId=None,maximumUniqueActionSeconds=101.5,
 nextAction='Validate the single8scene voice wrapper, fresh actual CIM/GPU and original research state; serialize one approved voice request. After actual exit verify research resume and whole8 plus independent complete-context ASR. Secure additional unique source actions if measured60:40 needs them; do not shorten approved PCM or loop/slow footage.')
save(BASE/'latest-checkpoint.json',checkpoint)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';original=qp.read_bytes();q=json.loads(original)
foreign=json.dumps([i for i in q['items'] if i['slug']!='limited-color-world'],sort_keys=True,ensure_ascii=False)
i=next(i for i in q['items'] if i['slug']=='limited-color-world')
i.update(stage=checkpoint['stage'],updatedAt=now(),nextAction=checkpoint['nextAction'],scriptReview=rel(review_path),sourceActionBank=rel(PROOF/'source-action-bank-v1.json'),sourceAdoptionApproved=True)
i['checkpoints']['script']=True
q['updatedAt']=q['lastProgressAt']=now()
assert foreign==json.dumps([i for i in q['items'] if i['slug']!='limited-color-world'],sort_keys=True,ensure_ascii=False) and qp.read_bytes()==original
save(qp,q)
print('All24 paired paragraphs sealed; one8scene voice measurement request prepared. No model, media or research control mutation.')
