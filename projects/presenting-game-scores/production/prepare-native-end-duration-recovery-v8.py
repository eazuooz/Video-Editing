"""Preserve failed1318-frame input and prepare exact native final-frame duration recovery."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,psutil,subprocess
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
oldp=BASE/'measured-native-inputs-execution-v7.json';old=read(oldp)
assert old['exitCode']==1 and old['completed']==0 and old['error']=='AssertionError()'
for identity in [old['processIdentity'],old['activeChild']]:
    try: assert abs(psutil.Process(identity['pid']).create_time()-identity['createTime'])>=.01
    except psutil.NoSuchProcess:pass
video=ROOT/'shared/output/presenting-game-scores/measured-native-inputs-v7/classic-01.mp4'
fp='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
p=subprocess.run([fp,'-v','error','-threads','2','-show_frames','-show_entries',
 'frame=best_effort_timestamp,width,height:stream=time_base,nb_frames,avg_frame_rate','-of','json',str(video)],
 capture_output=True,text=True,check=True)
d=json.loads(p.stdout);assert len(d['frames'])==1318 and d['streams'][0]['time_base']=='1/90000'
assert all(f['best_effort_timestamp']==n*1500 for n,f in enumerate(d['frames']))
proof=dict(schemaVersion=8,observedAt=datetime.now(timezone.utc).isoformat(),
 originalState=str(oldp.relative_to(ROOT)),originalStateSha256=sha(oldp),
 originalInput=str(video.relative_to(ROOT)),originalInputSha256=sha(video),
 observedEncodeExitCode=0,observedOuterExitCode=1,expectedFrames=1320,observedFrames=1318,
 observedTimebase='1/90000',allExistingPtsCorrect=True,
 cause='fps terminal handling omitted the remaining display time of source native frame599. Selected550 frames at25fps cover22s; the last source timestamp is21.96s relative. Encoded1318 at60fps cover21.966667s.',
 repair='Carry the last selected native frame through its existing native display interval before ordinary60fps sampling; cap output to exact planned normal-speed frame count. Absolute nativePTS trimming prevents frame-counter reinitialization ambiguity.',
 additionalSourceIntervals=0,loop=False,slowdown=False,extraOutputBeyondPlannedDuration=False,
 originalFailedFilePreserved=True,completedInputsRepeated=0,allFinalPixels=False,
 processOrResearchControls=0,newRasterGitAdditions=0)
dest=BASE/'native-end-duration-failure-review-v8.json';assert not dest.exists()
dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
source=(BASE/'build-measured-native-inputs-v7.py').read_text('utf-8')
source=source.replace("measured-native-inputs-v7'","measured-native-inputs-v8'")
source=source.replace("measured-native-inputs-execution-v7.json'","measured-native-inputs-execution-v8.json'")
source=source.replace("status='building-measured-native-inputs-v7'","status='building-measured-native-inputs-v8'")
oldtrim='trim=f"trim=start_frame={s[\'sourceStartFrame\']}:end_frame={s[\'sourceEndFrameExclusive\']},setpts=PTS-STARTPTS"'
newtrim='''from fractions import Fraction
        endpts=int(Fraction(s['sourceEndFrameExclusive'],1)/Fraction(s['nativeFps'])/Fraction(s['nativeTimebase']))
        trim=f"trim=start_pts={s['nativeStartPts']}:end_pts={endpts},setpts=PTS-{s['nativeStartPts']}"'''
assert oldtrim in source;source=source.replace(oldtrim,newtrim)
source=source.replace('[framed]fps=60:start_time=0:round=near,','[framed]tpad=stop_mode=clone:stop=1,fps=60:start_time=0:round=near,')
source=source.replace("'-threads','2','-i',s['sourcePath']","'-threads','2','-reinit_filter','0','-i',s['sourcePath']")
source=source.replace("results=[],activeChild=None", "recoveryFrom='projects/presenting-game-scores/production/native-end-duration-failure-review-v8.json',results=[],activeChild=None")
code=BASE/'build-measured-native-inputs-v8.py';assert not code.exists();code.write_text(source,'utf-8')
print('Preserved v7 failed1318 frames; new v8 exact-duration producer prepared, no render executed.')
