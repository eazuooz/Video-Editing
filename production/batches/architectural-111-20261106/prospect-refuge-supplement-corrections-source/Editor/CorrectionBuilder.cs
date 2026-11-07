using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Yamyam.Architectural111.ProspectRefugeSupplement.Corrections.Editor {
    public static class CorrectionBuilder {
        const string Own="Assets/VideoScenes/architectural-111-20261106/06-02-Supplement-corrections";
        const string Source="Assets/VideoScenes/architectural-111-20261106/06-02-Supplement";
        const string SharedShader="Assets/VideoScenes/architectural-111-20261106/ArchitecturalSurface.shader";
        const string Knight="Assets/ThirdParty/KayKitAdventurers";
        static readonly string[] Modes={"scale","atrium","courtyard","refuge"};
        [Serializable] sealed class ModeReference {
            public string mode,sourceScenePath,sourceSceneSHA256,sourceSceneMetaSHA256;
        }
        [Serializable] sealed class SourceReference {
            public string sourceCaptureFingerprint;
            public ModeReference[] modes;
        }
        [Serializable] sealed class FileProof {
            public string path,sha256,snapshotRelativePath;
            public long bytes;
        }
        [Serializable] sealed class SceneRecord {
            public string fingerprint,sourceCaptureFingerprint,mode,sourceKind="our-authored-corrected-illustration",unityVersion;
            public bool actualSceneFilesSaved=true;
            public int savedAtFrame=0;
            public string[] scenePaths;
            public FileProof[] files;
            public CeilingProof[] additiveGeometry;
        }
        [Serializable] sealed class CeilingProof {
            public string id,meshAssetPath,materialAssetPath,meshAssetSHA256,materialAssetSHA256,observerSectionLabel;
            public bool sharedColliderBothCameras=true,sectionalSingleSidedSurface=true,cameraSpecificGeometry=false;
            public int colliderLayer;
            public Vector3 actualColliderWorldMin,actualColliderWorldMax,actualMeshWorldMin,actualMeshWorldMax;
            public Vector3 originalExteriorOverhangWorldMin,originalExteriorOverhangWorldMax,playerFootPoint,ceilingAbovePlayerPoint;
        }
        [Serializable] sealed class ModeRecord {
            public string fingerprint,sourceCaptureFingerprint,mode,sourceKind,correction,frameConvention;
            public string configSHA256,sourceReferenceSHA256,sourceScenePath,sourceSceneSHA256,sourceSceneMetaSHA256,actualScenePath;
            public int frames,fps,width,height;
            public bool actualSceneSaved=true;
            public string[] cameras={"player","observer"};
        }
        static string Canonical(string path){return path.Replace('\\','/');}
        static string Sha(byte[] bytes){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();}
        static string FileSha(string path){return Sha(File.ReadAllBytes(path));}
        static bool Hex(string value){return value!=null&&value.Length==64&&value.Trim("0123456789abcdef".ToCharArray()).Length==0;}
        static string ScenePath(CorrectionConfig config,string mode){foreach(var scene in config.scenes)if(scene.mode==mode)return Own+"/"+scene.sceneFile;throw new ArgumentException("Unknown corrective mode");}
        static CorrectionConfig Config(){
            var config=JsonUtility.FromJson<CorrectionConfig>(File.ReadAllText(Own+"/config.json"));
            if(config.frames!=720||config.fps!=60||config.width!=1920||config.height!=1080||config.sceneFolder!=Own||config.sourceSceneFolder!=Source||config.scenes==null||config.scenes.Length!=4)
                throw new InvalidOperationException("Exact four-scene corrective contract changed");
            if(config.courtyardTurnStartFrame!=600||config.courtyardTurnEndFrame!=690||config.scaleVerticalFieldOfView!=38)
                throw new InvalidOperationException("Selected corrective camera clock changed");
            var names=new HashSet<string>();foreach(var scene in config.scenes){
                if(Array.IndexOf(Modes,scene.mode)<0||!names.Add(scene.mode)||string.IsNullOrEmpty(scene.sourceSceneFile)||string.IsNullOrEmpty(scene.sceneFile)||
                   scene.sourceSceneFile.Contains("/")||scene.sourceSceneFile.Contains("\\")||scene.sceneFile.Contains("/")||scene.sceneFile.Contains("\\")||
                   !scene.sourceSceneFile.EndsWith(".unity")||!scene.sceneFile.EndsWith(".unity"))throw new InvalidOperationException("Invalid editable scene mapping");
            }
            return config;
        }
        static SourceReference Reference(CorrectionConfig config){
            var reference=JsonUtility.FromJson<SourceReference>(File.ReadAllText(Own+"/source-reference.json"));
            if(!Hex(reference.sourceCaptureFingerprint)||reference.modes==null||reference.modes.Length!=4)throw new InvalidOperationException("Original capture proof is missing");
            var seen=new HashSet<string>();foreach(var row in reference.modes){
                var scene=Array.Find(config.scenes,x=>x.mode==row.mode);
                if(scene==null||!seen.Add(row.mode)||row.sourceScenePath!=Source+"/"+scene.sourceSceneFile||!Hex(row.sourceSceneSHA256)||!Hex(row.sourceSceneMetaSHA256))
                    throw new InvalidOperationException("Original scene proof escaped selected four modes");
                VerifySource(row);
            }
            return reference;
        }
        static void VerifySource(ModeReference reference){
            if(FileSha(reference.sourceScenePath)!=reference.sourceSceneSHA256||FileSha(reference.sourceScenePath+".meta")!=reference.sourceSceneMetaSHA256)
                throw new InvalidOperationException("Preserved original scene bytes changed");
        }
        static CorrectionDriver LoadCorrected(CorrectionConfig config,ModeReference reference){
            VerifySource(reference);EditorSceneManager.OpenScene(reference.sourceScenePath,OpenSceneMode.Single);
            var rigs=UnityEngine.Object.FindObjectsByType<Experiment>();
            if(rigs.Length!=1||rigs[0].mode!=reference.mode||rigs[0].IsEncounter)throw new InvalidOperationException("One selected original supplementary rig required");
            if(UnityEngine.Object.FindObjectsByType<CorrectionDriver>().Length!=0)throw new InvalidOperationException("Original scene must not already contain correction component");
            var driver=new GameObject("OUR CORRECTED ILLUSTRATION: "+reference.mode).AddComponent<CorrectionDriver>();
            driver.originalRig=rigs[0];driver.config=config;driver.previewInPlayMode=true;
            if(reference.mode=="refuge")AddInteriorCeiling(driver);
            driver.ResetCorrection();
            return driver;
        }
        const string CeilingName="OUR ADDITIVE SECTION: shared interior low ceiling";
        const string CeilingMesh=Own+"/Meshes/SectionalInteriorCeiling.asset";
        const string CeilingMaterial=Own+"/Materials/SectionalInteriorCeiling.mat";
        const string CeilingLabel="설명용 단면 · 실내 천장";
        static void AddCeilingAnchor(List<AnchorDefinition> anchors,string id,Vector3 point,string role){
            var target=new GameObject(id).transform;target.position=point;
            anchors.Add(new AnchorDefinition{id=id,role=role,target=target,localPoint=Vector3.zero});
        }
        static void AddInteriorCeiling(CorrectionDriver driver){
            var c=driver.config;var rig=driver.originalRig;
            if(c.interiorCeilingWidth!=6||c.interiorCeilingUndersideY!=1.65f||c.interiorCeilingThickness!=.1f||c.interiorCeilingMinZ!=-5||c.interiorCeilingMaxZ!=-1)
                throw new InvalidOperationException("Selected interior ceiling geometry changed");
            if(GameObject.Find(CeilingName))throw new InvalidOperationException("Do not duplicate additive ceiling");
            Directory.CreateDirectory(Own+"/Meshes");Directory.CreateDirectory(Own+"/Materials");AssetDatabase.Refresh();
            var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(CeilingMesh);bool newMesh=!mesh;if(newMesh)mesh=new Mesh();else mesh.Clear();
            float x=c.interiorCeilingWidth*.5f,y=c.interiorCeilingUndersideY,a=c.interiorCeilingMinZ,b=c.interiorCeilingMaxZ;
            mesh.name="Actual downward-facing interior ceiling sectional surface";
            mesh.vertices=new[]{new Vector3(-x,y,a),new Vector3(x,y,a),new Vector3(x,y,b),new Vector3(-x,y,b)};
            mesh.triangles=new[]{0,1,2,0,2,3};mesh.RecalculateNormals();mesh.RecalculateBounds();
            if(newMesh)AssetDatabase.CreateAsset(mesh,CeilingMesh);EditorUtility.SetDirty(mesh);
            var original=AssetDatabase.LoadAssetAtPath<Material>(Source+"/Materials/Wood.mat");if(!original)throw new InvalidOperationException("Original licensed stage wood material missing");
            var material=AssetDatabase.LoadAssetAtPath<Material>(CeilingMaterial);if(!material){material=new Material(original);AssetDatabase.CreateAsset(material,CeilingMaterial);}else material.CopyPropertiesFromMaterial(original);
            material.name="Original stage wood on additive sectional ceiling";EditorUtility.SetDirty(material);
            var go=new GameObject(CeilingName);go.layer=Experiment.EnvironmentLayer;
            go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterial=material;
            var collider=go.AddComponent<BoxCollider>();collider.center=new Vector3(0,y+c.interiorCeilingThickness*.5f,(a+b)*.5f);collider.size=new Vector3(x*2,c.interiorCeilingThickness,b-a);
            // A real front edge makes the section/height legible from above.
            // Its visual mesh is identical in both cameras; the shared full box
            // collider already describes the interior ceiling thickness.
            var edge=GameObject.CreatePrimitive(PrimitiveType.Cube);edge.name="Actual interior ceiling front thickness edge";edge.layer=Experiment.EnvironmentLayer;
            edge.transform.position=new Vector3(0,y+c.interiorCeilingThickness*.5f,b);edge.transform.localScale=new Vector3(x*2,c.interiorCeilingThickness,.06f);
            UnityEngine.Object.DestroyImmediate(edge.GetComponent<Collider>());edge.GetComponent<Renderer>().sharedMaterial=material;
            var anchors=new List<AnchorDefinition>(rig.anchorDefinitions);
            AddCeilingAnchor(anchors,"interior-ceiling-underside-above-player",new Vector3(0,y,-2),"Actual shared interior ceiling underside above the depressed actor");
            AddCeilingAnchor(anchors,"interior-ceiling-floor-below-player",new Vector3(0,-.65f,-2),"Actual depressed floor point below the ceiling height leader");
            AddCeilingAnchor(anchors,"interior-ceiling-front-edge-center",new Vector3(0,y,b),"Actual interior ceiling front edge, distinct from exterior overhang");
            AddCeilingAnchor(anchors,"interior-ceiling-front-left",new Vector3(-x,y,b),"Actual interior ceiling edge endpoint");
            AddCeilingAnchor(anchors,"interior-ceiling-front-right",new Vector3(x,y,b),"Actual interior ceiling edge endpoint");
            var outside=GameObject.Find("Deep real exterior overhang");if(!outside)throw new InvalidOperationException("Original exterior overhang must remain separate");
            AddCeilingAnchor(anchors,"original-exterior-overhang-center",outside.transform.position,"Original exterior overhang, not the new interior ceiling");
            rig.anchorDefinitions=anchors.ToArray();
            var label=new GameObject("Observer label: "+CeilingLabel);label.layer=Experiment.GuideLayer;label.transform.position=new Vector3(0,y+.5f,b);
            label.transform.rotation=Quaternion.LookRotation(label.transform.position-rig.observerCamera.transform.position);
            var text=label.AddComponent<TextMesh>();text.text=CeilingLabel;text.anchor=TextAnchor.MiddleCenter;text.alignment=TextAlignment.Center;text.fontSize=48;text.characterSize=.055f;text.color=new Color(1,.84f,.35f);
            text.font=AssetDatabase.LoadAssetAtPath<Font>(Source+"/Materials/NativeGuideFont.asset");if(!text.font)throw new InvalidOperationException("Original pinned OS-font descriptor missing");label.GetComponent<Renderer>().sharedMaterial=text.font.material;
            Physics.SyncTransforms();
        }
        static CeilingProof[] ActualCeilingProof(){
            var go=GameObject.Find(CeilingName);if(!go)return new CeilingProof[0];
            var collider=go.GetComponent<BoxCollider>();var mesh=go.GetComponent<Renderer>();var outside=GameObject.Find("Deep real exterior overhang").GetComponent<Collider>();
            var rig=UnityEngine.Object.FindObjectsByType<Experiment>()[0];var driver=UnityEngine.Object.FindObjectsByType<CorrectionDriver>()[0];
            return new[]{new CeilingProof{id="interior-ceiling",meshAssetPath=CeilingMesh,materialAssetPath=CeilingMaterial,meshAssetSHA256=FileSha(CeilingMesh),materialAssetSHA256=FileSha(CeilingMaterial),observerSectionLabel=CeilingLabel,
                colliderLayer=go.layer,actualColliderWorldMin=collider.bounds.min,actualColliderWorldMax=collider.bounds.max,actualMeshWorldMin=mesh.bounds.min,actualMeshWorldMax=mesh.bounds.max,
                originalExteriorOverhangWorldMin=outside.bounds.min,originalExteriorOverhangWorldMax=outside.bounds.max,playerFootPoint=rig.player.transform.position,
                ceilingAbovePlayerPoint=new Vector3(rig.player.transform.position.x,driver.config.interiorCeilingUndersideY,rig.player.transform.position.z)}};
        }
        static bool AllowedAsset(string path){return path.StartsWith(Own+"/")||path==Own+".meta"||path.StartsWith(Source+"/")||path==Source+".meta"||
            path.StartsWith(Knight+"/")||path==Knight+".meta"||path==SharedShader||path==SharedShader+".meta";}
        static void AddWithMeta(SortedSet<string> paths,string path){
            path=Canonical(path);if(!AllowedAsset(path)||!File.Exists(path))throw new InvalidOperationException("Missing/scoped-out editable source "+path);
            paths.Add(path);if(File.Exists(path+".meta"))paths.Add(path+".meta");
        }
        static void Snapshot(string output,string fp,SourceReference reference,string mode,string[] scenes){
            AssetDatabase.SaveAssets();AssetDatabase.Refresh();var paths=new SortedSet<string>(StringComparer.Ordinal);
            // Canonicalize BEFORE filtering. Directory.GetFiles returns mixed Windows separators.
            foreach(string raw in Directory.GetFiles(Own,"*",SearchOption.AllDirectories)){
                string path=Canonical(raw);
                bool sceneFile=path.EndsWith(".unity",StringComparison.OrdinalIgnoreCase)||path.EndsWith(".unity.meta",StringComparison.OrdinalIgnoreCase);
                bool selected=false;foreach(string scene in scenes)if(path==scene||path==scene+".meta")selected=true;
                if(!sceneFile||selected)paths.Add(path);
            }
            if(File.Exists(Own+".meta"))paths.Add(Own+".meta");
            foreach(string scene in scenes){
                AddWithMeta(paths,scene);
                foreach(string raw in AssetDatabase.GetDependencies(scene,true)){
                    string path=Canonical(raw);if(File.Exists(path))AddWithMeta(paths,path);
                }
                var selected=Array.Find(reference.modes,x=>ScenePath(Config(),x.mode)==scene);if(selected==null)throw new InvalidOperationException("Saved scene has no original proof");
                AddWithMeta(paths,selected.sourceScenePath);
            }
            foreach(string path in new[]{Source+"/Experiment.cs",Source+"/config.json",Own+"/CorrectionDriver.cs",Own+"/Editor/CorrectionBuilder.cs",Own+"/config.json",Own+"/source-reference.json",SharedShader})AddWithMeta(paths,path);
            var files=new List<FileProof>();foreach(string path in paths){
                if(!AllowedAsset(path)||path.Contains("..")||path.Contains("\\"))throw new InvalidOperationException("Noncanonical editable proof");
                byte[] bytes=File.ReadAllBytes(path);string relative="editable/"+Sha(Encoding.UTF8.GetBytes(path))+".bin";
                string target=Path.Combine(output,relative);Directory.CreateDirectory(Path.GetDirectoryName(target));
                if(File.Exists(target))throw new InvalidOperationException("Preserve existing flat editable snapshot");
                File.WriteAllBytes(target,bytes);files.Add(new FileProof{path=path,sha256=Sha(bytes),bytes=bytes.LongLength,snapshotRelativePath=relative});
            }
            var record=new SceneRecord{fingerprint=fp,sourceCaptureFingerprint=reference.sourceCaptureFingerprint,mode=mode,unityVersion=Application.unityVersion,scenePaths=scenes,files=files.ToArray(),additiveGeometry=ActualCeilingProof()};
            string result=Path.Combine(output,"scene-record.json");if(File.Exists(result))throw new InvalidOperationException("Preserve original scene record");
            File.WriteAllText(result+".tmp",JsonUtility.ToJson(record,true));File.Move(result+".tmp",result);
        }
        public static void Capture(){
            string output=null,fp=null,list=null;var args=Environment.GetCommandLineArgs();
            for(int i=0;i<args.Length-1;i++){
                if(args[i]=="-correctionOutput")output=args[i+1];if(args[i]=="-correctionFingerprint")fp=args[i+1];if(args[i]=="-correctionModes")list=args[i+1];
            }
            if(string.IsNullOrEmpty(output)||!Path.IsPathRooted(output)||!Hex(fp)||string.IsNullOrEmpty(list))throw new ArgumentException("Explicit fresh absolute output/64hex fingerprint/modes required");
            var requested=list.Split(',');var unique=new HashSet<string>();foreach(string mode in requested)if(Array.IndexOf(Modes,mode)<0||!unique.Add(mode))throw new ArgumentException("Only finite selected corrective modes allowed");
            if(Directory.Exists(output)&&Directory.GetFileSystemEntries(output).Length>0)throw new InvalidOperationException("Preserve previous/partial correction attempt");
            Directory.CreateDirectory(output);var config=Config();var reference=Reference(config);var saved=new List<string>();
            byte[] configBytes=File.ReadAllBytes(Own+"/config.json"),referenceBytes=File.ReadAllBytes(Own+"/source-reference.json");
            foreach(string mode in requested){
                var source=Array.Find(reference.modes,x=>x.mode==mode);var driver=LoadCorrected(config,source);var rig=driver.originalRig;
                string scene=ScenePath(config,mode);if(!EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),scene))throw new InvalidOperationException("Corrected editable scene save failed");
                saved.Add(scene);AssetDatabase.SaveAssets();string dir=Path.Combine(output,mode);Directory.CreateDirectory(dir);
                File.WriteAllBytes(Path.Combine(dir,"config.json"),configBytes);File.WriteAllBytes(Path.Combine(dir,"source-reference.json"),referenceBytes);
                var contract=new ModeRecord{fingerprint=fp,sourceCaptureFingerprint=reference.sourceCaptureFingerprint,mode=mode,sourceKind=config.sourceKind,
                    correction=driver.Scene().correction,frameConvention=config.frameConvention,configSHA256=Sha(configBytes),sourceReferenceSHA256=Sha(referenceBytes),
                    sourceScenePath=source.sourceScenePath,sourceSceneSHA256=source.sourceSceneSHA256,sourceSceneMetaSHA256=source.sourceSceneMetaSHA256,
                    actualScenePath=scene,frames=config.frames,fps=config.fps,width=config.width,height=config.height};
                File.WriteAllText(Path.Combine(dir,"mode-contract.json"),JsonUtility.ToJson(contract,true));
                Snapshot(dir,fp,reference,mode,new[]{scene});driver.previewInPlayMode=false;
                var rt=new RenderTexture(config.width,config.height,24);rt.antiAliasing=2;rt.Create();var image=new Texture2D(config.width,config.height,TextureFormat.RGB24,false);
                try{
                    using(var states=new StreamWriter(Path.Combine(dir,"states.jsonl")))using(var rays=new StreamWriter(Path.Combine(dir,"rays.jsonl")))using(var anchors=new StreamWriter(Path.Combine(dir,"projected-anchors.jsonl"))){
                        for(int frame=0;frame<config.frames;frame++){
                            if(driver.Frame!=frame||driver.CurrentState.frame!=frame)throw new InvalidOperationException("Correction shared frame drift");
                            states.WriteLine(JsonUtility.ToJson(driver.CurrentState));rays.WriteLine(JsonUtility.ToJson(new RayFrame{frame=frame,rays=driver.CurrentRays}));
                            anchors.WriteLine(JsonUtility.ToJson(driver.ProjectedAnchors()));
                            foreach(var pair in new[]{Tuple.Create("player",rig.playerCamera),Tuple.Create("observer",rig.observerCamera)}){
                                var camera=pair.Item2;camera.targetTexture=rt;camera.Render();RenderTexture.active=rt;image.ReadPixels(new Rect(0,0,config.width,config.height),0,0);image.Apply();
                                string folder=Path.Combine(dir,pair.Item1);Directory.CreateDirectory(folder);File.WriteAllBytes(Path.Combine(folder,frame.ToString("D4")+".jpg"),image.EncodeToJPG(93));
                            }
                            if(frame<config.frames-1)driver.AdvanceOneFrame();
                        }
                    }
                }finally{rig.playerCamera.targetTexture=null;rig.observerCamera.targetTexture=null;RenderTexture.active=null;rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(image);}
                File.WriteAllText(Path.Combine(dir,"corrected-route.json"),JsonUtility.ToJson(driver.RouteEvidence(),true));
                VerifySource(source);string done=Path.Combine(dir,"mode-complete.json");File.WriteAllText(done+".tmp",JsonUtility.ToJson(contract,true));File.Move(done+".tmp",done);
            }
            Snapshot(output,fp,reference,"selected-aggregate",saved.ToArray());
            File.WriteAllText(Path.Combine(output,"capture-complete.txt"),fp+"; selected corrective modes="+list+"; original source preserved; our illustration; no safety/AI measurement");
            EditorApplication.Exit(0);
        }
    }
}
