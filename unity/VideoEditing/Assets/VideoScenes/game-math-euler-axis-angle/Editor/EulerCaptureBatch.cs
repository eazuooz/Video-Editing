using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace YamyamCoding.GameMath.EulerAxisAngle.Editor
{
    /// <summary>Explicit isolated-project finite motion capture; no audio or automatic job creation.</summary>
    public static class EulerCaptureBatch
    {
        [Serializable] public class Job
        {
            public string outputDirectory, ffmpegPath;
            public bool renderPngPreviewsOnly;
            public Clip[] clips;
        }
        [Serializable] public class Clip
        {
            public string sceneId, fileStem;
            public int frames = 120;
            public float startNormalized, endNormalized = 1f;
            public FrameKey[] keys;
        }
        [Serializable] public class FrameKey { public int frame; public float normalized; }

        public static void Run()
        {
            EulerSceneAssetBuilder.RequireIsolatedBatch();
            EulerSceneAssetBuilder.RunMathChecks();
            string jobPath = Argument("-m04Job");
            if (string.IsNullOrWhiteSpace(jobPath)) throw new ArgumentException("Missing -m04Job JSON path.");
            Job job = JsonUtility.FromJson<Job>(File.ReadAllText(jobPath));
            if (job == null || job.clips == null || job.clips.Length == 0) throw new ArgumentException("Empty M04 capture job.");
            Directory.CreateDirectory(job.outputDirectory);
            // Only this disposable batch project changes pipeline selection. The
            // user's canonical URP editor and its settings are never modified.
            GraphicsSettings.defaultRenderPipeline = null;
            QualitySettings.renderPipeline = null;
            QualitySettings.antiAliasing = 2;
            try
            {
                foreach (Clip clip in job.clips) Capture(job, clip);
                File.WriteAllText(Path.Combine(job.outputDirectory, "capture-success.json"),
                    "{\"renderer\":\"Unity built-in isolated capture\",\"width\":1920,\"height\":1080,\"fps\":60,\"editor\":\"" + Application.unityVersion + "\"}");
                EditorApplication.Exit(0);
            }
            catch (Exception ex)
            {
                UnityEngine.Debug.LogException(ex);
                File.WriteAllText(Path.Combine(job.outputDirectory, "capture-error.txt"), ex.ToString());
                EditorApplication.Exit(1);
            }
        }
        private static void Capture(Job job, Clip clip)
        {
            int index = Array.IndexOf(EulerSceneAssetBuilder.Ids, clip.sceneId);
            if (index < 0 || clip.frames < 1 || clip.frames > 36000) throw new ArgumentException("Invalid clip.");
            string path = EulerSceneAssetBuilder.Root + "/Scenes/" + clip.sceneId + "-" + EulerSceneAssetBuilder.Modes[index] + ".unity";
            EditorSceneManager.OpenScene(path, OpenSceneMode.Single);
            EulerAircraftScene scene = UnityEngine.Object.FindAnyObjectByType<EulerAircraftScene>();
            if (scene == null) throw new InvalidOperationException("Missing M04 controller in " + path);
            scene.Build();
            var target = new RenderTexture(1920, 1080, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Default)
                { antiAliasing = 2, name = "M04 1080p capture target" };
            target.Create();
            var pixels = new Texture2D(1920, 1080, TextureFormat.RGB24, false, false);
            scene.SceneCamera.targetTexture = target;
            Process encoder = null; var errors = new StringBuilder();
            string stem = string.IsNullOrWhiteSpace(clip.fileStem) ? clip.sceneId : clip.fileStem;
            if (Path.GetFileName(stem) != stem) throw new ArgumentException("fileStem must be a filename only.");
            try
            {
                if (!job.renderPngPreviewsOnly)
                {
                    if (!File.Exists(job.ffmpegPath)) throw new FileNotFoundException("Explicit ffmpegPath is required.", job.ffmpegPath);
                    var start = new ProcessStartInfo(job.ffmpegPath)
                    {
                        UseShellExecute = false, RedirectStandardInput = true, RedirectStandardError = true,
                        CreateNoWindow = true,
                        Arguments = "-hide_banner -loglevel warning -n -f rawvideo -pixel_format rgb24 -video_size 1920x1080 -framerate 60 -i pipe:0 -vf vflip -an -c:v libx264 -preset fast -crf 16 -pix_fmt yuv420p -movflags +faststart "
                            + Quote(Path.GetFullPath(Path.Combine(job.outputDirectory, stem + ".mp4")))
                    };
                    encoder = new Process { StartInfo = start };
                    encoder.ErrorDataReceived += (_, e) => { if (e.Data != null) lock (errors) errors.AppendLine(e.Data); };
                    if (!encoder.Start()) throw new InvalidOperationException("Could not start local encoder.");
                    encoder.BeginErrorReadLine();
                }
                using (var anchors = new StreamWriter(Path.Combine(job.outputDirectory, stem + ".anchors.ndjson"), false, new UTF8Encoding(false)))
                {
                    for (int frame = 0; frame < clip.frames; frame++)
                    {
                        float n = NormalizedAt(clip, frame);
                        scene.Evaluate(n);
                        scene.SceneCamera.Render();
                        RenderTexture.active = target;
                        pixels.ReadPixels(new Rect(0, 0, 1920, 1080), 0, 0, false);
                        pixels.Apply(false, false);
                        var state = scene.GetFrameState(Mathf.RoundToInt(n * 1000000f), 1000001);
                        state.frame = frame; state.time = frame / 60f; state.normalizedTime = n;
                        anchors.WriteLine(JsonUtility.ToJson(state));
                        if (job.renderPngPreviewsOnly)
                            File.WriteAllBytes(Path.Combine(job.outputDirectory, stem + "-" + frame.ToString("D5") + ".png"), pixels.EncodeToPNG());
                        else
                        {
                            byte[] raw = pixels.GetRawTextureData();
                            encoder.StandardInput.BaseStream.Write(raw, 0, raw.Length);
                        }
                    }
                }
                if (encoder != null)
                {
                    encoder.StandardInput.Close(); encoder.WaitForExit();
                    File.WriteAllText(Path.Combine(job.outputDirectory, stem + ".encode.log"), errors.ToString());
                    if (encoder.ExitCode != 0) throw new InvalidOperationException("Capture encoder exit " + encoder.ExitCode + ": " + errors);
                }
            }
            finally
            {
                if (encoder != null) { if (!encoder.HasExited) encoder.Kill(); encoder.Dispose(); }
                scene.SceneCamera.targetTexture = null; RenderTexture.active = null;
                target.Release(); UnityEngine.Object.DestroyImmediate(target); UnityEngine.Object.DestroyImmediate(pixels);
            }
        }
        private static float NormalizedAt(Clip clip, int frame)
        {
            if (clip.keys == null || clip.keys.Length == 0)
                return Mathf.Lerp(clip.startNormalized, clip.endNormalized, clip.frames <= 1 ? 0f : frame / (float)(clip.frames - 1));
            if (frame <= clip.keys[0].frame) return clip.keys[0].normalized;
            for (int i = 1; i < clip.keys.Length; i++)
            {
                if (clip.keys[i].frame <= clip.keys[i - 1].frame) throw new ArgumentException("Capture keys must be strictly increasing.");
                if (frame <= clip.keys[i].frame)
                    return Mathf.Lerp(clip.keys[i - 1].normalized, clip.keys[i].normalized,
                        Mathf.InverseLerp(clip.keys[i - 1].frame, clip.keys[i].frame, frame));
            }
            return clip.keys[clip.keys.Length - 1].normalized;
        }
        private static string Argument(string key)
        { string[] args = Environment.GetCommandLineArgs(); for (int i = 0; i < args.Length - 1; i++) if (args[i] == key) return args[i + 1]; return null; }
        private static string Quote(string value)
        { return "\"" + value.Replace("\"", "\\\"") + "\""; }
    }
}
