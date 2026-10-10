"""Guarded final pair: seven reviewed action slots and eight retained ranges.

Preserve original54115 frames, whole AAC, narration/cues and white Manim.
This worker produces unapproved review media, never publishes or collects it.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, os, hashlib, subprocess, argparse, traceback
os.environ['OMP_NUM_THREADS']='2'
import psutil
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/final-pair-v2'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def probe(p):return json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-show_format','-of','json',str(p)]))
def ptscheck(p,count):
    r=json.loads(subprocess.check_output([FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=pts','-of','json',str(p)]))
    assert [int(x['pts']) for x in r['frames']]==list(range(0,count*1500,1500)),p
    s=next(s for s in probe(p)['streams'] if s['codec_type']=='video')
    assert s['time_base']=='1/90000' and s['r_frame_rate']=='60/1' and (s['width'],s['height'])==(1920,1080)
    return s
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--glyph-outer-exit-code',type=int,required=True);args=ap.parse_args()
    assert args.glyph_outer_exit_code==0
    failure=read(OUT/'final-pair-pts-failure-direct-review-v1.json')
    assert failure['failedWorkerExitCode']==1 and failure['failedPidAbsent']
    failed=read(OUT/'final-pair-execution-v1.json')
    assert failed['exitCode']==1 and (not psutil.pid_exists(failed['pid']) or psutil.Process(failed['pid']).create_time()!=failed['createTime'])
    repair=read(OUT/'minus-glyph-moving-pilots-execution-v5.json')
    assert repair['exitCode']==0 and repair['status']=='completed'
    assert not psutil.pid_exists(repair['pid']) or psutil.Process(repair['pid']).create_time()!=repair['createTime']
    proof=read(OUT/'minus-glyph-moving-direct-review-v5.json');assert proof['bothMovingPilotsAllListedPixelsDirectlyRead'] and proof['bothMovingGlyphRepairsApproved']
    audio=read(OUT/'current-aac-complete-comparison-v2.json');assert audio['all44CompleteContextsDirectlyCompared']
    resource=read(ROOT/args.resource)
    assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8000000
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    old=read(OUT/'six-moving-pilots-execution-v4.json');review=read(OUT/'six-moving-pilots-direct-review-v4.json')
    assert review['all956SamplesAnd162BoardsDirectlyRead']
    two=read(OUT/'scene02-moving-pilot-execution-v2.json')
    assert read(OUT/'scene02-pilot-direct-review-v2.json')['pilotBoundedReviewPassed']
    snapshot=read(OUT/'baseline-protected-sha-v1.json')
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
    baseline=ROOT/'shared/output/motion-canvas/game-math-polar-3d.mp4'
    assert sha(baseline)=='b983fb0206b2168f630c16de0c7dd987ab497fdca946f33121e5d5b275a04efd'
    pilots=[two]+[j for j in old['jobs'] if j['scene'] not in ['11','16']]+repair['jobs']
    pilots.sort(key=lambda j:j['globalStartFrame'])
    assert [str(j.get('scene','02')) for j in pilots]==['02','05','08','11','14','16','18']
    assert sum(j['frames'] for j in pilots)==21358
    LOCAL.mkdir(parents=True,exist_ok=False)
    statefile=OUT/'final-pair-execution-v2.json';assert not statefile.exists()
    p=psutil.Process()
    state={'startedAt':now(),'pid':p.pid,'createTime':p.create_time(),'commandLine':p.cmdline(),'cwd':str(ROOT),
      'resourceEvidence':args.resource,'priorGlyphOuterExitCode':args.glyph_outer_exit_code,'preservedFailureEvidence':'final-pair-pts-failure-direct-review-v1.json','retainedPtsMethod':'absolute source PTS minus known start in1/90000 units',
      'cpuThreads':2,'gpuJobs':0,'status':'assemble-reviewed-ranges','pieces':[],
      'narrationChanged':False,'baselineMutations':0,'newMediaApproved':False,
      'allFinalPixelsApproved':False,'humanListeningApproved':False,'publicRightsApproved':False,'researchControlChanges':0}
    def save():state['observedAt']=now();statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def run(cmd,name):
        state['currentCommand']=cmd;state['stage']=name;save()
        with (LOCAL/(name+'.log')).open('wb') as f:r=subprocess.run(cmd,stdout=f,stderr=f,cwd=ROOT,check=True)
        print(json.dumps({'stage':name,'exitCode':r.returncode}),flush=True);return r.returncode
    def retained(a,b):
        if a==b:return
        count=b-a;dest=LOCAL/f'retained-{a:05d}-{b:05d}.mp4'
        seek=max(0,a-120)/60
        cmd=[FF,'-hide_banner','-nostdin','-v','error','-threads','2','-filter_threads','1','-ss',f'{seek:.12f}','-copyts','-i',str(baseline),'-vf',f'trim=start_pts={a*1500}:end_pts={b*1500},setpts=PTS-{a*1500},setsar=1','-frames:v',str(count),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart',str(dest)]
        code=run(cmd,f'retained-{a:05d}-{b:05d}');s=ptscheck(dest,count)
        state['pieces'].append({'kind':'retained-original','globalStartFrame':a,'frames':count,'path':rel(dest),'sha256':sha(dest),'encodeExitCode':code,'allPts1500Verified':True,'sourceStartPts':a*1500,'sourceEndPts':b*1500,'video':s});save()
    save();print(json.dumps({'pid':p.pid,'createTime':p.create_time(),'frames':54115}),flush=True)
    try:
        cursor=0
        for j in pilots:
            sid=str(j.get('scene','02'));a=j['globalStartFrame'];count=j['frames'];retained(cursor,a)
            record=j[f'scene{sid}.annotated.clean'];source=ROOT/record['path']
            assert sha(source)==record['sha256'] and record['frames']==count and record['allPts1500Verified']
            state['pieces'].append({'kind':'reviewed-annotated-action','scene':sid,'globalStartFrame':a,'frames':count,'path':rel(source),'sha256':record['sha256'],'allPts1500Verified':True});save();cursor=a+count
        retained(cursor,54115)
        assert len(state['pieces'])==15 and sum(p['frames'] for p in state['pieces'])==54115
        for i,p in enumerate(state['pieces']):assert p['globalStartFrame']==sum(v['frames'] for v in state['pieces'][:i])
        listing=LOCAL/'selected-concat.ffconcat'
        listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{(ROOT/p['path']).as_posix()}'\nduration {p['frames']/60:.12f}\n" for p in state['pieces']),encoding='utf-8')
        clean=LOCAL/'game-math-polar-3d.clean.mp4';captioned=LOCAL/'game-math-polar-3d.captioned.mp4'
        state['cleanEncodeExitCode']=run([FF,'-hide_banner','-nostdin','-v','error','-f','concat','-safe','0','-i',str(listing),'-i',str(baseline),'-map','0:v:0','-map','1:a:0','-c','copy','-bsf:v','h264_metadata=sample_aspect_ratio=1/1','-video_track_timescale','90000','-movflags','+faststart',str(clean)],'concat-original-aac')
        ptscheck(clean,54115)
        state['captionEncodeExitCode']=run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-filter_threads','1','-i',str(clean),'-map','0:v:0','-map','0:a:0','-vf','ass=projects/game-math-polar-3d/script/final.ko.ass,setsar=1','-frames:v','54115','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',str(captioned)],'fixed-ko-captions')
        state['pair']=[]
        for video in [clean,captioned]:
            s=ptscheck(video,54115)
            code=run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(video),'-f','null','-'],video.stem+'-whole-decode')
            aac=LOCAL/(video.stem+'.aac.m4a');wav=LOCAL/(video.stem+'.aac-decoded.wav')
            run([FF,'-hide_banner','-nostdin','-v','error','-i',str(video),'-map','0:a:0','-c:a','copy','-vn',str(aac)],video.stem+'-aac-copy')
            run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(aac),'-c:a','pcm_s16le','-ar','48000','-ac','2',str(wav)],video.stem+'-aac-decode')
            assert sha(aac)==audio['aacSha256'] and sha(wav)==audio['wavSha256'],('AAC/PCM changed',video)
            a=next(a for a in probe(video)['streams'] if a['codec_type']=='audio')
            state['pair'].append({'path':rel(video),'sha256':sha(video),'bytes':video.stat().st_size,'video':s,'audio':a,
              'wholeDecodeExitCode':code,'all54115Pts1500Verified':True,'aacPath':rel(aac),'aacSha256':sha(aac),'pcmPath':rel(wav),'pcmSha256':sha(wav),'identicalReviewedWholeAacAndPcm':True});save()
        state['loudnessExitCode']=run([FF,'-hide_banner','-nostdin','-threads','2','-i',str(captioned),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],'final-loudness')
        log=(LOCAL/'final-loudness.log').read_text(encoding='utf-8',errors='replace');i=log.rfind('{');j=log.rfind('}');measurement=json.loads(log[i:j+1])
        assert -16.5<float(measurement['input_i'])<-15.5 and float(measurement['input_tp'])<=-1.5
        state.update(status='completed-await-all-final-pixel-review',exitCode=0,finishedAt=now(),frames=54115,seconds=54115/60,
          measuredBody={'frames':53395,'actual':21358,'explanation':32037,'ratioErrorFrames':0,'rule':'explicit lecture40:60 exception'},
          originalIntroFrames=120,originalMembershipFrames=600,measurement=measurement,
          currentAudioComparisonPreservedByIdenticalAacAndPcm=True,protectedBaselineUnchanged=all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files']));save()
        assert state['protectedBaselineUnchanged']
        print(json.dumps({'exitCode':0,'frames':54115,'originalAacAndPcmIdentical':True,'allFinalPixelsApproved':False}),flush=True)
    except Exception:
        state.update(status='failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());save();raise
if __name__=='__main__':main()
