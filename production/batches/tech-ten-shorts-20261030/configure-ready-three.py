"""Configure the reviewed Worker/Grid/Marine inputs without launching production."""
import json
from scoped_context import BATCH, ROOT, REVISION, read


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def split_clauses(project, changes):
    path = project / 'script/caption-clauses.json'; doc = read(path); out = []
    for row in doc['clauses']:
        parts = changes.get(row['id'])
        if not parts or any(c['id'] == row['id'] + 'b' for c in doc['clauses']):
            out.append(row); continue
        if ''.join(row['spoken'].split()) != ''.join(''.join(p[0].split()) for p in parts):
            raise RuntimeError('Spoken text changed: ' + row['id'])
        for i, part in enumerate(parts):
            out.append({**row, 'id': row['id'] + (chr(97 + i) if i else ''), 'spoken': part[0],
                        'ko': part[2] if len(part) > 2 else part[0], 'en': part[1]})
    doc['clauses'] = out; save(path, doc)


def main():
    recipes = {
      'shorts-starcraft-worker-mineral-walk': {
        'game': 'StarCraft · 자원 채집', 'head': ['일꾼끼리 겹쳐 지나가는 이유', '돈줄이 막히면 안 되니까'],
        'term': '채집 이동의 충돌 예외', 'english': 'Harvesting Collision Exception', 'plainMeaning': '자원을 오갈 때 유닛 사이 충돌만 무시',
        'definitionCue': 'p3-2', 'defaultExplanationKind': 'unity',
        'stages': {'game': 1, 'blocked': 0, 'rule': 1, 'compare': 1, 'stop': 2, 'result': 1},
        'cuts': {'game': {'source': 'game-master', 'in': 0, 'maxDuration': 16},
                 'result': {'source': 'game-master', 'in': 50, 'maxDuration': 15}},
        'nativeActionCues': {'rule': {'kind': 'harvest-on', 'cueId': 'p3-2'},
                            'compare': {'kind': 'harvest-on', 'cueId': 'p4-2b'},
                            'stop': {'kind': 'stop-scatter', 'cueId': 'p5-1b'}},
        'reactionCues': [{'cueId': 'p4-2b', 'kind': 'realize', 'durationSeconds': 2.5}, {'cueId': 'p6-2b', 'kind': 'relief', 'durationSeconds': 2.5}],
        'splits': {
          'p1-2': [('서로 길을 막으면 돈벌이까지 멈추니,','Blocking one another stops their income too,'), ('개발자는 특별한 규칙을 넣었습니다.','so developers added a special rule.')],
          'p2-2': [('좁은 곳에서 일꾼들이 마주 오면,','When workers meet in a tight space,'), ('서로 막혀 움직이지 못할 수 있죠.','they can block one another and get stuck.')],
          'p3-1': [('그래서 자원을 캐러 가거나,','So while heading to resources,'), ('자원을 들고 돌아오는 동안에는,','or returning while carrying them,')],
          'p4-1': [('우리 시연에선 유닛과 길은 그대로 두고,','In our demonstration, keep the units and path fixed,'), ('이동 상태만 바꿔 볼게요.','and change only the movement state.')],
          'p4-2': [('일반 이동에선 막히지만,','Normal movement gets blocked,'), ('채집 상태에선 겹쳐서 지나갑니다.','but harvesting workers overlap and pass through.')],
          'p5-1': [('채집 중인 일꾼들에게 정지를 명령하면,','Order the harvesting workers to stop,'), ('서로 겹치지 않도록 흩어지죠.','and they spread out to avoid overlap.')],
          'p6-1': [('이렇게 채집에 꼭 필요한 이동만','The movement needed for harvesting'), ('막힘없이 만든 겁니다.','can now keep flowing.')],
          'p6-2': [('길찾기를 전부 뜯어고치지 않고도,','Without rebuilding all of pathfinding,'), ('기지의 돈줄을 지킨 작은 예외였죠.','a small exception kept the economy flowing.')],
        }},
      'shorts-starcraft-diagonal-bridge-square-path-grid': {
        'game': 'StarCraft · 대각선 다리', 'head': ['다리는 대각선인데', '길찾기는 네모였다'],
        'term': '길찾기 격자', 'english': 'Pathfinding Grid', 'plainMeaning': '칸마다 통행 가능 여부를 기록한 지도',
        'definitionCue': 'p2-2', 'diagramType': 'grid', 'defaultExplanationKind': 'diagram',
        'stages': {'game': 0, 'coarse': 0, 'diagonal': 1, 'subdivide': 3, 'compare': 3, 'result': 2},
        'cuts': {'game': {'source': 'game-master', 'in': 50, 'maxDuration': 7}},
        'speechEvents': {'coarse:grid-reveal': ['p2-2'], 'diagonal:grid-reveal': ['p3-2'],
                         'subdivide:fine-grid': ['p4-1b'], 'compare:fine-grid': ['p5-1'],
                         'compare:path-trace': ['p5-1b'], 'result:path-trace': ['p6-1b']},
        'reactionCues': [{'cueId': 'p4-3', 'kind': 'realize', 'durationSeconds': 2.5}, {'cueId': 'p6-2b', 'kind': 'relief', 'durationSeconds': 2.5}],
        'splits': {
          'p1-2': [('그런데 유닛이 지나갈 길은','But the route units could take'), ('네모난 격자로 계산했습니다.','was calculated using a square grid.')],
          'p2-1': [('예전 엔진은 지형을','The older engine divided terrain'), ('가로 세로 삼십이 픽셀짜리 칸으로 나눴습니다.','into thirty-two-by-thirty-two-pixel tiles.','32 × 32픽셀 칸으로 나눴습니다.')],
          'p3-1': [('스타크래프트에서 그림은','In StarCraft, the artwork'), ('비스듬한 시점으로 바뀌었지만,','changed to a tilted perspective,')],
          'p4-1': [('그래서 길찾기 칸을','So the pathfinding cells'), ('가로 세로 팔 픽셀로 더 잘게 나눴습니다.','were divided into smaller eight-by-eight-pixel cells.','8 × 8픽셀로 더 잘게 나눴습니다.')],
          'p5-1': [('우리 그림에서도 칸을 줄이자,','In our diagram, making the cells smaller'), ('통과 가능한 경계가 다리를 더 촘촘히 따라가죠.','makes the passable boundary follow the bridge more closely.')],
          'p5-2': [('대신 찾아야 할 칸이 늘어나,','But the number of cells to search increases,'), ('길찾기 계산 부담도 커졌습니다.','which adds pathfinding work.')],
          'p6-1': [('매끈해 보이는 대각선 다리 아래에는,','Under the smooth-looking diagonal bridge,'), ('계단 모양의 통행 지도가 숨어 있던 거예요.','a staircase-shaped passability map was hidden.')],
          'p6-2': [('보이는 그림과,','The visible artwork'), ('게임이 길을 판단하는 지도는 달랐습니다.','differed from the map used to judge movement.')],
        }},
      'shorts-starcraft2-marine-random-firing-delay': {
        'game': 'StarCraft II · 해병 전투 예시', 'head': ['똑같은 해병이 자연스러운 이유', '발사 박자를 살짝 어긋낸다'],
        'term': '무작위 발사 지연', 'english': 'Random Firing Delay', 'plainMeaning': '다음 발사까지의 대기에 작은 차이 추가',
        'definitionCue': 'p1-2b', 'defaultExplanationKind': 'unity',
        'stages': {'game': 1, 'uniform': 0, 'change': 1, 'numbers': 2, 'compare': 1, 'result': 1},
        'cuts': {'game': {'source': 'game-master', 'in': 6, 'maxDuration': 7},
                 'result': {'source': 'game-master', 'in': 13, 'maxDuration': 7}},
        'reactionCues': [{'cueId': 'p5-1b', 'kind': 'realize', 'durationSeconds': 2.5}, {'cueId': 'p6-2b', 'kind': 'relief', 'durationSeconds': 2.5}],
        'splits': {
          'p1-2': [('이걸 더 자연스럽게 보이게 하는 장치 중 하나가,','One detail that makes this look natural'), ('발사 간격의 작은 무작위 차이예요.','is tiny random variation in shot intervals.')],
          'p2-2': [('같은 순간에 시작한 총성이 계속 겹쳐서,','Shots that start together keep overlapping,'), ('로봇처럼 딱딱해 보이죠.','which looks robotic.')],
          'p3-1': [('우리 시연에서는','In our demonstration,'), ('다음 발사까지 기다리는 시간만 조금 바꿔 봅니다.','change only the wait before the next shot.')],
          'p4-2': [('어떤 병사는 영 점 구팔 초,','One soldier waits 0.98 seconds,','어떤 병사는 0.98초,'), ('다른 병사는 일 점 영이 초를 기다리는 식입니다.','another waits 1.02 seconds.','다른 병사는 1.02초를 기다립니다.')],
          'p5-1': [('처음엔 함께 쐈어도,','Even if they start together,'), ('여러 번 반복하면 총 쏘는 박자가 조금씩 어긋나죠.','repeated shots gradually fall out of sync.')],
          'p5-2': [('발사 간격의 작은 무작위성이,','Tiny randomness in shot timing'), ('부대 전체의 움직임을 자연스럽게 만듭니다.','makes the whole group look more natural.')],
          'p6-1': [('스타크래프트 투는 실제로','StarCraft II actually','스타크래프트 II는 실제로'), ('해병의 발사 간격에 이런 작은 차이를 둡니다.','adds such small differences between Marine shots.')],
          'p6-2': [('똑같은 유닛을 복제해도,','Even when units are identical,'), ('모두 한 박자에 움직이는 느낌을 줄이는 거죠.','they feel less locked to one rhythm.')],
        }},
    }
    mc = ROOT / 'motion-canvas/src/projects/tech-ten-shorts-20261030'
    for slug, original in recipes.items():
        recipe = dict(original); project = ROOT / 'projects' / slug
        split_clauses(project, recipe.pop('splits')); stages = recipe.pop('stages')
        native = recipe['defaultExplanationKind'] == 'unity'
        config = {**recipe, 'slug': slug, 'frameRoot': '/@fs/' + (project / 'production/local/frames').resolve().as_posix(),
                  'definitionDurationSeconds': 4.2, 'annotations': {},
                  'annotationStatus': 'Source-keyframe verification and final motion review remain pending; no invented tracked measurements.'}
        save(project / 'production/visual-config.json', config)
        spec_path = project / 'production/section-plan.json'; spec = read(spec_path)
        for s in spec:
            s.update(kind='unity' if native else 'diagram', unityStage=stages[s['id']])
            if not native: s['diagramType'] = recipe['diagramType']
            if slug.endswith('square-path-grid') and s['id'] == 'game':
                s['purpose'] = 'Source890–897s diagonal bridge, full1920x1080 frame retained. Original recorder branding/top-right sponsor mark, facecam and UI are preserved. No cropped or erased attribution.'
            if slug.endswith('square-path-grid') and s['id'] == 'result':
                s['purpose'] = 'Close on same fine-grid diagram and staircase boundary. The only7s verified actual interval already appeared in the opening and is not repeated.'
        save(spec_path, spec)
        name = slug + '-' + REVISION
        code = [BATCH / 'prepare-visual.py', BATCH / 'render-one.cjs', BATCH / 'prepare-mc-entries.py']
        code += list(mc.glob('*.ts*')) + list((mc / 'entries' / slug).glob('*.ts'))
        if native: code += [BATCH / 'capture-unity.py'] + [p for p in (BATCH / 'unity-source').rglob('*') if p.is_file()]
        pipeline = {'revision': REVISION, 'usesUnity': native,
          'rendererReason': 'Native Unity behavior with stateful workers/soldiers.' if native else 'Actual square-grid resampling and path-boundary model, best shown directly in2D.',
          'prepareCommand': ['{PYTHON}', '-B', '-X', 'utf8', '{ROOT}/production/batches/tech-ten-shorts-20261030/prepare-visual.py', '{SLUG}'],
          'renderCommand': ['node', '{ROOT}/production/batches/tech-ten-shorts-20261030/render-one.cjs', '{SLUG}', name, '0', '{FRAMES}'],
          'visualOutput': '{LOCAL}/motion-canvas-output/' + name + '.mp4', 'renderReceipt': '{LOCAL}/' + name + '-render.json',
          'codePaths': sorted(set(p.relative_to(ROOT).as_posix() for p in code))}
        if native: pipeline.update(nativeCaptureCommand=['{PYTHON}', '-B', '-X', 'utf8', '{ROOT}/production/batches/tech-ten-shorts-20261030/capture-unity.py', '{SLUG}'], nativeCaptureReceipt='{LOCAL}/unity-capture/native-receipt.json')
        save(project / 'production/visual-pipeline.json', pipeline)
        pp = project / 'planning/production-plan.json'; plan = read(pp)
        plan.update(rightsAndFhdReady=True, sourceFileAndDecodedDimensionsVerified=True, finalWholeMotionAndListening='pending',
                    renderer={'selected': 'Unity' if native else 'Motion Canvas', 'compositor': 'Motion Canvas',
                              'source': 'production/batches/tech-ten-shorts-20261030/unity-source' if native else mc.relative_to(ROOT).as_posix(),
                              'nativeUnityClaimed': native, 'nativeLatestCodePreflight': 'pending-after-user-game-exit' if native else 'not-required'},
                    captionEditNote='Caption clauses split at natural phrases without changing complete spoken paragraphs. Display-only numerals preserve exact spoken values.',
                    productionReady=False if native else True)
        if slug.endswith('square-path-grid'):
            plan['sourceCropDecision'] = {'choice': 'full-original-frame', 'reason': 'Inspected dense source frames show top-right recorder/sponsor mark and facecam. Preserve complete original frame and aspect; do not remove branding with suggested crop.', 'sourceIntervalOriginalSeconds': [890, 897], 'repeatSource': False}
        save(pp, plan)
        print('Configured ' + slug + ('; native preflight pending.' if native else '; purpose-built MC model.'))


if __name__ == '__main__': main()
