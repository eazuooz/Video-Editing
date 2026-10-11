"""Local additive draft only; old 80 scenes/media and live uploads stay intact.

Besiege's explicit description-link condition is recorded, not waived. The
pending human choice must be resolved before an external upload using it.
"""
from pathlib import Path
import copy,datetime,hashlib,json,math
import numpy as np

ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
O=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3'
MASTER='game-math-quaternion-cross-game-additions-v3'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
assert read(B/'queue.json')['execution']['mode']=='active'
base=read(R/'baseline.json')
assert sum(len(x['sceneIds']) for x in base['episodes'])==80
proof=read(O/'native-source-controls-4.json');played=json.loads(proof['proof'])
for ident,lo,hi in [('trailmakers-JvTCVUEc1ZE',665,700),('space-engineers-XvpNC9lkLwQ',172,181),('besiege-uWKEJ92486U',58.8,69.7),('portal2-steam-80739',18,32)]:
 assert any(x['id']==ident and x['in']<=lo and x['out']>=hi and x['rate']==1 and x['normalSpeedReachedEnd'] for x in played),(ident,'normal-speed comparison missing')
sources=read(O/'source-overviews.json');lookup={s['id']:s for s in sources}
required_links=['https://www.youtube.com/watch?v=uWKEJ92486U','http://multiverse.spiderlinggames.co.uk/']
info=read(O/'sources/besiege-uWKEJ92486U.info.json')
assert 'provided you include links' in info['description'] and 'monetize' in info['description']
comparison={
 'recordedAt':datetime.datetime.now().astimezone().isoformat(),
 'proof':(O/'native-source-controls-4.json').relative_to(ROOT).as_posix(),
 'proofMeaning':'1x playback reached each interval end; direct source pixels/dense frames inspected. This is not final moving-overlay QA or a human listening approval.',
 'selectedForLocalDraft':[
  {'game':'Trailmakers','sourceId':'trailmakers-JvTCVUEc1ZE','interval':[665,700],
   'before':'Aircraft rests on runway, wings approximately level.',
   'action':'Takeoff then visibly banked wings and a changing nose direction; later wings approach level.',
   'after':'Continued flight with a different visible orientation; no suggestion of rewinding its traveled route.',
   'clarity':'Same aircraft and continuous flight, no presenter illustration before 700. The 683-area bridge can occlude part of the craft: suppress uncertain tracks. Camera changes too, so only observed projected body directions are annotated.',
   'reason':'Longer continuous before/action/result than the 70–74.8 promo cut; enough time to identify nose and wings separately.',
   'priorUse':'New official tutorial source, absent from inspected project/publishing source history. Reuse between these two episodes is disclosed and teaches different operations; no loops within an episode.',
   'primarySource':'https://store.steampowered.com/news/posts/?appids=585420&enddate=1681992388&feed=steam_community_announcements',
   'rights':'Flashbulb official upload featuring Yzuei. No blanket reuse statement found; original audio excluded. Creator/game-IP human review remains pending.'},
  {'game':'Space Engineers','sourceId':'space-engineers-XvpNC9lkLwQ','interval':[172,181],
   'before':'Upright landing-gear preview over a grid.',
   'action':'174 and 177 show the preview on its side; 175 and 178 return it upright.',
   'after':'179–181 show placed upright gear. The later placement is a separate action.',
   'clarity':'Direction visibly changes near a stable floor reference; UI/host at right and bottom require a reviewed crop. Size changes around 176 must not be narrated as rotations.',
   'reason':'Direct manipulation of an asymmetric component gives a clearer orientation/inverse result than static 118–165 or 522–566 previews.',
   'priorUse':'New official first-ship tutorial source, absent from inspected project/publishing source history. Shared comparison anchor across episodes is disclosed.',
   'primarySource':'https://www.spaceengineersgame.com/how-to-play/',
   'rights':'Official tutorial; developer FAQ/EULA permit game capture/video creation, but this host/tutorial edit is separately recorded and not treated as blanket third-party permission. No source audio; human source/game-IP review pending.'},
  {'game':'Besiege','sourceId':'besiege-uWKEJ92486U','interval':[58.8,69.7],
   'before':'A subset of the contraption is highlighted; surrounding structures provide references.',
   'action':'63–66.8 show the rotation manipulator and changing selected-part directions.',
   'after':'Selected barrels have changed directions while unselected adjacent pieces retain theirs.',
   'clarity':'Selection colors and rotation rings are visible. Reset tracking at the camera cut near 63; suppress rings outside actual rotation. Do not relabel later translate arrows as rotation.',
   'reason':'Action follows a visible selection, unlike the rapid destruction montage in the Alpha trailer; no gore is used in this selected editor interval.',
   'priorUse':'New developer tutorial source, absent from inspected project/publishing source history. Same local comparison anchor across episodes is disclosed.',
   'primarySource':'https://store.steampowered.com/news/posts/?appids=346010&enddate=1522940994',
   'rights':'Spiderling description explicitly allows transformative footage/audio and monetization conditioned on two description links.',
   'requiredDescriptionLinks':required_links,'descriptionExceptionAuthorized':False,
   'externalUploadHold':'Await the asked user preference: required links, or replace this game. Local planning is not external delivery.'}
 ],
 'rejected':[
  {'game':'Tiny Glade','sourceId':'tiny-glade-257046593','interval':[12,24],'reason':'Native playback and 13–22 dense pixels show building resize/paint and height changes; no clear object rotation. Camera motion and a matching title are insufficient.'},
  {'game':'Space Engineers','sourceId':'space-engineers-XvpNC9lkLwQ','interval':[118,165],'reason':'Mostly size selection, static preview and camera movement. Does not show a clear rotate/result pair.'},
  {'game':'Space Engineers','sourceId':'space-engineers-XvpNC9lkLwQ','interval':[522,566],'reason':'Thruster preview stays largely static; camera/placement alone cannot demonstrate rotation.'},
  {'game':'Trailmakers','sourceId':'trailmakers-257325554','interval':[67,84],'reason':'Good 70–74.8 bank, but then several aircraft/camera cuts interrupt the causal story. The continuous tutorial is clearer.'},
  {'game':'Besiege','sourceId':'besiege-2036907','interval':[13,28],'reason':'Construction montage does not isolate a clear rotation with a stable reference.'},
  {'game':'Besiege','sourceId':'besiege-2036907','interval':[35,45],'reason':'Rapid machine changes and collisions; rotor motion is too brief and easily confused with camera motion.'},
  {'game':'Portal 2','sourceId':'portal2-steam-80739','interval':[18,32],'reason':'Native panel/robot sequence has rapid cuts, dark framing and camera changes. Viewer cannot compare one component orientation as clearly as the selected build tool.'}
 ],
 'finalAnnotatedMovingPixelsApproved':False,'measuredWorldAngles':False,'gameEngineQuaternionImplementationAsserted':False,
 'minimumGamesPerIndependentEpisode':4,'fourGameExternalDeliveryComplete':False
}
for x in comparison['selectedForLocalDraft']+comparison['rejected']:
 x['sourceFile']=lookup[x['sourceId']]['sourceFile'];x['sourceSha256']=lookup[x['sourceId']]['sha256']
write(R/'candidate-comparison.json',comparison)

data=[
 ('QF00','foundations','01','explanation','같은 회전을 다른 게임으로 옮겨 보기',[
  '스키뿐 아니라 비행기와 조립 부품에서도 비교합니다. 무엇이 달라지고 무엇은 그대로인지 확인해 보세요.'
 ],['Alongside skiing, we compare aircraft and assembled components. Identify what changes and what remains the same.']),
 ('QF10','foundations','GA07','actual','트레일메이커스: 기수와 날개를 따로 보기',[
  '이번엔 트레일메이커스의 비행기입니다. 빨간 기수선과 파란 날개선을 같이 보세요. 이륙한 뒤 두 방향이 달라지고, 기체가 기울었다가 수평에 가까워집니다.',
  '스키처럼 위치와 자세를 나누어 봅니다. 자세가 달라져도 비행은 계속되죠. 선은 화면에서 관찰한 방향이며, 실제 각도나 내부 계산을 측정한 값은 아닙니다.'
 ],['This is a Trailmakers aircraft. Inspect the red nose direction and blue wing direction together. After takeoff, the aircraft banks and later approaches level wings.','As with skiing, separate position from orientation: flight continues while orientation changes. These lines depict observed screen directions, not measured world angles or internal calculations.']),
 ('QF11','foundations','QF10','explanation','같은 각도, 다른 축',[
  '계산용 비행기 모형에서는 앞을 엑스, 오른쪽 날개를 와이, 위를 제트 방향으로 정하겠습니다. 실제 게임의 좌표계라고 가정하지는 않습니다.',
  '앞축으로 구십 도 돌리면 기수 방향은 그대로이고 오른쪽 날개 방향은 위로 갑니다. 네 성분은 루트 이 나누기 이, 같은 값, 영, 영입니다. 앞에서 본 제트축 회전과 각도는 같지만 축을 담는 자리가 다르죠.'
 ],['For our defined aircraft model, x points forward, y points toward the right wing, and z points up. This is not an assumed game coordinate system.','A ninety-degree turn around the forward axis leaves the nose direction unchanged and moves the right-wing direction upward. Its wxyz components are square root of two over two, the same value, zero, zero. The angle matches our earlier z-axis turn, but the axis occupies a different component.']),
 ('QF20','foundations','GA08','actual','스페이스 엔지니어스: 부품을 돌렸다 되돌리기',[
  '우주선 부품을 보세요. 옆으로 돌렸다 되돌리면, 방향도 다시 처음 모습이 됩니다.'
 ],['Observe the ship component: turning it onto its side and back restores its earlier orientation.']),
 ('QF21','foundations','QF20','explanation','되돌리는 것은 방향 연산입니다',[
  '이제 계산용 모형의 처음 방향을 일, 영, 영으로 둡니다. 제트축으로 구십 도 돌리면 영, 일, 영이 됩니다. 반대 구십 도를 적용하면 일, 영, 영으로 돌아옵니다.',
  '이 되돌리는 회전이 역원입니다. 부품을 놓은 위치나 지난 이동까지 지우는 뜻은 아닙니다. 실제 영상의 각도를 잰 것이 아니라, 검산할 수 있는 모형을 정한 것입니다.'
 ],['Define the initial model direction as one, zero, zero. A ninety-degree z-axis turn gives zero, one, zero; the opposite ninety-degree turn restores one, zero, zero.','The cancelling rotation is the inverse. It does not erase placement or traveled motion. These are defined, checkable model angles, not measurements from the footage.']),
 ('QF30','foundations','GA09','actual','비시지: 선택한 부품에만 회전 적용',[
  '비시지의 주황색 선택 부품을 보세요. 회전을 적용하면 옆의 부품은 남고, 선택한 방향들이 함께 달라집니다.'
 ],['Inspect the orange selected Besiege parts. A rotation changes their directions together while neighboring unselected parts remain.']),
 ('QF31','foundations','QF30','explanation','대상은 달라도 회전은 같은 규칙',[
  '모형에서 오른쪽 방향과 위쪽 방향에 같은 구십 도 회전을 적용하면, 두 방향 사이의 직각은 유지됩니다. 방향마다 다른 회전을 적용하는 것과는 다릅니다.',
  '스키, 비행기, 우주선 부품, 조립한 기계는 모양이 달라도 방향을 바꾸는 문제를 만납니다. 이제 같은 회전을 한 번 더 적용하면 어떻게 되는지, 기존 계산에서 확인하겠습니다.'
 ],['Applying the same ninety-degree model rotation to two perpendicular directions preserves their right angle. That differs from applying a different rotation to each direction.','Skis, aircraft, ship parts and assembled machines all present orientation problems despite their different shapes. We now return to the original calculation and apply the same rotation a second time.']),
 ('QC00','calculations','F03','explanation','네 게임에서 입력과 결과 비교',[
  '이번에도 비행기와 조립 부품을 함께 비교합니다. 게임별 조작법을 외우기보다 현재 방향, 적용할 회전, 결과 방향을 연결해 보세요.'
 ],['We again compare aircraft and assembled components. Connect the current direction, applied rotation and resulting direction across games.']),
 ('QC10','calculations','GB01','actual','트레일메이커스: 물체의 방향과 보는 방향',[
  '트레일메이커스에서는 비행기가 기울고 기수의 방향도 바뀝니다. 빨간 기수선과 파란 날개선을 따라가세요. 물체의 앞과 옆을 함께 봐야 자세를 구분할 수 있습니다.',
  '카메라도 움직이므로 화면의 기울기만 읽어서 게임 속 구십 도라고 단정하지 않습니다. 다음 모형에서는 공간의 축을 고정하고 회전 순서만 바꾸어 비교하겠습니다.'
 ],['The Trailmakers aircraft banks and changes its nose direction. Follow the red nose line and blue wing line together to distinguish its orientation.','The camera also moves, so a screen tilt does not establish a ninety-degree world rotation. Our next model fixes the spatial axes and changes only the order of the rotations.']),
 ('QC11','calculations','QC10','explanation','같은 두 회전의 순서를 바꾸기',[
  '처음 위를 보는 모형 방향은 영, 영, 일입니다. 공간의 엑스축으로 구십 도, 이어 와이축으로 구십 도 돌리면 영, 마이너스 일, 영이 됩니다.',
  '순서를 바꾸면 일, 영, 영입니다. 각 회전은 같아도 마지막 방향이 다릅니다. 앞에서 검산한 오른손 좌표계와 곱셈 순서를, 비행기의 방향 문제로 다시 읽은 것입니다.'
 ],['Start with the upward model direction zero, zero, one. A ninety-degree fixed-world x turn followed by a ninety-degree fixed-world y turn gives zero, minus one, zero.','Reversing the order gives one, zero, zero. The individual turns match, but the final directions differ. This connects our verified right-handed convention and product order to an aircraft orientation problem.']),
 ('QC20','calculations','GB02','actual','스페이스 엔지니어스: 현재 방향에서 목표 방향으로',[
  '이번에는 옆으로 누운 부품을 세웁니다. 현재 방향에서 목표 방향으로 바꾸려면 어떤 회전이 필요할까요?'
 ],['This time, turn the sideways component upright. What rotation changes its current orientation into the target orientation?']),
 ('QC21','calculations','18','explanation','같은 축에서 목표까지 남은 회전',[
  '계산용 모형에서 현재 방향을 제트축 삼십 도, 목표를 구십 도로 정하면 남은 회전은 육십 도입니다. 목표 구십 도를 처음부터 다시 더하는 것이 아닙니다.',
  '현재 회전 에이로 만든 자세에 공간 기준의 차이 회전 디를 적용하면 목표 비가 됩니다. 따라서 디는 비 곱하기 에이의 역원입니다. 이 예시는 같은 축의 검산이며, 다른 축에서는 단순히 각도만 빼면 안 됩니다.'
 ],['In the defined same-axis model, the current z rotation is thirty degrees and the target is ninety; the remaining rotation is sixty, not an additional ninety.','Applying the world difference D to the current orientation A yields target B: D A equals B. Thus D equals B times the inverse of A. This same-axis check does not justify subtracting angles across different axes.']),
 ('QC30','calculations','GB05','actual','비시지: 계산 결과가 부품의 방향을 바꿉니다',[
  '비시지의 선택된 대포 방향이 달라집니다. 앞에서 계산한 방향 벡터의 변화도 이렇게 물체에 붙여 읽는 것입니다.'
 ],['The selected Besiege barrel directions change. Read a calculated direction-vector change on its attached object in the same way.']),
 ('QC31','calculations','QC30','explanation','벡터 계산을 보이는 결과로 읽기',[
  '모형의 방향 일, 영, 일을 제트축으로 구십 도 돌린 결과는 영, 일, 일입니다. 옆으로 보는 성분이 바뀌고 위쪽 성분 일은 남습니다.',
  '길이도 둘 다 루트 이입니다. 회전은 방향을 바꾸고 길이는 보존합니다. 비시지의 실제 각도나 내부 구현을 추정한 것이 아니라, 앞의 양쪽 곱셈 결과가 무엇을 바꾸는지 연결한 예시입니다.'
 ],['Turning the model direction one, zero, one by ninety degrees around z gives zero, one, one. Its horizontal component changes while its vertical component remains one.','Both lengths are square root of two: rotation changes direction and preserves length. This explains the preceding two-sided product, without inferring Besiege’s actual angles or implementation.'])
]
scenes=[]
for ident,ep,after,kind,title,ko,en in data:
 assert len(ko)==len(en)
 scenes.append(dict(id=ident,episode=ep,insertAfter=after,kind=kind,title=title,mode=ident,ko=ko,en=en,
  sourceType='actual-footage' if kind=='actual' else 'supplement',sceneSourceModule='quaternion_four_game_v3',
  preservesEveryApprovedV2Scene=True,visual='Independent spatial model or action-led annotated gameplay; reveal in narration order; keep captions at960,970.'))
actual={'QF10':('trailmakers-JvTCVUEc1ZE',665,700),'QC10':('trailmakers-JvTCVUEc1ZE',665,700),
 'QF20':('space-engineers-XvpNC9lkLwQ',172,181),'QC20':('space-engineers-XvpNC9lkLwQ',172,181),
 'QF30':('besiege-uWKEJ92486U',58.8,69.7),'QC30':('besiege-uWKEJ92486U',58.8,69.7)}
for s in scenes:
 if s['id'] not in actual:continue
 ident,lo,hi=actual[s['id']];src=lookup[ident]
 s.update(sourceId=ident,sourceFile=src['sourceFile'],sourceSha256=src['sha256'],maximumSeconds=hi-lo,
  intervals=[[lo,hi]],sourceSegments=[dict(sourceId=ident,sourceFile=src['sourceFile'],sourceSha256=src['sha256'],**{'in':lo,'maxSeconds':hi-lo})])
 s['annotation']=dict(red='observed forward/nose/selected-part direction',blue='observed second body direction',
  teal='separately defined comparison axis; never masquerades as measured world axis',
  tracking='Editable observed landmarks with resets/hides at cuts and occlusions',worldMeasurement=False,
  engineInternalsAsserted=False,movingPixelApproval=False,tracksPrepared=False)
 s['selection']=dict(comparedBeforeNarration=True,record=(R/'candidate-comparison.json').relative_to(ROOT).as_posix(),finalAnnotatedPixels='pending')
 s['externalUploadHold']=ident=='besiege-uWKEJ92486U'
write(R/'additions.json',dict(scenes=scenes,backgroundMusic=False,sourceAudio=False,minimumGames=4,
 fourGamesProvisional=['Riders Republic','Trailmakers','Space Engineers','Besiege'],
 besiegeRequiredDescriptionLinks=required_links,besiegeDescriptionExceptionAuthorized=False,
 original80ScenesPreserved=True,finalPixelsAsrAndPublishingComplete=False))

frozen={};newdirs=[]
for ep in base['episodes']:
 old=ep['slug'];new=ep['newSlug'];P=ROOT/'projects'/new
 if P.exists():raise SystemExit(f'Refuse to reset existing revision: {new}')
 lesson_path=R/'baseline'/old/'production/lesson.json';lesson=read(lesson_path)
 assert read(ROOT/'projects'/old/'production/lesson.json')['scenes']==lesson['scenes']
 frozen[old]=dict(sceneDictionarySha256=sha(lesson_path),sceneIds=ep['sceneIds'])
 added=[s for s in scenes if s['episode'] in new];ids={s['id'] for s in added}
 expanded=copy.deepcopy(lesson['scenes'])
 for s in added:
  at=next(i for i,x in enumerate(expanded) if x['id']==s['insertAfter']);expanded.insert(at+1,copy.deepcopy(s))
 assert [s for s in expanded if s['id'] not in ids]==lesson['scenes']
 lesson.update(slug=new,revisionOf=old,scenes=expanded,crossGameRevision=(R/'additions.json').relative_to(ROOT).as_posix())
 write(P/'production/lesson.json',lesson)
 m=read(R/'baseline'/old/'project.json')
 m['slug']=new;m['revisionOf']=old;m['status']='local-four-game-draft; original delivered episode retained';m['publishReady']=False
 m['paths']={k:v.replace(old,new) if isinstance(v,str) else v for k,v in m['paths'].items()}
 m['paths']['productionBuilder']='production/batches/game-math-part2-teaching-revision/build-quaternion-four-game-v3.py'
 m['paths']['manimProject']='manim/projects/game-math-part2-teaching-revision/quaternion_four_game_v3.py'
 m['delivery']['directory']=f'output/{new}';m['delivery']['collector']=f'node scripts/collect-video-output.cjs {new}';m['delivery']['qa']=f'projects/{new}/production/qa.json'
 m['tts']['outputDir']=m['tts']['outputDir'].replace(old,new);m['tts']['filenameStem']=m['tts']['filenameStem'].replace(old,new)
 m['tts']['renderMode']='preserved-v2-exact-PCM-plus-new-only-shared-batch'
 m['video']['durationSeconds']=None
 for k in ['actualGameplaySeconds','actualExplanationSeconds','actualGameplayShare','finalBodyFrames']:m['editing'][k]=None
 m['editing']['timingStatus']='new-only voice not yet measured; preserve earlier slot sample/frame counts'
 m['editing']['causalFlow']['continuousReview']='pending for new revision'
 m['editing']['openingOverview']['scenes'].append('QF00' if 'foundations' in new else 'QC00');m['editing']['openingOverview']['reviewedBeforeTts']=False
 m['editing']['crossGameExamples']=dict(minimumDistinctGames=4,gamesProvisional=['Riders Republic','Trailmakers','Space Engineers','Besiege'],adoptedMovingPixelCount=None,review='pending',originalGameRetained=True)
 m['editing']['exampleInterleaving']['planningPath']=f'projects/{new}/planning/outline.md';m['editing']['exampleInterleaving']['reviewStatus']='normal-speed source comparison complete; new tracks/pixels pending'
 m['membershipOutro']['appliedToFinal']=False;m['audio']['mixStatus']='new-revision-not-rendered'
 m['publishing'].update(privateUploadComplete=False,fullPublishingSettingsComplete=False,actualVideoId=None,
  availableStudioSettingsSaved=False,replacementBaselineVideoId=ep['actualVideoId'],
  scheduleStatus='existing v2 actual anchor retained; new ID not uploaded or scheduled',
  pendingBesiegeDescriptionException=True,requiredSourceDescriptionLinks=required_links)
 m['approvals']=dict(script='additive bilingual local draft; numerical checks passed; pre-TTS scene/audio planning pending',
  voice='baseline reference/PCM preserved; new audio not synthesized',rights='Besiege condition recorded; user exception pending; other source/game-IP human review pending',pixels='new revision not rendered or reviewed')
 m['finalRender']=dict(status='not-rendered',currentPixelApproval=False,knownIssues=[],openItems=['Resolve Besiege description links or replace it before external upload.','New moving tracks, narration/alignment/captions/full decode/pixels/collection and publishing remain incomplete.','Human whole listening and source/game-IP review remain pending.'])
 m['preservation'].update(baseline=old,approvedV2SceneIds=ep['sceneIds'],baselineMediaChanged=False,
  originalAudioMethod='Copy each v2 timeline scene PCM slice exactly; do not regenerate or crop from the older chapter audio.',
  baselineSnapshot=(R/'baseline.json').relative_to(ROOT).as_posix())
 write(P/'project.json',m)
 for lang in ['ko','en']:
  write(P/f'script/narration.{lang}.json',dict(project=new,language=lang,status='local-additive-draft; old scene dictionaries/order preserved',scenes=[dict(id=s['id'],title=s['title'],lines=s[lang]) for s in expanded]))
 outline=['# 기존 설명을 보존하는 네 게임 비교','',f'이 수정본은 {old}의 모든 장면과 음성을 보존합니다. 새 비공개 업로드와 예약은 아직 없습니다.','', '각 편 목표: 라이더스 리퍼블릭 + 트레일메이커스 + 스페이스 엔지니어스 + 비시지. 비시지는 필수 출처 링크 선택이 미완료이므로 외부 업로드를 보류합니다.','', '강의 비율은 본문 실제40/설명60, BGM/원본 소리 없음, 기존 흰색 Manim/고정 하단 자막을 유지합니다.','', '추가 위치:']
 outline += [f"- {s['insertAfter']} 다음 {s['id']}: {s['title']} ({s['kind']})" for s in added]
 (P/'planning').mkdir(exist_ok=True);(P/'planning/outline.md').write_text('\n'.join(outline)+'\n',encoding='utf8')
 write(P/'sources/candidate-comparison.json',comparison)
 (P/'sources/SOURCES.md').write_text('# 쿼터니언 네 게임 비교\n\n기존 라이더스 리퍼블릭 자료와 권리 기록은 이전 판을 보존합니다. 새 후보의 원본 URL, 선택/제외 구간, 정상속도 비교, 출처 조건은 candidate-comparison.json에 기록했습니다.\n\n화면 선과 모든 수치는 설명용입니다. 게임 세계의 실제 각도 또는 독점 엔진 구현을 측정했다고 주장하지 않습니다.\n\n비시지의 설명란 링크 조건 선택은 미완료이며 새 외부 업로드는 아직 진행하지 않았습니다.\n',encoding='utf8')
 newdirs.append(new)

# Store independently checkable results under the preserved RH/wxyz/Hamilton convention.
def mul(a,b):
 return np.r_[a[0]*b[0]-np.dot(a[1:],b[1:]),a[0]*b[1:]+b[0]*a[1:]+np.cross(a[1:],b[1:])]
def rotate(q,v):return mul(mul(q,np.r_[0.,v]),np.r_[q[0],-q[1:]])[1:]
c=math.sqrt(.5);qx=np.array([c,c,0.,0.]);qy=np.array([c,0.,c,0.]);qz=np.array([c,0.,0.,c])
checks=[]
for name,result,expected in [('x90 wing',rotate(qx,[0,1,0]),[0,0,1]),('x90 nose',rotate(qx,[1,0,0]),[1,0,0]),('z90 then inverse',rotate(np.r_[qz[0],-qz[1:]],rotate(qz,[1,0,0])),[1,0,0]),('fixed x then y',rotate(mul(qy,qx),[0,0,1]),[0,-1,0]),('fixed y then x',rotate(mul(qx,qy),[0,0,1]),[1,0,0]),('two-sided vector',rotate(qz,[1,0,1]),[0,1,1])]:
 assert np.allclose(result,expected,atol=1e-12);checks.append(dict(name=name,result=result.tolist(),expected=expected,passed=True))
qaxis=lambda deg:np.array([math.cos(math.radians(deg/2)),0,0,math.sin(math.radians(deg/2))])
A=qaxis(30);target=qaxis(90);D=mul(target,np.r_[A[0],-A[1:]])
assert np.allclose(D,qaxis(60),atol=1e-12) and np.allclose(mul(D,A),target,atol=1e-12)
checks.append(dict(name='same-axis world difference B*A inverse gives60 and D*A=B',passed=True,D=D.tolist()))
write(R/'numeric-and-preservation-audit.json',dict(recordedAt=datetime.datetime.now().astimezone().isoformat(),original80DictionariesAndOrderExact=True,
 baselineMediaChanged=False,preservation=frozen,contract=read(ROOT/'projects/game-math-quaternion-foundations-v2/production/lesson.json')['contract'],
 checks=checks,measuredGameWorldValues=False,actualEngineImplementationAsserted=False,sourceTracksBeforeTts=False,ttsReady=False))

master=read(ROOT/'projects/game-math-polygons-cross-game-additions-v4/project.json');oldmaster=master['slug']
master.update(slug=MASTER,title='쿼터니언 네 게임 비교 추가 내레이션',status='local-script-preparation',revisionOf='game-math-quaternion-operations')
master['paths']={k:v.replace(oldmaster,MASTER) for k,v in master['paths'].items()}
for k in ['outputDir','filenameStem']:master['tts'][k]=master['tts'][k].replace(oldmaster,MASTER)
master['preservation']['originalScenes']=80;master['contract']=read(ROOT/'projects/game-math-quaternion-foundations-v2/production/lesson.json')['contract']
write(ROOT/f'projects/{MASTER}/project.json',master)
maps=[]
for lang in ['ko','en']:
 write(ROOT/f'projects/{MASTER}/script/narration.{lang}.json',dict(project=MASTER,language=lang,status='new-only; pre-TTS tracking/flow check pending',scenes=[dict(id=f'{i:02}',title=s['title'],lines=s[lang]) for i,s in enumerate(scenes,1)]))
for i,s in enumerate(scenes,1):maps.append(dict(additionId=s['id'],ttsScene=f'{i:02}',episode=s['episode'],sourceType=s['sourceType']))
write(R/'tts-map.json',maps)
queue=read(B/'queue.json');queue['execution'].update(currentSlug='game-math-quaternion-operations',stage='quaternion-four-game-v3-local-bilingual-draft; observed tracks and source-condition choice pending',fourGameDraft=(R/'additions.json').relative_to(ROOT).as_posix(),fullTaskComplete=False);write(B/'queue.json',queue)
print('Two local v3 drafts and14 new bilingual scenes prepared. All80 v2 dictionaries/order remain exact; no GPU/render/upload/schedule launched.',flush=True)
