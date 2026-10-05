"""Produce one review pair only after direct current mixed-ASR comparison."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, time, traceback

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
W = BASE / 'final-v1'
FF = Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
FP = FF.with_name('ffprobe.exe')
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    digest = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()
STATE = W / 'review-pair-execution.json'
assert not STATE.exists()
plan = read(W / 'plan.json')
visual = read(W / 'visual-build.json')
mix = read(W / 'mix-settings.json')
review = read(W / 'full-mix-asr-review.json')
assert review['technicallyApproved'] and review['all26WindowsDirectlyCompared']
assert review['currentMixedAudioSha256'] == mix['wavSha256']
assert mix['planSha256'] == visual['planSha256'] == sha(W / 'plan.json')
assert plan['finalTimingApproved'] and plan['bodyRatioApproved']
assert sha(ROOT / visual['video']) == visual['sha256']
assert sha(W / 'final-mix.m4a') == mix['aacSha256']
clean = W / 'making-game-sequels.clean.review.mp4'
captioned = W / 'making-game-sequels.captioned.review.mp4'
assert not clean.exists() and not captioned.exists()
state = dict(schemaVersion=1, pid=os.getpid(), sessionId=None, startedAt=now(),
             status='preparing-current-review-pair', cpuThreads=2, gpuJobs=0,
             commands=[], activeTasks=[], rendered=False, qaApproved=False,
             finalFixedCaptionPixelsReviewed=False, sourceAudioStreams=0)


def write(p, data):
    temp = p.with_name(p.name + f'.{os.getpid()}.writing')
    for n in range(120):
        try:
            temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            os.replace(temp, p)
            return
        except OSError:
            if n == 119:
                raise
            time.sleep(.25)


def checkpoint():
    session = W / 'review-pair-session.json'
    if session.exists() and read(session).get('pid') == os.getpid():
        state['sessionId'] = read(session)['sessionId']
    state['observedAt'] = now()
    write(STATE, state)
    qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
    q = read(qp)
    item = next(r for r in q['items'] if r['slug'] == 'making-game-sequels')
    item.update(stage='current13-guided60-review-pair-and-final-QA', updatedAt=state['observedAt'],
                nextAction='Inspect every current encoded caption/cut and compositions; verify exact PTS, both decodes, identical AAC and mix loudness before collection, single private settings and Git.')
    running = 'endedAt' not in state
    item['execution'].update(status=state['status'], phase=item['stage'], observedAt=state['observedAt'],
                             pid=os.getpid(), sessionId=state['sessionId'], alive=running, state=rel(STATE),
                             commandLine='render-reviewed-pair-v1.py CPU2/GPU0', activeTasks=state['activeTasks'],
                             cpuProductionJobs=int(running), primaryCpuProductionJobs=int(running),
                             gpuSynthesisJobs=0, renderJobs=int(running), uploads=0)
    item.update(finalMixAsrApproved=True, rendered=state['rendered'], qaApproved=False,
                collected=False, privateUploaded=False, allFinalPixelsApproved=False)
    q['updatedAt'] = item['updatedAt']
    write(qp, q)
    for p in [BASE / 'latest-checkpoint.json', ROOT / 'production/batches/sakurai-planning-game-design/proof-making-game-sequels/latest-checkpoint.json']:
        data = read(p)
        for key in ['stage', 'updatedAt', 'nextAction', 'execution', 'finalMixAsrApproved', 'rendered', 'qaApproved', 'collected', 'privateUploaded', 'allFinalPixelsApproved']:
            data[key] = item[key]
        write(p, data)


def run(exe, args, kind):
    log = W / f'review-pair-{len(state["commands"])+1:03d}.log'
    command = [str(exe), *map(str, args)]
    with log.open('w', encoding='utf-8') as out:
        child = subprocess.Popen(command, cwd=W, stdout=out, stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        state.update(status=kind, activeTasks=[dict(kind=kind, pid=child.pid, command=command, log=rel(log))])
        checkpoint()
        code = child.wait()
    state['commands'].append(dict(command=command, pid=child.pid, exitCode=code, log=rel(log)))
    state['activeTasks'] = []
    checkpoint()
    assert code == 0, f'{kind}: exit{code}; retain output/log without repeated encoding'
    return log.read_text(encoding='utf-8')


def ff(args, kind):
    return run(FF, ['-v', 'error', '-nostdin', '-threads', '2', *args], kind)


try:
    checkpoint()
    ff(['-i', ROOT / visual['video'], '-i', W / 'final-mix.m4a', '-map', '0:v:0', '-map', '1:a:0',
        '-c', 'copy', '-video_track_timescale', '90000', '-movflags', '+faststart', clean], 'CPU-clean-copy-current-visual-and-AAC')
    ff(['-i', clean, '-map', '0:v:0', '-map', '0:a:0', '-filter_threads', '1', '-vf', 'ass=captions.ko.ass',
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-threads', '2', '-pix_fmt', 'yuv420p',
        '-fps_mode', 'passthrough', '-frames:v', '35583', '-video_track_timescale', '90000',
        '-c:a', 'copy', '-movflags', '+faststart', captioned], 'CPU-fixed-Korean-caption-review-encode')
    records = []
    for p in [clean, captioned]:
        probe = json.loads(run(FP, ['-v', 'error', '-threads', '2', '-count_frames', '-show_streams',
                                   '-show_format', '-of', 'json', p], 'CPU-count-current-review-pair'))
        video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        assert len(probe['streams']) == 2 and int(video['nb_read_frames']) == 35583
        assert video['width'] == 1920 and video['height'] == 1080 and video['avg_frame_rate'] == '60/1'
        assert abs(float(probe['format']['duration']) - 593.05) <= .017
        packet_clock = json.loads(run(FP, ['-v', 'error', '-select_streams', 'v:0', '-show_packets',
            '-show_entries', 'packet=pts,duration', '-of', 'json', p], 'CPU-exact-presentation-packet-clock'))['packets']
        assert video['time_base'] == '1/90000' and len(packet_clock) == 35583
        assert sorted(int(packet['pts']) for packet in packet_clock) == list(range(0, 35583 * 1500, 1500))
        assert all(int(packet['duration']) == 1500 for packet in packet_clock)
        assert not ff(['-i', p, '-f', 'null', '-'], 'CPU-whole-current-review-decode').strip()
        audio_hash = ff(['-i', p, '-map', '0:a:0', '-c:a', 'copy', '-f', 'hash', '-hash', 'sha256', '-'], 'CPU-current-AAC-payload-hash').strip()
        assert audio_hash.startswith('SHA256=')
        records.append(dict(path=rel(p), sha256=sha(p), probe=probe, wholeDecodeExitCode=0,
            exactPresentationClock=dict(timeBase='1/90000', count=35583, firstPts=0,
                lastPts=35582 * 1500, step=1500, allPacketPtsExact=True), aacPayloadHash=audio_hash))
    original_audio_hash = ff(['-i', W / 'final-mix.m4a', '-map', '0:a:0', '-c:a', 'copy', '-f', 'hash', '-hash', 'sha256', '-'], 'CPU-source-AAC-payload-hash').strip()
    assert records[0]['aacPayloadHash'] == records[1]['aacPayloadHash'] == original_audio_hash
    write(W / 'review-pair-build.json', dict(createdAt=now(), planSha256=sha(W / 'plan.json'),
        captionAssSha256=sha(W / 'captions.ko.ass'), sourceMixAacSha256=mix['aacSha256'],
        records=records, frames=35583, seconds=593.05, identicalAacPayload=True,
        inheritedSameAacLufs=-16.04, inheritedSameAacTruePeakDbtp=-1.98,
        allFinalFixedCaptionPixelsReviewed=False, qaApproved=False, completedVideo=False))
    state.update(status='closed-review-pair-built-final-caption-and-cut-QA-pending', rendered=True,
                 endedAt=now(), exitCode=0, activeTasks=[])
    checkpoint()
except BaseException:
    state.update(status='closed-review-pair-failed', endedAt=now(), exitCode=1,
                 error=traceback.format_exc(), activeTasks=[])
    checkpoint()
    raise
