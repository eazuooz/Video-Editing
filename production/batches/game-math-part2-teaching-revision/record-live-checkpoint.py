"""Record observed state without promoting planning or draft QA to delivery."""
from pathlib import Path
import json,hashlib,time
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'progress-20261010.json';d=read(p)
state=read(Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json'))
d['latestResearchSnapshot']={k:state.get(k) for k in ['status','time','owner_pid','job','completed','total']}
lease=ROOT/'shared/output/GPU_HANDOFF.json'
d['currentHandoff']=({k:read(lease).get(k) for k in ['token','project','state','boundaryStatus','completedJobEvidence','ttsLog']} if lease.exists() else {'state':'no-active-lease'})
d['thirdHandoff']={'token':'64959105-2306-4969-8e17-6398037d9616','trainingFinishedAndFiniteBeforeTts':True,'trainingJob':'train_wireframe_cnnA_42','checkpointSha256':'2f5d0d0c9c340e0e99c25f4785c96dcb77223682570d87c75c125bf38d3e1374','retainedUsefulTtsChunks':15,'cancelledOnlyOwnedTtsToPreserveCompletedChunksBeforeOversizedGameDrafts':True,'v3ScriptsAndBaselineUnchanged':True,'originalQueueRestoredPid':42892,'restoredStateVerified':'waiting_for_resources / infer_val_wireframe_cnnA_42; distinguish from actual training running','records':['quaternion-v3-owned-tts-checkpoint.json','quaternion-v3-asr-checkpoint.json']}
audio=[]
for version in ['v2','v3','v4','v5','v6']:
 out=ROOT/f'shared/output/narration/game-math-quaternion-teaching-additions-{version}/qwen3-1.7b-balanced-v1'
 chunks=list((out/'chunks').glob('*-scene.wav'))
 caches=0
 for wav in chunks:
  asr=out/f'asr/{wav.name.split("-")[0]}.json'
  if asr.exists() and read(asr)['audio_sha256']==hashlib.sha256(wav.read_bytes()).hexdigest():caches+=1
 audio.append({'version':version,'existingChunks':len(chunks),'currentHashReadbacks':caches,'humanListeningApproved':False})
corrections=read(B/'quaternion-source-corrections-v5.json')
timing=read(ROOT/'shared/output/game-math-part2-teaching-revision/combined-addition-timing.json')
plans=read(B/'quaternion-measured-episode-plan.json')
clips={}
for episode in plans['episodes']:
 slug=episode['slug'];ledger=ROOT/f'shared/output/{slug}/clip-receipts.json'
 clips[slug]={'renderedSceneClips':len(read(ledger)) if ledger.exists() else 0,'totalSeconds':episode['seconds'],'fullDeliveryComplete':False}
d['quaternion'].update(auxiliaryNarration=audio,currentHashAlignedAdditions=len(timing),newActualCandidateCapacitySeconds=509.25,captionSafeIndependentExplanationRenders=37,currentFullLectureRenderComplete=False,measuredEpisodeClips=clips)
d['sourceFineCorrections']={'record':str((B/'quaternion-source-corrections-v5.json').relative_to(ROOT)).replace('\\','/'),'newOnlyExcludedGetUpIntervals':['GB03 source572','GA05 old179.1–180.1'],'finalMovingReview':False}
v5=next(read(p) for p in (ROOT/'shared/output/gpu-handoff').glob('478685d5*.json') if 'token' in read(p))
d['v5V6Handoff']={'v5Token':v5['token'],'v6Token':'77b510c9-c995-455f-8470-87d0afe4c572','v6TtsExitCode':0,'normalTrainingCompletionBeforeTts':'fullft42 step2000 validation done698; checkpoint finite','postV6ActualQueueObserved':'running train_wireframe_fullft_43 owner13096 child33316 completed700 at16:13:02+09:00','humanListeningApproved':False}
d['captionSafeProof']={'path':'shared/output/game-math-part2-teaching-revision/flow-proof/flow-proof-captioned.mp4','seconds':86.55,'fullDecode':True,'nativeEndTime':86.55,'originalScene03AndAudioExact':True,'firstPixelIssue':'two-line caption obscured prior/question and beat labels','correction':'new labels in right calculation column at x3.2/y-1.8; two-line rendered caption leaves visible gap','staticCorrectedFrameReviewed':True,'fullLectureAndHumanListeningApproval':False}
d['sourceReview']['gb05LatestDraftNativePlayback']={'seconds':16,'ended':True,'movingContactFramesReviewed':16,'captionBandClearance':'labels moved above preview y355; final1080 narrated caption review still pending','observedOcclusionAfter518':'annotations hidden, never invented'}
d['completion']=False;d['updatedAtUnix']=time.time();write(p,d)
q=read(B/'queue.json');q['execution']['stage']='quaternion54-current-hash-additions; 25editable-tracks; measured-two-episode-render-in-progress'
q['items'][0]['status']='in-production-additive-revision';write(B/'queue.json',q)
print(json.dumps({'narration':audio,'stage':q['execution']['stage'],'newUploads':0,'completedRevisions':0}))
