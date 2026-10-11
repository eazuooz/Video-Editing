"""Repair only the failed captioned encode; retain clean/AAC and failed evidence."""
from pathlib import Path
import hashlib,json
source=Path(__file__).with_name('build-part3-reviewed-pair-v149.py').read_text('utf-8')
# Reapply every content/hash approval guard, without starting the original build.
exec(source[:source.index('resources=m.resources();')])
old=m.read(P/'part3-reviewed-pair-execution-v149.json')
assert old['status']=='failed' and old['error']=='AssertionError()'
assert len(old['commands'])==3 and all(x['exitCode']==0 for x in old['commands'])
oldout=OUT; clean=oldout/'game-lighting-history-04-3.clean.mp4'
failed=oldout/'game-lighting-history-04-3.captioned.mp4'
resources=m.resources();OUT=ROOT/'production/research/game-lighting-history/local/part3-captioned-pts-v156'
SP=P/'part3-captioned-pts-execution-v156.json'
assert not SP.exists() and not OUT.exists()
OUT.mkdir(parents=True);captioned=OUT/'game-lighting-history-04-3.captioned.mp4'
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,commands=[],results=[],resourceObservation=resources,
    failurePreserved=dict(execution=m.rel(P/'part3-reviewed-pair-execution-v149.json'),path=m.rel(failed),sha256=m.sha(failed)),
    cleanPreserved=dict(path=m.rel(clean),sha256=m.sha(clean),wholeDecode=old['commands'][1]),
    sourceVisualSha256=m.sha(visual),sourceAacSha256=m.sha(audio),allFinalPixelsReviewed=False,qaApproved=False,collected=False,uploaded=False)
m.save(SP,state)
def checkpoint():
    cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
    j['episode04Part3CaptionedPtsV156']=dict(execution=m.rel(SP),status=state['status'],worker=state['worker'],active=state['active'],completedCommands=len(state['commands']),finalApproved=False)
    j['ownedActiveWork']=dict(type='part3-captioned-pts-repair',execution=m.rel(SP),worker=state['worker'],cpuThreads=2,gpuJobs=0,next='2169 final pixels and normal-speed moving review') if state['status']=='running' else dict(status='no-active-owned-media-worker',execution=m.rel(SP),next='2169 final pixels and normal-speed moving review')
    m.save(cp,j)
def run(args,label):
    checkpoint();r=m.run(args,label,state,SP,OUT);checkpoint();return r
def probe(file,label,reuse_decode=None):
    cmd=[m.FP,'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,sample_rate,channels,duration:format=duration','-of','json',file]
    j=json.loads(m.subprocess.run(list(map(str,cmd)),capture_output=True,text=True,check=True).stdout)
    v=next(s for s in j['streams'] if s['codec_type']=='video');a=next(s for s in j['streams'] if s['codec_type']=='audio')
    assert len(j['streams'])==2 and (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',plan['finalFrames'])
    assert abs(float(v['duration'])-plan['finalFrames']/60)<.000002
    assert (a['codec_name'],a['sample_rate'],a['channels'])==('aac','48000',2)
    pc=[m.FP,'-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','json',file]
    pts=sorted(q['pts'] for q in json.loads(m.subprocess.run(list(map(str,pc)),capture_output=True,text=True,check=True).stdout)['packets'])
    assert pts==list(range(0,plan['finalFrames']*1500,1500)), label
    ac=[m.FP,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,duration,data_hash','-of','json',file]
    packets=json.loads(m.subprocess.run(list(map(str,ac)),capture_output=True,text=True,check=True).stdout)['packets']
    packetsha=hashlib.sha256(json.dumps(packets,sort_keys=True).encode()).hexdigest()
    decode=reuse_decode or run([m.FF,'-v','error','-nostdin','-threads','2','-i',file,'-f','null','NUL'],label+'-whole-decode')
    return dict(path=m.rel(file),sha256=m.sha(file),frames=len(pts),allPresentationPtsContinuous=True,probe=j,
        probeCommand=list(map(str,cmd)),packetCommand=list(map(str,pc)),aacPacketHashCommand=list(map(str,ac)),aacPacketCount=len(packets),aacPayloadPtsDurationHash=packetsha,wholeDecode=decode,
        previousCompleteDecodeReused=bool(reuse_decode),allPixelsReviewed=False)
try:
    cp=probe(clean,'clean',old['commands'][1]);assert cp['sha256']==state['cleanPreserved']['sha256']
    # Mixed source sequence parameter changes caused the filter graph to restart N.
    # Preserve the running filter graph so setpts and ASS retain the global clock.
    args=[m.FF,'-n','-hide_banner','-nostdin','-threads','2','-reinit_filter','0','-i',visual,'-i',audio,
        '-map','0:v:0','-map','1:a:0','-t',f"{plan['finalFrames']/60:.9f}",'-c:a','copy',
        '-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart',
        '-filter_threads','2','-vf',f"settb=1/90000,setpts=N*1500,ass=filename='{m.rel(ass)}'",
        '-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2',
        '-preset','veryfast','-crf','18','-pix_fmt','yuv420p',captioned]
    encode=run(args,'captioned-encode');pp=probe(captioned,'captioned')
    assert cp['aacPayloadPtsDurationHash']==pp['aacPayloadPtsDurationHash'] and cp['aacPacketCount']==pp['aacPacketCount']
    assert state['sourceVisualSha256']==m.sha(visual) and state['sourceAacSha256']==m.sha(audio)
    build=dict(createdAt=m.stamp(),status='encoded-review-pair-awaiting-all-pixels',slug=plan['slug'],
        planSha256=m.sha(PP),mixedAsrDirectApprovalSha256=m.sha(AP),visualSha256=m.sha(visual),mixAacSha256=m.sha(audio),captionAssSha256=m.sha(ass),
        clean=dict(cp,encode=old['commands'][0]),captioned=dict(pp,encode=encode),identicalAacPayloadPtsDuration=True,
        tracks=layout['tracks'],actualFrames=plan['actualFrames'],explanationFrames=plan['explanationFrames'],bodyFrames=plan['bodyFrames'],finalFrames=plan['finalFrames'],ratioErrorFrames=plan['ratioErrorFrames'],
        loudness=settings['finalAacMeasurement']['measurement'],sourceAudioStreams=0,
        allFinalPixelsReviewed=False,allMovingPixelsReviewed=False,captionTimingApproved=False,finalTimingApproved=False,bodyRatioApproved=False,qaApproved=False,collected=False,uploaded=False,
        humanWholeListening='pending',humanPronunciation='pending',rightsApproved=False,originalNimbusFileVerified=False,
        timingRepair=dict(execution=m.rel(SP),failedEncode=state['failurePreserved'],preservedClean=True,reinitFilter=0,reason='Retain global setpts/ASS clock across source parameter changes; exact 92038 packet PTS required.'))
    m.save(P/'part3-reviewed-pair-build-v149.json',build)
    state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None);m.save(SP,state);checkpoint()
    print(json.dumps(dict(frames=92038,exactPts=True,cleanDecodeReused=True,captionedDecode=0,identicalAac=True,pixelsApproved=False)))
except BaseException as e:
    state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
