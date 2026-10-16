from pathlib import Path
import json,subprocess,hashlib,argparse
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';O=P/'production/local/reference-preserving-v2/edit';plan=json.loads((P/'production/reference-preserving-v2/edit-plan.json').read_text(encoding='utf8'))
MC=R/'shared/output/game-reward-planning/reference-preserving-v2/game-reward-planning-v2-production-explanations.mp4'
def run(args,name):
 with (O/(name+'.log')).open('w',encoding='utf8') as f:p=subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError((O/(name+'.log')).read_text(encoding='utf8')[-2500:])
enc=['-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000']
def slice_mc(name,start,frames):
 output=O/(name+'.mp4');stamp=O/(name+'-mc.json');signature={'sourceSha256':mcsha,'start':start,'frames':frames}
 if output.exists() and stamp.exists() and json.loads(stamp.read_text())==signature:return
 run(['-ss',str(start/60),'-i',str(MC),'-an','-frames:v',str(frames),'-vf','fps=60,setsar=1',*enc,str(output)],name+'-mc');stamp.write_text(json.dumps(signature));print('Sliced',name,flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--stage',choices=['slices','clean','captioned'],required=True);a.add_argument('--audio-from',type=Path);args=a.parse_args()
 if args.stage=='slices':
  mcsha=hashlib.sha256(MC.read_bytes()).hexdigest()
  for c in plan['cuts']:
   if 'mcStartFrame' in c:slice_mc(c['id'],c['mcStartFrame'],c['frames'])
  slice_mc('branding',plan['mcFrames'],120);slice_mc('membership',plan['mcFrames']+120,600)
  files=[O/'branding.mp4',*[O/(c['id']+'.mp4') for c in plan['cuts']],O/'membership.mp4'];(O/'concat.txt').write_text('\n'.join("file '"+str(p).replace('\\','/')+"'" for p in files)+'\n',encoding='utf8')
 elif args.stage=='clean':
  source=args.audio_from or O/'final-mix.wav'
  audio=['-c:a','copy'] if args.audio_from else ['-af','apad','-c:a','aac','-b:a','320k','-ar','48000']
  run(['-f','concat','-safe','0','-i',str(O/'concat.txt'),'-i',str(source),'-map','0:v','-map','1:a','-frames:v',str(plan['totalFrames']),'-t',str(plan['totalFrames']/60),*enc,*audio,'-movflags','+faststart',str(O/'game-reward-planning-v2-clean.mp4')],'clean-master');print('Clean master encoded')
 else:
  ass=str((O/'captions.ko.ass').relative_to(R)).replace('\\','/')
  run(['-i',str(O/'game-reward-planning-v2-clean.mp4'),'-vf',f'subtitles={ass}',*enc,'-c:a','copy','-movflags','+faststart',str(O/'game-reward-planning-v2-captioned.mp4')],'captioned-master');print('Captioned1080p60 master encoded')
