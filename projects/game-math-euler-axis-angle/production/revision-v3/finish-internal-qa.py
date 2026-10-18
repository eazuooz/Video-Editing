"""Finite selected-video QA after its already-running final encode; no next video."""
from pathlib import Path
import json, subprocess, sys, time, hashlib
R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v3'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def selected():assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
deadline=time.time()+3600
while not (O/'pair-source.json').exists():
 selected();assert time.time()<deadline,'Current render did not finish within the finite QA wait'
 time.sleep(3)
selected();pair=read(O/'pair-source.json');assert pair['inputs']['timelineSha256']==sha(H/'timeline.json')
print('Current pair finished; beginning full decode, PTS, audio and changed-pixel extraction.',flush=True)
subprocess.run([sys.executable,'-X','utf8',str(H/'verify-output.py'),'all'],cwd=R,check=True)
selected();video=O/'euler-captioned.mp4';digest=sha(video);assert pair['outputs']['captioned']['sha256']==digest
audio=O/'encoded-audio.wav';receipt=O/'encoded-audio-source.json';sig=dict(videoSha256=digest,rate=16000,channels=1,format='pcm_s16le')
if receipt.exists():
 previous=read(receipt);assert previous['inputs']==sig and previous['audioSha256']==sha(audio),'Inspect changed encoded-audio provenance'
else:
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(audio)],cwd=R,check=True)
 receipt.write_text(json.dumps(dict(inputs=sig,audioSha256=sha(audio)),indent=2)+'\n',encoding='utf-8')
print('Encoded media integrity and pixel extraction complete; beginning one bounded final-mix ASR.',flush=True)
subprocess.run([sys.executable,'-X','utf8',str(H/'review-final-audio.py'),'--device','cuda:0'],cwd=R,check=True)
print('Finite internal QA jobs complete. Direct pixels, whole ASR text and subjective-listening states still require explicit review.',flush=True)
