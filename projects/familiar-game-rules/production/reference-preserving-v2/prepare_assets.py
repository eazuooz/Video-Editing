"""Create source-linked stills from inspected independent gameplay only."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[4]
L=R/'projects/familiar-game-rules/production/local/reference-preserving-v2'
FF=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
O=L/'assets';O.mkdir(parents=True,exist_ok=True)
rows=[
 ('rage-reticle','media/rage2-combat.mp4',5,None,'FPS reticle and weapon'),
 ('apex-reticle','media/apex.mp4',59,None,'Aim and weapon response'),
 ('apex-team','media/apex.mp4',52,None,'Teammates and environment'),
 ('rage-controller','media-supplement/rage2-controller.mp4',7.5,None,'Actual Xbox ON GROUND DEFAULT; Move/Look/Aim/Fire'),
 ('sf6-remap','media-supplement/sf6-permitted-menu.mp4',5,'crop=1120:630:0:150','Permitted recorder; actual action mapping and Edit Control Mapping; face excluded'),
 ('tales-remap','media-supplement/tales-controls.mp4',14,None,'Actual keyboard action mapping'),
 ('acc-remap','media-supplement/acc-bindings.mp4',11,'crop=1600:1020:0:60','Actual action binding list; crop excludes presenter'),
 ('smash-walk','media-inputs/smash-running-sprinkles.mp4',.7,None,'Observed upright Mario movement; no measured stick input'),
 ('smash-run','media-inputs/smash-running-sprinkles.mp4',2.1,None,'Observed Mario run and foot dust; no measured stick input'),
 ('atomic-run','media-inputs/atomic-runner-kawaii-gameplay.mp4',12,None,'Actual jump and circular projectile in original4:3'),
]
records=[]
for name,source,t,crop,purpose in rows:
 f=L/source;p=O/(name+'.png');assert f.is_file(),f
 if not p.exists():
  args=[str(FF),'-v','error','-threads','2','-ss',str(t),'-i',str(f),'-frames:v','1']
  if crop:args+=['-vf',crop]
  subprocess.run([*args,str(p)],check=True)
 records.append(dict(id=name,sourceFile=f.relative_to(R).as_posix(),sourceSha256=hashlib.sha256(f.read_bytes()).hexdigest(),localSeconds=t,framePurpose=purpose,crop=crop or 'none',image=p.relative_to(R).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),directPixelReview='pending-native-and375px-layout',classification='explanation-still-from-independent-gameplay',sourceLessonUsed=False))
(O/'provenance.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared',len(records),'source-linked stills')
