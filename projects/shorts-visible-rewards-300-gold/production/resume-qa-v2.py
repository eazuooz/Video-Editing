"""Resume after an outdated loudness bound; never repeat successful video decode."""
from pathlib import Path
import importlib.util,json,hashlib,datetime
import numpy as np
S=importlib.util.spec_from_file_location('short_qa',Path(__file__).with_name('verify-short.py'));V=importlib.util.module_from_spec(S);S.loader.exec_module(V)
Q=V.QA;target=Q/'short-qa.json';old=V.read_json(target)
assert not old['technicalExecutionComplete'] and 'integrated loudness' in old['error']
backup=Q/'short-qa-before-working-target-contract-fix.json';assert not backup.exists();backup.write_bytes(target.read_bytes())
integrity=V.read_json(Q/'integrity.json');assert integrity['status']=='pass' and integrity['pairedAacPayloadIdentical'] and integrity['pairedDecodedAudioIdentical']
for row in integrity['files'].values():
 assert V.artifact(V.ROOT/row['file']['path'])==row['file']
 assert row['fullDecode']['status']=='pass' and row['fullDecode']['decodedVideoFrames']==1812
 assert V.artifact(V.ROOT/row['fullDecode']['log']['path'])==row['fullDecode']['log']
source,proof,audio,inputs,provenance=V.source_and_inputs();captions,fonts=V.caption_and_font_preflight()
video=V.OUT/(V.PROJECT.name+'.captioned.mp4')
# Both complete video decodes already passed. Only recover the lost in-memory
# AAC PCM once for the interrupted audio step, retaining it for future analysis.
pcmfile=Q/'captioned-decoded-audio.npy'
if pcmfile.exists():pcm=np.load(pcmfile)
else:
 raw=V.renderer.run([V.renderer.FFMPEG,'-v','error','-i',str(video),'-vn','-ar','48000','-ac','2','-f','f32le','pipe:1']).stdout
 pcm=np.frombuffer(raw,dtype='<f4').reshape(-1,2)[:round(30.2*48000)].copy();np.save(pcmfile,pcm)
assert pcm.shape==(1449600,2)
a=V.audio_review(source,audio,pcm);pixels=V.pixel_samples(captions,video)
current=dict(inputs=[V.artifact(p) for p in inputs],finalFiles=[integrity['files'][k]['file'] for k in ['clean','captioned']])
d=dict(signature=hashlib.sha256(json.dumps(current,sort_keys=True).encode()).hexdigest(),inputs=current,technicalExecutionComplete=True,status='technical-pass-direct-review-pending' if not a['flaggedTransferWindows'] else 'audio-flags-need-targeted-review',integrity=integrity,sourceProvenance=provenance,fontPreflight=fonts,audioReview=V.artifact(Q/'audio-review.json'),pixelSamples=V.artifact(Q/'pixel-samples.json'),captionCount=len(captions['cues']),extractedUniqueFrames=pixels['uniqueFrameCount'],flaggedVoiceTransferWindows=len(a['flaggedTransferWindows']),fullVideoDecodeReusedFrom='Same-hash current integrity and complete showinfo logs; no video decode repeated',audioRecovery='One AAC-only decode recovered interrupted in-memory PCM; cached as .npy',selectedWorkingSpeechTargetLufs=-18,humanWholeListeningAndPronunciation='pending',userFinalReview='pending')
V.write_json(target,d);print(json.dumps({k:d[k] for k in ['status','technicalExecutionComplete','flaggedVoiceTransferWindows','extractedUniqueFrames']}))
