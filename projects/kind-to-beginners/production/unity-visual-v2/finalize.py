"""Publish verified local four-file deliveries; never touch a video platform."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[4]
def load(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--slug',choices=['kind-to-beginners','respect-player-time'],required=True);a=ap.parse_args();slug=a.slug
 p=ROOT/'projects'/slug;rev=p/'production/unity-visual-v2';local=p/'production/local/unity-visual-v2';final=local/'final'
 assert local.is_dir(),'Parent-approved local media junction missing'
 plan=load(rev/'visual-plan.json');proof=load(final/'structural-verification.json');assembly=load(final/'assembly-result.json');pixels=load(rev/'pixel-review.json')
 assert proof['audioExact'] and proof['captionsExact'] and pixels['status']=='passed' and pixels['reviewedExplanationCuts']==len(plan['explanationCuts'])
 assert all(x['everyFramePtsExact'] for x in proof['outputs'])
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();manifest=load(p/'project.json')
 files={'videoBurnedCaptions':final/(slug+'-unity-visual-v2-captioned.mp4'),'videoClean':final/(slug+'-unity-visual-v2-clean.mp4'),'captionsKo':final/'captions.ko.srt','captionsEn':final/'captions.en.srt'}
 hashes={k:sha(v) for k,v in files.items()}
 for k in ['videoBurnedCaptions','videoClean']:
  kind='captioned' if k=='videoBurnedCaptions' else 'clean';assert hashes[k]==assembly['outputs'][kind]['sha256']
 manifest['revision']='unity-visual-v2';manifest['status']='local-review-ready';manifest['updatedAt']=now;manifest['publishReady']=False
 manifest['delivery']['localStorageRoot']=f'projects/{slug}/production/local/unity-visual-v2/delivery'
 manifest['paths'].update({k:v.relative_to(ROOT).as_posix() for k,v in files.items()})
 manifest['visualRevisionPlan']=f'projects/{slug}/production/unity-visual-v2/visual-plan.json';manifest['paths']['visualRevisionPlan']=manifest['visualRevisionPlan']
 manifest['review']={'actualUserViewed':False,'humanWholeListening':'pending','baselineStoryAndOrderUserLiked':True,'newVisualVersionHumanReview':'pending'}
 manifest['finalRender']={'status':'complete-local-review-ready','knownIssues':[],'openItems':['새 Unity 설명 화면의 실제 전체 시청·최종 청취 검수 대기.']}
 manifest['localFinalReview']={'durationSeconds':assembly['seconds'],'actualUserViewed':False,'humanWholeListening':'pending','internalQa':'complete','reviewRecord':f'projects/{slug}/production/unity-visual-v2/review-status.json'}
 save(p/'project.json',manifest)
 subprocess.run(['node','scripts/collect-video-output.cjs',slug],cwd=ROOT,check=True)
 delivery=load(p/'production/delivery-output.json');droot=delivery['directory'];manifest['localFinalReview'].update({'index':droot+'/index.html','files':{k:f'{droot}/{slug}.{k}' for k in ['captioned.mp4','clean.mp4','ko.srt','en.srt']},'sha256':{x['name'].removeprefix(slug+'.'):x['sha256'] for x in delivery['files']}});save(p/'project.json',manifest)
 baseline_review=load(p/'production/review-status.json')
 cut_count=len(plan['explanationCuts']);scene_paths=[f'unity/VideoEditing/{c["scenePath"]}' for c in plan['explanationCuts']]
 assert all((ROOT/s).is_file() for s in scene_paths)
 review={'slug':slug,'revision':'unity-visual-v2','status':'local-review-ready','updatedAt':now,'fourOutputsVerified':True,'captionedSha256':hashes['videoBurnedCaptions'],'durationSeconds':assembly['seconds'],'technicalSummary':f'1920×1080 · 60fps · {assembly["expectedFrames"]}프레임. 두 완성본 전체 디코드·매 프레임 PTS·단조 DTS 통과. 실제 게임 컷·재생 속도·배분·전체 길이 유지.', 'visualSummary':f'설명 {cut_count}컷을 저장된 Unity 씬으로 교체. 7개 native 동작 상태, 주요 1080p 화면, 모든 변경 컷의 실제 최종 자막 4상태/375px 검수 완료. 이야기·순서·자막은 그대로 유지.', 'audioSummary':'기존 검수본의 최종 AAC 패킷을 그대로 복사해 SHA256 일치 확인. 내레이션·Nimbus BGM·기존 허용 게임 원음과 음량을 변경하지 않음. 기존 음성/발음 검수 근거 승계, 새 TTS/ASR 없음.', 'reviewFocus':['글 대신 보이는 물체·입력·결과가 설명 이해를 돕는지','실제 게임 장면과 Unity 설명의 연결','기존 내레이션과 새 동작의 호흡'],'humanWholeReview':'pending','humanWholeListening':'pending','actualUserReview':False,'nativeReplacedCutCount':cut_count,'savedScenePaths':scene_paths,'outputs':delivery['files'],'directory':delivery['directory'],'captureVersion':assembly['captureVersion'],'compiledSourceFingerprint':assembly['compiledSourceFingerprint'],'directQA':{'captureSourcePin':f'projects/{slug}/production/unity-visual-v2/capture-source-pin.json','nativePoseComparison':f'projects/{slug}/production/unity-visual-v2/native-pose-review-v4.json','native':f'projects/{slug}/production/unity-visual-v2/preflight-review.json','finalPixels':f'projects/{slug}/production/unity-visual-v2/pixel-review.json','structure':f'projects/{slug}/production/local/unity-visual-v2/final/structural-verification.json','assembly':f'projects/{slug}/production/local/unity-visual-v2/final/assembly-result.json','baselineAudioEvidence':baseline_review.get('evidence',{})},'baselinePreserved':plan['baseline'],'platformMutation':False}
 save(rev/'review-status.json',review)
 checkpoint={'slug':slug,'revision':'unity-visual-v2','status':'local-review-ready','updatedAt':now,'completed':['Frozen baseline/narration/scene order retained','Licensed imported assets and editable Unity scene per explanation cut','Native motion/preflight and final captioned visual QA','Two complete 1080p60 videos and unchanged KO/EN SRT','Original final AAC packets copied and verified','Local four-file output collection'],'pending':['Actual user whole-video viewing/listening of this new visual version'],'outputIndex':manifest['localFinalReview']['index'],'captionedSha256':hashes['videoBurnedCaptions'],'newTtsRuns':0,'platformMutation':False,'captureVersion':assembly['captureVersion'],'compiledSourceFingerprint':assembly['compiledSourceFingerprint'],'sourcePin':f'projects/{slug}/production/unity-visual-v2/capture-source-pin.json','review':f'projects/{slug}/production/unity-visual-v2/review-status.json'}
 save(rev/'checkpoint.json',checkpoint)
 plan['status']='local-review-ready';plan['finalDelivery']={'index':manifest['localFinalReview']['index'],'files':manifest['localFinalReview']['files'],'captionedSha256':hashes['videoBurnedCaptions'],'humanWholeReview':'pending'};save(rev/'visual-plan.json',plan)
 print(slug,'local delivery complete',hashes['videoBurnedCaptions'])
if __name__=='__main__':main()
