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
    '2026-10-18 수정: 긴 AI 설명 영상은 제외한다. **각 게임의 실행 환경·제작 기반·사용 도구만 PPT 한 장으로 5초씩** 보여 준다. 개발 기간과 사람이 다듬은 내용은 실제 게임 장면 위에서 설명한다. 별도 강의 구조나 60:40 비율을 강제하지 않는다.', '',
    '**현재 상태:** 전체 한영 대본 수정 완료. PPT와 음성·편집 진행 상태는 [현재 체크포인트](../production/checkpoint.json)에 기록한다. 최종 마스터는 1920×1080/60fps이며 완성본은 Drive에서 먼저 검수한다. 대본·무음 미리보기는 완성 영상이 아니다.', '',
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
          '## 게임마다 한 번 나오는 5초 요약 PPT', '',
          '각 화면은 300프레임(60fps), 여섯 장 합계 30초다. 실제 게임 화면 옆에 확인된 환경과 도구를 간단히 나열한다. 한 문장으로 핵심만 말하고 다시 게임으로 돌아간다. 말을 5초에 억지로 압축하지 않으며 필요하면 문장 끝은 돌아온 게임 화면 위로 자연스럽게 잇는다. 제작 기간은 별도 설명하고, 미확인 모델과 내부 엔진은 그대로 표시한다.', '',
          '| 위치 | 게임 | 5초 동안 표시할 내용 |', '|---|---|---|']
for scene in plan['scenes']:
    card = scene.get('developmentSummary')
    if card:
        contents = '<br>'.join(f"{label}: {value.replace(chr(10), ' · ')}" for label, value in card['rows'])
        lines.append(f"| {scene['id']}장 · {card['paragraph']}문단 | {card['title']} | {contents} |")
lines += ['', '## 전체 대본', '', '고유명사는 화면 표기로 적었다. 음성 생성용 한글 발음과 화면·자막의 정식 표기는 별도로 관리한다.', '']
for narration, scene in zip(ko['scenes'], plan['scenes']):
    lines += [f"### {narration['id']}. {narration['title']}", '']
    card = scene.get('developmentSummary')
    for number, paragraph in enumerate(narration['lines'], 1):
        if card and number == card['paragraph']:
            lines += [f"> **개발 환경·도구 PPT — 5초**\n>\n> 실제 게임 캡처와 위 표의 도구 목록. 이 문장 시작에 띄우고 5초 뒤 게임 화면으로 복귀한다.", '']
        lines += [display(paragraph), '']
    lines += [f"화면 구성: {scene.get('visualEvidenceKo', scene['visualEvidence'])}", '',
              f"다음 연결: {scene['transitionToNext'].get('narrativeKo', scene['transitionToNext']['narrative'])}", '']
lines += ['## AI·기술 설명의 공식 근거', '']
for source in research['toolReferences']:
    lines += [f"- [{source['label']}]({source['url']}): {source['supportsKo']}"]
lines += ['', '## 제작 상태', '',
    '- 완료: 여섯 게임 조사, 전체 한영 대본 32문단, 실행 환경·엔진 구분, 5초 요약 PPT 여섯 장의 내용·위치 설계. 긴 AI 기능 소개 삭제.',
    '- 확보: 네 게임의 FHD 이상 영상과 두 브라우저 게임의 FHD 화면. 기존 12초 무음 화면 샘플은 배치 검수 범위만 유효.',
    '- 제작: 실제 게임 캡처를 포함한 PPT 여섯 장과 편집용 프레임 준비, 실제 게임 컷 검수. 상세 상태는 체크포인트를 기준으로 한다.',
    '- 음성: 사용자의 이전 지시에 따라 게임·Unity 사용 종료/GPU 인계 확인 대기. 새 음성·완성 편집·최종 QA는 아직 완료되지 않음.',
    '- 완성 후: clean/captioned/KO/EN 출력과 Drive 검수본. 사용자 검수 이후 같은 버전의 YouTube 업로드. 자동 다음 편 없음.', '']
(P / 'planning/outline.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({'scenes': len(ko['scenes']), 'paragraphs': sum(len(s['lines']) for s in ko['scenes']), 'toolSlides': sum(bool(s.get('developmentSummary')) for s in plan['scenes']), 'output': str(P / 'planning/outline.md')}, ensure_ascii=False))
