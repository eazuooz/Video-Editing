#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace YamyamCoding.Shorts.SplatoonInkReadability.Editor
{
    /// <summary>
    /// Explicit batch entry point only. The parent owns launch/GPU scheduling.
    /// Absolute PCM frame numbers are retained in images and readback records.
    /// Loading this source does not build, render, encode or register callbacks.
    /// </summary>
    public static class InkReadabilityCapture
    {
        private const string Root = "Assets/VideoScenes/shorts-splatoon-ink-readability";

        [Serializable] public sealed class Cue
        {
            public string id;
            public int startFrame, endFrame;
        }
        [Serializable] public sealed class Track
        {
            public float from, to;
            public string startCueId, endCueId;
            public int startFrame = -1, endFrame = -1;
            public string ease = "linear";
        }
        [Serializable] public sealed class LabelRequest
        {
            public string id, target, textKo, textEn, role;
            public string startCueId, endCueId;
            public int startFrame = -1, endFrame = -1;
            public Vector3 localOffset;
        }
        [Serializable] public sealed class Section
        {
            public string id, visualId, stage;
            public int startFrame, endFrame;
            public Track comparison, phase;
            public string termEn, termKo, meaningKo;
            public string[] steps;
            public int activeStep;
            public LabelRequest[] labels;
        }
        [Serializable] public sealed class Job
        {
            public int schemaVersion = 1;
            public string revision, mode, expectedProjectPath, outputDirectory;
            public string scenePath = Root + "/Scenes/06-BalancedIllustration.unity";
            public bool buildIfMissing;
            public int width = 1920, height = 1080, fps = 60, totalFrames;
            public int startFrame, endFrame;
            public int[] sampleFrames;
            public bool timingVerified;
            public string pcmPath, pcmSha256, timingEvidence;
            public Cue[] cues;
            public Section[] sections;
            public bool writeJpg = true, encodeVideo;
            public int jpgQuality = 95;
            public string ffmpegPath, cancelFile;
        }
        [Serializable] public sealed class ProjectedLabel
        {
            public string id, target, textKo, textEn, role;
            public Vector3 world;
            public float x, y, u, v, depth;
            public bool inFrontAndInFrame, targetActive;
            public bool occlusionVerified = false;
        }
        [Serializable] public sealed class FrameRecord
        {
            public int frame;
            public double seconds;
            public string sectionId, visualId, stage;
            public float sectionProgress, comparisonNormalized, phaseNormalized;
            public string pictureKind = "our-implementation";
            public string pictureLabel = "우리 Unity 모형";
            public string termEn, termKo, meaningKo;
            public string[] steps;
            public int activeStep;
            public InkReadabilityDemo.State appliedState;
            public ProjectedLabel[] labelRequests;
        }
        [Serializable] public sealed class Result
        {
            public string status, revision, mode, scenePath, unity, graphicsDevice, outputDirectory;
            public int width, height, fps, firstFrame, endFrameExclusive, renderedFrames;
            public bool timingVerified, encodedVideo, videoRequested, jpgWritten;
            public bool humanReviewed = false;
            public string framesPattern = "frames/frame-%06d.jpg (absolute timeline index)";
            public string trace = "readback.ndjson (top-left pixel coordinates)";
            public string error;
        }

        private static Job job;
        private static Dictionary<string, Cue> cues;
        private static int[] frames;
        private static int cursor, renderedFrames;
        private static bool prepared, outputClaimed;
        private static Scene previousScene, loadedScene;
        private static InkReadabilityDemo demo;
        private static Camera camera;
        private static RenderTexture target;
        private static Texture2D pixels;
        private static FrameRecord pending;
        private static StreamWriter trace, encoderLog;
        private static System.Diagnostics.Process encoder;
        private static Stream encoderInput;
        private static readonly object EncoderLogLock = new object();

        // -executeMethod YamyamCoding.Shorts.SplatoonInkReadability.Editor.InkReadabilityCapture.Run
        // -inkReadabilityJob C:/.../job.json ; do not pass -quit (the update loop exits).
        public static void Run()
        {
            try
            {
                if (!Application.isBatchMode)
                    throw new InvalidOperationException("Run this finite capture in the parent's isolated batch Editor.");
                string json = File.ReadAllText(Argument("-inkReadabilityJob"));
                job = JsonUtility.FromJson<Job>(json);
                ValidateJob();
                Directory.CreateDirectory(job.outputDirectory);
                outputClaimed = true;
                if (job.writeJpg) Directory.CreateDirectory(Path.Combine(job.outputDirectory, "frames"));
                WriteNew("job-used.json", json);
                // Batch executeMethod may run before the startup scene is ready.
                // Validate the exact isolated C: project first, then initialize
                // on an Editor callback. Never apply this boot-save to D:.
                EditorApplication.delayCall += InitializeScene;
            }
            catch (Exception error) { Fail(error); }
        }

        private static void InitializeScene()
        {
            try
            {
                previousScene = SceneManager.GetActiveScene();
                AssertOtherScenesHaveNoGeometry();
                if (previousScene.IsValid() && string.IsNullOrEmpty(previousScene.path))
                {
                    if (SceneManager.sceneCount != 1) throw new InvalidOperationException("Preserve multiple unsaved startup scenes.");
                    const string generated = Root + "/Generated";
                    const string boot = generated + "/CaptureBoot.unity";
                    if (File.Exists(ProjectFile(boot)))
                    {
                        // Reuse our unchanged saved empty startup scene in this exact
                        // isolated batch project; never overwrite it on a later run.
                        previousScene = EditorSceneManager.OpenScene(boot, OpenSceneMode.Single);
                        AssertOtherScenesHaveNoGeometry();
                    }
                    else
                    {
                        if (File.Exists(ProjectFile(boot) + ".meta")) throw new IOException("Orphan boot metadata must be preserved.");
                        if (!AssetDatabase.IsValidFolder(generated)) AssetDatabase.CreateFolder(Root, "Generated");
                        if (!EditorSceneManager.SaveScene(previousScene, boot)) throw new IOException("Could not save isolated capture boot scene.");
                    }
                }
                if (!File.Exists(ProjectFile(job.scenePath)))
                {
                    if (!job.buildIfMissing) throw new FileNotFoundException("Build the scoped scene first.", job.scenePath);
                    InkReadabilityBuilder.Build();
                }
                EditorApplication.delayCall += OpenAndCapture;
            }
            catch (Exception error) { Fail(error); }
        }

        private static void OpenAndCapture()
        {
            try
            {
                if (SceneManager.GetSceneByPath(job.scenePath).isLoaded)
                    throw new InvalidOperationException("Do not capture or close an already open editing scene.");
                // Camera.Render sees loaded scenes. The isolated batch project may
                // keep an empty startup scene; reject other visible geometry rather
                // than disabling, moving, closing or saving unrelated objects.
                AssertOtherScenesHaveNoGeometry();
                loadedScene = EditorSceneManager.OpenScene(job.scenePath, OpenSceneMode.Additive);
                if (SceneManager.GetActiveScene() != loadedScene && !EditorSceneManager.SetActiveScene(loadedScene)) throw new InvalidOperationException("Capture scene is not yet active; preserve startup scene and retry after Editor initialization.");
                InkReadabilityDemo[] owners = loadedScene.GetRootGameObjects()
                    .SelectMany(g => g.GetComponentsInChildren<InkReadabilityDemo>(true)).ToArray();
                if (owners.Length != 1) throw new InvalidOperationException("Expected one saved lesson controller.");
                demo = owners[0];
                camera = demo.lessonCamera;
                if (!camera || demo.inkSurfaces == null || demo.inkSurfaces.Length != 2
                    || !demo.diver || !demo.ripple || demo.droplets == null || demo.droplets.Length == 0)
                    throw new InvalidOperationException("Saved scene references are incomplete; no synthetic replacement state is allowed.");
                foreach (Renderer surface in demo.inkSurfaces)
                    if (!surface || !surface.sharedMaterial || !surface.sharedMaterial.shader
                        || !surface.sharedMaterial.shader.isSupported || ShaderUtil.ShaderHasError(surface.sharedMaterial.shader))
                        throw new InvalidOperationException("The actual ink material shader has not imported successfully.");
                camera.enabled = false;
                camera.aspect = job.width / (float)job.height;
                camera.GetUniversalAdditionalCameraData().renderPostProcessing = false;
                demo.Apply(); // Required initialization after deserialization; not only an Inspector assumption.
                target = new RenderTexture(job.width, job.height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB)
                    {name = "InkReadability finite capture", antiAliasing = 1};
                if (!target.Create()) throw new InvalidOperationException("Render target allocation failed.");
                camera.targetTexture = target;
                pixels = new Texture2D(job.width, job.height, TextureFormat.RGB24, false, false);
                trace = new StreamWriter(new FileStream(Path.Combine(job.outputDirectory, "readback.ndjson"), FileMode.CreateNew), new UTF8Encoding(false));
                if (job.encodeVideo) StartEncoder();
                cursor = renderedFrames = 0;
                prepared = false;
                EditorApplication.update += Tick;
            }
            catch (Exception error) { Fail(error); }
        }

        private static void ValidateJob()
        {
            if (job == null || job.schemaVersion != 1 || string.IsNullOrWhiteSpace(job.revision))
                throw new ArgumentException("Missing schema/revision.");
            string actualProject = Path.GetFullPath(Path.Combine(Application.dataPath, "..")).TrimEnd('/', '\\');
            string expectedProject = FullCPath(job.expectedProjectPath).TrimEnd('/', '\\');
            if (!string.Equals(actualProject, expectedProject, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Job must name the exact isolated C: Unity project.");
            job.outputDirectory = FullCPath(job.outputDirectory).TrimEnd('/', '\\');
            if (job.outputDirectory.StartsWith(actualProject + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)
                || job.outputDirectory.Equals(actualProject, StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("Keep captures outside the isolated Unity project.");
            // The finite launcher opens its log/receipt before Unity invokes us.
            // Every image, subdirectory and earlier capture result remains protected.
            if (Directory.Exists(job.outputDirectory) && Directory.EnumerateFileSystemEntries(job.outputDirectory)
                .Any(p => Path.GetFileName(p) != "unity-editor.log" && Path.GetFileName(p) != "process.json"))
                throw new IOException("Output directory is not empty; preserve the existing run.");
            if (job.scenePath == null || !job.scenePath.StartsWith(Root + "/Scenes/", StringComparison.Ordinal)
                || !job.scenePath.EndsWith(".unity", StringComparison.Ordinal) || job.scenePath.Contains(".."))
                throw new ArgumentException("Only this lesson's saved scenes may be loaded.");
            RenderPipelineAsset pipeline = QualitySettings.renderPipeline
                ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            if (!(pipeline is UniversalRenderPipelineAsset)) throw new InvalidOperationException("Keep the selected URP settings; no global pipeline switch.");
            if (job.mode != "stills" && job.mode != "sequence") throw new ArgumentException("Mode must be stills or sequence.");
            if (job.fps != 60 || job.width < 1080 || job.height < 1080 || job.width > 3840 || job.height > 3840
                || job.width % 2 != 0 || job.height % 2 != 0) throw new ArgumentException("Use even FHD-or-larger dimensions at60fps.");
            if (job.startFrame < 0 || job.endFrame <= job.startFrame || job.endFrame > job.totalFrames)
                throw new ArgumentException("Capture interval must lie inside the PCM timeline, end exclusive.");
            if (job.mode == "sequence" && !job.timingVerified)
                throw new ArgumentException("Full sequence needs final PCM/cue timing; use stills for provisional timing.");
            if (job.timingVerified)
            {
                if (!File.Exists(job.pcmPath) || string.IsNullOrWhiteSpace(job.pcmSha256)
                    || string.IsNullOrWhiteSpace(job.timingEvidence)) throw new ArgumentException("Final timing needs PCM path/hash and evidence.");
                using (SHA256 sha = SHA256.Create())
                using (FileStream pcm = File.OpenRead(job.pcmPath))
                    if (!string.Equals(BitConverter.ToString(sha.ComputeHash(pcm)).Replace("-", ""), job.pcmSha256, StringComparison.OrdinalIgnoreCase))
                        throw new InvalidOperationException("PCM hash differs from the cue job.");
            }
            if (!job.writeJpg && !job.encodeVideo) throw new ArgumentException("Select at least one output.");
            if (job.mode == "stills" && (!job.writeJpg || job.encodeVideo)) throw new ArgumentException("Stills write JPG only.");
            if (job.jpgQuality < 80 || job.jpgQuality > 100) throw new ArgumentException("JPG quality outside80–100.");
            if (job.encodeVideo && !File.Exists(job.ffmpegPath)) throw new FileNotFoundException("Explicit ffmpeg executable required.");
            cues = new Dictionary<string, Cue>();
            foreach (Cue cue in job.cues ?? Array.Empty<Cue>())
            {
                if (string.IsNullOrWhiteSpace(cue.id) || cue.startFrame < 0 || cue.endFrame <= cue.startFrame
                    || cue.endFrame > job.totalFrames || cues.ContainsKey(cue.id)) throw new ArgumentException("Invalid/duplicate cue.");
                cues.Add(cue.id, cue);
            }
            if (job.sections == null || job.sections.Length == 0) throw new ArgumentException("Sections required.");
            int previousEnd = -1;
            var ids = new HashSet<string>();
            foreach (Section section in job.sections)
            {
                if (section == null || !ids.Add(section.id ?? "") || string.IsNullOrWhiteSpace(section.id)
                    || section.startFrame < 0 || section.endFrame <= section.startFrame || section.endFrame > job.totalFrames
                    || (previousEnd >= 0 && section.startFrame != previousEnd)) throw new ArgumentException("Sections must be ordered, unique and contiguous.");
                previousEnd = section.endFrame;
                if (section.stage != "balanced" && section.stage != "shading" && section.stage != "specular")
                    throw new ArgumentException("Unknown comparison stage: " + section.stage);
                ValidateTrack(section.comparison);
                ValidateTrack(section.phase);
                if (section.steps != null && section.steps.Length > 0 && (section.activeStep < 0 || section.activeStep >= section.steps.Length))
                    throw new ArgumentException("activeStep must index the requested step list.");
                foreach (LabelRequest label in section.labels ?? Array.Empty<LabelRequest>())
                {
                    if (!new[] {"floor", "wall", "boundary", "join", "diver", "splash"}.Contains(label.target))
                        throw new ArgumentException("Unknown label target: " + label.target);
                    if (!string.IsNullOrEmpty(label.startCueId) || label.startFrame >= 0)
                        Window(label.startCueId, label.endCueId, label.startFrame, label.endFrame, out _, out _);
                }
            }
            if (job.sections[0].startFrame > job.startFrame || job.sections[job.sections.Length - 1].endFrame < job.endFrame)
                throw new ArgumentException("Sections must cover the requested capture interval.");
            if (job.mode == "stills")
            {
                if (job.sampleFrames == null || job.sampleFrames.Length == 0) throw new ArgumentException("Stills need explicit sampleFrames.");
                frames = job.sampleFrames.OrderBy(f => f).ToArray();
                if (frames.Distinct().Count() != frames.Length || frames.Any(f => f < job.startFrame || f >= job.endFrame))
                    throw new ArgumentException("Still samples must be unique and inside the capture interval.");
            }
            else frames = Enumerable.Range(job.startFrame, job.endFrame - job.startFrame).ToArray();
        }

        private static void ValidateTrack(Track track)
        {
            if (track == null) return;
            if (float.IsNaN(track.from) || float.IsNaN(track.to) || track.from < 0 || track.from > 1 || track.to < 0 || track.to > 1)
                throw new ArgumentException("Normalized track values must be0..1.");
            if (track.ease != "linear" && track.ease != "smoothstep" && track.ease != "step") throw new ArgumentException("Unknown easing.");
            if (track.from != track.to) Window(track.startCueId, track.endCueId, track.startFrame, track.endFrame, out _, out _);
        }

        private static void Window(string startId, string endId, int directStart, int directEnd, out int start, out int end)
        {
            if (!string.IsNullOrEmpty(startId))
            {
                if (!cues.TryGetValue(startId, out Cue first) || !cues.TryGetValue(string.IsNullOrEmpty(endId) ? startId : endId, out Cue last))
                    throw new ArgumentException("Missing cue anchor: " + startId + " / " + endId);
                start = first.startFrame;
                end = last.endFrame;
            }
            else { start = directStart; end = directEnd; }
            if (start < 0 || end <= start || end > job.totalFrames) throw new ArgumentException("Invalid end-exclusive cue/track interval.");
        }

        private static float Evaluate(Track track, int frame, float fallback)
        {
            if (track == null) return fallback;
            if (track.from == track.to) return track.from;
            Window(track.startCueId, track.endCueId, track.startFrame, track.endFrame, out int start, out int end);
            float progress = track.ease == "step" ? (frame >= start ? 1 : 0)
                : Mathf.Clamp01((frame - start) / (float)Math.Max(1, end - start - 1));
            if (track.ease == "smoothstep") progress = progress * progress * (3 - 2 * progress);
            return Mathf.Lerp(track.from, track.to, progress);
        }

        private static FrameRecord ApplyFrame(int frame)
        {
            Section section = job.sections.First(s => frame >= s.startFrame && frame < s.endFrame);
            float comparison = Evaluate(section.comparison, frame, 0);
            float phase = Evaluate(section.phase, frame, 0.62f);
            if (section.stage == "shading") demo.SetShadingComparison(comparison, phase);
            else if (section.stage == "specular") demo.SetSpecularComparison(comparison, phase);
            else demo.SetBalancedIllustration(phase);
            var labels = new List<ProjectedLabel>();
            foreach (LabelRequest request in section.labels ?? Array.Empty<LabelRequest>())
            {
                if (!string.IsNullOrEmpty(request.startCueId) || request.startFrame >= 0)
                {
                    Window(request.startCueId, request.endCueId, request.startFrame, request.endFrame, out int start, out int end);
                    if (frame < start || frame >= end) continue;
                }
                labels.Add(Project(request));
            }
            return new FrameRecord {frame = frame, seconds = frame / (double)job.fps,
                sectionId = section.id, visualId = string.IsNullOrEmpty(section.visualId) ? section.id : section.visualId,
                stage = section.stage, sectionProgress = Mathf.Clamp01((frame - section.startFrame) / (float)Math.Max(1, section.endFrame - section.startFrame - 1)),
                comparisonNormalized = comparison, phaseNormalized = phase, appliedState = demo.ReadState(),
                termEn = section.termEn, termKo = section.termKo, meaningKo = section.meaningKo,
                steps = section.steps, activeStep = section.activeStep, labelRequests = labels.ToArray()};
        }

        private static ProjectedLabel Project(LabelRequest request)
        {
            Vector3 local;
            bool active = true;
            switch (request.target)
            {
                case "floor": local = new Vector3(-1.2f, 0.1f, -0.6f); break;
                case "wall": local = new Vector3(0.8f, 1.4f, 2.93f); break;
                case "join": local = new Vector3(0, 0.1f, 2.93f); break;
                case "boundary":
                    float uvY = 3f / 9.2f;
                    float boundary = 0.5f + 0.10f * Mathf.Sin(uvY * 17) + 0.035f * Mathf.Sin(uvY * 43);
                    local = new Vector3((boundary - 0.5f) * 6, 0.1f, 0); break;
                case "diver": local = demo.diver.localPosition + new Vector3(0, 0.9f, 0); active = local.y > 0.1f; break;
                default: local = new Vector3(demo.diverStart.x, 0.12f, demo.diverStart.z); active = demo.ripple.gameObject.activeInHierarchy; break;
            }
            Vector3 world = demo.transform.TransformPoint(local + request.localOffset);
            Vector3 point = camera.WorldToViewportPoint(world);
            return new ProjectedLabel {id = request.id, target = request.target, textKo = request.textKo,
                textEn = request.textEn, role = request.role, world = world, x = point.x * job.width,
                y = (1 - point.y) * job.height, u = point.x, v = 1 - point.y, depth = point.z,
                inFrontAndInFrame = point.z > 0 && point.x >= 0 && point.x <= 1 && point.y >= 0 && point.y <= 1,
                targetActive = active};
        }

        private static void Tick()
        {
            try
            {
                if (!string.IsNullOrEmpty(job.cancelFile) && File.Exists(job.cancelFile)) throw new OperationCanceledException("Parent cancel marker found.");
                int frame = frames[cursor];
                if (!prepared)
                {
                    pending = ApplyFrame(frame);
                    prepared = true;
                    EditorApplication.QueuePlayerLoopUpdate();
                    return;
                }
                RenderTexture previous = RenderTexture.active;
                try
                {
                    camera.Render();
                    RenderTexture.active = target;
                    pixels.ReadPixels(new Rect(0, 0, job.width, job.height), 0, 0, false);
                    pixels.Apply(false, false);
                }
                finally { RenderTexture.active = previous; }
                if (job.writeJpg)
                {
                    string path = Path.Combine(job.outputDirectory, "frames", "frame-" + frame.ToString("D6") + ".jpg");
                    using (FileStream output = new FileStream(path, FileMode.CreateNew))
                    { byte[] jpg = pixels.EncodeToJPG(job.jpgQuality); output.Write(jpg, 0, jpg.Length); }
                }
                if (encoderInput != null)
                {
                    byte[] bytes = pixels.GetRawTextureData();
                    encoderInput.Write(bytes, 0, bytes.Length);
                }
                trace.WriteLine(JsonUtility.ToJson(pending));
                renderedFrames++;
                cursor++;
                prepared = false;
                if (renderedFrames % 120 == 0) { trace.Flush(); Debug.Log("INK_READABILITY_FRAME " + frame + " / " + job.endFrame); }
                if (cursor == frames.Length) Complete();
            }
            catch (Exception error) { Fail(error); }
        }

        private static void StartEncoder()
        {
            string movie = Path.Combine(job.outputDirectory, "unity-explanation.mp4");
            encoderLog = new StreamWriter(new FileStream(Path.Combine(job.outputDirectory, "ffmpeg.log"), FileMode.CreateNew), new UTF8Encoding(false));
            string arguments = "-hide_banner -loglevel warning -n -f rawvideo -pixel_format rgb24 -video_size "
                + job.width + "x" + job.height + " -framerate " + job.fps
                + " -i pipe:0 -vf vflip -an -frames:v " + frames.Length
                + " -c:v libx264 -threads 4 -preset fast -crf 16 -pix_fmt yuv420p"
                + " -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart " + Quote(movie);
            encoder = new System.Diagnostics.Process {StartInfo = new System.Diagnostics.ProcessStartInfo(job.ffmpegPath, arguments)
                {UseShellExecute = false, CreateNoWindow = true, RedirectStandardInput = true, RedirectStandardError = true}};
            encoder.ErrorDataReceived += (sender, args) =>
            {
                if (args.Data == null) return;
                lock (EncoderLogLock)
                    if (encoderLog != null) { encoderLog.WriteLine(args.Data); encoderLog.Flush(); }
            };
            if (!encoder.Start()) throw new IOException("Could not start the explicitly configured encoder.");
            encoder.BeginErrorReadLine();
            encoderInput = encoder.StandardInput.BaseStream;
        }

        private static void Complete()
        {
            EditorApplication.update -= Tick;
            trace?.Dispose(); trace = null;
            encoderInput?.Dispose(); encoderInput = null;
            if (encoder != null)
            {
                if (!encoder.WaitForExit(60000)) throw new TimeoutException("Owned encoder did not finish.");
                encoder.WaitForExit(); // Drain the already-completed asynchronous stderr reader.
                if (encoder.ExitCode != 0) throw new IOException("Owned encoder exited " + encoder.ExitCode);
            }
            Result result = MakeResult("render-completed-not-reviewed", null);
            Cleanup();
            WriteNew("success.json", JsonUtility.ToJson(result, true));
            EditorApplication.Exit(0);
        }

        private static void Fail(Exception error)
        {
            EditorApplication.delayCall -= InitializeScene;
            EditorApplication.delayCall -= OpenAndCapture;
            EditorApplication.update -= Tick;
            Debug.LogException(error);
            try { Cleanup(); } catch (Exception cleanupError) { Debug.LogException(cleanupError); }
            if (outputClaimed)
                try { WriteNew("failure.json", JsonUtility.ToJson(MakeResult("failed-partial-output-preserved", error.ToString()), true)); }
                catch (Exception reportError) { Debug.LogException(reportError); }
            EditorApplication.Exit(1);
        }

        private static void Cleanup()
        {
            trace?.Dispose(); trace = null;
            encoderInput?.Dispose(); encoderInput = null;
            if (encoder != null)
            {
                try { if (!encoder.HasExited) { encoder.Kill(); encoder.WaitForExit(5000); } } catch (InvalidOperationException) { }
                encoder.Dispose(); encoder = null;
            }
            lock (EncoderLogLock) { encoderLog?.Dispose(); encoderLog = null; }
            if (camera) camera.targetTexture = null;
            if (target) { target.Release(); Object.DestroyImmediate(target); target = null; }
            if (pixels) { Object.DestroyImmediate(pixels); pixels = null; }
            if (loadedScene.IsValid() && loadedScene.isLoaded) EditorSceneManager.CloseScene(loadedScene, true);
            if (previousScene.IsValid() && previousScene.isLoaded && SceneManager.GetActiveScene() != previousScene) EditorSceneManager.SetActiveScene(previousScene);
        }

        private static Result MakeResult(string status, string error)
        {
            return new Result {status = status, error = error, revision = job?.revision, mode = job?.mode,
                scenePath = job?.scenePath, unity = Application.unityVersion, graphicsDevice = SystemInfo.graphicsDeviceName,
                outputDirectory = job?.outputDirectory, width = job?.width ?? 0, height = job?.height ?? 0, fps = job?.fps ?? 0,
                firstFrame = frames != null && frames.Length > 0 ? frames[0] : 0,
                endFrameExclusive = job?.endFrame ?? 0, renderedFrames = renderedFrames,
                timingVerified = job != null && job.timingVerified, videoRequested = job != null && job.encodeVideo,
                encodedVideo = status == "render-completed-not-reviewed" && job != null && job.encodeVideo,
                jpgWritten = renderedFrames > 0 && job != null && job.writeJpg,
                framesPattern = job != null && job.writeJpg ? "frames/frame-%06d.jpg (absolute timeline index)" : null};
        }

        private static void AssertOtherScenesHaveNoGeometry()
        {
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                Scene scene = SceneManager.GetSceneAt(i);
                if (!scene.isLoaded) continue;
                foreach (GameObject root in scene.GetRootGameObjects())
                    if (root.GetComponentsInChildren<Renderer>(false).Any(r => r.enabled)
                        || root.GetComponentsInChildren<Terrain>(false).Any(t => t.enabled))
                        throw new InvalidOperationException("Isolated capture needs an empty startup scene; preserve other open geometry.");
            }
        }
        private static string FullCPath(string value)
        {
            if (string.IsNullOrWhiteSpace(value) || !Path.IsPathRooted(value) || value.IndexOfAny(new[] {'"', '\r', '\n'}) >= 0)
                throw new ArgumentException("Expected an explicit absolute C: path.");
            string full = Path.GetFullPath(value);
            if (!string.Equals(Path.GetPathRoot(full), "C:\\", StringComparison.OrdinalIgnoreCase)
                || string.Equals(full.TrimEnd('\\', '/'), "C:", StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("Use an isolated C: subdirectory, never D: or a drive root.");
            return full;
        }
        private static string ProjectFile(string path) { return Path.GetFullPath(Path.Combine(Application.dataPath, "..", path)); }
        private static string Quote(string path) { return "\"" + path + "\""; }
        private static void WriteNew(string name, string text)
        {
            using (var writer = new StreamWriter(new FileStream(Path.Combine(job.outputDirectory, name), FileMode.CreateNew), new UTF8Encoding(false))) writer.Write(text);
        }
        private static string Argument(string name)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length - 1; i++) if (args[i] == name) return args[i + 1];
            throw new ArgumentException("Missing " + name);
        }
    }
}
#endif
