"""Unreal commandlet: create only the selected series-owned level, sequence and animation tracks."""
from pathlib import Path
import os,json,traceback
import unreal as u
project=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve()
job=json.loads((project/'build-job.json').read_text(encoding='utf-8'))
L=Path(job['local']).resolve()
assert project==L/'unreal-worker'
asset_root='/Game/YamyamAnimationSeries/'+job['episode']
tools=u.AssetToolsHelpers.get_asset_tools()
def owned(folder,name,kind,factory):
 path=f'{asset_root}/{folder}/{name}'
 u.EditorAssetLibrary.make_directory(f'{asset_root}/{folder}')
 return u.load_asset(path) or tools.create_asset(name,asset_root+'/'+folder,kind,factory)
def animation(key,row,data):
 clip=owned('Animations',key+'_'+row['side'],u.AnimSequence,factory())
 con=clip.controller;con.open_bracket('Yamyam authored animation study',False)
 con.set_frame_rate(u.FrameRate(60,1),False);con.set_number_of_frames(u.FrameNumber(data['frames']),False);con.remove_all_bone_tracks(False)
 for bone,values in row['tracks'].items():
  points,quats=values['p'],values['q']
  con.add_bone_curve(bone,False)
  assert con.set_bone_track_keys(bone,[u.Vector(*v) for v in points],[u.Quat(*q) for q in quats],[u.Vector(*values['s']) for _ in points],False),bone
 con.close_bracket(False);clip.set_editor_property('enable_root_motion',False);u.EditorAssetLibrary.save_loaded_asset(clip,False);return clip
def factory():
 f=u.AnimSequenceFactory();f.target_skeleton=u.load_asset(job['skeleton']);return f
def expose_portrait_eyes(mesh):
 # Glasses and shirt share one material. Keep the shirt below the neck and the original face/eye materials.
 slot=mesh.get_material_index('M00_UpperBody');assert slot>=0
 path=asset_root+'/Materials/PortraitShirt'
 material=u.load_asset(path)
 if not material:
  u.EditorAssetLibrary.make_directory(asset_root+'/Materials')
  material=u.EditorAssetLibrary.duplicate_asset(mesh.get_material(slot).get_path_name().split('.')[0],path)
  assert material
  material.set_editor_property('blend_mode',u.BlendMode.BLEND_MASKED)
  graph=u.MaterialEditingLibrary
  create=lambda kind,x,y:graph.create_material_expression(material,kind,x,y)
  world=create(u.MaterialExpressionWorldPosition,-1300,900)
  origin=create(u.MaterialExpressionActorPositionWS,-1300,1040)
  relative=create(u.MaterialExpressionSubtract,-1080,930)
  component=create(u.MaterialExpressionComponentMask,-860,930)
  for channel in 'rgba':component.set_editor_property(channel,channel=='b')
  cutoff=create(u.MaterialExpressionConstant,-860,1090);cutoff.set_editor_property('r',163.)
  visible=create(u.MaterialExpressionSubtract,-640,980)
  for src,dest,pin in ((world,relative,'A'),(origin,relative,'B'),(relative,component,''),(cutoff,visible,'A'),(component,visible,'B')):
   assert graph.connect_material_expressions(src,'',dest,pin)
  assert graph.connect_material_property(visible,'',u.MaterialProperty.MP_OPACITY_MASK)
  graph.recompile_material(material);u.EditorAssetLibrary.save_loaded_asset(material,False)
 if material.get_editor_property('use_material_attributes'):
  # The vendor cloth is a material-attributes graph. Its bundle otherwise overrides a separate opacity input.
  graph=u.MaterialEditingLibrary;props=u.MaterialProperty
  bundle=graph.get_material_property_input_node(material,props.MP_MATERIAL_ATTRIBUTES)
  assert bundle
  split=graph.create_material_expression(material,u.MaterialExpressionBreakMaterialAttributes,-380,430)
  assert graph.connect_material_expressions(bundle,'',split,'')
  material.set_editor_property('use_material_attributes',False)
  for output,prop in (('BaseColor','MP_BASE_COLOR'),('Metallic','MP_METALLIC'),('Specular','MP_SPECULAR'),
                      ('Roughness','MP_ROUGHNESS'),('Normal','MP_NORMAL'),('AmbientOcclusion','MP_AMBIENT_OCCLUSION')):
   assert graph.connect_material_property(split,output,getattr(props,prop))
  graph.recompile_material(material);u.EditorAssetLibrary.save_loaded_asset(material,False)
 mesh.set_material(slot,material)
def build(key):
 d=json.loads((L/'poses'/f'{key}.json').read_text('utf-8'));level=f'{asset_root}/Levels/{key}';u.EditorAssetLibrary.make_directory(asset_root+'/Levels')
 if not u.EditorAssetLibrary.does_asset_exist(level):
  assert u.EditorAssetLibrary.duplicate_asset('/Game/YamyamA01/assigning_v2/Levels/walk',level)
 assert u.EditorLevelLibrary.load_level(level);camera=None
 for actor in u.EditorLevelLibrary.get_all_level_actors():
  if isinstance(actor,u.CameraActor):camera=actor
  if isinstance(actor,u.SkeletalMeshActor):u.EditorLevelLibrary.destroy_actor(actor)
  elif actor.get_actor_label().startswith(('Held handle ','Ground correction slope','Hurt volume')):u.EditorLevelLibrary.destroy_actor(actor)
 assert camera
 if 'cameraDistance' in d:
  camera.set_actor_location(u.Vector(0,d['cameraDistance'],d.get('cameraHeight',85)),False,False)
  camera.camera_component.projection_mode=u.CameraProjectionMode.PERSPECTIVE
  camera.camera_component.field_of_view=d.get('fov',34.)
 if 'cameraWidth' in d:
  camera.camera_component.ortho_width=d['cameraWidth']
  camera.set_actor_location(u.Vector(0,900,d.get('cameraHeight',85)),False,False)
 if d.get('cameraView')=='top':
  camera.set_actor_location(u.Vector(0,35,720),False,False)
  camera.set_actor_rotation(u.Rotator(pitch=-88,yaw=-90,roll=0),False)
 if d.get('cameraView')=='perspective':
  camera.set_actor_location(u.Vector(0,790,85),False,False)
  camera.camera_component.projection_mode=u.CameraProjectionMode.PERSPECTIVE
  camera.camera_component.field_of_view=34.
 if 'rampPitch' in d:
  for x in (-125,125):
   ramp=u.EditorLevelLibrary.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,0,3),u.Rotator(pitch=d['rampPitch'],yaw=0,roll=0))
   ramp.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
   ramp.set_actor_scale3d(u.Vector(1.55,1.05,.04));ramp.set_actor_label('Ground correction slope')
 for xyz in d.get('sphereTargets',[]):
  target=u.EditorLevelLibrary.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*xyz),u.Rotator())
  target.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Sphere'));target.set_actor_scale3d(u.Vector(*([d['targetRadius']*.02]*3)));target.set_actor_label('Hurt volume')
 seq=owned('Sequences',key,u.LevelSequence,u.LevelSequenceFactoryNew());seq.set_display_rate(u.FrameRate(60,1));seq.set_playback_start(0);seq.set_playback_end(d['frames'])
 for binding in seq.get_bindings():binding.remove()
 for track in seq.get_tracks():seq.remove_track(track)
 cb=seq.add_possessable(camera);cuts=seq.add_track(u.MovieSceneCameraCutTrack);cs=cuts.add_section();cs.set_range(0,d['frames'])
 bid=u.MovieSceneObjectBindingID();bid.set_editor_property('guid',cb.get_id());cs.set_camera_binding_id(bid)
 clips=[]
 for i,row in enumerate(d['animations']):
  clip=animation(key,row,d);clips.append(clip.get_path_name())
  offset=d.get('actorSpacing',125)*(-1 if i==0 else 1)+d.get('shiftX',0)
  xyz=d.get('actorLocations',[[offset,0,0],[offset,0,0]])[i]
  yaw=d.get('sideYaws',[d.get('yaw',-73)]*2)[i]
  a=u.EditorLevelLibrary.spawn_actor_from_class(u.SkeletalMeshActor,u.Vector(*xyz),u.Rotator(pitch=0,yaw=yaw,roll=0));a.set_actor_label(f'{key}_{row["side"]}')
  mesh=a.skeletal_mesh_component;mesh.set_skeletal_mesh(u.load_asset(job['mesh']))
  if d.get('exposeEyes'):
   expose_portrait_eyes(mesh)
   # These comparisons isolate facial/hand controls. Keep the coat skinned so cloth warm-up cannot obscure them.
   mesh.set_editor_property('disable_cloth_simulation',True)
  mesh.set_editor_property('animation_mode',u.AnimationMode.ANIMATION_SINGLE_NODE)
  mesh.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES);mesh.set_editor_property('bounds_scale',2)
  parent=seq.add_possessable(a);child=seq.add_possessable(mesh);child.set_parent(parent);track=child.add_track(u.MovieSceneSkeletalAnimationTrack);section=track.add_section();section.set_range(0,d['frames'])
  params=u.MovieSceneSkeletalAnimationParams();params.animation=clip;section.params=params
  if 'handSockets' in d:
   handle=u.EditorLevelLibrary.spawn_actor_from_class(u.StaticMeshActor,u.Vector(),u.Rotator())
   component=handle.static_mesh_component;component.set_mobility(u.ComponentMobility.MOVABLE)
   component.set_static_mesh(u.load_asset('/Engine/BasicShapes/'+d.get('handShape','Cylinder')));handle.set_actor_label('Held handle '+row['side'])
   rule=u.AttachmentRule.SNAP_TO_TARGET
   handle.attach_to_component(mesh,d['handSockets'][i],rule,rule,rule,False)
   handle.set_actor_relative_location(u.Vector(*d.get('handOffset',[0,0,0])),False,False)
   handle.set_actor_relative_scale3d(u.Vector(*d.get('handScale',[.07,.07,.36])))
 u.EditorAssetLibrary.save_loaded_asset(seq,False);u.EditorLevelLibrary.save_current_level()
 cfg=owned('Capture',key+'_Capture',u.MoviePipelinePrimaryConfig,u.MoviePipelinePrimaryConfigFactory());output=cfg.find_or_add_setting_by_class(u.MoviePipelineOutputSetting);output.output_directory=u.DirectoryPath(str(L/'frames'/key));output.output_resolution=u.IntPoint(1920,1080)
 output.use_custom_frame_rate=True;output.output_frame_rate=u.FrameRate(60,1);output.file_name_format='{frame_number}';output.zero_pad_frame_numbers=6;output.override_existing_output=True
 cfg.find_or_add_setting_by_class(u.MoviePipelineDeferredPassBase);cfg.find_or_add_setting_by_class(u.MoviePipelineImageSequenceOutput_PNG)
 aa=cfg.find_or_add_setting_by_class(u.MoviePipelineAntiAliasingSetting);aa.temporal_sample_count=1;aa.spatial_sample_count=1;aa.engine_warm_up_count=16
 g=cfg.find_or_add_setting_by_class(u.MoviePipelineGameOverrideSetting);g.game_mode_override=u.MoviePipelineGameMode;g.cinematic_quality_settings=False;u.EditorAssetLibrary.save_loaded_asset(cfg,False)
 (L/f'{key}-build.json').write_text(json.dumps(dict(level=level,sequence=seq.get_path_name(),config=cfg.get_path_name(),animations=clips,frames=d['frames'],width=1920,height=1080,fps=60,engine='5.8',sample=job['mesh']),indent=2),encoding='utf-8')
try:
 for k in job['keys']:build(k)
except Exception:
 (L/'stage-error.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
