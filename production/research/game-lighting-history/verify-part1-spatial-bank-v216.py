from pathlib import Path
import subprocess,json,hashlib,datetime,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'production/research/game-lighting-history/local/part1-spatial-bank-v206'
plan=json.loads((BASE/'plan.json').read_text('utf-8'));job=plan['jobs'][0]
e=json.loads((ROOT/job['execution']).read_text('utf-8'))
if e.get('exitCode')!=0 or e['status']!='complete' or psutil.pid_exists(e['ffmpegPid']):raise RuntimeError('Inspect actual renderer completion/PID reuse first')
out=BASE/'media-verification-v216.json'
if out.exists():raise RuntimeError('Preserve verification')
video=ROOT/job['output'];fp='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
opts=dict(cwd=ROOT,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
probe=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)],**opts));v=next(x for x in probe['streams'] if x['codec_type']=='video')
if int(v['nb_read_frames'])!=job['frames'] or v['r_frame_rate']!='60/1' or v['time_base']!='1/90000' or (v['width'],v['height'])!=(1920,1080):raise RuntimeError('Exact source frame properties failed')
frames=json.loads(subprocess.check_output([fp,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',str(video)],**opts))['frames']
if len(frames)!=4653 or any(int(f['best_effort_timestamp'])!=i*1500 for i,f in enumerate(frames)):raise RuntimeError('Source frame PTS mismatch')
log=BASE/'source-whole-decode-v216.log'
with log.open('w',encoding='utf-8') as handle:
 code=subprocess.call([ff,'-hide_banner','-v','error','-threads','2','-i',str(video),'-threads','2','-f','null','-'],cwd=ROOT,stdout=handle,stderr=handle,creationflags=subprocess.CREATE_NO_WINDOW)
if code!=0 or log.read_text('utf-8').strip():raise RuntimeError('Source whole decode failed')
r=dict(verifiedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),path=job['output'],sha256=hashlib.sha256(video.read_bytes()).hexdigest(),probe=probe,frames=4653,allPtsExact=True,timebase=90000,ptsStep=1500,wholeDecodeExitCode=0,decodeLog=log.relative_to(ROOT).as_posix(),scenes=10,sceneBounds=[dict(id=s['id'],fromFrame=s['fromFrame'],toFrame=s['toFrame']) for s in plan['scenes']],sourceAudioAssembly='production/research/game-lighting-history/local/part1-spatial-bank-v206/audio-assembly-v212.json',allMovingPixelsReviewed=False,allFinalPixelsReviewed=False,finalMix=False,uploaded=False)
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps({'frames':4653,'ptsExact':True,'decodeExit':0,'movingReview':False}))
