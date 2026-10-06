"""One current review pair; mixed-ASR approval is checked before state creation."""
from final_cpu_common import *
import argparse, traceback
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);a=parser.parse_args()
plan=read(FINAL/'plan.json');mix=read(FINAL/'mix-settings.json');visual=read(FINAL/'visual-build.json')
review=read(FINAL/'full-mix-asr-review.json');n=plan['finalFrames']
assert n==23570 and plan['finalTimingApproved'] and plan['bodyRatioApproved']
assert review['technicallyApproved'] and review['all38WindowsDirectlyCompared']
assert review['currentMixedAudioSha256']==mix['wavSha256']==sha(FINAL/'final-mix.wav')
assert review['planSha256']==mix['planSha256']==visual['planSha256']==sha(FINAL/'plan.json')
assert sha(ROOT/visual['video'])==visual['sha256'] and sha(FINAL/'final-mix.m4a')==mix['aacSha256']
assert read(ROOT/read(FINAL/'mixed-asr-current.json')['execution'])['exitCode']==0
clean=FINAL/'familiar-game-rules.clean.review.mp4';captioned=FINAL/'familiar-game-rules.captioned.review.mp4'
assert not clean.exists() and not captioned.exists()
w=Worker('review-pair',a.resource,'Inspect all actual final cue/cut/UI pixels, exact PTS, two decodes and identical AAC, then collect/private/settings/Git. Pause24 after this delivery; no next queued.');w.state.update(rendered=False,finalMixAsrApproved=True,planSha256=sha(FINAL/'plan.json'),mixSha256=mix['wavSha256'])
try:
    w.checkpoint()
    w.ff(['-v','error','-i',ROOT/visual['video'],'-i',FINAL/'final-mix.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',clean],'CPU-clean-copy-current-visual-and-AAC')
    w.ff(['-v','error','-i',clean,'-map','0:v:0','-map','0:a:0','-vf','ass=captions.ko.ass','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-fps_mode','passthrough','-frames:v',n,'-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',captioned],'CPU-fixed-Korean-caption-review-encode',FINAL)
    records=[]
    for p in [clean,captioned]:
        probe=json.loads(w.run(FP,['-v','error','-threads','2','-count_frames','-show_streams','-show_format','-of','json',p],'CPU-count-current-review-pair'));v=next(s for s in probe['streams'] if s['codec_type']=='video')
        assert len(probe['streams'])==2 and int(v['nb_read_frames'])==n
        assert (v['width'],v['height'],v['avg_frame_rate'],v['time_base'])==(1920,1080,'60/1','1/90000')
        assert abs(float(probe['format']['duration'])-n/60)<=.017
        packets=json.loads(w.run(FP,['-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',p],'CPU-exact-presentation-packet-clock'))['packets']
        assert len(packets)==n and sorted(int(x['pts']) for x in packets)==list(range(0,n*1500,1500)) and all(int(x['duration'])==1500 for x in packets)
        assert not w.ff(['-v','error','-i',p,'-f','null','-'],'CPU-whole-current-review-decode').strip()
        ah=w.ff(['-v','error','-i',p,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],'CPU-current-AAC-payload-hash').strip();assert ah.startswith('SHA256=')
        records.append(dict(path=rel(p),sha256=sha(p),probe=probe,wholeDecodeExitCode=0,exactPresentationClock=dict(timeBase='1/90000',count=n,firstPts=0,lastPts=(n-1)*1500,step=1500,allPacketPtsExact=True),aacPayloadHash=ah))
    source=w.ff(['-v','error','-i',FINAL/'final-mix.m4a','-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],'CPU-source-AAC-payload-hash').strip()
    assert records[0]['aacPayloadHash']==records[1]['aacPayloadHash']==source
    write(FINAL/'review-pair-build.json',dict(createdAt=now(),planSha256=sha(FINAL/'plan.json'),captionAssSha256=sha(FINAL/'captions.ko.ass'),sourceMixAacSha256=mix['aacSha256'],mixedAsrReviewSha256=sha(FINAL/'full-mix-asr-review.json'),records=records,frames=n,seconds=n/60,identicalAacPayload=True,inheritedSameAacLufs=float(mix['finalAacMeasurement']['input_i']),inheritedSameAacTruePeakDbtp=float(mix['finalAacMeasurement']['input_tp']),allFinalFixedCaptionPixelsReviewed=False,qaApproved=False,completedVideo=False))
    w.state['rendered']=True;w.close('closed-review-pair-built-final-caption-and-cut-QA-pending')
except BaseException:w.close('closed-review-pair-failed',1,traceback.format_exc());raise
