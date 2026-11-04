from pathlib import Path
import json,unreal as u
H=Path(__file__).resolve().parent;L=H.parent/'local/fighters-v3'
j=json.loads((L/'unreal/A02-prototype-build.json').read_text())
u.EditorLevelLibrary.load_level(j['level'])
out=[]
for a in u.EditorLevelLibrary.get_all_level_actors():
 if isinstance(a,(u.CameraActor,u.SkeletalMeshActor)) or a.get_actor_label()=='Neutral grid backdrop':
  r={'label':a.get_actor_label(),'location':str(a.get_actor_location()),'rotation':str(a.get_actor_rotation()),'hidden':a.get_editor_property('hidden')}
  if isinstance(a,u.CameraActor):
   c=a.camera_component;r.update(near=c.ortho_near_clip_plane,far=c.ortho_far_clip_plane,auto=c.auto_calculate_ortho_planes,forward=str(a.get_actor_forward_vector()),projection=str(c.projection_mode))
  out.append(r)
(L/'unreal/scene-inspection.json').write_text(json.dumps(out,indent=2))
