from pathlib import Path
import unreal as u,json,traceback
p=Path("D:/Github/VideoEditing/projects/animation-facial-animations/production/local/series-v1/reference-pose.json")
try:
 m=u.load_asset("/Game/Characters/Paragon/Heroes/TwinBlast/Meshes/SKM_TwinBlast_ActionHero")
 modifier=u.SkeletonModifier();assert modifier.set_skeletal_mesh(m);component=u.SkeletalMeshComponent();component.set_skeletal_mesh(m)
 result={}
 for i in range(component.get_num_bones()):
  n=str(component.get_bone_name(i));t=modifier.get_bone_transform(n,False);g=modifier.get_bone_transform(n,True)
  def data(t):return {"p":list(t.translation.to_tuple()),"q":[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],"s":list(t.scale3d.to_tuple())}
  result[n]={"parent":str(component.get_parent_bone(n)),"local":data(t),"world":data(g)}
 p.write_text(json.dumps({"mesh":m.get_path_name(),"skeleton":m.skeleton.get_path_name(),"bones":result,"sourceModified":False}),encoding="utf-8")
except Exception:p.with_suffix(".error.txt").write_text(traceback.format_exc());raise
