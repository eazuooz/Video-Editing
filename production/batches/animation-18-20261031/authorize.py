"""Apply only the user's finite animation-series authorization and title/layout rules.

This is an idempotent metadata operation, not a TTS/render or publishing runner.
mutate() also supports selective commits against HEAD without foreign changes.
"""
from pathlib import Path
import copy, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'production/batches/design-25-30-review-actions-20261029'))
from scoped_json import load, patch

BATCH = 'animation-18-20261031'
PLAN = 'production/planning/sakurai-animation-20261031/plan.json'
CONTROL = 'shared/publishing/video-production-control.json'
WORKLIST = 'shared/publishing/video-worklist.json'
IDS = [f'A{i:02d}' for i in range(1, 19)]
REQUEST = '그럼 원본주제를 앞에두고 | 뒤에 우리제목 초안을 넣어줘. 애니메이션툴 환경처럼 배경을 깔고, 영상의 캐릭터 동작 분리 가능성을 확인하며 어려우면 그런 환경의 영상을 찾아서 사용. 각영상별로 원본 대본 검수해서 최대한 비슷한 흐름으로 영상제작 들어가줘.'
REVISED = {
    'A04': '공격의 준비 동작을 짧고 강하게 만드는 방법',
    'A07': '게임 화면에서 동작의 느낌이 약해지는 이유',
    'A10': '캐릭터는 맞았다는 사실을 어떻게 보여줄까?',
    'A12': '게임 캐릭터는 어떻게 표정을 바꿀까?',
    'A13': '방향이 바뀌어도 캐릭터의 포즈가 잘 보이는 비밀',
    'A15': '게임 속 손가락 하나에 계산이 많이 필요한 이유',
    'A16': '공격 동작과 판정은 왜 함께 설계해야 할까?',
    'A18': '회전 동작을 덜 기계적으로 보이게 하는 방법',
}
AUTH = dict(
    id=BATCH, requestedOnKst='2026-10-31', userEvidence=REQUEST,
    status='active-preproduction', episodeIds=IDS,
    scope='Exactly A01-A18 through original-lesson review, independently sourced footage, script, own-voice narration, scene production, internal QA and four local review outputs.',
    batch=f'production/batches/{BATCH}/batch.json',
    checkpoint=f'production/batches/{BATCH}/checkpoint.json',
    productionAuthorized=True, ttsAuthorized=True, renderAuthorized=True,
    sequentialAdvanceWithinExactList=True, automaticAdvanceOutsideList=False,
    humanFinalReviewRequired=True, youtubeAuthorized=False, driveAuthorized=False,
    publicPublicationAuthorized=False, schedulingAuthorized=False, deletionAuthorized=False,
    automaticChatOrHeartbeatAuthorized=False,
    resourcePolicy='Sequence costly jobs; inspect existing jobs and GPU before each new job. Preserve unrelated processes, user games, files and staging; no forced termination.',
)
VISUAL = dict(
    id='animation-grid-presentation-v1', scope=IDS,
    referenceImage='C:/Users/1/AppData/Local/Temp/codex-clipboard-27b57f74-50a8-4b02-afc9-b67e3197cac1.png',
    visualIntent='Light neutral square grid, grounded floor/reference line, sparse axis markers, fixed readable character scale and shared A/B framing. Adapt the submitted layout without reusing its characters or pixels.',
    firstChoice='Test a short independently sourced FHD gameplay clip for character separation and composite it onto our grid.',
    qualityChecks=['hair and thin weapons', 'fast-motion blur and effects', 'contact feet and shadows', 'occlusion and changing camera', 'temporal edge flicker', '1080p and mobile readability'],
    fallback='If separation damages the demonstrated motion, prefer rights-verified independent FHD animation-tool or native training-grid recordings. Use our licensed Unity animation preview only as a separately labelled explanation.',
    sourceSeparation='Finished reference lessons and character extractions from them remain research-only and must never enter the production cut list.',
    disclosure='A composited background is an editorial motion study, not proof of access to an original game editor. Distinguish original game/tool recording, background-separated composite and our Unity demonstration.',
    ratio='Retain the ordinary game-content 60:40 contract unless the user changes it. Tool recordings have their own source kind; self-authored Unity remains explanation. Never pad or relabel footage to meet a ratio.',
    preserve=['original motion speed and aspect', 'required source watermarks', 'fixed caption clearance', 'existing brand semantic tokens', 'independently editable scene sources'],
)

def dump(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')

def revised_plan(raw):
    p = load(raw)
    p.setdefault('authorizationHistory', []).append(copy.deepcopy(p['authorization'])) if not p['authorization'].get('batchProductionAuthorized') else None
    p['status'] = 'active-preproduction'
    p['authorization'].update(scope=AUTH['scope'], productionAuthorized=True,
        automaticNextVideoAuthorized=False, sequentialAdvanceWithinExactList=True,
        batchProductionAuthorized=True, ttsAuthorized=True, renderAuthorized=True,
        batchAuthorization=AUTH['batch'], userEvidence=REQUEST)
    p['titlePolicy'].update(format='{originalTopicKo} | {draftTitleKo}',
        optionalTitleSuffix=None, status='topic-first-draft',
        userDirectedOnKst='2026-10-31',
        basis='User-selected original topic first; use the topic-faithful revisions from the immediately preceding comparison as the recommended draft. Confirm against full lesson and selected footage before TTS.')
    p['visualPolicy'] = VISUAL
    for ep in p['episodes']:
        ep.setdefault('previousDraftTitleKo', ep['draftTitleKo'])
        ep['draftTitleKo'] = REVISED.get(ep['id'], ep['draftTitleKo'])
        ep['titleKo'] = f"{ep['topicKo']} | {ep['draftTitleKo']}"
        ep.update(titleStatus='topic-first-draft', productionAuthorized=True,
                  productionStatus='reference-review-in-progress',
                  batchAuthorization=AUTH['batch'])
    return p

def mutate(name, raw):
    if name == PLAN:
        return dump(revised_plan(raw))
    if name == CONTROL:
        c = load(raw)
        if 'finiteBatchAuthorizations' not in c:
            raw = patch(raw, ['finiteBatchAuthorizations'], {})
        return patch(raw, ['finiteBatchAuthorizations', BATCH], AUTH)
    p = revised_plan((ROOT / PLAN).read_bytes())
    by_id = {x['id']: x for x in p['episodes']}
    if name == WORKLIST:
        w = load(raw)
        for idx, row in enumerate(w['rows']):
            if row['id'] not in IDS:
                continue
            r = copy.deepcopy(row)
            r.update(title=by_id[r['id']]['titleKo'], titleStatus='topic-first-draft',
                productionAuthorized=True, productionStatus='원본 대본·화면 검토 및 격자 시연 방식 검증 중',
                reviewStatus='내부 사전 검토 중 · 완성본 사용자 검수 대기',
                humanApproval='18편 제작 착수 승인 · 완성본 검수/업로드 미승인',
                executionStatus='명시된 18편 제작 · 비용 작업 순차 실행',
                notes='원본 주제 | 우리 제목. 원본 전체 설명 흐름 보존, 독립 FHD 자료와 격자 배경 표현 검증. 검수본까지 제작하며 공개/예약/업로드는 별도.',
                batchAuthorization=AUTH['batch'])
            raw = patch(raw, ['rows', idx], r)
        a = copy.deepcopy(w['animationSeriesPlan'])
        a.update(status='active-preproduction', productionAuthorized=True,
                 sequentialAdvanceWithinExactList=True, batch=AUTH['batch'])
        raw = patch(raw, ['animationSeriesPlan'], a)
        return patch(raw, ['executionAuthorized'], list(dict.fromkeys(w['executionAuthorized'] + IDS)))
    text = raw.decode('utf-8-sig')
    newline = '\r\n' if '\r\n' in text else '\n'
    if name == 'docs/VIDEO_WORKLIST.md':
        start, end = '<!-- ANIMATION-PLAN-20261031-START -->', '<!-- ANIMATION-PLAN-20261031-END -->'
        lines = [start, '## 게임 애니메이션 18편 제작', '',
            '2026-10-31 사용자 지시로 A01–A18 전편을 로컬 최종 검수본까지 제작합니다. 원본 주제 순서·대본 흐름을 검토하고 제목은 `원본 주제 | 우리 제목`을 사용합니다. 음성·렌더 등 비용 작업은 순차 실행하며 다른 시리즈·기존 예약은 보존합니다.', '',
            '재생목록: [게임 애니메이션 / 움직임과 타격감의 비밀](https://studio.youtube.com/playlist/PLCyia-2FS2wE/edit) · 비공개 · 0편. 이번 요청은 제작 착수이며 업로드/공개/예약 승인은 포함하지 않습니다.', '',
            '| 번호 | 원본 주제 | 제작 제목 초안 | 현재 상태 |', '|---|---|---|---|']
        for ep in p['episodes']:
            title = ep['titleKo'].replace('|', '\\|')
            lines.append(f"| {ep['id']} | [{ep['topicKo']}]({ep['sourceUrl']}) | {title} | 원본 검토·자료/격자 시연 검증 중 |")
        lines += ['', f'진행 기록: [제작 배치](../{AUTH["batch"]}), [체크포인트](../{AUTH["checkpoint"]}), [제목·원본 대응](../{PLAN}). 완성 영상·검수·게시 상태는 실제 결과가 생긴 뒤 갱신합니다.', '', end]
        a, b = text.index(start), text.index(end) + len(end)
        text = text[:a] + newline.join(lines) + text[b:]
    elif name == 'docs/VIDEO_WORKFLOW.md':
        marker = '<!-- ANIMATION-BATCH-20261031 -->'
        if marker not in text:
            text += newline*2 + marker + newline + '2026-10-31 사용자 명시 요청 `animation-18-20261031`: [애니메이션 A01–A18](../production/batches/animation-18-20261031/batch.json)은 18편 전체를 각 원본 대본·화면 검토부터 로컬 최종 검수본까지 순차 제작하는 유한 예외다. 제목은 원본 주제를 앞에 두고 ` | ` 뒤에 우리 제목을 붙인다. 개별 편의 질문·주장·예시 역할·설명 순서·결론을 보존하며 원문 미제공 전체 대본을 번역·복제하지 않고 독립적으로 설명한다. 첨부 격자 배경은 시각 방향으로 사용하고, 실제 캐릭터 배경 분리 품질을 짧은 영상으로 검증한 뒤 독립 FHD 자료를 선택한다. 상세는 VIDEO_VISUAL_STYLE.md의 animation-grid-presentation-v1. 이 예외는 다른 배치·자동 채팅·업로드·공개·예약·삭제를 승인하지 않는다.' + newline
    elif name == 'docs/VIDEO_VISUAL_STYLE.md':
        marker = '<!-- ANIMATION-GRID-PRESENTATION-V1 -->'
        if marker not in text:
            text += newline*2 + marker + newline + '## 애니메이션 시리즈의 격자 관찰 배경' + newline*2 + '2026-10-31 사용자 요청 `animation-grid-presentation-v1`은 A01–A18의 동작 관찰 장면에 적용한다. 밝은 중성색 사각 격자, 바닥 기준선, 필요한 축/접지 표식, 고정된 캐릭터 크기와 A/B 프레이밍으로 동작을 비교한다. 이 무대는 기존 검정 설명 배경의 해당 시리즈용 예외이며 다른 편의 팔레트는 보존한다.' + newline*2 + '독립 FHD 게임 녹화에서 캐릭터를 분리해 3–5초 실제 움직이는 샘플로 머리카락·무기·모션 블러·이펙트·접지·가림·시간축 경계 떨림을 검사한다. 분리가 동작을 훼손하면 권리 확인된 애니메이션 툴/게임 자체 훈련 격자 녹화를 우선 찾는다. 자체 Unity 에셋 시연은 구분된 설명 장면으로 사용할 수 있다. 원본 강의에서 캐릭터만 추출해 재사용하지 않는다. 합성은 실제 에디터 출력이나 측정값처럼 표시하지 않고 자료 유형을 정확히 기록한다. 실제 게임의 속도·비율·필수 워터마크와 고정 자막 영역을 보존하며, 없는 게임 사운드를 원음으로 꾸미지 않는다. 전경의 출처·권리·FHD·해시·컷, 마스크 방식과 실패/채택 이유, 배경/축/카메라 설정, 시연 씬 경로를 기존 장면 계획과 검수 원장에 연결한다.' + newline
    elif name == 'AGENTS.md':
        marker = '<!-- ANIMATION-18-20261031 -->'
        if marker not in text:
            text += newline*2 + marker + newline + '- User explicitly selected all A01–A18 animation episodes on 2026-10-31 for sequential production through local final review. See `production/batches/animation-18-20261031/batch.json`; this finite exception does not resume unrelated batches or authorize YouTube/Drive publication.' + newline + '- For this series, title format is original Korean topic + ` | ` + our topic-faithful draft. Follow `animation-grid-presentation-v1` in docs/VIDEO_VISUAL_STYLE.md: test actual independent-footage character separation; otherwise source verified native grid/tool footage; reference-lesson extractions remain prohibited. Preserve original lesson flow after reviewing full narration and relevant visuals.' + newline
    else:
        raise ValueError(name)
    return (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'') + text.encode('utf8')

SHARED = [PLAN, CONTROL, WORKLIST, 'docs/VIDEO_WORKLIST.md', 'docs/VIDEO_WORKFLOW.md', 'docs/VIDEO_VISUAL_STYLE.md', 'AGENTS.md']

if __name__ == '__main__':
    for name in SHARED:
        f = ROOT / name
        old = f.read_bytes()
        new = mutate(name, old)
        if old != new:
            f.write_bytes(new)
    episodes = load((ROOT / PLAN).read_bytes())['episodes']
    batch = dict(AUTH, visualPolicy=VISUAL, episodes=episodes,
                 titleFormat='{originalTopicKo} | {draftTitleKo}',
                 plan=PLAN, destinationPlaylistId='PLCyia-2FS2wE',
                 voicePreference='Retain the user-approved own-voice ElevenLabs Sample B used by the latest game-design deliveries; do not silently substitute Qwen because of older generic defaults.')
    (HERE/'batch.json').write_bytes(dump(batch))
    checkpoint = HERE/'checkpoint.json'
    if not checkpoint.exists():
        checkpoint.write_bytes(dump(dict(batch=BATCH,status='active-preproduction',
            currentEpisode='A01',completedLocalReviews=[],
            currentWork=['full reference transcript and visual review','foreground isolation feasibility','independent FHD footage selection'],
            nextAction='Finish A01 source-to-screen plan using reviewed independent footage; then lock narration and run one approved-voice synthesis job.',
            costlyJobsStarted=0,platformMutations=0)))
    assert len(episodes) == 18 and all(x['productionAuthorized'] for x in episodes)
    assert all(x['titleKo'].startswith(x['topicKo']+' | ') for x in episodes)
    print(json.dumps({'batch': BATCH, 'episodes': len(episodes), 'titleFormat': 'topic | draft', 'publishingAuthorized': False}))
