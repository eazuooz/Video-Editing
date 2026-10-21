"""Record the human-selected visual polish without erasing previous revisions."""
from pathlib import Path
import copy, datetime, hashlib, json, shutil

R = Path(__file__).resolve().parents[4]
P = R / 'projects/game-math-euler-axis-angle'
H = Path(__file__).resolve().parent
O = P / 'production/local/private-polish-v1'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p, v):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
observation = read(O/'studio-observation.json')
private = {r['videoId']: r for r in observation['rows'] if r.get('visibility') == '비공개'}
assert len(private) == 20
evidence = 'shared/publishing/game-math-private-polish-studio-observation.json'
save(R/evidence, {**observation, 'scope': 'Private Game Math inventory; title search also returns older public lessons.',
                  'privateRows': list(private.values()), 'platformMutation': False})
work = read(R/'shared/publishing/video-worklist.json')
targets = [r for r in work['rows'] if r['series']=='M' and 4<=int(r['id'][1:])<=20]
assert len(targets)==17 and all(r['videoId'] in private for r in targets)
focus = [
 '몸통 방향·팔선·몸체축 / 회전 순서·짐벌락·축각 모형 가독성',
 '단위축·회전각·켤레와 역원 연결 표시', '곱셈 순서·목표 자세·회전 전후 벡터 비교',
 '두 자세 사이 경로·진행률·속도 변화 표시', '동일 자세를 공유하는 표현과 성분 대응',
 '두 끝점·선분 방향·매개변수 t와 결과점', '경계상자·중심·반지름과 회전 전후 비교',
 '표면·법선·수선 발·부호 있는 거리', '삼각형 꼭짓점·가중치·내부 점 대응',
 '중심 정의·경계·선택 목적 비교', '오목 경계·분할 대각선·빈 공간 보존',
 '빛·표면 법선·시선 벡터와 밝기 대응', '시야각·프러스텀·출력 창 대응',
 '같은 3D점의 좌표계 변환 경로 추적', '깊이·동차좌표 w·나눗셈 전후 값',
 '정점·면·법선과 메시 연결', '법선 변환·UV 좌표·텍스처 위치 대응']
for row, task in zip(targets, focus):
    live=private[row['videoId']]
    row['platformStatus']='비공개'
    row['platformEvidence']={'path':evidence,'observedAt':observation['observedAt'],'videoId':row['videoId'],'visibility':'private'}
    row['privatePolish']={
      'order': int(row['id'][1:])-3, 'baselineVideoId':row['videoId'], 'baselineTitle':live['title'],
      'duration':live['duration'], 'baselinePreserved':True, 'inventoryVerified':True,
      'task':task, 'scope':'기존 대본·음성·순서·유용한 예시 유지. 표식·가독성·필요한 애니메이션만 보강.',
      'status':'코드 복원·표식 제작 착수' if row['id']=='M04' else '대기 — 개별 착수 전',
      'selected':row['id']=='M04','contentReviewed':row['id']=='M04',
      'annotationsComplete':False,'animationPolishComplete':False,'renderComplete':False,
      'technicalQaComplete':False,'humanReview':'수정본 검수 전','uploadAuthorized':False,
      'sourceMaster':'업로드 원본 코드·타임라인에서 재렌더' if row['id']=='M04' else '선택 시 원본 코드·미디어 확인'}
main_ids={r['videoId'] for r in targets}
work['privateMathPolish']={
 'updatedAt':now,'policy':'baseline-preserving-visual-polish-v1','evidence':evidence,
 'privateUploadCount':20,'mainLessonCount':17,'selected':'M04','automaticNextVideo':False,
 'userEvidence':'새로만들지 말고 이전에 잘만들어진걸 수정하고 다듬어서 가독성과 이해하기 쉽게 좀더 바꾸는거야',
 'restorationEvidence':'그 코드 그대로 잇을꺼야 그걸로 그대로 렌더링해서 작업해줘~',
 'olderVersions':[dict(**r,status='기존 버전 보존·중복 제작 제외') for k,r in private.items() if k not in main_ids],
 'outOfScope':'공개 M01–M03, 미업로드 M21 이후, 기존 플랫폼 변경·삭제·새 업로드',
 'preserve':['narration','audio performance','section order','useful gameplay','timing','original palette'],
 'apply':['property-matched annotations','readable type and code colors','speech-synchronized animation','fixed captions','1080p60 / mobile QA']}
selected=next(r for r in targets if r['id']=='M04')
selected['title']=private['iv9esV7vv_g']['title']
selected['executionStatus']='기존 비공개본 코드 복원·시각 보강 중'
selected['reviewStatus']='기존본 검토 착수 / 시각 보강본 검수 전'
selected['latestRulesPassed']=False
selected['privatePolish']['plan']='projects/game-math-euler-axis-angle/planning/production-plan.json#baselineVisualPolish'
work['updatedAt']=now
save(R/'shared/publishing/video-worklist.json',work)
baseline=read(P/'publishing/youtube-upload.json')
timeline=read(P/'production/timeline.json')
lessonpath=R/'production/batches/game-math-part2-full-series/lessons/game-math-euler-axis-angle.json'
lesson=read(lessonpath)
for name in ['production-plan.json','checkpoint.json']:
    source=P/('planning' if name=='production-plan.json' else 'production')/name
    dest=O/('before-'+name)
    if not dest.exists(): shutil.copy2(source,dest)
auth={
 'project':P.name,'revision':'private-baseline-visual-polish-v1','selectedOn':now,
 'status':'authorized-existing-code-restoration-and-visual-polish',
 'userEvidence':work['privateMathPolish']['userEvidence'], 'restorationEvidence':work['privateMathPolish']['restorationEvidence'],
 'baselineVideoId':'iv9esV7vv_g','baselineScope':'Original 18:51.4167 Euler/axis-angle upload, not local V8 matrix lesson.',
 'fullProductionAuthorized':True,'renderAuthorized':True,'newTtsAuthorized':False,'scriptRewriteAuthorized':False,
 'platformMutation':False,'automaticNextVideo':False,'humanFinalReview':'pending',
 'originalTimelineSha256':sha(P/'production/timeline.json'),'originalLessonSha256':sha(lessonpath),
 'scope':'Restore original code at original timing; preserve narration/audio and examples; add tracked guides, improve needed spatial illustrations and text; four local outputs and selective Git.'}
save(H/'authorization.json',auth)
control=read(R/'shared/publishing/video-production-control.json')
prior=control['scopedProductionAuthorizations'].get(P.name,{})
if prior.get('revision')!=auth['revision']:
    save(H/'previous-authorization-v8.json',prior)
control['scopedProductionAuthorizations'][P.name]={**auth,'previousProductionRecord':str((H/'previous-authorization-v8.json').relative_to(R)).replace('\\','/')}
control['updatedAt']=now
save(R/'shared/publishing/video-production-control.json',control)
changes={
 '01':'원래 개요·네 단계 유지. 제목/진행 화살표 대비만 점검.',
 '02':'몸통 방향 화살표·팔선 추적. 회전축의 실제 측정값처럼 표시하지 않음.',
 '03':'원래 세 축 규약 유지, 비행기·축·라벨 확대.',
 '04':'몸체 Y→X→Z 회전을 같은 원래 말 큐에서 Unity 모형으로 표시.',
 '05':'몸통 방향·팔선과 화면 수직 기준을 분리. 카메라 영향은 측정하지 않음.',
 '06':'몸체/월드 축 비교에서 동시 강조와 같은 최종 자세 확인.',
 '07':'X→Y / Y→X의 현재 단계와 끝 방향 화살표 강화.',
 '08':'방향 전환 후 팔선 변화만 실제 보이는 구간에 표시.',
 '09':'서로 다른 세 숫자가 같은 자세에 대응하는 선·강조.',
 '10':'겹치는 축을 굵은 축선과 양/음 화살표로 구분. 짐벌락 규약 유지.',
 '11':'몸의 기울기만 추적; 게임 내부 짐벌락이라고 표시하지 않음.',
 '12':'두 자세와 h−b / h+b의 대응값을 같은 시각에 강조.',
 '13':'긴 340도 경로와 짧은 −20도 호의 단계적 표시.',
 '14':'목표 방향보다 실제 변화 경로를 짧은 추적선으로 가시화.',
 '15':'원래 wrap 코드 유지. 타입/함수/변수/리터럴/현재 줄 구분.',
 '16':'동일 시작/끝과 중간 경로 비교, 입력값과 자세를 나란히 표시.',
 '17':'시작/중간/끝 구간에서 자세 표시. 서로 다른 컷은 초기화.',
 '18':'단위축 n·각도 θ·회전호를 원래 문장에 맞춰 표시.',
 '19':'축 방향과 벡터 길이의 뜻 연결. 영 벡터 조건 강조.',
 '20':'중심점 이동과 팔선 회전을 별도 표식으로 구분.',
 '21':'같은 끝 자세와 다른 회전 경로를 색+라벨로 대조.',
 '22':'순차 회전과 성분 합을 같은 시점 비교. 유한각 조건 유지.',
 '23':'보이는 몸 방향 변화만 표시; 내부 합성 알고리즘 추정 금지.',
 '24':'2회전/3회전 카운터와 동일 끝 자세 대조.',
 '25':'원래 두 문제·해설 유지, 대입 중인 숫자/단위만 강조.',
 '26':'원래 요약 유지. 앞서 쓴 축·순서·단위 표식을 함께 회수.'}
plan=read(P/'planning/production-plan.json')
plan['baselineVisualPolish']={
 'revision':auth['revision'],'selectedAt':now,'status':'restoration-and-visual-polish-started',
 'baselineVideoId':'iv9esV7vv_g','baselineUploadReceipt':'publishing/youtube-upload.json',
 'baselineMasterSha256':'94b7b142d9d12e82f4da8f50acbb95b77f912795dd798af00b07622288a5758c',
 'timeline':'production/timeline.json','timelineSha256':auth['originalTimelineSha256'],
 'lesson':str(lessonpath.relative_to(R)).replace('\\','/'),'lessonSha256':auth['originalLessonSha256'],
 'sourceAudit':{'all26NarrationScenesRead':True,'all26RepresentativeFramesViewed':True,'fullMovingReview':'pending',
   'reviewVideo':'production/local/revision-v2/baseline-studio-review-720p30.mp4','reviewOnly720p':True,
   'nativeGameplay':'production/local/revision-v2/sources/FvSgGn941U0.mp4','originalCode':'manim/projects/game-math-part2-full-series/euler.py'},
 'preserve':{'allNarrationText':True,'originalTiming':True,'noNewTts':True,'originalExamplesAndOrder':True,'approvedWhitePalette':True,
             'audio':'Recover the existing uploaded performance from Studio restoration. Compressed source is not original PCM; record this limitation. Do not invent PCM identity.'},
 'rendering':{'width':1920,'height':1080,'fps':60,'sourceUpscaleForbidden':True,'backgroundMusic':False,
              'approach':'Render existing code; reuse editable Unity aircraft for appropriate spatial scenes, original Manim equations; compose guides with original narration timing.'},
 'gameplayConvention':'Screen-space editorial body/arm guides only; unknown world axes/3D angles are not measured or asserted.',
 'scenes':[{'id':s['id'],'title':s['title'],'start':s['start'],'frames':s['frames'],'seconds':s['seconds'],
    'baselineClassification':s['classification'],'change':changes[s['id']], 'speechTiming':'Original timeline cues; no added observation silence.',
    'status':'source reviewed; implementation pending','captionReserve':[0,880,1920,200]} for s in timeline['scenes']],
 'humanFinalReview':'pending','uploadAuthorized':False}
save(P/'planning/production-plan.json',plan)
project=read(P/'project.json');project['activeVisualPolish']={**auth,'plan':'planning/production-plan.json#baselineVisualPolish'}
project['updatedAt']=now;save(P/'project.json',project)
save(P/'production/checkpoint.json',{'schemaVersion':1,'slug':P.name,'revision':auth['revision'],'updatedAt':now,
 'stage':'original-code-restoration-and-tracked-guides','baselineVideoId':'iv9esV7vv_g',
 'completed':['Studio inventory:17 main private lessons and3 older versions','Original26-scene narration and representative visuals reviewed','Original FHD Superflight source retained'],
 'nextAction':'Restore original timing/voice; render retained scene code, improve selected Unity/math illustrations and add tracked gameplay annotations.',
 'blockers':[],'platformMutation':False,'automaticNextVideo':False,'finalUserReview':'pending',
 'previousCompletedV8':'production/revision-v8-orientation-matrix/production-checkpoint.json'})
print('Registered17 main private lessons;3 older versions preserved;M04 original-code visual polish selected.')
