"""Prepared guarded pair worker; execute only after current mixed80-context review.

Original12 scene order, six explanations, intro/outro and all approved PCM stay
untouched. Only the six inspected annotation windows replace corresponding
native scene ranges, beside the measured two new explanation/example bridges.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,re,subprocess,traceback
os.environ['OMP_NUM_THREADS']='2'
import psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/final-pair-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,o):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def probe(p):return json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-show_format','-of','json',str(p)]))
def ptscheck(p,n):
    z=json.loads(subprocess.check_output([FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=pts','-of','json',str(p)]))
    assert [int(v['pts']) for v in z['frames']]==list(range(0,n*1500,1500)),str(p)
    q=probe(p);s=next(x for x in q['streams'] if x['codec_type']=='video')
    assert (s['width'],s['height'],s['r_frame_rate'],s['time_base'])==(1920,1080,'60/1','1/90000')
    return s
def audiohash(p):
    q=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(p)]))
    rows=[v['data_hash'] for v in q['packets']];assert rows
    return dict(packets=len(rows),orderedPacketHashesSha256=hashlib.sha256('\n'.join(rows).encode()).hexdigest())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
    resource=read(ROOT/args.resource)
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
    subprocess.run([NODE,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)
    approved=read(R/'current-mixed-complete-direct-review-v1.json')
    assert approved['all14WholeAnd66IndependentContextsDirectlyCompared'] and approved['currentMixedContentReviewPassed']
    layout=read(R/'caption-layout-v1.json');assert layout['allCuesMeasured'] and not layout['unresolvedLayoutErrors']
    plan=read(R/'measured-additive-plan-v1.json');mix=read(R/'current-mix-execution-v1.json')
    assert mix['actualExitCode']==0 and approved['mixAacSha256']==mix['mixAacSha256']
    assert sha(ROOT/mix['mixAac'])==mix['mixAacSha256'] and abs(plan['ratioErrorFrames'])<=1
    protected=read(R/'narration-tts-waiting-v1.json')['protectedInputs']
    for v in protected:assert sha(ROOT/v['path'])==v['sha256']
    retained=read(R/'retained-annotation-render-execution-v1.json')
    assert read(R/'retained-encoded-sample-direct-review-v1.json')['encodedSelectedSampleReviewPassed']
    mc=read(R/'additive-mc-direct-review-v3.json');assert mc['selectedGoalSamplesApproved']
    baseline=read(ROOT/'projects/motion-sickness-games/production/visual-depth-v1/assembly-inputs.json')
    for v in baseline['segments']:assert sha(ROOT/v['file'])==v['sha256']
    sp=R/'final-pair-execution-v1.json';assert not sp.exists() and not LOCAL.exists()
    LOCAL.mkdir(parents=True);me=psutil.Process()
    if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
    state=dict(schemaVersion=1,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,
      startedAt=now(),status='assembling-measured14-scenes-current-pair',exitCode=None,resource=resource,cpuThreads=2,gpuJobs=0,
      pieces=[],jobs=[],newMediaApproved=False,allFinalPixelsApproved=False,humanListeningApproved=False,publicRightsApproved=False,
      oldPcmOrWhiteScenesRegenerated=False,researchManipulations=0,newGitMedia=0)
    def checkpoint():
        ss=sp.with_name(sp.stem+'.session.json')
        if ss.exists():
            s=read(ss);assert s['pid']==me.pid and abs(s['createTime']-me.create_time())<.01;state['sessionId']=s['sessionId']
        state['updatedAt']=now();save(sp,state)
        cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],ownedJob=dict(pid=me.pid,
          createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=rel(sp),
          cpuThreads=2,gpuJobs=0,exitCode=state['exitCode']),allFinalPixelsApproved=False,qaApproved=False,
          next='Observe actual pair exit, inspect every final cue/cut/annotation/2.5D sample and continuous transitions, collect4files and finish one new private replacement/settings/Git before replacing the schedule.')
        save(R/'latest-checkpoint.json',cp)
        qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
        q['execution'].update(currentSlug='motion-sickness-games',stage=cp['stage'],ownedJob=cp['ownedJob'],next=cp['next'])
        next(x for x in q['items'] if x['slug']=='motion-sickness-games').update(status=cp['stage'],currentExecution=cp['ownedJob'])
        q['updatedAt']=now();assert qp.read_text('utf-8-sig')==raw;save(qp,q)
    def run(args,name,info=False):
        cmd=[FF,'-hide_banner','-nostdin','-v','info' if info else 'error','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args]
        state['currentCommand']=cmd;state['currentStage']=name;checkpoint()
        with (LOCAL/(name+'.log')).open('wb') as log:x=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=log).returncode
        state['jobs'].append(dict(stage=name,exitCode=x,log=rel(LOCAL/(name+'.log'))));checkpoint();assert x==0,name
        print(json.dumps(dict(stage=name,exitCode=x)),flush=True);return x
    enc=['-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart']
    def generated(p,n,kind,inputs):
        ptscheck(p,n);state['pieces'].append(dict(path=rel(p),sha256=sha(p),frames=n,kind=kind,inputs=inputs,allPts1500Verified=True));checkpoint()
        return p
    def old(sid):return baseline['segments'][int(sid)]
    def mcpart(name,selected):
        src=ROOT/selected['source'];assert sha(src)==selected['sourceSha256'];n=selected['frames'];a=selected['firstFrame']
        p=LOCAL/(name+'.mp4');run(['-i',str(src),'-vf',f'trim=start_frame={a}:end_frame={a+n},setpts=PTS-STARTPTS,setsar=1','-frames:v',str(n),*enc,str(p)],name)
        return generated(p,n,'selected-new-projected-explanation',selected)
    def nativepart(seg):
        src=ROOT/seg['file'];assert sha(src)==seg['sourceSha256'];n=seg['frames'];a=seg['sourceFirstPts'];b=seg['sourceEndExclusivePts']
        p=LOCAL/(seg['id']+'.mp4');seek=max(0,seg['sourceFirstFrame']-120)/60
        title='PowerWash Simulator · FuturLab 개발 시연 (2022 WIP) · 발췌'
        label='서로 다른 개발 시연 발췌 · 연속 비교가 아닙니다'
        filt=f"trim=start_pts={a}:end_pts={b},showinfo,setpts=PTS-{a},setsar=1,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='{title}':fontsize=22:fontcolor=white:box=1:boxcolor=black@0.70:boxborderw=7:x=(w-tw)/2:y=28,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='{label}':fontsize=28:fontcolor=white:box=1:boxcolor=black@0.70:boxborderw=7:x=(w-tw)/2:y=845"
        run(['-ss',f'{seek:.12f}','-copyts','-i',str(src),'-vf',filt,'-frames:v',str(n),*enc,str(p)],seg['id'],True)
        log=(LOCAL/(seg['id']+'.log')).read_text('utf-8',errors='replace')
        actual=[int(v) for v in re.findall(r'\bn:\s*\d+\s+pts:\s*(-?\d+)',log)]
        assert actual==list(range(a,b,256)),('Current native PTS differ',seg['id'],actual[:2],actual[-2:])
        return generated(p,n,'new-unique-normal-speed-native-action',seg)
    def annotate_scene(scene):
        sid=scene['id'];base=old(sid);w=next(w for w in retained['windows'] if w['scene']==sid)
        src=ROOT/base['file'];ann=ROOT/w['video']['path'];assert sha(ann)==w['video']['sha256']
        a=w['sceneLocalStart'];b=a+w['frames'];n=scene['frames'];labels=[];filters=[]
        if a>0:filters.append(f'[0:v]trim=start_frame=0:end_frame={a},setpts=PTS-STARTPTS[prefix]');labels.append('[prefix]')
        filters.append(f'[1:v]trim=start_frame=0:end_frame={w["frames"]},setpts=PTS-STARTPTS[marked]');labels.append('[marked]')
        if b<n:filters.append(f'[0:v]trim=start_frame={b}:end_frame={n},setpts=PTS-STARTPTS[suffix]');labels.append('[suffix]')
        filters.append(''.join(labels)+f'concat=n={len(labels)}:v=1:a=0,setsar=1,fps=60,settb=1/90000,setpts=N*1500[v]')
        p=LOCAL/f'scene{sid}.annotated.mp4'
        run(['-i',str(src),'-i',str(ann),'-filter_complex',';'.join(filters),'-map','[v]','-frames:v',str(n),*enc,str(p)],f'scene{sid}-native-window-replacement')
        return generated(p,n,'retained-actual-with-one-reviewed-annotation-window',dict(base=base,annotation=w['video'],sceneLocalFrom=a,sceneLocalTo=b))
    def reused(v,kind):
        p=ROOT/v['file'];assert sha(p)==v['sha256'];ptscheck(p,v['frames'])
        state['pieces'].append(dict(path=v['file'],sha256=v['sha256'],frames=v['frames'],kind=kind,reencoded=False,allPts1500Verified=True));checkpoint();return p
    checkpoint()
    try:
        files=[reused(baseline['segments'][0],'original120-frame-branding')]
        for scene in plan['scenes']:
            sid=scene['id']
            if sid in ['00a','06b']:
                for seg in scene['segments']:
                    if seg['classification']=='explanation':files.append(mcpart(seg['id'],mc['selectedOpening'] if sid=='00a' else mc['selectedGoal']))
                    elif 'annotationPilot' in seg:
                        p=ROOT/seg['annotationPilot'];assert sha(p)=='2c8cc9f51f2f9e9d9d4ee38dfdfd864087ab8f1b24e879f32a31dbacb768f637'
                        files.append(generated(p,seg['frames'],'reviewed-moving-opening-annotation',seg))
                    else:files.append(nativepart(seg))
            elif int(sid)%2:files.append(annotate_scene(scene))
            else:files.append(reused(old(sid),'retained-projected-explanation'))
        files.append(reused(baseline['segments'][-1],'original600-frame-member-ending'))
        assert len(files)==20 and sum(v['frames'] for v in state['pieces'])==plan['totalFrames']
        concat=LOCAL/'current-concat.ffconcat';concat.write_text('ffconcat version 1.0\n'+''.join(f"file '{p.as_posix()}'\nduration {v['frames']/60:.12f}\n" for p,v in zip(files,state['pieces'])),'utf-8')
        joined=LOCAL/'joined.unsnapped.mp4';aac=ROOT/mix['mixAac']
        run(['-f','concat','-safe','0','-i',str(concat),'-i',str(aac),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(plan['seconds']),'-video_track_timescale','90000','-movflags','+faststart',str(joined)],'concat-current-silent-pieces-with-reviewed-AAC')
        packets=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','json',str(joined)]))['packets']
        ordered=sorted(int(v['pts']) for v in packets);assert len(ordered)==plan['totalFrames'] and all(abs(t-i*1500)<=2 for i,t in enumerate(ordered))
        clean=LOCAL/'motion-sickness-games.clean.mp4';captioned=LOCAL/'motion-sickness-games.captioned.mp4'
        run(['-i',str(joined),'-map','0:v:0','-map','0:a:0','-c','copy','-bsf:v','setts=pts=round(PTS/1500)*1500:dts=round(DTS/1500)*1500:duration=1500','-video_track_timescale','90000','-movflags','+faststart',str(clean)],'snap-concat-subframe-PTS')
        ptscheck(clean,plan['totalFrames'])
        ass=ROOT/layout['ass'];assert sha(ass)==layout['assSha256']
        run(['-i',str(clean),'-map','0:v:0','-map','0:a:0','-vf',f'ass={rel(ass)},setsar=1','-frames:v',str(plan['totalFrames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',str(captioned)],'fixed-bottom-KO-captions')
        originalaudio=audiohash(aac);pair=[]
        for p in [clean,captioned]:
            v=ptscheck(p,plan['totalFrames']);x=run(['-i',str(p),'-f','null','-'],p.stem+'-whole-decode')
            audio=audiohash(p);assert audio==originalaudio
            pair.append(dict(path=rel(p),sha256=sha(p),size=p.stat().st_size,video=v,audioPacketProof=audio,wholeDecodeExitCode=x,allPts1500Verified=True,identicalReviewedWholeAacPackets=True))
        for v in protected:assert sha(ROOT/v['path'])==v['sha256']
        state.update(status='current-pair-complete-awaiting-direct-final-pixels',exitCode=0,finishedAt=now(),frames=plan['totalFrames'],seconds=plan['seconds'],pair=pair,
          originalIntroFrames=120,originalMemberFrames=600,all26ProtectedInputsUnchanged=True,currentAudioPacketProof=originalaudio,
          bodyMeasured=dict(frames=plan['bodyFrames'],actual=plan['actualFrames'],explanation=plan['explanationFrames'],ratioErrorFrames=plan['ratioErrorFrames']))
        checkpoint();print(json.dumps(dict(exitCode=0,frames=plan['totalFrames'],pairWholeDecodeZero=True,identicalReviewedAac=True,finalPixelApproval=False)),flush=True)
    except BaseException:
        state.update(status='failed-current-pair-preserve-local-pieces',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
if __name__=='__main__':main()
