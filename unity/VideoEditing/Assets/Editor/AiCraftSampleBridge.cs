using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

// File requests are confined to this sample; no unrelated scene is closed or saved.
[InitializeOnLoad]
public static class AiCraftSampleBridge
{
    public static readonly string Repo = Path.GetFullPath(Path.Combine(Application.dataPath, "../../.."));
    public static readonly string Output = Path.Combine(Repo, "shared/output/ai-game-development-human-craft/unity-sample");
    static string Request => Path.Combine(Application.dataPath, "../Library/AiCraftSample.request");
    static AiCraftSampleBridge() { EditorApplication.update += Poll; }
    static void Poll()
    {
        if (EditorApplication.isCompiling || EditorApplication.isUpdating || !File.Exists(Request)) return;
        var command = File.ReadAllText(Request).Trim();
        var builder = typeof(AiCraftSampleBridge).Assembly.GetType("AiCraftSampleBuilder");
        if(command != "probe" && builder == null) return;
        File.Delete(Request);
        Directory.CreateDirectory(Output);
        try
        {
            File.WriteAllText(Path.Combine(Output,"error.txt"), "");
            if (command == "probe") Probe();
            else if (command == "preflight" || command == "render")
                builder.GetMethod("Run").Invoke(null, new object[] { command });
            else throw new Exception("Unknown sample request: " + command);
        }
        catch (Exception e) { File.WriteAllText(Path.Combine(Output, "error.txt"), e.ToString()); Debug.LogException(e); }
    }
    static void Probe()
    {
        const string path = "Assets/ThirdParty/KayKitAdventurers/Knight.fbx";
        var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
        if (!prefab) throw new Exception("Knight has not imported");
        var clips = AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__"));
        var result = "UNITY " + Application.unityVersion + "\n";
        result += string.Join("\n", clips.Select(c => $"CLIP {c.name} | {c.length} seconds | {c.frameRate} fps"));
        result += "\nTRANSFORMS\n" + string.Join("\n", prefab.GetComponentsInChildren<Transform>(true).Select(t => t.name));
        result += "\nRENDERERS\n" + string.Join("\n", prefab.GetComponentsInChildren<Renderer>(true).Select(r => $"{r.name} bounds {r.bounds} materials {string.Join(",",r.sharedMaterials.Select(m => m ? m.name : "null"))}"));
        File.WriteAllText(Path.Combine(Output, "asset-probe.txt"), result);
    }
}
