"""Repair measured loudnorm/PTS tail shortening; reuse every final video packet."""
from pathlib import Path
import importlib.util,json,os,shutil,time,uuid
import psutil
P=Path(__file__).resolve().parents[1];R=P.parents[1]
s=importlib.util.spec_from_file_location('edit',P/'production/compose-lecture.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
old=P/'production/local/render-v3';new=P/'production/local/render-v4';new.mkdir(exist_ok=True);W=new/'composite';W.mkdir(exist_ok=True)
queue=M.read(old/'queue.json');queue['visualReuse']={'sourceOutput':str(R/'output'/f'{P.name}-render-v3'),'sourceTechnicalReport':str(old/'final-qa/report.json'),'reason':'Exact video-stream reuse; only audio PTS/padding corrected after measured 3200-sample source-tail loss.'};M.save(new/'queue.json',queue)
M.save(new/'progress.json',dict(status='body-captures-complete-compositing-and-QA-pending',captureReuse=str(old/'progress.json'),newUnityCapture=False))
statefile=W/'worker.json'
if statefile.exists():
 d=M.read(statefile)
 try:assert abs(psutil.Process(d['pid']).create_time()-d['createTime'])>.1,'Existing audio repair active'
 except psutil.NoSuchProcess:pass
 assert d['status']!='encoded','Preserve completed repair'
state=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),status='waiting',startedAt=M.now(),automation=False,nextVideo=False)
owned=None;deadline=time.monotonic()+12*3600
try:
 while owned is None:
  M.G.authorized();reason=M.G.idle_reason();state.update(reason=reason,checkedAt=M.now());M.save(statefile,state)
  if reason is None:
   candidate=str(uuid.uuid4())
   try:
    with M.LEASE.open('x',encoding='utf-8') as f:json.dump(dict(owner=P.name+'-audio-frame-repair',id=candidate,pid=os.getpid(),createdAt=M.now()),f)
   except FileExistsError:pass
   else:owned=candidate;break
  if time.monotonic()>deadline:raise RuntimeError('Bounded wait ended, other jobs preserved')
  time.sleep(15)
 state.update(status='compositing');M.save(statefile,state)
 sources,receipt=M.prepare(queue,W);(W/'segments').mkdir(exist_ok=True);audios=[]
 for i,cut in enumerate(queue['cuts']):
  stem=f'{i:03}-{cut["scene"]}';n=cut['frames'];out=W/'segments'/f'{stem}.wav'
  if cut['kind']=='actual-gameplay' and cut['sourceId']!='X9UdRR_4Rog':
   src=sources[cut['sourceId']];audio=R/src.get('audio',{}).get('recoveredOriginalAudio',src['file']);M.normalized_audio(audio,cut['sourceIn'],n,out,-23,W,stem)
  else:
   out=old/'composite/segments'/f'{stem}.wav'
   stream=next(x for x in M.probe(out)['streams'] if x['codec_type']=='audio');assert int(stream['duration_ts'])==n*800
  audios.append(out)
 books=[]
 for name,n in [('branding',120),('membership',600)]:
  source=M.BOOK/f'{name}.mp4';out=W/'segments'/f'{name}.wav'
  if any(x['codec_type']=='audio' for x in M.probe(source)['streams']):M.normalized_audio(source,0,n,out,-23,W,name)
  else:M.silence(out,n,W,name)
  books.append(out)
 M.concat(audios,W/'game-bed.wav',W,'game-bed',True)
 voice=P/'production/local/audio-v1/narration.wav';assert M.sha(voice)==receipt['narrationSha256']
 M.normalized_audio(voice,0,queue['bodyFrames'],W/'narration-normalized.wav',-16,W,'narration')
 filt='[0:a]asplit=2[voice][side];[1:a][side]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[game];[voice][game]amix=inputs=2:duration=first:normalize=0[body]'
 M.ff(['-i',W/'narration-normalized.wav','-i',W/'game-bed.wav','-filter_complex',filt,'-map','[body]','-ar','48000','-ac','2','-c:a','pcm_f32le',W/'body-mix.wav'],W/'logs/mix.log')
 M.concat([books[0],W/'body-mix.wav',books[1]],W/'whole-mix.wav',W,'whole-mix',True)
 M.ff(['-i',W/'whole-mix.wav','-af','aresample=192000,alimiter=limit=0.831764:level=false:latency=true,aresample=48000','-ar','48000','-ac','2','-c:a','aac','-b:a','192k',W/'pair-audio.m4a'],W/'logs/pair-audio.log')
 dest=R/'output'/f'{P.name}-render-v4';dest.mkdir(exist_ok=True);prior=R/'output'/f'{P.name}-render-v3'
 for kind in ('clean','captioned'):
  source=prior/f'{P.name}.{kind}.mp4';target=dest/source.name
  M.ff(['-i',source,'-i',W/'pair-audio.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-map_metadata','-1','-movflags','+faststart',target],W/'logs'/f'{kind}.log');M.video_check(target,queue['bodyFrames']+720)
 for name in (f'{P.name}.ko.srt',f'{P.name}.en.srt','index.html'):shutil.copy2(prior/name,dest/name)
 M.save(W/'progress.json',dict(status='encoded-internal-QA-pending',output=str(dest),files=[dict(path=str(p),sha256=M.sha(p)) for p in dest.iterdir()],originalPcmUnchanged=M.sha(voice)==receipt['narrationSha256'],humanReview=False,finalReviewReady=False,finishedAt=M.now(),audioCorrection='Input-side time limit; audio PTS reset before exact sample trim; unchanged normalization/ducking/limiter policy',videoReencoded=False))
 state.update(status='encoded',finishedAt=M.now());M.save(statefile,state)
except BaseException as exc:state.update(status='failed',error=repr(exc),finishedAt=M.now());M.save(statefile,state);raise
finally:M.G.release_lease(owned)
