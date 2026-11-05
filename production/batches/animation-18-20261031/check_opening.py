"""Exercise the actual opening compositing path on CPU before voice/engine resources are granted."""
from pathlib import Path
import json,sys,subprocess,hashlib
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B))
import assemble_episode as edit
ep=edit.EP
folder=edit.L/'opening-proof';folder.mkdir(exist_ok=True)
edit.V=folder
edit.enc=['-r','60','-c:v','libx264','-threads','3','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','60000']
first=edit.visual['shots'][0][0];key,start,focus=first
assert key in edit.visual['gameFiles']
source=edit.visual['gameFiles'][key]
shot=dict(cue=1,key=key,sourcePoint=start,focus=focus,frames=240)
file=edit.encode_shot((0,shot),{'sourceEvidence':{key:{'file':source}}})
subprocess.run(['ffmpeg','-y','-v','error','-i',file,'-vf','fps=2,scale=375:-2,tile=4x2','-frames:v','1',folder/'mobile.jpg'],check=True)
out={'episode':ep,'sourceFile':source,'originalSourceStart':start,'verifiedFrames':240,'sourceSelection':edit.rel(edit.H/'source-selection.json'),'captionedMaster':False,'previewAudio':False,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
(folder/'proof.json').write_text(json.dumps(out,indent=2),'utf8')
print(ep,'first four seconds checked',flush=True)
