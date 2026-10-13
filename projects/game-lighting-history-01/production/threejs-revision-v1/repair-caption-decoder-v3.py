"""Repair caption patches with verified FFmpeg7.1 decoding and no filter reinitialization.
Retain all scene assets, clean output, native closed GOPs and audio unchanged.
"""
import importlib.util, pathlib, os, sys, shutil
from fractions import Fraction
spec=importlib.util.spec_from_file_location('pair',pathlib.Path(__file__).with_name('assemble-pair.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R,P,BASE,OLD=m.R,m.P,m.BASE,m.OLD
rd,write,sha,now=m.rd,m.write,m.sha,m.now
av,psutil,subprocess,hashlib=m.av,m.psutil,m.subprocess,m.hashlib
SRC=P/'production/local/threejs-revision-v1/pair-caption-safe-v2'
OUT=SRC.parent/'pair-caption-decoder-v3'
FF='C:/Users/eazuo/miniconda3/envs/renderformer/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
def main():
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['rendererRevision']['privateUploadAuthorized']
 assert not OUT.exists();OUT.mkdir()
 prior=rd(SRC/'execution.json');assert prior['exitCode']==0
 timeline=rd(SRC/'plan.json');write(OUT/'plan.json',timeline)
 assert sha(SRC/'clean.mp4')==prior['outputs']['clean']['sha256']
 os.link(SRC/'clean.mp4',OUT/'clean.mp4')
 state={**prior,'status':'running','pid':os.getpid(),'createTime':psutil.Process().create_time(),'command':psutil.Process().cmdline(),'startedAt':now(),'active':None,'outputs':{},'steps':[],'exitCode':None,'allFinalPixelsApproved':False,'repairReason':'FFmpeg March2024 decoder corrupts glyphs; filter reinitialization at color/SAR transitions loses buffered frames. Use7.1, disable reinit, explicit trim and integer N timebase.','retainedCleanSha256':prior['outputs']['clean']['sha256']}
 def save():write(OUT/'execution.json',state)
 def run(label,args):
  log=OUT/(label+'.log');state['active']={'label':label,'command':args,'log':log.relative_to(R).as_posix()};save()
  with log.open('w',encoding='utf8') as f:
   child=subprocess.Popen(args,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);state['active']['pid']=child.pid;save();rc=child.wait()
  state['steps'].append({'label':label,'exitCode':rc});save();assert rc==0,(label,rc)
 try:
  ranges=prior['captionPatchRanges'];patches=[]
  ass=(BASE/'captions.ko.ass').relative_to(R).as_posix();fonts=(BASE/'fonts').relative_to(R).as_posix()
  for i,(a,z) in enumerate(ranges):
   file=OUT/f'caption-patch-{i}.mp4'
   if i==2:
    os.link(SRC/'diagnostic-71-patch-2.mp4',file);state['steps'].append({'label':file.stem,'exitCode':0,'reusedDirectlyReviewedDiagnostic':True});save()
   else:
    filt=f"[0:v]trim=end_frame={z-a},setpts=N/(60*TB)+{a}/(60*TB),ass='{ass}':fontsdir='{fonts}',setpts=PTS-STARTPTS,setsar=0,setparams=range=unspecified:color_primaries=unknown:color_trc=unknown:colorspace=unknown[out]"
    run(file.stem,[FF,'-v','warning','-nostdin','-n','-threads','2','-reinit_filter','0','-ss',f'{a/60:.9f}','-i',str(OUT/'clean.mp4'),'-filter_complex_threads','2','-filter_complex',filt,'-map','[out]','-an','-frames:v',str(z-a),'-r','60','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(file)])
   patches.append(file)
  original=av.open(str(OLD/'captioned.mp4'));vs=original.streams.video[0];output=av.open(str(OUT/'captioned-video.mp4'),'w');dest=output.add_stream_from_template(vs);dest.time_base=Fraction(1,90000);packets=[[] for _ in ranges];inserted=set();retained=hashlib.sha256();retainedCount=0
  for i,file in enumerate(patches):
   with av.open(str(file)) as v:
    ss=v.streams.video[0];assert ss.codec_context.extradata==vs.codec_context.extradata,('extradata mismatch',i)
    for packet in v.demux(ss):
     if packet.dts is None:continue
     packet.pts+=ranges[i][0]*1500;packet.dts+=ranges[i][0]*1500;packets[i].append(packet)
  for packet in original.demux(vs):
   if packet.dts is None:continue
   ri=next((i for i,(a,z) in enumerate(ranges) if a*1500-3000<=packet.dts<z*1500-3000),None)
   if ri is not None:
    if ri not in inserted:
     for replacement in packets[ri]:replacement.stream=dest;output.mux(replacement)
     inserted.add(ri)
   else:retained.update(bytes(packet));retainedCount+=1;packet.stream=dest;output.mux(packet)
  output.close();original.close();assert len(inserted)==len(ranges)
  state['retainedCaptionedPackets']={'count':retainedCount,'sha256':retained.hexdigest(),'reusedReview':'production/local/final-edit-v1/repair-v2/combined-review.json'};save()
  run('captioned',[FF,'-v','warning','-nostdin','-n','-i',str(OUT/'captioned-video.mp4'),'-i',str(BASE/'final-mix.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(OUT/'captioned.mp4')])
  state['outputs']['clean']={**prior['outputs']['clean'],'path':(OUT/'clean.mp4').relative_to(R).as_posix(),'reusedIdenticalBytesFrom':str(SRC.relative_to(R))};save()
  for name in ['captioned']:
   file=OUT/(name+'.mp4');state['active']={'label':name+'-whole-decode-and-pts'};save()
   with av.open(str(file)) as c:
    s=c.streams.video[0];s.thread_type='SLICE';s.codec_context.thread_count=2;assert s.width==1920 and s.height==1080 and s.average_rate==60 and s.time_base==Fraction(1,90000);count=0
    for frame in c.decode(s):assert frame.pts==count*1500,(name,count,frame.pts);count+=1
    assert count==timeline['frames']
   aac=OUT/(name+'.aac');run(name+'-aac',[FF,'-v','error','-nostdin','-n','-i',str(file),'-vn','-c:a','copy','-f','adts',str(aac)])
   state['outputs'][name]={'path':file.relative_to(R).as_posix(),'sha256':sha(file),'frames':count,'seconds':count/60,'wholeDecodeExit':0,'wholeDecodeMethod':'PyAV/libav full-frame decoding with integer PTS checks','ptsEveryFrame1500':True,'timeBase':90000,'aacSha256':sha(aac)};save()
  assert state['outputs']['clean']['aacSha256']==state['outputs']['captioned']['aacSha256']==state['baselinePair']['captioned']['aacSha256']
  state.update(status='complete-awaiting-changed-encoded-pixels',exitCode=0,endedAt=now(),active=None,identicalAac=True,allFinalPixelsApproved=False);save()
 except BaseException as e:state.update(status='failed',error=repr(e),endedAt=now());save();raise
if __name__=='__main__':main()
