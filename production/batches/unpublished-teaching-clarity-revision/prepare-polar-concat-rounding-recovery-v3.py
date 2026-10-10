"""Preserve v2 and recover its one-tick ffconcat duration quantization."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
failed=read(OUT/'final-pair-execution-v2.json')
assert failed['exitCode']==1 and failed['status']=='failed'
assert not psutil.pid_exists(failed['pid']) or psutil.Process(failed['pid']).create_time()!=failed['createTime']
source=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/final-pair-v2/game-math-polar-3d.clean.mp4'
r=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,dts,duration','-of','json',str(source)]))
pts=sorted(int(p['pts']) for p in r['packets']);assert len(pts)==54115
errors=[t-i*1500 for i,t in enumerate(pts)]
assert errors[:48871]==[0]*48871 and errors[48871:]==[-1]*5244
assert all(p['allPts1500Verified'] for p in failed['pieces']) and sum(p['frames'] for p in failed['pieces'])==54115
for p in failed['pieces']:assert sha(ROOT/p['path'])==p['sha256']
now=datetime.now(timezone.utc).isoformat()
proof={'observedAt':now,'actualOuterExitCode':1,'exitObservedChunk':'141823','cimAbsenceObservedChunk':'b56acf',
 'failedPid':failed['pid'],'failedCreateTime':failed['createTime'],'actualFrames':54115,
 'all15PartFramesAndPtsPreviouslyValidated':True,'all15CurrentShasMatched':True,
 'firstOffsetFrame':48871,'offsetTicks':-1,'offsetFrames':5244,'timebase':'1/90000',
 'cause':'ffconcat duration strings are represented in microseconds. Cumulative fractional60fps durations quantize the final two part start timestamps by one1/90000 tick. All54115 frames are present in order; no full-frame loss or VFR duplication.',
 'repair':'Stream-copy the already assembled54115-frame video and wholeAAC, snapping each packet PTS/DTS to the nearest1500 ticks and duration1500 with setts. Guard exact input deviations0/-1, all final decodedPTS, decode, identicalAAC/PCM.',
 'source':source.relative_to(ROOT).as_posix(),'sourceSha256':sha(source),'failedV1AndV2Preserved':True,
 'retainedRangesRerendered':False,'reviewedPilotsRerendered':False,'narrationChanged':False,
 'allFinalPixelsApproved':False,'researchControlChanges':0}
dest=OUT/'final-pair-concat-rounding-direct-review-v2.json';assert not dest.exists()
dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=Path(__file__).with_name('assemble-polar-reviewed-pair-v2.py');new=Path(__file__).with_name('assemble-polar-reviewed-pair-v3.py');assert not new.exists()
code=old.read_text(encoding='utf-8').replace('final-pair-v2','final-pair-v3').replace('final-pair-execution-v2.json','final-pair-execution-v3.json')
start=code.index('        cursor=0\n');end=code.index('        ptscheck(clean,54115)',start)
replacement="""        rounding=read(OUT/'final-pair-concat-rounding-direct-review-v2.json')
        prior=read(OUT/'final-pair-execution-v2.json')
        assert prior['exitCode']==1 and (not psutil.pid_exists(prior['pid']) or psutil.Process(prior['pid']).create_time()!=prior['createTime'])
        assembled=ROOT/rounding['source'];assert sha(assembled)==rounding['sourceSha256']
        packets=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','json',str(assembled)]))['packets']
        ordered=sorted(int(v['pts']) for v in packets)
        assert len(ordered)==54115 and all(t-i*1500 in [0,-1] for i,t in enumerate(ordered))
        state['pieces']=prior['pieces']
        assert len(state['pieces'])==15 and sum(p['frames'] for p in state['pieces'])==54115
        for p in state['pieces']:assert sha(ROOT/p['path'])==p['sha256'] and p['allPts1500Verified']
        state.update(reusedAll15VerifiedPieces=True,retainedRangesRerendered=False,roundingRecoveryEvidence='final-pair-concat-rounding-direct-review-v2.json');save()
        clean=LOCAL/'game-math-polar-3d.clean.mp4';captioned=LOCAL/'game-math-polar-3d.captioned.mp4'
        state['cleanEncodeExitCode']=run([FF,'-hide_banner','-nostdin','-v','error','-i',str(assembled),'-map','0:v:0','-map','0:a:0','-c','copy','-bsf:v','setts=pts=round(PTS/1500)*1500:dts=round(DTS/1500)*1500:duration=1500','-video_track_timescale','90000','-movflags','+faststart',str(clean)],'snap-concat-subframe-rounding')
"""
code=code[:start]+replacement+code[end:]
new.write_text(code,encoding='utf-8')
qfile=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qfile)
q['execution']['failedJobs'].append({'sessionId':73920,'pid':failed['pid'],'createTime':failed['createTime'],
 'state':'projects/game-math-polar-3d/revision-teaching-clarity-v1/final-pair-execution-v2.json','actualOuterExitCode':1,
 'exitObservedChunk':'141823','causeEvidence':dest.relative_to(ROOT).as_posix(),'historicalMediaPreserved':True,'all15VerifiedPartsReusable':True})
q['execution'].update(stage='polar-concat-subframe-rounding-recovery-prepared',heavyJob=None,
 next='Fresh resource; one v3 CPU2/GPU0 stream-copy packet rounding and fixed-caption pair. Reuse all15 verified parts; no pilot/audio rerender.')
q['updatedAt']=now;qfile.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frames':54115,'missingFrames':0,'last5244PacketPtsOffsetTicks':-1,'recoveryPrepared':True,'retainedRangesRerendered':False}))
