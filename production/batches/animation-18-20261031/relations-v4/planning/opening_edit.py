"""Reusable frame/sample EDL for narrated maps and relocated observation sets.

Only planning metadata is read by make_edit().  Media is written solely when the
caller explicitly invokes reconstruct_pcm().  No production master is changed.

Typical use from relations-v4/assemble.py::

    edit = make_edit(id, oldFrames, tm['frames'], repairs, O/'relation.mp4')
    for part in edit['pictureEdl']:
        # Encode part['source'] at part['sourceStartFrame'] for part['frames'].
        # native-pass parts additionally expose passIndex/passTotal for labels.
        ...
    proof = reconstruct_pcm(edit, old, Path(tm['audio']), O/'mix.wav')
    addition = new_cues(ep, tm, edit['mapStartSeconds'])
    shifted = retime_cues(oldcaptions[lang], edit)
    ass = retime_ass(old_ass_text, edit).splitlines()
    allFrames = edit['totalFrames']

Caption additions are already positioned at mapStartSeconds and must NOT be
passed through retime_cues again. Body repairs remain in old-master coordinates.
"""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BATCH_REL = Path('production/batches/animation-18-20261031')
FPS, RATE, SPF = 60, 48000, 800


def _read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def _sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _seconds(value):
    h, m, s = value.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def _stamp(t, srt=False):
    scale = 1000 if srt else 100
    n = round(t * scale)
    sec, fraction = divmod(n, scale)
    h, sec = divmod(sec, 3600)
    m, sec = divmod(sec, 60)
    return f'{h:02d}:{m:02d}:{sec:02d},{fraction:03d}' if srt else f'{h}:{m:02d}:{sec:02d}.{fraction:02d}'


def read_cues(path):
    result = []
    for block in re.split(r'\n\s*\n', Path(path).read_text('utf-8-sig').strip()):
        lines = block.splitlines()
        start, end = map(_seconds, lines[1].split(' --> '))
        result.append({'start': start, 'end': end, 'text': '\n'.join(lines[2:])})
    return result


def _current_event_coordinates(events):
    picture, audio, shift = {}, {}, 0
    for event in events:
        start = event['pictureAt'] + shift
        picture[event['key']] = [start, start + event['frames']]
        shift += event['frames']
    shift = 0
    for event in sorted(events, key=lambda x: x['audioAt']):
        start = round(event['audioAt'] * SPF) + shift
        audio[event['key']] = [start, start + event['frames'] * SPF]
        shift += event['frames'] * SPF
    return picture, audio


def _check_cues(cues, removals, anchor, tolerance, context):
    rounded_touches = []
    for cue in cues:
        a, b = cue['start'], cue['end']
        if a + tolerance < anchor < b - tolerance:
            raise ValueError(f'{context}: diagram anchor splits spoken caption: {cue}')
        for lo, hi in removals:
            lo, hi = lo / RATE, hi / RATE
            overlap = min(b, hi) - max(a, lo)
            if overlap > tolerance:
                raise ValueError(f'{context}: proposed music removal intersects caption by {overlap:.6f}s: {cue}')
            if overlap > 0:
                rounded_touches.append({'cue': cue['text'], 'overlapSeconds': overlap, 'reason': 'Timestamp rounding only; exact insert provenance is checked separately.'})
    return rounded_touches


def _partition(total, deletions, anchor, insert_parts, replacements=()):
    """Return an EDL in original coordinates, each output interval contiguous."""
    events = [{'start': a, 'end': b, 'kind': 'delete'} for a, b in deletions]
    events += [dict(x, kind='replacement') for x in replacements]
    events.append({'start': anchor, 'end': anchor, 'kind': 'insertion'})
    events.sort(key=lambda x: (x['start'], x['end']))
    output, cursor, dest = [], 0, 0

    def add(part):
        nonlocal dest
        n = part['length']
        if n <= 0:
            return
        output.append(dict(part, outputStart=dest, outputEnd=dest + n))
        dest += n

    for event in events:
        a, b = event['start'], event['end']
        if not 0 <= cursor <= a <= b <= total:
            raise ValueError(f'Overlapping or invalid old-coordinate edit: cursor={cursor}, {event}')
        add({'kind': 'baseline', 'sourceStart': cursor, 'length': a - cursor})
        if event['kind'] == 'insertion':
            for part in insert_parts:
                add(part)
        elif event['kind'] == 'replacement':
            add({'kind': 'repair', 'source': str(event['path']), 'sourceStart': int(event.get('sourceStartFrame', 0)), 'length': b - a})
        cursor = b
    add({'kind': 'baseline', 'sourceStart': cursor, 'length': total - cursor})
    return output


def make_edit(id, old_frames, map_frames, repairs=(), map_path=None, root=ROOT):
    """Build and preflight both EDLs; no media writes, TTS or encoding."""
    root = Path(root).resolve()
    batch = root / BATCH_REL
    planning = batch / 'relations-v4/planning'
    layout_path = planning / 'opening-layout.json'
    relations_path = planning / 'relations-plan.json'
    layout = next(x for x in _read(layout_path)['episodes'] if x['id'] == id)
    ep = next(x for x in _read(relations_path)['episodes'] if x['id'] == id)
    manifest_path = batch / 'pacing-v3/review-manifest.json'
    base = next(x for x in _read(manifest_path)['records'] if x['id'] == id)
    assert old_frames == round(base['durationSeconds'] * FPS)
    assert int(map_frames) == map_frames and map_frames > 0
    map_frames = int(map_frames)
    pacing_path = root / layout['pacingPlan']
    assert _sha(pacing_path) == layout['pacingPlanSha256'], 'Pacing plan changed; regenerate opening-layout first.'
    pacing = _read(pacing_path)
    picture, audio = _current_event_coordinates(pacing['events'])
    pdir = root / 'projects' / ep['slug'] / 'production/local/pacing-v3'
    proof_path = pdir / 'audio-proof.json'
    proof = _read(proof_path)
    if layout['moves']:
        assert proof.get('preservationMode') == 'preserve-final-mix'
    bridges = proof.get('insertedMusicBridges', [])
    at = ep['insertion']['atSeconds']
    anchor_frame, anchor_sample = round(at * FPS), round(at * RATE)
    requested_anchor_sample = anchor_sample
    assert anchor_frame == layout['originalMapAnchorFrame']
    assert anchor_sample == layout['originalMapAnchorSample']
    deletions_p, deletions_a, music_provenance = [], [], []
    native_hashes = {}
    for move in layout['moves']:
        event = next(x for x in pacing['events'] if x['key'] == move['key'])
        assert event['kind'] == 'explanation' and event['speed'] == 1
        assert picture[move['key']] == move['originalPictureRangeFrames']
        assert audio[move['key']] == move['originalMusicOnlyRangeSamples']
        assert event['sourceSHA256'] == move['nativeSourceSha256']
        assert event['sourceStartFrame'] == move['nativeSourceRangeFrames'][0]
        assert event['sourceEndFrame'] == move['nativeSourceRangeFrames'][1]
        native_path = root / move['nativeSource']
        native_hashes[str(native_path)] = _sha(native_path)
        assert native_hashes[str(native_path)] == move['nativeSourceSha256'], (id, move['key'], 'Native preview changed.')
        a, b = audio[move['key']]
        bridge = next((x for x in bridges if x['startSample'] <= a and b <= x['startSample'] + x['samples']), None)
        if bridge is None:
            raise ValueError(f'{id}/{move["key"]}: removal is not wholly within a proven music-only inserted bridge.')
        deletions_p.append(picture[move['key']])
        deletions_a.append([a, b])
        music_provenance.append({'key': move['key'], 'sourceRangeSamples': [a, b], 'authoredMusicBridge': bridge, 'proof': str(proof_path), 'notSynthesizedSpeech': True})
    deletions_a.sort()
    deletions_p.sort()
    for ranges in [deletions_a, deletions_p]:
        assert all(a[1] <= b[0] for a, b in zip(ranges, ranges[1:]))
    # SRT anchors are millisecond-rounded; A17's 43.033 cue precedes the
    # music-bridge end 43.033333 by 16 samples. Snap only inside that proven
    # removed music, never across an unverified narration sample.
    for a, b in deletions_a:
        if a < anchor_sample < b:
            assert b - anchor_sample <= round(.001 * RATE)
            anchor_sample = b
    rounded_touches = {}
    input_hashes = {str(p): _sha(p) for p in [layout_path, relations_path, pacing_path, proof_path, manifest_path]}
    input_hashes.update(native_hashes)
    for language in ('ko', 'en'):
        record = next(x for x in base['files'] if x['kind'] == language + '.srt')
        path = root / record['path']
        assert _sha(path) == record['sha256']
        input_hashes[str(path)] = record['sha256']
        rounded_touches[language] = _check_cues(read_cues(path), deletions_a, at, .0011, f'{id}/{language}')
    ass_path = pdir / 'captions.ass'
    ass_cues = []
    for line in ass_path.read_text('utf-8-sig').splitlines():
        if line.startswith('Dialogue:'):
            x = line.split(',', 9)
            ass_cues.append({'start': _seconds(x[1]), 'end': _seconds(x[2]), 'text': x[9]})
    rounded_touches['ass'] = _check_cues(ass_cues, deletions_a, at, .0101, f'{id}/ass')
    input_hashes[str(ass_path)] = _sha(ass_path)
    old_clean = root / next(x['path'] for x in base['files'] if x['kind'] == 'clean.mp4')
    old_clean_sha = next(x['sha256'] for x in base['files'] if x['kind'] == 'clean.mp4')
    map_path = Path(map_path) if map_path else root / 'projects' / ep['slug'] / 'production/local/relations-v4/relation.mp4'
    inserts_p = [{'kind': 'map', 'source': str(map_path), 'sourceStart': 0, 'length': map_frames}]
    inserts_a = [{'kind': 'map', 'sourceStart': 0, 'length': map_frames * SPF}]
    for move in layout['moves']:
        start, end = move['nativeSourceRangeFrames']
        for k in range(move['newInsertedPassCount']):
            inserts_p.append({'kind': 'native-pass', 'key': move['key'], 'source': str(root / move['nativeSource']), 'sourceSha256': move['nativeSourceSha256'], 'sourceStart': start, 'length': end - start, 'passIndex': k + 1, 'passTotal': 3, 'overlayLabel': True, 'normalSpeed': 1.0, 'thirdPassFromUnchangedBody': move['thirdPassFromUnchangedBodyAtAnchor']})
        a, b = move['originalMusicOnlyRangeSamples']
        inserts_a.append({'kind': 'music-replay', 'key': move['key'], 'sourceStart': a, 'sourceEnd': b, 'length': move['newInsertedFrames'] * SPF, 'musicOnlyProvenance': next(x for x in music_provenance if x['key'] == move['key'])})
    picture_edl = _partition(old_frames, deletions_p, anchor_frame, inserts_p, repairs)
    for part in picture_edl:
        if part['kind'] == 'baseline':
            part['source'] = str(old_clean)
            part['sourceSha256'] = old_clean_sha
        part.update(sourceStartFrame=part.pop('sourceStart'), frames=part.pop('length'), outputStartFrame=part.pop('outputStart'), outputEndFrame=part.pop('outputEnd'))
    # A16's first 129 unchanged body frames are the third normal-speed pass.
    # Isolate that exact range for the 3/3 label without inserting any frames,
    # changing PCM, or turning the later slow analysis into another repeat.
    for move in layout['moves']:
        if not move['thirdPassFromUnchangedBodyAtAnchor']:
            continue
        n = move['nativeSourceRangeFrames'][1] - move['nativeSourceRangeFrames'][0]
        index = next(i for i, part in enumerate(picture_edl) if part['kind'] == 'baseline' and part['sourceStartFrame'] == anchor_frame)
        original = picture_edl[index]
        assert original['frames'] >= n
        labeled = dict(original, frames=n, outputEndFrame=original['outputStartFrame'] + n,
                       key=move['key'], passIndex=3, passTotal=3, overlayLabel=True,
                       normalSpeed=1.0, thirdPassFromUnchangedBody=True)
        replacement = [labeled]
        if original['frames'] > n:
            replacement.append(dict(original, sourceStartFrame=original['sourceStartFrame'] + n,
                                    frames=original['frames'] - n,
                                    outputStartFrame=original['outputStartFrame'] + n))
        picture_edl[index:index + 1] = replacement
    audio_edl = _partition(old_frames * SPF, deletions_a, anchor_sample, inserts_a)
    for part in audio_edl:
        part.update(sourceStartSample=part.pop('sourceStart'), samples=part.pop('length'), outputStartSample=part.pop('outputStart'), outputEndSample=part.pop('outputEnd'))
    total_frames = picture_edl[-1]['outputEndFrame']
    assert audio_edl[-1]['outputEndSample'] == total_frames * SPF
    map_p = next(x for x in picture_edl if x['kind'] == 'map')
    map_a = next(x for x in audio_edl if x['kind'] == 'map')
    edit = {
        'schemaVersion': 1, 'id': id, 'slug': ep['slug'], 'fps': FPS, 'sampleRate': RATE,
        'oldFrames': old_frames, 'mapFrames': map_frames, 'totalFrames': total_frames,
        'anchorFrame': anchor_frame, 'anchorSample': anchor_sample,
        'requestedAnchorSeconds': at, 'requestedAnchorSample': requested_anchor_sample,
        'anchorMusicBoundarySnapSamples': anchor_sample - requested_anchor_sample,
        'removedPictureRanges': deletions_p, 'removedMusicRangesSamples': deletions_a,
        'mapStartFrame': map_p['outputStartFrame'], 'mapStartSample': map_a['outputStartSample'],
        'mapStartSeconds': map_a['outputStartSample'] / RATE,
        'mapPictureAudioOffsetSeconds': map_p['outputStartFrame'] / FPS - map_a['outputStartSample'] / RATE,
        'insertedAudioSamples': sum(x['samples'] for x in audio_edl if x['kind'] != 'baseline'),
        'pictureEdl': picture_edl, 'audioEdl': audio_edl, 'inputMetadataHashes': input_hashes,
        'baselineVideoExpectedSha256': old_clean_sha,
        'musicOnlyProvenance': music_provenance,
        'captionBoundaryRoundingTouches': rounded_touches,
        'validation': {'sentenceTextUnchanged': True, 'oldNarrationOrderPreserved': True, 'removedRangesAreAuthoredMusicOnly': True, 'noSpokenSubtitleCueRemoved': True, 'pictureAndSampleTotalsAgree': True, 'renderedAndListeningReview': 'pending'},
    }
    # Verify every current speech cue remains positive, ordered and disjoint.
    for language in ('ko', 'en'):
        path = root / next(x['path'] for x in base['files'] if x['kind'] == language + '.srt')
        changed = retime_cues(read_cues(path), edit)
        assert all(c['end'] > c['start'] for c in changed)
        assert all(a['end'] <= b['start'] + .002 for a, b in zip(changed, changed[1:]))
    return edit


def transform_seconds(t, edit, end=False, ass=False):
    """Old-master cue time → final time, with rounded boundary snapping."""
    point = round(float(t) * RATE)
    anchor = edit['anchorSample']
    tolerance = round((.0051 if ass else .00051) * RATE)
    boundaries = [anchor] + [n for r in edit['removedMusicRangesSamples'] for n in r]
    nearest = min(boundaries, key=lambda n: abs(n - point))
    if abs(nearest - point) <= tolerance:
        point = nearest
    original = point
    deleted = 0
    for a, b in edit['removedMusicRangesSamples']:
        if point >= b:
            deleted += b - a
        elif point > a:
            deleted += point - a
            break
    point -= deleted
    if (original > anchor) if end else (original >= anchor):
        point += edit['insertedAudioSamples']
    return point / RATE


def retime_cues(cues, edit):
    return [dict(c, start=transform_seconds(c['start'], edit), end=transform_seconds(c['end'], edit, end=True)) for c in cues]


def retime_ass(text, edit):
    result = []
    for line in text.splitlines():
        if line.startswith('Dialogue:'):
            row = line.split(',', 9)
            a, b = _seconds(row[1]), _seconds(row[2])
            row[1] = _stamp(transform_seconds(a, edit, ass=True))
            row[2] = _stamp(transform_seconds(b, edit, end=True, ass=True))
            line = ','.join(row)
        result.append(line)
    return '\n'.join(result) + '\n'


def _music_loop(source, count, fade_samples=480):
    """Loop only a proven old music bridge; all joins stay inside new music."""
    import numpy as np
    assert len(source) > fade_samples * 2
    block = source.astype(np.float64)
    result = block.copy()
    # Overlap-add at wraps preserves the requested output length after trimming.
    while len(result) < count:
        n = min(fade_samples, len(result) // 4, len(block) // 4)
        w = np.linspace(0, 1, n, dtype=np.float64)[:, None]
        seam = result[-n:] * (1 - w) + block[:n] * w
        result = np.concatenate([result[:-n], seam, block[n:]], axis=0)
    result = result[:count].copy()
    edge = min(fade_samples, count // 4)
    w = np.linspace(0, 1, edge, dtype=np.float64)[:, None]
    result[:edge] *= w
    result[-edge:] *= w[::-1]
    # PCM_24 in libsndfile's int32 representation must be a multiple of 256.
    return (np.clip(np.rint(result / 256), -8388608, 8388607) * 256).astype(np.int32)


def reconstruct_pcm(edit, old_pcm, map_pcm, output_pcm, chunk_samples=48000 * 8):
    """Stream PCM_24 assembly and verify every retained/map sample after saving.

    Original speech-bearing regions remain byte-identical and in order. Old
    music-only inserts may move or be looped; newly made music alone gets fades.
    Returns evidence for the caller to save, rather than writing an extra file.
    """
    import numpy as np
    import soundfile as sf
    old_pcm, map_pcm, output_pcm = map(Path, (old_pcm, map_pcm, output_pcm))
    assert output_pcm.resolve() not in (old_pcm.resolve(), map_pcm.resolve())
    output_pcm.parent.mkdir(parents=True, exist_ok=True)
    retained, maps, music = [], [], []
    with sf.SoundFile(old_pcm) as old, sf.SoundFile(map_pcm) as new:
        assert old.samplerate == new.samplerate == RATE and old.channels == new.channels == 2
        assert len(old) == edit['oldFrames'] * SPF
        assert len(new) == edit['mapFrames'] * SPF
        with sf.SoundFile(output_pcm, 'w', samplerate=RATE, channels=2, subtype='PCM_24') as output:
            for part in edit['audioEdl']:
                assert output.tell() == part['outputStartSample']
                digest = hashlib.sha256()
                if part['kind'] == 'music-replay':
                    old.seek(part['sourceStartSample'])
                    source = old.read(part['sourceEnd'] - part['sourceStartSample'], dtype='int32', always_2d=True)
                    samples = _music_loop(source, part['samples'])
                    output.write(samples)
                    digest.update(samples.tobytes())
                    music.append(dict(part, pcmSha256=digest.hexdigest(), generatedSpeech=False, loopJoin='10 ms overlap-add; edge fades affect only new music', sourcePcmSha256=hashlib.sha256(source.tobytes()).hexdigest()))
                else:
                    source = old if part['kind'] == 'baseline' else new
                    source.seek(part['sourceStartSample'])
                    remaining = part['samples']
                    while remaining:
                        block = source.read(min(remaining, chunk_samples), dtype='int32', always_2d=True)
                        assert len(block)
                        output.write(block)
                        digest.update(block.tobytes())
                        remaining -= len(block)
                    row = dict(part, pcmSha256=digest.hexdigest())
                    (retained if part['kind'] == 'baseline' else maps).append(row)
        assert len(retained) and len(maps) == 1
        assert all(a['sourceStartSample'] + a['samples'] <= b['sourceStartSample'] for a, b in zip(retained, retained[1:]))
    with sf.SoundFile(output_pcm) as check:
        assert len(check) == edit['totalFrames'] * SPF
        for row in retained + maps + music:
            check.seek(row['outputStartSample'])
            remaining, digest = row['samples'], hashlib.sha256()
            while remaining:
                block = check.read(min(remaining, chunk_samples), dtype='int32', always_2d=True)
                assert len(block)
                digest.update(block.tobytes())
                remaining -= len(block)
            row['serializedPcmExactEquality'] = digest.hexdigest() == row['pcmSha256']
            assert row['serializedPcmExactEquality'], row
    removed = sum(b - a for a, b in edit['removedMusicRangesSamples'])
    assert sum(x['samples'] for x in retained) + removed == edit['oldFrames'] * SPF
    return {
        'id': edit['id'], 'baselinePcm': str(old_pcm), 'baselinePcmSha256': _sha(old_pcm),
        'additionPcm': str(map_pcm), 'additionSha256': _sha(map_pcm), 'mixSha256': _sha(output_pcm),
        'inputMetadataHashes': edit['inputMetadataHashes'],
        'allOriginalSpokenPcmSamplesPreserved': True,
        'retainedBaselinePcmInOriginalOrder': True,
        'allAdditionSamplesExactlyPreserved': True,
        'allBaselineSamplesExactlyPreservedInOrder': not bool(removed),
        'removedBaselineSamples': removed,
        'removedRangesAreAuthoredMusicOnly': edit['musicOnlyProvenance'],
        'noSpokenSubtitleCueRemoved': True, 'noOriginalTtsRegenerated': True,
        'nativeSpeedPassesPreserved': True,
        'audioInsertionSample': edit['mapStartSample'], 'pictureInsertionFrame': edit['mapStartFrame'],
        'pictureAudioOffsetSeconds': edit['mapPictureAudioOffsetSeconds'],
        'retainedRegions': retained, 'unchangedNewNarrationRegions': maps, 'newMusicRegions': music,
        'totalSamples': edit['totalFrames'] * SPF, 'fullListeningPerformed': False,
    }


def dry_run_all(root=ROOT):
    root = Path(root)
    batch = root / BATCH_REL
    timing_path = batch / 'relations-v4/local/timing.json'
    timings = {x['id']: x['frames'] for x in _read(timing_path)['episodes']} if timing_path.exists() else {}
    records = _read(batch / 'pacing-v3/review-manifest.json')['records']
    reports = []
    for base in records:
        if not re.fullmatch(r'A\d\d', base['id']):
            continue
        id = base['id']
        frames = timings.get(id, 2400)
        edit = make_edit(id, round(base['durationSeconds'] * FPS), frames, root=root)
        assert edit['mapStartFrame'] <= next(x['outputStartFrame'] for x in edit['pictureEdl'] if x['kind'] == 'map')
        for part in edit['pictureEdl']:
            assert part['frames'] > 0
        ass_path = root / 'projects' / edit['slug'] / 'production/local/pacing-v3/captions.ass'
        output = retime_ass(ass_path.read_text('utf-8-sig'), edit)
        dialogue_count = 0
        for line in output.splitlines():
            if line.startswith('Dialogue:'):
                parts = line.split(',', 9)
                assert _seconds(parts[2]) > _seconds(parts[1]), (id, line)
                dialogue_count += 1
        reports.append({'id': id, 'mapFrames': frames, 'actualTimingUsed': id in timings,
                        'mapStartFrame': edit['mapStartFrame'], 'mapStartSample': edit['mapStartSample'],
                        'pictureSegments': len(edit['pictureEdl']), 'audioSegments': len(edit['audioEdl']),
                        'oldFrames': edit['oldFrames'], 'totalFrames': edit['totalFrames'],
                        'movedMusicBlocks': len(edit['musicOnlyProvenance']), 'assDialogueCount': dialogue_count,
                        'checks': edit['validation']})
    assert len(reports) == 18
    return {'status': 'metadata-dry-run-passed', 'episodes': reports, 'mediaWritten': False, 'audioSamplesRendered': False}


if __name__ == '__main__':
    print(json.dumps(dry_run_all(), ensure_ascii=False, indent=2))
