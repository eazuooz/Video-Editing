"""Prepare only six paired bridges; preserve all approved original material."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, re

ROOT = Path(__file__).resolve().parents[3]
R = ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = datetime.now(timezone.utc).isoformat()
baseline = read(R/'baseline-preservation-v1.json')
for x in baseline['protectedFiles']:
    assert sha(ROOT/x['path']) == x['sha256'], x['path']
plan = read(R/'causal-flow-and-annotation-plan-v1.json')
assert plan['bridgeFullKoEnDirectComparisonApproved']
bridges = copy.deepcopy(plan['preparedAdditionalBridges'])
bridges[0]['ko'] = '슈퍼플라이트는 장애물 사이를 날아가는 게임입니다. 지금은 점수보다 캐릭터를 보세요. 몸통에 표시한 관찰점이 화면에서 어디로 움직이는지, 몸이 어떻게 기울어지는지 따로 보겠습니다. 빨간 이동선은 화면에서 관찰한 변화를 나타내며, 게임 내부의 좌표값은 아닙니다.'
bridges[0]['en'] = 'Superflight is a game about flying between obstacles. For now, watch the character rather than the score. We will separately observe where the marked torso point moves on screen and how the body tilts. The red displacement line shows an observed screen change, not an internal game coordinate.'
ids = ['02a', '06a', '09a', '13a', '16a', '21a']
titles = ['비행에서 무엇을 관찰할까', '몸의 자를 바깥 기준으로 읽기', '축 방향의 몫과 전치', '길이와 직각부터 검사하기', '평행한 조각을 빼는 교정', '중간 자세도 같은 검사로 확인']
scripts = {}
for language in ['ko','en']:
    scenes = [dict(id=i, title=t, lines=re.split(r'(?<=[.!?])\s+', b[language]))
              for i,t,b in zip(ids,titles,bridges)]
    assert all(len(x['lines']) in range(2,5) for x in scenes)
    scripts[language] = dict(title='방향과 회전 행렬 · 연결 설명',
        status='paired-prepared-current-source-adoption-pending', scenes=scenes)
manifest = copy.deepcopy(read(ROOT/'projects/game-math-orientation-matrices/project.json'))
outdir = 'shared/output/narration/game-math-orientation-matrices/teaching-clarity-additions-v1'
manifest.update(status='six-additive-bridges-voice-measurement-only')
manifest['tts'].update(outputDir=outdir, filenameStem='orientation-teaching-clarity-additions-v1',
    renderMode='scene', sceneGapSeconds=.45, maxNewTokens=1024)
manifest['paths'].update(script=rel(R/'script/additions.ko.json'), scriptEn=rel(R/'script/additions.en.json'))
review = dict(schemaVersion=1, reviewedAt=now,
    allSixPairedBridgeWholeTextsDirectlyCompared=True,
    contentReadyForApprovedVoiceMeasurement=False, originalAllWordingAndOrderPreserved=True,
    original24ApprovedPcmRegeneration=0, original140KoEnLinesEachPreserved=True,
    overviewPromiseReview=True, retainedOverviewSeconds=20.16,
    semanticCorrection='Torso observation point and red screen displacement replace the ambiguous physical body center. No inferred world/engine measurement.',
    mathematicsReview='R columns are local axes in world coordinates; dot-product projection explains RT for a pure orthonormal rotation. Checks preserve lengths/right angles/handedness; Gram–Schmidt removes the parallel component then normalizes with degenerate-input guards; arithmetic matrix interpolation can collapse axes.',
    pairedBridges=bridges, sourcePlanningApproval=False, currentPcmAndAsrApproved=False,
    humanListeningApproved=False, finalMixedAsrApproved=False,
    scope='Prepared paired wording only. Actual normal-playback/native source adoption must be sealed before TTS state/model creation.')
request = dict(schemaVersion=1, slug='game-math-orientation-matrices', recordedAt=now,
    manifest=rel(R/'tts-manifest-v1.json'), scriptReview=rel(R/'paired-additive-script-direct-review-v1.json'),
    total=6, paragraphs=sum(len(s['lines']) for s in scripts['ko']['scenes']),
    pairedWholeTextReview=True, overviewPromiseReview=True,
    baselineApprovedPcmRegeneration=0, protectedInputs=baseline['protectedFiles'],
    preparedOnly=True, modelLoaded=False, actualOwnGpuJobs=0, researchManipulations=0,
    outputDir=outdir, scenes=[dict(id=s['id'], title=s['title'], text=' '.join(s['lines']),
        classification=b['classification'], beforeScene=b['beforeScene'],
        path=outdir+'/chunks/'+s['id']+'-scene.wav') for s,b in zip(scripts['ko']['scenes'],bridges)],
    sourceAdoptionProof=rel(R/'source-selection-preflight-v2.json'),
    next='Actual source-planning adoption, one owned cooperative handoff, actual exit/research restoration, then six whole current-PCM ASR texts and complete independent contexts.')
destinations = {R/'script/additions.ko.json':scripts['ko'],R/'script/additions.en.json':scripts['en'],
    R/'tts-manifest-v1.json':manifest,R/'paired-additive-script-direct-review-v1.json':review,
    R/'narration-tts-request-v1.json':request}
for p in destinations: assert not p.exists(), 'Inspect existing prepared or current voice files: '+str(p)
for p,obj in destinations.items():
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf-8')
for x in baseline['protectedFiles']: assert sha(ROOT/x['path']) == x['sha256']
print(json.dumps(dict(preparedScenes=6,paragraphs=request['paragraphs'],originalPcmRegenerated=0,
    protectedBaselineUnchanged=38,sourceAdoptionApproved=False,modelLoaded=False)))
