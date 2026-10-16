from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';D=P/'production/reference-preserving-v2';O=P/'production/local/reference-preserving-v2/edit/original-deletion-v4';plan=json.loads((D/'original-deletion-v4-plan.json').read_text(encoding='utf8'))
c=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'));assert c['selectedVideo']=='game-reward-planning' and c['selectedRevisionCorrection']['id']=='original-deletion-v4'
def run(args,name):
 with (O/(name+'.log')).open('wb') as f:r=subprocess.run(['ffmpeg','-hide_banner','-y','-loglevel','warning',*args],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,name
run(['-i',str(O/'final-mix.wav'),'-c:a','aac','-b:a','320k','-ar','48000','-t',str(plan['totalFrames']/60),str(O/'final-audio.m4a')],'aac')
deleted='+'.join(f"between(n,{x['startFrame']},{x['endFrame']-1})" for x in plan['deletions']);ass=(O/'captions.ko.ass').relative_to(R).as_posix();graph=f"[0:v]select='not({deleted})',setpts=N/(60*TB),split=2[clean][sub];[sub]subtitles={ass}[captioned]"
enc=['-c:v','libx264','-threads:v','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000','-frames:v',str(plan['totalFrames']),'-t',str(plan['totalFrames']/60),'-c:a','copy','-movflags','+faststart']
args=['-i',str(R/plan['sourceMaster']),'-i',str(O/'final-audio.m4a'),'-filter_complex_threads','2','-filter_complex',graph,'-map','[clean]','-map','1:a',*enc,str(O/'game-reward-planning-v2-clean.mp4'),'-map','[captioned]','-map','1:a',*enc,str(O/'game-reward-planning-v2-captioned.mp4')]
run(args,'retained-original-pair');print('Both1080p60 outputs encoded from retained original v2 frames; original voice reused')
