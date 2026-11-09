"""Read back changed passages from finalized AAC using a caller-owned CPU model.

This module never loads a model, generates voice, edits media, or submits work.
Source WAV readback and final mixed AAC readback are distinct evidence records.
"""
from pathlib import Path
import hashlib, json, os, subprocess, time, difflib
import numpy as np
import soundfile as sf

H = Path(__file__).resolve().parent
R = H.parents[3]
L = H / 'local/asr-final-aac'
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/animation-contrast-v5-work/asr-final-aac')
OUT = Path('C:/Users/1/Videos/YamyamCoding/animation-contrast-v5-review')
_hashes = {}

def read(p):
    return json.loads(Path(p).read_text('utf-8-sig'))

def sha(p):
    p = Path(p); s = p.stat(); k = (str(p), s.st_size, s.st_mtime_ns)
    if k not in _hashes:
        with p.open('rb') as f: _hashes[k] = hashlib.file_digest(f, 'sha256').hexdigest()
    return _hashes[k]

def save(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_suffix(p.suffix + '.' + str(os.getpid()) + '.pending')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')
    for attempt in range(50):
        try: os.replace(temp, p); return
        except PermissionError:
            if attempt == 49: raise
            time.sleep(.1)

def norm(s):
    return ''.join(c.lower() for c in s if c.isalnum())

def source_readbacks_current(jobs):
    # Retakes have priority over the longer final-AAC pass. Importing the source
    # helper loads no model; its ready() checks current final-Rendered evidence.
    import asr_changed_passages as source
    if not jobs or sha(source.SOURCE) != jobs[0]['sourceRevisionsSha256']: return False
    for job in jobs:
        proof = source.ready(job)
        if proof is None: return False
        raw = source.L / 'raw' / (job['key'] + '.' + proof['audioSha256'][:12] + '.json')
        if not raw.exists(): return False
    return True

def path(p):
    p = Path(p)
    return p if p.is_absolute() else R / p

def proof_for(ep, expected):
    """Only complete, current masters whose caption/EDL/audio ancestry agrees."""
    delivery_path = OUT / ep / 'delivery.json'
    if not delivery_path.exists(): return None, 'final-delivery-not-ready'
    delivery = read(delivery_path)
    if not delivery.get('localFinalFilesReady'): return None, 'final-delivery-not-ready'
    record = next(x for x in delivery['files'] if x['kind'] == 'captioned.mp4')
    master = path(record['path'])
    if not master.exists() or sha(master) != record['sha256']: return None, 'master-hash-not-current'
    edl_path = H / 'local/explanation-assembly' / ep / 'edl.json'
    plan_path = H / 'local/final-audio' / ep / 'audio-plan.json'
    review_path = plan_path.parent / 'captions/review.json'
    if not all(p.exists() for p in [edl_path, plan_path, review_path]): return None, 'placement-proof-not-ready'
    edl, plan, captions = read(edl_path), read(plan_path), read(review_path)
    if captions['assemblySha256'] != sha(edl_path): return None, 'captions-edl-not-current'
    mix_input = delivery['technicalQa']['audioInput']
    if sha(path(mix_input['source'])) != mix_input['sha256']: return None, 'mix-input-changed'
    if edl['frames'] != delivery['frames']: return None, 'frame-count-mismatch'
    positions = []
    for group in plan['groups']:
        if not group.get('technicalMixVerified'): return None, 'source-mix-verification-pending'
        rows = [x for x in edl['audioEdl'] if x.get('id') in (group['id'], group['id'] + '-audio')]
        if len(rows) != 1: return None, 'placement-not-unique'
        row = rows[0]
        if row.get('sourceSha256') != group['sourceSha256'] or sha(path(group['source'])) != group['sourceSha256']:
            return None, 'replacement-mix-changed'
        for placement in group['placements']:
            target = expected.get((ep, placement['sentenceId']))
            if not target or target['expected'] != placement['ko']: return None, 'script-placement-mismatch'
            if sha(path(placement['take']['path'])) != placement['take']['sha256']: return None, 'source-take-changed'
            start = row['outputStartSample'] + placement['offsetSample']
            end = start + placement['samples']
            assert row['outputStartSample'] <= start < end <= row['outputEndSample']
            positions.append({'sentenceId': placement['sentenceId'], 'expected': placement['ko'],
                'startSample': start, 'endSample': end, 'sampleRate': 48000,
                'sourceTakeSha256': placement['take']['sha256'], 'sourceTake': placement['take']['path'],
                'groupId': group['id'], 'fullTakeUncut': placement['take']['fullTakeRetained'], 'speed': placement['take']['speed']})
    if len(positions) != sum(k[0] == ep for k in expected): return None, 'changed-passage-count-mismatch'
    return {'episode': ep, 'master': str(master), 'masterSha256': record['sha256'],
        'deliveryPath': str(delivery_path), 'deliverySha256': sha(delivery_path),
        'assemblyPath': str(edl_path), 'assemblySha256': sha(edl_path),
        'audioPlanPath': str(plan_path), 'audioPlanSha256': sha(plan_path),
        'mixInput': mix_input, 'positions': positions}, None

def decode_aac(proof):
    master = Path(proof['master'])
    payload = subprocess.check_output(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(master),
        '-map', '0:a:0', '-c:a', 'copy', '-f', 'hash', '-hash', 'sha256', '-'],
        text=True, creationflags=subprocess.CREATE_NO_WINDOW).strip().split('=')[-1]
    decoded = MEDIA / 'decoded' / (proof['episode'] + '.' + payload[:16] + '.wav')
    receipt = decoded.with_suffix('.json')
    if not decoded.exists() or not receipt.exists():
        decoded.parent.mkdir(parents=True, exist_ok=True)
        temporary = decoded.with_suffix('.pending.wav')
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-threads', '2', '-i', str(master),
            '-map', '0:a:0', '-vn', '-c:a', 'pcm_f32le', '-ar', '48000', '-ac', '2', str(temporary)],
            check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        os.replace(temporary, decoded)
        save(receipt, {'aacPayloadSha256': payload, 'decodedAudioSha256': sha(decoded),
            'decoder': 'FFmpeg AAC decode to stereo float32 48000 Hz; original sample order, no gain/speed adjustment'})
    r = read(receipt)
    assert r['decodedAudioSha256'] == sha(decoded)
    return decoded, r

def equivalence(position, text, segment_hash):
    reviews = read(H / 'local/asr-changed/text-review.json')['entries']
    source = next((r for r in reviews if r['episode'] == position['episode'] and r['sentenceId'] == position['sentenceId']
        and r['audioSha256'] == position['sourceTakeSha256'] and r['acceptedForCaptionAlignment']), None)
    aliases = dict(source.get('alignmentAliases', {})) if source else {}
    reviewed_final = None
    review_path = L / 'text-review.json'
    if review_path.exists():
        reviewed_final = next((r for r in read(review_path).get('entries', [])
            if r.get('episode') == position['episode'] and r.get('sentenceId') == position['sentenceId']
            and r.get('segmentSha256') == segment_hash and r.get('recognized') == text
            and r.get('acceptedForReadback') is True), None)
        if reviewed_final: aliases.update(reviewed_final.get('alignmentAliases', {}))
    canonical = text
    for a, b in aliases.items(): canonical = canonical.replace(a, b)
    exact = norm(canonical) == norm(position['expected'])
    sm = difflib.SequenceMatcher(None, norm(position['expected']), norm(canonical), autojunk=False)
    return {'acceptedSemanticReadback': exact, 'reviewedAliases': aliases,
        'additionalFinalTextReview': reviewed_final,
        'differences': [{'kind': tag, 'expected': norm(position['expected'])[i:j], 'recognized': norm(canonical)[k:l]}
            for tag, i, j, k, l in sm.get_opcodes() if tag != 'equal'],
        'reviewScope': 'Independent final AAC ASR text compared with expected text and previously reviewed source-take spelling aliases; not human listening',
        'humanListening': False}

def alternate_readbacks(recognize, jobs, stop_requested):
    """One explicitly requested beam5 read per source hash; no acceptance shortcut."""
    import asr_changed_passages as source
    request_path = source.L / 'alternate-decode-requests.json'
    if not request_path.exists(): return False
    request = read(request_path); rows = []; progressed = False
    for target in request['targets']:
        if stop_requested(): break
        job = next(j for j in jobs if j['episode'] == target['episode'] and j['sentenceId'] == target['sentenceId'])
        proof = source.ready(job)
        if proof is None or proof['audioSha256'] != target['audioSha256']:
            rows.append(dict(target, state='requested-take-not-current-ready')); continue
        file = source.L / 'alternate-beam5' / (job['key'] + '.' + proof['audioSha256'][:12] + '.json')
        if file.exists(): result = read(file)
        else:
            print('ALTERNATE BEAM5 ASR', job['episode'], job['sentenceId'], flush=True)
            raw = recognize(str(job['wav']), generate_kwargs={'language': 'korean', 'task': 'transcribe', 'num_beams': 5, 'do_sample': False},
                return_timestamps='word', batch_size=1)
            if sha(job['wav']) != proof['audioSha256']:
                rows.append(dict(target, state='take-changed-during-alternate-readback')); continue
            result = {'episode': job['episode'], 'sentenceId': job['sentenceId'], 'key': job['key'],
                'audio': source.rel(job['wav']), 'audio_sha256': proof['audioSha256'], 'duration': proof['duration'],
                'text': raw['text'], 'chunks': raw.get('chunks', []), 'model': 'same caller-owned local whisper-large-v3-turbo',
                'device': 'cpu', 'threads': 2, 'batchSize': 1, 'numBeams': 5, 'doSample': False,
                'expectedTextPromptSupplied': False, 'humanListening': False,
                'semanticStatus': 'pending-model-comparison; no automatic approval from alternate decoding'}
            save(file, result); progressed = True
            print('ALTERNATE BEAM5 READBACK', job['episode'], job['sentenceId'], result['text'], flush=True)
        rows.append(dict(target, state='alternate-readback-persisted', expected=job['expected'], recognized=result['text'],
            asrPath=str(file), asrSha256=sha(file), humanListening=False))
    save(source.L / 'alternate-beam5-index.json', {'scope': request['scope'], 'entries': rows,
        'oneExistingCpuModel': True, 'expectedTextPromptSupplied': False, 'humanListening': False})
    return progressed

def run_once(recognize, jobs, stop_requested=lambda: False):
    """Called after source takes finish; reuses the exact already-loaded model."""
    expected = {(j['episode'], j['sentenceId']): j for j in jobs}
    control = read(R / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    episodes = control['episodes']; assert len(episodes) == 17 and 'A03' not in episodes
    progressed = alternate_readbacks(recognize, jobs, stop_requested)
    all_rows, waiting, complete_episodes = [], {}, []
    for ep in episodes:
        if stop_requested(): break
        if not source_readbacks_current(jobs):
            waiting['sourceReadbackPriority'] = 'A source take changed or is active; return the same model to source ASR first'
            break
        try:
            proof, reason = proof_for(ep, expected)
            if reason: waiting[ep] = reason; continue
            if not proof['positions']:
                complete_episodes.append(ep); continue
            decoded, decoded_proof = decode_aac(proof)
            info = sf.info(decoded); assert info.samplerate == 48000 and info.channels == 2
            episode_rows = []
            for pos in proof['positions']:
                if stop_requested(): break
                if not source_readbacks_current(jobs):
                    waiting['sourceReadbackPriority'] = 'A source take changed during final AAC review; source ASR resumes at this saved boundary'
                    break
                pos = dict(pos, episode=ep)
                assert pos['fullTakeUncut'] and pos['speed'] == 1.0 and pos['endSample'] <= info.frames
                samples, rate = sf.read(decoded, start=pos['startSample'], stop=pos['endSample'], dtype='float32', always_2d=True)
                assert len(samples) == pos['endSample'] - pos['startSample'] and np.isfinite(samples).all()
                segment = MEDIA / 'segments' / (ep + 'S' + pos['sentenceId'] + '.' + decoded_proof['aacPayloadSha256'][:16] + '.' + str(pos['startSample']) + '-' + str(pos['endSample']) + '.wav')
                segment.parent.mkdir(parents=True, exist_ok=True)
                if not segment.exists(): sf.write(segment, samples, rate, subtype='FLOAT')
                segment_hash = sha(segment)
                raw_path = L / 'raw' / (ep + 'S' + pos['sentenceId'] + '.' + segment_hash[:16] + '.json')
                if raw_path.exists(): result = read(raw_path)
                else:
                    print('FINAL AAC ASR', ep, pos['sentenceId'], f'{len(samples)/rate:.2f}s', flush=True)
                    raw = recognize(str(segment), generate_kwargs={'language': 'korean', 'task': 'transcribe'}, return_timestamps='word', batch_size=1)
                    if sha(proof['master']) != proof['masterSha256']: raise RuntimeError('Master changed during AAC readback; discard unsaved result')
                    result = {'episode': ep, 'sentenceId': pos['sentenceId'], 'audio': str(segment), 'audioSha256': segment_hash,
                        'text': raw['text'], 'chunks': raw.get('chunks', []), 'model': 'local whisper-large-v3-turbo',
                        'device': 'cpu', 'threads': 2, 'batchSize': 1, 'expectedTextPromptSupplied': False,
                        'humanListening': False, 'createdAt': time.time()}
                    save(raw_path, result); progressed = True
                    print('FINAL AAC READBACK', ep, pos['sentenceId'], result['text'], flush=True)
                row = dict(pos, recognized=result['text'], masterSha256=proof['masterSha256'], master=proof['master'],
                    assemblySha256=proof['assemblySha256'], audioPlanSha256=proof['audioPlanSha256'],
                    decodedAudio=decoded_proof, segmentSha256=segment_hash, asrPath=str(raw_path), asrSha256=sha(raw_path),
                    comparison=equivalence(pos, result['text'], segment_hash))
                episode_rows.append(row)
            all_rows += episode_rows
            if len(episode_rows) == len(proof['positions']):
                complete_episodes.append(ep)
                save(L / 'episodes' / (ep + '.json'), {'proof': proof, 'entries': episode_rows,
                    'allChangedPassagesReadBack': True, 'allSemanticReadbacksAccepted': all(x['comparison']['acceptedSemanticReadback'] for x in episode_rows),
                    'unchangedNarrationReprocessed': False, 'humanListening': False})
        except (OSError, ValueError, KeyError, AssertionError, RuntimeError, subprocess.CalledProcessError) as exc:
            waiting[ep] = repr(exc)
    complete = len(complete_episodes) == len(episodes)
    save(L / 'index.json', {'status': 'complete-changed-passages-readback' if complete else 'waiting-for-current-final-masters',
        'expectedEpisodes': episodes, 'completedEpisodes': complete_episodes, 'waiting': waiting,
        'expectedPassages': len(jobs), 'completedPassages': len(all_rows), 'entries': all_rows,
        'pendingTextDifferences': [x for x in all_rows if not x['comparison']['acceptedSemanticReadback']],
        'oneCallerOwnedCpuModel': True, 'gpuUsed': False, 'humanListening': False})
    return complete, progressed
