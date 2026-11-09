"""CPU1 encoded-frame QA for the selected17; never renders/edits a master.

Checks current narration/mix/caption/picture ancestry before extraction. Generated
samples remain inspection-pending until a model actually reads the pictures.
This is sampled visual QA, never full playback, listening or human approval.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, subprocess
from PIL import Image, ImageDraw, ImageFont

H = Path(__file__).resolve().parent
R = H.parents[3]
OUT = Path('C:/Users/1/Videos/YamyamCoding/animation-contrast-v5-review')
QA = H / 'local/encoded-visual-qa'
HASHES = {}


def read(p):
    return json.loads(Path(p).read_text('utf-8-sig'))


def path(p):
    return R / Path(p)


def sha(p):
    p = path(p); s = p.stat(); k = (str(p), s.st_size, s.st_mtime_ns)
    if k not in HASHES:
        with p.open('rb') as f: HASHES[k] = hashlib.file_digest(f, 'sha256').hexdigest()
    return HASHES[k]


def save(p, data):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_suffix('.' + str(os.getpid()) + '.pending')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')
    os.replace(temp, p)


def module(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def same(p, digest):
    assert path(p).is_file() and sha(p) == digest, ('Source changed', str(p))


def identity(ep):
    control = read(R / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert ep in control['episodes'] and ep != 'A03'
    revisions = read(H / 'narration/source-verified-revisions.json')
    expected = {}
    for e in revisions['episodes']:
        for c in e['changes']:
            expected[e['id'], c['id']] = {'expected': c['ko']}
    for c in revisions['existingApprovedChanges']:
        expected[c['episode'], c['id']] = {'expected': c['ko']}
    # Read-only proof: independent ASR-approved input takes/current final audio
    # placement, not another ASR execution or final listening claim.
    aac = module('encoded_qa_aac_proof', H / 'asr_final_aac.py')
    proof, why = aac.proof_for(ep, expected)
    assert proof, why
    edl = read(path(proof['assemblyPath']))
    correction=H/'visual-corrections'/(ep+'.json')
    if correction.exists():
        assert read(correction)['readyForAssembly']
        assert (edl.get('visualCorrection')or{}).get('sha256')==sha(correction),'Current episode visual correction not assembled'
    delivery = read(OUT / ep / 'delivery.json')
    signature = read(H / 'local/final-encode' / ep / 'signature.json')
    receipt = read(H / 'local/explanation-assembly' / ep / 'captionless/receipt.json')
    assert receipt['pictureEdl'] == edl['pictureEdl'] and receipt['audioEdl'] == edl['audioEdl']
    assert signature['frames'] == edl['frames'] == delivery['frames']
    same(H / 'local/explanation-assembly' / ep / 'captionless/picture.mp4', signature['pictureSha256'])
    assert signature['mixSha256'] == proof['mixInput']['sha256']
    same(H / 'local/final-audio' / ep / 'captions/captions.provisional.ko.ass', signature['assSha256'])
    gamefile = H / ('game-plates-caption-safe.json' if (H / 'game-plates-caption-safe.json').exists() else 'game-plates-manifest.json')
    integrationfile = H / 'renderer' / ('integration-caption-safe.json' if (H / 'renderer/integration-caption-safe.json').exists() else 'integration-manifest.json')
    game = next(x for x in read(gamefile)['episodes'] if x['id'] == ep)
    integration = next(x for x in read(integrationfile)['episodes'] if x['id'] == ep)
    # Original paths can remain readable while selected caption-safe versions
    # have new paths. Match edit identities as well, so an old master cannot
    # pass merely because its archived input file has not changed.
    current_ids = {q['id']: q['pictureSha256'] for q in game['pictureEdits']}
    current_ids.update({q['id']: q['sha256'] for q in integration['rows']})
    current = {str(path(q['picture']).absolute()).lower(): q['pictureSha256'] for q in game['pictureEdits']}
    current.update({str(path(q['output']).absolute()).lower(): q['sha256'] for q in integration['rows']})
    builderhash = sha(H / 'build_final_extensions.py')
    composites = []
    for q in edl['pictureEdits']:
        same(q['picture'], q['pictureSha256'])
        original_id = re.sub(r'-fragment\d+$', '', q['id'])
        if original_id in current_ids:
            assert q['pictureSha256'] == current_ids[original_id], ('Archived source selected instead of current safe plate', q['id'])
        k = str(path(q['picture']).absolute()).lower()
        if k in current:
            assert q['pictureSha256'] == current[k], ('Current plate differs', q['id'])
        if 'mediaComposition' in q:
            s = read(path(q['picture']).parent / 'signature.json')
            assert s['codeSha256'] == builderhash, ('Speech compositor code changed', q['id'])
            assert s['nativeFrames'] == q['mediaComposition']['originalUnscaledFrames']
            for c in s['clips']:
                same(c['source'], c['sha256'])
                if c['id'] in current_ids:
                    assert c['sha256'] == current_ids[c['id']], ('Composite contains archived plate', c['id'])
                ck = str(path(c['source']).absolute()).lower()
                if ck in current:
                    assert c['sha256'] == current[ck]
            composites.append({'id': q['id'], 'signatureSha256': sha(path(q['picture']).parent / 'signature.json')})
    for q in edl['pictureEdl']:
        same(q['source'], q['sourceSha256'])
    # Final AAC readback may be a separate worker. Do not elevate this visual
    # proof into an audio pass, even if its input-take ASR was accepted.
    final_asr = H / 'local/asr-final-aac/episodes' / (ep + '.json')
    asr_status = 'no-changed-passages' if not proof['positions'] else 'pending-separate-final-AAC-worker'
    if final_asr.exists():
        ar = read(final_asr)
        if ar.get('proof', {}).get('masterSha256') == proof['masterSha256']:
            asr_status = 'current-master-readback-record-exists; inspect its individual results separately'
        else:
            asr_status = 'prior-master-readback-only; current-AAC-worker-pending'
    proof.update(finalEncodeSignatureSha256=sha(H / 'local/final-encode' / ep / 'signature.json'),
        currentPictureSourceHashesVerified=True, currentSpeechCompositeSignatures=composites,
        finalAacReadbackStatus=asr_status, scriptInputChecks='Current replacement text/take/mix placement matches; no new ASR',
        captionedVideoDimensions=[1920, 1080], fps=60)
    return proof, edl, game, integration


def captions(file):
    values = []
    def sec(v):
        h, m, s = v.replace(',', '.').split(':'); return int(h) * 3600 + int(m) * 60 + float(s)
    for block in re.split(r'\r?\n\s*\r?\n', Path(file).read_text('utf-8-sig').strip()):
        lines = block.splitlines()
        if len(lines) >= 3 and '-->' in lines[1]:
            a, b = lines[1].split('-->')
            values.append({'startFrame': round(sec(a.strip()) * 60), 'endFrame': round(sec(b.strip()) * 60),
                           'text': ' '.join(lines[2:])})
    return values


def select_samples(ep, edl, game, integration, cues):
    rows = edl['pictureEdl']; selected = []
    own = {q['id']: q for q in integration['rows']}
    plates = {str(path(q['picture']).absolute()).lower(): q for q in game['pictureEdits']}
    edits = {q['id']: q for q in edl['pictureEdits']}

    def add(role, row, fraction=.5, exact=None):
        lo, hi = row['outputStartFrame'], row['outputEndFrame']
        frame = int(exact if exact is not None else lo + max(0, hi - lo - 1) * fraction)
        frame = max(lo, min(hi - 1, frame))
        # Stay close to the requested action phase while preferring a genuinely
        # active final caption. Do not invent a dummy caption in the picture.
        nearby = [c for c in cues if max(lo, frame - 20, c['startFrame']) < min(hi, frame + 21, c['endFrame'])]
        if exact is None and nearby:
            c = min(nearby, key=lambda c: abs((c['startFrame'] + c['endFrame']) / 2 - frame))
            frame = max(lo, min(hi - 1, max(c['startFrame'], min(c['endFrame'] - 1, frame))))
        if any(x['frame'] == frame for x in selected):
            next(x for x in selected if x['frame'] == frame)['roles'].append(role); return
        q = edits.get(row['id'], {})
        origin = plates.get(str(path(row['source']).absolute()).lower(), {})
        cue = next((c for c in cues if c['startFrame'] <= frame < c['endFrame']), None)
        selected.append({'roles': [role], 'frame': frame, 'seconds': frame / 60, 'edlId': row['id'],
            'edlKind': row['kind'], 'source': row['source'], 'sourceSha256': row['sourceSha256'],
            'sourceFrame': row['sourceStartFrame'] + frame - lo,
            'caption': cue['text'] if cue else None, 'sourceClassification': origin.get('sourceClassification'),
            'mediaSegments': origin.get('mediaSegments', q.get('mediaSegments', [])),
            'explanationStudy': own.get(row['id'], {}).get('key'),
            'focus': own.get(row['id'], {}).get('focus'), 'realEncodedCaption': bool(cue)})

    games = [q for q in rows if q['kind'] == 'independent-gameplay']
    if games:
        add('first-native-game-observation', games[0])
        add('native-game-later-action', max(games, key=lambda q: q['frames']))
    # One observable native sample for each adopted recording/action, not merely
    # the first and longest game (which can otherwise hide the Nintendo example).
    source_rows = {}
    for row in games:
        origin = plates.get(str(path(row['source']).absolute()).lower(), {})
        for seg in origin.get('mediaSegments', []):
            if seg['kind'] != 'native-gameplay': continue
            lo = max(row['sourceStartFrame'], seg['offsetFrame'])
            hi = min(row['sourceStartFrame'] + row['frames'], seg['offsetFrame'] + seg['frames'])
            if lo < hi:
                source_rows.setdefault(seg['sourceKey'], []).append((hi - lo, row, lo, hi))
    for source_key, choices in source_rows.items():
        _, row, lo, hi = max(choices, key=lambda q: q[0])
        frame = row['outputStartFrame'] + (lo + hi) // 2 - row['sourceStartFrame']
        add('source-action-' + source_key, row, exact=frame)
    for region in integration.get('preservedRelationRegions', []):
        target = (region['outputStartFrame'] + region['outputEndFrame']) // 2
        row = next(q for q in rows if q['oldStartFrame'] <= target < q['oldEndFrame'])
        add('protected-relationship-map', row, exact=row['outputStartFrame'] + target - row['oldStartFrame'])
    demo = [q for q in rows if q['id'] in own]
    analysis = [q for q in demo if own[q['id']].get('mode') == 'analysis']
    if analysis:
        strong = max(analysis, key=lambda q: q['frames'])
        add('strongest-comparison-before', strong, .2)
        add('strongest-comparison-after', strong, .75)
    stages = [q for q in demo if own[q['id']].get('phaseModeAtTail')]
    if stages: add('simultaneous-action-stages', max(stages, key=lambda q: q['frames']), .88)
    native_own = [q for q in demo if own[q['id']].get('mode') == 'native']
    if native_own: add('authored-native-demonstration', max(native_own, key=lambda q: q['frames']), .62)
    actual_analysis = [q for q in rows if plates.get(str(path(q['source']).absolute()).lower(), {}).get('sourceClassification') == 'analysis']
    if actual_analysis: add('actual-game-frame-analysis', max(actual_analysis, key=lambda q: q['frames']), .63)
    speech = [q for q in rows if 'mediaComposition' in edits.get(q['id'], {})]
    if speech:
        for row in [speech[0], max(speech, key=lambda q: edits[q['id']]['mediaComposition']['labelledStillAnalysisFrames'])]:
            comp = edits[row['id']]['mediaComposition']; tail = comp['originalUnscaledFrames']
            add('changed-voice-extension-native-prefix', row, exact=row['outputStartFrame'] + min(row['frames'] - 1, max(0, tail - 12)))
            add('changed-voice-extension-labelled-still', row, exact=row['outputStartFrame'] + min(row['frames'] - 1, tail + max(1, comp['labelledStillAnalysisFrames'] // 2)))
    late = [q for q in rows if edl['frames'] * .68 < q['outputStartFrame'] < edl['frames'] - 700]
    if late:
        join = max(late, key=lambda q: q['frames'])
        index = rows.index(join)
        if index: add('late-chapter-join-before', rows[index - 1], .9)
        add('late-chapter-join-after', join, .1)
    add('membership-ending', rows[-1], exact=edl['frames'] - 240)
    return sorted(selected, key=lambda x: x['frame'])


def extract(ep):
    proof, edl, game, integration = identity(ep)
    delivery = read(OUT / ep / 'delivery.json')
    srt = next(x['path'] for x in delivery['files'] if x['kind'] == 'ko.srt')
    samples = select_samples(ep, edl, game, integration, captions(srt))
    directory = QA / ep / proof['masterSha256'][:16]
    directory.mkdir(parents=True, exist_ok=True)
    for i, sample in enumerate(samples):
        file = directory / f'{i + 1:02d}-{sample["frame"]:06d}.png'
        mobile = file.with_name(file.stem + '-375.png')
        if not file.exists():
            # Integer-second demux seek + exact CFR frame trim, CPU1 only.
            seek = max(0, sample['frame'] // 60 - 2)
            offset = sample['frame'] - seek * 60
            subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-threads', '1', '-ss', str(seek),
                '-i', proof['master'], '-an', '-filter_threads', '1', '-vf', f'select=eq(n\\,{offset})',
                '-frames:v', '1', '-threads', '1', '-y', str(file)], check=True,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        with Image.open(file) as image:
            assert image.size == (1920, 1080)
            if not mobile.exists(): image.resize((375, 211), Image.Resampling.LANCZOS).save(mobile)
        sample.update(file=str(file), mobile=str(mobile), sha256=sha(file), mobileSha256=sha(mobile))
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 17)
    sheets = []
    for offset in range(0, len(samples), 8):
        batch = samples[offset:offset + 8]
        sheet = Image.new('RGB', (1280, math_ceil(len(batch) / 2) * 393), '#141414')
        draw = ImageDraw.Draw(sheet)
        for j, sample in enumerate(batch):
            x, y = j % 2 * 640, j // 2 * 393
            with Image.open(sample['file']) as image: sheet.paste(image.resize((640, 360)), (x, y))
            draw.text((x + 6, y + 363), f"{offset+j+1:02d} | {sample['seconds']:.2f}s | {sample['roles'][0]}", font=font, fill='white')
        file = directory / f'contact-{offset // 8 + 1:02d}.jpg'
        sheet.save(file, quality=92); sheets.append(str(file))
    assert sha(proof['master']) == proof['masterSha256'], 'Master changed while sampling'
    report = {'episode': ep, 'status': 'encoded-frames-generated-inspection-pending', 'proof': proof,
        'qaCodeSha256': sha(__file__),
        'samples': samples, 'contactSheets': sheets, 'extraction': 'FFmpeg CPU1 exact frame from current captioned master',
        'sampleSelection': 'Native game; relationship map; comparison before/after; simultaneous stages; own scene; game analysis; speech extension; late join; ending where present',
        'modelVisualInspection': None, 'fullContinuousPlayback': False, 'humanFullWatch': False,
        'humanFullListening': False, 'publicationRightsApproved': False}
    save(directory / 'samples.json', report)
    save(H / 'visual-qa' / (ep + '.json'), report)
    return {'episode': ep, 'masterSha256': proof['masterSha256'], 'samples': len(samples),
            'contactSheets': sheets, 'report': str(H / 'visual-qa' / (ep + '.json'))}


def math_ceil(x):
    return int(-(-x // 1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--episode')
    parser.add_argument('--check-all', action='store_true')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    ids = read(R / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']['episodes'] if args.check_all else [args.episode]
    results = []
    for ep in ids:
        try:
            if args.check_all or args.check_only:
                p, *_ = identity(ep)
                results.append({'episode': ep, 'readyForSampledVisualQa': True, 'masterSha256': p['masterSha256'],
                                'finalAacReadbackStatus': p['finalAacReadbackStatus']})
            else: results.append(extract(ep))
        except (AssertionError, OSError, KeyError, StopIteration, ValueError) as e:
            results.append({'episode': ep, 'readyForSampledVisualQa': False, 'reason': repr(e)})
    print(json.dumps(results, ensure_ascii=False, indent=2))
