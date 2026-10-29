"""Bind full V1 sampled reviews plus two-cut delta QA to the exact final master."""
from pathlib import Path
import datetime, hashlib, json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];EDIT=HERE.parent/'local/botw-v4/edit'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def evidence(name):return {'path':rel(HERE/name),'sha256':sha(HERE/name)}
def main():
 plan=read(HERE/'edit-plan.json');correction=read(HERE/'final-visual-corrections.json')
 before=read(EDIT/'review-v1-preserved/edit-plan.json');pair=read(EDIT/'pair-build.json');priorpair=read(EDIT/'review-v1-preserved/pair-build.json');structure=read(EDIT/'structural-verification.json')
 delta=read(HERE/'gameplay-delta-pixel-review.json');native=read(HERE/'native-final-pixel-review.json');caption=read(HERE/'caption-final-pixel-review.json');binding=read(HERE/'native-binding.json')
 current_sha=sha(EDIT/'kind-to-beginners-captioned.mp4');plan_sha=sha(HERE/'edit-plan.json')
 assert correction['editPlanSha256']==plan_sha and correction['priorEditPlanSha256']==sha(EDIT/'review-v1-preserved/edit-plan.json')
 assert delta['status']=='passed' and delta['captionedSha256']==current_sha and delta['editPlanSha256']==plan_sha
 assert structure['status']=='pass' and structure['outputs']['captioned']['sha256']==current_sha
 assert native['status']=='passed' and caption['passed'] and caption['cueCount']==113
 assert native['finalMasterSha256']==caption['captionedSha256']==priorpair['outputs']['captioned']['sha256']
 assert native['nativeBindingSha256']==sha(HERE/'native-binding.json')
 for name,wanted in correction['unchangedInputs'].items():
  p=EDIT/name if (EDIT/name).exists() else HERE/name
  assert sha(p)==wanted,(name,'changed')
 for item in correction['unchangedCutMedia']:assert sha(EDIT/(item['cut']+'.mp4'))==item['sha256']
 assert len(correction['unchangedCutMedia'])==51
 for a,b in zip(before['cuts'],plan['cuts']):
  if a['id'] in ['04-05','07-01']:
   assert {k:v for k,v in a.items() if k!='marks'}=={k:v for k,v in b.items() if k!='marks'}
  else:assert a==b
 assert {k:v for k,v in before.items() if k!='cuts'}=={k:v for k,v in plan.items() if k!='cuts'}
 for name in ['aacSha256','captionsAssSha256','encoder','codeSha256','frameClock']:
  assert pair['signature'][name]==priorpair['signature'][name],name
 for item in caption['captionInputs']:assert sha(ROOT/item['path'])==item['sha256']
 for cap in binding['captures']:
  assert sha(ROOT/cap['movie'])==cap['movieSha256']
  assert sha(ROOT/cap['scene'])==cap['sceneSha256']
  assert sha(ROOT/cap['sceneMeta'])==cap['sceneMetaSha256']
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 reused=[evidence(n) for n in ['native-final-pixel-review.json','caption-final-pixel-review.json','gameplay-final-pixel-review.json']]
 basis={'priorMasterSha256':priorpair['outputs']['captioned']['sha256'],'unchangedCutCount':51,'changedCutIds':['04-05','07-01'],'sameCaptionFilesAndClock':True,'sameNative22MoviesAndScenes':True,'sameContinuousAac':True,'sameEncoderAndAssemblyCode':True,'method':'Reuse prior full sampled pixel review for identical scene/caption inputs; directly inspect newly encoded two-cut marks and adjacent boundaries. This is not a claim to have watched every frame continuously.','priorReviews':reused,'deltaReview':evidence('gameplay-delta-pixel-review.json'),'correctionEvidence':evidence('final-visual-corrections.json')}
 save(HERE/'pixel-review.json',{'status':'passed','at':now,'revision':'botw-v4','editPlanSha256':plan_sha,'captionedSha256':current_sha,'captionsAssSha256':sha(EDIT/'captions.ko.ass'),'captionsKoSha256':sha(EDIT/'captions.ko.srt'),'captionsEnSha256':sha(EDIT/'captions.en.srt'),'reviewBasis':basis,'coverage':{'gameplayCuts':31,'nativeExplanationCuts':22,'koreanCaptionCues':113,'sampledPriorStates':341,'additionalGameStates':7},'scope':'Sampled direct encoded pixels at1080 and375px plus source/caption/clock preservation; whole human viewing/listening remains pending.','blockingFindings':[],'humanWholeReview':'pending','actualListeningPerformed':False})
 save(HERE/'native-review.json',{'status':'passed','at':now,'revision':'botw-v4','editPlanSha256':plan_sha,'captionedSha256':current_sha,'nativeBindingSha256':sha(HERE/'native-binding.json'),'savedScenePaths':binding['savedScenePaths'],'captureCount':22,'compiledFingerprint':binding['compiledFingerprint'],'sourceReview':evidence('native-final-pixel-review.json'),'reviewReuseBasis':basis,'directSampledStateCount':184,'nativeRerenderForTwoGameplayMarks':False,'actualListeningPerformed':False,'humanWholeReview':'pending'})
 correction['status']='passed-final-delta-review';correction['finalCaptionedSha256']=current_sha;correction['deltaReview']=evidence('gameplay-delta-pixel-review.json');save(HERE/'final-visual-corrections.json',correction)
 # Refresh evidence after the completion receipt has its final status.
 for name in ['pixel-review.json','native-review.json']:
  obj=read(HERE/name);key='reviewBasis' if name=='pixel-review.json' else 'reviewReuseBasis';obj[key]['correctionEvidence']=evidence('final-visual-corrections.json');save(HERE/name,obj)
 print('Final QA aggregated with explicit unchanged-input reuse',current_sha)
if __name__=='__main__':main()
