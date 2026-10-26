using System;
using System.IO;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Yamyam.Video.SurfaceInk.Editor
{
    // A finite, explicitly supplied job. It does not run on editor import.
    public static class SurfaceInkCapture
    {
        [Serializable] public class Clip
        {
            public string id; public int stage, frames, startFrame, endFrame;
            public float split=.5f;
            public bool cueSynchronized;
            public float hitAt=.65f, stampEnd=1, floorAt=0;
            public int expectedHitTimelineFrame=-1, stampEndTimelineFrame=-1, floorTimelineFrame=-1;
        }
        [Serializable] public class Job { public string output; public bool preview; public Clip[] clips; }
        [Serializable] public class PaintSample
        {
            public int frame, finalTimelineFrame; public float progress; public Vector2 wallUV; public Vector3 wallHit;
            public Vector3 cameraPosition, cameraForward;
            public SurfaceInkDemo.PaintTextureEvidence paint;
        }
        [Serializable] public class Readback
        {
            public string id; public int stage, frames; public bool preview; public Vector2 wallUV; public Vector3 wallHit;
            public string sourceKind="our-Unity-implementation";
            public PaintSample[] textureSamples;
            public bool allCapturedTextureFramesChecked, paintBytesUnchangedAcrossCheckedFrames;
            public bool textureObjectsUnchangedAcrossCheckedFrames, noTextureMutationsAfterFirstCheckedFrame;
            public bool cameraMovedAcrossCheckedFrames;
            public bool cueSynchronized;
            public float hitAt, stampEnd, floorAt;
            public int startFrame, endFrame, firstWallHitTimelineFrame, expectedHitTimelineFrame;
            public int stampEndTimelineFrame, floorTimelineFrame;
            public string textureEvidenceLimit="Hashes are actual CPU Texture2D bytes after Upload/Apply, not a GPU texture readback. Full orbit frames are checked; other full clips retain boundary/switch samples only.";
        }
        static Job job; static int clipIndex, index; static SurfaceInkDemo demo;
        static RenderTexture target; static Texture2D pixels; static Scene scene;
        static readonly List<PaintSample> textureSamples = new List<PaintSample>();
        static int firstWallHitFrame;
        static readonly string[] Names={"01-SurfaceSheet","02-Collision","03-UVAddress","04-StampFloorWall","05-AdjacentPatch","06-CameraOrbit"};
        static readonly float[] Samples={0,.35f,.7f,1};
        public static void Run()
        {
            try
            {
                string[] args=Environment.GetCommandLineArgs();int at=Array.IndexOf(args,"-inkJob");
                if(at<0 || at+1>=args.Length)throw new ArgumentException("Explicit -inkJob required");
                job=JsonUtility.FromJson<Job>(File.ReadAllText(args[at+1]));
                if(job.clips==null || job.clips.Length==0 || !Path.IsPathRooted(job.output))throw new ArgumentException("Invalid job");
                const string isolated="C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/unity-capture";
                if(!string.Equals(Path.GetFullPath(".").Replace('\\','/').TrimEnd('/'),isolated,StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Run this capture only in the owned isolated project.");
                EditorApplication.delayCall+=StartCapture;
            }
            catch(Exception e){Fail(e);}
        }
        static void StartCapture()
        {
            try
            {
                var boot=SceneManager.GetActiveScene();
                if(boot.IsValid() && string.IsNullOrEmpty(boot.path))
                {
                    Directory.CreateDirectory("Assets/CaptureScratch");
                    if(!EditorSceneManager.SaveScene(boot,"Assets/CaptureScratch/Boot.unity"))
                        throw new IOException("Save the isolated editor's initial untitled scene before additive lesson creation.");
                }
                if(File.Exists(Path.Combine(job.output,"success.json")))throw new IOException("Preserve successful capture");
                Directory.CreateDirectory(job.output);
                if(!File.Exists("Assets/VideoScenes/shorts-splatoon-surface-ink/Scenes/"+Names[0]+".unity"))SurfaceInkBuilder.Build();
                target=new RenderTexture(1080,1920,24,RenderTextureFormat.ARGB32){antiAliasing=1};target.Create();
                pixels=new Texture2D(1080,1920,TextureFormat.RGB24,false);
                Prepare();EditorApplication.update+=Tick;
            }
            catch(Exception e){Fail(e);}
        }
        static void Prepare()
        {
            var clip=job.clips[clipIndex];
            if(clip.stage<0 || clip.stage>=Names.Length || clip.frames<2 || clip.id.IndexOfAny(Path.GetInvalidFileNameChars())>=0)throw new ArgumentException("Invalid clip");
            if(clip.cueSynchronized && (clip.startFrame<0 || clip.endFrame-clip.startFrame!=clip.frames ||
                clip.hitAt<=0 || clip.hitAt>1 || clip.stampEnd<=0 || clip.stampEnd>1 || clip.floorAt<0 || clip.floorAt>1))
                throw new ArgumentException("Invalid actual speech-to-stage parameters");
            scene=EditorSceneManager.OpenScene("Assets/VideoScenes/shorts-splatoon-surface-ink/Scenes/"+Names[clip.stage]+".unity",OpenSceneMode.Additive);
            foreach(var root in scene.GetRootGameObjects()){demo=root.GetComponentInChildren<SurfaceInkDemo>();if(demo)break;}
            if(!demo)throw new InvalidOperationException("Scene component missing");
            demo.Initialize();demo.lessonCamera.targetTexture=target;index=0;
            textureSamples.Clear();
            firstWallHitFrame=-1;
            Directory.CreateDirectory(Path.Combine(job.output,clip.id));
        }
        static void Tick()
        {
            try
            {
                var clip=job.clips[clipIndex];float t=job.preview?Samples[index]:index/(float)(clip.frames-1);
                float hitAt=clip.cueSynchronized?clip.hitAt:.65f;
                demo.ApplyFrame(clip.stage,t,clip.stage!=4 || t>=clip.split,hitAt,
                    clip.cueSynchronized?clip.stampEnd:1,clip.cueSynchronized?clip.floorAt:0);
                if(demo.wallPaintHasHit && firstWallHitFrame<0)firstWallHitFrame=index;
                // Every orbit frame is checked, not just matching endpoint hashes.
                // Other full clips preserve first/last and the patch switch edge.
                int switchFrame=Mathf.CeilToInt(clip.split*(clip.frames-1));
                int hitFrame=Mathf.CeilToInt(hitAt*(clip.frames-1));
                int stampFrame=Mathf.CeilToInt((clip.cueSynchronized?clip.stampEnd:1)*(clip.frames-1));
                int floorFrame=Mathf.CeilToInt((clip.cueSynchronized?clip.floorAt:0)*(clip.frames-1));
                bool inspectTexture=job.preview || clip.stage==5 || index==0 || index==clip.frames-1 ||
                    (clip.stage==4 && Mathf.Abs(index-switchFrame)<=1) ||
                    (clip.stage==1 && Mathf.Abs(index-hitFrame)<=1) ||
                    (clip.stage==3 && (Mathf.Abs(index-stampFrame)<=1 || Mathf.Abs(index-floorFrame)<=1));
                if(inspectTexture)textureSamples.Add(new PaintSample{frame=index,finalTimelineFrame=clip.startFrame+index,progress=t,
                    wallUV=demo.wallUV,wallHit=demo.wallHit,cameraPosition=demo.lessonCamera.transform.position,
                    cameraForward=demo.lessonCamera.transform.forward,paint=demo.CapturePaintEvidence()});
                demo.lessonCamera.Render();
                if(ShaderUtil.ShaderHasError(demo.paintMaterial.shader))throw new InvalidOperationException("Lesson shader failed compilation; preserve the failed preview and fix source.");
                var prior=RenderTexture.active;RenderTexture.active=target;
                pixels.ReadPixels(new Rect(0,0,1080,1920),0,0);pixels.Apply(false);RenderTexture.active=prior;
                string file=Path.Combine(job.output,clip.id,index.ToString("D6")+".jpg");
                using(var stream=new FileStream(file,FileMode.CreateNew)) {var bytes=pixels.EncodeToJPG(94);stream.Write(bytes,0,bytes.Length);}
                index++;
                if(index<(job.preview?Samples.Length:clip.frames))return;
                var readback=MakeReadback(clip,index);
                if(!job.preview && clip.cueSynchronized && clip.stage==1 &&
                    (firstWallHitFrame<0 || Mathf.Abs(readback.firstWallHitTimelineFrame-clip.expectedHitTimelineFrame)>1))
                    throw new InvalidOperationException("Actual collision hit differs from its measured narration cue binding.");
                if(clip.stage==5 && (!readback.allCapturedTextureFramesChecked ||
                    !readback.paintBytesUnchangedAcrossCheckedFrames ||
                    !readback.textureObjectsUnchangedAcrossCheckedFrames ||
                    !readback.noTextureMutationsAfterFirstCheckedFrame || !readback.cameraMovedAcrossCheckedFrames))
                    throw new InvalidOperationException("Orbit must preserve paint bytes/objects and perform no further reset/stamp/upload while only the camera moves.");
                File.WriteAllText(Path.Combine(job.output,clip.id,"capture.json"),JsonUtility.ToJson(readback,true));
                EditorSceneManager.CloseScene(scene,true);demo=null;clipIndex++;
                if(clipIndex<job.clips.Length){Prepare();return;}
                File.WriteAllText(Path.Combine(job.output,"success.json"),"{\"width\":1080,\"height\":1920,\"fps\":60,\"clips\":"+clipIndex+",\"preview\":"+(job.preview?"true":"false")+"}");
                EditorApplication.update-=Tick;EditorApplication.Exit(0);
            }
            catch(Exception e){Fail(e);}
        }
        static Readback MakeReadback(Clip clip,int frames)
        {
            bool sameBytes=true,sameObjects=true,noMutations=true,cameraMoved=false;
            if(textureSamples.Count==0)throw new InvalidOperationException("Texture evidence samples missing.");
            var first=textureSamples[0];
            foreach(var sample in textureSamples)
            {
                sameBytes &= sample.paint.floorSHA256==first.paint.floorSHA256 && sample.paint.wallSHA256==first.paint.wallSHA256;
                sameObjects &= sample.paint.floorTextureEntityId==first.paint.floorTextureEntityId &&
                               sample.paint.wallTextureEntityId==first.paint.wallTextureEntityId;
                noMutations &= sample.paint.resetOperations==first.paint.resetOperations &&
                               sample.paint.stampOperations==first.paint.stampOperations &&
                               sample.paint.pairedTextureUploadOperations==first.paint.pairedTextureUploadOperations;
                cameraMoved |= (sample.cameraPosition-first.cameraPosition).sqrMagnitude>.000001f ||
                               (sample.cameraForward-first.cameraForward).sqrMagnitude>.000001f;
                if(!sample.paint.sheetAndWallShareTexture)throw new InvalidOperationException("Sheet and wall must sample the same real wall paint texture.");
            }
            return new Readback{id=clip.id,stage=clip.stage,frames=frames,preview=job.preview,
                wallUV=demo.wallUV,wallHit=demo.wallHit,textureSamples=textureSamples.ToArray(),
                allCapturedTextureFramesChecked=textureSamples.Count==frames,
                paintBytesUnchangedAcrossCheckedFrames=sameBytes,textureObjectsUnchangedAcrossCheckedFrames=sameObjects,
                noTextureMutationsAfterFirstCheckedFrame=noMutations,cameraMovedAcrossCheckedFrames=cameraMoved,
                cueSynchronized=clip.cueSynchronized,hitAt=clip.cueSynchronized?clip.hitAt:.65f,
                stampEnd=clip.cueSynchronized?clip.stampEnd:1,floorAt=clip.cueSynchronized?clip.floorAt:0,
                startFrame=clip.startFrame,endFrame=clip.endFrame,
                firstWallHitTimelineFrame=firstWallHitFrame<0?-1:clip.startFrame+firstWallHitFrame,
                expectedHitTimelineFrame=clip.expectedHitTimelineFrame,
                stampEndTimelineFrame=clip.stampEndTimelineFrame,floorTimelineFrame=clip.floorTimelineFrame};
        }
        static void Fail(Exception e){EditorApplication.update-=Tick;Debug.LogException(e);EditorApplication.Exit(1);}
    }
}
