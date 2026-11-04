"""Speech-timed editorial directions, and measured delivery loudness; raw VO unchanged."""
from pathlib import Path
import json,subprocess,re
import audio_pipeline as ap,video_pipeline as vp
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v3'
def main():
 ap.require_authorized('mix');p=ap.read(H/'edit-plan.json');by={c['id']:c for c in p['cuts']}
 source=L/'edit/final-mix.wav';dest=L/'edit/final-mix-normalized.wav'
 # Two-pass measured normalization is applied only to the delivery mix.
 measurement=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(source),'-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','NUL'],capture_output=True,text=True,check=True).stderr
 stats=json.loads(measurement[measurement.rfind('{'):measurement.rfind('}')+1])
 f='loudnorm=I=-16:TP=-2:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true:print_format=json'.format(**stats)
 result=subprocess.run(['ffmpeg','-y','-hide_banner','-nostats','-i',str(source),'-af',f,'-ar','48000','-ac','2','-c:a','pcm_s24le',str(dest)],capture_output=True,text=True,check=True)
 (L/'edit/normalization.log').write_text(result.stderr,encoding='utf-8')
 p['mixFile']=ap.relative(dest);ap.save(H/'edit-plan.json',p)
 ap.save(H/'delivery-audio-normalization.json',{'input':ap.artifact(source),'output':ap.artifact(dest),'inputMeasurement':stats,'sourceVoiceFilesModified':False,'existingSpeechSpeedModified':False,'purpose':'Match original channel voice loudness while containing peaks; raw stems remain separately preserved.'})
 print('Measured delivery normalization prepared.')
if __name__=='__main__':main()
