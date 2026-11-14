"""UE commandlet. Bind vendor AnimSequence assets directly, without bone-track edits."""
from pathlib import Path
import json
import math
import unreal as u

PROJECT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve()
JOB = json.loads((PROJECT / 'native-job.json').read_text(encoding='utf-8'))
OUT = Path(JOB['work'])
ASSET_ROOT = '/Game/YamyamNativeClipsV6'
TOOLS = u.AssetToolsHelpers.get_asset_tools()


def owned(folder, name, kind, factory):
    directory = ASSET_ROOT + '/' + folder
    u.EditorAssetLibrary.make_directory(directory)
    return u.load_asset(directory + '/' + name) or TOOLS.create_asset(name, directory, kind, factory)


def build(row):
    key = row['id']
    clip = u.load_asset(row['clip'])
    mesh = u.load_asset(row['mesh'])
    assert isinstance(clip, u.AnimSequence) and isinstance(mesh, u.SkeletalMesh), key
    assert clip.get_editor_property('skeleton') == mesh.get_editor_property('skeleton'), key
    frames = max(60, math.ceil(clip.get_play_length() * 60))
    level = ASSET_ROOT + '/Levels/' + key
    u.EditorAssetLibrary.make_directory(ASSET_ROOT + '/Levels')
    if not u.EditorAssetLibrary.does_asset_exist(level):
        assert u.EditorAssetLibrary.duplicate_asset('/Game/YamyamA01/assigning_v2/Levels/walk', level)
    assert u.EditorLevelLibrary.load_level(level)
    camera = None
    for actor in u.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, u.SkeletalMeshActor):
            u.EditorLevelLibrary.destroy_actor(actor)
        elif isinstance(actor, u.CameraActor):
            camera = actor
    assert camera
    camera.set_actor_location(u.Vector(0, 900, 100), False, False)
    camera.camera_component.ortho_width = 580
    sequence = owned('Sequences', key, u.LevelSequence, u.LevelSequenceFactoryNew())
    sequence.set_display_rate(u.FrameRate(60, 1))
    sequence.set_playback_start(0)
    sequence.set_playback_end(frames)
    for binding in sequence.get_bindings():
        binding.remove()
    for track in sequence.get_tracks():
        sequence.remove_track(track)
    camera_binding = sequence.add_possessable(camera)
    cut = sequence.add_track(u.MovieSceneCameraCutTrack).add_section()
    cut.set_range(0, frames)
    binding_id = u.MovieSceneObjectBindingID()
    binding_id.set_editor_property('guid', camera_binding.get_id())
    cut.set_camera_binding_id(binding_id)
    for side, yaw in enumerate(row.get('yaws', [-70, -25])):
        actor = u.EditorLevelLibrary.spawn_actor_from_class(
            u.SkeletalMeshActor, u.Vector(-145 if side == 0 else 145, 0, 0), u.Rotator(0, yaw, 0))
        actor.set_actor_label(key + ('_left' if side == 0 else '_right'))
        component = actor.skeletal_mesh_component
        component.set_skeletal_mesh(mesh)
        component.set_editor_property('visibility_based_anim_tick_option',
                                      u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
        component.set_editor_property('bounds_scale', 3.0)
        actor_binding = sequence.add_possessable(actor)
        component_binding = sequence.add_possessable(component)
        component_binding.set_parent(actor_binding)
        section = component_binding.add_track(u.MovieSceneSkeletalAnimationTrack).add_section()
        section.set_range(0, frames)
        params = u.MovieSceneSkeletalAnimationParams()
        params.animation = clip
        section.params = params
    u.EditorAssetLibrary.save_loaded_asset(sequence, False)
    u.EditorLevelLibrary.save_current_level()
    config = owned('Capture', key, u.MoviePipelinePrimaryConfig, u.MoviePipelinePrimaryConfigFactory())
    output = config.find_or_add_setting_by_class(u.MoviePipelineOutputSetting)
    output.output_directory = u.DirectoryPath(str(OUT / 'frames' / key))
    output.output_resolution = u.IntPoint(1920, 1080)
    output.use_custom_frame_rate = True
    output.output_frame_rate = u.FrameRate(60, 1)
    output.file_name_format = '{frame_number}'
    output.zero_pad_frame_numbers = 6
    config.find_or_add_setting_by_class(u.MoviePipelineDeferredPassBase)
    config.find_or_add_setting_by_class(u.MoviePipelineImageSequenceOutput_PNG)
    aa = config.find_or_add_setting_by_class(u.MoviePipelineAntiAliasingSetting)
    aa.engine_warm_up_count = 8
    aa.temporal_sample_count = 1
    aa.spatial_sample_count = 1
    game = config.find_or_add_setting_by_class(u.MoviePipelineGameOverrideSetting)
    game.game_mode_override = u.MoviePipelineGameMode
    game.cinematic_quality_settings = False
    u.EditorAssetLibrary.save_loaded_asset(config, False)
    result = dict(row, frames=frames, seconds=clip.get_play_length(), level=level,
                  sequence=sequence.get_path_name(), config=config.get_path_name(),
                  sourceSkeleton=clip.get_editor_property('skeleton').get_path_name(),
                  originalSequenceBoundDirectly=True, boneTracksEdited=False)
    (OUT / (key + '-build.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    u.log('NATIVE_CLIP_V6_READY ' + key)


for entry in JOB['clips']:
    build(entry)
