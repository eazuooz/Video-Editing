"""Prepare the three owned Shorts from measured PCM/captions, never text estimates.

Run only after voice, narration.timing.json and script/captions.json exist:
  python -X utf8 projects/shorts-noita-material-pixels/production/prepare-actual-visuals.py --all
Use --slug for one selected project. --self-test performs pure synthetic checks only.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
REVISION = 'distinctive-ten-v1'
SLUGS = ('shorts-noita-material-pixels', 'shorts-rain-world-body-chunks', 'shorts-obra-dinn-dithering')
FALLBACK = dict(zip(SLUGS, ('material', 'chunks', 'reveal')))
FPS = 60


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def run(args):
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stderr[-5000:])
    return result.stdout


def frame(seconds):
    return int(math.floor(float(seconds) * FPS + .5))


def compact(text):
    return re.sub(r'\s+', '', text)


def event(cues, paragraph, phrases):
    """Keep canonical cue IDs, including added b-clauses; never renumber cues."""
    matching = [c for c in cues if c['lineIndex'] == paragraph and
                any(compact(p) in compact(c.get('spoken', '') + c['ko']) for p in phrases)]
    if not matching:
        raise ValueError(f'No actual caption anchor for paragraph {paragraph}: {phrases}')
    return dict(startFrame=min(c['startFrame'] for c in matching),
                endFrame=max(c['endFrame'] for c in matching),
                cueIds=[c['id'] for c in matching], method='actual-caption-phrase')


def build_timing(slug, lines, clauses, spec, config, narration, captions):
    """Pure assembly: no file writes, media extraction or proof-status mutation."""
    if captions.get('fps') != FPS or abs(float(captions['voiceOffsetSeconds']) - .2) > 1e-8:
        raise ValueError('Expected actual 60fps captions with the already-applied 0.20s voice offset.')
    frames = int(captions['frames'])
    if frames <= 0 or abs(captions['durationSeconds'] - frames / FPS) > 1e-7:
        raise ValueError('Caption frames and duration differ.')
    offset = float(captions['voiceOffsetSeconds'])
    entries = {int(e['lineIndex']): e for e in narration['entries'] if e.get('scene_id') == 'main'}
    if len(entries) != len(lines) or sorted(entries) != list(range(len(lines))):
        raise ValueError('Actual PCM paragraph inventory differs from the narration.')
    for i, line in enumerate(lines):
        if compact(entries[i]['text']) != compact(line):
            raise ValueError(f'PCM paragraph {i} differs from current script.')
        if compact(' '.join(c['spoken'] for c in clauses if c['lineIndex'] == i)) != compact(line):
            raise ValueError(f'Caption clauses do not reconstruct paragraph {i}.')
    canonical_ids = [c['id'] for c in clauses]
    cues = captions['cues']
    if [c['id'] for c in cues] != canonical_ids:
        raise ValueError('Actual captions must preserve every canonical cue ID and added b-clause.')
    by_id = {c['id']: c for c in cues}
    for c, canonical in zip(cues, clauses):
        if c['ko'] != canonical['ko'] or c['en'] != canonical['en']:
            raise ValueError('Caption text differs from canonical clause: ' + c['id'])
        if c['lineIndex'] != canonical['lineIndex'] or not 0 <= c['startFrame'] < c['endFrame'] <= frames:
            raise ValueError('Invalid actual cue: ' + c['id'])
    expected_minimum = math.ceil((float(narration['duration_seconds']) + offset + .4) * FPS - 1e-8)
    if frames < expected_minimum or frames > expected_minimum + 1:
        raise ValueError('Use the finite actual-PCM +0.20s/+0.40s timeline, without extra padding.')
    boundaries = [0] + [frame(entries[i]['start'] + offset) for i in range(1, len(lines))] + [frames]
    if any(b <= a for a, b in zip(boundaries, boundaries[1:])):
        raise ValueError('Actual paragraph starts are not strictly increasing.')
    sections = []
    for i, s in enumerate(spec):
        paragraph = int(s['paragraph'])
        if paragraph != i or s['firstCue'] not in by_id or by_id[s['firstCue']]['lineIndex'] != paragraph:
            raise ValueError('Section/firstCue mapping changed: ' + s['id'])
        start, end = boundaries[i], boundaries[i + 1]
        first_cue = by_id[s['firstCue']]
        if not start - 2 <= first_cue['startFrame'] < end:
            raise ValueError('First cue lies outside its PCM paragraph: ' + s['firstCue'])
        base = dict(s, visualId=s['id'], firstCueFrame=first_cue['startFrame'],
                    pcmParagraphStart=float(entries[i]['start']) + offset,
                    pcmParagraphEnd=float(entries[i]['end']) + offset)
        if s['id'] in config['cuts']:
            cut = config['cuts'][s['id']]
            available = int(math.floor(float(cut['maxDuration']) * FPS + 1e-8))
            game_end = min(end, start + available)
            sections.append(dict(base, kind='game', startFrame=start, endFrame=game_end,
                                 source='game-master', sourceStart=float(cut['in']),
                                 sourceEnd=float(cut['in']) + (game_end - start) / FPS,
                                 sourceTimeBasis='original-seconds', rate=1, nativeAudioAdopted=False,
                                 frameDirectoryKey=s['id']))
            if game_end < end:
                visual_id = FALLBACK[slug] if s['id'] == 'game' else 'close'
                sections.append(dict(base, id=s['id'] + '-explain', visualId=visual_id,
                                     kind='diagram', forceDiagram=True, startFrame=game_end, endFrame=end,
                                     continuity='Same spoken paragraph continues over the matching principle diagram; no source loop, slowdown, hold or invented game action.'))
        else:
            sections.append(dict(base, kind='diagram', forceDiagram=True, startFrame=start, endFrame=end))
    for s in sections:
        s.update(start=s['startFrame'] / FPS, end=s['endFrame'] / FPS,
                 cueIds=[c['id'] for c in cues if c['startFrame'] < s['endFrame'] and c['endFrame'] > s['startFrame']])
    for a, b in zip(sections, sections[1:]):
        if a['endFrame'] != b['startFrame']:
            raise ValueError('Visual timeline has a gap or overlap.')
    if sections[0]['startFrame'] != 0 or sections[-1]['endFrame'] != frames:
        raise ValueError('Visual timeline does not cover the exact caption frame count.')
    if slug == SLUGS[0]:
        events = {'flowFallStart': event(cues, 2, ['아래가 비면']),
                  'flowSideStart': event(cues, 2, ['막히면']),
                  'oilIgnition': event(cues, 3, ['불이 옮겨']),
                  'waterReplacement': event(cues, 3, ['기름을 물로'])}
    elif slug == SLUGS[1]:
        events = {'bodyRotation': event(cues, 2, ['한쪽이 걸리면']),
                  'limbsAdded': event(cues, 3, ['팔과 다리'])}
    else:
        events = {'fourCells': event(cues, 2, ['네 칸만']),
                  'twelveCells': event(cues, 2, ['열두 칸']),
                  'patternStable': event(cues, 4, ['깜빡임을 줄였습니다'])}
    first_reveal = next(s for s in sections if s['id'] == spec[1]['id'])
    reveal_start = max(first_reveal['start'], first_reveal['firstCueFrame'] / FPS) + .15
    reactions = [dict(kind='realize', start=reveal_start, end=min(reveal_start + 1.6, first_reveal['end']))]
    # Keep the closing reaction only after gameplay has ended, so it cannot hide game evidence.
    final_diagrams = [s for s in sections if s['paragraph'] == len(lines) - 1 and s['kind'] != 'game']
    if final_diagrams:
        s = final_diagrams[-1]
        if s['end'] - s['start'] >= 1.2:
            reactions.append(dict(kind='relief', start=max(s['start'], s['end'] - 2.7), end=s['end'] - .4))
    return dict(revision=REVISION, previewOnly=False, fps=FPS, frames=frames,
                durationSeconds=frames / FPS, voiceOffsetSeconds=offset, sections=sections,
                sourceTimeBasis='original-seconds', sources={}, events=events, reactions=reactions,
                cueAnchors={c['id']: dict(lineIndex=c['lineIndex'], startFrame=c['startFrame'], endFrame=c['endFrame']) for c in cues},
                actualTimingMethod='Measured paragraph PCM starts plus existing caption offset; cue events from canonical actual captions, including b-clauses.',
                actualAudioListening='pending', fullMovingReview='pending')


def authorize(project):
    control = read(ROOT / 'shared/publishing/video-production-control.json')
    auth = control.get('scopedBatchAuthorizations', {}).get('explicit-ten-distinctive-shorts-20261025', {})
    manifest = read(project / 'project.json')
    plan = read(project / 'planning/production-plan.json')
    if auth.get('status') != 'active' or project.name not in auth.get('slugs', []) or not auth.get('fullProductionAuthorized'):
        raise RuntimeError('The finite selected production scope is not active.')
    if manifest['currentRevision'] != REVISION or not plan.get('scriptFinalized') or not plan.get('independentFootageViewed'):
        raise RuntimeError('Current script/source preparation is incomplete.')


def load_actual(slug):
    p = ROOT / 'projects' / slug
    authorize(p)
    paths = dict(narration=p / 'script/narration.spoken.ko.json', clauses=p / 'script/clauses.json',
                 captions=p / 'script/captions.json', pcmTiming=p / 'production/local/audio-v1/voice/narration.timing.json',
                 voice=p / 'production/local/audio-v1/voice/narration.wav', evidence=p / 'sources/selected-footage.json',
                 sections=p / 'production/section-plan.json', config=p / 'production/visual-config.json')
    missing = [str(q) for q in paths.values() if not q.exists()]
    if missing:
        raise FileNotFoundError('Actual PCM/captions must exist before preparing visuals: ' + ', '.join(missing))
    data = {key: read(q) for key, q in paths.items() if key != 'voice'}
    hashes = {key: sha(q) for key, q in paths.items() if key != 'config'}
    inputs = data['captions'].get('timingInputs', {})
    if inputs.get('voiceSha256') != hashes['voice'] or inputs.get('clausesSha256') != hashes['clauses']:
        raise ValueError('Captions belong to another PCM or clause version; regenerate timing first.')
    if inputs.get('narrationSha256') and inputs['narrationSha256'] != hashes['narration']:
        raise ValueError('Narration hash changed after caption timing.')
    config = data['config']
    source = ROOT / config['source']
    if sha(source) != data['evidence']['sourceSha256']:
        raise ValueError('The selected FHD source master has changed.')
    probe = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(source)]))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    if video['width'] < 1920 or video['height'] < 1080:
        raise ValueError('Genuine FHD original required.')
    source_duration = float(probe['format']['duration'])
    for cut in config['cuts'].values():
        if float(cut['in']) < 0 or float(cut['in']) + float(cut['maxDuration']) > source_duration + 1 / FPS:
            raise ValueError('A selected cut extends past the real source duration.')
    voice_probe = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-of', 'json', str(paths['voice'])]))
    if abs(float(voice_probe['format']['duration']) - float(data['pcmTiming']['duration_seconds'])) > .002:
        raise ValueError('PCM duration differs from paragraph timing.')
    lines = data['narration']['scenes'][0]['lines']
    timing = build_timing(slug, lines, data['clauses']['clauses'], data['sections'], config, data['pcmTiming'], data['captions'])
    policy = 'Original recording has no audio stream.' if slug == SLUGS[0] else 'Official trailer music is excluded; no native soundtrack or invented substitute adopted.'
    timing['sources']['game-master'] = dict(path=config['source'], sourceSHA256=data['evidence']['sourceSha256'],
                                          originalOffsetSeconds=0, nativeAudioAdopted=False, sourceAudioAdopted=False,
                                          audioPolicy=policy, nativeDimensions=[video['width'], video['height']],
                                          nativeFrameRate=video['avg_frame_rate'], sourceDuration=source_duration)
    clean_cuts = {key: {k: v for k, v in value.items() if k != 'frameDirectory'} for key, value in config['cuts'].items()}
    fingerprint = hashlib.sha256(encoded(dict(hashes=hashes, cuts=clean_cuts, preparationCodeSha256=sha(__file__))).encode()).hexdigest()
    version = REVISION + '-pcm-' + fingerprint[:12]
    timing['preparationFingerprint'] = fingerprint
    timing['timingInputs'] = dict(hashes, voiceDurationSeconds=data['pcmTiming']['duration_seconds'])
    for s in timing['sections']:
        if s['kind'] == 'game':
            s['frameDirectory'] = version + '/' + s['frameDirectoryKey']
            s['nativeAudioPolicy'] = policy
    return p, config, timing, version


def preserve_and_write(path, value, archive):
    """Only advance the active JSON pointer; preserve previous exact bytes first."""
    payload = encoded(value)
    if path.exists():
        previous = path.read_bytes()
        if previous == payload.encode():
            return
        archive.mkdir(parents=True, exist_ok=True)
        snapshot = archive / (path.stem + '-' + hashlib.sha256(previous).hexdigest()[:12] + path.suffix)
        if snapshot.exists():
            if snapshot.read_bytes() != previous:
                raise ValueError('Snapshot collision; preserve both versions.')
        else:
            snapshot.write_bytes(previous)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding='utf8', newline='\n')


def prepare(loaded):
    p, config, timing, version = loaded
    bundle = p / 'production/local/actual-visuals' / version
    source = ROOT / config['source']
    outputs = []
    for s in timing['sections']:
        if s['kind'] != 'game':
            continue
        authorize(p)
        cut = config['cuts'][s['frameDirectoryKey']]
        folder = p / 'production/local/game-frames' / s['frameDirectory']
        count = s['endFrame'] - s['startFrame']
        width, height = int(cut.get('proxyWidth', 1920)), int(cut.get('proxyHeight', 1080))
        if width < 1920 or height < 1080:
            raise ValueError('Actual production frames must retain FHD or higher; small previews stay separate.')
        if folder.exists():
            files = sorted(folder.glob('*.jpg'))
            if len(files) != count or [f.name for f in files] != [f'{i:05}.jpg' for i in range(count)]:
                raise ValueError('Preserve incomplete prior frame folder; investigate before rerunning: ' + str(folder))
        else:
            folder.mkdir(parents=True)
            run(['ffmpeg', '-v', 'error', '-n', '-ss', str(s['sourceStart']), '-i', str(source),
                 '-an', '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps=60',
                 '-frames:v', str(count), '-q:v', '3', '-start_number', '0', str(folder / '%05d.jpg')])
            files = sorted(folder.glob('*.jpg'))
            if len(files) != count:
                raise ValueError('Decoded frame count differs from exact game cut; partial folder retained.')
        outputs.append(dict(id=s['id'], path=str(folder.relative_to(ROOT)), frames=count,
                            sourceStart=s['sourceStart'], sourceEnd=s['sourceEnd'], rate=1,
                            firstFrameSha256=sha(files[0]), lastFrameSha256=sha(files[-1]), proxyDimensions=[width, height]))
    timing['preparedFrames'] = outputs
    bundle.mkdir(parents=True, exist_ok=True)
    snapshot = bundle / 'visual-timing.json'
    if snapshot.exists() and read(snapshot) != timing:
        raise ValueError('Existing actual timing bundle differs; preserve it and investigate.')
    if not snapshot.exists():
        snapshot.write_text(encoded(timing), encoding='utf8')
    history = p / 'production/local/actual-visuals/previous-active-json'
    preserve_and_write(p / 'production/visual-timing.json', timing, history)
    preserve_and_write(p / 'production/local/visual-timing.json', timing, history)
    print(encoded(dict(slug=p.name, actualTimingPrepared=True, frames=timing['frames'], version=version,
                       games=[dict(id=s['id'], frames=s['endFrame']-s['startFrame']) for s in timing['sections'] if s['kind']=='game'],
                       overflowDiagrams=[s['id'] for s in timing['sections'] if s.get('continuity')],
                       fullRender=False, listening=False)))


def self_test():
    """Synthetic only: no source status, production timing or media is written."""
    for slug in SLUGS:
        p = ROOT / 'projects' / slug
        lines = read(p / 'script/narration.spoken.ko.json')['scenes'][0]['lines']
        clauses = read(p / 'script/clauses.json')['clauses']
        spec = read(p / 'production/section-plan.json')
        config = read(p / 'production/visual-config.json')
        # Every 20s paragraph deliberately exceeds every selected gameplay cut.
        entries = [dict(lineIndex=i, scene_id='main', text=line, start=i*20., end=(i+1)*20.-.2) for i,line in enumerate(lines)]
        duration = entries[-1]['end']; total = math.ceil((duration+.6)*60-1e-8)
        cues=[]
        for i in range(len(lines)):
            group=[c for c in clauses if c['lineIndex']==i]
            for j,c in enumerate(group):
                a=frame(i*20+.2+j*19/len(group)); b=frame(i*20+.2+(j+1)*19/len(group))
                cues.append(dict(c,startFrame=a,endFrame=b,start=a/60,end=b/60))
        cap=dict(fps=60,frames=total,durationSeconds=total/60,voiceOffsetSeconds=.2,cues=cues)
        narration=dict(entries=entries,duration_seconds=duration)
        result=build_timing(slug,lines,clauses,spec,config,narration,cap)
        assert result['frames']==total and not result['previewOnly']
        assert [s['id'] for s in result['sections'] if s.get('forceDiagram') and s['id'].endswith('-explain')]==['game-explain','close-explain']
        assert set(result['cueAnchors'])=={c['id'] for c in clauses}
        assert all(s['sourceEnd']-s['sourceStart']<=config['cuts'][s['frameDirectoryKey']]['maxDuration']+1e-8 for s in result['sections'] if s['kind']=='game')
        # Extra b-clause IDs must survive without parsing numeric suffixes.
        renamed=json.loads(json.dumps(clauses)); changed=json.loads(json.dumps(cap))
        renamed[-1]['id']+='b'; changed['cues'][-1]['id']+='b'
        again=build_timing(slug,lines,renamed,spec,config,narration,changed)
        assert renamed[-1]['id'] in again['cueAnchors']
        # Invalid or stale timing must fail before any expensive source decode.
        for field,value in [('voiceOffsetSeconds',.4),('frames',total+60)]:
            invalid=json.loads(json.dumps(cap)); invalid[field]=value
            try:
                build_timing(slug,lines,clauses,spec,config,narration,invalid)
                raise AssertionError('Invalid caption contract accepted: '+field)
            except ValueError:
                pass
        stale=json.loads(json.dumps(cap)); stale['cues'][-1]['id']+='-stale'
        try:
            build_timing(slug,lines,clauses,spec,config,narration,stale)
            raise AssertionError('Stale cue ID accepted.')
        except ValueError:
            pass
        print(slug+': PCM/offset/frame coverage, finite source overflow, b-clause retention, event anchors and invalid-input rejection passed (synthetic only).')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--slug',choices=SLUGS)
    group.add_argument('--all',action='store_true')
    group.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:
        self_test()
    else:
        # Validate all requested real inputs first; never partly advance an unready batch.
        ready=[load_actual(slug) for slug in (SLUGS if args.all else (args.slug,))]
        for item in ready:
            prepare(item)
