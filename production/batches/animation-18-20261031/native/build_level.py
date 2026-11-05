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
def build(key):
 d=json.loads((L/'poses'/f'{key}.json').read_text('utf-8'));level=f'{asset_root}/Levels/{key}';u.EditorAssetLibrary.make_directory(asset_root+'/Levels')
 if not u.EditorAssetLibrary.does_asset_exist(level):
  assert u.EditorAssetLibrary.duplicate_asset('/Game/YamyamA01/assigning_v2/Levels/walk',level)
 assert u.EditorLevelLibrary.load_level(level);camera=None
 for actor in u.EditorLevelLibrary.get_all_level_actors():
  if isinstance(actor,u.CameraActor):camera=actor
  if isinstance(actor,u.SkeletalMeshActor):u.EditorLevelLibrary.destroy_actor(actor)
 assert camera
 if d.get('cameraView')=='top':
  camera.set_actor_location(u.Vector(0,35,720),False,False)
  camera.set_actor_rotation(u.Rotator(pitch=-88,yaw=-90,roll=0),False)
 if d.get('cameraView')=='perspective':
  camera.set_actor_location(u.Vector(0,790,85),False,False)
  camera.camera_component.projection_mode=u.CameraProjectionMode.PERSPECTIVE
  camera.camera_component.field_of_view=34.
 seq=owned('Sequences',key,u.LevelSequence,u.LevelSequenceFactoryNew());seq.set_display_rate(u.FrameRate(60,1));seq.set_playback_start(0);seq.set_playback_end(d['frames'])
 for binding in seq.get_bindings():binding.remove()
 for track in seq.get_tracks():seq.remove_track(track)
 cb=seq.add_possessable(camera);cuts=seq.add_track(u.MovieSceneCameraCutTrack);cs=cuts.add_section();cs.set_range(0,d['frames'])
 bid=u.MovieSceneObjectBindingID();bid.set_editor_property('guid',cb.get_id());cs.set_camera_binding_id(bid)
 clips=[]
 for i,row in enumerate(d['animations']):
  clip=animation(key,row,d);clips.append(clip.get_path_name())
  a=u.EditorLevelLibrary.spawn_actor_from_class(u.SkeletalMeshActor,u.Vector(-125 if i==0 else 125,0,0),u.Rotator(pitch=0,yaw=d.get('yaw',-73),roll=0));a.set_actor_label(f'{key}_{row["side"]}')
  mesh=a.skeletal_mesh_component;mesh.set_skeletal_mesh(u.load_asset(job['mesh']))
  mesh.set_editor_property('animation_mode',u.AnimationMode.ANIMATION_SINGLE_NODE)
  mesh.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES);mesh.set_editor_property('bounds_scale',2)
  parent=seq.add_possessable(a);child=seq.add_possessable(mesh);child.set_parent(parent);track=child.add_track(u.MovieSceneSkeletalAnimationTrack);section=track.add_section();section.set_range(0,d['frames'])
  params=u.MovieSceneSkeletalAnimationParams();params.animation=clip;section.params=params
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
