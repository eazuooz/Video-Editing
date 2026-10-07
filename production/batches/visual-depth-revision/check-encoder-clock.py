from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[3];folder=ROOT/'projects/picking-sides/production/visual-depth-v1';ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';probe=ff.replace('ffmpeg','ffprobe')
args=[ff,'-hide_banner','-v','warning','-reinit_filter','0','-f','concat','-safe','0','-i',str(folder/'revised-concat.txt'),'-vf','settb=expr=1/60,setpts=N','-frames:v','120','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-enc_time_base','1:60','-fps_mode','passthrough','-video_track_timescale','90000',str(folder/'encoder-clock-fixed-120.mp4')]
if (folder/'encoder-clock-fixed-120.mp4').exists():raise RuntimeError('Preserve observed diagnostic')
subprocess.run(args,check=True,cwd=ROOT)
data=json.loads(subprocess.check_output([probe,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',str(folder/'encoder-clock-fixed-120.mp4')],text=True));pts=[int(f['best_effort_timestamp']) for f in data['frames']]
result=dict(frames=len(pts),exact=pts==list(range(0,180000,1500)),pts=pts,command=args);(folder/'encoder-clock-fixed-120-verification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(dict(frames=len(pts),exact=result['exact'])))
