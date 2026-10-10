"""Preserve observed official clips and acquire one observed official match, once."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, shutil, subprocess, sys, traceback
import psutil

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
LOCAL = ROOT / 'shared/output/character-parameters/preflight'
MEDIA = ROOT / 'shared/assets/character-parameters/raw'
STATE = PROOF / 'official-acquisition-execution-v1.json'
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
FFDIR = 'C:/ProgramData/HP/LCDDisplayHelper/bin'
QUEUE = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
stamp = lambda: datetime.now(timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, value):
    temp = p.with_name(p.name + f'.{os.getpid()}.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, p)

if STATE.exists():
    raise SystemExit('Existing execution: inspect it, do not rerun completed acquisition.')
subprocess.run([NODE, 'scripts/review-video-duplicates.cjs', 'character-parameters', '--check'], cwd=ROOT, check=True)
LOCAL.mkdir(parents=True, exist_ok=True)
MEDIA.mkdir(parents=True, exist_ok=True)
(LOCAL / 'source-info').mkdir(exist_ok=True)
state = {
    'schemaVersion': 1, 'slug': 'character-parameters', 'status': 'initializing',
    'startedAt': stamp(), 'pid': os.getpid(), 'processCreateTime': psutil.Process().create_time(),
    'commandLine': sys.argv, 'workingDirectory': str(ROOT), 'sessionId': None,
    'sourceOwner': 'Aether Studios / Dan Fornace', 'children': [], 'sources': [],
    'gpuJobs': 0, 'sourceAdoptionApproved': False, 'fullDecode': False,
    'directNativeReview': False, 'scriptCreated': False, 'ttsStarted': False,
    'externalResearchChanges': 0,
    'cuaMatchDownload': {'result': '60-second tool timeout; no completed file observed in Downloads',
                         'repeatedBrowserDownload': False, 'fileAdopted': False},
    'rights': {'officialPolicyUrl': 'https://rivalsofaether.com/press/',
               'officialPolicyTextDirectlyRead': True, 'commercialGameContentsPermissionObserved': True,
               'recordingOwnerDirectlyObserved': True, 'sourceAudioForFinal': 'exclude-all',
               'finalPublicRightsHumanReview': False},
}

def save(status):
    state['status'] = status
    state['updatedAt'] = stamp()
    session = STATE.with_name(STATE.name + '.session.json')
    if session.exists():
        s = json.loads(session.read_text(encoding='utf-8-sig'))
        if s.get('pid') == os.getpid():
            state['sessionId'] = s.get('sessionId')
    write(STATE, state)
    before = QUEUE.read_bytes()
    q = json.loads(before)
    item = next(x for x in q['items'] if x['slug'] == 'character-parameters')
    if item.get('videoId') or any(item['checkpoints'].values()):
        raise RuntimeError('Character item advanced: refusing preflight overwrite')
    item.update(status='in-progress', stage='official-source-' + status, updatedAt=state['updatedAt'])
    item['execution'] = {k: state[k] for k in ('status', 'pid', 'processCreateTime', 'commandLine', 'workingDirectory', 'sessionId', 'children', 'gpuJobs')}
    item['execution'].update(phase='official-source-acquisition-only', state=str(STATE.relative_to(ROOT)).replace('\\', '/'))
    item['duplicateReview'] = {'decision': 'distinct', 'evidence': 'production/batches/sakurai-planning-game-design/proof-character-parameters/content-studio-direct-review-v1.json'}
    item['nextAction'] = 'Single CPU2/GPU0 decode and native PTS/action/UI review of obtained official sources; secure sufficient unique concept-matched action before narration.'
    q['currentSlug'] = 'character-parameters'
    q['nextSlug'] = 'character-parameters'
    q['updatedAt'] = q['lastProgressAt'] = state['updatedAt']
    q['progress']['inProgress'] = 1
    q['progress']['queued'] = 6
    if QUEUE.read_bytes() != before:
        raise RuntimeError('Concurrent queue changed; preserve it and reconcile after worker')
    write(QUEUE, q)

try:
    save('preserving-clip-downloads')
    dom = json.loads((LOCAL / 'rivals-official-media-dom-v1.json').read_text(encoding='utf-8-sig'))
    for char in ('zetterburn', 'orcane', 'forsburn'):
        for num in (1, 2):
            name = f'{char}-gameplay{num}.mp4'
            src = Path('C:/Users/eazuo/Downloads') / name
            dst = MEDIA / name
            observed = [v for v in dom['videos'] if any(s.endswith('/' + name) for s in v['sources'])]
            if len(observed) != 1 or not src.is_file():
                raise RuntimeError('Missing observed original: ' + name)
            if dst.exists():
                if sha(dst) != sha(src):
                    raise RuntimeError('Existing file differs, preserve both: ' + name)
            else:
                shutil.copy2(src, dst)
            state['sources'].append({'kind': 'official-character-page-clip', 'character': char,
                                     'downloadPath': str(src), 'localPath': str(dst.relative_to(ROOT)).replace('\\', '/'),
                                     'sourceUrl': observed[0]['sources'][0], 'browserNominalDuration': observed[0]['duration'],
                                     'bytes': dst.stat().st_size, 'sha256': sha(dst), 'downloadOriginalPreserved': True,
                                     'decodeApproved': False, 'adopted': False})
    save('match-download-running')
    target = MEDIA / 'gBbKFYZYvbc.mp4'
    if target.exists():
        raise RuntimeError('A match file already exists; inspect before acquisition')
    args = [sys.executable, '-m', 'yt_dlp', '--no-playlist', '--write-info-json', '--no-write-thumbnail',
            '--http-chunk-size', '1M', '--retries', '2', '--fragment-retries', '2', '--socket-timeout', '30',
            '--js-runtimes', 'node:' + NODE, '--ffmpeg-location', FFDIR,
            '-f', 'bv*[height<=1080][vcodec^=avc]+ba[ext=m4a]/b[height<=1080][ext=mp4]/bv*[height<=1080]+ba',
            '--merge-output-format', 'mp4', '--paths', 'infojson:' + str(LOCAL / 'source-info'),
            '-o', str(MEDIA / '%(id)s.%(ext)s'), 'https://www.youtube.com/watch?v=gBbKFYZYvbc']
    log_path = LOCAL / 'gBbKFYZYvbc-download-v1.log'
    with log_path.open('wb') as log:
        child = subprocess.Popen(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        c = {'pid': child.pid, 'processCreateTime': psutil.Process(child.pid).create_time(),
             'commandLine': args, 'workingDirectory': str(ROOT), 'status': 'running', 'log': str(log_path.relative_to(ROOT)).replace('\\', '/')}
        state['children'].append(c)
        save('match-download-running')
        code = child.wait()
        c.update(exitCode=code, status='exited', endedAt=stamp())
    if code:
        raise RuntimeError(f'Official match acquisition exited {code}; read preserved log')
    infos = list((LOCAL / 'source-info').glob('gBbKFYZYvbc*.info.json'))
    if len(infos) != 1 or not target.is_file():
        raise RuntimeError('Missing completed match or metadata')
    info = json.loads(infos[0].read_text(encoding='utf-8'))
    if info['id'] != 'gBbKFYZYvbc' or info.get('channel_id') != 'UCjJe1z4OSKKav9MLVEvXWfA':
        raise RuntimeError('Official owner/id mismatch')
    state['sources'].append({'kind': 'official-tournament-recording', 'sourceVideoId': info['id'],
                             'sourceUrl': info['webpage_url'], 'channel': info['channel'], 'channelId': info['channel_id'],
                             'title': info['title'], 'uploadDate': info.get('upload_date'), 'nominalDuration': info.get('duration'),
                             'localPath': str(target.relative_to(ROOT)).replace('\\', '/'), 'bytes': target.stat().st_size,
                             'sha256': sha(target), 'metadata': str(infos[0].relative_to(ROOT)).replace('\\', '/'),
                             'decodeApproved': False, 'adopted': False})
    save('downloaded-awaiting-decode-and-native-review')
    print(json.dumps({'status': state['status'], 'sources': len(state['sources']), 'sourceAdoption': False}, ensure_ascii=False), flush=True)
except BaseException as e:
    state['error'] = traceback.format_exc()
    try:
        save('failed')
    except Exception:
        write(STATE, state)
    print(state['error'], flush=True)
    sys.exit(1)
