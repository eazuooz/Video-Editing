"""Bind audited Alyx/Sea of Thieves records. Does not mark a held source ready."""
from pathlib import Path
import json
from scoped_context import BATCH, ROOT, REVISION, read, sha


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    audit_path = BATCH / 'preproduction/first-five.json'; audit = read(audit_path)
    topics = ['alyx-liquid-shader', 'sea-of-thieves-water-masking']
    rows = next(value for value in audit.values() if isinstance(value, list) and value and isinstance(value[0], dict) and value[0].get('id') == 'alyx-liquid-shader')
    for topic in topics:
        source = next(item for item in rows if item['id'] == topic)
        slug = 'shorts-' + topic; project = ROOT / 'projects' / slug; plan_path = project / 'planning/production-plan.json'; plan = read(plan_path)
        selected = {'schemaVersion': 1, 'revision': REVISION, 'sourceAudit': audit_path.relative_to(ROOT).as_posix(),
            'sourceAuditSHA256': sha(audit_path), 'sources': {'game-master': {
                'path': source['localFile'], 'sourceSHA256': source['sha256'], 'originalOffsetSeconds': source['decoded']['sourceInterval'][0],
                'sourceUrl': source['sourceUrl'], 'sourceTitle': source['sourceTitle'], 'author': source['author'],
                'recordingLicense': source['recordingLicense'], 'publisherPolicy': audit['rights'][source['publisherPolicy']],
                'decoded': source['decoded'], 'viewingScope': audit['reviewScope']['method'],
                'fullRealtimePlayback': False, 'sourceAudioAdopted': False, 'nativeAudioAdopted': False,
                'audioExclusionReason': 'Video-only source; third-party soundtrack and voices not adopted.',
                'observedBeforeActionResult': source['observed'], 'claimLimits': source['claimLimit'],
                'inspectedIntervalsOriginalSeconds': source['proposedSourceCuts'],
                'publicPublishingCheck': 'Confirm exact recorder CC BY license URL and all description attribution before a separate publishing request.'}}}
        save(project / 'sources/selected-footage.json', selected)
        if topic.startswith('alyx'):
            # Root and source reviewer explicitly held the visible-liquid fit.
            plan['productionSourceFitStatus'] = 'held: liquid interface needs clear actual motion evidence'
            plan['scriptFinalized'] = False
            plan['rightsAndFhdReady'] = True
            save(plan_path, plan)
            continue
        clauses_path = project / 'script/caption-clauses.json'; clauses = read(clauses_path)
        if not any(c['id'] == 'p1-1b' for c in clauses['clauses']):
            first = clauses['clauses'][0]
            if first['id'] != 'p1-1' or first['spoken'] != '바다는 이렇게 높은데, 배 안의 물은 따로 고여 있죠.':
                raise RuntimeError('Preserve edited first-clause text; inspect before splitting.')
            clauses['clauses'][:1] = [
                {'id': 'p1-1', 'lineIndex': 0, 'spoken': '바다는 이렇게 높은데,', 'ko': '바다는 이렇게 높은데,', 'en': 'The waves are this high,'},
                {'id': 'p1-1b', 'lineIndex': 0, 'spoken': '배 안의 물은 따로 고여 있죠.', 'ko': '배 안의 물은\n따로 고여 있죠.',
                 'en': 'but water inside the ship collects separately.', 'emphasis': {'text': '따로', 'role': 'result'}}]
            save(clauses_path, clauses)
        stages = {'game': 1, 'unmasked': 0, 'mask': 1, 'compare': 1, 'flood': 2, 'result': 2}
        spec_path = project / 'production/section-plan.json'; spec = read(spec_path)
        for section in spec:
            section.update(unityStage=stages[section['id']], kind='unity')
        save(spec_path, spec)
        config = {'slug': slug, 'game': 'Sea of Thieves', 'head': ['배 안으로 들어온 바다', '화면에서 지워 버린다'],
            'term': '물 표면 마스킹', 'english': 'Water Masking', 'plainMeaning': '바다를 그리지 않을 영역을 지정',
            'frameRoot': '/@fs/' + str((project / 'production/local/frames').resolve()).replace('\\', '/'),
            'defaultExplanationKind': 'unity', 'definitionCue': 'p4-1', 'definitionDurationSeconds': 4.2,
            'cuts': {
                'game': {'sequence': [
                    {'source': 'game-master', 'in': 120, 'maxDuration': 6, 'untilCue': 'p1-1b', 'nativeAudioAdopted': False},
                    {'source': 'game-master', 'in': 127, 'maxDuration': 10, 'fromCue': 'p1-1b', 'nativeAudioAdopted': False}]},
                'result': {'sequence': [
                    {'source': 'game-master', 'in': 130, 'maxDuration': 7, 'untilCue': 'p6-2', 'nativeAudioAdopted': False},
                    {'source': 'game-master', 'in': 138, 'maxDuration': 6, 'fromCue': 'p6-2', 'nativeAudioAdopted': False}]}},
            'annotations': {},
            'reactionCues': [{'cueId': 'p3-2', 'kind': 'realize', 'durationSeconds': 2.6}, {'cueId': 'p6-2', 'kind': 'relief', 'durationSeconds': 2.6}],
            'speechEvents': {'unmasked:ocean-crosses-hull': ['p2-2'], 'mask:mask-reveal': ['p3-1'],
                'mask:clip-ocean': ['p3-2'], 'compare:mask-compare': ['p4-2'], 'flood:interior-water-rise': ['p5-2']},
            'annotationStatus': 'Actual source motion/keyframe verification still required before complete visual QA; do not invent tracked geometry.'}
        save(project / 'production/visual-config.json', config)
        name = slug + '-tech-ten-v1'
        shared_code = [p.relative_to(ROOT).as_posix() for p in BATCH.glob('*.py')]
        shared_code += [(BATCH / 'render-one.cjs').relative_to(ROOT).as_posix()]
        shared_code += [p.relative_to(ROOT).as_posix() for p in (BATCH / 'unity-source').rglob('*') if p.is_file()]
        shared_code += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'motion-canvas/src/projects/tech-ten-shorts-20261030').glob('*.ts*')]
        shared_code += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'motion-canvas/src/projects/tech-ten-shorts-20261030/entries' / slug).glob('*.ts')]
        pipeline = {'revision': REVISION, 'usesUnity': True,
            'prepareCommand': ['{PYTHON}', '-B', '-X', 'utf8', '{ROOT}/production/batches/tech-ten-shorts-20261030/prepare-visual.py', '{SLUG}'],
            'nativeCaptureCommand': ['{PYTHON}', '-B', '-X', 'utf8', '{ROOT}/production/batches/tech-ten-shorts-20261030/capture-unity.py', '{SLUG}'],
            'nativeCaptureReceipt': '{LOCAL}/unity-capture/native-receipt.json',
            'renderCommand': ['node', '{ROOT}/production/batches/tech-ten-shorts-20261030/render-one.cjs', '{SLUG}', name, '0', '{FRAMES}'],
            'visualOutput': '{LOCAL}/motion-canvas-output/' + name + '.mp4', 'renderReceipt': '{LOCAL}/' + name + '-render.json',
            'codePaths': sorted(set(shared_code))}
        save(project / 'production/visual-pipeline.json', pipeline)
        plan.update(rightsAndFhdReady=True, sourceFileAndDecodedDimensionsVerified=True,
            productionSourceFitStatus='sampled moving sequence supports exterior waves and distinct interior flood; full real-time review pending',
            renderer={'default': 'Unity', 'sceneSource': 'production/batches/tech-ten-shorts-20261030/unity-source',
                'captureProject': 'C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030/unity-capture',
                'frameDimensions': [1080, 1080], 'fps': 60, 'compositor': 'Motion Canvas'},
            captionEditNote='Split p1-1 at the existing comma into p1-1/p1-1b to bind exterior/interior shots to actual speech. Whole narration unchanged.',
            finalWholeMotionAndListening='pending')
        save(plan_path, plan)
        print('Prepared audited source/config/pipeline for ' + slug + '; readiness not automatically asserted.')


if __name__ == '__main__': main()
