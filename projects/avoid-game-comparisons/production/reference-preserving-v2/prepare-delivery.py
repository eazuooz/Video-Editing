"""Promote the checked local revision while retaining previous manifest pointers."""
from pathlib import Path
import json,datetime
R=Path(__file__).resolve().parents[4];P=R/'projects/avoid-game-comparisons';V=P/'production/reference-preserving-v2';L=P/'production/local/reference-preserving-v2/edit'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def rel(p):return p.relative_to(R).as_posix()
plan=read(V/'edit-plan.json');qa=read(L/'qa/integrity.json');ledger=read(V/'review-ledger.json')
assert ledger['visualQA'].get('completeFinalPixels')=='passed-direct-review'
assert ledger['audioQA'].get('wholeEncodedMixAsr')=='complete-full-text-reviewed'
assert all(r['fullDecodePassed'] and r['ptsMonotonicAndUniform'] for r in qa['outputs'])
p=P/'project.json';m=read(p);m.setdefault('preservedDeliveryManifests',[])
if not any(r.get('id')=='before-reference-preserving-v2' for r in m['preservedDeliveryManifests']):m['preservedDeliveryManifests'].append({'id':'before-reference-preserving-v2','titles':m.get('titles'),'paths':m.get('paths'),'finalRender':m.get('finalRender'),'editing':m.get('editing'),'platformVideoId':'cQE7_ygx_XM','preserved':True})
design=read(P/'planning/chapter-plan.json')['currentRevision'];m['titles']={'ko':design['selectedTitle'],'en':'Why “Like Mario” Does Not Explain Your Game'}
m['status']='awaiting-local-final-review';m['publishReady']=False;m['visualStyle']='research-black-v1';m['activeRevision']='reference-preserving-v2'
m['paths']={**m['paths'],'script':rel(P/'script/reference-preserving-v2/narration.ko.json'),'scriptEn':rel(P/'script/reference-preserving-v2/narration.en.json'),'narration':'shared/output/narration/avoid-game-comparisons/reference-preserving-v2/avoid-comparisons-reference-v2.wav','audioMix':rel(L/'final-mix.m4a'),'editorAudioMix':rel(L/'final-mix.wav'),'audioReport':rel(L/'audio-build.json'),'captionsKo':rel(L/'captions.ko.srt'),'captionsEn':rel(L/'captions.en.srt'),'videoClean':rel(L/'avoid-game-comparisons-v2-clean.mp4'),'videoBurnedCaptions':rel(L/'avoid-game-comparisons-v2-captioned.mp4'),'timeline':rel(V/'edit-plan.json'),'footageCuts':rel(V/'edit-plan.json'),'sources':rel(P/'planning/chapter-plan.json'),'sceneProductionPlan':rel(V/'edit-plan.json'),'motionCanvasProject':'motion-canvas/src/projects/avoid-game-comparisons/revision-v2/production-project.ts','publishingKo':rel(P/'publishing/reference-preserving-v2/description.ko.txt'),'publishingEn':rel(P/'publishing/reference-preserving-v2/description.en.txt')}
m['paths'].pop('captionAlignmentReview',None);m['paths'].pop('candidateTimeline',None)
m['editing'].update(actualGameplaySeconds=plan['actualFrames']/60,actualExplanationSeconds=plan['explanationFrames']/60,actualGameplayShare=.6,actualCommercialGameplaySeconds=plan['actualFrames']/60,actualDevelopmentFootageSeconds=0,actualPrototypeExplanationSeconds=0,explanationStyle='research-black-v1; progressive arrows and state labels',sourceMinimum=[1920,1080])
m['editing']['exampleInterleaving']['planningPath']=rel(V/'edit-plan.json');m['editing']['exampleInterleaving']['reviewStatus']='current26cuts and115caption cues directly reviewed; source actions retained at native speed'
m['tts']=read(V/'tts-manifest.json')['tts']
m.setdefault('audio',{}).update(narrationTargetLufs=-16,bgmTargetLufs=-31,gameWorkingRmsDbfs=-33,gameLevelNote='RMS working gain, not a LUFS claim; useful effects retained under narration',voiceGainMode='constant-global-gain-with-short-peak-limiter',voiceDucked=False,report=rel(L/'audio-build.json'),continuityReport=rel(L/'qa/audio-continuity.json'))
m['membershipOutro']['appliedToFinal']=True
m['finalRender']={'status':'complete-local-user-review-pending','frames':plan['totalFrames'],'durationSeconds':plan['totalFrames']/60,'resolution':[1920,1080],'fps':60,'technicalQa':rel(L/'qa/integrity.json'),'reviewLedger':rel(V/'review-ledger.json'),'allFinalPixelsReviewed':True,'humanListening':'pending','technicalApproved':not ledger['audioQA'].get('unresolvedTechnicalFlags',[]),'videoClean':m['paths']['videoClean'],'videoBurnedCaptions':m['paths']['videoBurnedCaptions'],'openItems':['현재 완성본 사용자 최종 검수·전체 청취 대기. 기존 비공개 YouTube 영상은 변경하지 않았습니다.']}
m['finalRender']['openItems']=['현재 완성본 사용자 최종 검수·전체 청취 대기. 일부 발음 인식 차이와 원음의 국소 음량 후보는 청취 확인 전이며, 자동 검사만으로 음성 승인하지 않았습니다. 기존 비공개 YouTube 영상은 변경하지 않았습니다.']
m['currentDelivery']={'revision':'reference-preserving-v2','boundary':'local-user-final-review','driveRequired':False,'youtubeUploadAuthorized':False,'baselineVideoId':'cQE7_ygx_XM','baselineUnchanged':True,'builtAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Manifest points to checked local masters; prior delivery pointers preserved')
