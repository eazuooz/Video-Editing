"""Extract real room frames and preserve per-shot source provenance for the making-of."""
from pathlib import Path
import json,subprocess,hashlib,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local/full-video-v1';A=L/'assets';A.mkdir(parents=True,exist_ok=True)
shots={
 'room':('web-final-v6',1),'sit':('web-final-v6',9.7),'desk':('web-final-v6',14),'window':('web-final-v6',22),'day':('web-final-v6',29),'hair':('web-final-v6',35),
 'read':('hearth-v4',28),'fire':('hearth-v4',44),'record':('hearth-v4',53),'old':('unity-sample-v1',17),'walk':('nature-v2',3),
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
 source=P/'production/local/web-final-v6'/source
 if source.exists():shutil.copy2(source,A/(name+'.jpg'))
demo=P/'production/local/web-final-v6/web-memo-demo.jpg'
if demo.exists():shutil.copy2(demo,A/'webMemo.jpg')
for name in ('model','animation'):
 source=P/'production/local/web-final-v6'/('tripo-'+name+'-source.jpg')
 if source.exists():
  # Exclude unrelated asset thumbnails/account chrome; preserve the actual work UI.
  run=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(source),'-vf','crop=1648:1016:0:60','-frames:v','1',str(A/('tripo-'+name+'.png'))]
  subprocess.run(run,check=True)
print('Prepared',len(records),'actual captured frames')
