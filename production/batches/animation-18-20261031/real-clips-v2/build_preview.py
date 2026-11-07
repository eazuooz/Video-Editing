"""Create read-only-source animation audition plates in an owned Unreal namespace."""
from pathlib import Path
import json, math, traceback
import unreal as u

H=Path(__file__).resolve().parent
L=H.parent/'local/real-clips-v2'
assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve()==(L/'unreal-worker').resolve()
ROOT='/Game/YamyamRealClipsV2/Audition'
T=u.AssetToolsHelpers.get_asset_tools()

def asset(folder,name,kind,factory):
    path=ROOT+'/'+folder+'/'+name
    u.EditorAssetLibrary.make_directory(ROOT+'/'+folder)
    return u.load_asset(path) or T.create_asset(name,ROOT+'/'+folder,kind,factory)

def main():
    request=json.loads((L/'audition-request.json').read_text('utf-8'))
    key=request['id']; frames=request.get('frames',480)
    level=ROOT+'/Levels/'+key
    u.EditorAssetLibrary.make_directory(ROOT+'/Levels')
    if not u.EditorAssetLibrary.does_asset_exist(level):
        assert u.EditorAssetLibrary.duplicate_asset('/Game/YamyamA01/assigning_v2/Levels/walk',level)
    assert u.EditorLevelLibrary.load_level(level)
    camera=None
    for actor in u.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor,u.SkeletalMeshActor):u.EditorLevelLibrary.destroy_actor(actor)
        elif isinstance(actor,u.CameraActor):camera=actor
    assert camera
    camera.set_actor_location(u.Vector(0,900,165),False,False)
    camera.camera_component.ortho_width=780.
    seq=asset('Sequences',key,u.LevelSequence,u.LevelSequenceFactoryNew())
    seq.set_display_rate(u.FrameRate(60,1));seq.set_playback_start(0);seq.set_playback_end(frames)
    for b in seq.get_bindings():b.remove()
    for t in seq.get_tracks():seq.remove_track(t)
    cb=seq.add_possessable(camera);cut=seq.add_track(u.MovieSceneCameraCutTrack).add_section();cut.set_range(0,frames)
    bid=u.MovieSceneObjectBindingID();bid.set_editor_property('guid',cb.get_id());cut.set_camera_binding_id(bid)
    selected=[]
    for i,row in enumerate(request['clips']):
        source=u.load_asset(row['clip']); mesh=u.load_asset(row['mesh'])
        assert isinstance(source,u.AnimSequence) and isinstance(mesh,u.SkeletalMesh)
        assert source.get_editor_property('skeleton')==mesh.get_editor_property('skeleton')
        target=ROOT+'/Animations/'+key+'_'+str(i)
        u.EditorAssetLibrary.make_directory(ROOT+'/Animations')
        clip=u.load_asset(target) or u.EditorAssetLibrary.duplicate_asset(row['clip'],target)
        clip.set_editor_property('enable_root_motion',False);clip.set_editor_property('force_root_lock',True)
        clip.set_editor_property('root_motion_root_lock',u.RootMotionRootLock.ANIM_FIRST_FRAME)
        u.EditorAssetLibrary.save_loaded_asset(clip,False)
        pos=row.get('position',[-190 if i%2==0 else 190,0,195 if i<2 else -20])
        a=u.EditorLevelLibrary.spawn_actor_from_class(u.SkeletalMeshActor,u.Vector(*pos),u.Rotator(pitch=0,yaw=row.get('yaw',-65),roll=0))
        a.set_actor_label(row['label']);c=a.skeletal_mesh_component;c.set_skeletal_mesh(mesh)
        c.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
        c.set_editor_property('bounds_scale',3.)
        bind=seq.add_possessable(a);bc=seq.add_possessable(c);bc.set_parent(bind)
        section=bc.add_track(u.MovieSceneSkeletalAnimationTrack).add_section();section.set_range(0,frames)
        params=u.MovieSceneSkeletalAnimationParams();params.animation=clip;section.params=params
        selected.append(dict(row,seconds=source.get_play_length()))
    u.EditorAssetLibrary.save_loaded_asset(seq,False);u.EditorLevelLibrary.save_current_level()
    cfg=asset('Capture',key,u.MoviePipelinePrimaryConfig,u.MoviePipelinePrimaryConfigFactory())
    out=cfg.find_or_add_setting_by_class(u.MoviePipelineOutputSetting)
    out.output_directory=u.DirectoryPath(str(L/'audition-frames'/key));out.output_resolution=u.IntPoint(1920,1080)
    out.use_custom_frame_rate=True;out.output_frame_rate=u.FrameRate(60,1);out.file_name_format='{frame_number}';out.zero_pad_frame_numbers=6
    cfg.find_or_add_setting_by_class(u.MoviePipelineDeferredPassBase)
    cfg.find_or_add_setting_by_class(u.MoviePipelineImageSequenceOutput_PNG)
    aa=cfg.find_or_add_setting_by_class(u.MoviePipelineAntiAliasingSetting);aa.engine_warm_up_count=16;aa.temporal_sample_count=1;aa.spatial_sample_count=1
    game=cfg.find_or_add_setting_by_class(u.MoviePipelineGameOverrideSetting);game.game_mode_override=u.MoviePipelineGameMode;game.cinematic_quality_settings=False
    u.EditorAssetLibrary.save_loaded_asset(cfg,False)
    (L/(key+'-audition.json')).write_text(json.dumps(dict(level=level,sequence=seq.get_path_name(),config=cfg.get_path_name(),frames=frames,clips=selected),indent=2),'utf-8')
try:main()
except Exception:
    (L/'audition-error.txt').write_text(traceback.format_exc(),'utf-8');raise
