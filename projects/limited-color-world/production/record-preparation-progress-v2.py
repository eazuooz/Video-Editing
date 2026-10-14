"""Record prepared work and fresh identities, preserving all voice inputs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;P=BASE.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.limited-writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
def identity(pid,created=None):
 try:
  p=psutil.Process(pid)
  if created is not None and abs(p.create_time()-created)>.01:return {'pid':pid,'sameIdentity':False}
  return dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),parent=p.ppid(),sameIdentity=True)
 except psutil.NoSuchProcess:return dict(pid=pid,alive=False,sameIdentity=False)
req=read(BASE/'narration-tts-request-v1.json')
protected=[dict(**x,currentSha256=sha(ROOT/x['path']),matches=sha(ROOT/x['path'])==x['sha256']) for x in req['protectedInputs']]
assert all(x['matches'] for x in protected)
mc=read(BASE/'prepared-independent-mc-v1.json')
assert all(sha(ROOT/x['path'])==x['sha256'] for x in mc['files'])
ts=dict(schemaVersion=1,checkedAt=now(),scope='motion-canvas/tsconfig.limited-color-world.json',
 command=['node','node_modules/typescript/bin/tsc','--project','tsconfig.limited-color-world.json'],
 actualExitCode=0,actualToolObservation='adfe1e',allRepositoryTypescriptApproved=False,
 preparedMc=dict(path=rel(BASE/'prepared-independent-mc-v1.json'),sha256=sha(BASE/'prepared-independent-mc-v1.json')),
 actualRenderCreated=False,pixelReviewApproved=False,measuredTimingApproved=False)
assert not (BASE/'scoped-typescript-verification-v1.json').exists();save(BASE/'scoped-typescript-verification-v1.json',ts)
causal=read(P/'planning/causal-chain-additions-v1.json')
assert len(causal['sceneChain'])==8 and len(causal['preparedAdditions'])==3
review=dict(schemaVersion=1,reviewedAt=now(),plan=rel(P/'planning/causal-chain-additions-v1.json'),sha256=sha(P/'planning/causal-chain-additions-v1.json'),
 whole8SceneKoEnOriginalTextDirectlyRead=True,all3PairedBridgeParagraphsDirectlyRead=True,
 original24ParagraphsAndOrderPreserved=True,retainedVoiceRequestUnchanged=True,additiveOnly=True,
 reviews=[dict(id=b['id'],bothLanguagesRead=True,before=b['before'],reason=b['reason']) for b in causal['preparedAdditions']],
 bridgeContentPrepared=True,bridgeVoiceRequested=False,bridgePcmCreated=False,finalCausalFlowApproved=False,
 nextAction='Retain current8scene voice measurement. After actual completion/restoration and full current-hash ASR review, prepare a serialized3bridge request with protected original PCM. Render and review narrated transitions continuously before final flow approval.')
assert not (BASE/'causal-bridge-paired-direct-review-v1.json').exists();save(BASE/'causal-bridge-paired-direct-review-v1.json',review)
from PIL import Image
thumb=P/'publishing/thumbnail-upload-v1.jpg';original=P/'publishing/thumbnail-v1.png'
with Image.open(thumb) as im:size=list(im.size);mode=im.mode
assert size==[1672,941] and thumb.stat().st_size<2_000_000
tr=dict(schemaVersion=1,reviewedAt=now(),generationTool='built-in image_gen',generationObservation='exec-1a588f74-fb54-477d-b86c-2888eddef19e',
 original=dict(path=rel(original),sha256=sha(original),bytes=original.stat().st_size),
 delivery=dict(path=rel(thumb),sha256=sha(thumb),bytes=thumb.stat().st_size,size=size,mode=mode),
 serialization='Single FFmpeg JPEG encoding, original pixels/dimensions/composition unchanged geometrically; original PNG retained. Generated source image retained under CODEX_HOME.',
 directFullGeneratedImageRead=True,directSerializedDeliveryRead=True,
 observations=['Exact header 얌얌코딩 | 게임 기획·디자인 is legible.','Exact headline 색이 달라도 / 읽히는 게임 uses large black/red Korean type on white.','Natural calico cat with scarf leaps along dimensional platform tops toward a bright doorway.','Colored landscape becomes monochrome while dark edges, roof pattern, platform height/top surfaces and direction signs remain readable.','Yellow header and illustrated narrative are preserved; no video inset, player, PPT cards, medical claims or pasted screenshot.','The illustration is original and is not evidence of a specific Chicory route or color-accessibility result.'],
 preparedVisualApproved=True,savedPlatformThumbnail=False,fullSettingsVerified=False,actualVideoId=None,
 registryAdded=False,gitAdded=False,localOnlyUntilReviewedDelivery=True)
assert not (P/'publishing/prepared-thumbnail-direct-review-v1.json').exists();save(P/'publishing/prepared-thumbnail-direct-review-v1.json',tr)
session=read(BASE/'narration-tts-session-v1.json');wait=read(BASE/'narration-tts-waiting-v1.json')
own=identity(session['actualPid'],session['createTime']);assert own['sameIdentity']
lease=read(ROOT/'shared/output/GPU_HANDOFF.json') if (ROOT/'shared/output/GPU_HANDOFF.json').exists() else None
foreign=identity(lease['coordinator']['pid'],lease['coordinator']['createTime']) if lease else None
snap=dict(schemaVersion=1,observedAt=now(),actualSingleSession=1912,actualOwnIdentity=own,waitingSnapshot=wait,
 currentForeignLease=lease,actualForeignCoordinator=foreign,currentHostAvailableBytes=psutil.virtual_memory().available,
 protectedInputs=protected,all10ProtectedInputsMatched=True,
 ownExecutionStateCreated=(BASE/'narration-tts-execution-v1.json').exists(),ownPcmCount=sum((ROOT/x['path']).exists() for x in req['scenes']),
 researchControlsOrProcessesModified=0,ownResearchResumeClaim=False,
 preparedIndependentScenes=8,scopedTypescriptActualExitCode=0,structuralRenderStarted=False,structuralPixelApproved=False,
 causalBridgeParagraphsPrepared=3,causalBridgeVoiceStarted=False,finalCausalFlowApproved=False,
 thumbnailPreparedAndDirectlyReviewed=True,savedPlatformThumbnail=False,
 nextAction='Reuse active1912. Wait for foreign handoff closure/restoration and >=8GB host availability. Then observe own approved8scene TTS/actual outer exit/original research resume; directly review whole8 plus complete ASR contexts. Preserve24 paragraphs/PCM and add3 reviewed causal bridges with a later single request. Additional unique source actions and all final timed animation/60:40/mix/pixels/QA/collection/publishing remain pending.')
assert not (BASE/'prepared-handoff-resource-verification-v2.json').exists();save(BASE/'prepared-handoff-resource-verification-v2.json',snap)
cp=read(BASE/'latest-checkpoint.json')
# Do not overwrite a state advanced by the actual voice worker during this read.
assert not snap['ownExecutionStateCreated'] and snap['ownPcmCount']==0
cp.update(recordedAt=now(),stage='single-request-waiting-foreign-handoff-with-MC-and-additive-bridges-prepared',
 motionCanvasCreated=True,prototypeStructuralPixelReviewApproved=False,preparedIndependentScenes=8,
 measuredNarrationTimed=False,continuousWholeAnimation=False,causalBridgeParagraphsPrepared=3,bridgeTtsStarted=False,
 finalCausalFlowApproved=False,thumbnailPrepared=True,savedPlatformThumbnail=False,
 preparationVerification=rel(BASE/'prepared-handoff-resource-verification-v2.json'),nextAction=snap['nextAction'])
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';raw=qp.read_bytes();q=json.loads(raw)
foreignItems=json.dumps([i for i in q['items'] if i['slug']!='limited-color-world'],ensure_ascii=False,sort_keys=True)
i=next(i for i in q['items'] if i['slug']=='limited-color-world')
i.update(stage=cp['stage'],updatedAt=now(),nextAction=cp['nextAction'],preparedIndependentScenes=8,preparedCausalBridges=3,
 preparationVerification=cp['preparationVerification'],thumbnailPrepared=True,savedPlatformThumbnail=False)
# Preparation is not the scene-render checkpoint.
assert i['checkpoints']['scenes'] is False and i['checkpoints']['narration'] is False
q['updatedAt']=q['lastProgressAt']=now()
assert qp.read_bytes()==raw and foreignItems==json.dumps([i for i in q['items'] if i['slug']!='limited-color-world'],ensure_ascii=False,sort_keys=True)
save(qp,q)
print('Prepared8 independent scenes/scopedTS0/3 reviewed bridges/thumbnail; actual1912 waiting and10protected inputs preserved. Model/PCM/render/ownresearchcontrols/Git0.')
