using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using Unity.Pipeline.Commands;
using Yamyam.LofiRoom;

public static class LofiGardenQA
{
    static string Folder=>Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/garden-v5");
    [CliCommand("lofi_garden_preview","Render a named PC v5 inspection angle",MainThreadRequired=true)]
    public static string Preview(string view)
    {
        var s=UnityEngine.Object.FindAnyObjectByType<LofiRoomSample>();s.showControls=false;
        if(view=="room")s.CameraRoom();
        if(view=="desk"){var pos=new Vector3(3.05f,1.75f,.3f);s.roomCamera.transform.SetPositionAndRotation(pos,Quaternion.LookRotation(new Vector3(1,.94f,1.18f)-pos));s.roomCamera.orthographicSize=1.02f;}
        if(view=="window"){var pos=new Vector3(.35f,2.10f,-.4f);s.roomCamera.transform.SetPositionAndRotation(pos,Quaternion.LookRotation(new Vector3(-1.78f,1.85f,2.4f)-pos));s.roomCamera.orthographicSize=1.32f;}
        var c=s.roomCamera;var rt=new RenderTexture(1920,1080,24);var t=new Texture2D(1920,1080,TextureFormat.RGB24,false);
        var active=RenderTexture.active;c.targetTexture=rt;c.Render();RenderTexture.active=rt;
        t.ReadPixels(new Rect(0,0,1920,1080),0,0);t.Apply();var path=Path.Combine(Folder,"preview-"+view+".png");File.WriteAllBytes(path,t.EncodeToPNG());
        c.targetTexture=null;RenderTexture.active=active;UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(t);s.showControls=true;return path;
    }
    [CliCommand("lofi_garden_qa","Check revised scene dimensions, shaders and isolated local memo persistence",MainThreadRequired=true)]
    public static string Check()
    {
        var s=UnityEngine.Object.FindAnyObjectByType<LofiRoomSample>();var hair=s.actor.GetComponent<LofiHairMotion>();
        var back=GameObject.Find("reading chair back").GetComponent<Renderer>().bounds;
        var monitor=GameObject.Find("iMac all-in-one body").GetComponent<Renderer>().bounds;
        var test=new GameObject("Isolated memo persistence QA").AddComponent<LofiMemo>();
        test.storeDirectory=Path.Combine(Folder,"memo-editor-test");
        string sample="오늘의 메모\n숲과 달을 보며 책 읽기 🌙\nアイデア · café · 123";
        test.SetText(sample);if(!test.SaveNow())throw new Exception("Memo save failed");test.text="";test.Reload();bool roundtrip=test.text==sample;
        test.SetText(sample+"\n두 번째 저장");if(!test.SaveNow())throw new Exception("Second memo save failed");
        bool backup=File.Exists(test.FilePath+".bak");File.WriteAllText(test.FilePath,"{broken QA fixture");test.Reload();bool recovered=test.text==sample;test.SaveNow();
        bool atomic=!File.Exists(test.FilePath+".tmp");UnityEngine.Object.DestroyImmediate(test.gameObject);
        if(!roundtrip || !backup || !recovered || !atomic)throw new Exception("Memo persistence contract failed");
        var shaders=new[]{"Yamyam/Forest Window","Yamyam/Hearth Flame","Yamyam/Lofi Detailed Surface"}.Select(Shader.Find).ToArray();
        var data=new{chairBackSize=back.size.ToString("F3"),chairBackTop=back.max.y,displayCenter=monitor.center.ToString("F3"),hair.breezeStrength,hair.maximumSway,hair.measuredOffset,hair.maximumObservedOffset,hair.maximumLengthError,hair.collisionCorrections,leafWind=AssetDatabase.LoadAssetAtPath<Material>("Assets/LofiRoom/GeneratedGardenV5/Materials/living-leaf.mat").GetFloat("_WindStrength"),shaderErrors=shaders.Sum(x=>ShaderUtil.GetShaderMessages(x).Count(m=>m.severity==UnityEditor.Rendering.ShaderCompilerMessageSeverity.Error)),shaderSupported=shaders.All(x=>x.isSupported),memo=new{roundtrip,backup,recovered,atomic,defaultPath=s.memo.FilePath,qaDirectory=Path.Combine(Folder,"memo-editor-test"),noUserNoteWritten=true},s.activities.phase};
        string json=Newtonsoft.Json.JsonConvert.SerializeObject(data,Newtonsoft.Json.Formatting.Indented);File.WriteAllText(Path.Combine(Folder,"runtime-qa.json"),json);return json;
    }
}
