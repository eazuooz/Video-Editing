from pathlib import Path
import subprocess,json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];folder=ROOT/'projects/picking-sides/production/visual-depth-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
index=json.loads((folder/'encoded-pixels-local/index.json').read_text('utf-8-sig'))
write(folder/'encoded-pixel-direct-review-pre-outro-fix.json',dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),videoSha256=index['videoSha256'],srtSha256=index['srtSha256'],boardsRead=100,framesRead=600,cuesRead=151,gameCutsRead=45,boardHashes=[b['sha256'] for b in index['boards']],allFinalPixelsReviewed=False,requiredFix='outro-source-frame-0-old-PPT-flash',findings=['All six replacement explanation scenes show projected top/side faces, meaningful spatial changes and chapter-specific narration phases.','All 151 cue start/middle/end pixels read; fixed bottom-center style, wrapping and game focus visibility pass.','Chapter 04 label/border proximity inspected separately at full resolution; glyphs clear.','Board100 frame36293 reproduces old PPT for one frame at original member-clip frame0; frame1,2,15,30,60 directly inspected and actual member identities retained. Replace frame0 with a duplicate of member frame1.'],humanListening='pending'))
src=ROOT/'projects/picking-sides/production/final-v1/outro.mp4';target=folder/'outro-boundary-fixed.mp4'
if target.exists():raise RuntimeError('Inspect existing fix, do not repeat')
ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';probe='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
cmd=[ff,'-v','error','-threads','2','-i',str(src),'-vf','trim=start_frame=1,settb=1/60,setpts=N,tpad=start=1:start_mode=clone','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-enc_time_base','1:60','-fps_mode','passthrough','-video_track_timescale','90000',str(target)]
subprocess.run(cmd,check=True)
p=json.loads(subprocess.check_output([probe,'-v','error','-show_streams','-of','json',str(target)],text=True));v=p['streams'][0]
assert int(v['nb_frames'])==600 and v['time_base']=='1/90000'
subprocess.run([ff,'-v','error','-threads','2','-i',str(target),'-f','null','-'],check=True)
write(folder/'outro-boundary-fix.json',dict(source=src.relative_to(ROOT).as_posix(),sourceSha256=sha(src),path=target.relative_to(ROOT).as_posix(),sha256=sha(target),frames=600,fullDecodeExitCode=0,change='Only remove old-PPT source frame0; duplicate actual member source frame1 at first frame. Frames1..599 retain original timing and member identities; source file preserved.',command=cmd,pixelsPending=True))
a=json.loads((folder/'assembly-inputs.json').read_text('utf-8-sig'));a['segments'][-1]['file']=target.relative_to(ROOT).as_posix();a['segments'][-1]['boundaryFix']='outro-boundary-fix.json';write(folder/'assembly-inputs.json',a)
qpath=ROOT/'production/batches/visual-depth-revision/queue.json';q=json.loads(qpath.read_text('utf-8-sig'));i=q['items'][0];i.update(stage='final-pixel-one-frame-outro-fix',allPixelsReviewed=False,pid=None,activePid=None,pixelReview='projects/picking-sides/production/visual-depth-v1/encoded-pixel-direct-review-pre-outro-fix.json');write(qpath,q)
print('One-frame ending boundary corrected; final pair pixel approval remains false.')
