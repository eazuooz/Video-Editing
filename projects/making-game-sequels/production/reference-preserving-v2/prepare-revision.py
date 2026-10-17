"""Register only the selected D19 revision; preserve prior deliveries and history."""
from pathlib import Path
import json, datetime
R=Path(__file__).resolve().parents[4]; P=R/'projects/making-game-sequels'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
control=read(R/'shared/publishing/video-production-control.json')
assert control['selectedVideo']==P.name
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
sections=[
 ('00:04–00:27','같은 작품의 반복과 속편의 가치','성공작의 다음 편도 구매 이유가 필요하다. 피크민·그란 투리스모 시리즈의 역할 유지.','01','일률적인 판매량 절반 주장은 검증된 통계가 아니므로 확정 수치로 재현하지 않고 위험의 방향을 설명한다.'),
 ('00:28–01:11','기반 시스템과 제작 도구','영화의 새 장면 제작과 게임의 시스템/도구/콘텐츠를 비교하고, 재사용 가능한 기반과 새 콘텐츠를 분리한다.','02–03','코드·데이터·도구의 관계와 작은 가상 작업량 예제를 해당 위치에 추가. 실제 게임의 내부 구현을 추정한 구조도로 제시하지 않는다.'),
 ('01:12–01:44','재미의 불확실성과 검증','줄거리만으로 조작의 재미를 확정할 수 없다. 동작하는 시제품과 검증된 기반이 제작 위험을 줄인다. 신규 기획에는 취소될 위험도 있다.','04','플레이테스트(Playtest) 정의와 동일 장면의 조작→피드백 설명을 추가. 취소 확률 수치 없음.'),
 ('01:45–02:01','스매시브라더스의 제작 연속성','이전 시리즈의 팀 변경/기반 재구축과 for Wii U/3DS→Ultimate의 개발 연속성.','05','개인 경험은 내부 귀속에만 보존. 개발사 공식 제품 실적으로 교차 확인. 재사용 코드 비율을 발명하지 않음.'),
 ('02:02–02:40','기대와 실제 경험','첫 구매는 기대에 영향을 받고, 플레이 후의 만족/중단 경험이 다음 구매 의사에 영향을 준다.','06','기대→플레이→기억→다음 선택 흐름. 구매자 수치가 필요하면 가정임을 표시; 판매 예측 금지.'),
 ('02:41–02:59','같은 것과 더 원하는 것','전편을 좋아해도 비슷한 규모/내용이면 이미 경험했다고 느낄 수 있다. 새 편의 더 큰 매력과 변화가 보여야 한다.','07–08','피크민4의 오치 등 검증된 새 행동을 옆에서 설명. 최신판이라는 이유만으로 게임 교체하지 않음.'),
 ('03:00–03:51','속편도 신작도 완성도가 중요','기반의 이점은 자동 성공을 의미하지 않는다. 완성도와 새로 할 이유를 만들고 두 종류 모두 좋은 게임으로 완성해야 한다.','09','개인 의뢰/이력·원작자 취향은 생략. 일반 제작 판단으로 연결; 전기/일인칭 경험을 우리 것으로 전환하지 않음.')
]
mapping=[dict(referenceRange=a,topic=b,retained=c,scenes=d,clarification=e) for a,b,c,d,e in sections]
plan=read(P/'planning/chapter-plan.json')
plan['currentRevision']={
 'id':'reference-preserving-v2','status':'independent-footage-inspection-and-design','updatedAt':now,
 'authorization':'2026-10-17: 이거 업로드해줘 그리고 다음영상 제작해줘~',
 'baselineVideoId':'2-IyuwcP_vQ','baselinePreserved':True,
 'reference':{'url':'https://www.youtube.com/watch?v=plPR6-Gqemc','title':'Making Sequels [Planning & Game Design]','classification':'research-reference-only','durationSeconds':240,'fullNarrationRead':True,'visualReview':'48 full frames at five-second intervals; all six contact sheets directly viewed; 240 lower-caption OCR samples read as complete narration','localEvidence':'projects/making-game-sequels/production/local/reference-preserving-v2/research','productionUse':False},
 'referenceCoverage':mapping,
 'baselineDifference':'The old Orcs Must Die lesson rearranged and expanded the reference into another lesson. Preserve that delivery but use the actual reference backbone and original example roles for this selected revision.',
 'screenRole':{'actual':0.6,'explanation':0.4,'excludedSeconds':12,'roundingFrames':1,'paddingOrLoops':False,'sourceMinimum':[1920,1080],'master':[1920,1080,60]},
 'games':[
  {'series':'Pikmin','selected':'Pikmin 4 (Nintendo Switch)','role':'serial game; established command/collection activity and new companion decisions','latestAvailability':'Switch2Edition+DandoriAcademy announced for2026-11-12, after current2026-10-17; not yet available','primary':'https://www.nintendo.com/us/store/products/pikmin-4-nintendo-switch-2-edition-dandori-academy-125241/'},
  {'series':'Gran Turismo','selected':'Gran Turismo 7','role':'serial driving game; distinguish visible cars/courses from reusable driving systems','primary':'https://www.gran-turismo.com/gb/products/gt7/'},
  {'series':'Super Smash Bros.','selected':['for Wii U','Ultimate'],'role':'historical team/environment continuity comparison; keep WiiU because replacing it loses the historical contrast','primary':['https://www.bandainamcostudios.com/products/smashbros-wiiu.html','https://www.bandainamcostudios.com/products/smashbros-special.html']}
 ],
 'renderer':'Motion Canvas','rendererReason':'The lesson concerns development layers, experience flow and screenshot comparisons; 2D diagrams and annotated actual recordings explain it without inventing an engine implementation.',
 'visualStyle':'research-black-v1','uiPolicy':'yamyam-video-ui-v1','visualEvidencePolicy':'explanation-visual-evidence-v1',
 'captions':{'style':'boxed-white-forest-v1','center':[960,970],'fontSize':48,'maxLines':2},
 'glossary':[
  {'ko':'기반 시스템','en':'Underlying systems','meaning':'입력을 받아 움직임·충돌·규칙 결과를 반복해서 처리하는 공통 기능'},
  {'ko':'제작 도구','en':'Development tools','meaning':'맵·적·경주 등을 만들고 고치는 작업용 프로그램'},
  {'ko':'콘텐츠','en':'Content','meaning':'그 기능으로 플레이어에게 제공하는 구체적인 장소·도전·상대'},
  {'ko':'시제품','en':'Prototype','meaning':'핵심 행동이 재미있는지 먼저 시험하는 작은 실행본'},
  {'ko':'플레이테스트','en':'Playtest','meaning':'실제로 조작하며 의도한 재미·문제를 확인하는 과정'}
 ],
 'nextAction':'Inspect downloaded independent native-FHD gameplay before final narration. Then complete KO/EN script and all editable scene designs; preserve reference order and pair screenshots with each explanation.',
 'humanFinalReview':'pending-complete-new-version','youtubeUpload':'not-authorized-before-new-version-review','automaticNextVideo':False
}
write(P/'planning/chapter-plan.json',plan)
manifest=read(P/'project.json')
manifest['currentRevision']={'id':'reference-preserving-v2','status':'in-production','plan':'projects/making-game-sequels/planning/chapter-plan.json#currentRevision','baselineVideoId':'2-IyuwcP_vQ','baselinePreserved':True,'selectedAt':now,'deliveryStatus':'not-rendered'}
manifest['status']='selected-reference-preserving-v2-in-production'
write(P/'project.json',manifest)
checkpoint=read(P/'production/latest-checkpoint.json')
if 'previousCompletedCheckpoint' not in checkpoint:
 checkpoint={'schemaVersion':2,'slug':P.name,'previousCompletedCheckpoint':checkpoint}
checkpoint.update(updatedAt=now,revision='reference-preserving-v2',stage='reference-read-independent-footage-inspection',nextAction=plan['currentRevision']['nextAction'],selectedVideoOnly=True,baselineVideoId='2-IyuwcP_vQ',newRevisionRendered=False,newRevisionHumanReviewed=False,automaticNextVideo=False)
write(P/'production/latest-checkpoint.json',checkpoint)
ledger=P/'production/review-ledger.json'
if not ledger.exists():write(ledger,{'schemaVersion':1,'slug':P.name,'revision':'reference-preserving-v2','referenceCoverage':'projects/making-game-sequels/planning/chapter-plan.json#currentRevision','checks':[{'id':'reference-full-content','status':'reviewed','evidence':'local/reference-preserving-v2/research/reference-ocr.txt + reference-sheet-00..05.jpg','reviewedAt':now}],'footageInspection':'pending','scriptReview':'pending','voiceReview':'pending','renderReview':'pending','humanListening':'pending','driveFinalReview':'pending'})
print('D19 selected revision registered; baseline and historical evidence retained.')
