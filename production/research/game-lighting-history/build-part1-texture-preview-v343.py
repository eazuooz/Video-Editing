"""Two evidenced source/UI corrections, retaining exact narration and captions."""
from pathlib import Path
import importlib.util, json
spec = importlib.util.spec_from_file_location('common', Path(__file__).with_name('review-media-common-v15.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
R = m.ROOT; P = R/'projects/game-lighting-history-04/production'
proposal_path = P/'part1-texture-source-repair-proposal-v342b.json'
proposal = m.read(proposal_path)
assert proposal['allTwoSourceIntervalsActuallyPlayed'] and proposal['playbackRate'] == 1
plan_path = P/'part1-final-input-plan-v309.json'; plan = m.read(plan_path)
assert proposal['planSha256'] == m.sha(plan_path)
settings = m.read(P/'part1-final-mix-settings-v310.json'); mix = R/settings['wav']
layout = m.read(P/'part1-caption-layout-v309.json'); ass = R/layout['ass']['path']
assert m.sha(mix) == settings['wavSha256'] and m.sha(ass) == layout['ass']['sha256']
out = R/'production/research/game-lighting-history/local/part1-texture-preview-v343'
sp = P/'part1-texture-preview-execution-v343.json'
assert not out.exists() and not sp.exists()
resources = m.resources(); out.mkdir(parents=True)
state = dict(startedAt=m.stamp(), status='running', worker=m.worker(), active=None,
             commands=[], results=[], resources=resources, cpuThreads=2, gpuJobs=0,
             proposalSha256=m.sha(proposal_path), newTts=0, newAudioMix=0, newGitImages=0,
             allPixelsApproved=False, qaApproved=False, collected=False, uploaded=False)
def checkpoint():
    cp = R/'production/research/game-lighting-history/checkpoint.json'; j = m.read(cp)
    j['updatedAt'] = m.stamp()
    j['episode04Part1TexturePreviewV343'] = dict(execution=m.rel(sp), status=state['status'],
        worker=state['worker'], active=state['active'], completedInputs=len(state['results']), approved=False)
    j['ownedActiveWork'] = dict(type='one-sequential-texture-input-preview-job', execution=m.rel(sp),
        worker=state['worker'], active=state['active'], cpuThreads=2, gpuJobs=0,
        next='Direct both complete captioned previews and every changed cue before assembly') if state['status']=='running' else dict(
        status='no-active-owned-media-worker', execution=m.rel(sp),
        next='Direct both corrected captioned previews before current master/pair')
    m.save(cp, j)
def run(args, label):
    checkpoint(); result = m.run(args, label, state, sp, out); checkpoint(); return result
m.save(sp, state); checkpoint()
try:
    for c in proposal['inputs']:
        source = R/c['video']['path']; assert m.sha(source) == c['video']['sha256']
        original = next(x for x in plan['cuts'] if x['id'] == c['id'])
        assert c['frames'] == original['frames'] and c['pcm'] == original['pcm']
        assert c['fromFrame'] == original['fromFrame'] and c['toFrame'] == original['toFrame']
        assert len(c['proposedCuts']) == 1
        piece = c['proposedCuts'][0]; assert piece['outFrame']-piece['inFrame'] == c['frames']
        slug = c['id'].split(':')[0]; native = out/(slug+'.native.mp4')
        text = out/(slug+'.identity.txt'); text.write_text(c['identityLabel'], 'utf8')
        label = f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{m.rel(text)}':expansion=none:x=32:y=22:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.82:boxborderw=8"
        x,y,w,h = c['cropRect']
        scale = 'scale=1566:880:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:0:black' if c['id']=='texture-stack-uv:native' else 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black'
        vf = f'crop={w}:{h}:{x}:{y},'+scale+f',setsar=1,fps=60,setpts=PTS-STARTPTS,trim=end_frame={c["frames"]},settb=1/90000,setpts=N*1500,'+label
        run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-ss',f'{piece["inFrame"]/60:.9f}','-i',source,
             '-filter_threads','2','-vf',vf,'-map','0:v:0','-frames:v',str(c['frames']),'-an','-fps_mode','passthrough',
             '-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20',
             '-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',native],slug+'-native')
        technical = m.verify_video(native,c['frames'],state,sp,out,slug+'-native')
        preview = out/(slug+'.captioned-preview.mp4'); start = c['fromFrame']/60
        vf = f"setpts=PTS+{start:.12f}/TB,ass='{m.rel(ass)}',setpts=PTS-STARTPTS,setsar=1"
        run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-i',native,'-ss',f'{start:.9f}','-i',mix,
             '-filter_threads','2','-vf',vf,'-map','0:v:0','-map','1:a:0','-frames:v',str(c['frames']),
             '-t',f'{c["frames"]/60:.9f}','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18',
             '-pix_fmt','yuv420p','-fps_mode','passthrough','-enc_time_base','1:90000','-video_track_timescale','90000',
             '-c:a','aac','-b:a','192k','-movflags','+faststart',preview],slug+'-captioned-preview')
        run([m.FF,'-v','error','-threads','2','-i',preview,'-f','null','NUL'],slug+'-preview-decode')
        state['results'].append(dict(id=c['id'],frames=c['frames'],fromFrame=c['fromFrame'],toFrame=c['toFrame'],
             native=dict(path=m.rel(native),sha256=m.sha(native)),preview=dict(path=m.rel(preview),sha256=m.sha(preview)),
             sourcePieces=c['proposedCuts'],cropRect=c['cropRect'],reframe=c['reframe'],technical=technical,
             allPixelsApproved=False,normalSpeedInputPixelsApproved=False))
        m.save(sp,state); checkpoint()
    state.update(status='complete-awaiting-direct-review',exitCode=0,active=None,completedAt=m.stamp())
    m.save(sp,state); checkpoint(); print(json.dumps(dict(status=state['status'],inputs=2,approved=False)))
except BaseException as e:
    state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp(),active=None)
    m.save(sp,state); checkpoint(); raise
