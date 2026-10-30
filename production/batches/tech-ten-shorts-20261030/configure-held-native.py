"""Provisional scene bindings only. No adopted footage or production readiness."""
import json
from scoped_context import BATCH, ROOT, REVISION, read


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    recipes = {
      'shorts-batman-origins-snow-below-camera': {
        'game': 'Batman: Arkham Origins', 'head': ['눈 위에 남은 발자국', '땅 밑에서 찍었다'],
        'term': '높이맵', 'english': 'Height Map', 'plainMeaning': '그림의 밝기로 눈이 눌린 정도를 기록', 'definitionCue': 'p4-1',
        'stages': {'game': 2, 'capture': 1, 'record': 2, 'compare': 2, 'render': 2, 'result': 2},
        'nativeActionCues': {'compare': {'kind': 'accumulation-toggle', 'cueId': 'p4-2', 'resumeCueId': 'p4-3'}},
        'steps': {'capture': ['직교 투영: 거리와 무관한 크기', '눈 아래 카메라 → 발목 높이 영역'],
                  'record': ['흰색 접촉 모양', '이전 흔적에 누적'],
                  'render': ['콘솔: 릴리프 매핑', 'PC DX11: 테셀레이션', '화면은 자체 단순화 시연']},
        'reactionCues': [{'cueId': 'p1-2b', 'kind': 'realize', 'durationSeconds': 2.5}, {'cueId': 'p6-2', 'kind': 'relief', 'durationSeconds': 2.5}],
        'limits': ['No clear rights-cleared commercial snow-contact shot adopted yet.',
                   'Current Unity mesh displacement is explanatory, not measured Batman tessellation or a claim that relief mapping changes actual geometry.',
                   'Console relief mapping versus PC tessellation visual differentiation remains unresolved; latest native implementation still needs compilation/preflight.']},
      'shorts-uncharted3-fixed-plane-scrolling-desert': {
        'game': 'Uncharted 3: Drake’s Deception', 'head': ['날아가는 비행기는 고정', '사막이 뒤로 움직였다'],
        'term': '무한 스크롤 배경', 'english': 'Infinite Scrolling Background', 'plainMeaning': '배경을 끊김 없이 움직여 이동감을 표현', 'definitionCue': 'p4-3',
        'stages': {'game': 1, 'observer': 2, 'relative': 2, 'repeat': 1, 'compare': 2, 'result': 2},
        'nativeActionCues': {'compare': {'kind': 'background-toggle', 'cueId': 'p5-1', 'resumeCueId': 'p5-3'}},
        'steps': {'observer': ['고정: 비행기 · 탑승 카메라', '이동: 사막 배경'],
                  'relative': ['탑승 시점 | 바깥 관찰 시점', '같은 시간 · 같은 배경 이동'],
                  'repeat': ['이어지는 타일: 자체 구현 예시'],
                  'compare': ['변수 하나: 배경 이동 OFF / ON']},
        'reactionCues': [{'cueId': 'p1-2', 'kind': 'realize', 'durationSeconds': 2.5}, {'cueId': 'p5-3b', 'kind': 'relief', 'durationSeconds': 2.5}],
        'limits': ['Independent gameplay publisher-rights gate unresolved; no adopted cut.',
                   'Recycled background tiles are our illustration. The original engine tile-manager algorithm and zero-physics/origin-coordinate claims are not asserted.']},
      'shorts-uncharted4-taut-rope-fallback': {
        'game': 'Uncharted 4: A Thief’s End', 'head': ['흔들리는 로프 뒤에는', '팽팽한 안전장치가 있다'],
        'term': '폴백', 'english': 'Fallback', 'plainMeaning': '계산이 불안정할 때 사용할 대체 경로', 'definitionCue': 'p5-3',
        'stages': {'game': 1, 'particles': 0, 'risk': 0, 'safe': 1, 'fallback': 2, 'result': 1},
        'nativeActionCues': {'risk': {'kind': 'rope-risk', 'cueId': 'p3-2'},
                            'fallback': {'kind': 'rope-fallback', 'cueId': 'p5-3'}},
        'steps': {'particles': ['입자 사이 거리 · 충돌 조건'],
                  'risk': ['불안정한 계산: 자체 실패 시연'],
                  'safe': ['장애물을 감싸는 별도 경로'],
                  'fallback': ['폴백 복원 원리 시연']},
        'reactionCues': [{'cueId': 'p4-3', 'kind': 'realize', 'durationSeconds': 2.5}, {'cueId': 'p6-3b', 'kind': 'relief', 'durationSeconds': 2.5}],
        'limits': ['Independent gameplay publisher-rights gate unresolved; no adopted cut.',
                   'Particle restoration onto maintained taut path is our simplified fallback demonstration. Exact commercial fallback restoration is undisclosed.',
                   'Artificial weak-solver risk is not actual Uncharted bug footage.']},
    }
    mc = ROOT / 'motion-canvas/src/projects/tech-ten-shorts-20261030'
    for slug, original in recipes.items():
        recipe = dict(original); project = ROOT / 'projects' / slug
        stages, steps, limits = recipe.pop('stages'), recipe.pop('steps'), recipe.pop('limits')
        config = {**recipe, 'slug': slug, 'frameRoot': '/@fs/' + (project / 'production/local/frames').resolve().as_posix(),
                  'defaultExplanationKind': 'unity', 'definitionDurationSeconds': 4.2, 'cuts': {}, 'annotations': {},
                  'provisionalOnly': True, 'heldReasons': limits}
        save(project / 'production/visual-config.json', config)
        path = project / 'production/section-plan.json'; sections = read(path)
        for row in sections:
            row.update(kind='unity', unityStage=stages[row['id']])
            if row['id'] in steps: row.update(steps=steps[row['id']], activeStep=0)
            if row['id'] == 'game': row['pendingActualGameOpening'] = True
        save(path, sections)
        name = slug + '-' + REVISION
        code = [BATCH / 'prepare-visual.py', BATCH / 'capture-unity.py', BATCH / 'render-one.cjs', BATCH / 'prepare-mc-entries.py']
        code += list(mc.glob('*.ts*')) + list((mc / 'entries' / slug).glob('*.ts'))
        code += [p for p in (BATCH / 'unity-source').rglob('*') if p.is_file()]
        save(project / 'production/visual-pipeline.json', {'revision': REVISION, 'usesUnity': True, 'provisionalOnly': True,
            'prepareCommand': ['{PYTHON}', '-B', '-X', 'utf8', '{ROOT}/production/batches/tech-ten-shorts-20261030/prepare-visual.py', '{SLUG}'],
            'nativeCaptureCommand': ['{PYTHON}', '-B', '-X', 'utf8', '{ROOT}/production/batches/tech-ten-shorts-20261030/capture-unity.py', '{SLUG}'],
            'nativeCaptureReceipt': '{LOCAL}/unity-capture/native-receipt.json',
            'renderCommand': ['node', '{ROOT}/production/batches/tech-ten-shorts-20261030/render-one.cjs', '{SLUG}', name, '0', '{FRAMES}'],
            'visualOutput': '{LOCAL}/motion-canvas-output/' + name + '.mp4', 'renderReceipt': '{LOCAL}/' + name + '-render.json',
            'codePaths': sorted(set(p.relative_to(ROOT).as_posix() for p in code))})
        path = project / 'planning/production-plan.json'; plan = read(path)
        plan.update(productionReady=False, scriptFinalized=False, nativeLatestCodePreflight='pending-after-user-game-exit',
                    provisionalSceneBindings=True, nativeImplementationLimits=limits)
        save(path, plan)
        print('Prepared held native configuration: ' + slug)


if __name__ == '__main__': main()
