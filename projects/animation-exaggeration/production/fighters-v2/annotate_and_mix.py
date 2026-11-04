"""Speech-timed editorial directions, and measured delivery loudness; raw VO unchanged."""
from pathlib import Path
import json,subprocess,re
import audio_pipeline as ap,video_pipeline as vp
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v2'
def main():
 ap.require_authorized('mix');p=ap.read(H/'edit-plan.json');by={c['id']:c for c in p['cuts']}
 for cid in ['A02-F32','A02-F31','A02-F23']:by[cid]['marks']=[]
 def arrow(cid,name,t0,t1,points,label,pos,color='yellow'):
  by[cid]['marks'].append({'id':name,'shape':'arrow','t0':t0,'t1':t1,'color':color,'thickness':8,'label':label,'labelPosition':pos,'points':points,'keyframes':[{'t':t0,'points':points},{'t':t1,'points':points}],'revealSeconds':.25,'interpretation':'Editorial direction/held-pose region, not a measured motion vector or detector.'})
 # Source229.4–231.1: held charge pose. Leader ends at raised forearm;
 # the complete arm remains visible in the directly inspected source sequence.
 arrow('A02-F32','raised-arm',1.8,3.5,[[860,390],[760,390],[654,446]],'팔을 뒤로',[860,320])
 # Source221.8–223.5: same named move's separate first demonstration.
 arrow('A02-F31','preparation',1.8,3.5,[[880,390],[780,430],[645,478]],'준비 자세',[880,320],'green')
 # Source109.5–110.4: native hitstop/rising slash. This shows direction
 # alongside the silhouette and clears before the following camera change.
 arrow('A02-F23','rise-direction',1.5,2.4,[[1000,680],[1000,540],[1000,365]],'상승 방향',[600,350],'blue')
 ap.save(H/'edit-plan.json',p)
 for c in p['cuts']:
  if c.get('marks') and c['kind']=='independent-gameplay':vp.gameplay_labels(c,p)
 ap.save(H/'annotation-review.json',{'sourceFrames':['source-review/kof-windup-composed.png','source-review/gg-rise-composed.png'],'scope':'Short held-preparation and rising-direction guides. No invented detector/rig measurements. All marks clear at cuts.','captionProtectedRect':[150,892,1784,1060],'sourceViewport':[160,90,1600,792],'watermarksAndHudRetained':True,'finalPixelReview':'pending'})
 source=L/'edit/final-mix.wav';dest=L/'edit/final-mix-normalized.wav'
 # Two-pass measured normalization is applied only to the delivery mix.
 measurement=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(source),'-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','NUL'],capture_output=True,text=True,check=True).stderr
 stats=json.loads(measurement[measurement.rfind('{'):measurement.rfind('}')+1])
 f='loudnorm=I=-16:TP=-2:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true:print_format=json'.format(**stats)
 result=subprocess.run(['ffmpeg','-y','-hide_banner','-nostats','-i',str(source),'-af',f,'-ar','48000','-ac','2','-c:a','pcm_s24le',str(dest)],capture_output=True,text=True,check=True)
 (L/'edit/normalization.log').write_text(result.stderr,encoding='utf-8')
 p['mixFile']=ap.relative(dest);ap.save(H/'edit-plan.json',p)
 ap.save(H/'delivery-audio-normalization.json',{'input':ap.artifact(source),'output':ap.artifact(dest),'inputMeasurement':stats,'sourceVoiceFilesModified':False,'existingSpeechSpeedModified':False,'purpose':'Match original channel voice loudness while containing peaks; raw stems remain separately preserved.'})
 print('Three source-anchored guides and measured delivery normalization prepared.')
if __name__=='__main__':main()
