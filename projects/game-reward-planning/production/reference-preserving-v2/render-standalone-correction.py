"""Remux unchanged clean video, then burn only the updated subtitle track."""
from pathlib import Path
import subprocess,json,hashlib
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';B=P/'production/local/reference-preserving-v2/edit';O=B/'standalone-v3'
control=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'));assert control['selectedVideo']=='game-reward-planning' and control['selectedRevisionCorrection']['id']=='standalone-v3'
def run(args,name):
 with (O/(name+'.log')).open('wb') as f:r=subprocess.run(['ffmpeg','-hide_banner','-y','-loglevel','warning',*args],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,name
run(['-i',str(B/'game-reward-planning-v2-clean.mp4'),'-i',str(O/'final-mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-ar','48000','-t',str(33770/60),'-movflags','+faststart',str(O/'game-reward-planning-v2-clean.mp4')],'clean-remux')
def streamhash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
before=streamhash(B/'game-reward-planning-v2-clean.mp4');after=streamhash(O/'game-reward-planning-v2-clean.mp4');assert before==after
(O/'visual-reuse.json').write_text(json.dumps({'originalVideoStream':before,'currentVideoStream':after,'encodedCleanVideoStreamIdentical':True,'frames':33770,'fps':60,'dimensions':[1920,1080],'bodyRatioPreserved':True,'previousVisualEvidence':'../integrity.json and review ledger currentRevision.encodedVisualReview','changedVisualScope':'Caption text/timing for four sentences only'},indent=2)+'\n')
print('Clean video stream unchanged; new narration remuxed',flush=True)
ass=(O/'captions.ko.ass').relative_to(R).as_posix();run(['-i',str(O/'game-reward-planning-v2-clean.mp4'),'-vf',f'subtitles={ass}','-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000','-c:a','copy','-movflags','+faststart',str(O/'game-reward-planning-v2-captioned.mp4')],'captioned')
print('Captioned1080p60 master ready',flush=True)
