from common import *
P=R/'projects/game-math-camera-projection';H=P/'production/concept-fit-v2';D=R/f'output/{P.name}-concept-fit-v2'
out=read(H/'outputs.json');qa=read(H/'qa.json');c=read(H/'caption-pixel-coverage.json');master=out['outputs'][1]
assert master['sha256']==qa['technical'][1]['sha256']==c['masterSha256']
assert all(x['decodeErrors']==0 for x in qa['technical']) and c['cues']==184 and len(qa['frames'])==88
review='88 final frames/8 sheets,147 additional caption frames/13 sheets covering184 cues and11 mobile frames directly inspected. Scene14 front roof hides rear building at681.86/686.55 and reveals it at690.20; scene05/08 reference marks checked against actual roofs. No caption/pane overlap observed.'
c.update(directReview=review,reviewedAt=now());save(H/'caption-pixel-coverage.json',c)
playback=dict(masterSha256=master['sha256'],checkedAt=now(),tool='cua_repl local tab76',segments=[dict(start=0,end=842.333333,rate=1,ended=True)],continuousHumanViewing=False,actualListening=False,evidence='Native full-file playback completed; sampled pixels directly reviewed. This is not continuous human listening.')
save(H/'native-playback-final.json',playback);qa.update(directVisualReview=review,nativePlayback=rel(H/'native-playback-final.json'));save(H/'qa.json',qa)
asr=read(H/'changed-scene-asr-review.json')
for s in asr['scenes']:s['directTextReview']='Expected and recognized complete paragraphs compared; 세계/색의/3개 and 값/갑 recognition differences retained for listening. Scene11 chunk-overlap repetition absent in targeted unchunked recognition; 같고 onset/ending still needs listening.'
save(H/'changed-scene-asr-review.json',asr)
ledger=dict(checkedAt=now(),status='local-review-ready-with-listening-notes',masterSha256=master['sha256'],outputs=out['outputs'],frames=out['frames'],seconds=out['seconds'],technicalQa=rel(H/'qa.json'),captionCoverage=rel(H/'caption-pixel-coverage.json'),nativePlayback=rel(H/'native-playback-final.json'),visualChecks=dict(sceneCount=16,finalFrames=88,additionalCaptionFrames=147,mobileFrames=11,sourceActionMatch='Object placement, persistent roof landmarks and camera-dependent occlusion; numeric coordinates restricted to our model.',sourceException='Two Portal2 windows retain explicitly approved original720p exception; final1080p60.'),audio=dict(unchangedParagraphs=91,changedGameParagraphs=9,unchangedSource='Recovered original AAC; original PCM unavailable',actualListening=False,pending=['Changed paragraph joins and canonical pronunciations','Scene11 같고 ending','Game sound balance']),humanReview='pending-for-this-hash',uploadAuthorized=False)
save(H/'review-ledger.json',ledger);out.update(status=ledger['status'],internalVisualQa='completed',actualWholeListening=False);save(H/'outputs.json',out)
page=(D/'index.html').read_text(encoding='utf8').replace('내부 검수 진행 중 · 최종 사용자 시청/청취 대기','화면·자막·파일 검사 완료 · 사용자 시청/청취 대기. 바뀐 문단의 발음과 연결, 게임 소리 균형은 최종 청취 확인이 필요합니다.');(D/'index.html').write_text(page,encoding='utf8')
project=read(P/'project.json');project['activeConceptFitRevision']=dict(revision='concept-fit-v2',timeline=rel(H/'timeline.json'),outputs=rel(H/'outputs.json'),reviewLedger=rel(H/'review-ledger.json'),status=ledger['status'],humanReview='pending',originalTimelinePreserved=True);save(P/'project.json',project)
print('M17 visual/technical ready; listening pending')
