"""Re-encode only GOP-aligned visual patches and stream-copy all other video/audio."""
from pathlib import Path
import json,subprocess,hashlib,bisect,sys
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v5';E=O/'assembly';E.mkdir(parents=True,exist_ok=True);B=P/'production/local/revision-v4-clarity'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def selected():assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
def run(cmd,name):
 with (E/(name+'.log')).open('wb') as f:p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError((E/(name+'.log')).read_text(errors='replace')[-2400:])
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def check(p,frames):
 r=probe(p);v=next(s for s in r['streams'] if s['codec_type']=='video');assert(v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',frames),(p,v,frames)
ENC=['-c:v','libx264','-threads','3','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000']
def prepare():
 selected();g=read(O/'gizmos/outputs.json')['replacements'];t=read(P/'production/revision-v3/timeline.json');N=t['totalFrames']
 for sid in ['15','25']:
  s=next(s for s in t['scenes'] if s['id']==sid);clean=O/f'code-color/{sid}.mp4';cap=O/f'code-color/{sid}-captioned.mp4';check(clean,s['frames']);sig=dict(cleanSha256=sha(clean),globalStartFrame=s['startFrame'],frames=s['frames'],captionAssSha256=sha(P/'production/local/revision-v3/captions.ko.ass'))
  receipt=cap.with_suffix('.json')
  if not(cap.exists() and receipt.exists() and read(receipt)==sig):
   vf='settb=1/60,setpts=N+'+str(s['startFrame'])+',ass='+(P/'production/local/revision-v3/captions.ko.ass').relative_to(R).as_posix()+',setpts=PTS-STARTPTS'
   run(['ffmpeg','-v','warning','-y','-i',str(clean),'-an','-vf',vf,'-frames:v',str(s['frames']),'-r','60','-enc_time_base','1:60',*ENC,str(cap)],sid+'-captions');save(receipt,sig)
  g.append(dict(id='code-'+sid,globalStartFrame=s['startFrame'],frames=s['frames'],kind='code-color',files={k:dict(file=p.relative_to(R).as_posix(),sha256=sha(p)) for k,p in [('clean',clean),('captioned',cap)]}))
 g.sort(key=lambda r:r['globalStartFrame']);assert all(a['globalStartFrame']+a['frames']<=b['globalStartFrame'] for a,b in zip(g,g[1:]))
 kindPlans={}
 for kind in ['clean','captioned']:
  baseline=B/f'euler-{kind}.mp4';packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time,flags','-of','json',str(baseline)]))['packets']
  keys=sorted({round(float(p['pts_time'])*60) for p in packets if 'K' in p['flags']}|{N});assert keys[0]==0
  spans=[]
  for r in g:
   a=keys[bisect.bisect_right(keys,r['globalStartFrame'])-1];b=keys[bisect.bisect_left(keys,r['globalStartFrame']+r['frames'])]
   if spans and a<=spans[-1][1]:spans[-1][1]=max(b,spans[-1][1])
   else:spans.append([a,b])
  bounds=sorted({0,N,*[f for s in spans for f in s]});parts=[dict(index=i,startFrame=a,frames=b-a,modified=any(a>=x and b<=y for x,y in spans),replacementIds=[r['id'] for r in g if a<=r['globalStartFrame'] and r['globalStartFrame']+r['frames']<=b]) for i,(a,b) in enumerate(zip(bounds,bounds[1:]))]
  kindPlans[kind]=dict(modifiedFrameRanges=spans,boundaries=bounds,parts=parts,retainedFrames=N-sum(b-a for a,b in spans))
 plan=dict(revision='tracked-gizmos-code-colors-v5',totalFrames=N,fps=60,baseline={k:dict(file=(B/f'euler-{k}.mp4').relative_to(R).as_posix(),sha256=sha(B/f'euler-{k}.mp4')) for k in ['clean','captioned']},audio=dict(file=(B/'final-mix.m4a').relative_to(R).as_posix(),sha256=sha(B/'final-mix.m4a')),timelineSha256=sha(P/'production/revision-v3/timeline.json'),replacements=g,kindPlans=kindPlans,note='Clean and captioned encodes have independent scene-cut keyframes. Each uses its own GOP-aligned boundaries. Only bounded spans re-encoded; complete original AAC retained.')
 save(H/'assembly-plan.json',plan);print('Prepared',len(g),'visual replacements;', {k:round((N-v['retainedFrames'])/60,2) for k,v in kindPlans.items()},'seconds of GOP patches.',flush=True)
def build():
 selected();plan=read(H/'assembly-plan.json');N=plan['totalFrames'];outputs={}
 for kind in ['clean','captioned']:
  selected();kp=plan['kindPlans'][kind];src=R/plan['baseline'][kind]['file'];assert sha(src)==plan['baseline'][kind]['sha256'];dest=E/kind;dest.mkdir(exist_ok=True)
  segmentReceipt=dest/'segment-source.json';sig=dict(sourceSha256=sha(src),boundaries=kp['boundaries'])
  if not(segmentReceipt.exists() and read(segmentReceipt)==sig):
   times=','.join(f'{f/60:.9f}' for f in kp['boundaries'][1:-1])
   run(['ffmpeg','-v','warning','-y','-i',str(src),'-map','0:v:0','-c','copy','-f','segment','-segment_times',times,'-segment_time_delta','0.000001','-reset_timestamps','1','-segment_format_options','video_track_timescale=60000',str(dest/'segment-%02d.mp4')],kind+'-segment');save(segmentReceipt,sig)
  files=[]
  for part in kp['parts']:
   selected();old=dest/f'segment-{part["index"]:02}.mp4';check(old,part['frames']);out=old
   if part['modified']:
    out=dest/f'patch-{part["index"]:02}.mp4';receipt=out.with_suffix('.json');rows=[next(r for r in plan['replacements'] if r['id']==i) for i in part['replacementIds']]
    inputs=dict(originalSha256=sha(old),replacementHashes=[r['files'][kind]['sha256'] for r in rows],part=part,codec=ENC)
    if not(out.exists() and receipt.exists() and read(receipt)==inputs):
     args=['ffmpeg','-v','warning','-y','-i',str(old)];graph=[];labels=[];cursor=0;retain=0
     # Each retained portion has its own split output, so the original segment
     # is decoded once and precise frame ranges are concatenated without fades.
     gaps=[]
     for r in rows:
      a=r['globalStartFrame']-part['startFrame'];b=a+r['frames']
      if a>cursor:gaps.append((cursor,a))
      cursor=b
     if cursor<part['frames']:gaps.append((cursor,part['frames']))
     if gaps:graph.append('[0:v]split='+str(len(gaps))+''.join(f'[base{i}]' for i in range(len(gaps))))
     cursor=0
     for n,r in enumerate(rows,1):
      f=R/r['files'][kind]['file'];assert sha(f)==r['files'][kind]['sha256'];args+=['-i',str(f)];a=r['globalStartFrame']-part['startFrame'];b=a+r['frames']
      if a>cursor:
       label=f'old{retain}';graph.append(f'[base{retain}]trim=start_frame={cursor}:end_frame={a},setpts=PTS-STARTPTS[{label}]');labels.append(label);retain+=1
      label=f'new{n}';graph.append(f'[{n}:v]settb=1/60,setpts=N[{label}]');labels.append(label);cursor=b
     if cursor<part['frames']:
      label=f'old{retain}';graph.append(f'[base{retain}]trim=start_frame={cursor}:end_frame={part["frames"]},setpts=PTS-STARTPTS[{label}]');labels.append(label)
     graph.append(''.join('['+l+']' for l in labels)+f'concat=n={len(labels)}:v=1:a=0,settb=1/60,setpts=N[out]')
     args+=['-filter_complex',';'.join(graph),'-map','[out]','-an','-frames:v',str(part['frames']),'-r','60','-enc_time_base','1:60',*ENC,str(out)];run(args,kind+'-patch-'+str(part['index']));save(receipt,inputs)
    check(out,part['frames'])
   files.append(out)
  concat=dest/'concat.txt';concat.write_text('\n'.join("file '"+f.as_posix()+"'\nduration "+f'{part["frames"]/60:.9f}' for f,part in zip(files,kp['parts']))+'\n',encoding='utf8');master=O/f'euler-{kind}.mp4';audio=R/plan['audio']['file'];assert sha(audio)==plan['audio']['sha256']
  run(['ffmpeg','-v','warning','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','60000','-movflags','+faststart',str(master)],kind+'-master');check(master,N)
  outputs[kind]=dict(file=master.relative_to(R).as_posix(),sha256=sha(master));print('Current master',kind,flush=True)
 save(O/'pair-source.json',dict(inputs=dict(timelineSha256=plan['timelineSha256'],assemblyPlanSha256=sha(H/'assembly-plan.json'),audioSha256=plan['audio']['sha256']),outputs=outputs))
if __name__=='__main__':
 stage=sys.argv[1] if len(sys.argv)>1 else 'all'
 if stage in ['prepare','all']:prepare()
 if stage in ['build','all']:build()
