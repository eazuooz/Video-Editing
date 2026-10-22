"""Record only checks actually performed on the final revision; listening remains open."""
from common import *
P=R/'projects/game-math-orientation-matrices';H=P/'production/concept-fit-v2';D=R/f'output/{P.name}-concept-fit-v2'
out=read(H/'outputs.json');qa=read(H/'qa.json');coverage=read(H/'caption-pixel-coverage.json')
master=out['outputs'][1]
assert master['sha256']==qa['technical'][1]['sha256']==coverage['masterSha256']
assert all(x['decodeErrors']==0 for x in qa['technical'])
assert coverage['cues']==194 and len(coverage['sheets'])==12
coverage.update(directReview='All12 additional contact sheets directly inspected;194 final caption cues covered together with prior current-master QA frames',reviewedAt=now(),findings='No caption/model overlap or clipped equation in inspected frames. Syntax roles and axis colours distinguished. Corrected scene17 now uses rigid rotation throughout.')
save(H/'caption-pixel-coverage.json',coverage)
playback=dict(masterSha256=master['sha256'],checkedAt=now(),tool='cua_repl native local browser',segments=[dict(scene='02',start=22.833333333333332,end=50.932642,rate=1),dict(scene='17',start=514.35,end=542.198493,rate=1)],evidence='Visible browser playback log after reload of the final master. Screenshots at scene starts/results plus encoded contact sheets inspected.',continuousHumanViewing=False,actualListening=False,previousWholePlayback='Earlier full native1x run is retained in native-playback-round2.json;23 unchanged scene composites and unchanged audio reused, current whole files separately decode-tested.')
save(H/'native-playback-final.json',playback)
ledger=dict(checkedAt=now(),status='local-review-ready-with-listening-notes',masterSha256=master['sha256'],outputs=out['outputs'],frames=out['frames'],seconds=out['seconds'],technicalQa=rel(H/'qa.json'),captionCoverage=rel(H/'caption-pixel-coverage.json'),nativePlayback=rel(H/'native-playback-final.json'),visualChecks=dict(sceneCount=24,gameIntervals=4,sampledFinalFrames=130,additionalCaptionFrames=138,mobileFrames=12,sourceActionMatch='Object pickup/rotation/placement and fixed-object camera changes; no unrelated flight padding',corrections=['intro and local/world labels','source-action timing','scene02 moving circle cleared after native highlight takes over','scene17 rigid axis rotation']),audio=dict(unchangedParagraphs=115,changedGameParagraphs=25,unchangedSource='Recovered original AAC, not original PCM',asr='9 changed scenes read against intended narration; no material omission observed',actualListening=False,pending=['비시즈 / 기울기 pronunciation','changed paragraph joins','original game sound balance']),humanReview='pending-for-this-hash',uploadAuthorized=False)
save(H/'review-ledger.json',ledger)
out.update(status=ledger['status'],internalVisualQa='completed-with-sampled-and-native-playback-evidence',actualWholeListening=False);save(H/'outputs.json',out)
page=(D/'index.html').read_text(encoding='utf8').replace('내부 검수 진행 중 · 최종 사용자 시청/청취 대기','화면·자막·파일 검사 완료 · 사용자 시청/청취 대기. 바뀐 문단의 발음과 연결, 게임 소리 균형은 최종 청취 확인이 필요합니다.')
(D/'index.html').write_text(page,encoding='utf8')
print('M03 local review ready; human viewing/listening pending',master['sha256'])
