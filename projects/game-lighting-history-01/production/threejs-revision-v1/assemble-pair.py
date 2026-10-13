"""Same-timing visual revision. Retain native segments and untouched captioned GOPs.

No source audio, TTS, narration timing, subtitles or baseline upload is changed.
The new output remains unapproved until its changed encoded pixels are reviewed.
"""
import os,sys,json,pathlib,datetime,hashlib,subprocess
from fractions import Fraction
import av,psutil
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01'
BASE=P/'production/local/final-edit-v1';OLD=BASE/'repair-v2'
CAPTION_SAFE='--caption-safe' in sys.argv
OUT=P/('production/local/threejs-revision-v1/pair-caption-safe-v2' if CAPTION_SAFE else 'production/local/threejs-revision-v1/pair');OUT.mkdir(parents=True,exist_ok=True)
FF='C:/Users/eazuo/miniconda3/envs/renderformer/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['rendererRevision']['privateUploadAuthorized']
 renderplan=rd(P/'production/threejs-revision-v1/render-plan.json')
 three=rd(OUT.parent/'three/execution.json');math=rd(OUT.parent/'manim/execution.json')
 assert not three.get('active') and set(renderplan['keys'])=={x['key'] for x in three['completed']}
 assert len(math['completed'])==8 and math['status']=='complete-awaiting-pixels'
 assets={x['key']:x for x in three['completed']+math['completed']}
 for a in assets.values():assert sha(R/a['path'])==a['sha256'],a['key']
 timeline=rd(OLD/'plan.json');timing=rd(R/'motion-canvas/src/projects/game-lighting-history-01/explanation-assets-v1/data.json')
 captions=rd(BASE/'captions.json');asr=rd(BASE/'mixed-asr-direct-review.json')
 assert asr['allCurrentMixedTextsDirectlyCompared'] and asr['contentCoverageApproved'] and asr['mixSha256']==sha(BASE/'final-mix.wav')
 assert captions['allCueTextDirectReview']
 resume='--resume-native-explanation' in sys.argv
 assert resume or not (OUT/'execution.json').exists(),'Inspect existing execution; never restart a successful or running pair.'
 state={'status':'running','pid':os.getpid(),'createTime':psutil.Process().create_time(),'command':psutil.Process().cmdline(),'startedAt':now(),'cpuThreads':2,'gpuJobs':0,'steps':[],'outputs':{},'baselinePlanSha256':sha(OLD/'plan.json'),'baselinePair':rd(OLD/'execution.json')['outputs'],'inputHashes':{n:sha(BASE/n) for n in ['final-mix.m4a','captions.ko.ass','mixed-asr-direct-review.json']},'assets':assets,'allFinalPixelsApproved':False}
 if resume:
  prior=rd(OUT/'execution.json');assert prior['status']=='failed' and prior['error']=='StopIteration()' and len(prior['steps'])==23
  assert prior['assets']==assets and prior['inputHashes']==state['inputHashes'] and prior['baselinePlanSha256']==state['baselinePlanSha256']
  assert not psutil.pid_exists(prior['pid']) or psutil.Process(prior['pid']).create_time()!=prior['createTime']
  write(OUT/'execution-first-failure.json',prior);state['steps']=prior['steps'];state['resumedFrom']='execution-first-failure.json';state['retainedCompletedSegments']=[]
 def save():write(OUT/'execution.json',state)
 def run(label,args):
  log=OUT/(label+'.log');state['active']={'label':label,'command':args,'log':log.relative_to(R).as_posix()};save()
  with log.open('w',encoding='utf8') as f:
   child=subprocess.Popen(args,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);state['active']['pid']=child.pid;save();rc=child.wait()
  state['steps'].append({'label':label,'exitCode':rc});save();assert rc==0,(label,rc)
 def encode(inputs,filt,out,count):
  if resume and out.exists() and any(x['label']==out.stem and x['exitCode']==0 for x in state['steps']):
   with av.open(str(out)) as c:
    s=c.streams.video[0];assert s.frames==count and s.width==1920 and s.height==1080 and s.average_rate==60
   state['retainedCompletedSegments'].append({'path':out.relative_to(R).as_posix(),'sha256':sha(out),'frames':count});save();return
  args=[FF,'-v','warning','-nostdin','-n','-threads','2']
  for path,seek in inputs:args+=['-reinit_filter','0','-ss',f'{seek:.9f}','-i',str(path)]
  run(out.stem,args+['-filter_complex_threads','2','-filter_complex',filt,'-map','[out]','-an','-frames:v',str(count),'-r','60','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(out)])
 save()
 try:
  changed=[];paths=[];newnodes=[]
  for n in timeline['nodes']:
   if n['role']!='explanation':
    file=OLD/(n['id']+'.mp4')
    if not file.exists():file=BASE/'segments'/(n['id']+'.mp4')
    assert file.exists(),file
    paths.append(file);newnodes.append(n);continue
   chapter=next((c for c in timing['chapters'] if n['path'].endswith('explanation-'+c['id']+'.mp4')),None)
   if chapter is None:
    assert n.get('actualExportGraph') is True and n['id']=='s109'
    file=BASE/'segments'/(n['id']+'.mp4');assert file.exists();paths.append(file);newnodes.append(n);continue
   a,z=n['sourceStartFrame'],n['sourceStartFrame']+n['frames'];parts=[]
   for b in chapter['blocks']:
    start=b['pcmStartFrame']-chapter['pcmStartFrame'];end=start+b['frames'];lo,hi=max(a,start),min(z,end)
    if hi<=lo:continue
    asset=assets.get(b['paragraphKey']);parts.append({'key':b['paragraphKey'],'path':R/asset['path'] if asset else R/n['path'],'seek':(lo-start if asset else lo)/60,'frames':hi-lo,'changed':bool(asset)})
   assert sum(x['frames'] for x in parts)==n['frames']
   if not any(x['changed'] for x in parts):paths.append(BASE/'segments'/(n['id']+'.mp4'));newnodes.append(n);continue
   filters=[f'[{i}:v]trim=end_frame={x["frames"]},setpts=N/(60*TB),'+('scale=1804:1014:flags=lanczos,pad=1920:1080:58:0:black,' if CAPTION_SAFE and x['key'] in renderplan['keys'] else '')+f'setsar=1,format=yuv420p[v{i}]' for i,x in enumerate(parts)]
   filters.append(''.join(f'[v{i}]' for i in range(len(parts)))+f'concat=n={len(parts)}:v=1:a=0[out]')
   file=OUT/(n['id']+'.mp4');encode([(x['path'],x['seek']) for x in parts],';'.join(filters),file,n['frames'])
   changed.append([n['startFrame'],n['endFrame']]);paths.append(file);newnodes.append({**n,'path':file.relative_to(R).as_posix(),'sourceStartFrame':0,'retainedExplanationAsset':False,'rendererRevisionParts':[{**x,'path':x['path'].relative_to(R).as_posix()} for x in parts]})
  plan={**timeline,'nodes':newnodes,'allFinalPixelsApproved':False,'finalPairComplete':False,'visualRevision':{'id':'threejs-revision-v1','changedRanges':changed,'sameTimingAndAudio':True,'captionSafeThreeJSInset':{'width':1804,'height':1014,'x':58,'y':0,'reason':'Original footer at y882-908 collided with two-line caption top896; uniformly inset only Three.js assets to reserve caption area.'} if CAPTION_SAFE else None}};write(OUT/'plan.json',plan)
  listing=OUT/'segments.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in paths)+'\n',encoding='utf8')
  run('clean',[FF,'-v','warning','-nostdin','-n','-f','concat','-safe','0','-i',str(listing),'-i',str(BASE/'final-mix.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(OUT/'clean.mp4')])
  with av.open(str(OLD/'captioned.mp4')) as c:
   s=c.streams.video[0];keys=[round(p.pts*s.time_base*60) for p in c.demux(s) if p.is_keyframe and p.pts is not None]
  keys=sorted(set(keys+[timeline['frames']]));ranges=[]
  for a,z in changed:
   a=max(k for k in keys if k<=a);z=min(k for k in keys if k>=z)
   if ranges and a<=ranges[-1][1]:ranges[-1][1]=max(z,ranges[-1][1])
   else:ranges.append([a,z])
  state['captionPatchRanges']=ranges;save();patches=[]
  ass=(BASE/'captions.ko.ass').relative_to(R).as_posix();fonts=(BASE/'fonts').relative_to(R).as_posix()
  for i,(a,z) in enumerate(ranges):
   file=OUT/f'caption-patch-{i}.mp4';filt=f"[0:v]trim=end_frame={z-a},setpts=N/(60*TB)+{a}/(60*TB),ass='{ass}':fontsdir='{fonts}',setpts=PTS-STARTPTS,setsar=0,setparams=range=unspecified:color_primaries=unknown:color_trc=unknown:colorspace=unknown[out]";encode([(OUT/'clean.mp4',a/60)],filt,file,z-a);patches.append(file)
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
  for name in ['clean','captioned']:
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
