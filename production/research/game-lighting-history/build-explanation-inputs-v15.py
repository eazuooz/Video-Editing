"""Extract every retained explanation once; assemble a silent review candidate."""
import importlib.util, shutil, os
from pathlib import Path
_p = Path(__file__).with_name('review-media-common-v15.py')
_s = importlib.util.spec_from_file_location('review_media', _p)
m = importlib.util.module_from_spec(_s); _s.loader.exec_module(m)
ROOT, PROD, FF = m.ROOT, m.PROD, m.FF
plan_path = PROD / 'review-input-plan-v15.json'
plan = m.read(plan_path)
for x in plan['inputHashes']: assert m.sha(ROOT / x['path']) == x['sha256'], 'Plan input changed'
native_state = m.read(PROD / 'native-framing-execution-v16.json')
assert native_state['status'] == 'complete' and native_state['exitCode'] == 0 and len(native_state['results']) == 112
out = ROOT / 'production/research/game-lighting-history/local/explanation-framing-v15'
out.mkdir(parents=True, exist_ok=True)
state_path = PROD / 'explanation-framing-execution-v15.json'
observation = m.resources()
state = m.read(state_path) if state_path.exists() else dict(startedAt=m.stamp(), results=[], commands=[])
state.update(status='running', worker=m.worker(), active=None, resourceObservation=observation,
             cpuThreads=2, gpuJobs=0, allFinalPixelsReviewed=False, finalMixedAsrApproved=False)
m.save(state_path, state)
try:
    inputs = plan['inputs']
    sources = {}
    for c in inputs:
        if c['kind'] != 'explanation-review-input': continue
        source = ROOT / c['sourceChapter']
        proof = m.read(ROOT / c['sourceChapterVerification'])
        if c['sourceChapter'] not in sources:
            # Clean render verifier records the actual normalized path and SHA.
            expected = proof['video']['sha256']
            assert proof['video']['path'] == c['sourceChapter'] and m.sha(source) == expected, 'Retained chapter source changed'
            assert proof['wholeDecode']['exitCode'] == 0
            sources[c['sourceChapter']] = expected
        dest, vp = ROOT / c['output'], ROOT / c['verification']
        if vp.exists():
            v = m.read(vp)
            assert m.sha(dest) == v['outputSha256'] and v['observedFrames'] == c['frames'] and v['wholeDecode']['exitCode'] == 0
            continue
        assert not dest.exists(), 'Unverified output preserved; inspect before retry'
        filters = f"trim=start_frame={c['localFromFrame']}:end_frame={c['localToFrame']},setpts=N/(60*TB),setsar=1"
        command = [FF, '-n', '-v', 'error', '-threads', '2', '-i', source, '-an', '-vf', filters,
                   '-frames:v', str(c['frames']), '-c:v', 'libx264', '-threads', '2', '-preset',
                   'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-video_track_timescale', '90000',
                   '-movflags', '+faststart', dest]
        encode = m.run(command, c['id'] + '-encode', state, state_path, out)
        v = m.verify_video(dest, c['frames'], state, state_path, out, c['id'])
        v.update(input=c, sourceSha256=sources[c['sourceChapter']], encode=encode)
        m.save(vp, v)
        state['results'].append(dict(id=c['id'], frames=c['frames'], verification=m.rel(vp), sha256=v['outputSha256']))
        m.save(state_path, state)
        print(m.json.dumps(dict(done=len(state['results']), total=47, id=c['id'], frames=c['frames'])), flush=True)
    # Explicit durations use differences of rounded absolute microsecond boundaries,
    # so fractional 60fps durations cannot accumulate at the 161 concat boundaries.
    concat = out / 'review-inputs.ffconcat'
    lines = ['ffconcat version 1.0']
    collected = []
    for c in inputs:
        if c['kind'].startswith('preserved-original'):
            source = ROOT / c['media']; assert m.sha(source) == c['sha256']
            dest = out / (c['id'] + '.mp4')
            if not dest.exists(): shutil.copyfile(source, dest)
            assert m.sha(dest) == c['sha256']
        else:
            dest = ROOT / c['output']; v = m.read(ROOT / c['verification'])
            assert m.sha(dest) == v['outputSha256'] and v['observedFrames'] == c['frames'] and v['wholeDecode']['exitCode'] == 0
        absolute = dest.as_posix(); assert "'" not in absolute
        micros = round(c['toFrame'] * 1_000_000 / 60) - round(c['fromFrame'] * 1_000_000 / 60)
        lines += [f"file '{absolute}'", f'duration {micros / 1_000_000:.6f}']
        collected.append(dict(id=c['id'], media=m.rel(dest), sha256=m.sha(dest), fromFrame=c['fromFrame'], frames=c['frames']))
    concat.write_text('\n'.join(lines) + '\n', 'utf-8')
    visual = out / 'silent-review-visual-v15.mp4'
    visual_proof = out / 'silent-review-visual-v15.verification.json'
    if visual_proof.exists():
        v = m.read(visual_proof); assert v['outputSha256'] == m.sha(visual)
    else:
        assert not visual.exists(), 'Unverified visual preserved'
        encode = m.run([FF, '-n', '-v', 'error', '-threads', '2', '-f', 'concat', '-safe', '0',
                        '-i', concat, '-map', '0:v:0', '-an', '-c:v', 'copy', '-video_track_timescale',
                        '90000', '-movflags', '+faststart', visual], 'silent-review-visual', state, state_path, out)
        v = m.verify_video(visual, plan['totals']['finalFrames'], state, state_path, out, 'silent-review-visual')
        v.update(assembly=encode, reviewInputPlanSha256=m.sha(plan_path), inputs=collected,
                 allOriginalAssetsByteIdentical=True, looped=False, sourceAudioStreams=0,
                 finalTimingApproved=False, bodyRatioApproved=False, allFinalPixelsReviewed=False,
                 finalMixedAsrApproved=False, collected=False, uploaded=False)
        m.save(visual_proof, v)
    state.update(status='complete', exitCode=0, completedAt=m.stamp(), silentVisual=m.rel(visual),
                 silentVisualSha256=m.sha(visual), active=None, allFinalPixelsReviewed=False)
    m.save(state_path, state)
    print(m.json.dumps(dict(explanations=47, inputs=161, frames=plan['totals']['finalFrames'], wholeDecode=0, finalApproved=False)), flush=True)
except BaseException as e:
    state.update(status='failed', exitCode=1, failedAt=m.stamp(), error=str(e))
    m.save(state_path, state)
    raise
