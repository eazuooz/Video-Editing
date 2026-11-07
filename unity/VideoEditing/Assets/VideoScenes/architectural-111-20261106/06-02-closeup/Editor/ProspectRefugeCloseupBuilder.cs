using System;
using System.IO;
using System.Text;
using System.Reflection;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
namespace Yamyam.Architectural111.ProspectRefuge.Closeup.Editor {
 public static class ProspectRefugeCloseupBuilder {
  const string Main="Assets/VideoScenes/architectural-111-20261106/06-02";
  const string Own="Assets/VideoScenes/architectural-111-20261106/06-02-closeup";
  [Serializable] sealed class Job {public string fingerprint,output,mainAttempt,mainFingerprint;public ModeReference[] modes;}
  [Serializable] sealed class ModeReference {public string mode,statesSHA256,configSHA256,commandTapeSHA256;}
  [Serializable] sealed class Header {public string fingerprint;}
  [Serializable] sealed class Pin {public string path,sha256;public long bytes;}
  [Serializable] sealed class Anchor {public string id;public Vector3 world,viewport,actualCameraRayEndpoint;public bool environmentBlocked,inFrustum;public string hitCollider;}
  [Serializable] sealed class CameraFrame {public int frame,mainSourceFrame;public Vector3 position,forward,focus;public float fieldOfView,nearClip,farClip,mainPlayerAspect,mainObserverAspect;public float[] viewProjectionRowMajor;public Anchor[] anchors;}
  [Serializable] sealed class Receipt {public string fingerprint,mainFingerprint,mode,mainStatesSHA256,closeupConfigSHA256;public int frames,fps,width,height,statesCompared;public string camera="closeup",comparisonPolicy;public bool allSharedStatesEqual=true;}
  [Serializable] sealed class SnapshotFile {public string path,snapshotRelativePath,sha256;public long bytes;}
  [Serializable] sealed class ModeSceneRecord {public string fingerprint,mainFingerprint,mode,scenePath;public int mainSourceFrame=0;public bool actualSceneFilesSaved=true;public SnapshotFile[] files;}
  static void ModeSnapshot(string output,Job job,string mode) {
   AssetDatabase.SaveAssets();AssetDatabase.Refresh();var files=new List<SnapshotFile>();
   var sourceKeys=new HashSet<string>(StringComparer.OrdinalIgnoreCase);var storageKeys=new HashSet<string>(StringComparer.Ordinal);
   var paths=new List<string>(Directory.GetFiles(Own,"*",SearchOption.AllDirectories));if(File.Exists(Own+".meta"))paths.Add(Own+".meta");
   foreach(var path in paths) {
    string canonical=path.Replace('\\','/');
    if((canonical.EndsWith(".unity",StringComparison.OrdinalIgnoreCase)||canonical.EndsWith(".unity.meta",StringComparison.OrdinalIgnoreCase))&&canonical!=CloseupScene(mode)&&canonical!=CloseupScene(mode)+".meta")continue;
    string relative="editable/"+Sha(Encoding.UTF8.GetBytes(canonical))+".bin";
    if(!sourceKeys.Add(canonical)||!storageKeys.Add(relative))throw new InvalidOperationException("Duplicate editable-source snapshot identity");
    var bytes=File.ReadAllBytes(path);string target=Path.Combine(output,relative);Directory.CreateDirectory(Path.GetDirectoryName(target));
    if(File.Exists(target))throw new InvalidOperationException("Preserve prior mode editable snapshot");File.WriteAllBytes(target,bytes);
    files.Add(new SnapshotFile{path=canonical,snapshotRelativePath=relative,sha256=Sha(bytes),bytes=bytes.LongLength});
   }
   File.WriteAllText(Path.Combine(output,"mode-scene-record.json"),JsonUtility.ToJson(new ModeSceneRecord{fingerprint=job.fingerprint,mainFingerprint=job.mainFingerprint,mode=mode,scenePath=CloseupScene(mode),files=files.ToArray()},true));
  }
  [Serializable] sealed class SceneRecord {public string fingerprint,mainFingerprint,unityVersion;public bool actualSceneFilesSaved=true;public string[] scenePaths;public Pin[] files;}
  static string Sha(byte[] bytes){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();}
  static Pin FilePin(string path){var b=File.ReadAllBytes(path);return new Pin{path=path.Replace('\\','/'),sha256=Sha(b),bytes=b.LongLength};}
  static void Same(object expected,object actual,string path) {
   if(path.EndsWith(".hitColliderEntityId",StringComparison.Ordinal))return;
   if(expected==null||actual==null){if(expected!=actual)throw new InvalidOperationException("State null mismatch: "+path);return;}
   var type=expected.GetType();if(type!=actual.GetType())throw new InvalidOperationException("State type mismatch: "+path);
   if(type==typeof(float)){if(BitConverter.SingleToInt32Bits((float)expected)!=BitConverter.SingleToInt32Bits((float)actual))throw new InvalidOperationException("Float32 state mismatch: "+path);return;}
   if(type.IsPrimitive||type==typeof(string)||type.IsEnum){if(!expected.Equals(actual))throw new InvalidOperationException("State value mismatch: "+path);return;}
   if(type.IsArray){var a=(Array)expected;var b=(Array)actual;if(a.Length!=b.Length)throw new InvalidOperationException("State length mismatch: "+path);for(int i=0;i<a.Length;i++)Same(a.GetValue(i),b.GetValue(i),path+"["+i+"]");return;}
   foreach(var field in type.GetFields(BindingFlags.Public|BindingFlags.Instance))Same(field.GetValue(expected),field.GetValue(actual),path+"."+field.Name);
  }
  static string Scene(string mode){return Main+(mode=="baseline"?"/S02-ProspectRefuge-Baseline.unity":"/S03-ProspectRefuge-Shifted.unity");}
  static string CloseupScene(string mode){return Own+(mode=="baseline"?"/S02-ProspectRefuge-Closeup-Baseline.unity":"/S03-ProspectRefuge-Closeup-Shifted.unity");}
  static CameraFrame Projection(ProspectRefugeExperiment rig,ProspectRefugeCloseupCamera follow,int frame) {
   var cam=follow.view;var anchors=new List<Anchor>();
   Action<string,Vector3> add=(id,world)=>{
    Vector3 viewport=cam.WorldToViewportPoint(world),delta=world-cam.transform.position;RaycastHit hit=new RaycastHit();
    bool blocked=delta.magnitude>1e-6f&&Physics.Raycast(cam.transform.position,delta.normalized,out hit,delta.magnitude,1<<ProspectRefugeExperiment.EnvironmentLayer,QueryTriggerInteraction.Ignore);
    if(!blocked)hit=new RaycastHit();
    anchors.Add(new Anchor{id=id,world=world,viewport=viewport,environmentBlocked=blocked,actualCameraRayEndpoint=blocked?hit.point:world,hitCollider=blocked?hit.collider.name:null,
     inFrustum=viewport.z>cam.nearClipPlane&&viewport.z<cam.farClipPlane&&viewport.x>=0&&viewport.x<=1&&viewport.y>=0&&viewport.y<=1});
   };
   add("player-ground",rig.player.transform.position);add("main-player-camera-eye",rig.playerCamera.transform.position);add("enemy-eye",rig.CurrentState.enemyEye);
   foreach(var ray in rig.BodyRays){add("body-"+ray.id,ray.desiredEndpoint);add("enemy-ray-"+ray.id+"-actual-end",ray.actualEndpoint);}
   add("first-cover-top",rig.config.firstCoverCenter+Vector3.up*rig.config.firstCoverSize.y*.5f);
   add("first-cover-bottom",rig.config.firstCoverCenter-Vector3.up*rig.config.firstCoverSize.y*.5f);
   add("second-cover-top",rig.secondCover.position+Vector3.up*rig.config.secondCoverSize.y*.5f);
   add("second-cover-bottom",rig.secondCover.position-Vector3.up*rig.config.secondCoverSize.y*.5f);
   var matrix=cam.projectionMatrix*cam.worldToCameraMatrix;var entries=new float[16];for(int r=0;r<4;r++)for(int c=0;c<4;c++)entries[r*4+c]=matrix[r,c];
   return new CameraFrame{frame=frame,mainSourceFrame=frame,position=cam.transform.position,forward=cam.transform.forward,focus=rig.player.transform.position+follow.config.lookOffset,
    fieldOfView=cam.fieldOfView,nearClip=cam.nearClipPlane,farClip=cam.farClipPlane,mainPlayerAspect=rig.playerCamera.aspect,mainObserverAspect=rig.observerCamera.aspect,viewProjectionRowMajor=entries,anchors=anchors.ToArray()};
  }
  public static void Capture() {
   var job=JsonUtility.FromJson<Job>(File.ReadAllText(Own+"/main-reference.json"));var args=Environment.GetCommandLineArgs();string selectedModes="baseline,shifted";
   for(int i=0;i<args.Length-1;i++) {
    if(args[i]=="-prospectRefugeOutput")job.output=args[i+1];
    if(args[i]=="-prospectRefugeFingerprint")job.fingerprint=args[i+1];
    if(args[i]=="-prospectRefugeModes")selectedModes=args[i+1];
   }
   if(job.fingerprint==null||job.fingerprint.Length!=64||job.fingerprint.Trim("0123456789abcdef".ToCharArray()).Length!=0||string.IsNullOrEmpty(job.output)||!Path.IsPathRooted(job.output)||job.modes==null||job.modes.Length!=2)throw new ArgumentException("Bound finite two-case main reference and explicit output/fingerprint required");
   var requested=new List<ModeReference>();var requestedNames=new HashSet<string>();
   foreach(string name in selectedModes.Split(',')){if(!requestedNames.Add(name))throw new ArgumentException("Duplicate mode");var reference=Array.Find(job.modes,m=>m.mode==name);if(reference==null)throw new ArgumentException("Unknown derivative mode");requested.Add(reference);}
   if(requested.Count<1)throw new ArgumentException("Finite derivative case required");job.modes=requested.ToArray();
   var mainHeader=JsonUtility.FromJson<Header>(File.ReadAllText(Path.Combine(job.mainAttempt,"input-provenance.json")));if(mainHeader.fingerprint!=job.mainFingerprint)throw new InvalidOperationException("Main capture identity differs");
   var config=JsonUtility.FromJson<CloseupConfig>(File.ReadAllText(Own+"/closeup-config.json"));if(config.frames!=600||config.fps!=60||config.width!=1920||config.height!=1080)throw new InvalidOperationException("Closeup clock differs");
   var seen=new HashSet<string>();foreach(var reference in job.modes){if((reference.mode!="baseline"&&reference.mode!="shifted")||!seen.Add(reference.mode))throw new InvalidOperationException("Exact baseline/shifted only");string dir=Path.Combine(job.output,reference.mode);if(Directory.Exists(dir)&&Directory.GetFileSystemEntries(dir).Length>0)throw new InvalidOperationException("Preserve previous closeup mode outputs");}
   if(File.Exists(Path.Combine(job.output,"scene-record.json")))throw new InvalidOperationException("Preserve previous closeup scene proof");
   Directory.CreateDirectory(job.output);var scenePaths=new List<string>();
   foreach(var reference in job.modes) {
    string mainMode=Path.Combine(job.mainAttempt,reference.mode),statePath=Path.Combine(mainMode,"states.jsonl");var originalBytes=File.ReadAllBytes(statePath);
    if(Sha(originalBytes)!=reference.statesSHA256||Sha(File.ReadAllBytes(Path.Combine(mainMode,"capture-config.json")))!=reference.configSHA256||Sha(File.ReadAllBytes(Path.Combine(mainMode,"command-tape.json")))!=reference.commandTapeSHA256)throw new InvalidOperationException("Main reference bytes changed");
    var originalLines=File.ReadAllLines(statePath);if(originalLines.Length!=600)throw new InvalidOperationException("Main600states required");
    EditorSceneManager.OpenScene(Scene(reference.mode),OpenSceneMode.Single);var rigs=UnityEngine.Object.FindObjectsByType<ProspectRefugeExperiment>();if(rigs.Length!=1)throw new InvalidOperationException("Exactly one saved main rig required");var rig=rigs[0];
    ProspectRefugeCloseupCamera.RestoreSourceAspect(rig);rig.ResetExperiment();var go=new GameObject("Derivative oblique closeup — same physical frame");var camera=go.AddComponent<Camera>();camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.018f,.025f,.023f);camera.cullingMask=rig.observerCamera.cullingMask;
    var follow=go.AddComponent<ProspectRefugeCloseupCamera>();follow.originalRig=rig;follow.subject=rig.player.transform;follow.view=camera;follow.config=config;follow.Refresh();
    if(!EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),CloseupScene(reference.mode)))throw new InvalidOperationException("Derivative editable scene save failed");scenePaths.Add(CloseupScene(reference.mode));
    string output=Path.Combine(job.output,reference.mode);Directory.CreateDirectory(output);ModeSnapshot(output,job,reference.mode);rig.previewInPlayMode=false;Directory.CreateDirectory(Path.Combine(output,"closeup"));
    var rt=new RenderTexture(1920,1080,24);rt.antiAliasing=2;rt.Create();var texture=new Texture2D(1920,1080,TextureFormat.RGB24,false);
    try {
     using(var states=new StreamWriter(Path.Combine(output,"states.jsonl")))using(var projections=new StreamWriter(Path.Combine(output,"projected-anchors.jsonl"))) {
      for(int frame=0;frame<600;frame++) {
       if(rig.Frame!=frame)throw new InvalidOperationException("Derivative capture clock drift");follow.Refresh();
       string stateJson=JsonUtility.ToJson(rig.CurrentState);
       Same(JsonUtility.FromJson<FrameState>(originalLines[frame]),JsonUtility.FromJson<FrameState>(stateJson),"FrameState");
       states.WriteLine(stateJson);projections.WriteLine(JsonUtility.ToJson(Projection(rig,follow,frame)));
       camera.targetTexture=rt;camera.Render();RenderTexture.active=rt;texture.ReadPixels(new Rect(0,0,1920,1080),0,0);texture.Apply();File.WriteAllBytes(Path.Combine(output,"closeup",frame.ToString("D4")+".jpg"),texture.EncodeToJPG(93));
       if(frame<599)rig.AdvanceOneFrame();
      }
     }
    } finally {camera.targetTexture=null;RenderTexture.active=null;rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(texture);}
    var receipt=new Receipt{fingerprint=job.fingerprint,mainFingerprint=job.mainFingerprint,mode=reference.mode,mainStatesSHA256=reference.statesSHA256,closeupConfigSHA256=Sha(File.ReadAllBytes(Own+"/closeup-config.json")),frames=600,fps=60,width=1920,height=1080,statesCompared=600,comparisonPolicy=config.comparisonPolicy};
    File.WriteAllText(Path.Combine(output,"mode-complete.json"),JsonUtility.ToJson(receipt,true));
   }
   AssetDatabase.SaveAssets();AssetDatabase.Refresh();var files=new List<Pin>();foreach(var f in Directory.GetFiles(Own,"*",SearchOption.AllDirectories))files.Add(FilePin(f));if(File.Exists(Own+".meta"))files.Add(FilePin(Own+".meta"));
   File.WriteAllText(Path.Combine(job.output,"scene-record.json"),JsonUtility.ToJson(new SceneRecord{fingerprint=job.fingerprint,mainFingerprint=job.mainFingerprint,unityVersion=Application.unityVersion,scenePaths=Array.FindAll(new[]{CloseupScene("baseline"),CloseupScene("shifted")},File.Exists),files=files.ToArray()},true));EditorApplication.Exit(0);
  }
 }
}
