"""Register the completed local polish in existing records, never upload."""
from datetime import datetime,timezone
import common as c

def main():
 out=c.read(c.H/'outputs.json');qa=c.read(c.H/'technical-qa.json');pixels=c.read(c.H/'pixel-review.json')
 assert qa['status']=='pass' and pixels['status']=='pass-with-stated-scope'
 for item in out['outputs']:assert c.sha(c.R/item['path'])==item['sha256']
 master=next(x for x in out['outputs'] if x['path'].endswith('.captioned.mp4'))
 assert pixels['finalMasterSamplesReviewed'] and pixels['captionedMasterSha256']==master['sha256']
 assert pixels['assemblySha256']==c.sha(c.H/'assembly.json')
 now=datetime.now(timezone.utc).isoformat()
 review={'revision':'private-baseline-visual-polish-v1','status':'ready-for-human-local-review','availableAt':now,
  'directory':'output/game-math-euler-axis-angle-private-polish','index':'output/game-math-euler-axis-angle-private-polish/index.html',
  'captionedVideo':master['path'],'captionedMasterSha256':master['sha256'],'durationSeconds':c.T['seconds'],
  'technicalQa':'production/private-polish-v1/technical-qa.json','pixelReview':'production/private-polish-v1/pixel-review.json',
  'humanFinalReview':'pending','wholeHumanListening':'pending','youtubeUploadAuthorized':False,'driveUploadAuthorized':False,
  'automaticNextVideo':False,'originalUpload':'https://youtu.be/iv9esV7vv_g','originalUploadChanged':False}
 out['fullReviewStatus']='internal-checks-complete-with-baseline-audio-limitation';out['localReview']=review;c.save(c.H/'outputs.json',out)
 plan=c.read(c.P/'planning/production-plan.json');polish=plan['baselineVisualPolish'];polish['status']='local-final-review-ready'
 polish['localReview']=review;polish['implementation']={
  'originalSceneCount':26,'nativeUnityExplanations':12,'actualGameplayScenes':8,'actualSeconds':447.7666666667,
  'bodyActualShare':.4,'shareReason':'Preserved original approved timing; no new quota or filler.',
  'unityPlacement':'production/private-polish-v1/unity-placement.json','gameplayPlacement':'production/private-polish-v1/gameplay-placement.json',
  'codeStyle':'production/private-polish-v1/code-style.json','assembly':'production/private-polish-v1/assembly.json',
  'restoration':'production/private-polish-v1/restoration.json','savedUnityScenesHashVerified':12,
  'model':'Existing self-authored detailed aircraft, shared editable Unity scenes retained.',
  'audio':'Recovered uploaded AAC performance, stream-copy preserved; original PCM missing; no new TTS or music.',
  'preservedLegacyScope':'Original narration, gameplay choices, cut order, white palette and narration-only audio are retained by the current baseline-preserving request. No wholesale lesson rewrite.'}
 for scene in polish['scenes']:
  sid=scene['id'];scene['status']='rendered-and-checked;human-review-pending';scene['finalClipSha256']=c.sha(c.O/'clips'/f'{sid}.mp4')
  if c.SCENES[sid].get('cuts'):
   scene['change']='관찰 문장에 맞춘 화면 좌표 안내 원·연결선. 가려지거나 확정할 수 없는 팔 끝/세계 회전축을 추정하지 않음.'
   if sid=='20':scene['change']+=' 검증한 몸통 중심의 점과 과거 화면 위치 궤적을 추가.'
  elif sid=='15':scene['change']='원래 C++ 코드와 말 시점 유지. 48px 문법 색·행 번호·현재 줄 표식.'
  elif sid=='24':scene['change']='원래 수식·대본 유지. 720°/s·1080°/s 시연의 2회전·3회전 시간을 1초로 맞춤.'
  elif sid=='25':scene['change']='원래 두 문제 유지. 라디안 함수에 도 단위를 넣는 듯한 화면 표기만 도 단위 산술식으로 정정.'
  elif sid in ['03','04','06','07','09','10','12','16','18','19','21','22']:
   scene['change']='기존 편집 가능한 Unity 비행기·축 모형을 원래 문장 시점에 배치. 실제 모형 앵커의 축 라벨과 해당 수식만 표시.'
 polish['rebuild']=['restore.py prepare','restore.py flat','unity.py','graphics.py','gameplay.py','verify.py layout','assemble.py','verify.py final']
 c.save(c.P/'planning/production-plan.json',plan)
 project=c.read(c.P/'project.json');project['activeVisualPolish'].update(status='local-final-review-ready',localReview=review);project['updatedAt']=now;c.save(c.P/'project.json',project)
 ledger=c.read(c.P/'production/review-ledger.json');ledger['activeVisualPolishReview']={
  'revision':review['revision'],'updatedAt':now,'baselineVideoId':'iv9esV7vv_g','checks':[
   {'name':'actual Studio inventory','status':'pass','evidence':'shared/publishing/game-math-private-polish-studio-observation.json','private':20,'main':17,'older':3},
   {'name':'original timeline/narration/cuts','status':'pass','evidence':'production/private-polish-v1/assembly.json'},
   {'name':'native FHD gameplay and editable Unity scenes','status':'pass','evidence':'production/private-polish-v1/gameplay-placement.json'},
   {'name':'axis labels','status':'pass','evidence':'production/private-polish-v1/layout-qa.json'},
   {'name':'current pixels/mobile/sequence samples','status':pixels['status'],'evidence':'production/private-polish-v1/pixel-review.json'},
   {'name':'whole decode and recovered audio identity','status':'pass','evidence':'production/private-polish-v1/technical-qa.json'},
   {'name':'human review of this final master','status':'pending','sha256':master['sha256']}],
  'localReview':review,'oldLedgerHistoryRetained':True}
 c.save(c.P/'production/review-ledger.json',ledger)
 work=c.read(c.R/'shared/publishing/video-worklist.json');row=next(x for x in work['rows'] if x['id']=='M04')
 row['privatePolish'].update(status='시각 보강본 완성 · 로컬 검수 대기',annotationsComplete=True,animationPolishComplete=True,renderComplete=True,technicalQaComplete=True,
    task='게임 관찰 안내선·중심점 / Unity 축·회전 모형 / 코드 문법 색·현재 줄',humanReview='새 완성본 검수 대기',localReview=review)
 row['executionStatus']='기존 비공개본 시각 보강 완료 · 로컬 검수 대기';row['reviewStatus']='자체 검사 완료 / 사용자 새 버전 검수 대기'
 row['latestRulesPassed']=True;row['privatePolish']['rulesScope']='Selected visual-only revision passed; original lesson/audio/palette preserved as explicitly requested.'
 work['privateMathPolish']['updatedAt']=now;work['updatedAt']=now;c.save(c.R/'shared/publishing/video-worklist.json',work)
 control=c.read(c.R/'shared/publishing/video-production-control.json');a=control['scopedProductionAuthorizations'][c.P.name]
 a.update(status='local-final-review-ready',localReview=review,humanFinalReview='pending',fullProductionAuthorized=False,renderAuthorized=False)
 control['updatedAt']=now;c.save(c.R/'shared/publishing/video-production-control.json',control)
 c.save(c.P/'production/checkpoint.json',{'schemaVersion':1,'slug':c.P.name,'revision':review['revision'],'updatedAt':now,
  'stage':'local-final-review-ready','baselineVideoId':'iv9esV7vv_g','completed':['17 main private lessons inventoried;3 older versions preserved',
  'Original26-scene18:51.4167 timeline and existing narration restored','FHD gameplay annotations and12 Unity spatial scenes','Current pixels/mobile checks, whole decode, unchanged recovered audio,4outputs'],
  'localReview':review,'blockers':[],'nextAction':'Wait for user review of the exact complete captioned master; no automatic next video or platform change.',
  'platformMutation':False,'automaticNextVideo':False,'finalUserReview':'pending','previousCompletedV8':'production/revision-v8-orientation-matrix/production-checkpoint.json'})
 print('Registered local review;17-video table retained, next16 waiting.',flush=True)

if __name__=='__main__':main()
