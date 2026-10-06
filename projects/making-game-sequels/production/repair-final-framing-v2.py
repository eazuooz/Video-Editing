"""Repair two observed hotbar collisions; preserve all timing, narration and sources."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, os, shutil, subprocess, time, traceback

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
OLD = BASE / 'final-v1'
W = BASE / 'final-v2'
FF = Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
FP = FF.with_name('ffprobe.exe')
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: p.relative_to(ROOT).as_posix()

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def write(p, d):
    t = p.with_name(p.name + f'.{os.getpid()}.writing')
    for n in range(120):
        try:
            t.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            os.replace(t, p)
            return
        except OSError:
            if n == 119: raise
            time.sleep(.25)

ledger = read(OLD / 'encoded-pixel-direct-review.json')
assert ledger['reviewedSheetCount'] == 124 and ledger['reviewedImageCount'] == 744
assert not ledger['allFinalPixelsApproved']
assert ledger['unresolvedIssues'] and len(ledger['unresolvedIssues']) == 2
old_plan = read(OLD / 'plan.json')
old_visual = read(OLD / 'visual-build.json')
mix = read(OLD / 'mix-settings.json')
asr = read(OLD / 'full-mix-asr-review.json')
assert asr['technicallyApproved'] and asr['all26WindowsDirectlyCompared']
assert asr['currentMixedAudioSha256'] == mix['wavSha256']
assert old_visual['planSha256'] == mix['planSha256'] == sha(OLD / 'plan.json')
assert sha(OLD / 'final-mix.m4a') == mix['aacSha256']
assert not W.exists(), 'Preserve previous revision; never silently repeat this job.'
W.mkdir()
(W / 'framed-native').mkdir()
STATE = W / 'repair-execution.json'
ids = ['08-p1-action-28-26280-26580', '08-p3-action-28-26580-26820']
state = dict(schemaVersion=1, startedAt=now(), pid=os.getpid(), sessionId=None,
    status='scoped-hotbar-framing-repair', cpuThreads=2, gpuJobs=0, activeTasks=[], commands=[],
    newGitImages=0, rendered=False, qaApproved=False, changedSegments=ids,
    retainedMixedAsr=rel(OLD / 'full-mix-asr-review.json'))

def checkpoint():
    sp = W / 'repair-session.json'
    if sp.exists() and read(sp).get('pid') == os.getpid(): state['sessionId'] = read(sp)['sessionId']
    state['observedAt'] = now()
    write(STATE, state)
    qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
    q = read(qp); item = next(i for i in q['items'] if i['slug'] == 'making-game-sequels')
    item.update(stage='current13-guided60-two-hotbar-framing-repair', updatedAt=state['observedAt'],
        nextAction='Directly review all revised encoded cue/cut pixels; preserve original failed pair and exact audio/timing; collect/private/Git only after QA.')
    alive = 'endedAt' not in state
    item['execution'].update(status=state['status'], phase=item['stage'], observedAt=state['observedAt'],
        pid=os.getpid(), sessionId=state['sessionId'], commandLine='repair-final-framing-v2.py CPU2/GPU0',
        state=rel(STATE), activeTasks=state['activeTasks'], alive=alive, cpuProductionJobs=int(alive),
        primaryCpuProductionJobs=int(alive), gpuSynthesisJobs=0, renderJobs=int(alive), uploads=0)
    item.update(rendered=state['rendered'], qaApproved=False, allFinalPixelsApproved=False,
        collected=False, privateUploaded=False, finalMixAsrApproved=True)
    item['encodedPixelReview'] = dict(originalReview=rel(OLD / 'encoded-pixel-direct-review.json'),
        original744DirectlyRead=True, originalPairApproved=False, defectSegments=ids,
        revisionDirectory=rel(W), revisedPixelsApproved=False)
    q['updatedAt'] = item['updatedAt']; write(qp, q)
    for p in [BASE / 'latest-checkpoint.json', ROOT / 'production/batches/sakurai-planning-game-design/proof-making-game-sequels/latest-checkpoint.json']:
        d = read(p)
        for k in ['stage','updatedAt','nextAction','execution','rendered','qaApproved','allFinalPixelsApproved','collected','privateUploaded','finalMixAsrApproved','encodedPixelReview']: d[k] = item[k]
        write(p, d)

def run(exe, args, kind):
    log = W / f'repair-{len(state["commands"])+1:03d}.log'
    cmd = [str(exe), *map(str, args)]
    with log.open('wb') as f:
        child = subprocess.Popen(cmd, cwd=W, stdout=f, stderr=f, creationflags=subprocess.CREATE_NO_WINDOW)
        state.update(status=kind, activeTasks=[dict(pid=child.pid, command=cmd, log=rel(log))]); checkpoint()
        code = child.wait()
    state['activeTasks'] = []
    state['commands'].append(dict(command=cmd, pid=child.pid, exitCode=code, log=rel(log)))
    checkpoint(); assert code == 0, (kind, code, rel(log))
    return log.read_text(encoding='utf-8')

def ff(args, kind): return run(FF, ['-v','error','-nostdin','-threads','2',*args], kind)

def probe(p, frames, audio=False):
    d = json.loads(run(FP, ['-v','error','-threads','2','-count_frames','-show_streams','-show_format','-of','json',p], 'CPU-revision-count'))
    s = next(s for s in d['streams'] if s['codec_type'] == 'video')
    assert len(d['streams']) == (2 if audio else 1)
    assert int(s['nb_read_frames']) == frames and s['width'] == 1920 and s['height'] == 1080
    assert s['avg_frame_rate'] == '60/1' and s['time_base'] == '1/90000'
    assert abs(float(d['format']['duration']) - frames/60) <= .017
    return d

try:
    checkpoint()
    plan = copy.deepcopy(old_plan); segments = copy.deepcopy(old_visual['segments']); revisions = []
    for scene in plan['scenes']:
        for c in scene['segments']:
            if c['id'] not in ids: continue
            raw = ROOT / c['rawCompiledVideo']; assert sha(raw) == c['rawCompiledSha256']
            out = W / 'framed-native' / (c['id'] + '.mp4')
            ff(['-i',raw,'-an','-vf','crop=1472:828:0:100,scale=1920:1080,setsar=1,setpts=N/(60*TB)',
                '-fps_mode','passthrough','-frames:v',c['frames'],'-c:v','libx264','-preset','veryfast','-crf','18',
                '-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',out], 'CPU-two-observed-hotbar-crop')
            pr = probe(out,c['frames']); assert not ff(['-i',out,'-f','null','-'],'CPU-repaired-cut-decode').strip()
            revisions.append(dict(id=c['id'], oldCrop=c['sourceFraming'], newCrop=[0,100,1472,828],
                raw=c['rawCompiledVideo'], rawSha256=c['rawCompiledSha256'], output=rel(out), sha256=sha(out),
                frames=c['frames'], startFrame=c['startFrame'], probe=pr, wholeDecodeExitCode=0,
                reason='Actual encoded hotbar overlapped fixed subtitles; crop excludes central hotbar, retains live resource counter at lower left and trap focus above subtitles.',
                captionPositionUnchanged=True, sourceIntervalUnchanged=True, speed=1, revisedFinalPixelsApproved=False))
            c.update(sourceFraming=[0,100,1472,828],video=rel(out),videoSha256=sha(out),encodedFramingReviewed=False)
            s = next(s for s in segments if s['id'] == c['id'])
            s.update(sourceFraming=[0,100,1472,828],video=rel(out),sha256=sha(out),probe=pr,finalPixelApproved=False)
    assert len(revisions) == 2 and sum(r['frames'] for r in revisions) == 540
    unchanged = [s for s in segments if s['id'] not in ids]
    for s in unchanged: assert sha(ROOT / s['video']) == s['sha256']
    assert len(unchanged) == 92
    assert [(s['id'],s['startFrame'],s['frames']) for s in segments] == [(s['id'],s['startFrame'],s['frames']) for s in old_visual['segments']]
    plan.update(revision=dict(basePlan=rel(OLD/'plan.json'),basePlanSha256=sha(OLD/'plan.json'),changedSegments=revisions,
        unchangedInputCount=92, timingByteEquivalent=True, audioUnchanged=True, captionTracksUnchanged=True),
        allFinalPixelsApproved=False,rendered=False,qaApproved=False,collected=False,privateUploaded=False)
    write(W / 'plan.json',plan)
    for name in ['captions.ko.ass','captions.ko.srt','captions.en.srt','caption-tracks.json']:
        shutil.copyfile(OLD/name,W/name); assert sha(OLD/name) == sha(W/name)
    adopted_mix = dict(mix, planSha256=sha(W/'plan.json'), originalPlanSha256=mix['planSha256'],
        mediaDirectory=rel(OLD), adoptedAt=now(), reason='Only two source crops changed; every sample and timing retained.')
    write(W / 'mix-settings.json',adopted_mix)
    write(W / 'full-mix-asr-review.json',dict(asr, adoptedPlanSha256=sha(W/'plan.json'),
        originalReview=rel(OLD/'full-mix-asr-review.json'), audioNotRegenerated=True))
    listing=W/'visual-concat.txt'; listing.write_text('\n'.join("file '"+(ROOT/s['video']).as_posix()+"'" for s in segments)+'\n',encoding='utf-8')
    visual=W/'visual-silent-review.mp4'
    ff(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-c:v','copy',
        '-video_track_timescale','90000','-movflags','+faststart',visual],'CPU-scoped-repaired-visual-assembly')
    pr=probe(visual,35583); assert not ff(['-i',visual,'-f','null','-'],'CPU-revised-silent-decode').strip()
    write(W/'visual-build.json',dict(createdAt=now(),planSha256=sha(W/'plan.json'),segments=segments,
        frames=35583,seconds=593.05,video=rel(visual),sha256=sha(visual),probe=pr,wholeDecodeExitCode=0,
        sourceAudioStreams=0,cleanWhiteReencoded=False,originalBrandingMembershipByteIdentical=True,
        changedSegments=revisions,unchangedInputCount=92,finalFixedCaptionPixelsApproved=False))
    clean=W/'making-game-sequels.clean.review.mp4'; captioned=W/'making-game-sequels.captioned.review.mp4'
    ff(['-i',visual,'-i',OLD/'final-mix.m4a','-map','0:v:0','-map','1:a:0','-c','copy',
        '-video_track_timescale','90000','-movflags','+faststart',clean],'CPU-repaired-clean-same-AAC')
    ff(['-i',clean,'-map','0:v:0','-map','0:a:0','-filter_threads','1','-vf','ass=captions.ko.ass',
        '-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p',
        '-fps_mode','passthrough','-frames:v','35583','-video_track_timescale','90000',
        '-c:a','copy','-movflags','+faststart',captioned],'CPU-repaired-fixed-caption-encode')
    records=[]
    for p in [clean,captioned]:
        pr=probe(p,35583,True)
        packets=json.loads(run(FP,['-v','error','-select_streams','v:0','-show_packets',
            '-show_entries','packet=pts,duration','-of','json',p],'CPU-revised-presentation-clock'))['packets']
        assert len(packets)==35583
        assert sorted(int(p['pts']) for p in packets)==list(range(0,35583*1500,1500))
        assert all(int(p['duration'])==1500 for p in packets)
        assert not ff(['-i',p,'-f','null','-'],'CPU-revised-whole-pair-decode').strip()
        ah=ff(['-i',p,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],'CPU-revised-AAC-hash').strip()
        assert ah=='SHA256=c6539f67027300678d562e28e5b2bae97e4fe32de3ae0450ce3a85cf400d687b'
        records.append(dict(path=rel(p),sha256=sha(p),probe=pr,wholeDecodeExitCode=0,aacPayloadHash=ah,
            exactPresentationClock=dict(timeBase='1/90000',count=35583,firstPts=0,lastPts=53373000,
                step=1500,allPacketPtsExact=True)))
    write(W/'review-pair-build.json',dict(createdAt=now(),planSha256=sha(W/'plan.json'),
        captionAssSha256=sha(W/'captions.ko.ass'),sourceMixAacSha256=mix['aacSha256'],records=records,
        frames=35583,seconds=593.05,identicalAacPayload=True,inheritedSameAacLufs=-16.04,
        inheritedSameAacTruePeakDbtp=-1.98,allFinalFixedCaptionPixelsReviewed=False,qaApproved=False,
        completedVideo=False,basePairPreserved=rel(OLD/'review-pair-build.json'),changedSegments=revisions))
    state.update(status='closed-two-crop-repair-revised-pixel-review-pending',exitCode=0,
        endedAt=now(),rendered=True,activeTasks=[]); checkpoint()
except BaseException:
    state.update(status='closed-two-crop-repair-failed',exitCode=1,endedAt=now(),error=traceback.format_exc(),activeTasks=[])
    checkpoint(); raise
