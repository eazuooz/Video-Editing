"""Same-duration four-node repair. Retain original files, PCM, captions and unaffected GOPs."""
import pathlib,json,datetime,hashlib,subprocess,runpy,os,sys
from fractions import Fraction
import av,psutil
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-01';O=P/'production/local/final-edit-v1';D=O/'repair-v2'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP=FF.replace('ffmpeg','ffprobe')
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sh(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8388608),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['publishingAuthorization']['privateUploadForMobileReview']
 assert rd(D/'source-review.json')['approved']
 resume='--resume' in sys.argv
 if resume:
  prior=rd(D/'execution.json');assert prior['status']=='failed' and 'extradata differs' in prior['error']
  assert not (D/'execution-first-attempt.json').exists();wr(D/'execution-first-attempt.json',prior)
 else:assert not (D/'execution.json').exists()
 plan=rd(O/'plan.json');ranges=rd(D/'gop-ranges.json');fr=runpy.run_path(str(P/'production/final-framing-v1.py'))
 state=dict(status='running',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=0,baselinePlanSha256=sh(O/'plan.json'),baselinePair=rd(O/'pair-execution.json'),steps=[],outputs={},captionPatchRanges=ranges)
 def save():wr(D/'execution.json',state)
 def run(name,args):
  state['active']=dict(name=name,command=args,log=(D/(name+'.log')).relative_to(R).as_posix());save()
  with (D/(name+'.log')).open('w') as f:rc=subprocess.call(args,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  state['steps'].append(dict(name=name,exitCode=rc));save();assert rc==0,(name,rc)
 def encode(inp,out,filt,count,seek=0):
  run(out.stem,[FF,'-v','warning','-nostdin','-n','-threads','2','-ss',f'{seek:.9f}','-i',str(inp),'-filter_complex_threads','2','-filter_complex',filt,'-map','[out]','-an','-frames:v',str(count),'-r','60','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(out)])
 save()
 try:
  replacements={};newnodes=[]
  for n in plan['nodes']:
   if n['id'] not in ['s014','s015','s018','s076']:newnodes.append(n);continue
   specs={'s014':[(1758,360)],'s015':[(2118,504)],'s018':[(3126,162),(252,78)],'s076':[(2280,840)]}[n['id']]
   parts=[];position=n['startFrame']
   for i,(start,count) in enumerate(specs):
    nn=dict(n,sourceStartFrame=start,frames=count,startFrame=position,endFrame=position+count,id=n['id'] if len(specs)==1 else n['id']+chr(97+i));position+=count
    if n['id'] in ['s014','s015']:nn['focusKo']='2024 재발매판 · 추가 에피소드와 원작 맵의 실제 플레이입니다.'
    newnodes.append(nn);out=D/(nn['id']+'.mp4')
    if not resume:encode(R/nn['path'],out,fr['filtergraph'](nn),count,start/60)
    else:assert out.exists()
    parts.append(out)
   replacements[n['id']]=parts
  repaired=dict(plan,nodes=newnodes,allFinalPixelsApproved=False);repaired['visualRevision']=dict(reason='Remove promotional intertitles and HL2 red tail; timing and audio unchanged.',baselinePlan=state['baselinePlanSha256'])
  wr(D/'plan.json',repaired)
  paths=[]
  for n in plan['nodes']:paths.extend(replacements.get(n['id'],[O/'segments'/(n['id']+'.mp4')]))
  listing=D/'segments.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in paths)+'\n',encoding='utf8')
  if not resume:run('clean',[FF,'-v','warning','-nostdin','-n','-f','concat','-safe','0','-i',str(listing),'-i',str(O/'final-mix.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(D/'clean.mp4')])
  else:state['preservedCleanSha256']=sh(D/'clean.mp4')
  ass=(O/'captions.ko.ass').relative_to(R).as_posix();fonts=(O/'fonts').relative_to(R).as_posix();patches=[]
  for i,(a,b) in enumerate(ranges):
   out=D/f'caption-patch-match-{i}.mp4';filt=f"[0:v]setpts=PTS+{a}/(60*TB),ass='{ass}':fontsdir='{fonts}',setpts=PTS-STARTPTS,setsar=0,setparams=range=unspecified:color_primaries=unknown:color_trc=unknown:colorspace=unknown[out]"
   encode(D/'clean.mp4',out,filt,b-a,a/60);patches.append(out)
  original=av.open(str(O/'captioned.mp4'));vs=original.streams.video[0]
  output=av.open(str(D/'captioned-video.mp4'),'w');dest=output.add_stream_from_template(vs);dest.time_base=Fraction(1,90000)
  packets=[[] for _ in ranges];inserted=set();retainedHash=hashlib.sha256();retainedCount=0
  for i,p in enumerate(patches):
   with av.open(str(p)) as v:
    ss=v.streams.video[0];assert ss.codec_context.extradata==vs.codec_context.extradata,('extradata differs',i)
    for packet in v.demux(ss):
     if packet.dts is None:continue
     packet.pts+=ranges[i][0]*1500;packet.dts+=ranges[i][0]*1500;packets[i].append(packet)
  for packet in original.demux(vs):
   if packet.dts is None:continue
   ri=next((i for i,(a,b) in enumerate(ranges) if a*1500-3000<=packet.dts<b*1500-3000),None)
   if ri is not None:
    if ri not in inserted:
     for replacement in packets[ri]:replacement.stream=dest;output.mux(replacement)
     inserted.add(ri)
   else:
    retainedHash.update(bytes(packet));retainedCount+=1;packet.stream=dest;output.mux(packet)
  output.close();original.close();assert len(inserted)==len(ranges)
  state['retainedEncodedPackets']=dict(count=retainedCount,sha256=retainedHash.hexdigest(),closedGopBoundaries=ranges)
  run('captioned',[FF,'-v','warning','-nostdin','-n','-i',str(D/'captioned-video.mp4'),'-i',str(O/'final-mix.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(D/'captioned.mp4')])
  for name in ['clean','captioned']:
   f=D/(name+'.mp4');run(name+'-decode',[FF,'-v','error','-nostdin','-threads','2','-i',str(f),'-f','null','-'])
   with av.open(str(f)) as c:
    s=c.streams.video[0];s.thread_type='SLICE';s.codec_context.thread_count=2;count=0
    assert s.width==1920 and s.height==1080 and s.average_rate==60 and s.time_base==Fraction(1,90000)
    for frame in c.decode(s):assert frame.pts==count*1500,(name,count,frame.pts);count+=1
    assert count==131010
   aac=D/(name+'.aac');run(name+'-aac',[FF,'-v','error','-nostdin','-n','-i',str(f),'-vn','-c:a','copy','-f','adts',str(aac)])
   state['outputs'][name]=dict(path=f.relative_to(R).as_posix(),sha256=sh(f),frames=count,seconds=count/60,wholeDecodeExit=0,ptsEveryFrame1500=True,timeBase=90000,aacSha256=sh(aac));save()
  assert state['outputs']['clean']['aacSha256']==state['outputs']['captioned']['aacSha256']==state['baselinePair']['outputs']['captioned']['aacSha256']
  state.update(status='complete-awaiting-changed-range-pixel-review',endedAt=now(),exitCode=0,active=None,identicalAac=True,allFinalPixelsApproved=False);save()
 except BaseException as e:state.update(status='failed',error=repr(e),endedAt=now());save();raise
if __name__=='__main__':main()
