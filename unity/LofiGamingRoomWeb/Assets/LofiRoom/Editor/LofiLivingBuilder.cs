using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using Unity.Pipeline.Commands;
using Yamyam.LofiRoom;

public static class LofiLivingBuilder
{
    const string Folder="Assets/LofiRoom/GeneratedLivingV8";
    const string Scene="Assets/LofiRoom/Scenes/LofiLivingRoomV8.unity";
    static string Delivery=>Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/living-room-v8");
    [CliCommand("lofi_living_prepare","Prepare only the selected enhanced living room, keeping the prior scene",MainThreadRequired=true)]
    public static string Prepare()
    {
        if(EditorApplication.isPlaying)throw new Exception("Stop Play before scene preparation");
        Directory.CreateDirectory(Folder);AssetDatabase.Refresh();
        EditorSceneManager.OpenScene("Assets/LofiRoom/Scenes/LofiFinalRoom.unity");
        var room=UnityEngine.Object.FindAnyObjectByType<LofiRoomSample>();
        var old=AssetDatabase.GetAssetPath(room.actor.runtimeAnimatorController);string path=Folder+"/LivingController.controller";
        if(!AssetDatabase.LoadAssetAtPath<AnimatorController>(path))AssetDatabase.CopyAsset(old,path);
        var ac=AssetDatabase.LoadAssetAtPath<AnimatorController>(path);room.actor.runtimeAnimatorController=ac;
        var layer=ac.layers[0];layer.iKPass=true;ac.layers=new[]{layer};
        var clips=AssetDatabase.LoadAllAssetsAtPath("Assets/LofiRoom/NativeMotion/Rig_Medium_Simulation.fbx").OfType<AnimationClip>().ToArray();
        foreach(var pair in new[]{("LoungeDown","Lie_Down"),("LoungeIdle","Lie_Idle"),("LoungeUp","Lie_StandUp")})
        {
            var state=layer.stateMachine.states.Select(x=>x.state).FirstOrDefault(x=>x.name==pair.Item1)??layer.stateMachine.AddState(pair.Item1);
            state.motion=clips.First(x=>x.name==pair.Item2);state.speed=pair.Item1=="LoungeIdle"?1:.46f;state.iKOnFeet=false;
        }
        var living=room.gameObject.AddComponent<LofiLivingRoom>();living.room=room;living.lieDuration=clips.First(x=>x.name=="Lie_Down").length/.46f;living.getUpDuration=clips.First(x=>x.name=="Lie_StandUp").length/.46f;
        var rain=AssetDatabase.LoadAssetAtPath<Material>(Folder+"/WindowRain.mat");if(!rain){rain=new Material(Shader.Find("Yamyam/Window Rain"));AssetDatabase.CreateAsset(rain,Folder+"/WindowRain.mat");}living.rainTemplate=rain;
        var playlist=room.gameObject.AddComponent<LofiPlaylist>();playlist.source=room.music;
        playlist.tracks=AssetDatabase.FindAssets("t:AudioClip",new[]{"Assets/LofiRoom/PlaylistV8"}).Select(AssetDatabase.GUIDToAssetPath).OrderBy(x=>x).Select(AssetDatabase.LoadAssetAtPath<AudioClip>).ToArray();
        playlist.titles=new[]{"Morning Coffee","Glad To Be Stuck Inside","Laundry On The Wire","A Little Shade","Keeping Cool","Come Again","Windows Down","Waves","Something In the Air","Everything You Ever Dreamed"};
        if(playlist.tracks.Length!=10)throw new Exception("Expected ten complete licensed tracks");
        foreach(var track in playlist.tracks){var importer=(AudioImporter)AssetImporter.GetAtPath(AssetDatabase.GetAssetPath(track));var settings=importer.defaultSampleSettings;settings.loadType=AudioClipLoadType.CompressedInMemory;settings.compressionFormat=AudioCompressionFormat.Vorbis;settings.quality=.6f;settings.preloadAudioData=false;importer.defaultSampleSettings=settings;importer.SaveAndReimport();}
        EditorUtility.SetDirty(ac);EditorSceneManager.SaveScene(room.gameObject.scene,Scene);AssetDatabase.SaveAssets();
        EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(Scene,true)};
        var report=new{scene=Scene,lieDuration=living.lieDuration,getUpDuration=living.getUpDuration,tracks=playlist.tracks.Select(x=>new{x.name,x.length}).ToArray()};Directory.CreateDirectory(Delivery);File.WriteAllText(Delivery+"/prepared.json",Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented));return Scene;
    }
    [CliCommand("lofi_living_web_build","Build enhanced living room WebGL into a new delivery directory",MainThreadRequired=true)]
    public static string BuildWeb()
    {
        if(EditorApplication.isPlaying)throw new Exception("Stop Play before build");
        var dest=Delivery+"/webgl";Directory.CreateDirectory(dest);
        EditorApplication.delayCall+=()=>{PlayerSettings.WebGL.compressionFormat=WebGLCompressionFormat.Gzip;PlayerSettings.WebGL.decompressionFallback=true;PlayerSettings.WebGL.nameFilesAsHashes=false;var r=BuildPipeline.BuildPlayer(new[]{Scene},dest,BuildTarget.WebGL,BuildOptions.None);File.WriteAllText(Delivery+"/web-build.json",Newtonsoft.Json.JsonConvert.SerializeObject(new{result=r.summary.result.ToString(),errors=r.summary.totalErrors,bytes=r.summary.totalSize},Newtonsoft.Json.Formatting.Indented));};return dest;
    }
}
