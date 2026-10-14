"""Correct only a new guide's onset order, preserving the original111 body paragraphs."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
def write(p,x):
    if p.exists():raise RuntimeError('Preserve existing '+str(p))
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
guide=read(ROOT/'projects/game-lighting-history-04/script/physical-part3-guided-actions.koen.v69.json')
old=next(x for x in guide['scenes'] if x['id']=='capture-target-view')
pair=copy.deepcopy(old)
pair['ranges']=[[48,67]]
pair['ko']='먼저 선택한 이벤트의 출력부터 구별하겠습니다. 명령 목록의 화면 지우기와 그리기는 다른 역할입니다. 드로 인스턴스드를 선택하면 파란 배경 위에 색이 섞인 삼각형이 보입니다. 이제 이 결과에서 메시의 꼭짓점과 셰이더 입력으로 질문을 옮겨 보겠습니다.'
pair['en']='First distinguish the selected event’s output. Clearing the image and drawing it have different roles in the command list. Selecting DrawInstanced reveals a colored triangle on the blue background. We now move the question from that result to mesh vertices and shader inputs.'
pair['focus']='Identify the event/output before DrawInstanced appears near57.8; move to mesh and shader input after the output. No vertex-return as final pixel-color claim.'
source=guide['sources']['capture']
if sha(ROOT/source['path'])!=source['sha256']:raise RuntimeError('Native source changed')
evidence=BASE/'native-source-followup-review-v127.json'
write(evidence,dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),ui='CUA browser4/tab50; normal-rate player v123',source=source,
    observations=[dict(id='grade-channel-controls',normalSpeedRun=[1855,1872.5],endObserved=1872.525,middleObserved=1865,observed='Contrast RGB controls1.01 at1865; unequal channels at1872.525. Selected Film3 volume and the same cube arrangement remain visible.'),
    dict(id='grade-shared-reference',normalSpeedRun=[1872.5,1890.3],endObserved=1890.340,observed='Camera shifts; reacquire the same face rather than holding an untracked screen-space mark. Tonemapper and MobileTonemapper fields become visible.'),
    dict(id='grade-to-lookup',normalSpeedRun=[1890.3,1911],endObserved=1911.133,observed='MobileTonemapper Tint/contrast/saturation values and camera distance change; no isolated light-object edit.'),
    dict(id='capture-target-view',normalSpeedRun=[48,67],endObserved=67.142,triangleDirectlyObserved=57.8,observed='48 selects CloseCommandList with black output;57.8 selectsEID14 DrawInstanced with blue/colored triangle;67 shows IA POSITION/COLOR input layout. Old first sentence preceded the draw selection, so revise this newly added guide only.'),
    dict(id='capture-position-input',normalSpeedRun=[67,89.8],endObserved=89.854,middleObserved=76.6,observed='IA input layout, mesh POSITION values and triangle, then VS debugging source with distinct POSITION/COLOR fields. No evidence that this tiny sample implements game lighting.'),
    dict(id='capture-stage-selection',normalSpeedRun=[89.8,109.52],endObserved=109.544,middleObserved=95.2,observed='VSMain returns VSOutput, then color output inspection. Do not label the VS return as a pixel shader final color. Reserved original109.52–125 and125–132.5 remain excluded from additions.')],
    focusOrdinaryLater=dict(range=[2470,2486.2],observedFramesAt=[2470,2480.5,2486.387],ordinaryDisplay=True,sameConditionAsEarlierDiagnostic=False,label='뒤의 일반 화면 · 다른 설정/카메라'),
    focusErrorDiagnostic=dict(range=[2380.1,2397.633333333],endObserved=2397.895,label='앞선 진단 화면 · 별도 조건',reconstructionFailureProved=False),
    revision=dict(id=old['id'],before=old['ko'],after=pair['ko'],en=pair['en'],preservedClaims=['selected event output','clear and draw have different roles','DrawInstanced triangle','move from output to mesh vertices and shader inputs'],original111NarrationChanged=False,oldAddedTakePreserved=True),
    exactMovingAnnotationsApproved=False,finalTimingApproved=False,bodyRatioApproved=False,allFinalPixelsReviewed=False,uploaded=False,newImages=0))
script=ROOT/'projects/game-lighting-history-04/script/native-onset.koen.v128.json';write(script,dict(schemaVersion=1,sourceReview=ref(evidence),scenes=[pair]))
for lang in ['ko','en']:
    p=ROOT/f'projects/game-lighting-history-04/script/native-onset.{lang}.v128.json'
    write(p,dict(title='Observed command/output onset correction',scenes=[dict(id=pair['id'],title=pair['id'],lines=[pair[lang]],screenRole='actual')]))
manifest=read(BASE/'native-tail-manifest-v126.json')
manifest['status']='prepared-one-new-guide-onset-correction'
manifest['tts'].update(outputDir='shared/output/narration/game-lighting-history-04/qwen3-1.7b-native-onset-v128',filenameStem='game-lighting-history-04-native-onset-v128',maxNewTokensReason='Only the added capture guide; retain every original111 PCM and prior43 takes, unchanged thresholds.')
manifest['paths'].update(script='projects/game-lighting-history-04/script/native-onset.ko.v128.json',scriptEn='projects/game-lighting-history-04/script/native-onset.en.v128.json')
stem=manifest['tts']['outputDir']+'/'+manifest['tts']['filenameStem']
for key,suffix in [('narration','.wav'),('captionsKo','.srt'),('captionsEn','.en.srt')]:manifest['paths'][key]=stem+suffix
mp=BASE/'native-onset-manifest-v128.json';write(mp,manifest)
request=read(BASE/'native-tail-request-v126.json')
selected=read(BASE/'native-followup-selected-v126.json')
request.update(preparedAt=datetime.now(timezone.utc).isoformat(),manifestOverride=mp.relative_to(ROOT).as_posix(),script=ref(script),sourceReview=ref(evidence),scenes=[dict(id=pair['id'],path=manifest['tts']['outputDir']+'/chunks/capture-target-view-scene.wav',kind='added-guide-native-onset-correction')])
request['protectedInputs'] += [ref(mp),ref(BASE/'native-followup-selected-v126.json'),ref(BASE/'native-tail-execution-v126.json'),ref(ROOT/manifest['paths']['script']),ref(ROOT/manifest['paths']['scriptEn'])]
request['existingSelectedTakeFiles'] += [dict(path=r['path'],sha256=r['sha256']) for r in selected['results']]
write(BASE/'native-onset-request-v128.json',request)
worker=(ROOT/'production/research/game-lighting-history/render-native-tail-v126.py').read_text('utf-8')
worker=worker.replace('native-tail-request-v126.json','native-onset-request-v128.json').replace('native-tail-execution-v126.json','native-onset-execution-v128.json').replace("expected={'focus-layers-entry'}","expected={'capture-target-view'}")
target=ROOT/'production/research/game-lighting-history/render-native-onset-v128.py'
if target.exists():raise RuntimeError('Preserve existing worker')
compile(worker,str(target),'exec');target.write_text(worker,'utf-8')
print(json.dumps(dict(prepared=True,original111Changed=False,newGuideChanges=1,newImages=0,rendered=False)))
