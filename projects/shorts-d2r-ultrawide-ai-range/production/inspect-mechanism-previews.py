"""Inspect finite three-second silent previews; never mark final/audio QA complete."""
from pathlib import Path
import json,subprocess,shutil
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
ITEMS=[('shorts-d2r-ultrawide-ai-range','shorts-d2r-ultrawide-ai-range-preview-300-1792895286071.mp4'),('shorts-d2r-loot-grass-clearance','shorts-d2r-loot-grass-clearance-preview-725-1792895290775.mp4'),('shorts-d2-modular-sprite-equipment','shorts-d2-modular-sprite-equipment-preview-709-1792895297822.mp4')]
for slug,name in ITEMS:
 p=ROOT/'projects'/slug/'production/local/mechanism-preview';p.mkdir(parents=True,exist_ok=True)
 source=ROOT/'shared/output/motion-canvas'/name
 shutil.copy2(source,p/'silent-3s.mp4')
 subprocess.run(['ffmpeg','-v','error','-n','-i',str(source),'-vf','fps=2','-frames:v','6',str(p/'frame-%02d.png')],check=True)
 sheet=Image.new('RGB',(1125,1394),'#202020');d=ImageDraw.Draw(sheet)
 for i,f in enumerate(sorted(p.glob('frame-*.png'))):
  im=Image.open(f);im.thumbnail((375,667));x=i%3*375;y=i//3*697
  sheet.paste(im,(x,y));d.text((x+8,y+670),f'preview {i*.5:.1f}s / no audio / draft timing',fill='white')
 sheet.save(p/'mobile-contact-sheet.jpg',quality=94)
 (p/'scope.json').write_text(json.dumps({'kind':'silent-mechanism-preview','durationSeconds':3,'nativeDimensions':[1080,1920],'mobileDimensions':[375,667],'frameSamplingFps':2,'actualFinalAudioCaptionsPresent':False,'actualViewed':False},indent=2),encoding='utf8')
 print(slug)
