"""Record directly inspected final pixels, observed native playback, and remaining listening scope."""
from common import *
import sys
unit=sys.argv[1]
spec={
 'm19':dict(slug='game-math-mesh-uv',scenes=16,frames=50324,cues=184,qaFrames=83,captionFrames=144,mobile=14,unchanged=84,changed=13,
 review='83 final frames/7 sheets,144 additional caption frames/12 sheets covering184 cues,and14 actual375px mobile frames directly inspected. The roof focus ring follows rotation and height; hull shape versus panel seams is compared with defined triangles; fixed prism positions remain unchanged during smooth-normal interpolation; tower visible at house boundary; hole thickness visible with the character crossing. Code colours and caption clearance checked; no clipping or object/caption collision observed.',
 asr='All4 full expected/recognized scene texts compared. 기하/기아, 메시/메쉬, 빨강/빨간, numeric names and 이을/이율 retained as recognition/listening notes. Targeted complete-paragraph ASR for06L03 and07L03 showed 테두리 and 위쪽 면 without the chunk-boundary duplicate. No apparent missing paragraph. Actual listening remains pending.',
 pending=['타이니 글레이드·메시·법선·인덱스 발음','06·07 변경 문단의 호흡과 연결','원본에서 복원한 수학 내레이션과 게임 소리 균형']),
 'm20':dict(slug='game-math-normal-transform-uv',scenes=13,frames=43217,cues=157,unchanged=63,changed=18,
 review='',
 asr='All5 full expected/recognized scene texts compared. UV/numeral spellings are normalized recognition variants; 수치 예제/수치해제, 무늬/문의, 기하/기아, 네/내, 보간/보관, 기와/기화 and 맞히는/맞추는 remain targeted listening notes. No apparent missing or duplicated paragraph. Actual listening remains pending.',
 pending=['수치 예제·기하·보간·기와·UV·역전치 발음','변경 문단 연결과 자연스러운 호흡','게임 소리와 내레이션 균형'])
}[unit]
P=R/'projects'/spec['slug'];H=P/'production/concept-fit-v2';D=R/f'output/{P.name}-concept-fit-v2'
out=read(H/'outputs.json');qa=read(H/'qa.json');cap=read(H/'caption-pixel-coverage.json');play=read(H/'native-playback-final.json')
master=next(x for x in out['outputs'] if x['path'].endswith('.captioned.mp4'))
assert master['sha256']==qa['technical'][1]['sha256']==cap['masterSha256']==play['masterSha256']
assert len(out['outputs'])==4 and out['frames']==spec['frames'] and cap['cues']==spec['cues']
assert all(x['decodeErrors']==0 for x in qa['technical'])
assert play['segments'][-1]['ended'] and abs(play['segments'][-1]['end']-out['seconds'])<.05
assert not play['actualListening'] and not play['continuousHumanViewing']
for key,actual in [('qaFrames',len(qa['frames'])),('captionFrames',cap['addedFrames']),('mobile',len(qa['mobile']))]:
 if key in spec:assert spec[key]==actual,(key,actual)
 else:spec[key]=actual
if unit=='m20':
 spec['review']=read(H/'final-pixel-observation.json')['directReview']
review=spec['review'];assert review
cap.update(directReview=review,reviewedAt=now());save(H/'caption-pixel-coverage.json',cap)
qa.update(directVisualReview=review,nativePlayback=rel(H/'native-playback-final.json'));save(H/'qa.json',qa)
asr=read(H/'changed-scene-asr-review.json')
for scene in asr['scenes']:scene['directTextReview']=spec['asr']
asr['directTextReviewedAt']=now();save(H/'changed-scene-asr-review.json',asr)
mix=read(H/'audio-mix.json');mix['targetedListeningPending']=spec['pending'];save(H/'audio-mix.json',mix)
plan=read(H/'scene-visual-plan.json');plan.update(status='encoded-visual-review-complete',finalVisualReview=review);save(H/'scene-visual-plan.json',plan)
ledger=dict(checkedAt=now(),status='local-review-ready-with-listening-notes',masterSha256=master['sha256'],outputs=out['outputs'],frames=out['frames'],seconds=out['seconds'],technicalQa=rel(H/'qa.json'),captionCoverage=rel(H/'caption-pixel-coverage.json'),nativePlayback=rel(H/'native-playback-final.json'),visualChecks=dict(sceneCount=spec['scenes'],finalFrames=spec['qaFrames'],additionalCaptionFrames=spec['captionFrames'],mobileFrames=spec['mobile'],sourceActionMatch='Observed construction, surface geometry, or material changes compared with explicit authored illustrations; numeric game internals not inferred.'),audio=dict(unchangedParagraphs=spec['unchanged'],changedGameParagraphs=spec['changed'],unchangedSource='Recovered original AAC, not original PCM',actualListening=False,pending=spec['pending']),humanReview='pending-for-this-hash',uploadAuthorized=False)
save(H/'review-ledger.json',ledger);out.update(status=ledger['status'],internalVisualQa='completed',actualWholeListening=False);save(H/'outputs.json',out)
page=(D/'index.html').read_text(encoding='utf8').replace('내부 검수 진행 중 · 최종 사용자 시청/청취 대기','화면·자막·파일 검사 완료 · 사용자 시청/청취 대기. 바뀐 문단의 발음과 연결, 게임 소리 균형은 최종 청취 확인이 필요합니다.')
(D/'index.html').write_text(page,encoding='utf8')
project=read(P/'project.json');project['activeConceptFitRevision']=dict(revision='concept-fit-v2',timeline=rel(H/'timeline.json'),outputs=rel(H/'outputs.json'),reviewLedger=rel(H/'review-ledger.json'),status=ledger['status'],humanReview='pending',originalTimelinePreserved=True);save(P/'project.json',project)
print(unit.upper(),'visual/technical ready; actual listening pending')
