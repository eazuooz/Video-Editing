"""Record completed evidence only; native playback is not actual listening."""
from common import *
specs=[{'id': 'M13', 'slug': 'game-math-polygon-centers-v2', 'seconds': 745.25, 'tab': 67, 'scenes': 25, 'cues': 164, 'frames': 118, 'extra': 113, 'mobile': 11, 'unchanged': 77, 'changed': 12, 'asrScenes': 7, 'review': 'Ten final QA sheets with118 frames, ten additional sheets with113 frames covering all164 caption cues, and11 actual375px frames directly inspected. Native full playback0 to745.25s ended at1x.', 'fit': 'Dorfromantik tile placement and Tiny Glade wall, opening, building-size and height manipulations are directly inspected. Own models distinguish centers, perimeter, openings and height from planar polygon changes.', 'corrections': ['Removed stale model children during replacement', 'Aligned source marks to reviewed edit operations', 'Verified targeted ASR boundary without repeated phrase in source assembly'], 'pending': ['도르프로만틱·타이니 글레이드·메시·엘자 pronunciation', 'changed paragraph joins', 'game sound balance']}]
for s in specs:
 P=R/'projects'/s['slug'];H=P/'production/concept-fit-v2';D=R/f'output/{P.name}-concept-fit-v2'
 out=read(H/'outputs.json');qa=read(H/'qa.json');coverage=read(H/'caption-pixel-coverage.json');master=out['outputs'][1]
 assert master['sha256']==qa['technical'][1]['sha256']==coverage['masterSha256']
 assert all(x['decodeErrors']==0 for x in qa['technical']) and coverage['cues']==s['cues']
 assert abs(out['seconds']-s['seconds'])<.001
 coverage.update(directReview=s['review'],reviewedAt=now())
 if s['id']=='M08':
  assert len(coverage['deltaFrames'])==9
  coverage['deltaDirectReview']='completed'
 save(H/'caption-pixel-coverage.json',coverage)
 playback=dict(masterSha256=master['sha256'],checkedAt=now(),tool=f'cua_repl native local browser tab{s["tab"]}',segments=[dict(start=0,end=s['seconds'],rate=1,ended=True)],evidence='Visible native controls report full playback completion; frames and caption evidence directly inspected.',continuousHumanViewing=False,actualListening=False)
 save(H/'native-playback-final.json',playback)
 qa.update(directVisualReview=s['review'],nativePlayback=rel(H/'native-playback-final.json'));save(H/'qa.json',qa)
 ledger=dict(checkedAt=now(),status='local-review-ready-with-listening-notes',masterSha256=master['sha256'],outputs=out['outputs'],frames=out['frames'],seconds=out['seconds'],technicalQa=rel(H/'qa.json'),captionCoverage=rel(H/'caption-pixel-coverage.json'),nativePlayback=rel(H/'native-playback-final.json'),visualChecks=dict(sceneCount=s['scenes'],sampledFinalFrames=s['frames'],additionalCaptionFrames=s['extra'],mobileFrames=s['mobile'],sourceActionMatch=s['fit'],corrections=s['corrections']),audio=dict(unchangedParagraphs=s['unchanged'],changedGameParagraphs=s['changed'],unchangedSource='Recovered original AAC, not original PCM',asr=f'{s["asrScenes"]} changed full scene texts compared; no actual listening approval inferred',actualListening=False,pending=s['pending']),humanReview='pending-for-this-hash',uploadAuthorized=False)
 save(H/'review-ledger.json',ledger);out.update(status=ledger['status'],internalVisualQa='completed-with-native-playback-evidence',actualWholeListening=False);save(H/'outputs.json',out)
 page=(D/'index.html').read_text(encoding='utf8').replace('내부 검수 진행 중 · 최종 사용자 시청/청취 대기','화면·자막·파일 검사 완료 · 사용자 시청/청취 대기. 바뀐 문단의 발음과 연결, 게임 소리 균형은 최종 청취 확인이 필요합니다.');(D/'index.html').write_text(page,encoding='utf8')
 project=read(P/'project.json');project['activeConceptFitRevision']=dict(revision='concept-fit-v2',timeline=rel(H/'timeline.json'),outputs=rel(H/'outputs.json'),reviewLedger=rel(H/'review-ledger.json'),status=ledger['status'],humanReview='pending',originalTimelinePreserved=True);save(P/'project.json',project)
 print(s['id'],'visual/technical ready; listening pending')
