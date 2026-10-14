from pathlib import Path
import datetime, hashlib, html, json, os

raise SystemExit('Superseded four-game package generator: do not run. Follow planning/production-plan.json and the current source-preserving policy.')

ROOT=Path(__file__).resolve().parents[4]
P=ROOT/'projects/hierarchical-game-outlines'
V=P/'revision-teaching-clarity-v1'
OUT=Path(__file__).resolve().parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

# One editable scene design per retained/inserted script scene. Source claims remain bounded.
designs=[
('01b','추가 · 전체 개론','큰 질문 → 가지의 범위 → 포함과 연결, 세 단계','기존 흰색 투영 트리에서 목표·기능·조건을 차례로 펼치고 4게임 이름은 해당 단계 옆에 표시. 23.84초 기존 PCM. 마지막 포커스를 놀이기구로 넘긴다.'),
('01','유지+표식 · Two Point Museum','큰 설치 결정과 세부 결정은 같은 크기가 아니다','놀이기구 몸체/입구를 빨간 브래킷으로 차례로 지시. 실제 UI와 겹치는 부분은 숨기고 컷마다 좌표를 새로 잡는다. 원래 네 문단·컷 순서를 보존.'),
('02','유지 · 목표→기능→조절값','부모 질문에 하위 항목이 답한다','검수된 white-02-v4의 투영된 트리·층·가림·순차 펼침 재사용. 실제 게임 내부 설계도가 아니라 화면 관찰로 만든 문서 예시임을 유지.'),
('03','유지+표식 · 전체와 선로 조각','부모의 범위와 선택한 부분을 구별한다','선택된 전체 놀이기구와 선로 조각의 외곽을 컷별 추적. 빨강=지금 읽는 대상, 청록=연관 조절값. 화면 이동/가림에서는 표식을 숨긴다.'),
('04','유지 · 형제 항목','같은 단계는 비슷한 크기의 질문이어야 한다','white-04-v4의 형제 높이와 가지 재배치 동작 유지. 너무 큰 목표와 작은 수치가 같은 층에 있는 오류→교정 결과를 보여 준다.'),
('04a','추가 · Manor Lords','수치 조절 외에 선택형 항목도 같은 원리인가','2022 pre-alpha 맥락을 먼저 말한다. 건물 배치→목공 인원 1/3→2/3→시장 Hide 선택/인원 0/2→1/2를 서로 다른 발췌로 명시. 중간 투영 문서에서 목공/시장 기능 아래 인원/품목을 붙인다. 원본 UI값을 덮지 않는다.'),
('05','유지+표식 · 전체/조각','큰 구조를 읽다가 필요한 세부로 내려간다','Two Point Museum 전체→선택 조각→조절값의 순서대로 외곽과 관련 패널을 지시. 원래 여섯 문단 보존. 다음 접기 설명의 대상은 동일한 문서 트리.'),
('06','유지 · 접기','가리는 것과 삭제하는 것은 다르다','white-06-v4의 접기/다시 펼치기 재사용. 자식 노드를 지우지 않고 부모 뒤로 들어갔다가 같은 내용으로 복귀. 문서 접기이며 게임 기능이라고 주장하지 않는다.'),
('07','유지+표식 · 조각과 설명','항목을 옮길 때 붙은 조건도 함께 따라야 한다','선택 조각·그 설정 패널을 같은 색쌍으로 묶는다. 컷 전환시 이전 브래킷 제거. 원래 일곱 문단 순서를 유지하고 실제 동작과 문서 비유를 구별.'),
('08','유지 · 가지 이동','이동 뒤에도 부모 질문에 맞는 뜻인가','white-08-v4의 부모+자식 묶음 이동 재사용. 목표 아래 잘못 들어간 세부 조건을 비교하고, 이름만 이동시키는 오류와 구분.'),
('08a','추가 · Against the Storm','다른 기능의 조건을 엉뚱한 가지에 넣지 않는가','2024 개발 시연 맥락과 정착지 규칙 설명. 주택 회전/기초/한 채 완성→광산 건설 조건→낚시 미끼 설정을 비교. 주택/자원 생산 가지는 분리하고 조건을 해당 기능 아래 붙인다. 광산 채굴·낚시 생산 완료는 관찰되지 않아 주장하지 않는다.'),
('09','유지+표식 · 포함과 참조','같이 영향을 준다고 같은 부모 아래인가','실제 선택 대상과 다른 관련 대상을 빨강/청록으로 구분. 화면상 의미 연결만 표시하고 엔진 데이터 구조/물리적 연결이라고 부르지 않는다.'),
('10','유지 · 트리의 한계','포함 관계와 다른 가지 참조를 따로 적는다','white-10-v4의 부모-자식 실선과 참조선 대비 유지. 선 색만으로 구별하지 않고 포함/참조 라벨도 유지.'),
('10a','추가 · Timberborn','수문 설정과 레버 신호는 어떻게 적는가','1.0 시연, 수문 Off 1m/On 2m와 Badtide 신호 필드→레버 Off/On의 관찰된 표시만 설명. 수문 설정은 자식, 레버/신호는 다른 기능으로 두고 청록 참조선으로 연결. 실제 배선·수위 변화·효과는 추정하지 않는다. 네 게임의 공통점/차이를 말한 뒤 전체 읽기로 복귀.'),
('11','유지+표식 · 전체 다시 읽기','세부 변경 뒤 목표가 여전히 읽히는가','Two Point Museum 실제 조절과 전체 보기의 차이를 추적 표식으로 연결. 원래 일곱 문단·좋은 설명·관찰 시간을 보존.'),
('12','유지 · 읽는 사람을 위한 문서','찾고 비교하고 수정하기 쉬운가','white-12-v4와 원래 네 문단/과외 안내 유지. 최종 트리의 목표→기능→조건·접기·이동·참조를 요약. 원래 고양이120프레임/회원600프레임과 12회원 신원 보존.')]
original={lang:read(P/f'script/narration.{lang}.json') for lang in ['ko','en']}
added={lang:read(V/f'script/additions.{lang}.json') for lang in ['ko','en']}
combined={}
for lang in ['ko','en']:
    byid={s['id']:s for s in original[lang]['scenes']+added[lang]['scenes']}
    combined[lang]={'title':original[lang]['title'],'scenes':[byid[id] for id,*_ in designs]}
    assert len(combined[lang]['scenes'])==16 and sum(len(s['lines']) for s in combined[lang]['scenes'])==78
    assert [s for s in combined[lang]['scenes'] if s['id'] in {x['id'] for x in original[lang]['scenes']}]==original[lang]['scenes']
    save(OUT/f'combined.{lang}.json',combined[lang])

refs=['current-content-and-studio-direct-review-v1.json','causal-paired-script-direct-review-v2.json','native-candidate-direct-review-v4.json','candidate-normal-playback-observation-v3.json','source-primary-rights-and-recent-use-v1.json','source-action-planning-direct-review-v1.json','retained-gameplay-annotation-gap-audit-v1.json','two-paragraph-repair-voice-closure-verification-v1.json']
bindings={rel(V/f):sha(V/f) for f in refs}
bindings.update({rel(P/f'script/narration.{l}.json'):sha(P/f'script/narration.{l}.json') for l in ['ko','en']})
bindings[rel(P/'project.json')]=sha(P/'project.json')
license=dict(track='Late Night Radio',artist='Kevin MacLeod',officialPage='https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN2100003',license='CC BY 4.0',licenseUrl='https://creativecommons.org/licenses/by/4.0/',commercialUse=True,attributionRequired=True,
    file=rel(OUT/'Late-Night-Radio.mp3'),sha256=sha(OUT/'Late-Night-Radio.mp3'),acquiredVia='CUA129 official download',reviewedAt=now,selectionStatus='proposed audio comparison; user listening pending',
    attribution='Late Night Radio — Kevin MacLeod (incompetech.com). CC BY 4.0: https://creativecommons.org/licenses/by/4.0/ . Excerpted, faded and mixed under narration.',
    otherCandidate={'track':'No Rush — Dyalla','status':'download-blocked-by-browser-security-policy; not acquired or used','workaroundAttempted':False})
save(OUT/'music-rights.json',license)
text='''# 계층형 아웃라인 — 수동 수정 제작안

이 문서는 사용자가 선택한 한 편의 수정안이다. 기존 예약 영상 jBRt3xatdPk와 원본 납품은 그대로 보존한다. 전체 수정 영상은 아직 제작 완료가 아니다.

## 무엇을 바꾸나

- 기존 12장·한영 각 60문단·승인 PCM·설명 순서를 유지한다. 개론과 세 게임 비교를 끼워 넣어 16장·한영 각 78문단으로 구성한다.
- **Two Point Museum → Manor Lords → Against the Storm → Timberborn**으로 같은 문서 원리를 다른 기능과 조건에 적용한다. 타이틀 몽타주가 아니라 각 게임의 규칙·행동·결과·차이를 설명한다.
- 게임 위에 말하는 대상과 설정값의 추적 브래킷/선을 추가한다. 원본 UI·고정 하단 자막과 충돌하지 않도록 컷별 위치와 가림을 설계한다.
- 검수된 흰색 2.5D 설명은 유지한다. 이 편의 대상은 문서의 가지/노드이므로 투영된 기하 도식이 적합하며, 불필요한 사람 삽화를 덧붙이지 않는다.
- 이번에 제안하는 오디오는 조용한 로파이 후보다. 게임 디자인 편의 기존 Nimbus 계약을 모든 영상에서 일괄 변경하는 것은 아니다.

## 비교 샘플

약47초: 기존 첫 문단의 게임 화면 + 부모/자식 설명 장면. 같은 화면으로 기존 믹스와 새 음악을 비교한다. 전체 수정본이나 새 게임 위 표식의 승인 샘플은 아니다.

- 원본: `production/manual-preflight-v1/original-comparison.mp4`
- 로파이 제안: `production/manual-preflight-v1/lofi-comparison.mp4`
- 후보 곡: Late Night Radio — Kevin MacLeod, 공식 배포 CC BY 4.0. 수익화 사용 가능, 출처·라이선스·편집 여부 표시 필요.
- 이번 샘플은 내레이션+음악이다. 기존 Two Point Museum 원본에 오디오 트랙은 있으나 진행자 해설/음악과 섞여 기존 납품에서 제외했다. 새 세 게임 자료는 영상 전용이다. 효과음이 보존되었다고 주장하지 않는다. 분리된 적법한 원음이 확보되지 않으면 해당 구간은 무원음으로 남기며 합성 효과음으로 대체하지 않는다.

## 장면별 제작 입력

각 장면은 실제 최종 자막 박스(중심960,970/48px/최대2줄)를 먼저 배치한다. 설명용 도식은 대략 y≤850을 사용하고, 게임 UI는 해당 컷별로 가림을 확인한다. 빨강=선택 대상, 청록=관련 조건/참조, 노랑=독자가 답할 질문. 움직임은 해당 문장의 발화 순서에 맞춘다.

| 순서 | 장면 | 질문/역할 | 화면·동작·보존 |
|---|---|---|---|
'''
for i,(id,role,claim,visual) in enumerate(designs,1): text+=f'| {i} · {id} | {role} | {claim} | {visual} |\n'
text+='''
## 길이·실제 화면 분량

기존 9분46.75초, 본편 실제60:설명40을 유지한다. 추가 음성은 현재196.96초이며 두 교정 후보 채택 시 실측을 갱신한다. 예상 완성 길이는 약14–15분으로 잡되 확정 길이는 아니다.

검토된 세 게임의 후보 창은 Manor21초, Storm25.5초, Timber38초로 합84.5초이며, 이 안의 정지/툴팁 중심 구간은 설명으로 분리해야 한다. 이 수치 전체를 실제 분량 승인으로 사용하지 않는다. 추가196.96초를 그대로 배치하고 후보84.5초를 전부 실제로 간주해도, 정확60:40에는 추가로 약84.19초의 관련 고유 행동이 필요하다. Museum 추가34.5초 및 Timber 설정20초는 후보이지 승인된 분량이 아니다.

따라서 **최종 음성 배정/본 렌더 전에 소스 용량을 닫아야 한다.** 기존 유용한 설명을 줄이거나 동일 컷 반복/감속/무관 대기로 채우지 않는다. 충분한 관련 행동을 확보하지 못하면 비중을 통과했다고 쓰지 않고 사용자에게 구체적인 선택지를 제시한다.

## 검수와 납품 범위

중복 검사 현재 통과(실제39bd5b/exit0). 완료된870소스 표본·151판과 정상 재생 근거를 재사용한다. 두 교정 음성 후보는 이번에 현재 파일만 ASR 확인하고, 채택 시 다른08a 문단의 PCM을 그대로 보존한다. 기존 전체 TTS/소스 추출은 반복하지 않는다.

본 제작에서는 바뀐 표식/추가 장면·현재 타이밍 자막·접합부를 한 번 묶어 검수한다. 새 최종 쌍의 decode/PTS/길이/60:40/동일AAC/현재믹스ASR은 필요하다. 최종 clean/captioned/KO/EN4파일과 제목/설명/썸네일을 함께 전달한다.

현재 Studio는 예약됨/SDHD완료/저장 비활성으로 읽었고 변경하지 않았다. 이전 실제 예약은2026-10-14 09:00 Asia/Seoul이다. 업로드·예약교체·옛 영상 삭제는 이번 패키지의 완료본 확인과 게시 범위를 따른다. 자동 다음 영상/자동채팅은 꺼진 상태를 유지한다.

## 전체 한영 대본

기존 문단은 원문과 순서를 보존했다. 아래 추가 문단도 이미 준비한 쌍을 재사용한다.

'''
for ko,en in zip(combined['ko']['scenes'],combined['en']['scenes']):
    text+=f"### {ko['id']} · {ko['title']}\n\n"
    for n,(a,b) in enumerate(zip(ko['lines'],en['lines']),1): text+=f'{n}. **KO** {a}\n\n   **EN** {b}\n\n'
(P/'planning/manual-revision.md').write_text(text,encoding='utf8')
plan=dict(schemaVersion=1,policyId='preproduction-first-v1',slug='hierarchical-game-outlines',updatedAt=now,status='selected-video-preproduction-package-in-progress',
    selection=dict(userMessage='계층형아웃라인 영상 새로운 규칙에 맞게 수정해줘',selectedAt=now,scope='This video only: concrete revision design and bounded samples; full production follows package confirmation'),
    outline=rel(P/'planning/manual-revision.md'),scripts={l:rel(OUT/f'combined.{l}.json') for l in combined},sceneDesigns=[dict(id=id,role=role,claim=claim,visual=visual) for id,role,claim,visual in designs],inputHashes=bindings,
    preservation=dict(originalScenes=12,originalParagraphsPerLanguage=60,combinedScenes=16,combinedParagraphsPerLanguage=78,originalOrderAndWordsExact=True,baselineProjectSha256=sha(P/'project.json'),palette='research-paper-white-v1',ratio='actual60:explanation40',baselineVideoId='jBRt3xatdPk',scheduleChanged=False),
    audio=dict(policy='lecture-lofi-game-audio-v1 proposed for this selected teaching video',rights=rel(OUT/'music-rights.json'),sample=rel(OUT/'lofi-comparison.mp4'),comparison=rel(OUT/'original-comparison.mp4'),sourceSfxRestored=False,sourceSfxAvailability='original Museum mixed commentary/music; added three sources video-only',humanListening=False),
    sourceCapacity=dict(status='pending exact action-only allocation',baselineSeconds=586.75,additionVoiceSeconds=196.96,candidateSecondsUpperBound=84.5,additionalActionMinimumAtUpperBound=84.19,expectedDurationRangeSeconds=[840,900],noLoopsOrSlowdown=True),
    approvals=dict(preproduction=dict(status='pending',message=None),finalDelivery=dict(status='pending',actions=[])),
    fullRenderAllowed=False,automaticNextVideo=False,reviewLedger=rel(P/'production/review-ledger.json'),nextAction='Complete remaining capacity/annotation preflight, then present this single package for confirmation; preserve baseline reservation.')
save(P/'planning/production-plan.json',plan)
controlpath=ROOT/'shared/publishing/video-production-control.json'; control=read(controlpath)
control.update(updatedAt=now,selectedVideo='hierarchical-game-outlines',newProductionAuthorization=plan['selection'])
save(controlpath,control)
ledgerpath=P/'production/review-ledger.json'
assert not ledgerpath.exists(), 'Merge existing ledger rather than replace.'
save(ledgerpath,dict(schemaVersion=1,slug=plan['slug'],updatedAt=now,package=rel(P/'planning/production-plan.json'),entries=[
 dict(check='original-content',status='pass',method='Exact equality of all retained scene objects, line order and both languages',inputHashes=bindings),
 dict(check='source-research',status='reused',evidence=rel(V/'native-candidate-direct-review-v4.json'),samples=870,boards=151,completedViewsRepeated=0),
 dict(check='current-duplicate',status='pass',actualChunk='39bd5b',actualExit=0),
 dict(check='source-capacity',status='pending',detail=plan['sourceCapacity']),
 dict(check='current-Studio',status='pass',scope='Read-only CUA119: jBRt3xatdPk scheduled, SDHD, alerts dash, Save disabled; exact date not reopened in this turn',mutation=False),
 dict(check='sample',status='technical-only',evidence=rel(OUT/'sample-state.json'),scope='46.683s audio comparison; no full production, recovered SFX, new annotation or human-listening approval')],fullProductionComplete=False))
cp=read(V/'latest-checkpoint.json');cp.update(recordedAt=now,stage='selected-manual-preproduction-package',currentUserMode='manual-one-video-at-a-time',currentPlan=rel(P/'planning/production-plan.json'),next=plan['nextAction'],automaticContinuationEnabled=False)
save(V/'latest-checkpoint.json',cp)
print(json.dumps({'plan':rel(P/'planning/production-plan.json'),'outline':rel(P/'planning/manual-revision.md'),'originalEquality':True,'scenes':16,'paragraphsPerLanguage':78,'rootProjectUnchanged':sha(P/'project.json')==bindings[rel(P/'project.json')]},ensure_ascii=False))
