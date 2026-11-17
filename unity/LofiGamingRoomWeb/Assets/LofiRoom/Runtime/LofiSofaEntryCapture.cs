#if UNITY_EDITOR
using System;
using System.Collections;
using System.Diagnostics;
using System.IO;
using UnityEditor;
using UnityEngine;
using Unity.Pipeline.Commands;
using Yamyam.LofiRoom;

public sealed class LofiSofaEntryCapture:MonoBehaviour
{
    const int Width=1920,Height=1080,Fps=60,Frames=1440;
    static string Folder=>Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/living-room-v11/sofa-entry");
    Process encoder;RenderTexture target;Texture2D pixels;
    public int frame;public string ffmpeg;
    [CliCommand("lofi_sofa_entry_record","Record approach, seated transition, feet-to-table and book raise at FHD60",MainThreadRequired=true)]
    public static string Begin(string ffmpeg)
    {
        if(!EditorApplication.isPlaying)throw new Exception("Enter Play mode first");
        if(FindAnyObjectByType<LofiSofaEntryCapture>())throw new Exception("Capture already active");
        new GameObject("Native sofa entry capture").AddComponent<LofiSofaEntryCapture>().ffmpeg=ffmpeg;return Folder;
    }
    IEnumerator Start()
    {
        Directory.CreateDirectory(Folder);Time.captureDeltaTime=1f/Fps;
        target=new RenderTexture(Width,Height,24,RenderTextureFormat.ARGB32);pixels=new Texture2D(Width,Height,TextureFormat.RGB24,false);
        var process=new ProcessStartInfo(ffmpeg,"-hide_banner -loglevel error -y -f rawvideo -pixel_format rgb24 -video_size 1920x1080 -framerate 60 -i pipe:0 -vf vflip -an -c:v h264_nvenc -preset p5 -cq 19 -pix_fmt yuv420p -movflags +faststart \""+Path.Combine(Folder,"unity-native-clean.mp4")+"\"");
        process.UseShellExecute=false;process.CreateNoWindow=true;process.RedirectStandardInput=true;process.RedirectStandardError=true;encoder=Process.Start(process);
        var s=FindAnyObjectByType<LofiRoomSample>();s.showControls=false;s.CameraRoom();s.SetNight(true);s.music.Play();s.music.volume=0;if(s.hearth)s.hearth.crackle.volume=0;s.rain.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);
        s.actor.transform.SetPositionAndRotation(new Vector3(.65f,s.groundY,-1.95f),Quaternion.Euler(0,145,0));
        try
        {
            for(frame=0;frame<Frames;frame++)
            {
                if(frame==0)s.ReadBook();
                if(frame==360){var view=new Vector3(2.2f,1.8f,-3.1f);s.roomCamera.transform.SetPositionAndRotation(view,Quaternion.LookRotation(new Vector3(-.52f,.8f,-.75f)-view));s.roomCamera.orthographicSize=1.0f;}
                yield return null;
                var camera=s.roomCamera;var previous=camera.targetTexture;var active=RenderTexture.active;
                camera.targetTexture=target;camera.Render();RenderTexture.active=target;
                pixels.ReadPixels(new Rect(0,0,Width,Height),0,0,false);pixels.Apply(false);
                encoder.StandardInput.BaseStream.Write(pixels.GetRawTextureData<byte>().ToArray());
                camera.targetTexture=previous;RenderTexture.active=active;
                if(frame%120==0)File.WriteAllText(Path.Combine(Folder,"capture-progress.json"),"{\"frame\":"+frame+",\"total\":"+Frames+"}");
            }
            encoder.StandardInput.Close();encoder.WaitForExit();
            File.WriteAllText(Path.Combine(Folder,"capture-result.json"),"{\"frames\":"+frame+",\"width\":1920,\"height\":1080,\"fps\":60,\"exitCode\":"+encoder.ExitCode+"}");
        }
        finally
        {
            Time.captureDeltaTime=0;s.showControls=true;s.CameraRoom();
            if(encoder!=null && !encoder.HasExited){encoder.StandardInput.Close();encoder.WaitForExit();}
            if(target)Destroy(target);if(pixels)Destroy(pixels);Destroy(gameObject);
        }
    }
}
#endif
