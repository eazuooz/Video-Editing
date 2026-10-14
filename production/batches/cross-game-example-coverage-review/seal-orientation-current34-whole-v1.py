"""Seal directly compared full text, retaining alternatives for independent review."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
out=O/'current34-mixed-whole-direct-review-v1.json';assert not out.exists()
s=rd(O/'current34-mixed-whole-asr-execution-v1.json');assert s['exitCode']==s['actualOuterExitCode']==0 and s['workerDead'] and s['completed']==s['total']==34
partial=rd(O/'current34-mixed-whole-partial-direct-review-v1.json');notes={v['id']:v['observation'] for v in partial['rows']}
for v in partial['rows']:assert sha(ROOT/v['result'])==v['resultSha256']
notes.update({
 '07b':'All six full contexts present; 탈것/탈컷, 화면에/화면의, 수학/수확 recognition alternatives require independent p02/p06. Camera and separate illustrative90deg disclaimers retained.',
 '08':'All six complete body/world/input-reference and transformation sentences recovered.',
 '09a':'All four complete inverse-direction, dot-product and transpose prerequisite sentences recovered.',
 '09':'All six expected contexts present. Whole recognizer inserts 점심으로 확인해 주시기 바랍니다 and repeats p04/p05; 세/새 alternative. Exact source placement remains proven, but independent complete p04-p06 must distinguish recognition from current audio; no pronunciation/content approval.',
 '10':'Six expected contexts present; p05 expected 얻습니다 recognized 넣습니다 and local축의 recognized 축에; 내적/내척 also differs. Independent p05/p06 required; numerical1/0/-1 contexts retained.',
 '10b':'All six assembly/preview/orientation/placement/size-distinction/common-basis contexts present; 놓기 전의/전에 particle alternative p03. No rotation-only claim across size selection.',
 '11':'All six expected contexts present. Whole recognizer adds 다음 영상에서 만나요 and repeats camera-view p04 across observation silence. Independent p04/p05 required; no acoustic failure inferred.',
 '12':'All six parent-child/input-output/right-to-left/composition/order contexts present. 자식/즉 and 곱/코브 alternatives in p01/p03 require independent comparison; A/B and two90degree context retained.',
 '13a':'All four complete three-check prerequisite contexts present; 축 길이 recognized 축끼리 in p03 requires independent recovery.',
 '13':'All six complete orthonormal/determinant+1/reflection/tolerance contexts present; 세/새 alternative p02. Numeric/symbol normalization retained.',
 '14':'All six expected size/perspective/length-preservation contexts present; whole recognizer repeats last sentence and adds 다음 영상에서 만나요. Independent p06 and source endpoint required.',
 '15':'All six complete scaling/reflection/two-flip/handedness/check conditions recovered; signs and numeric results retained.',
 '16a':'All four complete projection-subtraction/normalization/degenerate-input prerequisites recovered.',
 '16':'All six expected numerical-error/creep/orthonormal-repair/degenerate-input contexts present. 매/맵 and 정규화/정교화 alternatives p01/p04 require independent comparison; do not approve terminology from whole output.',
 '17':'All six complete visible-motion versus mathematical-condition/disclaimer/next-storage contexts recovered.',
 '18':'All six matrix/storage/interoperability contexts present,36/12/16bytes correct. 합성에/합성의 particle alternative p01; quaternion unit constraint and metadata disclaimer retained.',
 '19':'All six input-output/point-versus-vector/storage-versus-convention contexts present; 로컬 투/로컬2 normalization and 공간의/공간에 particle alternatives.',
 '20':'All six body/camera/input-space/disclaimer/next-interpolation contexts present; 변수에/변수의 particle alternative p04.',
 '21a':'All three complete repaired warning/half-mix/length-check bridge sentences recovered from current spliced PCM.',
 '21':'Six expected contexts present. First 처음 missing in recognition and 보간 recognized 보관 in p05/p06. Independent p01/p05/p06 required.180degree diagonal(-1,-1,1),average(0,0,1) and collapsedX/Y retained.',
 '22':'All six expected worked-problem contexts present; whole output repeats p04/p05 and adds 다시 돌아옵니다/회전입니다. 변위 recognized 변이 and 앞의/앞에 differs. Independent p04-p06 required. Numeric world(4,5,0),origin(3,3,0),local(2,-1,0) results present.',
 '23':'All six body-position/forward/arms/camera/measurement-disclaimer/next-lecture contexts present. 오일러 각 contains a replacement-character token in recognizer output; independent p06 required, not evidence of an audio encoding failure.',
 '24':'All four complete conclusion and next-order/gimbal/axis-angle contexts recovered; numbers normalized to digits. Original useful conclusion retained.',
})
assert set(notes)==set(v['id'] for v in s['results']), 'Finish direct comparison and explicit notes for remaining scenes before sealing.'
rows=[]
for v in s['results']:
 p=O/f'current34-mixed-whole-asr-v1/{v["id"]}.json';r=rd(p)
 assert r['sourceSha256']==s['decodedAacSha256'] and r['exactSourceStereoPcmBytesMatched'] and not r['expectedWasRecognizerPrompt']
 rows.append(dict(id=r['id'],result=rel(p),resultSha256=sha(p),expectedWhole=r['expectedKo'],recognizedWhole=r['text'],wholeTextsDirectlyCompared=True,observation=notes[r['id']],currentIndependentReviewRequired=True,humanListeningApproved=False,humanPronunciationApproved=False))
value=dict(recordedAt=datetime.now(timezone.utc).isoformat(),actualSession=s['actualSession'],actualOuterExitCode=s['actualOuterExitCode'],actualCompletion=s['completionChunk'],wholeExecutionSha256=sha(O/'current34-mixed-whole-asr-execution-v1.json'),decodedAacSha256=s['decodedAacSha256'],mixAacSha256=s['mixAacSha256'],partialReview=rel(O/'current34-mixed-whole-partial-direct-review-v1.json'),partialReviewSha256=sha(O/'current34-mixed-whole-partial-direct-review-v1.json'),remainingDirectReadChunks=['eda918','e9041d','2cf922','c2e247','60e5ac','44dc00','ae18eb','054b92','e7abbb'],rows=rows,all34WholeTextsDirectlyCompared=True,all34And180IndependentContextsDirectlyCompared=False,currentMixedAudioApproved=False,recognitionAlternativesAndAddedRepeatedTextRetained=True,wordTimestampsApproximate=True,humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False)
out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8');print('Sealed full34 text comparison; independent180 and human pronunciation still pending.')
