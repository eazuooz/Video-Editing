"""Derive storage-only capture changes; preserve every original model/source.

The full render is still720 states/view at60fps. A32-state codec smoke capture
checks the actual Unity→RGB→encoder route before a full capture is allowed.
"""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;OUT=HERE/'native-stream-storage-v2'
CASES={
 'lockon':('native-source-v1','LockOnCapture.cs'),
 'camera':('camera-source-v1','CameraCapture.cs'),
 'sand':('sand-source-v1','SandCapture.cs'),
 'placement':('placement-source-v1','PlacementCapture.cs'),
 'temporal':('temporal-source-v1','TemporalCapture.cs'),
 'remaining-seven':('remaining-seven-source-v1','RemainingCapture.cs'),
}
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
    receipt=OUT/'source-derivation.json';assert not receipt.exists();rows=[]
    for name,(folder,filename)in CASES.items():
        source=HERE/folder/'Editor'/filename;s=source.read_text(encoding='utf8')
        assert s.count('public string output,fingerprint,mode;')==1 and s.count('static Job job;')==1
        s='using Yamyam.OriginalTechTwelve.CaptureStorageV2;\n'+s
        s=s.replace('public string output,fingerprint,mode;','public string output,fingerprint,mode,ffmpeg;public int frameLimit;')
        s=s.replace('static Job job;','static Job job;static int Limit{get{return job.frameLimit>0?job.frameLimit:Frames;}}'+('static LosslessFrameSink[] sinks;'if name=='temporal'else'static LosslessFrameSink sink;'))
        s=s.replace('?Frames:Preview.Length','?Limit:Preview.Length').replace('++index<Frames','++index<Limit')
        if name=='temporal':
            create='Directory.CreateDirectory(Path.Combine(job.output,demo.mode,traces[i].camera));'
            assert s.count(create)==1;s=s.replace('targets=new RenderTexture[2];traces=new Trace[2];','targets=new RenderTexture[2];traces=new Trace[2];sinks=new LosslessFrameSink[2];')
            s=s.replace(create,create+'if(job.mode=="full")sinks[i]=new LosslessFrameSink(Path.Combine(job.output,demo.mode,traces[i].camera),job.ffmpeg,Size,Size,Fps,Limit);')
            write='File.WriteAllBytes(Path.Combine(job.output,demo.mode,traces[c].camera,$"{index:D5}.png"),pixels.EncodeToPNG());'
            assert s.count(write)==1;s=s.replace(write,'if(job.mode=="full"){sinks[c].Write(pixels,index);if(Array.IndexOf(Preview,index)>=0||index==Limit-1)File.WriteAllBytes(Path.Combine(job.output,demo.mode,traces[c].camera,$"reference-{index:D5}.png"),pixels.EncodeToPNG());}else '+write)
            s=s.replace('if(++index<Limit)return;foreach(var trace in traces)', 'if(++index<Limit)return;if(sinks!=null)foreach(var sink in sinks)if(sink!=null)sink.Close();foreach(var trace in traces)')
            s=s.replace('\\"renderedFramesPerCamera\\":720,','\\"renderedFramesPerCamera\\":"+Limit+",')
            s=s.replace('Advance all720 states and both independent camera histories; only','Advance every requested state and both camera histories; only')
            cleanup='if(sinks!=null)foreach(var sink in sinks)if(sink!=null)try{sink.Close();}catch(Exception){}'
        else:
            directory='Path.Combine(job.output,demo.topic,demo.mode,trace.camera)'if name=='remaining-seven'else'Path.Combine(job.output,demo.mode,trace.camera)'
            create='Directory.CreateDirectory('+directory+');';assert s.count(create)==1;s=s.replace(create,create+'if(job.mode=="full")sink=new LosslessFrameSink('+directory+',job.ffmpeg,Size,Size,Fps,Limit);')
            token='frame'if name=='remaining-seven'else'f'
            write='File.WriteAllBytes('+directory[:-1]+',$"{'+token+':D5}.png"),pixels.EncodeToPNG());';assert s.count(write)==1
            replacement='if(job.mode=="full"){sink.Write(pixels,'+token+');if(Array.IndexOf(Preview,'+token+')>=0||'+token+'==Limit-1)File.WriteAllBytes('+directory[:-1]+',$"reference-{'+token+':D5}.png"),pixels.EncodeToPNG());}else '+write
            s=s.replace(write,replacement)
            tracewrite='File.WriteAllText('+directory[:-1]+',"trace.json"),JsonUtility.ToJson(trace,true));';assert s.count(tracewrite)==1;s=s.replace(tracewrite,'if(sink!=null){sink.Close();sink=null;}'+tracewrite)
            cleanup='if(sink!=null)try{sink.Close();}catch(Exception){}'
        tickcatch='catch(Exception e){EditorApplication.update-=Tick;Debug.LogException(e);EditorApplication.Exit(1);}'
        assert s.count(tickcatch)==1;s=s.replace(tickcatch,'catch(Exception e){'+cleanup+'EditorApplication.update-=Tick;Debug.LogException(e);EditorApplication.Exit(1);}')
        target=OUT/name/'Editor'/filename;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);target.write_text(s,encoding='utf8');rows.append(dict(case=name,original=pin(source),derived=pin(target),scope='Storage transport and explicit smoke frame budget only; geometry/model/material/camera definitions unchanged'))
    receipt.write_text(json.dumps(dict(sourceDerivations=rows,storageSource=pin(OUT/'LosslessFrameSink.cs'),originalFilesModified=False,fullFrameCount=720,smokeFrameCount=32,requestedFps=60,losslessPixelsStillRequireActualUnityRoundTrip=True),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Derived six storage-only capture sources; originals preserved')
if __name__=='__main__':main()
