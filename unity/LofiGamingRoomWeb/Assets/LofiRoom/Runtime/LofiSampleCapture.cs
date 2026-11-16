#if UNITY_EDITOR
using System;
using System.Collections;
using System.Diagnostics;
using System.IO;
using UnityEngine;
using Unity.Pipeline.Commands;
using UnityEditor;

public sealed class LofiSampleCapture : MonoBehaviour
{
    const int Width=1920,Height=1080,Fps=60,Frames=2160;
    static string Folder=>Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/unity-sample-v1");
    Process encoder;
    RenderTexture target;
    Texture2D pixels;
    public int frame;
    public string ffmpeg;

    [CliCommand("lofi_record", "Record a native 1080p60 camera sample with imported Tripo animations", MainThreadRequired=true)]
    public static string Begin(string ffmpeg)
    {
        if(!EditorApplication.isPlaying)throw new Exception("Enter Play mode first");
        if(FindAnyObjectByType<LofiSampleCapture>())throw new Exception("Capture already active");
        var capture=new GameObject("Lofi native capture").AddComponent<LofiSampleCapture>();capture.ffmpeg=ffmpeg;
        return Folder;
    }

    IEnumerator Start()
    {
        Directory.CreateDirectory(Folder);
        Time.captureDeltaTime=1f/Fps;
        target=new RenderTexture(Width,Height,24,RenderTextureFormat.ARGB32);
        pixels=new Texture2D(Width,Height,TextureFormat.RGB24,false);
        var start=new ProcessStartInfo(ffmpeg,"-hide_banner -loglevel error -y -f rawvideo -pixel_format rgb24 -video_size 1920x1080 -framerate 60 -i pipe:0 -vf vflip -an -c:v h264_nvenc -preset p5 -cq 19 -pix_fmt yuv420p -movflags +faststart \""+Path.Combine(Folder,"unity-native-clean.mp4")+"\"");
        start.UseShellExecute=false;start.CreateNoWindow=true;start.RedirectStandardInput=true;start.RedirectStandardError=true;
        encoder=Process.Start(start);
        var sample=FindAnyObjectByType<Yamyam.LofiRoom.LofiRoomSample>();
        sample.Idle();sample.showControls=false;sample.SetNight(true);sample.CameraRoom();
        sample.actor.transform.SetPositionAndRotation(new Vector3(-.8f,sample.groundY,-.8f),Quaternion.Euler(0,145,0));
        try
        {
            for(frame=0;frame<Frames;frame++)
            {
                if(frame==300)sample.Walk();
                if(frame==1020){sample.Idle();sample.actor.transform.SetPositionAndRotation(new Vector3(-.8f,sample.groundY,-.8f),Quaternion.Euler(0,145,0));}
                if(frame>=1020 && frame<1440){var p=sample.actor.transform.position+new Vector3(1.7f,1.45f,-2.7f);sample.roomCamera.transform.SetPositionAndRotation(p,Quaternion.LookRotation(sample.actor.transform.position+Vector3.up*.95f-p));sample.roomCamera.orthographicSize=1.32f;}
                if(frame==1440){sample.roomCamera.transform.SetPositionAndRotation(new Vector3(-.55f,1.3f,.75f),Quaternion.LookRotation(new Vector3(-.02f,.94f,1.2f)-new Vector3(-.55f,1.3f,.75f)));sample.roomCamera.orthographicSize=.34f;}
                if(frame==1740){sample.CameraRoom();sample.SetNight(false);}
                if(frame==1920)sample.SetNight(true);
                // EndOfFrame is not emitted by Unity's batch-mode Editor.
                // Each resume follows one completed native animation frame.
                yield return null;
                var cam=sample.roomCamera;var previous=cam.targetTexture;var active=RenderTexture.active;
                cam.targetTexture=target;cam.Render();RenderTexture.active=target;
                pixels.ReadPixels(new Rect(0,0,Width,Height),0,0,false);pixels.Apply(false);
                var raw=pixels.GetRawTextureData<byte>();var bytes=raw.ToArray();encoder.StandardInput.BaseStream.Write(bytes,0,bytes.Length);
                cam.targetTexture=previous;RenderTexture.active=active;
                if(frame%120==0)File.WriteAllText(Path.Combine(Folder,"capture-progress.json"),"{\"frame\":"+frame+",\"total\":"+Frames+"}");
            }
            encoder.StandardInput.Close();encoder.WaitForExit();
            string err=encoder.StandardError.ReadToEnd();
            File.WriteAllText(Path.Combine(Folder,"capture-result.json"),"{\"frames\":"+frame+",\"width\":1920,\"height\":1080,\"fps\":60,\"exitCode\":"+encoder.ExitCode+"}");
            if(encoder.ExitCode!=0)UnityEngine.Debug.LogError(err);
        }
        finally
        {
            Time.captureDeltaTime=0;sample.showControls=true;sample.CameraRoom();
            if(encoder!=null && !encoder.HasExited){encoder.StandardInput.Close();encoder.WaitForExit();}
            if(target)Destroy(target);if(pixels)Destroy(pixels);Destroy(gameObject);
        }
    }
}
#endif
