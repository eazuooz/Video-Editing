"""Prepare/preserve the exact prior BGM mix. Default is read-only; --execute archives.

Never moves original narration, chunks, captions, timing or voice-ASR reports.
Original mix-ASR reports remain at their existing paths and are also copied.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil

from audio_revision import L, VOICE, R, MEDIA_ROOT, guard, assert_no_game_apps, LEASE

PRIOR_MIX = '53620cdd2b75552881428344a35211d150123c66cb1973f8551e13fb77381dfb'
VOICE_SHA = '81585b4dd719b142e607111951952d27bbee6646b841f98d1628a6b5770a3456'
SOURCE_SHA = 'd1670b4532efcc7f3227a530e386e111a2623ca0477a8af3a168a8234287adc6'
NAMES = {
    'narration-source-timeline.wav', 'narration-prepared-stem.wav', 'narration-stem.wav',
    'game-stem.wav', 'music-stem.wav', 'background-stem.wav', 'final-mix.wav', 'final-mix.m4a',
}


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def plan():
    active = L.resolve()
    expected = (MEDIA_ROOT / 'local/audio-v2').resolve()
    if active != expected:
        raise RuntimeError('Refuse archive outside this exact owned audio-v2 directory.')
    if sha(VOICE) != VOICE_SHA:
        raise RuntimeError('Current narration changed; no archive performed.')
    build = read(active / 'audio-build.json')
    if (set(build['artifacts']) != NAMES
            or build['artifacts']['final-mix.m4a']['sha256'] != PRIOR_MIX
            or build['recipe']['scriptSha256'] != SOURCE_SHA):
        raise RuntimeError('Only the exact original attempted mix may be archived by this helper.')
    destination = active / 'mix-archive' / PRIOR_MIX
    if not destination.resolve().is_relative_to(active) or destination.exists():
        raise RuntimeError('Archive destination already exists or escaped the owned directory; preserve it.')
    rows = []
    for name, entry in build['artifacts'].items():
        source = (R / entry['path']).resolve()
        if source != active / name or sha(source) != entry['sha256']:
            raise RuntimeError('Prior successful artifact path/hash changed: ' + name)
        rows.append({'name': name, 'source': str(source), 'sha256': entry['sha256'], 'action': 'move'})
    for name in ['audio-build.json', 'audio-continuity.json']:
        source = active / name
        if read(source).get('fingerprint') != build['fingerprint']:
            raise RuntimeError('Prior mix evidence fingerprint changed: ' + name)
        rows.append({'name': name, 'source': str(source), 'sha256': sha(source), 'action': 'move'})
    for source in sorted(active.glob('asr-mix-' + PRIOR_MIX[:12] + '*')):
        if source.parent.resolve() != active or source.suffix not in ['.json', '.wav'] or not source.is_file():
            raise RuntimeError('Unexpected prior mix-ASR path.')
        rows.append({'name': source.name, 'source': str(source), 'sha256': sha(source), 'action': 'copy'})
    original_source = MEDIA_ROOT / 'local/qa/bgm-dip-preparation/finish-audio.before.py'
    if sha(original_source) != SOURCE_SHA:
        raise RuntimeError('Original mix recipe source snapshot changed.')
    rows.append({'name': 'finish-audio.py', 'source': str(original_source.resolve()), 'sha256': SOURCE_SHA, 'action': 'copy'})
    return destination, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='After the parent serial job is idle, preserve the exact prior mix.')
    args = parser.parse_args()
    destination, rows = plan()
    record = {'schemaVersion': 1, 'priorMixSha256': PRIOR_MIX, 'voiceSha256': VOICE_SHA,
              'archive': str(destination), 'files': rows, 'originalNarrationCaptionTimingUntouched': True}
    if not args.execute:
        print(json.dumps({**record, 'readOnly': True, 'filesMoved': 0}, ensure_ascii=False, indent=2))
        return
    guard()
    assert_no_game_apps()
    if LEASE.exists():
        raise RuntimeError('A costly-job lease is active; archive after the parent job finishes.')
    # All final absolute sources/destinations were checked before any mutation.
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'archive-plan.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    for row in rows:
        source, target = Path(row['source']), destination / row['name']
        if sha(source) != row['sha256'] or target.exists():
            raise RuntimeError('An archive input changed; preserve the partial archive for inspection.')
        if row['action'] == 'move':
            source.rename(target)
        else:
            shutil.copy2(source, target)
        if sha(target) != row['sha256']:
            raise RuntimeError('Archive copy hash differs; stop and preserve every file.')
    if sha(VOICE) != VOICE_SHA:
        raise RuntimeError('Narration changed concurrently; archive preserved, do not mix.')
    record.update(status='preserved-exact-original-mix', completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (destination / 'archive-complete.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'archive': str(destination), 'filesPreserved': len(rows), 'narrationUnchanged': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
