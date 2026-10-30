"""Configure only the two source-verified StarCraft state-diagram Shorts."""
import json
from scoped_context import BATCH, ROOT, REVISION, read


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    recipes = {
        'shorts-starcraft-eud-compatibility-emulator': {
            'diagramType': 'eud', 'game': 'StarCraft · EUD 유즈맵 예시',
            'head': ['스타 유즈맵을 살리려고', '에뮬레이터를 만들었다'],
            'term': 'EUD 에뮬레이터', 'english': 'EUD Emulator', 'plainMeaning': '지원되는 옛 요청을 새 데이터에 맞춰 처리',
            'definitionCue': 'p5-1',
            'stages': {'game': 1, 'trigger': -1, 'blocked': 0, 'need': 0, 'emulator': 1, 'result': 2},
            'cuts': {'game': {'source': 'game-master', 'in': 31, 'maxDuration': 7},
                     'result': {'source': 'game-master', 'in': 49, 'maxDuration': 7, 'fromCue': 'p6-2'}},
            'speechEvents': {'trigger:request-travel': ['p2-2'], 'trigger:read-other-data': ['p2-3', 'p2-4'],
                             'blocked:request-travel': ['p3-2'], 'need:request-travel': ['p4-2'],
                             'emulator:request-travel': ['p5-2'], 'emulator:value-return': ['p5-3'],
                             'result:request-travel': ['p6-1'], 'result:value-return': ['p6-1']},
            'reactionCues': [{'cueId': 'p5-3', 'kind': 'realize', 'durationSeconds': 2.5}, {'cueId': 'p6-2', 'kind': 'relief', 'durationSeconds': 2.5}]},
        'shorts-starcraft2-replay-input-resimulation': {
            'diagramType': 'replay', 'game': 'StarCraft II · 리플레이',
            'head': ['리플레이를 켜면', '게임이 다시 실행된다'],
            'term': '결정론적 시뮬레이션', 'english': 'Deterministic Simulation', 'plainMeaning': '같은 시작·규칙·입력으로 같은 결과 재현',
            'definitionCue': 'p4-2b',
            'stages': {'game': 0, 'commands': 0, 'replay': 1, 'compare': 1, 'version': 2, 'result': 1},
            'cuts': {'game': {'source': 'game-master', 'in': 25, 'maxDuration': 12},
                     'result': {'source': 'game-master', 'in': 37, 'maxDuration': 7, 'fromCue': 'p6-2'}},
            'speechEvents': {'commands:replay-run': ['p2-2'], 'replay:move-command': ['p3-1b'], 'replay:attack-command': ['p3-1c'],
                             'compare:replay-run': ['p4-1'], 'version:replay-run': ['p5-1'], 'result:replay-run': ['p6-1']},
            'reactionCues': [{'cueId': 'p3-2', 'kind': 'realize', 'durationSeconds': 2.5}, {'cueId': 'p6-2', 'kind': 'relief', 'durationSeconds': 2.5}]},
    }
    for slug, recipe in recipes.items():
        project = ROOT / 'projects' / slug; stages = recipe.pop('stages')
        config = {**recipe, 'slug': slug, 'frameRoot': '/@fs/' + (project / 'production/local/frames').resolve().as_posix(),
                  'defaultExplanationKind': 'diagram', 'definitionDurationSeconds': 4.2, 'annotations': {},
                  'annotationStatus': 'Exact moving source-keyframe verification remains a visual QA item; no fabricated tracked rectangles.'}
        save(project / 'production/visual-config.json', config)
        spec_path = project / 'production/section-plan.json'; spec = read(spec_path)
        for section in spec: section.update(kind='diagram', diagramType=recipe['diagramType'], unityStage=stages[section['id']])
        save(spec_path, spec)
        name = slug + '-tech-ten-v1'
        mc = ROOT / 'motion-canvas/src/projects/tech-ten-shorts-20261030'
        code = [BATCH / 'prepare-visual.py', BATCH / 'render-one.cjs', BATCH / 'prepare-mc-entries.py']
        code += list(mc.glob('*.ts*')) + list((mc / 'entries' / slug).glob('*.ts'))
        save(project / 'production/visual-pipeline.json', {'revision': REVISION, 'usesUnity': False,
            'rendererReason': 'Abstract command/state mappings are executed as purposeful Motion Canvas models; no native Unity or proprietary internal buffer claim.',
            'prepareCommand': ['{PYTHON}', '-B', '-X', 'utf8', '{ROOT}/production/batches/tech-ten-shorts-20261030/prepare-visual.py', '{SLUG}'],
            'renderCommand': ['node', '{ROOT}/production/batches/tech-ten-shorts-20261030/render-one.cjs', '{SLUG}', name, '0', '{FRAMES}'],
            'visualOutput': '{LOCAL}/motion-canvas-output/' + name + '.mp4', 'renderReceipt': '{LOCAL}/' + name + '-render.json',
            'codePaths': [p.relative_to(ROOT).as_posix() for p in code]})
        plan_path = project / 'planning/production-plan.json'; plan = read(plan_path)
        plan.update(rightsAndFhdReady=True, sourceFileAndDecodedDimensionsVerified=True,
                    renderer={'selected': 'Motion Canvas', 'reason': 'Explain old-request adapters and recorded-input state transitions by executing deterministic compact state models.',
                              'nativeUnityClaimed': False, 'source': mc.relative_to(ROOT).as_posix()},
                    finalWholeMotionAndListening='pending')
        save(plan_path, plan)
        print('Configured ' + slug)


if __name__ == '__main__': main()
