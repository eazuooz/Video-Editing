"""Combine current measured diagrams and reviewed source marks; author safe header guides.

No media jobs, audio changes or platform mutations. Existing input plans remain intact.
Run after build-annotations.py; the final plan references the same measured audio clock.
"""
from pathlib import Path
import copy
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audio_pipeline as audio
import video_pipeline as video
from storage_paths import relative

ROOT = HERE.parents[3]
LOCAL = ROOT / 'projects/similar-game-design/production/local/reference-preserving-v2'


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def artifact(path):
    return {'path': relative(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path, value):
    content = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    if path.exists() and path.read_bytes() != content:
        raise ValueError(f'Preserved incompatible output: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def clock(t):
    cs = round(t * 100)
    return f'{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}'


def main():
    audio.require_authorized('current final visual plan and header authoring')
    diagrams = HERE / 'edit-plan-diagram-v3.json'
    annotation_file = HERE / 'edit-plan-annotated.json'
    plan, annotated = read(diagrams), read(annotation_file)
    assert audio.audio_plan_contract(plan) == audio.audio_plan_contract(annotated)
    assert [c['id'] for c in plan['cuts']] == [c['id'] for c in annotated['cuts']]
    actual = {c['id']: c for c in annotated['cuts'] if c['kind'] == 'independent-gameplay'}
    for i, cut in enumerate(plan['cuts']):
        if cut['kind'] == 'independent-gameplay':
            replacement = copy.deepcopy(actual[cut['id']])
            for key in ('startFrame', 'endFrame', 'frames', 'sourceFile', 'sourceStart', 'sourceSha256'):
                assert cut[key] == replacement[key], (cut['id'], key)
            assert replacement['viewport'] == [224, 52, 1472, 828]
            plan['cuts'][i] = replacement
    spec = {
        'project': 'similar-game-design', 'revision': 'reference-preserving-v2',
        'meaning': 'Canonical game name and actual-picture kind in reserved black header; separate source-shot label where native timer jumps.',
        'viewport': [224, 52, 1472, 828], 'header': [0, 0, 1920, 50],
        'font': 'Malgun Gothic', 'gameNameFontSize': 40, 'pictureKindFontSize': 32,
        'names': {'Deep Rock Galactic: Survivor': 'Deep Rock Galactic: Survivor', 'Super Mario Maker 2': 'Super Mario Maker 2'},
        'sourceUrlsOrCreditsDrawn': False, 'detectorOrMeasuredGameData': False,
        'whyFramed': 'Preserve the entire16:9 source and bottom HUD above fixed-caption y892; header labels never cover gameplay.',
    }
    spec_file = HERE / 'editorial-guides-spec.json'
    save(spec_file, spec)
    refs = [artifact(ROOT / 'shared/output/narration/similar-game-design/reference-preserving-v2/whole-source-asr.json'),
            artifact(LOCAL / 'edit/captions.json'),
            artifact(ROOT / 'projects/similar-game-design/sources/footage-options-v2.json')]
    header = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Game,Malgun Gothic,40,&H0083CFE8,&H0083CFE8,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Kind,Malgun Gothic,32,&H00B5B5B5,&H00B5B5B5,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    for cut in plan['cuts']:
        if cut['kind'] != 'independent-gameplay':
            continue
        cut['gameTitleChipPending'] = False
        cut['gameTitleChipLayout'] = 'Reserved header above entire16:9 gameplay; no game UI or caption overlap.'
        end = cut['frames'] / 60
        kind = cut.get('editorialTransitionLabel') or '실제 게임 화면'
        content = header
        content += f'Dialogue: 4,0:00:00.00,{clock(end)},Game,,0,0,0,,{{\\an7\\pos(224,0)}}{cut["game"]}\n'
        content += f'Dialogue: 4,0:00:00.00,{clock(end)},Kind,,0,0,0,,{{\\an7\\pos(1435,5)}}{kind}\n'
        file = LOCAL / f'edit/editorial-guides/{cut["id"]}.ass'
        file.parent.mkdir(parents=True, exist_ok=True)
        if file.exists() and file.read_text('utf-8-sig') != content:
            raise ValueError(f'Preserve changed existing guide: {file}')
        file.write_bytes(content.encode())
        events = [{'start': 0, 'end': end, 'globalStart': cut['startFrame'] / 60,
                   'globalEnd': cut['endFrame'] / 60, 'bounds': [224, 0, 1335, 50],
                   'text': cut['game'], 'meaning': 'Canonical game identification'},
                  {'start': 0, 'end': end, 'globalStart': cut['startFrame'] / 60,
                   'globalEnd': cut['endFrame'] / 60, 'bounds': [1435, 0, 1880, 50],
                   'text': kind, 'meaning': 'Actual recording or truthful separate native shot'}]
        cut['editorialGuideAss'] = {**artifact(file), 'cutBindingSha256': video.editorial_guide_binding(cut, plan),
            'guideSpec': artifact(spec_file), 'mappingInputs': refs, 'clock': 'cut-relative-seconds',
            'coordinateSystem': 'output1920x1080', 'detectorOutput': False, 'measuredGameData': False,
            'appliesTo': ['clean', 'captioned'], 'events': events}
        video.editorial_guide_ass(cut, plan)
        checked = {**cut, 'protectedRects': [*cut.get('protectedRects', []), *[x['bounds'] for x in events]]}
        video.annotations(checked, plan)
    plan.update(status='current-final-visual-plan-ready-to-render',
                gameTitleChipLayout='Reserved header, no gameplay UI covered; source framing1472x828 inside1920x1080.',
                finalVisualInputs={'diagrams': artifact(diagrams), 'annotations': artifact(annotation_file), 'guides': artifact(spec_file)},
                annotationReview='Hash-bound native sampled tracks, output mapping and header/caption geometry checked; actual moving final pixels pending.')
    assert audio.audio_plan_contract(plan) == audio.audio_plan_contract(read(diagrams))
    video.validate_plan(plan)
    save(HERE / 'edit-plan-final.json', plan)
    print(json.dumps({'cuts': len(plan['cuts']), 'guides': len(actual), 'frames': plan['totalFrames'], 'audioChanged': False, 'movingPixels': 'pending'}))


if __name__ == '__main__':
    main()
