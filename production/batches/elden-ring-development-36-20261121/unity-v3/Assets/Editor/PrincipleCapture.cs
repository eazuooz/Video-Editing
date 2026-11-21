using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Yamyam.EldenRingLessons
{
    public static class PrincipleCapture
    {
        const int Width = 950;
        const int Height = 650;
        const int Fps = 60;
        const string SceneFolder = "Assets/VideoScenes/EldenRingPrinciples";

        [Serializable] sealed class Cut
        {
            public string id;
            public int episode, shot, frames, speechStartFrame, speechEndFrame;
        }

        [Serializable] sealed class Job
        {
            public string output, ffmpeg, fingerprint;
            public bool pilot;
            public Cut[] cuts;
        }

        [Serializable] sealed class Receipt
        {
            public string id, scene, unity, renderPipeline, backend, fingerprint;
            public int frames, width, height, fps;
            public bool pilot;
        }

        public static void Run()
        {
            try
            {
                var project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
                if (!File.Exists(Path.Combine(project, "ELDEN_RING_PRINCIPLES_CAPTURE")))
                    throw new InvalidOperationException("Use the isolated Elden Ring capture project.");
                var path = Environment.GetEnvironmentVariable("YAMYAM_ELDEN_PRINCIPLE_JOB");
                if (string.IsNullOrEmpty(path)) throw new InvalidOperationException("An explicit capture job is required.");
                var job = JsonUtility.FromJson<Job>(File.ReadAllText(path));
                if (SystemInfo.graphicsDeviceType == UnityEngine.Rendering.GraphicsDeviceType.Null ||
                    UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline != null)
                    throw new InvalidOperationException("The captures require the built-in pipeline and an actual graphics device.");
                Directory.CreateDirectory(SceneFolder);
                Directory.CreateDirectory(job.output);
                AssetDatabase.Refresh();
                foreach (var cut in job.cuts)
                    Capture(job, cut);
                EditorApplication.Exit(0);
            }
            catch (Exception error)
            {
                UnityEngine.Debug.LogException(error);
                EditorApplication.Exit(1);
            }
        }

        static void Capture(Job job, Cut cut)
        {
            if (cut.episode < 1 || cut.episode > 36 || (cut.shot != 1 && cut.shot != 3) ||
                cut.id != $"{cut.episode:00}-{cut.shot}" || cut.frames < 150 || cut.frames > 1000 ||
                cut.speechStartFrame < 0 || cut.speechStartFrame >= cut.speechEndFrame || cut.speechEndFrame >= cut.frames)
                throw new InvalidDataException("Unexpected cut identity or approved cue window.");
            var folder = Path.Combine(job.output, cut.id);
            var scenePath = $"{SceneFolder}/{cut.id}.unity";
            var receiptPath = Path.Combine(folder, "capture.json");
            if (File.Exists(receiptPath))
            {
                var existing = JsonUtility.FromJson<Receipt>(File.ReadAllText(receiptPath));
                if (existing.fingerprint != job.fingerprint || existing.frames != cut.frames ||
                    existing.id != cut.id || existing.scene != scenePath || existing.pilot != job.pilot ||
                    !File.Exists(scenePath) || (job.pilot ? Directory.GetFiles(folder, "*.png").Length != 3 :
                    !File.Exists(Path.Combine(folder, "unity.mp4"))))
                    throw new InvalidDataException("Existing scope changed. Its capture has been preserved.");
                return;
            }
            Directory.CreateDirectory(folder);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var demo = new GameObject($"Elden Ring principle {cut.id}").AddComponent<PrincipleDemo>();
            var camera = new GameObject("Principle camera").AddComponent<Camera>();
            camera.transform.SetParent(demo.transform, false);
            demo.episode = cut.episode;
            demo.shot = cut.shot;
            demo.seconds = cut.frames / (float)Fps;
            demo.speechStart = cut.speechStartFrame / (float)Fps;
            demo.speechEnd = cut.speechEndFrame / (float)Fps;
            demo.view = camera;
            if (!EditorSceneManager.SaveScene(scene, scenePath)) throw new IOException($"Failed to save {scenePath}");
            demo.Build();
            foreach (var shader in demo.GetComponentsInChildren<Renderer>(true)
                         .Select(r => r.sharedMaterial).Where(m => m).Select(m => m.shader).Distinct())
                if (ShaderUtil.GetShaderMessages(shader).Any(message => message.severity.ToString() == "Error"))
                    throw new InvalidDataException($"Shader compilation failed for {shader.name}");

            var target = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32);
            var pixels = new Texture2D(Width, Height, TextureFormat.RGB24, false);
            target.Create();
            camera.targetTexture = target;
            try
            {
                if (job.pilot)
                {
                    var frames = new[] {cut.speechStartFrame, (cut.speechStartFrame + cut.speechEndFrame) / 2, cut.speechEndFrame};
                    foreach (var frame in frames)
                    {
                        Read(demo, target, pixels, frame);
                        File.WriteAllBytes(Path.Combine(folder, $"frame-{frame:0000}.png"), pixels.EncodeToPNG());
                    }
                }
                else Encode(job, cut, demo, target, pixels, folder);
            }
            finally
            {
                camera.targetTexture = null;
                RenderTexture.active = null;
                target.Release();
                Object.DestroyImmediate(target);
                Object.DestroyImmediate(pixels);
            }
            var receipt = new Receipt
            {
                id = cut.id, scene = scenePath, unity = Application.unityVersion, renderPipeline = "Built-in",
                backend = SystemInfo.graphicsDeviceType.ToString(), fingerprint = job.fingerprint,
                frames = cut.frames, fps = Fps, width = Width, height = Height, pilot = job.pilot
            };
            File.WriteAllText(receiptPath + ".tmp", JsonUtility.ToJson(receipt, true));
            File.Move(receiptPath + ".tmp", receiptPath);
            UnityEngine.Debug.Log($"Captured {cut.id} ({cut.frames} frames) using {receipt.backend}");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        }

        static void Read(PrincipleDemo demo, RenderTexture target, Texture2D pixels, int frame)
        {
            demo.Evaluate(frame / (float)Fps);
            demo.view.Render();
            RenderTexture.active = target;
            pixels.ReadPixels(new Rect(0, 0, Width, Height), 0, 0, false);
            RenderTexture.active = null;
        }

        static void Encode(Job job, Cut cut, PrincipleDemo demo, RenderTexture target, Texture2D pixels, string folder)
        {
            var result = Path.Combine(folder, "unity.mp4");
            var stage = Path.Combine(folder, "unity-in-progress.mp4");
            if (File.Exists(stage) || File.Exists(result))
                throw new IOException($"An interrupted cut was preserved at {folder}; use its recovery copy.");
            var args = $"-nostdin -hide_banner -loglevel error -n -f rawvideo -pixel_format rgb24 " +
                $"-video_size {Width}x{Height} -framerate {Fps} -i pipe:0 -vf vflip -an -c:v libx264 " +
                $"-threads 3 -preset ultrafast -crf 18 -pix_fmt yuv420p -movflags +faststart \"{stage}\"";
            using (var encoder = new Process {StartInfo = new ProcessStartInfo(job.ffmpeg, args)
                {UseShellExecute = false, CreateNoWindow = true, RedirectStandardInput = true}})
            {
                if (!encoder.Start()) throw new IOException("Cannot start the Unity capture encoder.");
                var buffer = new byte[Width * Height * 3];
                using (var pipe = encoder.StandardInput.BaseStream)
                    for (int frame = 0; frame < cut.frames; frame++)
                    {
                        Read(demo, target, pixels, frame);
                        pixels.GetRawTextureData<byte>().CopyTo(buffer);
                        pipe.Write(buffer, 0, buffer.Length);
                    }
                encoder.WaitForExit();
                if (encoder.ExitCode != 0) throw new IOException($"Capture encoding failed for {cut.id}");
            }
            File.Move(stage, result);
        }
    }
}
