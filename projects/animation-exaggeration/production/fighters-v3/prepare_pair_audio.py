from pathlib import Path
import audio_pipeline as ap,video_pipeline as vp
H=Path(__file__).resolve().parent;L=H.parent/'local/fighters-v3';R=H.parents[3]
ap.require_authorized('mix');plan=ap.read(H/'edit-plan.json');mix=R/plan['mixFile'];aac=L/'edit/pair-audio.m4a'
signature={'sourceSha256':ap.sha(mix),'duration':plan['totalFrames']/60,'codec':'aac','bitrate':192000,'sampleRate':48000,'channels':2,'deliveryGainDb':0.0}
receipt=L/'edit/aac-source.json'
if not (aac.exists() and receipt.exists() and ap.read(receipt).get('signature')==signature and ap.read(receipt).get('outputSha256')==ap.sha(aac)):
 vp.run(['-i',str(mix),'-vn','-af','volume=0.0dB','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',str(aac)],L/'edit/audio-encode.log')
 ap.save(receipt,{'signature':signature,'outputSha256':ap.sha(aac)})
print('Continuous delivery AAC ready for the unchanged pair')
