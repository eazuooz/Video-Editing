"""Preserve failed v1 and prepare absolute-PTS retained-range recovery."""
from pathlib import Path
from datetime import datetime, timezone
import json, subprocess, hashlib, psutil
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
failed=read(OUT/'final-pair-execution-v1.json')
assert failed['status']=='failed' and failed['exitCode']==1
assert not psutil.pid_exists(failed['pid']) or psutil.Process(failed['pid']).create_time()!=failed['createTime']
baseline=ROOT/'shared/output/motion-canvas/game-math-polar-3d.mp4'
partial=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/final-pair-v1/retained-00000-01669.mp4'
def frames(p,interval):
    return json.loads(subprocess.check_output([FP,'-v','error','-threads','2','-read_intervals',interval,'-select_streams','v:0','-show_frames','-show_entries','frame=pts,sample_aspect_ratio,pix_fmt,width,height,color_range,color_space,color_primaries,color_transfer','-of','json',str(p)]))['frames']
source=frames(baseline,'0%28');bad=frames(partial,'0%30')
assert len(source)==1680 and [int(v['pts']) for v in source]==list(range(0,1680*1500,1500))
assert len(bad)==1667 and [int(v['pts']) for v in bad]==list(range(0,1667*1500,1500))
assert all(source[1666].get(k) is None for k in ['color_range','color_space','color_primaries','color_transfer'])
assert source[1667]['color_range']=='tv' and source[1667]['color_space']=='bt709'
now=datetime.now(timezone.utc).isoformat()
evidence={'observedAt':now,'failedWorkerExitCode':1,'exitObservedChunk':'577b7a',
 'failedPid':failed['pid'],'failedCreateTime':failed['createTime'],'failedPidAbsent':True,
 'sourceFirst1680PtsAreExact1500':True,'sourceColorChangeFrame':1667,
 'sourceBefore':source[1666],'sourceAfter':source[1667],
 'requestedRetainedFrames':1669,'actualRetainedFrames':1667,'actualRetainedPtsAreExact1500':True,
 'failedMedia':str(partial.relative_to(ROOT).as_posix()),'failedMediaSha256':sha(partial),
 'cause':'setpts=PTS-STARTPTS is reinitialized at source color-metadata change1667. The last two selected frames restart at zero and are dropped by CFR output. Absolute source PTS remain continuous; this is not evidence of VFR source duplication.',
 'repair':'Keep absolute source trim boundaries and subtract the known interval start in1/90000 units: setpts=PTS-startFrame*1500. Validate every retained frame and final whole pair.',
 'failedV1Preserved':True,'reusedReviewedPilots':True,'newFinalPairCreated':False,
 'baselineMutations':0,'narrationChanged':False,'researchControlChanges':0,
 'allFinalPixelsApproved':False,'humanListeningApproved':False,'publicRightsApproved':False}
dest=OUT/'final-pair-pts-failure-direct-review-v1.json';assert not dest.exists()
dest.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=Path(__file__).with_name('assemble-polar-reviewed-pair-v1.py')
new=Path(__file__).with_name('assemble-polar-reviewed-pair-v2.py');assert not new.exists()
code=old.read_text(encoding='utf-8').replace('final-pair-v1','final-pair-v2').replace('final-pair-execution-v1.json','final-pair-execution-v2.json')
code=code.replace("setpts=PTS-STARTPTS,setsar=1','-frames:v',str(count)","setpts=PTS-{a*1500},setsar=1','-frames:v',str(count)")
assert "setpts=PTS-{a*1500}" in code
code=code.replace("FP,'-v','error','-select_streams'","FP,'-v','error','-threads','2','-select_streams'")
code=code.replace("assert args.glyph_outer_exit_code==0", "assert args.glyph_outer_exit_code==0\n    failure=read(OUT/'final-pair-pts-failure-direct-review-v1.json')\n    assert failure['failedWorkerExitCode']==1 and failure['failedPidAbsent']\n    failed=read(OUT/'final-pair-execution-v1.json')\n    assert failed['exitCode']==1 and (not psutil.pid_exists(failed['pid']) or psutil.Process(failed['pid']).create_time()!=failed['createTime'])")
code=code.replace("'priorGlyphOuterExitCode':args.glyph_outer_exit_code,", "'priorGlyphOuterExitCode':args.glyph_outer_exit_code,'preservedFailureEvidence':'final-pair-pts-failure-direct-review-v1.json','retainedPtsMethod':'absolute source PTS minus known start in1/90000 units',")
new.write_text(code,encoding='utf-8')
qfile=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qfile)
q['execution'].setdefault('failedJobs',[]).append({'pid':failed['pid'],'createTime':failed['createTime'],
 'state':'projects/game-math-polar-3d/revision-teaching-clarity-v1/final-pair-execution-v1.json',
 'actualOuterExitCode':1,'exitObservedChunk':'577b7a','causeEvidence':dest.relative_to(ROOT).as_posix(),'historicalMediaPreserved':True})
q['execution'].update(stage='polar-absolute-pts-final-pair-recovery-prepared',heavyJob=None,
 next='Fresh actual resource; one v2 CPU2/GPU0 final pair with absolute PTS. Reuse reviewed pilots and whole audio. Then all final cue/cut/Manim pixels and technical QA.')
q['updatedAt']=now;qfile.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'failedFrames':1667,'expectedFrames':1669,'sourceColorChangeFrame':1667,'recoveryPrepared':True,'newFinalPairCreated':False}))
