"""Build editable copies of genuine clip studies without writing vendor content."""
from pathlib import Path
import json,traceback
import unreal as u
H=Path(__file__).resolve().parent;L=H.parent/'local/real-clips-v2'
assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve()==(L/'unreal-worker').resolve()
ROOT='/Game/YamyamRealClipsV2';T=u.AssetToolsHelpers.get_asset_tools()
def owned(folder,name,kind,factory):
    path=ROOT+'/'+folder+'/'+name;u.EditorAssetLibrary.make_directory(ROOT+'/'+folder)
    return u.load_asset(path) or T.create_asset(name,ROOT+'/'+folder,kind,factory)
def animation(key,d,row):
    factory=u.AnimSequenceFactory();factory.target_skeleton=u.load_asset(row.get('skeleton',d['skeleton']))
    clip=owned(d['episode']+'/Animations',key,u.AnimSequence,factory)
    con=clip.controller;con.open_bracket('Source-derived animation, original clip preserved',False)
    con.set_frame_rate(u.FrameRate(60,1),False);con.set_number_of_frames(u.FrameNumber(d['frames']),False);con.remove_all_bone_tracks(False)
    for bone,track in row['tracks'].items():
        con.add_bone_curve(bone,False)
        values={k:list(track[k]) for k in ('p','q','s')}
        for k in values:
            if len(values[k])==d['frames']:values[k].append(values[k][-1])
        assert con.set_bone_track_keys(bone,[u.Vector(*v) for v in values['p']],[u.Quat(*q) for q in values['q']],[u.Vector(*v) for v in values['s']],False),bone
    con.close_bracket(False);clip.set_editor_property('enable_root_motion',False);u.EditorAssetLibrary.save_loaded_asset(clip,False)
    return clip
def weapon(mesh,d):
    axis=u.Vector(*d['weaponAxisInHand']);rotation=u.MathLibrary.make_rot_from_z(axis)
    # Independently authored blade, guard and grip; no vendor mesh is changed.
    for part,z,scale in [('blade',48,[.045,.11,.85]),('guard',4,[.06,.29,.04]),('grip',-9,[.05,.05,.20])]:
        a=u.EditorLevelLibrary.spawn_actor_from_class(u.StaticMeshActor,u.Vector(),u.Rotator())
        a.set_actor_label('Study weapon '+part);c=a.static_mesh_component;c.set_mobility(u.ComponentMobility.MOVABLE)
        c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
        rule=u.AttachmentRule.SNAP_TO_TARGET;a.attach_to_component(mesh,'hand_r',rule,rule,rule,False)
        a.set_actor_relative_location(axis*z,False,False);a.set_actor_relative_rotation(rotation,False,False)
        a.set_actor_relative_scale3d(u.Vector(*scale))
def build(job):
    key=job['key'];d=json.loads(Path(job['file']).read_text('utf-8'));folder=d['episode']
    level=ROOT+'/'+folder+'/Levels/'+key;u.EditorAssetLibrary.make_directory(ROOT+'/'+folder+'/Levels')
    if not u.EditorAssetLibrary.does_asset_exist(level):assert u.EditorAssetLibrary.duplicate_asset('/Game/YamyamA01/assigning_v2/Levels/walk',level)
    assert u.EditorLevelLibrary.load_level(level);camera=None
    for a in u.EditorLevelLibrary.get_all_level_actors():
        if isinstance(a,u.CameraActor):camera=a
        if isinstance(a,u.SkeletalMeshActor) or a.get_actor_label().startswith(('Study weapon ','Study target ')):u.EditorLevelLibrary.destroy_actor(a)
    assert camera;camera.set_actor_location(u.Vector(0,900,d.get('cameraHeight',100)),False,False)
    camera.camera_component.ortho_width=d.get('cameraWidth',500)
    seq=owned(folder+'/Sequences',key,u.LevelSequence,u.LevelSequenceFactoryNew())
    seq.set_display_rate(u.FrameRate(60,1));seq.set_playback_start(0);seq.set_playback_end(d['frames'])
    for b in seq.get_bindings():b.remove()
    for t in seq.get_tracks():seq.remove_track(t)
    cb=seq.add_possessable(camera);cut=seq.add_track(u.MovieSceneCameraCutTrack).add_section();cut.set_range(0,d['frames'])
    bid=u.MovieSceneObjectBindingID();bid.set_editor_property('guid',cb.get_id());cut.set_camera_binding_id(bid)
    rows=d.get('animations',[dict(tracks=d['tracks'])] if 'tracks' in d else [])
    for i,row in enumerate(rows):
        clip=animation(key+'_'+str(i),d,row);xyz=row.get('location',[0,0,0]);yaw=row.get('yaw',d.get('yaw',-65))
        a=u.EditorLevelLibrary.spawn_actor_from_class(u.SkeletalMeshActor,u.Vector(*xyz),u.Rotator(pitch=0,yaw=yaw,roll=0))
        a.set_actor_label('Genuine motion '+key+' '+str(i));c=a.skeletal_mesh_component;c.set_skeletal_mesh(u.load_asset(row.get('mesh',d['mesh'])))
        c.set_editor_property('animation_mode',u.AnimationMode.ANIMATION_SINGLE_NODE)
        c.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES);c.set_editor_property('bounds_scale',4.)
        parent=seq.add_possessable(a);child=seq.add_possessable(c);child.set_parent(parent)
        section=child.add_track(u.MovieSceneSkeletalAnimationTrack).add_section();section.set_range(0,d['frames'])
        params=u.MovieSceneSkeletalAnimationParams();params.animation=clip;section.params=params
        if d.get('weapon'):weapon(c,d)
    if 'targetLocation' in d:
        target=u.EditorLevelLibrary.spawn_actor_from_class(u.SkeletalMeshActor,u.Vector(*d['targetLocation']),u.Rotator(pitch=0,yaw=110,roll=0))
        target.set_actor_label('Study target mannequin');component=target.skeletal_mesh_component
        component.set_skeletal_mesh(u.load_asset(d['mesh']));component.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE)
        component.set_animation(u.load_asset(d['sourceClip']));component.set_position(0,False)
        # A separate target mesh is held still; contact is computed from the sampled blade capsule.
    u.EditorAssetLibrary.save_loaded_asset(seq,False);u.EditorLevelLibrary.save_current_level()
    cfg=owned(folder+'/Capture',key,u.MoviePipelinePrimaryConfig,u.MoviePipelinePrimaryConfigFactory())
    out=cfg.find_or_add_setting_by_class(u.MoviePipelineOutputSetting);out.output_directory=u.DirectoryPath(str(L/'study-frames'/key));out.output_resolution=u.IntPoint(1920,1080)
    out.use_custom_frame_rate=True;out.output_frame_rate=u.FrameRate(60,1);out.file_name_format='{frame_number}';out.zero_pad_frame_numbers=6;out.override_existing_output=True
    cfg.find_or_add_setting_by_class(u.MoviePipelineDeferredPassBase);cfg.find_or_add_setting_by_class(u.MoviePipelineImageSequenceOutput_PNG)
    aa=cfg.find_or_add_setting_by_class(u.MoviePipelineAntiAliasingSetting);aa.engine_warm_up_count=16;aa.temporal_sample_count=1;aa.spatial_sample_count=1
    game=cfg.find_or_add_setting_by_class(u.MoviePipelineGameOverrideSetting);game.game_mode_override=u.MoviePipelineGameMode;game.cinematic_quality_settings=False
    u.EditorAssetLibrary.save_loaded_asset(cfg,False)
    return dict(key=key,level=level,sequence=seq.get_path_name(),config=cfg.get_path_name(),frames=d['frames'])
try:
    result=[build(job) for job in json.loads((L/'study-build-request.json').read_text('utf-8'))]
    (L/'study-builds.json').write_text(json.dumps(result,indent=2),'utf-8')
    queue=u.MoviePipelineQueue()
    for row in result:
        job=queue.allocate_new_job(u.MoviePipelineExecutorJob);job.job_name=row['key']
        job.map=u.SoftObjectPath(row['level']);job.sequence=u.SoftObjectPath(row['sequence']);job.set_configuration(u.load_asset(row['config']))
    saved,manifest=u.MoviePipelineEditorLibrary.save_queue_to_manifest_file(queue)
    (L/'study-queue.json').write_text(json.dumps(dict(queue=manifest,jobs=result),indent=2),'utf-8')
except Exception:
    (L/'study-build-error.txt').write_text(traceback.format_exc(),'utf-8');raise
