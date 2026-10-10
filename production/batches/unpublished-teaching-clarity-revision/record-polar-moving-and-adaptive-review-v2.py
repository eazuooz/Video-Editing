"""Record directly read v4 pixels and all six complete adaptive AAC texts.

Keep the two unsupported-minus defects held and every human alternative pending.
Prepare only the affected two moving renders; historical reviews stay intact.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, importlib.util, psutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
render=read(OUT/'six-moving-pilots-execution-v4.json')
asr=read(OUT/'adaptive-complete-audio-execution-v2.json')
assert render['exitCode']==asr['exitCode']==0 and asr['completed']==6
for s in [render,asr]:
    assert not psutil.pid_exists(s['pid']) or psutil.Process(s['pid']).create_time()!=s['createTime']
notes={
 '05':'All128 samples/22 boards read. Components, horizontal triangle and height/reference-plane distinction remain legible; world plane is explicitly illustrative, not terrain clearance. Credit, rider, numeric UI and fixed captions remain clear.',
 '08':'All208/35 read. Fresh normal-speed riding cuts replace the held crash/menu history. Red heading/blue pitch and world-up versus screen vertical are distinguished. Blue screen-vertical touches the gauge arc but not its numeric speed; no blocking collision found.',
 '11':'All181/31 read. Opposite placement/view vectors are explicitly an explanatory relation diagram. Later blue box marks image centre, not rider tracking. Unsupported U+2212 renders as a box in the24.086667–30.0s subtraction label: moving adoption held until v5.',
 '14':'All132/22 read. Canonical numeric representation is distinguished from smooth following; pole/controller discussion does not claim that this rider reaches a mathematical pole. Rider, captions and credit remain clear.',
 '16':'All205/35 read. Opposite subtraction, moving centre and separate obstruction/speed policies are distinguished. Both U+2212 signs render as boxes in16.82–25.94s formula: held until v5. Other labels/cues and normal riding are clear.',
 '18':'All102/17 read. Position/attitude/viewpoint are separated with yellow/red/blue labelled shapes while real riding, turns and jumps continue. Labels explain useful coordinate scope and separate control rules without claiming engine internals. Brief natural foliage occlusion is source action, not an overlay obstruction. All captions/credit/numeric UI clear.'}
jobs=[]
for j in render['jobs']:
    for r in j['samples']+j['boards']:assert sha(ROOT/r['path'])==r['sha256']
    jobs.append({'scene':j['scene'],'samples':j['samples'],'boards':j['boards'],
      'fullDirectReview':notes[j['scene']],'allListedPixelsDirectlyRead':True,
      'boundedPilotPixelsApproved':j['scene'] not in ['11','16'],
      'unresolved':[] if j['scene'] not in ['11','16'] else ['unsupported subtraction glyph; prepared v5 is not moving approval']})
save(OUT/'six-moving-pilots-direct-review-v4.json',{
 'reviewedAt':now,'sessionId':20169,'actualOuterExitCode':0,'exitObservedChunk':'9331ba',
 'all956SamplesAnd162BoardsDirectlyRead':True,'jobs':jobs,
 'movingAdoptionHeldScenes':['11','16'],'allSixMovingPilotsApproved':False,
 'allFinalPixelsApproved':False,'wholeVideoApproved':False,'imageGitAdded':0})
local=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/adaptive-complete-audio-v2'
bundle=read(local/'asr.json');assert bundle['complete'] and len(bundle['results'])==6
audioNotes={
 '03':'Both complete paragraphs and all three components preserved in recognized text. Initial 먼저 is again absent and 세 값 is 색값. These recognition differences do not prove a PCM omission; initial connective/pronunciation requires human listening. No audio regeneration or perfect-pronunciation claim.',
 '05':'Both complete paragraphs preserve terrain versus chosen world-plane height and the reference-basis conclusion. 세계 is 색의, retained as unresolved human pronunciation/recognizer alternative.',
 '07':'Both complete axis/sign paragraphs intact; positive pitch down and negative pitch up are present. Spoken 지 축 recognized g축. Axis glyph/phonetic interpretation requires human listening; no signed-formula error inferred.',
 '08':'Both complete paragraphs intact; world-up versus tilted horizon and checking axes preserved. 세계의 recognized3개의. Human pronunciation remains pending.',
 '09':'Both complete paragraphs,0/90 reference directions and radian units preserved. 세계 recognized3개. Human pronunciation remains pending.',
 '11':'Both complete paragraphs retain target position, camera placement, look direction and relative-origin conversion. 세계 recognized3개. Human pronunciation remains pending.'}
rows=[]
for r in bundle['results']:
    p=local/(r['label']+'.json');assert sha(ROOT/r['windowPath'])==r['windowSha256']
    rows.append({**r,'directlyCompared':True,'fullTextReview':audioNotes[r['scene']],
                 'recognitionJson':rel(p),'recognitionJsonSha256':sha(p)})
prior=read(OUT/'current-whole-aac-direct-review-v1.json')
assert prior['all19WholeAnd19IndependentFullExpectedAndActualTextsDirectlyRead']
save(OUT/'current-aac-complete-comparison-v2.json',{
 'reviewedAt':now,'sessionId':35148,'actualOuterExitCode':0,'exitObservedChunk':'a4d534',
 'allSixFullExpectedAndRecognizedTextsDirectlyRead':True,'all44CompleteContextsDirectlyCompared':True,
 'prior38ContextEvidence':rel(OUT/'current-whole-aac-direct-review-v1.json'),'rows':rows,
 'aacSha256':asr['aacSha256'],'wavSha256':asr['wavSha256'],
 'currentMixedAudioMachineComparisonComplete':True,
 'humanListeningApproved':False,'pronunciationApproved':False,'publicRightsApproved':False,
 'recognizerAlternativesResolvedByInference':False,'audioRegenerated':False,
 'finalPairAudioEquivalencePending':True,'wholeVideoApproved':False})
spec=importlib.util.spec_from_file_location('glyph_v5',Path(__file__).with_name('prepare-polar-minus-glyph-repair-v5.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
prep=read(OUT/'minus-glyph-repair-preparation-v5.json')
plan=read(ROOT/next(j for j in prep['jobs'] if j['scene']=='11')['plan'])
raw=read(OUT/'action-clarity-execution-v3.json')
records=next(j for j in raw['jobs'] if str(j['scene'])=='11')['records']
r=min([r for r in records if r['frame']>=1446],key=lambda r:r['frame'])
assert sha(ROOT/r['path'])==r['sha256']
p=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/minus-glyph-repair-prepared-v5/scene11-active-minus-fixed.png';assert not p.exists()
with Image.open(ROOT/r['path']) as im:m.annotate(im,r['frame'],plan).save(p)
save(OUT/'minus-glyph-active-stage-preparation-v5.json',{
 'preparedAt':now,'scene':'11','sample':{'frame':r['frame'],'path':rel(p),'sha256':sha(p)},
 'previousScene11SampleAt1440BeforeFormulaStage':True,'movingPixelsApproved':False})
worker=Path(__file__).with_name('render-polar-minus-glyph-pilots-v5.py');assert not worker.exists()
code=Path(__file__).with_name('render-polar-six-gameplay-pilots-v4.py').read_text(encoding='utf-8')
replacements={
 'six-moving-pilots-v4':'minus-glyph-moving-pilots-v5',
 'prepare-polar-remaining-annotations-v4.py':'prepare-polar-minus-glyph-repair-v5.py',
 'six-moving-pilots-execution-v4.json':'minus-glyph-moving-pilots-execution-v5.json',
 'remaining-editorial-annotation-preparation-v4.json':'minus-glyph-repair-preparation-v5.json',
 "proof=json.loads((OUT/'remaining-editorial-annotation-direct-review-v4.json').read_text(encoding='utf-8'))\n    assert proof['sixBoundedPreparedLayoutsApproved'] and proof['all150PreparedSamplesAnd27BoardsDirectlyRead']":
 "proof=json.loads((OUT/'minus-glyph-prepared-direct-review-v5.json').read_text(encoding='utf-8'))\n    assert proof['bothActiveFormulaSamplesDirectlyRead']\n    adaptive=json.loads((OUT/'current-aac-complete-comparison-v2.json').read_text(encoding='utf-8'))\n    assert adaptive['all44CompleteContextsDirectlyCompared']",
 "'scenes':6":"'scenes':2"}
for a,b in replacements.items():
    assert a in code,a
    code=code.replace(a,b)
code=code.replace('One owned CPU batch, six repaired narrated gameplay overlays','One owned CPU batch, two narrowly repaired subtraction glyph overlays')
worker.write_text(code,encoding='utf-8')
qfile=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qfile)
for sid,s,file,chunk in [(20169,render,'six-moving-pilots-execution-v4.json','9331ba'),(35148,asr,'adaptive-complete-audio-execution-v2.json','a4d534')]:
    assert not any(j['sessionId']==sid for j in q['execution']['completedJobs'])
    q['execution']['completedJobs'].append({'sessionId':sid,'pid':s['pid'],'createTime':s['createTime'],
      'state':rel(OUT/file),'actualOuterExitCode':0,'exitObservedChunk':chunk,'allListedOutputsDirectlyRead':True})
q['execution'].update(stage='polar-two-minus-glyph-moving-repairs-prepared',heavyJob=None,
 next='Directly review both active v5 formula samples, then fresh-resource singleCPU2/GPU0 two-job renderer. All44 AAC contexts compared; human pronunciation remains pending. Preserve other four v4 pilots and scene02 v2. Final54115-frame original-AAC pair remains unmade.')
q['updatedAt']=now;qfile.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'readPixels':956,'readBoards':162,'heldScenes':['11','16'],'adaptiveFullTextsRead':6,'preparedWorker':rel(worker),'activeFormulaFrame':r['frame']}))
