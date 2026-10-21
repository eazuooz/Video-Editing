"""Prepare V8 source-plan metadata and a few unchanged inspected exact stills.

No source video decode, capture, audio generation or encoding is performed.
The final compositor reads the existing genuine1080p original directly.
"""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image

H=Path(__file__).resolve().parent; R=H.parents[3]
P=R/'projects/game-math-euler-axis-angle'; G=P/'production/local/revision-v8-orientation-matrix/game'
V7=P/'production/revision-v7-part1'; L7=P/'production/local/revision-v7-part1'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
script=P/'script/revision-v8-orientation-matrix/narration.ko.json'
auth=read(H/'authorization.json'); assert auth['fullProductionAuthorized'] and sha(script)==auth['approvedScriptSha256']
G.mkdir(parents=True,exist_ok=True); (G/'stills').mkdir(exist_ok=True)
old=read(V7/'game-inputs.json'); source=old['sources']['totk']
container=read(L7/'gameplay/source-container-metadata.json')['totk']
origin=R/source['sourcePath']; signature=container['inputSignature']
assert origin.stat().st_size==signature['bytes'] and origin.stat().st_mtime_ns==signature['mtimeNs']
assert signature['sourceSha256']==source['sourceSha256']
assert container['dimensions']==[1920,1080] and container['fps']==60
stills=[]
for sid,t,meaning in [('ground',998.75,'통나무 옆에 누운 돛'),('held-flat',1000.,'울트라핸드로 들었지만 누운 돛'),('held-high-flat',1002.75,'위치가 높아져도 아직 누운 돛'),('upright',1006.5,'회전 UI와 세운 돛 전체가 보이는 결과')]:
    src=P/f'production/local/revision-v7-script/totk/native-{t:08.3f}.png'
    dst=G/'stills'/f'{sid}.png'
    if dst.exists():assert sha(dst)==sha(src),'Do not overwrite a differing still'
    else:shutil.copy2(src,dst)
    assert Image.open(dst).size==(1920,1080)
    stills.append(dict(id=sid,file=rel(dst),sha256=sha(dst),sourceFile=source['sourcePath'],sourceSha256=source['sourceSha256'],sourceFrame=round(t*60),sourceSeconds=t,
        meaning=meaning,classification='gameplay-derived-analysis',audio=False,countsAs='explanation',copiedExactPixelsAndPngBytes=True))
endpoint=G/'held-translate-end.json'
if endpoint.exists():
    exact=read(endpoint);assert exact['sourceFrame']==60195 and sha(R/exact['file'])==exact['sha256']
    stills.append(dict(id='held-translate-end',file=exact['file'],sha256=exact['sha256'],sourceFile=source['sourcePath'],sourceSha256=source['sourceSha256'],
        sourceFrame=60195,sourceSeconds=1003.25,meaning='이동 끝/회전 시작의 정확한 경계 프레임; 아직 누운 돛',classification='gameplay-derived-analysis',audio=False,countsAs='explanation',endpointReceipt=rel(endpoint)))
paragraphs=read(script)['scenes'][0]['paragraphs']; text=paragraphs[1]
def cue(literal):
    a=text.index(literal);return dict(scene='m01',paragraph=2,paragraphId='m01.L02',literal=literal,sourceKoOffset=a,sourceKoEnd=a+len(literal),binding='actual source speech/ASR character clock; no proportional guessed seconds')
clips=[dict(id='totk-translate',sceneId='m01',paragraphId='m01.L02',sourceId='totk',sourceStartFrame=59925,sourceEndFrameExclusive=60195,sourceStartSeconds=998.75,sourceEndSecondsExclusive=1003.25,frames=270,seconds=4.5,
    cue=cue('울트라핸드'),cueAdjustment=dict(previousLiteral='잡아서 옮기고',reason='Start the complete native selection/lift/move example at the spoken ability name. First actual V8 speech clock leaves only3.8s from grab/move to the later orientation cue, so the4.5s source would overlap. Earlier ability context preserves before/action/result without speed, PCM or source changes.',binding='Recompute exact output frames from current Clock when edit-plan is built'),stateBefore='바닥에 누운 돛',action='선택해 들어 올리고 위치를 옮김',stateAfter='위치/카메라가 변했지만 넓은 돛천이 아직 누워 있음',
    allowedClaim='물체를 옮기는 것과 세우는 것은 구분된다. 실제3D중심/회전량 고정은 주장하지 않음',rightProperty='position-versus-orientation, controlled independent illustration',postClipStill='held-translate-end' if endpoint.exists() else 'held-high-flat'),
    dict(id='totk-rotate',sceneId='m01',paragraphId='m01.L02',sourceId='totk',sourceStartFrame=60195,sourceEndFrameExclusive=60390,sourceStartSeconds=1003.25,sourceEndSecondsExclusive=1006.5,frames=195,seconds=3.25,
    cue=cue('어떤 기울기로'),stateBefore='높이 들어 올렸지만 아직 누운 돛',action='회전 조작 UI가 나타나고 돛이 세워짐',stateAfter='세워진 돛 전체를 확인',
    allowedClaim='관찰되는 누운 상태/선 상태의 차이와 별도 회전 입력; 정확90도·같은중심·같은앞축·내부Euler/행렬은 주장하지 않음',rightProperty='orientation change of authored object, not Nintendo engine telemetry',postClipStill='upright')]
for row in clips:row.update(file=source['sourcePath'],sourceSha256=source['sourceSha256'],sourceTotalFrames=103252,sourceDimensions=[1920,1080],fps=60,nativeSpeed=1,loop=False,classification='independent-gameplay',sourceAudioAllowed=True,sourceAudio='synchronized original44100stereo AAC; standard profile; no addedBGM',status='confirmed finite source interval; actual output timing not yet bound')
oldkeys=read(L7/'gameplay/guide-keys.json')['streams']['totk']
keys=[x for x in oldkeys if 59925<=x['sourceFrame']<=60390]
for key in keys:
    for mark in key['guides']:mark['label']='돛천의 놓인 모양'
    key['review']='Reuse manually inspected native source-space anchor. Exact images at998.75/1000/1002.75/1003.5/1004/1006.5 and temporal1003.25/1004.5 re-viewed for V8; no new3Daxis recovery.'
annotations=dict(coordinateSpace='normalized source screen1920x1080',kind='editorial attention guides; not game telemetry',role='focus',
    preferredShape='small thick hollow open bracket around visible cloth, never a filled region or fake3Drotation ring',
    sourceCutRule='Clear all prior guide state at each source cut; do not bridge a frozen/live cut with old source coordinates',
    motionRule='Interpolate only adjacent confirmed visible anchors; output continuous60fps move, not10Hz holds. No interpolation across explicit hidden keys.',
    axisConvention='Only original game rotation UI on the left; X/Y/Z axes and chosen positive angle belong to the right authored illustration.',
    protect=['top-left hearts/ability UI','bottom rotation/move controls','bottom-right minimap','visible sail texture','fixed captions outside pane'],keys=keys,
    mandatoryHide=[dict(sourceStartFrame=60210,sourceEndFrameExclusive=60270,reason='Cloth partly outside top; cyan tether is not mast. Original rotation UI remains visible.')],
    pending='Current paired1080 and375px moving review after actual word binding; previous source and V7 output evidence are reusable, not V8 moving approval.')
plan=dict(schemaVersion=1,revision='orientation-matrix-v8',sourceScope='8.1–8.2.5',script=rel(script),scriptSha256=sha(script),source=source,sourceContainer=container,
    sourceContentIdentity='Reuse V7 verified hash/probe/selected exact frames; same local size/mtime checked. No network download, full-source re-decode or newly granted rights claimed.',
    selectedGameCount=1,fourGameQuotaInherited=False,sourceNativeFrames=465,sourceNativeSeconds=7.75,
    playback='direct original source at1x; root compositor scales with aspect preserved; original audio extracted at exact matching in/out',
    clips=clips,stills=stills,annotations=annotations,
    opening=dict(scene='m01',paragraph=1,choice='Authored aircraft and arrow hero',reason='Same forward direction with changed bank is verified only in our controlled illustration, not this moving-camera sail recording.'),
    actualParagraph=dict(scene='m01',paragraph=2,preLiveStill='ground',afterTranslation='held-translate-end' if endpoint.exists() else 'held-high-flat',afterRotation='upright',
        boundary='Keep game left and matching explanation right while teaching the actual move/rotate example. Continue narration during native action and optional analysis still; no added observation silence.',
        fallback='If actual voice window cannot contain both finite ranges at1x, report word/action mismatch to root. Never silently trim before/result, overlap unrelated sentences, stretch voice or loop game.'),
    recap=dict(scene='m13',paragraph=1,proposal='Optional exact upright analysis still only for first sentence 이제 처음의 물체로 돌아가 보겠습니다; label 실제 화면 분석.',
        returnToModelAt='앞쪽이 같은 곳을 향해도',reason='Same forward plus changed up is not established for the sail. Do not use its unknown internal axes as proof of the matrix. No replayed native clip is needed.',
        repeatedStillPurpose='Recall the opening object for continuity; counts as explanation, never additional native gameplay.'),
    forbiddenClaims=['game stores orientation as this3×3row matrix','reconstructed hidden world/localaxes','fixed3Dcenter from screen point','exact90degree native step','green/cyan tether is mast','same forward axis proved by this sail footage'],
    currentReview=dict(exactSourceFramesDirectlyViewed=[59925,60000,60165,60210,60240,60390],
        temporalSourceSamplesDirectlyViewed=[60195,60270],temporalCadence='Existing384x216 quarter-second source evidence, nominal sample time; not first-input-frame measurement.',
        priorExactBoundaryEvidence=rel(L7/'gameplay/raft-lift-rotation-boundary-review.json'),
        priorMovingEvidence=rel(L7/'qa/final-left-visual-review.json'),
        sourceSound='Original source audio/provenance retained; V8 final mix/listening not yet performed.',
        currentV8OutputExists=False,currentV8MovingApproval=False))
save(H/'game-inputs.json',plan)
save(H/'game-cut-plan.json',dict(schemaVersion=1,scriptSha256=sha(script),clips=clips,stills=stills,annotations=annotations,recap=plan['recap'],status='source intervals confirmed; awaiting actual word clock; no game render needed'))
save(G/'preparation-receipt.json',dict(schemaVersion=1,preparedStills=len(stills),files=stills,sourceVideoDecoded=False,sourceMediaEncoded=False,sourceSignatureChecked=True,sourceDataReusedByHash=True,
    plan=rel(H/'game-inputs.json'),planSha256=sha(H/'game-inputs.json'),auth=rel(H/'authorization.json'),authSha256=sha(H/'authorization.json')))
print(json.dumps(dict(plan=rel(H/'game-inputs.json'),clips=len(clips),nativeSeconds=7.75,stills=len(stills),sourceDecode=False),ensure_ascii=False))
