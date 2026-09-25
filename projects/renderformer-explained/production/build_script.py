"""Compile the reviewed page narration into pipeline JSON, never synthesize audio.

Canonical authoring file: script/review.ko.md. Generated timing is an estimate,
not suitable for SRT or rendering. Actual WAV durations must replace it later.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]

CHAPTERS = [
    (1, 2, '영상 안내'),
    (3, 11, '트랜스포머와 입력 표현'),
    (12, 25, '셀프 어텐션과 멀티헤드'),
    (26, 31, '잔차 연결·정규화·FFN'),
    (32, 44, '디코더·마스킹·크로스 어텐션'),
    (45, 49, 'RenderFormer의 전체 구조'),
    (50, 61, '삼각형 토큰과 공개 코드'),
    (62, 71, '공간 위치 인코딩과 RoPE'),
    (72, 76, '시점 독립 트랜스포머'),
    (77, 85, '카메라 레이와 이미지 복원'),
    (86, 88, '학습 데이터·결과·한계'),
]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    manifest = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    source = Path(manifest['sourceDocument']['path'])
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash != manifest['sourceDocument']['sha256']:
        raise ValueError('The source PDF has changed; review page coverage and corrections before rebuilding.')
    review = (ROOT / 'script/review.ko.md').read_text(encoding='utf-8')
    pieces = re.split(r'^## (\d{2}) \| (.+)$', review, flags=re.MULTILINE)
    scenes = []
    for i in range(1, len(pieces), 3):
        scene_id, title, body = pieces[i:i+3]
        screen, narration = body.split('\n내레이션:\n', 1)
        visual = screen.strip().removeprefix('화면: ').strip()
        lines = [line.strip() for line in narration.splitlines() if line.strip()]
        if not lines or any(line.startswith(('#', '화면:', '보완:')) for line in lines):
            raise ValueError(f'Invalid narration at {scene_id}')
        scenes.append({'id': scene_id, 'title': title, 'sourcePage': int(scene_id),
                       'visual': visual, 'lines': lines})
    if [s['sourcePage'] for s in scenes] != list(range(1, 89)):
        raise ValueError('All original pages 1..88 must appear exactly once, in order.')

    spoken_units = []
    for scene in scenes:
        # Non-whitespace characters are only a rough proxy for Korean delivery.
        # 4.5..5.5 units/s plus 3..6s per page for pauses/looking at diagrams.
        units = len(re.findall(r'[가-힣A-Za-z0-9]', ''.join(scene['lines'])))
        spoken_units.append(units)
        scene['estimatedSecondsRange'] = [round(units / 5.5 + 3), round(units / 4.5 + 6)]
        scene['timingIsMeasured'] = False
    draft = {'title': '트랜스포머부터 RenderFormer까지 | 삼각형에서 이미지로',
             'status': manifest['approvals']['script'], 'updatedAt': '2026-09-25',
             'source': 'script/review.ko.md', 'language': 'ko',
             'pageCount': 88, 'scenes': scenes}
    write_json(ROOT / 'script/narration.ko.json', draft)
    report = {
        'status': 'script-only-not-rendered',
        'sourcePdf': str(source),
        'sourceSha256': source_hash,
        'sourceHashMatchesManifest': True,
        'scriptSha256': hashlib.sha256(review.encode('utf-8')).hexdigest(),
        'sourcePageCount': 88, 'sceneCount': len(scenes),
        'coverage': '88/88 sequential, no omitted or duplicate pages',
        'narrationLineCount': sum(len(s['lines']) for s in scenes),
        'estimatedSpokenUnits': sum(spoken_units),
        'estimatedTotalSecondsRange': [sum(s['estimatedSecondsRange'][j] for s in scenes) for j in (0, 1)],
        'timingIsMeasured': False,
        'timingWarning': 'Non-whitespace letter count / 4.5..5.5 per second + 3..6 sec/page; replace using actual TTS lengths. Not SRT timestamps.',
        'chapters': [],
    }
    for start, end, title in CHAPTERS:
        selected = scenes[start-1:end]
        report['chapters'].append({'title': title, 'pages': [start, end],
            'estimatedSecondsRange': [sum(s['estimatedSecondsRange'][j] for s in selected) for j in (0, 1)]})
    write_json(ROOT / 'planning/page-plan.json', {'timingIsMeasured': False, 'scenes': [
        {k: s[k] for k in ('id', 'title', 'sourcePage', 'visual', 'estimatedSecondsRange', 'timingIsMeasured')} for s in scenes]})
    write_json(ROOT / 'production/script-check.json', report)

    index = ['# 페이지별 제작표', '',
             '원본 88쪽을 한 페이지당 독립 씬 하나로 사용한다. 아래 시간은 발화량에 근거한 예상치이며 자막 타임코드가 아니다.', '',
             '| 페이지 | 제목 | 예상 길이(초) | 화면 지시 |', '|---|---|---:|---|']
    for s in scenes:
        low, high = s['estimatedSecondsRange']
        index.append(f"| {s['id']} | {s['title']} | {low}~{high} | {s['visual'].replace('|', '/')} |")
    (ROOT / 'planning/page-plan.md').write_text('\n'.join(index)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
