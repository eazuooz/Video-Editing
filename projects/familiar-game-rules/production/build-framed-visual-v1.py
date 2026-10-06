"""One CPU worker, exact native intervals and slices of the existing white reel."""
from final_cpu_common import *
import argparse, traceback
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);a=parser.parse_args()
plan=read(FINAL/'plan.json');assert plan['finalTimingApproved'] and plan['allInputSegmentCaptionPixelsReviewed']
assert read(FINAL/'mix-execution.json')['exitCode']==0
w=Worker('framed-visual',a.resource,'Complete85 unique native inputs/8slices of existing white reel; next current final-mix19whole+19complete-context CPU ASR, final pair/allpixels/QA/collect/private/Git then pause24. No new GPU/queued.')
w.state.update(totalNativeCuts=85,completedNativeCuts=0,cuts=[],white=[])
def probe(path,frames):
    pr=json.loads(w.run(FP,['-v','error','-threads','2','-count_frames','-show_streams','-show_format','-of','json',path],'CPU-probe-current-segment'));ss=pr['streams']
    assert len(ss)==1 and ss[0]['codec_type']=='video'
    v=ss[0];assert v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='60/1' and int(v['nb_read_frames'])==frames and v['time_base']=='1/90000',v
    assert abs(float(pr['format']['duration'])-frames/60)<.017
    w.ff(['-v','error','-i',path,'-f','null','-'],'CPU-whole-segment-decode')
    return pr
try:
    w.checkpoint();(FINAL/'framed-native').mkdir();(FINAL/'white-segments').mkdir();checked={}
    reuse=read(PROOF/'guide13-encoded-input-v7.json')['nativeCuts'];reuse={c['cutId']:c for c in reuse}
    for c in plan['nativeCuts']:
        raw=ROOT/c['sourcePath']
        if c['sourcePath'] not in checked:assert sha(raw)==c['sourceSha256'];checked[c['sourcePath']]=c['sourceSha256']
        if c['id'] in reuse:
            old=reuse[c['id']];video=ROOT/old['path'];assert old['frames']==c['durationFrames'] and sha(video)==old['sha256'];reused=True
        else:
            video=FINAL/'framed-native'/f'{c["id"]}.mp4';reused=False;x,y,cw,ch=c['sourceCrop']
            filt=f'trim=start_frame={c["inFrameInclusive"]}:end_frame={c["outFrameExclusive"]},setpts=PTS-STARTPTS,fps=60,crop={cw}:{ch}:{x}:{y},scale=1920:1080,setsar=1'
            w.ff(['-v','error','-i',raw,'-an','-vf',filt,'-frames:v',c['durationFrames'],'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',video],'CPU-native-normal-speed-framing')
        pr=probe(video,c['durationFrames'])
        w.state['cuts'].append(dict(id=c['id'],pieceId=c['pieceId'],sceneId=c['logicalScene'],startFrame=c['startFrame'],frames=c['durationFrames'],video=rel(video),sha256=sha(video),sourcePath=c['sourcePath'],sourceSha256=c['sourceSha256'],sourceFrameRate=c['sourceFrameRate'],inFrameInclusive=c['inFrameInclusive'],outFrameExclusive=c['outFrameExclusive'],sourceCrop=c['sourceCrop'],classification='actual-existing-game',probe=pr,wholeDecodeExitCode=0,reusedGuide13EncodedInput=reused,sourceAudioStreams=0,finalPixelsApproved=False))
        w.state['completedNativeCuts']+=1;w.checkpoint();print('Framed',w.state['completedNativeCuts'],'/85',flush=True)
    raw=ROOT/plan['whiteInput'];assert sha(raw)==plan['whiteInputSha256']
    for c in plan['whiteSegments']:
        video=FINAL/'white-segments'/f'{c["id"]}.mp4'
        filt=f'trim=start_frame={c["reelStartFrame"]}:end_frame={c["reelStartFrame"]+c["frames"]},setpts=N/(60*TB),setsar=1'
        w.ff(['-v','error','-i',raw,'-an','-vf',filt,'-frames:v',c['frames'],'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000',video],'CPU-exact-white-input-slice-no-MC-render')
        pr=probe(video,c['frames']);w.state['white'].append(dict(id='white-'+c['id'],pieceId=c['pieceId'],sceneId=c['id'],startFrame=c['finalStartFrame'],frames=c['frames'],video=rel(video),sha256=sha(video),classification='explanation',whiteReelSha256=plan['whiteInputSha256'],reelStartFrame=c['reelStartFrame'],newMotionCanvasRender=False,frameExactSliceEncoded=True,probe=pr,wholeDecodeExitCode=0,finalPixelsApproved=False));w.checkpoint()
    segments=[]
    for name in ['branding','membership']:
        c=plan[name];assert sha(ROOT/c['path'])==c['sha256'];segments.append(dict(id=name,startFrame=c['startFrame'],frames=c['frames'],video=c['path'],sha256=c['sha256'],classification=name))
    segments=sorted(segments+w.state['cuts']+w.state['white'],key=lambda c:c['startFrame']);pos=0
    for c in segments:assert c['startFrame']==pos;pos+=c['frames']
    assert pos==23570
    listing=FINAL/'visual-concat.txt';listing.write_text('\n'.join("file '"+(ROOT/c['video']).as_posix()+"'" for c in segments)+'\n','utf-8')
    visual=FINAL/'visual-silent-review.mp4'
    w.ff(['-v','error','-f','concat','-safe','0','-i',listing,'-an','-c:v','copy','-video_track_timescale','90000','-movflags','+faststart',visual],'CPU-silent-exact-assembly');pr=probe(visual,23570)
    write(FINAL/'visual-build.json',dict(createdAt=now(),planSha256=sha(FINAL/'plan.json'),segments=segments,frames=23570,seconds=23570/60,video=rel(visual),sha256=sha(visual),probe=pr,sourceAudioStreams=0,originalBrandingMembershipByteIdentical=True,wholeDecodeExitCode=0,newMotionCanvasRender=False,finalFixedCaptionPixelsApproved=False,finalMixAsrApproved=False,silentVisualIsCompletedVideo=False))
    w.close('closed-framed-visual-awaiting-current-mixed-ASR');print(json.dumps(dict(frames=23570,nativeCuts=85,whiteSegments=8,decodeExitCode=0,finalApproved=False)),flush=True)
except BaseException:
    w.close('closed-framed-visual-failed',1,traceback.format_exc());raise
