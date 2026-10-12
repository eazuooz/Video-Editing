"""Normal-speed labelled before/changed comparison; preserve all original frames once."""
from pathlib import Path
import importlib.util,json
spec=importlib.util.spec_from_file_location('m',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
pp=P/'part1-texture-source-order-proposal-v343c.json';proposal=m.read(pp)
c=proposal['inputs'][0]
assert c['id']=='texture-stack-uv:native'
# Actual full source playback has just reached116.266s at1x through all4 ranges.
c['sourceReview'].update(fullCandidateActuallyPlayed=True,endObserved=116.266,observedAdditionalTime=112.2,
    observation='Source graph stays recognizable through all four comparisons; first shared coordinate, changed connections/count, returned shared-coordinate comparison, and changed result. Continuous105–131.1167 candidate rejected for city transition. Labels distinguish the return to the before state.')
proposal.update(allTwoSourceIntervalsActuallyPlayed=True,reviewedAt=m.stamp())
m.save(pp,proposal)
planp=P/'part1-final-input-plan-v309.json';plan=m.read(planp)
assert proposal['planSha256']==m.sha(planp)
original=next(x for x in plan['cuts'] if x['id']==c['id'])
assert c['frames']==original['frames'] and c['pcm']==original['pcm']
source=R/c['video']['path'];assert m.sha(source)==c['video']['sha256']
pieces=c['proposedCuts'];assert sum(x['outFrame']-x['inFrame'] for x in pieces)==1567
assert sorted((x['inFrame'],x['outFrame']) for x in pieces)==[(5400,5599),(5599,6534),(6534,6865),(6865,6967)]
settings=m.read(P/'part1-final-mix-settings-v310.json');mix=R/settings['wav']
layout=m.read(P/'part1-caption-layout-v309.json');ass=R/layout['ass']['path']
assert m.sha(mix)==settings['wavSha256'] and m.sha(ass)==layout['ass']['sha256']
out=R/'production/research/game-lighting-history/local/part1-texture-stack-preview-v343d'
sp=P/'part1-texture-stack-preview-execution-v343d.json'
assert not out.exists() and not sp.exists();resources=m.resources();out.mkdir(parents=True)
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,commands=[],results=[],resources=resources,cpuThreads=2,gpuJobs=0,
    proposalSha256=m.sha(pp),allOriginal1567SourceFramesUsedOnce=True,sourceRate=1,newTts=0,newAudioMix=0,newGitImages=0,allPixelsApproved=False,qaApproved=False,collected=False,uploaded=False)
def checkpoint():
    cp=R/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
    j['episode04Part1TextureStackPreviewV343d']=dict(execution=m.rel(sp),status=state['status'],worker=state['worker'],active=state['active'],approved=False)
    j['ownedActiveWork']=dict(type='one-stack-input-preview-job',execution=m.rel(sp),worker=state['worker'],active=state['active'],cpuThreads=2,gpuJobs=0,next='Direct corrected stack plus all5 cue pixels; reuse reviewed tile343') if state['status']=='running' else dict(status='no-active-owned-media-worker',execution=m.rel(sp),next='Direct corrected stack before final assembly')
    m.save(cp,j)
def run(args,label):
    checkpoint();q=m.run(args,label,state,sp,out);checkpoint();return q
m.save(sp,state);checkpoint()
try:
    identity=out/'identity.txt';identity.write_text(c['identityLabel'],'utf8')
    x,y,w,h=c['cropRect']
    base=f'crop={w}:{h}:{x}:{y},scale=1566:880:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:0:black,setsar=1,fps=60,trim=end_frame=1567,split=4[s0][s1][s2][s3];'
    for i,p in enumerate(pieces):
        text=out/f'condition-{i}.txt';text.write_text(p['condition'],'utf8')
        base+=f"[s{i}]trim=start_frame={p['inFrame']-5400}:end_frame={p['outFrame']-5400},setpts=PTS-STARTPTS,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{m.rel(text)}':expansion=none:x=1150:y=22:fontsize=28:fontcolor=0xffdf8a:box=1:boxcolor=black@0.9:boxborderw=8[p{i}];"
    base+="[p0][p1][p2][p3]concat=n=4:v=1:a=0,settb=1/90000,setpts=N*1500,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='"+m.rel(identity)+"':expansion=none:x=32:y=22:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.82:boxborderw=8[v]"
    native=out/'texture-stack-uv.native.mp4'
    run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-ss','90','-i',source,'-filter_complex_threads','2','-filter_complex',base,'-map','[v]','-frames:v','1567','-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',native],'stack-native')
    technical=m.verify_video(native,1567,state,sp,out,'stack-native')
    preview=out/'texture-stack-uv.captioned-preview.mp4';start=c['fromFrame']/60
    vf=f"setpts=PTS+{start:.12f}/TB,ass='{m.rel(ass)}',setpts=PTS-STARTPTS,setsar=1"
    run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-i',native,'-ss',f'{start:.9f}','-i',mix,'-filter_threads','2','-vf',vf,'-map','0:v:0','-map','1:a:0','-frames:v','1567','-t',f'{1567/60:.9f}','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-enc_time_base','1:90000','-video_track_timescale','90000','-c:a','aac','-b:a','192k','-movflags','+faststart',preview],'stack-captioned-preview')
    run([m.FF,'-v','error','-threads','2','-i',preview,'-f','null','NUL'],'stack-preview-decode')
    result=dict(id=c['id'],frames=1567,fromFrame=c['fromFrame'],toFrame=c['toFrame'],native=dict(path=m.rel(native),sha256=m.sha(native)),preview=dict(path=m.rel(preview),sha256=m.sha(preview)),sourcePieces=pieces,cropRect=c['cropRect'],reframe=c['reframe'],technical=technical,allPixelsApproved=False,normalSpeedInputPixelsApproved=False)
    state['results']=[result];state.update(status='complete-awaiting-direct-review',exitCode=0,active=None,completedAt=m.stamp());m.save(sp,state);checkpoint()
    template=(R/'production/research/game-lighting-history/local/part1-texture-reordered-source-v343c.html').read_text('utf8');a=template.index('const rows=');b=template.index(';const pick=',a)
    paragraph=next(x for x in plan['paragraphs'] if x['id']=='texture-stack-uv')
    rows=[dict(id=c['id'],path=m.rel(preview),ranges=[[0,1567/60]],ko=paragraph['ko'])]
    (out/'review.html').write_text(template[:a]+'const rows='+json.dumps(rows,ensure_ascii=False)+template[b:],'utf8')
    print(json.dumps(dict(status=state['status'],frames=1567,approved=False)))
except BaseException as e:
    state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp(),active=None);m.save(sp,state);checkpoint();raise
