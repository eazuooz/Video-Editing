"""Prepare one new Teardown audio attempt; never generate/transcribe/render media.

--check validates the staged change and six unchanged raw takes without mutation.
--apply is coordinator-only at the exact selected project/revision safe boundary.
Old audio-v1 and raw ASR remain in place. No pronunciation alias is created.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
C = Path('C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/shorts-teardown-spray-palette/local')
PACKET = C / 'repairs/first-paragraph-ti-v2'
PACKAGE_SHA256 = 'e0940d5d52c4106a28a55213a13931c69ddf24f07866d4503c11e8d95b0ebaab'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_new(path, document):
    with Path(path).open('x', encoding='utf8') as stream:
        stream.write(json.dumps(document, ensure_ascii=False, indent=2) + '\n')


def verify_package():
    if sha(PACKET / 'package.json') != PACKAGE_SHA256:
        raise RuntimeError('Repair package changed; preserve and re-review it.')
    package = read(PACKET / 'package.json')
    if (package['slug'] != P.name or package['revision'] != 'spray-palette-v1'
            or Path(package['newAudioDirectory']).resolve() != (C / 'audio-v2').resolve()
            or Path(package['oldAudioDirectory']).resolve() != (C / 'audio-v1').resolve()
            or (C / 'audio-v2').exists() or (PACKET / 'apply-started.json').exists()):
        raise RuntimeError('Attempt already exists or repair scope changed; inspect without overwriting.')
    for item in package['files']:
        target, staged = Path(item['target']), Path(item['stagedPath'])
        if (target != P / item['relative'] or not target.resolve().is_relative_to(P.resolve())
                or not staged.resolve().is_relative_to((PACKET / 'after').resolve())
                or sha(target) != item['beforeSha256'] or sha(staged) != item['afterSha256']):
            raise RuntimeError('A live or staged input changed: ' + item['relative'])
        if target.suffix == '.py':
            compile(staged.read_bytes(), str(staged), 'exec')
    old = C / 'audio-v1'
    if (sha(old / 'voice/narration.wav') != package['oldVoiceSha256']
            or sha(old / 'asr-voice-edce6c2bd87a.json') != package['oldASRSha256']):
        raise RuntimeError('Existing complete voice or raw ASR changed.')
    old_receipt = read(old / 'reuse-takes.json')
    staged_script = read(PACKET / 'after/script/narration.spoken.ko.json')
    lines = [line for scene in staged_script['scenes'] for line in scene['lines']]
    expected_names = {f'main-{index:02}.wav' for index in range(2, 8)}
    if {item['name'] for item in package['sixUnchangedTakes']} != expected_names:
        raise RuntimeError('Exactly six unaffected raw takes must be preserved.')
    for item in package['sixUnchangedTakes']:
        source = Path(item['source'])
        if (source != old / 'voice/chunks' / item['name'] or sha(source) != item['sha256']
                or old_receipt['takes'][item['name']] != item['record']
                or item['record']['text'] != lines[int(item['name'][5:7]) - 1]):
            raise RuntimeError('An unchanged take is not byte-identical to its original receipt.')
    manifest = read(PACKET / 'after/production/tts-manifest.json')
    receipt = package['newReuseReceipt']
    identity = receipt['inputLocks']
    if (set(receipt['takes']) != expected_names
            or identity['manifestSha256'] != sha(PACKET / 'after/production/tts-manifest.json')
            or identity['scriptSha256'] != sha(PACKET / 'after/script/narration.spoken.ko.json')
            or manifest['tts']['outputDir'] != f'projects/{P.name}/production/local/audio-v2/voice'):
        raise RuntimeError('New attempt reuse identity is inconsistent.')
    return package


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    from audio_revision import guard, assert_no_game_apps, LEASE
    guard(require_current_selection=args.apply)
    package = verify_package()
    if args.check:
        print(json.dumps({'packageSha256': PACKAGE_SHA256, 'checked': True,
                          'filesToUpdate': len(package['files']), 'takesToReuse': 6,
                          'oldAudioPreserved': True, 'writes': 0, 'mediaJobs': 0}))
        return
    assert_no_game_apps()
    if LEASE.exists():
        raise RuntimeError('Wait for the coordinator serial boundary; never alter a live GPU lease.')
    # Capture every old audio file hash before any mutation; leave the whole tree untouched.
    old_files = [{'path': str(path), 'sha256': sha(path)}
                 for path in sorted((C / 'audio-v1').rglob('*')) if path.is_file()]
    before = PACKET / 'before'
    before.mkdir(exist_ok=False)
    for item in package['files']:
        backup = before / item['relative']
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item['target'], backup)
        if sha(backup) != item['beforeSha256']:
            raise RuntimeError('Input backup verification failed; no target changed.')
    write_new(PACKET / 'apply-started.json', {
        'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'packageSha256': PACKAGE_SHA256, 'oldAudioFiles': old_files,
        'state': 'preparing-new-attempt-no-media-generation'})
    new = C / 'audio-v2'
    chunks = new / 'voice/chunks'
    chunks.mkdir(parents=True, exist_ok=False)
    for item in package['sixUnchangedTakes']:
        target = chunks / item['name']
        shutil.copy2(item['source'], target)
        if sha(target) != item['sha256']:
            raise RuntimeError('Copied raw take hash differs; no new media job is permitted.')
    write_new(new / 'reuse-takes.json', package['newReuseReceipt'])
    for item in package['files']:
        target = Path(item['target'])
        temporary = target.with_name(target.name + '.ti-v2-writing')
        with temporary.open('xb') as stream:
            stream.write(Path(item['stagedPath']).read_bytes())
        os.replace(temporary, target)
        if sha(target) != item['afterSha256']:
            raise RuntimeError('Applied input hash differs; stop before any generation.')
    for item in old_files:
        if sha(item['path']) != item['sha256']:
            raise RuntimeError('Old audio-v1 must remain byte-identical.')
    # New process avoids stale imported constants. Both checks are read-only; no device/model load.
    result = subprocess.run([sys.executable, '-B', '-X', 'utf8', '-c',
        "import sys;sys.path.insert(0,r'" + str(P / 'production') + "');"
        "import audio_revision,visual_revision;audio_revision.guard();visual_revision.static_guard();"
        "print('updated-audio-and-picture-input-guards-passed')"], cwd=R, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('Repair remains preserved but requires inspection before generation: ' + result.stderr[-3000:])
    write_new(PACKET / 'applied.json', {
        'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'packageSha256': PACKAGE_SHA256, 'state': 'prepared-audio-v2-first-take-only',
        'oldAudioAllHashesUnchanged': True, 'sixCopiedRawTakes': package['sixUnchangedTakes'],
        'newFirstTakeExists': (chunks / 'main-01.wav').exists(), 'mediaJobsStarted': 0,
        'validation': result.stdout.strip(), 'actualListening': 'pending',
        'next': 'Coordinator render-voice.py; then new whole-input ASR and strict current-hash captions.'})
    print('Prepared audio-v2 with six exact raw takes; audio-v1 preserved; no media generation started.')


if __name__ == '__main__':
    main()
