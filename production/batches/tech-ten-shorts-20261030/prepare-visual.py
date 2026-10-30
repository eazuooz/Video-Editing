"""Build exact PCM-aligned timeline and extract inspected native-speed game cuts.

This helper does not draft a script or invent a source interval. Every adopted
cut comes from the selected project's visual config and verified source record.
"""
from pathlib import Path
import argparse
import json
import math
import subprocess

from scoped_context import ROOT, REVISION, make_context, read, sha


def immutable(path, value):
    path = Path(path); text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if path.exists():
        if read(path) != value: raise RuntimeError('Preserve previous differing timeline/receipt: ' + str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding='utf8')


def run(command):
    process = subprocess.run(command, cwd=ROOT, capture_output=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if process.returncode: raise RuntimeError(process.stderr.decode(errors='replace')[-5000:])
    return process.stdout


def source_inventory(ctx, config, source_doc):
    sources = source_doc.get('sources')
    if isinstance(sources, list): sources = {r['id']: r for r in sources}
    if not isinstance(sources, dict): raise RuntimeError('selected-footage.json needs sources keyed by explicit source ID.')
    adopted = {cut.get('source', 'game-master') for group in config.get('cuts', {}).values()
               for cut in group.get('sequence', [group])}
    if not adopted: raise RuntimeError('At least one inspected independent actual-game cut is required.')
    result = {}
    for key in sorted(adopted):
        source = dict(sources[key]); path = Path(source['path']); path = path if path.is_absolute() else ROOT / path
        if not ctx['media_allowed'](path) or not path.is_file() or source.get('sourceSHA256') != sha(path):
            raise RuntimeError('Source path/hash changed or outside authorized media: ' + key)
        probe = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))
        video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        if video['width'] < 1920 or video['height'] < 1080: raise RuntimeError('Use independently decoded native FHD or higher: ' + key)
        source.update(path=ctx['media_reference'](path), decodedWidth=video['width'], decodedHeight=video['height'],
                      decodedDurationSeconds=float(probe['format']['duration']))
        result[key] = source
    return result


def cue_event(cues, ids):
    rows = [c for c in cues if any(c['id'] == key or (c['id'].startswith(key) and c['id'][len(key):].isalpha()) for key in ids)]
    if not rows or not all(any(c['id'] == key for c in rows) for key in ids): raise RuntimeError('Unknown actual cue event: ' + repr(ids))
    return {'startFrame': min(c['startFrame'] for c in rows), 'endFrame': max(c['endFrame'] for c in rows), 'cueIds': [c['id'] for c in rows]}


def annotation_geometry(keyframes, at):
    """Interpolate within inspected source keyframes; never extrapolate a target."""
    if not keyframes[0]['at'] <= at <= keyframes[-1]['at']:
        raise RuntimeError('Source annotation needs observed keyframes covering its full interval.')
    previous = keyframes[0]
    for following in keyframes[1:]:
        if at < following['at']:
            fraction = (at - previous['at']) / (following['at'] - previous['at'])
            result = {'at': at, 'center': [a + (b - a) * fraction for a, b in zip(previous['center'], following['center'])],
                    'size': [a + (b - a) * fraction for a, b in zip(previous['size'], following['size'])],
                    'visible': previous.get('visible', True)}
            if 'labelCenter' in previous and 'labelCenter' in following:
                result['labelCenter'] = [a + (b - a) * fraction for a, b in zip(previous['labelCenter'], following['labelCenter'])]
            return result
        previous = following
    return {**previous, 'at': at, 'visible': previous.get('visible', True)}


def remap_source_annotations(sections, config, sources):
    """Intersect source-local inspected marks with each actual cut, clearing at cuts.

    sourceAnnotations[sourceId] uses decoded-source pixels and file-local seconds.
    A keyframe with visible:false hides the target until the next visible keyframe.
    Source/file bounds and any display crop are checked again by the compositor.
    """
    result = {key: list(value) for key, value in config.get('annotations', {}).items()}
    for source_id, marks in config.get('sourceAnnotations', {}).items():
        if source_id not in sources: raise RuntimeError('Annotation source is not an adopted inspected source: ' + source_id)
        source = sources[source_id]
        for mark_index, mark in enumerate(marks):
            start, end = mark['start'], mark['end']; keys = mark['keyframes']
            if not (isinstance(start, (int, float)) and isinstance(end, (int, float)) and
                    math.isfinite(start) and math.isfinite(end) and 0 <= start < end <= source['decodedDurationSeconds']):
                raise RuntimeError('Invalid source annotation interval: ' + source_id)
            if len(keys) < 2 or mark.get('kind', 'box') not in {'box', 'ellipse', 'arrow'} or not mark.get('label'):
                raise RuntimeError('Inspected marks require a label, supported shape and covering keyframes.')
            labels = [key['labelCenter'] for key in keys if 'labelCenter' in key]
            if labels and len(labels) != len(keys): raise RuntimeError('Animated label positions need every inspected keyframe.')
            if 'labelCenter' in mark: labels.append(mark['labelCenter'])
            if any(len(label) != 2 or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in label) for label in labels):
                raise RuntimeError('Label center must be finite decoded-source pixels.')
            for i, key in enumerate(keys):
                values = [key.get('at')] + list(key.get('center', [])) + list(key.get('size', []))
                if len(values) != 5 or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
                    raise RuntimeError('Annotation geometry must be finite source pixels.')
                if i and key['at'] <= keys[i - 1]['at']: raise RuntimeError('Source keyframes must be strictly increasing.')
                if mark.get('kind', 'box') != 'arrow' and min(key['size']) <= 0: raise RuntimeError('Hollow shapes need positive size.')
                if 'visible' in key and not isinstance(key['visible'], bool): raise RuntimeError('Visibility must be explicit boolean.')
            if keys[0]['at'] > start or keys[-1]['at'] < end:
                raise RuntimeError('Do not extrapolate beyond inspected annotation keyframes.')
            for section in sections:
                if section['kind'] != 'game' or section['source'] != source_id: continue
                left, right = max(start, section['sourceStart']), min(end, section['sourceEnd'])
                if right <= left: continue
                clipped = [annotation_geometry(keys, left)] + [dict(k) for k in keys if left < k['at'] < right] + [annotation_geometry(keys, right)]
                for key in clipped: key['at'] -= section['sourceStart']
                mapped = {k: v for k, v in mark.items() if k not in {'start', 'end', 'keyframes'}}
                mapped.update(start=left - section['sourceStart'], end=right - section['sourceStart'], keyframes=clipped,
                    sourceProvenance={'source': source_id, 'sourceSHA256': source['sourceSHA256'], 'annotationIndex': mark_index,
                                      'sourceStart': left, 'sourceEnd': right, 'timeBasis': 'file-local-seconds',
                                      'geometryBasis': 'decoded-source-pixels', 'interpolation': 'linear-between-inspected-keyframes'})
                result.setdefault(section['id'], []).append(mapped)
    return result


def apply_native_sequences(sections, config):
    """Continue the absolute-time boat simulation across a spoken paragraph join.

    This carries its analytic wave/flood clock, not arbitrary stateful scene data.
    Unconfigured sections retain the existing zero-based sampling behavior.
    """
    sequences = config.get('nativeSequences', {})
    if not sequences: return
    if config.get('slug') != 'shorts-sea-of-thieves-water-masking':
        raise RuntimeError('Native elapsed continuity is currently verified only for the analytic boat scene.')
    if not isinstance(sequences, dict): raise RuntimeError('nativeSequences must map exact section IDs.')
    indices = {row['id']: index for index, row in enumerate(sections)}
    if len(indices) != len(sections): raise RuntimeError('Native continuity requires unique section IDs.')
    if set(sequences) - set(indices): raise RuntimeError('Native continuity names an absent destination section.')
    for index, row in enumerate(sections):
        if row['id'] not in sequences: continue
        instruction = sequences[row['id']]
        if not isinstance(instruction, dict) or set(instruction) != {'inheritFrom'}:
            raise RuntimeError('Native continuity requires only an explicit inheritFrom section ID.')
        source_id = instruction['inheritFrom']
        if index == 0 or indices.get(source_id) != index - 1:
            raise RuntimeError('Native continuity must inherit the immediately preceding section.')
        source = sections[index - 1]
        if (source['kind'] != 'unity' or row['kind'] != 'unity' or
                source['endFrame'] != row['startFrame'] or source['unityStage'] != row['unityStage']):
            raise RuntimeError('Native continuity requires adjacent Unity sections of the same saved stage.')
        if row['id'] in config.get('nativeActionCues', {}) or row.get('actionKind'):
            raise RuntimeError('Inherited native sequence cannot also reset its own action cue.')
        offset = (row['startFrame'] - source['startFrame']) / 60 + source.get('elapsedOffsetSeconds', 0)
        if not math.isfinite(offset) or offset <= 0:
            raise RuntimeError('Native continuity offset must be finite and strictly positive.')
        row.update(elapsedOffsetSeconds=offset, nativeSequenceInheritFrom=source_id)
        for key in ('actionKind', 'actionStartSeconds', 'actionCueId', 'actionResumeSeconds', 'actionResumeCueId'):
            if key in source: row[key] = source[key]


def build(ctx, spec, config, sources, captions, pcm):
    lines = [x for s in read(ctx['P'] / 'script/narration.spoken.ko.json')['scenes'] for x in s['lines']]
    entries = {e['lineIndex']: e for e in pcm['entries'] if e['scene_id'] == 'main'}
    if len(spec) != len(lines) or sorted(entries) != list(range(len(lines))):
        raise RuntimeError('Current helper needs one ordered section-plan item per complete paragraph.')
    if captions['timingInputs']['voiceSha256'] != sha(ctx['VOICE']) or captions['fps'] != 60:
        raise RuntimeError('Use measured captions from this exact current PCM.')
    if captions['frames'] != math.ceil((pcm['duration_seconds'] + .2 + .4) * 60 - 1e-8):
        raise RuntimeError('Do not stretch or pad the current narration to a target duration.')
    normalize = lambda text: ''.join(text.split())
    for i, line in enumerate(lines):
        if normalize(entries[i]['text']) != normalize(line): raise RuntimeError('Actual paragraph text changed.')
    by_id = {c['id']: c for c in captions['cues']}
    boundaries = [0] + [math.floor((entries[i]['start'] + .2) * 60 + .5) for i in range(1, len(lines))] + [captions['frames']]
    sections = []; fallback_kind = config.get('defaultExplanationKind', 'unity')
    if fallback_kind not in {'unity', 'diagram'}: raise RuntimeError('Choose an explicit explanation renderer.')
    for i, item in enumerate(spec):
        if item['paragraph'] != i or by_id[item['firstCue']]['lineIndex'] != i:
            raise RuntimeError('Section mapping differs from actual narration.')
        start, end = boundaries[i], boundaries[i + 1]
        if start >= end: raise RuntimeError('Nonpositive actual paragraph interval.')
        base = {**item, 'unityStage': item.get('unityStage', min(i, 2)), 'pcmParagraphStart': entries[i]['start'] + .2,
                'pcmParagraphEnd': entries[i]['end'] + .2}
        group = config.get('cuts', {}).get(item['id'])
        if group:
          cursor = start
          sequence = group.get('sequence', [group])
          for cut_index, cut in enumerate(sequence):
            game_start = max(cursor, by_id[cut['fromCue']]['startFrame']) if cut.get('fromCue') else cursor
            if game_start >= end: raise RuntimeError('Selected actual-game start is outside its paragraph.')
            if game_start > cursor:
                sections.append({**base, 'id': item['id'] + '-before-' + str(cut_index + 1), 'kind': item.get('fallbackKind', fallback_kind),
                                 'startFrame': cursor, 'endFrame': game_start})
            source_id = cut.get('source', 'game-master'); source = sources[source_id]
            game_end = min(end, game_start + math.floor(float(cut['maxDuration']) * 60 + 1e-8))
            if cut.get('untilCue'): game_end = min(game_end, by_id[cut['untilCue']]['startFrame'])
            if game_end <= game_start: raise RuntimeError('Selected source cut supplies no actual frame.')
            source_start = float(cut['in']); source_end = source_start + (game_end - game_start) / 60
            if not 0 <= source_start < source_end <= source['decodedDurationSeconds'] + 1e-7:
                raise RuntimeError('Inspected cut exceeds original source duration.')
            section_id = item['id'] if len(sequence) == 1 else item['id'] + '-game-' + str(cut_index + 1)
            folder = ctx['LOCAL'].resolve() / 'frames' / section_id
            row = {**base, 'id': section_id, 'kind': 'game', 'startFrame': game_start, 'endFrame': game_end,
                   'source': source_id, 'sourceStart': source_start, 'sourceEnd': source_end,
                   'sourceTimeBasis': 'clip-relative', 'rate': 1,
                   'nativeAudioAdopted': cut.get('nativeAudioAdopted', source.get('nativeAudioAdopted', False)),
                   'frameDirectory': '/@fs/' + folder.as_posix(), 'firstFrame': 0, 'digits': 6,
                   'framePattern': '{frame}.jpg', 'width': source['decodedWidth'], 'height': source['decodedHeight']}
            if cut.get('crop'): row['crop'] = cut['crop']
            sections.append(row)
            cursor = game_end
          if cursor < end:
                sections.append({**base, 'id': item['id'] + '-explain', 'kind': item.get('fallbackKind', fallback_kind),
                                 'startFrame': cursor, 'endFrame': end,
                                 'continuity': 'Same paragraph continues with its mechanism; no loop, slowdown or frozen source padding.'})
        else:
            kind = item.get('kind', fallback_kind)
            if kind == 'game': raise RuntimeError('Actual-game section lacks an inspected config cut.')
            sections.append({**base, 'kind': kind, 'startFrame': start, 'endFrame': end})
    for row in sections:
        row.update(start=row['startFrame'] / 60, end=row['endFrame'] / 60)
        row['cueIds'] = [c['id'] for c in captions['cues'] if c['startFrame'] < row['endFrame'] and c['endFrame'] > row['startFrame']]
        if row['kind'] == 'unity':
            row.update(frameDirectory='/@fs/' + (ctx['LOCAL'].resolve() / 'unity-capture' / row['id']).as_posix(),
                       firstFrame=0, digits=5, framePattern='{frame}.jpg', width=1080, height=1080)
            action = config.get('nativeActionCues', {}).get(row['id'])
            if action:
                cue = by_id[action['cueId']]
                if not row['startFrame'] <= cue['startFrame'] < row['endFrame']:
                    raise RuntimeError('Native action cue is outside its actual Unity section: ' + row['id'])
                row.update(actionKind=action['kind'], actionStartSeconds=(cue['startFrame'] - row['startFrame']) / 60,
                           actionCueId=action['cueId'])
                if action.get('resumeCueId'):
                    resume = by_id[action['resumeCueId']]
                    if not cue['startFrame'] < resume['startFrame'] < row['endFrame']:
                        raise RuntimeError('Native resume cue must follow its action inside the same section.')
                    row.update(actionResumeSeconds=(resume['startFrame'] - row['startFrame']) / 60,
                               actionResumeCueId=action['resumeCueId'])
        elif row['kind'] == 'diagram':
            row['diagramType'] = row.get('diagramType', config.get('diagramType'))
            if row['diagramType'] not in {'grid', 'eud', 'replay'}: raise RuntimeError('Select the authored diagram mechanism.')
    apply_native_sequences(sections, config)
    if sections[0]['kind'] != 'game': raise RuntimeError('Open with actual independent gameplay.')
    events = {name: cue_event(captions['cues'], ids) for name, ids in config.get('speechEvents', {}).items()}
    if config.get('definitionCue'):
        definition = cue_event(captions['cues'], [config['definitionCue']])
        definition['endFrame'] = min(captions['frames'], definition['startFrame'] + round(config.get('definitionDurationSeconds', 4.5) * 60))
        events['term-definition'] = definition
    reactions = []
    for reaction in config.get('reactionCues', []):
        event = cue_event(captions['cues'], [reaction['cueId']]); start = event['startFrame'] / 60
        reactions.append({'start': start, 'end': min(captions['frames'] / 60, start + float(reaction.get('durationSeconds', 2.4))),
                          'kind': reaction['kind']})
    if not reactions: raise RuntimeError('Author purposeful cat reaction cue IDs; do not insert arbitrary timed reactions.')
    return {'revision': REVISION, 'previewOnly': False, 'fps': 60, 'frames': captions['frames'],
            'durationSeconds': captions['durationSeconds'], 'voiceOffsetSeconds': .2,
            'timingInputs': captions['timingInputs'], 'sources': sources, 'sections': sections,
            'events': events, 'reactions': reactions,
            'annotations': remap_source_annotations(sections, config, sources),
            'actualGameSeconds': sum(s['end'] - s['start'] for s in sections if s['kind'] == 'game'),
            'sourceSpeed': 1, 'nativeUnityFootageClaimedOnlyForUnitySections': True}


def extract(ctx, timing):
    receipt_dir = ctx['LOCAL'] / 'frame-extraction'; receipt_dir.mkdir(parents=True, exist_ok=True)
    for row in timing['sections']:
        if row['kind'] != 'game': continue
        source = timing['sources'][row['source']]; source_path = Path(source['path']); source_path = source_path if source_path.is_absolute() else ROOT / source_path
        directory = ctx['LOCAL'] / 'frames' / row['id']; receipt = receipt_dir / (row['id'] + '.json')
        count = row['endFrame'] - row['startFrame']
        request = {'sourceSHA256': source['sourceSHA256'], 'sourceStart': row['sourceStart'], 'frames': count, 'fps': 60, 'width': row['width'], 'height': row['height']}
        if receipt.exists():
            prior = read(receipt)
            if prior['request'] != request: raise RuntimeError('Preserve old inspected frame extraction: ' + row['id'])
            for entry in prior['artifacts']:
                path = Path(entry['path'])
                if not path.exists() or sha(path) != entry['sha256']: raise RuntimeError('Stored source frame changed: ' + str(path))
            continue
        if directory.exists() and any(directory.iterdir()): raise RuntimeError('Incomplete prior frame directory preserved: ' + str(directory))
        ctx['assert_no_game_apps'](); directory.mkdir(parents=True, exist_ok=True)
        run(['ffmpeg', '-v', 'error', '-n', '-ss', str(row['sourceStart']), '-i', str(source_path),
             '-an', '-vf', 'fps=60', '-frames:v', str(count), '-q:v', '2', '-start_number', '0', str(directory / '%06d.jpg')])
        files = sorted(directory.glob('*.jpg'))
        if len(files) != count: raise RuntimeError('Actual source extraction is shorter than selected timeline.')
        artifacts = [{'path': str(p.resolve()), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in files]
        immutable(receipt, {'request': request, 'artifacts': artifacts})


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('slug'); parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args(); ctx = make_context(args.slug); ctx['guard'](); ctx['assert_no_game_apps']()
    project = ctx['P']; config = read(project / 'production/visual-config.json')
    sources = source_inventory(ctx, config, read(project / 'sources/selected-footage.json'))
    timing = build(ctx, read(project / 'production/section-plan.json'), config, sources,
                   read(project / 'script/captions.json'), read(ctx['L'] / 'voice/narration.timing.json'))
    immutable(project / 'production/visual-timing.json', timing); immutable(ctx['LOCAL'] / 'visual-timing.json', timing)
    if not args.plan_only: extract(ctx, timing)
    print(json.dumps({'slug': args.slug, 'frames': timing['frames'], 'sections': len(timing['sections']), 'planOnly': args.plan_only}, ensure_ascii=False))


if __name__ == '__main__': main()
