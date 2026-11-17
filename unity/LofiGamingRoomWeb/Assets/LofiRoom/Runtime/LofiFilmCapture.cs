#if UNITY_EDITOR
using System;
using System.Collections;
using System.Diagnostics;
using System.IO;
using UnityEditor;
using UnityEngine;
using Unity.Pipeline.Commands;
using Yamyam.LofiRoom;

public sealed class LofiFilmCapture:MonoBehaviour
{
    const int Width=1920,Height=1080,Fps=60,Frames=2400;
    static string Folder=>Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/final-activities-v7");
    Process encoder;RenderTexture target;Texture2D pixels;
    public int frame;public string ffmpeg;
    [CliCommand("lofi_film_record","Record the actual chair, reading, hearth and record-player review at FHD60",MainThreadRequired=true)]
    public static string Begin(string ffmpeg)
    {
        if(!EditorApplication.isPlaying)throw new Exception("Enter Play mode first");
        if(FindAnyObjectByType<LofiFilmCapture>())throw new Exception("Capture already active");
        new GameObject("Native hearth review capture").AddComponent<LofiFilmCapture>().ffmpeg=ffmpeg;return Folder;
    }
    IEnumerator Start()
    {
        Directory.CreateDirectory(Folder);Time.captureDeltaTime=1f/Fps;
        target=new RenderTexture(Width,Height,24,RenderTextureFormat.ARGB32);pixels=new Texture2D(Width,Height,TextureFormat.RGB24,false);
        var process=new ProcessStartInfo(ffmpeg,"-hide_banner -loglevel error -y -f rawvideo -pixel_format rgb24 -video_size 1920x1080 -framerate 60 -i pipe:0 -vf vflip -an -c:v h264_nvenc -preset p5 -cq 19 -pix_fmt yuv420p -movflags +faststart \""+Path.Combine(Folder,"unity-native-clean.mp4")+"\"");
        process.UseShellExecute=false;process.CreateNoWindow=true;process.RedirectStandardInput=true;process.RedirectStandardError=true;encoder=Process.Start(process);
        var s=FindAnyObjectByType<LofiRoomSample>();s.showControls=false;s.CameraRoom();s.SetNight(true);s.music.Play();s.rain.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);
        s.actor.transform.SetPositionAndRotation(new Vector3(-.8f,s.groundY,-.8f),Quaternion.Euler(0,145,0));
        try
        {
            for(frame=0;frame<Frames;frame++)
            {
                if(frame==0)s.activities.Request("computer");
                if(frame==480){Vector3 p=new(3.05f,1.75f,.30f);s.roomCamera.transform.SetPositionAndRotation(p,Quaternion.LookRotation(new Vector3(1,.94f,1.18f)-p));s.roomCamera.orthographicSize=1.02f;}
                if(frame==600)s.activities.Request("read");
                if(frame==720){Vector3 p=new(3.1f,1.8f,.5f);s.roomCamera.transform.SetPositionAndRotation(p,Quaternion.LookRotation(new Vector3(1,1.0f,1.05f)-p));s.roomCamera.orthographicSize=.86f;}
                if(frame==1260){s.CameraRoom();s.activities.Request("idle");}
                if(frame==1560){Vector3 p=new(-.55f,1.15f,-1.3f);s.roomCamera.transform.SetPositionAndRotation(p,Quaternion.LookRotation(new Vector3(-2.80f,.75f,.30f)-p));s.roomCamera.orthographicSize=1.02f;}
                if(frame==1980){Vector3 p=new(-.25f,1.4f,.35f);s.roomCamera.transform.SetPositionAndRotation(p,Quaternion.LookRotation(new Vector3(-1.8f,.77f,1.86f)-p));s.roomCamera.orthographicSize=.66f;}
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
