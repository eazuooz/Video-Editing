using System;
using System.IO;
using System.Collections.Generic;
using System.Diagnostics;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;
namespace Yamyam.OriginalTechTwelve.CaptureStorageV2 {
    // This changes storage only. Model states, render targets and frame order
    // remain owned by each independently compiled lesson capture.
    public sealed class LosslessFrameSink : IDisposable {
        [Serializable]public class PixelFrame{public int frame;public string rgbSHA256;}
        [Serializable]public class Manifest{
            public string storage="lossless-libx264rgb-crf0",pixelFormat="RGB24",orientation="top-left row-major",video="frames-lossless-rgb.mp4";
            public int width,height,fps,expectedFrames,encoderExitCode;public bool complete;
            public List<PixelFrame>frames=new List<PixelFrame>();
        }
        readonly string folder;readonly int width,height;readonly byte[] upright;
        readonly Process encoder;readonly Stream input;readonly StringBuilder errors=new StringBuilder();readonly SHA256 hasher=SHA256.Create();
        readonly Manifest record;bool closed;
        static string Quote(string s){if(s.IndexOfAny(new[]{'"','\r','\n'})>=0)throw new ArgumentException("Invalid local encoder path");return "\""+s+"\"";}
        public LosslessFrameSink(string folder,string ffmpeg,int width,int height,int fps,int expectedFrames){
            this.folder=Path.GetFullPath(folder);this.width=width;this.height=height;Directory.CreateDirectory(folder);
            string video=Path.Combine(folder,"frames-lossless-rgb.mp4");if(File.Exists(video)||File.Exists(Path.Combine(folder,"streamed-capture.json")))throw new Exception("Preserve existing encoded capture");
            if(!File.Exists(ffmpeg)||width!=1080||height!=1080||fps!=60||(expectedFrames!=32&&expectedFrames!=720))throw new Exception("Exact local encoder and capture contract required");
            upright=new byte[checked(width*height*3)];record=new Manifest{width=width,height=height,fps=fps,expectedFrames=expectedFrames};
            var start=new ProcessStartInfo{FileName=ffmpeg,UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true,RedirectStandardError=true,
                Arguments="-hide_banner -loglevel error -nostdin -threads 2 -f rawvideo -pixel_format rgb24 -video_size "+width+"x"+height+" -framerate "+fps+" -i pipe:0 -an -c:v libx264rgb -crf 0 -preset fast -threads 2 -g 60 -pix_fmt rgb24 -color_range pc -video_track_timescale 15360 -movflags +faststart -n "+Quote(video)};
            encoder=new Process{StartInfo=start};encoder.ErrorDataReceived+=(sender,args)=>{if(args.Data!=null)lock(errors)errors.AppendLine(args.Data);};
            if(!encoder.Start())throw new Exception("Could not start this capture's local lossless encoder");encoder.BeginErrorReadLine();input=encoder.StandardInput.BaseStream;
        }
        public void Write(Texture2D pixels,int frame){
            if(closed||frame!=record.frames.Count||frame>=record.expectedFrames||pixels.width!=width||pixels.height!=height||pixels.format!=TextureFormat.RGB24)throw new Exception("Unexpected pixel frame/order/format");
            byte[] bottomUp=pixels.GetRawTextureData();if(bottomUp.Length!=upright.Length)throw new Exception("Unexpected native RGB byte count");
            int stride=width*3;for(int row=0;row<height;row++)Buffer.BlockCopy(bottomUp,(height-1-row)*stride,upright,row*stride,stride);
            string digest=BitConverter.ToString(hasher.ComputeHash(upright)).Replace("-","").ToLowerInvariant();
            input.Write(upright,0,upright.Length);record.frames.Add(new PixelFrame{frame=frame,rgbSHA256=digest});
        }
        public void Close(){
            if(closed)return;closed=true;input.Close();
            // Only this instance's own encoder handle is terminated on failure.
            // It is never a PID selected from another application or project.
            bool ended=encoder.WaitForExit(120000);if(!ended){encoder.Kill();encoder.WaitForExit();}
            encoder.WaitForExit();record.encoderExitCode=encoder.ExitCode;record.complete=ended&&encoder.ExitCode==0&&record.frames.Count==record.expectedFrames;
            File.WriteAllText(Path.Combine(folder,"encoder-errors.log"),errors.ToString());File.WriteAllText(Path.Combine(folder,"streamed-capture.json"),JsonUtility.ToJson(record,true));
            encoder.Dispose();hasher.Dispose();if(!record.complete)throw new Exception("Lossless capture incomplete; preserve this attempt for review");
        }
        public void Dispose(){Close();}
    }
}
