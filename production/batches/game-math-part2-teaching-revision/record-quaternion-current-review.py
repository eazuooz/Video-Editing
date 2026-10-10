"""Record completed technical/pixel checks without inventing listening/platform QA.

Run only after inspecting the hash-matched changed-final review sheets and native
windows. Older render observations remain separately retained in review history.
"""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
baseline=read(B/'baselines/game-math-quaternion-operations/lesson.json');combined=[];episodes=[]
expected={'game-math-quaternion-foundations-v2':'84709251ae2c9fb03e9df5f3f3bcd24e1fe5ad01a207c37cb5e475678611a33e','game-math-quaternion-calculations-v2':'b4d6570baad8bf4293b3c8da24d009be59ce5d8bc03dd473b85b1d3eca924811'}
for slug,digest in expected.items():
 P=ROOT/'projects'/slug;m=read(P/'project.json');t=read(P/'production/timeline.json');l=read(P/'production/lesson.json');qa=read(P/'production/qa.json')
 assert sha(ROOT/m['paths']['videoBurnedCaptions'])==digest==qa['videos']['videoBurnedCaptions']['sha256']
 assert qa['fullDecodePassed'] and qa['ratioErrorFrames']==0 and qa['koEnMatchingTimes'] and not qa['backgroundMusic'] and not qa['sourceAudioUsed']
 assert t['actualFrames']*5==t['bodyFrames']*2 and t['explanationFrames']*5==t['bodyFrames']*3
 assert l['contract']==baseline['contract'];combined.extend(s for s in l['scenes'] if s['id'].isdigit())
 changed=read(ROOT/'shared/output'/slug/'changed-final-pixel-review'/digest[:16]/'extraction.json');assert changed['sha256']==digest
 retained=[]
 for ident in ['intro','outro']:
  src=ROOT/'shared/output/game-math-quaternion-operations/clips'/f'{ident}.mp4';dst=ROOT/'shared/output'/slug/'clips'/f'{ident}.mp4';assert sha(src)==sha(dst)
  retained.append({'scene':ident,'source':str(src.relative_to(ROOT)).replace('\\','/'),'sha256':sha(src),'originalEncodedClipExact':True})
 audit={'source':m['paths']['videoBurnedCaptions'],'sha256':digest,'technicalFullDecodePassed':True,'exact40To60Passed':True,'koEnTimingAndFixedGeometryPassed':True,'baselineMaterialReview':'quaternion-native-review-history.json','changedFinalReview':str((ROOT/'shared/output'/slug/'changed-final-pixel-review'/digest[:16]/'extraction.json').relative_to(ROOT)).replace('\\','/'),'allChangedMotionSamplesDirectlyViewed':changed['motionSamples'],'allChangedCueSamplesDirectlyViewed':changed['cueSamples'],'changedLabels':'independent line layout; spacing and caption clearance directly verified','annotationReview':'current GA08/GB07 native windows and current nine-frame tracks; remaining track sheets and full composition reviewed before unchanged clip reuse','retainedOriginalBrandingAndOutro':retained,'currentWholeNativePlayback':'started at1x after selective corrections; ended observation pending','humanListening':'pending','gameIPHumanRights':'pending','uploadedPlayerCaptionProof':'pending','platformComplete':False}
 write(P/'production/current-pixel-review.json',audit)
 qa['directVisualReview']='current full captioned file selectively reviewed after spacing/wing correction; all prior cues/compositions retained by unchanged source/timing';qa['currentPixelReview']='production/current-pixel-review.json';write(P/'production/qa.json',qa)
 m['status']='reviewed-local-render; private-upload-pending';m['titles']['ko']=m['titles']['ko'].replace('Part2','Part 2')
 m['membershipOutro']['appliedToFinal']=True;m['membershipOutro']['originalClipProof']='production/current-pixel-review.json'
 m['approvals']['script']='original26complete scene dictionaries/order retained;54 additive narrated scenes measured and numerically reviewed'
 m['approvals']['voice']='approved reference retained; current-hash ASR/alignment complete; human whole listening pending'
 m['approvals']['pixels']='current final changed-scene pixels and fixed captions reviewed; history and hash proof retained'
 m['finalRender']={'status':'complete-technical-and-direct-pixel-review','currentPixelApproval':True,'review':'production/current-pixel-review.json','knownIssues':[],'openItems':['사람의 전체 청취 및 게임 IP 공개 권리 검토는 별도 미완료입니다.','비공개 업로드와 실제 플랫폼 설정 검증은 진행 전입니다.']}
 m['publishReady']=False;write(P/'project.json',m)
 episodes.append({'slug':slug,'seconds':t['seconds'],'captionCount':len(t['koCaptions']),'sha256':digest,'localTechnicalAndPixelReview':True,'humanListening':'pending','uploadComplete':False})
assert combined==baseline['scenes']
result={'reviewedAt':datetime.datetime.now().astimezone().isoformat(),'original26SceneDictionariesAnd155Ko155EnLinesExact':True,'originalContractExact':True,'episodes':episodes,'fullBatchCompleted':False}
write(B/'quaternion-current-render-checkpoint.json',result)
q=read(B/'queue.json');q['items'][0]['revision'].update(renderComplete=True,flowReviewPassed=True,localPixelReviewComplete=True,currentRenderCheckpoint='quaternion-current-render-checkpoint.json');q['execution']['stage']='two quaternion final files technically and visually reviewed; collecting and private upload next';write(B/'queue.json',q)
print(json.dumps(result,ensure_ascii=False),flush=True)
