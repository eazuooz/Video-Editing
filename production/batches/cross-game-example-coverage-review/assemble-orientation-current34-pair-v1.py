"""Single CPU2 final pair,37 bound pieces and unchanged reviewed AAC."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, traceback
for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
    os.environ[key] = '2'
import psutil
ROOT = Path(__file__).resolve().parents[3]; B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
LOCAL = ROOT / 'shared/output/unpublished-teaching-clarity-revision/orientation/current34-final-pair-v1'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: p.resolve().relative_to(ROOT).as_posix()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def save(p, v):
    t = p.with_name(p.name+'.writing'); t.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', 'utf-8'); os.replace(t, p)
def probe(p):
    return json.loads(subprocess.check_output([FP, '-v', 'error', '-show_streams', '-of', 'json', str(p)]))
def ptscheck(p, n):
    frames = json.loads(subprocess.check_output([FP, '-v', 'error', '-threads', '2', '-select_streams', 'v:0', '-show_frames', '-show_entries', 'frame=pts', '-of', 'json', str(p)]))['frames']
    assert [int(x['pts']) for x in frames] == list(range(0, n*1500, 1500)), str(p)
    v = next(x for x in probe(p)['streams'] if x['codec_type'] == 'video')
    assert (v['width'], v['height'], v['r_frame_rate'], v['time_base']) == (1920,1080,'60/1','1/90000')
    return v
def audiohash(p):
    rows = json.loads(subprocess.check_output([FP, '-v', 'error', '-select_streams', 'a:0', '-show_packets', '-show_data_hash', 'sha256', '-show_entries', 'packet=data_hash', '-of', 'json', str(p)]))['packets']
    hashes = [x['data_hash'] for x in rows]; assert hashes
    return dict(packets=len(hashes), orderedPacketHashesSha256=hashlib.sha256('\n'.join(hashes).encode()).hexdigest())
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--resource', required=True); a = ap.parse_args()
    resource = read(ROOT / a.resource)
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds() < 240
    assert resource['ownHeavyJobs'] == 0 and resource['cpuLoadPercent'] < 85 and resource['freePhysicalMemoryKiB'] > 8_000_000
    me = psutil.Process(); own = []
    for p in psutil.process_iter(['pid','name','cmdline']):
        try:
            c = p.info['cmdline'] or []; cmd = ' '.join(c)
            if p.pid == me.pid or (me.parent() and p.pid == me.parent().pid and c[1:] == me.cmdline()[1:]): continue
            if (p.info['name'] or '').lower() in ['python.exe','ffmpeg.exe','node.exe'] and 'cross-game-example-coverage-review' in cmd and any(x in cmd for x in ['review-orientation','render-orientation','extract-orientation','build-orientation','assemble-orientation','review-motion','render-motion','extract-motion']): own.append(p.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied): pass
    assert not own
    subprocess.run([NODE, 'scripts/review-video-duplicates.cjs', 'game-math-orientation-matrices', '--candidate-file', str(O/'duplicate-candidate-v1.json'), '--check'], cwd=ROOT, check=True)
    review = read(O/'current34-mixed-complete-direct-review-v1.json'); mix = read(O/'current34-mix-execution-v2.json')
    assert review['all180ContextsDirectlyCompared'] and review['all34WholeTextsDirectlyCompared'] and review['currentMixedPlacementAndContentReviewPassed']
    assert review['mixAacSha256'] == mix['mixAacSha256'] == sha(ROOT/mix['mixAac'])
    plan = read(O/'current34-measured-timing-plan-v1.json'); inputs = read(O/'current34-assembly-inputs-v1.json')
    assert inputs['planSha256'] == sha(O/'current34-measured-timing-plan-v1.json') and abs(inputs['ratioErrorFrames']) <= 1
    layout = read(O/'current34-caption-layout-v1.json'); alignment = read(O/'current34-caption-alignment-v1.json')
    assert layout['allCuesMeasured'] and not layout['unresolvedLayoutErrors'] and alignment['allNewCueTimingDirectlyReviewed']
    assert layout['cueCount'] == 244 and alignment['mixAacSha256'] == mix['mixAacSha256']
    ass = O/'current34.captions.ko.ass'; assert sha(ass) == layout['assSha256']
    proof = read(O/'narration-07b-guide-repair-execution-v1.json'); protected = proof['protectedInputs']+proof['results']
    for x in protected: assert sha(ROOT/x['path']) == x['sha256']
    sp = O/'current34-final-pair-execution-v1.json'; assert not sp.exists() and not LOCAL.exists()
    assert read(O/'latest-checkpoint.json')['activeOwnedWorkers'] == 0
    LOCAL.mkdir(parents=True); me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    state = dict(startedAt=now(), pid=me.pid, createTime=me.create_time(), commandLine=me.cmdline(), cwd=me.cwd(), sessionId=None,
        resource=a.resource, resourceSha256=sha(ROOT/a.resource), status='preparing-current34-final-pair', exitCode=None,
        cpuThreads=2, gpuJobs=0, pieces=[], jobs=[], finalPixelApproval=False, humanListeningApproved=False,
        humanPronunciationApproved=False, publicRightsApproved=False, newGitMedia=0, researchChanges=0)
    def checkpoint():
        ss = sp.with_name(sp.stem+'.session.json')
        if ss.exists():
            x = read(ss); assert x['pid'] == me.pid and abs(x['createTime']-me.create_time()) < .01; state['sessionId'] = x['sessionId']
        state['updatedAt'] = now(); save(sp, state)
        cp = read(O/'latest-checkpoint.json'); cp.update(recordedAt=now(), stage=state['status'], activeOwnedWorkers=int(state['exitCode'] is None),
            ownedJob=dict(active=state['exitCode'] is None, pid=me.pid, createTime=me.create_time(), commandLine=me.cmdline(), cwd=me.cwd(), sessionId=state['sessionId'], state=rel(sp), cpuThreads=2, gpuJobs=0),
            next='Observe actual pair exit and all244 final cue/cut/annotation/UI pixels; then explicit main promotion/4outputs/private settings/Git/current Studio schedule replacement. No baseline deletion before verified replacement.')
        save(O/'latest-checkpoint.json', cp)
        qp = B/'queue.json'; raw = qp.read_bytes(); q = read(qp)
        q['currentOrientationReview'].update(stage=cp['stage'], activeOwnedWorkers=cp['activeOwnedWorkers'], ownedJob=cp['ownedJob'], next=cp['next']); q['updatedAt'] = now()
        assert qp.read_bytes() == raw; save(qp, q)
    def run(args, name):
        cmd = [FF, '-hide_banner', '-nostdin', '-v', 'error', '-threads', '2', '-filter_threads', '1', '-filter_complex_threads', '1', *args]
        state.update(status=name, currentCommand=cmd); checkpoint(); log = LOCAL/(name+'.log')
        with log.open('wb') as f: code = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=f).returncode
        state['jobs'].append(dict(stage=name, exitCode=code, log=rel(log))); checkpoint(); assert code == 0, name
        print(json.dumps(dict(stage=name, exitCode=code)), flush=True)
    checkpoint()
    try:
        for row in inputs['pieces']:
            p = ROOT/row['path']; assert sha(p) == row['sha256']
            if row['reencodeRequired']:
                assert row['actualFrames'] == 0 and row['explanationTailPadFrames'] <= 1
                target = LOCAL/(row['id']+'.normalized.mp4')
                vf = 'setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0.05,setsar=1'
                run(['-i',str(p),'-vf',vf,'-an','-frames:v',str(row['frames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000',str(target)], 'normalize-EX-'+row['id'])
                ptscheck(target, row['frames']); piece = {**row, 'preparedFromPath':row['path'], 'preparedFromSha256':row['sha256'], 'path':rel(target), 'sha256':sha(target), 'reencoded':True}
            else: piece = {**row, 'reencoded':False}
            state['pieces'].append(piece); checkpoint()
        assert len(state['pieces']) == 37 and sum(x['frames'] for x in state['pieces']) == plan['totalFrames']
        concat = LOCAL/'current37.ffconcat'
        concat.write_text('ffconcat version 1.0\n'+''.join(f"file '{(ROOT/x['path']).as_posix()}'\nduration {x['frames']/60:.12f}\n" for x in state['pieces']), 'utf-8')
        joined = LOCAL/'joined.unsnapped.mp4'; aac = ROOT/mix['mixAac']
        run(['-f','concat','-safe','0','-i',str(concat),'-i',str(aac),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(plan['totalFrames']/60),'-video_track_timescale','90000','-movflags','+faststart',str(joined)], 'concat37-current34-AAC')
        packets = json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','json',str(joined)]))['packets']
        ordered = sorted(int(x['pts']) for x in packets)
        assert len(ordered) == plan['totalFrames'] and all(abs(t-i*1500) <= 2 for i,t in enumerate(ordered))
        clean = LOCAL/'game-math-orientation-matrices.clean.mp4'; captioned = LOCAL/'game-math-orientation-matrices.captioned.mp4'
        run(['-i',str(joined),'-map','0:v:0','-map','0:a:0','-c','copy','-bsf:v','setts=pts=round(PTS/1500)*1500:dts=round(DTS/1500)*1500:duration=1500','-video_track_timescale','90000','-movflags','+faststart',str(clean)], 'snap37-PTS')
        ptscheck(clean, plan['totalFrames'])
        run(['-i',str(clean),'-map','0:v:0','-map','0:a:0','-vf',f'ass={rel(ass)},setsar=1','-frames:v',str(plan['totalFrames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',str(captioned)], 'fixed244-KO-captions')
        ah = audiohash(aac); pair = []
        for p in [clean, captioned]:
            video = ptscheck(p, plan['totalFrames']); run(['-i',str(p),'-f','null','-'], p.stem+'-whole-decode')
            audio = audiohash(p); assert audio == ah
            pair.append(dict(path=rel(p), sha256=sha(p), size=p.stat().st_size, video=video, audioPacketProof=audio,
                wholeDecodeExitCode=0, allPts1500Verified=True, identicalReviewedWholeAacPackets=True))
        for x in protected: assert sha(ROOT/x['path']) == x['sha256']
        for x in inputs['pieces']: assert sha(ROOT/x['path']) == x['sha256']
        state.update(status='current34-pair-encoded-awaiting-all-final-pixels', exitCode=0, finishedAt=now(), frames=plan['totalFrames'], seconds=plan['totalFrames']/60,
            pair=pair, all79ProtectedInputsUnchanged=True, repairCandidateUnchanged=True, retainedByteIdenticalPieceCount=14,
            originalIntroFrames=120, originalMemberFrames=600, currentAudioPacketProof=ah,
            bodyMeasured={k:inputs[k] for k in ['bodyFrames','actualFrames','explanationFrames','ratioErrorFrames']})
        checkpoint(); print(json.dumps(dict(exitCode=0, frames=plan['totalFrames'], aacPacketsIdentical=True, finalPixels=False)))
    except BaseException:
        state.update(status='failed-current34-pair-preserve-local-history', exitCode=1, error=traceback.format_exc(), finishedAt=now()); checkpoint(); raise
if __name__ == '__main__': main()
