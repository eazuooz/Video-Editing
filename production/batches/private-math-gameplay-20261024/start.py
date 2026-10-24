"""Record the user's gameplay-only revision and audit the actual old edit lists.

This is an edit-list audit, not a claim that somebody watched the final videos.
Never changes old media, old approval evidence, unrelated selections or staging.
"""
from pathlib import Path
import copy, datetime, html, json

R = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
KEY = B.name
OLD = R / 'production/batches/private-math-concept-fit-20261023'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p, v):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
control_path = R/'shared/publishing/video-production-control.json'
control = read(control_path)
prior = control['scopedBatchAuthorizations']['private-math-concept-fit-20261023']
auth = dict(id=KEY, recordedAt=now, status='active', ids=prior['ids'], slugs=prior['slugs'],
    userEvidence=[
        '핵심 주요 내용마다 영상한개씩은 그러면 영상마다 3개이상은 들어가줘야지 이해가 돼지',
        '어떤영상은 잘들어갔는데 어떤영상은 안들어갔고 어떤영상은 너무 빠르게 넘어가서 짧고 그래 다 검수해서 만들어줘봐',
        '설명쪽은 잘 된거같아 실제 게임 영상만 잘 삽입하고 기즈모그려서 표현해서 매끄럽게 잘 연결되게끔 해줘'],
    scope='18 selected existing Game Math lectures: preserve explanation scenes, formulas, voice and teaching order; fix actual gameplay selection, meaningful exposure, guides and joins.',
    fullProductionAuthorized=True, renderAuthorized=True, newTtsAuthorized=False,
    explanationRewriteAuthorized=False, uploadAuthorized=False, deleteAuthorized=False,
    scheduleAuthorized=False, heartbeatEnabled=False, automaticAdvanceWithinThisList=True,
    advanceBeyondThisList=False, stopAt='18 revised four-file local deliveries and truthful internal QA, then human review',
    choice=dict(minimumMeaningfulGameExamplesPerEpisode=3,
       interpretation='Three distinct taught examples/intervals, not a requirement to pad with three different titles. Each main concept needs a matched example; three alone is not a coverage pass.',
       duration='Before/action/result and associated narration determine length. No automatic short window, looping, slowdown, or unrelated lead/tail padding.',
       preserved='Existing explanation animation and speech. If a game-specific spoken fact cannot be matched, record it before changing narration; no automatic new TTS.',
       stillFrames='An explicitly labeled analytical freeze can support a moving demonstration; it is explanation time, never counted as additional actual gameplay.'))
if KEY not in control['scopedBatchAuthorizations']:
    control['scopedBatchAuthorizations'][KEY]=auth
    save(control_path,control); save(B/'authorization.json',auth)

core = {
 'M03-original':['물체의 방향과 자세','로컬 축과 월드 축','회전 합성과 되돌리기'],
 'M04':['축과 회전 순서','로컬/월드 회전','같은 자세와 다른 회전 경로'],
 'M05':['회전축과 회전량','같은 자세의 표현','회전과 역회전'],
 'M06':['서로 다른 축의 합성','현재 자세에서 목표 자세','물체에 붙은 방향 벡터'],
 'M07':['두 자세 사이 중간 자세','경로와 각속도','짧은 회전과 여러 바퀴'],
 'M08':['같은 자세/다른 표현','기준 축과 180도','앞과 위로 자세 결정'],
 'M09':['원과 중심/반지름','직선/반직선/선분','두 끝점과 거리'],
 'M10':['물체의 범위','겹침과 실제 접촉','회전 뒤 경계 변화'],
 'M11':['점과 표면 거리','기울어진 평면의 방향','세 점으로 정한 면'],
 'M12':['삼각형 모양과 넓이','면 안의 위치','꼭짓점 속성의 보간'],
 'M13':['중심을 정하는 목적','한 타일과 전체 경계','오목한 부분과 빈 공간'],
 'M14':['볼록한 조각/전체 윤곽','오목한 홈과 영역 보존','조각 분할 뒤 경계 갱신','좁은 통로와 분할 품질'],
 'M15':['가림과 깊이','빛/재질/표면 방향','간접광과 반사'],
 'M16':['뷰포트와 분할 화면','시야각과 관찰 범위','카메라 이동과 확대'],
 'M17':['물체/월드/카메라 좌표','같은 물체의 투영','가까운 물체와 화면 경계'],
 'M18':['앞뒤 가림과 깊이','기울어진 면의 무늬','거리와 투영 크기'],
 'M19':['표면의 연결과 모서리','평평한 면과 둥근 면','경계에서 다른 표면 속성'],
 'M20':['크기 변경과 표면 방향','표면에 붙는 무늬','무늬의 좌표/반복/경계']}
entries=[]
for e in read(OLD/'checkpoint.json')['entries']:
    h=R/'projects'/e['slug']/'production/concept-fit-v2'
    c=read(h/'composition.json'); t=read(h/'timeline.json')
    slots={s['id']:s for s in t['scenes']}; shots=[]
    for s in c['scenes']:
        games=s.get('game') or []
        if isinstance(games,dict): games=[games]
        for g in games:
            if not isinstance(g,dict): continue
            slot=slots[s['id']]
            shots.append(dict(scene=s['id'],source=g.get('source'),sourceIn=g.get('start'),
                seconds=g['seconds'],sceneSeconds=slot['seconds'],offset=g.get('offset',0),
                title=g.get('title'),narratedSeconds=slot.get('voiceSeconds'),
                risk='very-short-review-required' if g['seconds']<5 else 'watch-with-narration',
                actualMovingReview=False,semanticFit='pending-current-review'))
    entries.append(dict(id=e['id'],slug=e['slug'],title=e['title'],status='재검수 중 · 기존본 보존',
        previousOutput=e['outputFolder'],oldClipCount=len(shots),
        oldGameSeconds=round(sum(x['seconds'] for x in shots),3),
        underFiveSeconds=sum(x['seconds']<5 for x in shots),
        coreConcepts=[dict(concept=k,matchedExample=None,review='pending') for k in core[e['id']]],
        shots=shots,actualFinalReview=False,newRender=False,humanReview='pending'))
save(B/'edit-list-audit.json',dict(at=now,kind='composition-metadata-audit',entries=entries,
    warning='Clip count/duration is a triage measure only, not semantic or playback approval.'))
if not (B/'checkpoint.json').exists():
    save(B/'checkpoint.json',dict(updatedAt=now,status='gameplay-only-revision-active',entries=entries,
        ready=0,current='M14',nextAction='Review source motion and narration for polygon partition, then replace short/weak gameplay; preserve existing explanations.',
        explanationPreserved=True,newTts=False,platformChanges=False))
workpath=R/'shared/publishing/video-worklist.json';work=read(workpath)
work['privateMathPolish']['gameplayTimingRevision']=dict(authorization=str((B/'authorization.json').relative_to(R)).replace('\\','/'),
    checkpoint=str((B/'checkpoint.json').relative_to(R)).replace('\\','/'),status='재검수 중 · 수정본 0/18',
    readyCount=0,entries=[{k:e[k] for k in ['id','slug','title','status','oldClipCount','oldGameSeconds','underFiveSeconds']} for e in entries])
save(workpath,work)
workflow=R/'docs/VIDEO_WORKFLOW.md';text=workflow.read_text('utf-8-sig')
marker='2026-10-24 사용자 보강: **핵심 내용별 게임 예시와 충분한 동작 노출**'
if marker not in text:
    line=next(l for l in text.splitlines() if l.startswith('2026-10-23 사용자 지시 `narration-matched-gameplay-v1`'))
    addition=marker+' — 이번18편 게임수학 수정은 편당 최소3개의 의미 있는 실제 게임 예시를 배치하고, 각 주요 개념의 대응 장면을 확인한다. 같은 장면의 재사용·짧은 반복·다른 제목만으로 개수를 채우지 않는다. 발화와 실제 동작을 함께 보며 전 상태→동작→결과가 충분히 보이는 길이를 정한다. 특정 초 수에 맞춰 잘라내지 않으며1–5초 삽입 컷은 자동 통과시키지 않는다. 사용자가 좋다고 평가한 기존 설명·수식·애니메이션·음성은 보존하고 게임 구간·성질에 맞는 표식·연결만 고친다. 분석용 정지 화면은 명시하고 설명 시간으로 집계하며 실제 게임 재생을 대체하는 최소 개수로 세지 않는다. 이번 명시 수정 범위는 `private-math-gameplay-20261024`이며 자동 재개·업로드·다른 영상 제작은 허용하지 않는다.'
    workflow.write_text(text.replace(line,line+'\n\n'+addition),encoding='utf8')
rows=[]
for e in entries:
    rows.append(f"| {e['id']} | {e['title']} | {e['oldClipCount']} | {e['oldGameSeconds']:g}초 | {e['underFiveSeconds']} | 재검수 중 | 미완료 |")
report='# 게임수학 실제 게임 장면 재검수\n\n'+f'갱신: {now}\n\n'+\
    '**현재 수정본 완료 0/18. 기존 concept-fit-v2는 이전 검수본입니다.** 설명·수식·애니메이션·음성을 보존하고 게임 예시·기즈모·연결을 수정합니다. 아래 수치는 편집목록에서 확인한 것으로 실제 의미 적합성 검수를 대신하지 않습니다.\n\n'+\
    '| 번호 | 강의 | 기존 게임 컷 | 기존 게임 총길이 | 5초 미만 컷 | 현재 상태 | 새 렌더·검수 |\n|---|---|---:|---:|---:|---|---|\n'+'\n'.join(rows)+'\n\n기준: 주요 내용별 실제 동작 예시, 편당 최소3개 의미 있는 예시, 동시 해설과 충분한 전후 상태, 대상에 맞는 선/기즈모, 정상 속도, FHD 소스와1080p60 출력. 잘 맞는 기존 구간은 유지합니다.\n'
(B/'review-table.md').write_text(report,encoding='utf8')
doc=R/'docs/GAME_MATH_PRIVATE_POLISH.md';old=doc.read_text('utf-8-sig')
start='<!-- GAMEPLAY-20261024-START -->';end='<!-- GAMEPLAY-20261024-END -->'
if start in old: old=old.split(start)[0]+old.split(end,1)[1].lstrip('\n')
doc.write_text(start+'\n'+report+'\n'+end+'\n\n'+old,encoding='utf8')
out=R/'output/private-math-gameplay-20261024';out.mkdir(parents=True,exist_ok=True)
htmlrows=''.join('<tr>'+''.join(f'<td>{html.escape(str(v))}</td>' for v in [e['id'],e['title'],e['oldClipCount'],f"{e['oldGameSeconds']:g}초",e['underFiveSeconds'],'재검수 중','미완료'])+'</tr>' for e in entries)
(out/'index.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>게임수학 게임 장면 재검수</title><style>body{background:#101412;color:#f5f5ef;font:17px/1.6 system-ui;margin:28px}h1{color:#ffd773}table{border-collapse:collapse;width:100%}td,th{padding:12px;text-align:left;border-bottom:1px solid #455047}a{color:#80d3a2}.scroll{overflow:auto}</style><h1>게임수학 게임 장면 재검수</h1><p>현재 수정본 완료 <b>0 / 18</b> · 설명/수식/애니메이션/음성 보존</p><p>기존 검수본과 구분한 새 수정 진행표입니다. 컷 수와 길이만으로 통과시키지 않습니다.</p><div class="scroll"><table><tr><th>번호</th><th>강의</th><th>기존 게임 컷</th><th>총길이</th><th>5초 미만</th><th>진행</th><th>새 렌더</th></tr>'+htmlrows+'</table></div></html>',encoding='utf8')
print(json.dumps(dict(episodes=len(entries),belowThree=[e['id'] for e in entries if e['oldClipCount']<3],shortCuts=sum(e['underFiveSeconds'] for e in entries),table=str(out/'index.html')),ensure_ascii=False))
