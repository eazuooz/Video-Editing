"""Extract real room frames and preserve per-shot source provenance for the making-of."""
from pathlib import Path
import json,subprocess,hashlib,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local/full-video-v4';A=L/'assets';A.mkdir(parents=True,exist_ok=True)
shots={
 'room':('living-room-v10',2),'sit':('living-room-v10',40),'desk':('living-room-v10',40),'window':('living-room-v10',57),'day':('living-room-v10',70),'hair':('web-final-v6',35),
 'read':('living-room-v10',16),'fire':('final-activities-v7',29),'record':('living-room-v10',65),'old':('unity-sample-v1',17),'walk':('living-room-v10/walk-source',2),'cat':('living-room-v10',49),'coding':('living-room-v10',40),'rain':('living-room-v10',57),
}
records=[]
for name,(folder,second) in shots.items():
 source=P/'production/local'/folder/'unity-native-clean.mp4';assert source.exists(),source
 out=A/(name+'.png')
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(second),'-i',str(source),'-frames:v','1',str(out)],check=True)
 records.append({'name':name,'source':source.relative_to(R).as_posix(),'second':second,'sourceSha256':hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),'frameSha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),'rights':'Own room capture; original Tripo generated models, licensed rendered character motion. No raw model redistribution.'})
for name,source in {'concept':P/'assets/concept-room-v1.png','hero':P/'assets/hero-reference-v1.png','headphones':P/'assets/headphones-reference-v1.png','memo':P/'production/local/garden-v5/native-memo-reopened.jpg'}.items():
 if source.exists():shutil.copy2(source,A/(name+source.suffix))
textures=R/'unity/LofiGamingRoomWeb/Assets/LofiRoom/TexturesNatureV2/hero'
if textures.exists():
 for f in textures.glob('*.png'):
  shutil.copy2(f,A/('hero-'+f.name))
(L/'source-frames.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n','utf-8')
for name,source in {'webMemo':'web-memo-restored.jpg','webTimer':'web-timer-restored.jpg','webRoom':'web-room.jpg'}.items():
 source=P/'production/local/living-room-v10'/source
 if source.exists():shutil.copy2(source,A/(name+'.jpg'))
demo=P/'production/local/living-room-v10/web-memo-demo.jpg'
if demo.exists():shutil.copy2(demo,A/'webMemo.jpg')
pixel=R/'projects/ai-2d-game-assets/production/local/room-v4-video/browser-evidence/radio-playing-fhd.png'
assert pixel.exists();shutil.copy2(pixel,A/'pixelRoom.png')
from PIL import Image
records.append({'name':'pixelRoom','source':pixel.relative_to(R).as_posix(),'sourceSha256':hashlib.file_digest(pixel.open('rb'),'sha256').hexdigest(),'decodedDimensions':list(Image.open(pixel).size),'kind':'own previous 2D game still illustration, not moving footage','rights':'Own previous game screenshot; historical 2D-to-3D comparison.'})
(L/'source-frames.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n','utf-8')
for name in ('model','animation'):
 source=P/'production/local/web-final-v6'/('tripo-'+name+'-source.jpg')
 if source.exists():
  # Exclude unrelated asset thumbnails/account chrome; preserve the actual work UI.
  run=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(source),'-vf','crop=1648:1016:0:60','-frames:v','1',str(A/('tripo-'+name+'.png'))]
  subprocess.run(run,check=True)
print('Prepared',len(records),'actual captured frames')

# Own paid Tripo cat job UI; exclude unrelated asset sidebar/account chrome.
from PIL import Image
cat=P/"production/local/living-room-v10/tripo-cat-ready.jpg"
if cat.exists():
 image=Image.open(cat);image.crop((0,60,min(1648,image.width),min(1076,image.height))).save(A/"tripo-cat.png")
for key,source in [('cat-photo',P/'assets/references/sleeping-calico-cc0-original.jpg'),('cat-input',P/'assets/references/sleeping-calico-tripo-input-v1.png')]:
 shutil.copy2(source,A/(key+source.suffix))
