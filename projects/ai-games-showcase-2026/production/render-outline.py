"""Render the readable script from current narration, evidence and the single plan."""
from pathlib import Path
import json, re

P = Path(__file__).resolve().parents[1]

def read(name):
    return json.loads((P / name).read_text(encoding='utf-8-sig'))

ko = read('script/narration.ko.json')
en = read('script/narration.en.json')
plan = read('planning/production-plan.json')
research = read('sources/research.json')
aliases = read('script/pronunciation.json')['aliases']
assert [s['id'] for s in ko['scenes']] == [s['id'] for s in en['scenes']] == [s['id'] for s in plan['scenes']]
assert all(len(a['lines']) == len(b['lines']) for a, b in zip(ko['scenes'], en['scenes']))

def display(text):
    for canonical, spoken in sorted(aliases.items(), key=lambda pair: len(pair[1]), reverse=True):
        # A Korean suffix such as '했다고도' must not turn into '했다Godot'.
        text = re.sub(r'(?<![가-힣A-Za-z0-9])' + re.escape(spoken), lambda _: canonical, text)
    return text

lines = [
    '# AI 게임 제작 근황 — 전체 대본과 화면 구성', '',
    '2026-10-18 수정: 여섯 게임의 **실행 환경·엔진/제작 기반**을 설명하고, 사용한 AI를 처음 등장하는 대목에 소개한다. 게임 소개 형식은 유지하며, 별도 강의 구조나 60:40 비율을 강제하지 않는다.', '',
    '**현재 상태:** 한영 대본과 삽입 영상 설계 수정 완료. 아래 AI 소개 화면은 제작 계획이며 아직 촬영·렌더링된 완성 영상이 아니다. 기존 12초 무음 샘플은 화면 배치 참고용이다. 최종 마스터는 1920×1080/60fps, 완성본은 Drive에서 먼저 검수한다.', '',
    '## 실행 환경과 제작 기반', '',
    '| 게임 | 어디서 실행하는가 | 엔진·프레임워크·플랫폼 | 확인 범위 |',
    '|---|---|---|---|',
]
for g in research['games']:
    env = g['runtimeAndEngine']
    game_link = f"[{g['name']}]({g['url']})"
    if g.get('editorUrl'):
        game_link += f" · [레벨 에디터]({g['editorUrl']})"
    lines.append(f"| {game_link} | {env['viewerRuntimeKo']} | {env['viewerEngineKo']} | {env['limitsKo']} |")
lines += ['', '## 개발 기간과 AI 사용 근거', '',
          '| 게임 | 개발 기간의 의미 | 공개된 모델·AI |', '|---|---|---|']
for g in research['games']:
    period = g['development']['value'] or '전체 기간 미공개/미확인'
    models = ' / '.join((m['name'] or '정확한 모델 미공개') + (' (소개자 언급만 확인·확정 사실로 내레이션하지 않음)' if m['confidence'] == 'reviewer-reported-only' else '') for m in g['models'])
    lines.append(f"| {g['name']} | {period} · {g['development']['stage']} | {models} |")
lines += ['', '기간은 제작자가 공개한 해당 단계의 기록이다. 초기 버전 3일, 진행 중 11주 차, 약 3주 작업을 같은 완성 기준으로 비교하지 않는다. [게임별 조사 근거](../sources/research.json)와 [확보 영상 목록](../sources/media.json)을 구분해 보관한다.', '',
          '## 사이에 들어갈 AI 소개 영상', '',
          '소개는 해당 게임의 구체적인 작업을 이어받는다. 공식 기능 화면 또는 출처가 확인된 시연을 바탕으로 요청 → 작업 → 결과를 짧게 보여 준 뒤 게임으로 돌아온다. 설명용 흐름도는 그 사실을 표시하며 제작자의 실제 작업 화면으로 꾸미지 않는다. 모든 삽입 화면은 아래 문단 번호에 연결되어 있고 정확한 시간은 TTS 실측 뒤 확정한다.', '',
          '| 위치 | 소개 대상 | 보여 줄 동작과 게임으로 돌아가는 연결 |', '|---|---|---|']
for scene in plan['scenes']:
    for insert in scene.get('aiIntroInserts', []):
        span = str(insert['paragraphs'][0]) if len(insert['paragraphs']) == 1 else f"{insert['paragraphs'][0]}–{insert['paragraphs'][-1]}"
        lines.append(f"| {scene['id']}장 · {span}문단 | {insert['titleKo']} | {insert['visualKo']} → {insert['returnKo']} |")
lines += ['', '## 전체 대본', '', '고유명사는 화면 표기로 적었다. 음성 생성용 한글 발음과 화면·자막의 정식 표기는 별도로 관리한다.', '']
for narration, scene in zip(ko['scenes'], plan['scenes']):
    lines += [f"### {narration['id']}. {narration['title']}", '']
    start = {item['paragraphs'][0]: item for item in scene.get('aiIntroInserts', [])}
    for number, paragraph in enumerate(narration['lines'], 1):
        if number in start:
            insert = start[number]
            lines += [f"> **삽입 영상 — {insert['titleKo']}**\n>\n> {insert['visualKo']}", '']
        lines += [display(paragraph), '']
    lines += [f"화면 구성: {scene.get('visualEvidenceKo', scene['visualEvidence'])}", '',
              f"다음 연결: {scene['transitionToNext'].get('narrativeKo', scene['transitionToNext']['narrative'])}", '']
lines += ['## AI·기술 설명의 공식 근거', '']
for source in research['toolReferences']:
    lines += [f"- [{source['label']}]({source['url']}): {source['supportsKo']}"]
lines += ['', '## 제작 상태', '',
    '- 완료: 여섯 게임 조사, 한영 대본 수정, 실행 환경·엔진 구분, AI 소개 삽입 위치와 게임 복귀 동작 설계.',
    '- 확보: 네 게임의 FHD 이상 영상과 두 브라우저 게임의 FHD 화면. 기존 12초 무음 화면 샘플은 배치 검수 범위만 유효.',
    '- 다음 작업: AI 소개용 공식 화면·시연의 사용 조건 및 FHD 해상도 확인, 필요한 촬영과 삽입 장면 제작, 실제 영상 컷 검수.',
    '- 음성: 사용자의 이전 지시에 따라 게임·Unity 사용 종료/GPU 인계 확인 대기. 새 음성·완성 편집·최종 QA는 아직 완료되지 않음.',
    '- 완성 후: clean/captioned/KO/EN 출력과 Drive 검수본. 사용자 검수 이후 같은 버전의 YouTube 업로드. 자동 다음 편 없음.', '']
(P / 'planning/outline.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({'scenes': len(ko['scenes']), 'paragraphs': sum(len(s['lines']) for s in ko['scenes']), 'inserts': sum(len(s.get('aiIntroInserts', [])) for s in plan['scenes']), 'output': str(P / 'planning/outline.md')}, ensure_ascii=False))
