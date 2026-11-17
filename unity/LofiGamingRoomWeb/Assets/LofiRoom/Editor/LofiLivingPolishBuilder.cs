using System;
using System.IO;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using Unity.Pipeline.Commands;
using Yamyam.LofiRoom;
public static class LofiLivingPolishBuilder
{
    const string Scene="Assets/LofiRoom/Scenes/LofiLivingRoomV9.unity";
    static string Delivery=>Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/living-room-v9");
    [CliCommand("lofi_polish_prepare","Preserve v8 and create the selected contact/coat revision",MainThreadRequired=true)]
    public static string Prepare(){if(EditorApplication.isPlaying)throw new Exception("Edit mode required");EditorSceneManager.OpenScene("Assets/LofiRoom/Scenes/LofiLivingRoomV8.unity");var r=UnityEngine.Object.FindAnyObjectByType<LofiRoomSample>();r.actor.transform.SetPositionAndRotation(new Vector3(.65f,r.actor.transform.position.y,-1.95f),Quaternion.Euler(0,145,0));EditorSceneManager.SaveScene(r.gameObject.scene,Scene);AssetDatabase.SaveAssets();return Scene;}
    [CliCommand("lofi_polish_web_build","Build only the selected v9 scene",MainThreadRequired=true)]
    public static string Build(){if(EditorApplication.isPlaying)throw new Exception("Edit mode required");Directory.CreateDirectory(Delivery);var dst=Delivery+"/webgl";EditorApplication.delayCall+=()=>{PlayerSettings.WebGL.compressionFormat=WebGLCompressionFormat.Gzip;PlayerSettings.WebGL.decompressionFallback=true;PlayerSettings.WebGL.nameFilesAsHashes=false;var b=BuildPipeline.BuildPlayer(new[]{Scene},dst,BuildTarget.WebGL,BuildOptions.None);File.WriteAllText(Delivery+"/web-build.json",Newtonsoft.Json.JsonConvert.SerializeObject(new{result=b.summary.result.ToString(),errors=b.summary.totalErrors,bytes=b.summary.totalSize},Newtonsoft.Json.Formatting.Indented));};return dst;}
}
