"""Record completed evidence only; native playback is not actual listening."""
from common import *
specs=[{'id': 'M11', 'slug': 'game-math-plane-distances-v2', 'seconds': 641.7333333333333, 'tab': 63, 'scenes': 19, 'cues': 145, 'frames': 57, 'extra': 105, 'mobile': 10, 'unchanged': 56, 'changed': 17, 'asrScenes': 6, 'review': 'Five final QA sheets with57 frames, nine additional caption sheets with105 frames covering all145 cues, and ten actual375px mobile frames directly inspected. Native full playback ended at641.733333s at1x.', 'fit': 'Poly Bridge3 deck boundary, lifting drawbridge and triangle construction are observed independently; own plane model explains normals and distance, never claims gameplay telemetry.', 'corrections': ['Deck boundary guides aligned to inspected motion and cleared at cuts', 'Pentagon no longer edge-on; hidden contour dashed behind raised strip', 'Ordered XZ perimeter and its negativeY normal agree'], 'pending': ['폴리 브리지 쓰리·법선·메시·꼭짓점 pronunciation', 'changed paragraph joins', 'game sound balance']}]
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
