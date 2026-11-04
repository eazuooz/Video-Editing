"""Build owned, editable Unreal A02 levels/sequences from checked pose data."""
from pathlib import Path
import json,traceback
import unreal as u

H=Path(__file__).resolve().parent;L=H.parent/'local/fighters-v3'
ASSET='/Game/YamyamA02/fighters_v3_final'
TOOLS=u.AssetToolsHelpers.get_asset_tools()
def owned(path):
    assert path.startswith(ASSET+'/');return path
def asset(name,folder,cls,factory):
    path=owned(ASSET+'/'+folder+'/'+name)
    return u.load_asset(path) or TOOLS.create_asset(name,ASSET+'/'+folder,cls,factory)
def material(name,rgb,unlit=False):
    m=asset(name,'Materials',u.Material,u.MaterialFactoryNew())
    u.MaterialEditingLibrary.delete_all_material_expressions(m)
    color=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector,0,0)
    color.constant=u.LinearColor(*rgb,1)
    if unlit:
        m.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
        prop=u.MaterialProperty.MP_EMISSIVE_COLOR
    else:prop=u.MaterialProperty.MP_BASE_COLOR
    u.MaterialEditingLibrary.connect_material_property(color,'',prop)
    u.MaterialEditingLibrary.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m,False)
    return m
def cube(name,position,scale,mat):
    a=u.EditorLevelLibrary.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*position))
    a.set_actor_label(name);a.set_actor_scale3d(u.Vector(*scale))
    c=a.static_mesh_component;c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'));c.set_material(0,mat)
    c.set_editor_property('cast_shadow',False)
    return a
def build_animation(row,data):
    name=data['id'].replace('-','_')+'_'+row['side']
    path=owned(ASSET+'/Animations/'+name)
    clip=u.load_asset(path)
    if clip is None:
        factory=u.AnimSequenceFactory();factory.target_skeleton=u.load_asset(data['skeleton'])
        clip=TOOLS.create_asset(name,ASSET+'/Animations',u.AnimSequence,factory)
    controller=clip.controller
    controller.open_bracket('A02 authored comparison',False)
    controller.set_frame_rate(u.FrameRate(60,1),False)
    # UE default compressed sampling is30Hz. Even animation length avoids a
    # half-frame endpoint assert; the sequence/render keeps its exact60Hz range.
    animation_frames=data['frames']+(data['frames']%2)
    controller.set_number_of_frames(u.FrameNumber(animation_frames),False)
    controller.remove_all_bone_tracks(False)
    for name,track in row['tracks'].items():
        controller.add_bone_curve(name,False)
        ps=list(track['p']);qs=list(track['q'])
        if len(ps)>1 and animation_frames>data['frames']:ps.append(ps[-1]);qs.append(qs[-1])
        pos=[u.Vector(*v) for v in ps];rot=[u.Quat(*q) for q in qs]
        scale=[u.Vector(*track['s']) for _ in pos]
        assert controller.set_bone_track_keys(name,pos,rot,scale,False),name
    controller.close_bracket(False)
    clip.set_editor_property('enable_root_motion',False)
    u.EditorAssetLibrary.save_loaded_asset(clip,False)
    return clip

def main():
    job=json.loads((L/'unreal/build-job.json').read_text())
    cid=job['id'];data=json.loads((L/'unreal/poses'/f'{cid}.json').read_text())
    safe=cid.replace('-','_');level=owned(ASSET+'/Levels/'+safe)
    u.EditorAssetLibrary.make_directory(ASSET+'/Levels')
    # Only the isolated worker's editor world is replaced.
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve()==(L/'unreal-worker').resolve()
    if u.EditorAssetLibrary.does_asset_exist(level):
        assert u.EditorLevelLibrary.load_level(level)
        for existing in u.EditorLevelLibrary.get_all_level_actors():
            if not isinstance(existing,(u.WorldSettings,u.Brush)):
                u.EditorLevelLibrary.destroy_actor(existing)
    else:
        assert u.EditorLevelLibrary.new_level(level)
    bg=material('M_Background',(.76,.77,.76),True)
    grid=material('M_Grid',(.56,.58,.57),True)
    major=material('M_GridMajor',(.38,.42,.40),True)
    floor=material('M_Floor',(.56,.57,.56),True)
    red=material('M_GroundLine',(.63,.08,.08),True)
    cube('Neutral grid backdrop',(0,-110,130),(12,.05,7),bg)
    cube('Ground',(0,0,-2),(12,8,.025),floor)
    for x in range(-400,401,20):cube('Grid vertical '+str(x),(x,-106,130),(.008 if x%100==0 else .0035,.02,7),major if x%100==0 else grid)
    for z in range(-200,401,20):cube('Grid horizontal '+str(z),(0,-105,z),(12,.02,.008 if z%100==0 else .0035),major if z%100==0 else grid)
    cube('Ground reference line',(0,-103,0),(12,.03,.7/100),red)
    light=u.EditorLevelLibrary.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,200,350),u.Rotator(pitch=-35,yaw=-65,roll=0))
    light.light_component.set_editor_property('intensity',4.0)
    fill=u.EditorLevelLibrary.spawn_actor_from_class(u.DirectionalLight,u.Vector(100,300,200),u.Rotator(pitch=-15,yaw=125,roll=0))
    fill.light_component.set_editor_property('intensity',1.5)
    fill.light_component.set_editor_property('cast_shadows',False)
    camera=u.EditorLevelLibrary.spawn_actor_from_class(u.CameraActor,u.Vector(0,900,85),u.Rotator(pitch=0,yaw=-90,roll=0))
    camera.set_actor_label('A02 fixed comparison camera')
    cc=camera.camera_component;cc.projection_mode=u.CameraProjectionMode.ORTHOGRAPHIC;cc.ortho_width=550.
    cc.set_auto_calculate_ortho_planes(False);cc.set_update_ortho_planes(False)
    cc.set_ortho_near_clip_plane(.1);cc.set_ortho_far_clip_plane(5000.)
    if job.get('perspective'):
        cc.projection_mode=u.CameraProjectionMode.PERSPECTIVE;cc.field_of_view=34.
    cc.aspect_ratio=16/9;cc.constrain_aspect_ratio=True
    pp=cc.post_process_settings
    pp.override_auto_exposure_method=True;pp.auto_exposure_method=u.AutoExposureMethod.AEM_MANUAL
    pp.override_auto_exposure_bias=True;pp.auto_exposure_bias=1.0
    pp.override_auto_exposure_apply_physical_camera_exposure=True;pp.auto_exposure_apply_physical_camera_exposure=False
    pp.override_motion_blur_amount=True;pp.motion_blur_amount=0.
    cc.post_process_settings=pp;cc.post_process_blend_weight=1.0
    seq=asset(safe,'Sequences',u.LevelSequence,u.LevelSequenceFactoryNew())
    seq.set_display_rate(u.FrameRate(60,1));seq.set_playback_start(0);seq.set_playback_end(data['frames'])
    for binding in seq.get_bindings():binding.remove()
    for track in seq.get_tracks():seq.remove_track(track)
    camera_binding=seq.add_possessable(camera)
    ct=seq.add_track(u.MovieSceneCameraCutTrack);cs=ct.add_section();cs.set_range(0,data['frames'])
    bid=u.MovieSceneObjectBindingID();bid.set_editor_property('guid',camera_binding.get_id());cs.set_camera_binding_id(bid)
    clips=[]
    for i,row in enumerate(data['animations']):
        clip=build_animation(row,data);clips.append(clip.get_path_name())
        actor=u.EditorLevelLibrary.spawn_actor_from_class(u.SkeletalMeshActor,u.Vector(-125 if i==0 else 125,0,0),u.Rotator(pitch=0,yaw=-60,roll=0))
        actor.set_actor_label('A02 '+row['side']+' mannequin')
        component=actor.skeletal_mesh_component
        component.set_skeletal_mesh(u.load_asset(data['mesh']))
        component.set_editor_property('animation_mode',u.AnimationMode.ANIMATION_SINGLE_NODE)
        component.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
        component.set_editor_property('bounds_scale',2.0)
        binding=seq.add_possessable(actor);cb=seq.add_possessable(component);cb.set_parent(binding)
        track=cb.add_track(u.MovieSceneSkeletalAnimationTrack);section=track.add_section();section.set_range(0,data['frames'])
        params=u.MovieSceneSkeletalAnimationParams();params.animation=clip;section.params=params
    u.EditorAssetLibrary.save_loaded_asset(seq,False)
    u.EditorLevelLibrary.save_current_level()
    config=asset(safe+'_Capture','Capture',u.MoviePipelinePrimaryConfig,u.MoviePipelinePrimaryConfigFactory())
    output=config.find_or_add_setting_by_class(u.MoviePipelineOutputSetting)
    output.output_directory=u.DirectoryPath(str(L/'unreal/renders'/job.get('renderFolder',cid)));output.output_resolution=u.IntPoint(1920,1080)
    output.use_custom_frame_rate=True;output.output_frame_rate=u.FrameRate(60,1)
    output.file_name_format='{frame_number}';output.zero_pad_frame_numbers=6
    output.override_existing_output=False
    config.find_or_add_setting_by_class(u.MoviePipelineDeferredPassBase)
    config.find_or_add_setting_by_class(u.MoviePipelineImageSequenceOutput_PNG)
    aa=config.find_or_add_setting_by_class(u.MoviePipelineAntiAliasingSetting)
    aa.spatial_sample_count=1;aa.temporal_sample_count=1;aa.engine_warm_up_count=16;aa.render_warm_up_count=8
    game=config.find_or_add_setting_by_class(u.MoviePipelineGameOverrideSetting)
    game.game_mode_override=u.MoviePipelineGameMode;game.cinematic_quality_settings=False
    u.EditorAssetLibrary.save_loaded_asset(config,False)
    result={'id':cid,'level':level,'sequence':seq.get_path_name(),'captureConfig':config.get_path_name(),
        'animationAssets':clips,'frames':data['frames'],'fps':60,'resolution':[1920,1080],
        'camera':{'type':'orthographic','widthCm':550,'positionCm':[0,900,85],'yaw':-90},
        'sourceMesh':data['mesh'],'sourceAnimation':data['sourcePose'],'sourceAssetsModified':False,'renderFolder':job.get('renderFolder',cid),
        'classification':'authored Unreal explanation','status':'assets-created-not-yet-render-reviewed'}
    (L/'unreal'/f'{cid}-build.json').write_text(json.dumps(result,indent=2)+'\n')
    u.log('A02_BUILD_OK '+cid)

try:main()
except Exception:
    (L/'unreal/build-stage-error.txt').write_text(traceback.format_exc());raise
