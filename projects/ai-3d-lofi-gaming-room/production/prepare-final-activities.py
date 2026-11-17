"""Record the final room, preserving every prior capture and first full master."""
from pathlib import Path
import json,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[1];runtime=R/'unity/LofiGamingRoomWeb/Assets/LofiRoom/Runtime';L=P/'production/local'
src=(runtime/'LofiHearthCapture.cs').read_text('utf-8').replace('LofiHearthCapture','LofiFilmCapture').replace('Frames=4320','Frames=2400').replace('local/hearth-v4','local/final-activities-v7').replace('lofi_hearth_record','lofi_film_record')
start=src.index('                if(frame==300)');end=src.index('                yield return null;',start)
src=src[:start]+'''                if(frame==0)s.activities.Request("computer");
                if(frame==480){Vector3 p=new(3.05f,1.75f,.30f);s.roomCamera.transform.SetPositionAndRotation(p,Quaternion.LookRotation(new Vector3(1,.94f,1.18f)-p));s.roomCamera.orthographicSize=1.02f;}
                if(frame==600)s.activities.Request("read");
                if(frame==720){Vector3 p=new(3.1f,1.8f,.5f);s.roomCamera.transform.SetPositionAndRotation(p,Quaternion.LookRotation(new Vector3(1,1.0f,1.05f)-p));s.roomCamera.orthographicSize=.86f;}
                if(frame==1260){s.CameraRoom();s.activities.Request("idle");}
                if(frame==1560){Vector3 p=new(-.55f,1.15f,-1.3f);s.roomCamera.transform.SetPositionAndRotation(p,Quaternion.LookRotation(new Vector3(-2.80f,.75f,.30f)-p));s.roomCamera.orthographicSize=1.02f;}
                if(frame==1980){Vector3 p=new(-.25f,1.4f,.35f);s.roomCamera.transform.SetPositionAndRotation(p,Quaternion.LookRotation(new Vector3(-1.8f,.77f,1.86f)-p));s.roomCamera.orthographicSize=.66f;}
'''+src[end:]
(runtime/'LofiFilmCapture.cs').write_text(src,'utf-8')
prior=L/'full-video-v1/prior-before-final-activities';prior.mkdir(parents=True,exist_ok=True)
for f in (L/'full-video-v1/final').glob('*'):
 if f.is_file() and f.suffix in ('.mp4','.srt','.png') and not (prior/f.name).exists():shutil.copy2(f,prior/f.name)
for name in ('full-video-delivery.json','full-video-qa.json','companion-frames.json'):
 if not (prior/name).exists():shutil.copy2(P/'production'/name,prior/name)
(L/'final-activities-v7').mkdir(exist_ok=True)
j=json.loads((P/'project.json').read_text('utf-8'));j.update(status='latest-room-footage-reconciliation',productionComplete=False);(P/'project.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Prepared 40-second final-scene capture; previous master and frame mapping preserved')
