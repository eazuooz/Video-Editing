// Read-only dependency inventory for already successful, hash-bound captures.
// Install into the owned capture project's Assets/Editor only after captures end.
// Does not build, open, save, reserialize, refresh, or export any scene.
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;
using UnityEditor;
using UnityEditor.PackageManager;

namespace Yamyam.TechTen.Archive {
 public static class TechTenDependencyManifest {
  const string Media="C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030";
  const string Owned=Media+"/unity-capture";
  const string SceneRoot="Assets/VideoScenes/tech-ten-shorts-20261030/";
  const string BuildSettingsPath="ProjectSettings/EditorBuildSettings.asset";
  const string BuildSettingsSha="746171162169ec7b3f70ac4a8c2fd7c3c94d982ff2cf1da6d10986fd56757a95";
  [Serializable] public class Job { public Entry[] captures; }
  [Serializable] public class Entry { public string slug,receiptPath,receiptSha256,inputPath,inputSha256,manifestPath; }
  [Serializable] public class Artifact { public string path,sha256; public long bytes; }
  [Serializable] public class Receipt { public bool success; public string topic,voiceSha256; public string[] savedScenes; public Artifact[] artifacts; }
  [Serializable] public class Input { public string voiceSha256,timingSha256,sourceTreeSha256; }
  [Serializable] public class Item { public string assetPath,physicalPath,kind,guid,sha256; public long bytes; }
  [Serializable] public class UnresolvedSettingsReference {
   public string assetPath,physicalPath,settingsSha256,key,guid,serializedLine,reason;
   public string scope="Only the seven receipt-bound Sample(seconds)/Camera.Render captures; not general Play Mode or player builds";
   public bool runtimeReopenVerified=false,playerBuildVerified=false;
  }
  [Serializable] public class Manifest {
   public int schemaVersion=1;
   public string slug,project,unityVersion,receiptPath,receiptSha256,inputPath,inputSha256,voiceSha256,sourceTreeSha256,sourceSnapshot;
   public string generatedAtUtc;
   public string method="AssetDatabase.GetDependencies(savedScenes, recursive:true); read-only file inventory";
   public string dependencyTiming="Scenes are receipt-bound. Dependency/meta/settings bytes are observed at export time; no missing capture-time hashes are invented.";
   public string sourceBinding="CPU copier must restore every sourceCode file from the input-bound immutable source snapshot, never from the current shared capture code.";
   public string[] savedScenes;
   public List<Item> files=new List<Item>();
   public List<UnresolvedSettingsReference> unresolvedSettingsReferences=new List<UnresolvedSettingsReference>();
  }
  static string Full(string p) { return Path.GetFullPath(p).Replace('\\','/').TrimEnd('/'); }
  static void Within(string path,string root) { var p=Full(path);var r=Full(root);if(!p.StartsWith(r+"/",StringComparison.OrdinalIgnoreCase))throw new IOException("Outside allowed root: "+path); }
  static string Hash(string p) { using(var s=SHA256.Create())using(var f=File.OpenRead(p))return BitConverter.ToString(s.ComputeHash(f)).Replace("-","").ToLowerInvariant(); }
  static void Verify(string p,string hash) { if(!File.Exists(p)||Hash(p)!=hash)throw new IOException("Hash differs: "+p); }
  public static void Run() {
   try {
    if(!string.Equals(Full(Path.GetDirectoryName(Application.dataPath)),Owned,StringComparison.OrdinalIgnoreCase))throw new IOException("Only the owned isolated capture project is allowed");
    var args=Environment.GetCommandLineArgs();int n=Array.IndexOf(args,"-techTenExportJob");
    if(n<0||n+1>=args.Length)throw new IOException("Explicit export job required");
    string path=Full(args[n+1]);Within(path,Media+"/native-export-tools/jobs");
    var job=JsonUtility.FromJson<Job>(File.ReadAllText(path));if(job.captures==null||job.captures.Length!=7)throw new IOException("Expected exactly seven native captures");
    if(job.captures.Select(x=>x.slug).Distinct().Count()!=7)throw new IOException("Duplicate capture slug");
    foreach(var e in job.captures)Write(e);
    Debug.Log("TECH_TEN_DEPENDENCY_MANIFESTS_COMPLETE");EditorApplication.Exit(0);
   } catch(Exception ex) { Debug.LogException(ex);EditorApplication.Exit(1); }
  }
  static void Write(Entry e) {
   Within(e.receiptPath,Media+"/"+e.slug+"/local/unity-capture");
   Within(e.inputPath,Media+"/"+e.slug+"/local/unity-capture");
   Within(e.manifestPath,Media+"/native-dependency-manifests");
   Verify(e.receiptPath,e.receiptSha256);Verify(e.inputPath,e.inputSha256);
   var r=JsonUtility.FromJson<Receipt>(File.ReadAllText(e.receiptPath));
   var input=JsonUtility.FromJson<Input>(File.ReadAllText(e.inputPath));
   if(!r.success||e.slug!="shorts-"+r.topic||string.IsNullOrWhiteSpace(r.voiceSha256)||r.voiceSha256!=input.voiceSha256)throw new IOException("Not a successful full capture");
   if(input.sourceTreeSha256==null||input.sourceTreeSha256.Length!=64)throw new IOException("Missing source snapshot binding");
   if(r.savedScenes==null||r.savedScenes.Length==0)throw new IOException("No receipt-listed scenes");
   var m=new Manifest {slug=e.slug,project=Owned,unityVersion=Application.unityVersion,receiptPath=Full(e.receiptPath),receiptSha256=e.receiptSha256,inputPath=Full(e.inputPath),inputSha256=e.inputSha256,voiceSha256=r.voiceSha256,sourceTreeSha256=input.sourceTreeSha256,sourceSnapshot=Media+"/native-source-snapshots/"+input.sourceTreeSha256,savedScenes=r.savedScenes,generatedAtUtc=DateTime.UtcNow.ToString("o")};
   var inventory=new SortedDictionary<string,Item>(StringComparer.Ordinal);
   foreach(string scene in r.savedScenes) {
    if(!scene.StartsWith(SceneRoot+"Scenes/"+r.topic+"/source-"+input.sourceTreeSha256.Substring(0,12)+"/",StringComparison.Ordinal)||!scene.EndsWith(".unity",StringComparison.Ordinal))throw new IOException("Unexpected scene path: "+scene);
    string absolute=Full(Path.Combine(Owned,scene));Within(absolute,Owned+"/Assets");
    var a=r.artifacts.Single(x=>string.Equals(Full(x.path),absolute,StringComparison.OrdinalIgnoreCase));Verify(absolute,a.sha256);
   }
   foreach(string dep in AssetDatabase.GetDependencies(r.savedScenes,true))AddAsset(dep,inventory);
   // MonoScript's AssetDatabase edge need not enumerate all C# partials. The CPU
   // copier later filters these against capture-time sourceCode and restores it.
   foreach(string code in Directory.EnumerateFiles(Path.Combine(Owned,SceneRoot),"*",SearchOption.AllDirectories)) {
    string ext=Path.GetExtension(code).ToLowerInvariant();
    if(new[]{".cs",".shader",".hlsl",".cginc",".asmdef",".asmref"}.Contains(ext))AddAsset(Full(code).Substring(Owned.Length+1),inventory);
   }
   if(inventory.Keys.Any(x=>x.StartsWith("Assets/ThirdParty/KayKitAdventurers/",StringComparison.Ordinal))) {
    foreach(string name in new[]{"LICENSE.txt","provenance.json"})AddAsset("Assets/ThirdParty/KayKitAdventurers/"+name,inventory);
   }
   foreach(string rel in new[]{"Packages/manifest.json","Packages/packages-lock.json"})AddFile(rel,Owned+"/"+rel,"package-lock","",inventory);
   var settingsRoots=new HashSet<string>(StringComparer.Ordinal);
   foreach(string settings in Directory.EnumerateFiles(Owned+"/ProjectSettings","*",SearchOption.TopDirectoryOnly)) {
    AddFile("ProjectSettings/"+Path.GetFileName(settings),settings,"project-settings","",inventory);
    // Graphics/quality settings can reference render-pipeline assets outside a
    // scene. Resolve their GUIDs too, otherwise a copied project could reopen
    // with missing settings dependencies despite a complete scene graph.
    foreach(System.Text.RegularExpressions.Match match in System.Text.RegularExpressions.Regex.Matches(File.ReadAllText(settings),@"guid:\s*([0-9a-f]{32})")) {
     string guid=match.Groups[1].Value;if(guid.StartsWith("0000000000000000",StringComparison.Ordinal))continue;
     string asset=AssetDatabase.GUIDToAssetPath(guid);
     if(string.IsNullOrEmpty(asset)) {
      var known=CaptureUnusedSetting(settings,guid,input.sourceTreeSha256);
      if(known==null)throw new IOException("Unresolved ProjectSettings GUID: "+guid);
      m.unresolvedSettingsReferences.Add(known);continue;
     }
     settingsRoots.Add(asset);
    }
   }
   if(settingsRoots.Count>0)foreach(string dep in AssetDatabase.GetDependencies(settingsRoots.ToArray(),true))AddAsset(dep,inventory);
   // This is not a general missing-GUID exemption. Preserve the exact default
   // settings bytes, record their three unresolved references, and fail if any
   // such GUID is referenced by an actual scene/render/source dependency.
   if(m.unresolvedSettingsReferences.Count>0) {
    if(m.unresolvedSettingsReferences.Count!=3||m.unresolvedSettingsReferences.Select(x=>x.guid).Distinct().Count()!=3)throw new IOException("Unexpected partial settings exception");
    foreach(var item in inventory.Values) {
     if(item.assetPath==BuildSettingsPath||string.IsNullOrEmpty(item.physicalPath))continue;
     if(!new[]{".unity",".prefab",".mat",".asset",".controller",".anim",".cs",".shader",".hlsl"}.Contains(Path.GetExtension(item.assetPath).ToLowerInvariant()))continue;
     string content=File.ReadAllText(item.physicalPath);
     if(m.unresolvedSettingsReferences.Any(x=>content.Contains(x.guid)))throw new IOException("Capture dependency uses unresolved settings GUID: "+item.assetPath);
    }
   }
   m.files=inventory.Values.ToList();
   Verify(e.receiptPath,e.receiptSha256);Verify(e.inputPath,e.inputSha256);
   Directory.CreateDirectory(Path.GetDirectoryName(e.manifestPath));
   using(var stream=new FileStream(e.manifestPath,FileMode.CreateNew,FileAccess.Write,FileShare.None))using(var writer=new StreamWriter(stream,new UTF8Encoding(false)))writer.Write(JsonUtility.ToJson(m,true)+"\n");
  }
  static UnresolvedSettingsReference CaptureUnusedSetting(string settings,string guid,string sourceTree) {
   if(Full(settings)!=Owned+"/"+BuildSettingsPath||Hash(settings)!=BuildSettingsSha)return null;
   if(sourceTree!="ae3b2fd85f8fad48b6e51fc20d5d673868c1aba8aaa5dad8fb81ac58e3f4a661"&&sourceTree!="f16754c26af604fd8a69414a83dcc5d5de968ba602d57e050bdef005a2401939")return null;
   string key,line,reason;
   if(guid=="99c9720ab356a0642a771bea13969a05") {
    key="m_Scenes[0].guid (Assets/Scenes/SampleScene.unity)";line="    guid: "+guid;
    reason="Pre-existing enabled SampleScene build-list entry is absent in the isolated capture project. The successful capture runner opens only receipt-listed scenes explicitly and does not run BuildPipeline.";
   }else if(guid=="1b1c20d82303e4b5781c3ef50ac1449f") {
    key="m_configObjects.com.unity.dt.app-ui";line="    com.unity.dt.app-ui: {fileID: 11400000, guid: "+guid+", type: 2}";
    reason="Pre-existing App UI config reference; App UI package is absent from this isolated project's manifest and lock. Receipt scenes and captured source have no App UI component or API use.";
   }else if(guid=="052faaac586de48259a63d0c4782560b") {
    key="m_configObjects.com.unity.input.settings.actions";line="    com.unity.input.settings.actions: {fileID: -944628639613478452, guid: "+guid+", type: 3}";
    reason="Pre-existing project-wide InputActionAsset/player-build preload reference is unresolved. Selected captures use explicit Sample(seconds), not PlayerInput/InputSystem actions or builds. This exception does not certify input, Play Mode, or player-build validity.";
   }else return null;
   if(File.ReadAllLines(settings).Count(x=>x==line)!=1)return null;
   foreach(string packages in new[]{Owned+"/Packages/manifest.json",Owned+"/Packages/packages-lock.json"})if(File.ReadAllText(packages).Contains("\"com.unity.dt.app-ui\""))throw new IOException("App UI package changed; settings exception requires renewed analysis");
   return new UnresolvedSettingsReference {assetPath=BuildSettingsPath,physicalPath=Full(settings),settingsSha256=BuildSettingsSha,key=key,guid=guid,serializedLine=line,reason=reason};
  }
  static void AddAsset(string p,SortedDictionary<string,Item> all) {
   p=p.Replace('\\','/');if(p.Contains(".."))throw new IOException("Unsafe asset path");
   if(p.StartsWith("Assets/",StringComparison.Ordinal)) {
    string physical=Owned+"/"+p;Within(physical,Owned+"/Assets");
    if(!File.Exists(physical))throw new IOException("Missing dependency: "+p);
    AddFile(p,physical,"asset",AssetDatabase.AssetPathToGUID(p),all);
    AddFile(p+".meta",physical+".meta","meta",AssetDatabase.AssetPathToGUID(p),all);
    string dir=Path.GetDirectoryName(p).Replace('\\','/');
    while(dir!="Assets"&&dir.StartsWith("Assets/",StringComparison.Ordinal)) {
     if(File.Exists(Owned+"/"+dir+".meta"))AddFile(dir+".meta",Owned+"/"+dir+".meta","folder-meta",AssetDatabase.AssetPathToGUID(dir),all);
     dir=Path.GetDirectoryName(dir).Replace('\\','/');
    }
   } else if(p.StartsWith("Packages/",StringComparison.Ordinal)) {
    var info=UnityEditor.PackageManager.PackageInfo.FindForAssetPath(p);if(info==null)throw new IOException("Unresolved package dependency: "+p);
    string prefix="Packages/"+info.name+"/";if(!p.StartsWith(prefix,StringComparison.Ordinal))throw new IOException("Package prefix mismatch");
    string physical=Path.Combine(info.resolvedPath,p.Substring(prefix.Length));Within(physical,info.resolvedPath);
    AddFile(p,physical,"package-reference",AssetDatabase.AssetPathToGUID(p),all);
    if(File.Exists(physical+".meta"))AddFile(p+".meta",physical+".meta","package-meta-reference",AssetDatabase.AssetPathToGUID(p),all);
   } else {
    if(!p.StartsWith("Resources/",StringComparison.Ordinal)&&!p.StartsWith("Library/",StringComparison.Ordinal))throw new IOException("Unknown external dependency: "+p);
    all[p]=new Item{assetPath=p,physicalPath="",kind="unity-built-in-reference",guid=AssetDatabase.AssetPathToGUID(p),sha256="",bytes=0};
   }
  }
  static void AddFile(string logical,string physical,string kind,string guid,SortedDictionary<string,Item> all) {
   physical=Full(physical);if(!File.Exists(physical))throw new IOException("Missing required file: "+physical);
   all[logical]=new Item{assetPath=logical,physicalPath=physical,kind=kind,guid=guid,sha256=Hash(physical),bytes=new FileInfo(physical).Length};
  }
 }
}
