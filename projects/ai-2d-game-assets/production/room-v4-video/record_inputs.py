from pathlib import Path
import json,hashlib
from PIL import Image
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v4-video'
rows=[]
for f in (L/'browser-evidence').iterdir():
 if f.suffix.lower() not in ['.png','.jpg']:continue
 with Image.open(f) as im:rows.append({'name':f.name,'path':str(f),'sha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest(),'dimensions':list(im.size),'actualFormat':im.format,'kind':'actual-public-browser-still','rootObserved':'Public v6 writing, memo save and radio controls; prior user memo restored and playback stopped.','fhdVideoClaim':False,'usedInVideo':f.name in ['radio-playing-fhd.png','radio-playlist-native.jpg','memo-saved-native.jpg']})
(H/'browser-evidence.json').write_text(json.dumps({'source':'root CUA actual screenshots of deployed site v6','records':rows,'presentation':'Screenshot explanation plus editorial zoom, separate from continuous native1920x1080 Canvas game capture.','noScreenRecordingClaim':True},ensure_ascii=False,indent=2),'utf8')
text=(H.parent/'room-v3/caption_layout.cjs').read_text('utf8').replace('../local/room-v3','../local/room-v4-video');(H/'caption_layout.cjs').write_text(text,'utf8')
print('Recorded',len(rows),'browser stills')
