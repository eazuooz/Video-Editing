"""Prepare eight independent additive guides; leave measured/final approval pending."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
MC=ROOT/'motion-canvas/src/projects/familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+f'.{os.getpid()}.writing')
    t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)

dest=BASE/'observation-guide-tts-request-v1.json';assert not dest.exists()
framing=read(PROOF/'source-framing-direct-review-v1.json')
assert framing['all30BoardsDirectlyRead'] and framing['all180SourceSamplesDirectlyRead']
bank=read(PROOF/'source-action-bank-v4.json');assert bank['clipCount']==60 and bank['allEdgesDirectlyRead']
measurement=read(BASE/'current-narration-measurement-v1.json')
assert len(measurement['measurements'])==11 and measurement['explanationSpeechSeconds']==147.2
entries=[
 ('12','02',2,'문 앞의 대상과 계단 위의 대상',
  '분홍색 문 앞의 대상을 겨눕니다. 다음 계단 컷에서는 높은 쪽으로 화면을 돌리죠. 대상의 높이와 방향 잡기를 함께 따라가 보세요.',
  'The player aims at a target by the pink door. The next stairway shot turns the view upward. Follow the target’s height and the change in direction together.',
  ['additional-01','additional-02','additional-03'],
  'Separate pink-door/brain-hall and escalator excerpts. Centre targets and upper direction, not exact keys, learning time or optimal play.'),
 ('13','04',2,'문을 차기와 방 안에서 겨누기',
  '문을 발로 차고, 다른 방에서는 총을 겨눕니다. 대상을 향해도 실행하는 행동은 다르죠. 새 발차기와 방향 잡기의 연결을 나누어 보세요.',
  'The player kicks a door, then aims in another room. Facing a target can lead to different actions. Examine how the new kick connects to establishing a direction.',
  ['additional-09','additional-10','additional-11','additional-13','additional-04','additional-05','additional-06','additional-07'],
  'Escalator/metal-door kick, crossbow/upward kick and separate room firing excerpts. Editorial sequence, not a continuous encounter or input sequence.'),
 ('14','06',1,'지상 이동과 공중 우산',
  '시장에서 총을 쏘는 컷과 우산을 펴고 줄 근처를 지나는 컷을 보세요. 몸의 이동과 도구의 상태는 함께 바뀌죠. 같은 도구가 여러 행동에 쓰입니다.',
  'Compare firing at the market with opening the umbrella near a wire in a separate shot. The body moves while the tool changes state. The same tool appears in several actions.',
  ['additional-16','additional-17'],
  'City market ground attack, forest-wire umbrella and laundry roof. Ground body is currently mask-conflicted; exact cues/source recomposition must resolve before final use. No binding/parry immunity claim.'),
 ('15','06',2,'서로 다른 높이의 공격 방향',
  '기찻길과 시장, 늪과 컨테이너 전투는 별도 구간입니다. 몸이 있는 높이와 총의 방향을 나누어 보세요. 도구 사용과 방향 선택을 함께 점검합니다.',
  'The rail, market, swamp and container fights are separate intervals. Compare the body’s height with the gun’s direction. Examine tool use together with direction selection.',
  ['additional-22','additional-25'],
  'Separate rail/mech, circular market machine, rainy roof, swamp and container excerpts. Rail/market ground body mask-conflicted; preserve right-edge descending player. No causality or universal blocking assertion.'),
 ('16','08',1,'객차 안에서 높이가 다른 대상',
  '이번에는 다른 기차 구간입니다. 객차 안을 지나면서 바닥 쪽 상대를 겨누다가 상자 위의 상대를 향하죠. 몸이 지나가는 길과 목표의 높이를 따로 따라가 보세요.',
  'Here is a different train interval. While traversing the carriage, the player aims at an opponent near the floor and then at one on a crate. Follow the body’s route separately from the target’s height.',
  ['hype-01','hype-02'],
  'Hype9–21 native train interior and crate heights, distinct from old YIV train/mech. Body and target directions visible above stress mask; exact final cues still pending.'),
 ('17','08',3,'공중에서 갈라지는 두 총',
  '뛰어오른 순간에는 두 총이 서로 반대쪽을 향합니다. 몸의 이동 방향 하나로 두 대상을 고르는 문제를 대신할 수는 없죠. 이동과 목표 선택을 따로 설계할 이유입니다.',
  'During the jump the two guns point in opposite directions. One movement direction cannot stand in for selecting both targets. This illustrates why movement and target selection need separate design.',
  ['hype-03','hype-04'],
  'Hype21–33 airborne opposite guns and next-car/crate heights. Inspect explicit24.5 opposite-gun moment in actual final cues. No claim of two mice/buttons or supported device.'),
 ('18','10',3,'지붕 위 이동과 아래쪽 목표',
  '지붕 위로 움직이는 동안 총은 아래를 향합니다. 몸의 위치만 따라가면 아래쪽 목표를 놓칠 수 있죠. 이동 경로와 총이 향하는 쪽을 각각 확인해 보세요.',
  'The gun points downward as the body moves above the roof. Following the body alone can miss the lower target. Check the traversal route and the gun’s direction separately.',
  ['hype-05','hype-06'],
  'Hype33–45 crate/roof motion and downward air shots before spin. Low target feet stress conflict remains; do not call every target unobstructed.'),
 ('19','10',4,'지붕에서 객차 안으로 바뀌는 경로',
  '회전하며 뛰던 몸이 지붕으로 돌아왔다가 객차 안으로 내려갑니다. 총이 향하는 대상도 바뀌죠. 새로운 길에서도 이동과 목표 선택의 연결이 이어지는지 점검합니다.',
  'After a spinning jump the body returns to the roof and descends into the carriage. The guns change targets. Check whether movement and target selection remain connected on a new route.',
  ['hype-07','hype-08'],
  'Hype45–54.5 spin/roof/descend/shoot route. Native camera tilt preserved, no reuse/loop/artificial slowdown; lowest target feet still need final cue inspection.')
]
guides=[]
for gid,parent,p,title,ko,en,ids,connection in entries:
    cuts=[next(x for x in bank['clips'] if x['id']==i) for i in ids]
    guides.append(dict(id=gid,parentScene=parent,afterOriginalParagraph=p,title=title,ko=ko,en=en,text=ko,
        path=f'shared/output/narration/familiar-game-rules/observation-guides-v1/{gid}.wav',classification='actual-existing-game',
        bankCutIds=ids,sourceIntervals=[{k:x[k] for k in ['id','sourceVideoId','sourcePath','sourceSha256','inFrameInclusive','outFrameExclusive','inSeconds','outSeconds','seconds']} for x in cuts],
        visibleActionAndConnection=connection,sourceEvidence=rel(PROOF/'source-framing-direct-review-v1.json'),
        measuredSeconds=None,finalWordActionAlignment=False,framingApproved=False))
request=dict(schemaVersion=1,slug='familiar-game-rules',preparedAt=now(),guides=guides,pairedWholeTextReview=False,overviewPromiseReview=False,
    baselineScenes=11,baselineParagraphs=46,baselinePcmSeconds=296.72,baselineActualPcmSeconds=149.52,
    originalExplanationSeconds=147.2,overviewSeconds=24.32,allPriorScenePcmPreserved=True,device='cpu',cpuThreads=2,gpuJobs=0,
    currentCanonicalScriptsUnchangedUntilMeasuredAdoption=True,finalTimingApproved=False,newGuidesTechnicalAsrApproved=False,
    humanWholeListening='pending',humanPronunciation='pending',sameApprovedModelAndReference=True,NimbusUnchanged=True,
    newGitImages=0,sourceAudioStreams=0,selfCreatedGames=0,loops=0,slowdown=0,
    sourceBank=rel(PROOF/'source-action-bank-v4.json'),sourceBankSha256=sha(PROOF/'source-action-bank-v4.json'),
    originalPcmMeasurements=measurement['measurements'],protectedInputs=[])
save(dest,request);save(BASE.parent/'planning/observation-guides-v1.json',request)
for language in ['ko','en']:
    save(BASE.parent/f'script/observation-guides.{language}.json',dict(schemaVersion=1,slug='familiar-game-rules',baselineScriptPreserved=True,
        scenes=[dict(id=g['id'],parentScene=g['parentScene'],afterOriginalParagraph=g['afterOriginalParagraph'],title=g['title'],lines=[g[language]],role=g['classification']) for g in guides]))
plan=dict(schemaVersion=1,slug='familiar-game-rules',finalTimingApproved=False,allSourceSegmentPixelsReviewed=False,allFinalCaptionPixelsReviewed=False,
          guides=[dict(id=g['id'],parentScene=g['parentScene'],title=g['title'],role=g['classification'],durationFrames=0,segments=[],sourceActionIds=g['bankCutIds']) for g in guides])
save(MC/'guide-scene-plan.json',plan)
for g in guides:
    p=MC/'scenes'/('scene'+g['id']+'.tsx');assert not p.exists()
    p.write_text("import {observationGuideScene} from '../guide-scene-factory';\nexport default observationGuideScene('"+g['id']+"');\n",encoding='utf-8')
outline=BASE.parent/'planning/outline.md';original=outline.read_text('utf-8')
assert '## 추가 관찰 해설 v1' not in original
addition='\n## 추가 관찰 해설 v1\n\n기존11장46문단과296.72초 PCM, 여섯 흰 설명147.2초, 전체도입24.32초를 그대로 보존한다. 확보하고 직접 본 새 공식 행동을 안내하는 독립KOEN8문단을 실제 사례 장 안에 삽입한다. 원래결론11은 마지막에 남긴다. 원본11 PCM은 재생성하지 않는다.\n\n'
addition+='순서는 Anger Foot02+12→03→04+13→05→Gunbrella06+14/15→07→Pedro08+16/17→09→10+18/19→11이다. 새 관찰은 도입이 약속한 동일3사례와 기능 구별을 구체화하며 새로운 게임의 입력설정이나 지원장치를 입증한다고 주장하지 않는다. 개별 삽입 위치는 각 JSON의 afterOriginalParagraph에 있다.\n\n'
addition+='233.467초는 고유소스 용량이며 최종 비율 승인이 아니다. TTS실측 이후 자연스러운 무음, 모든PCM보존, 정수프레임과 실제cue/shot배치를 함께 맞춘다. 전체30스트레스판180표본을 직접 읽었지만 하단인물·목표물 충돌이 남았으므로 final framing/caption gate는false다. 자막 중심960,970을 고정하고 실제짧은큐·원본재구성·구간재배정을 검수한다.\n\n'
for g in guides:addition+=f"### {g['id']} {g['title']} — {g['parentScene']}장 원래{g['afterOriginalParagraph']}문단 뒤\n\n{g['ko']}\n\n{g['en']}\n\n관찰: {g['visibleActionAndConnection']}\n\n"
outline.write_text(original+addition,encoding='utf-8')
qpath=PROOF.parent/'queue.json';q=read(qpath);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
item.update(stage='independent8-observation-guides-prepared-awaiting-whole-text-review',updatedAt=now(),
 observationGuides=dict(request=rel(dest),guides=8,measured=False,pairedWholeTextReview=False,technicalAsrApproved=False),
 nextAction='Directly read all8independent KOEN guide texts with original11/full conclusion and opening promise, then currentdistinct/resource gates and only newguide CPU2 synthesis; original11PCM/147.2white preserved.')
q['updatedAt']=now();save(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','observationGuides','nextAction']:d[k]=item[k]
    save(p,d)
print(json.dumps(dict(guides=[{'id':g['id'],'characters':len(g['ko']),'estimatedSecondsAt8_5CharsPerSecond':round(len(g['ko'])/8.5,2)} for g in guides],originalPcmSecondsPreserved=296.72,allFinalApproval=False),ensure_ascii=False))
