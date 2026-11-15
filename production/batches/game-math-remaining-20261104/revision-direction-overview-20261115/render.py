"""Finite local revision: patch changed keyframe spans; copy all other pictures/audio."""
import sys,os,json,subprocess,hashlib,math,shutil,time,argparse
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];PREV=HERE.parent/'revision-game-subjects-20261115'
sys.path.insert(0,str(PREV));import subject_revision as old
sys.path.insert(0,str(HERE));import base_renderer as base
from lesson_bookends import build
FF=old.FF;FP=FF.with_name('ffprobe.exe')
DEST=ROOT/'output/game-math-direction-overview-20261115/local-masters'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,cwd=HERE,name='command',capture=False):
 args=[str(x) for x in args]
 if capture:
  r=subprocess.run(args,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
  if r.returncode:raise RuntimeError(r.stderr.decode('utf8','replace')[-4000:])
  return r.stdout
 with open(cwd/(name+'.log'),'w',encoding='utf8') as log:
  r=subprocess.run(args,cwd=cwd,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
 if r.returncode:raise RuntimeError((cwd/(name+'.log')).read_text(encoding='utf8',errors='replace')[-4000:])
def ff(args,cwd=HERE,name='ffmpeg',capture=False):return run([FF,'-hide_banner','-nostdin','-v','warning','-y',*args],cwd,name,capture)
def stream(p):return json.loads(run([FP,'-v','error','-select_streams','v:0','-show_streams','-of','json',p],capture=True))['streams'][0]
def keys(row):
 p=HERE/'local/work'/row['slug']/'keyframes.json'
 if p.exists():return read(p)
 sets=[]
 for kind in ('clean','captioned'):
  fs=json.loads(run([FP,'-v','error','-select_streams','v:0','-skip_frame','nokey','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',row['sources'][kind]['path']],capture=True))['frames']
  sets.append(set([0,row['frames']]+[round(float(x['best_effort_timestamp_time'])*60) for x in fs if 'best_effort_timestamp_time' in x]))
 a=sorted(sets[0]&sets[1]);save(p,a);save(p.with_name('joint-keyframe-proof.json'),dict(cleanKeyframes=len(sets[0]),captionedKeyframes=len(sets[1]),sharedKeyframes=len(a),allCopyStartsValidInBothStreams=True));return a
def direction_ranges(e):
 if e['id'] in ('M24','M25','M26'):return [(t['start'],t['end']) for t in base.tracks(e)]
 if e['id']=='M27':return [(s['start'],s['end']) for s in e['scenes'] if s['scene']=='021']
 if e['id']=='M28':return [(s['start'],s['end']) for s in e['scenes'] if s['scene'] in ('010','024')]
 if e['id']=='M33':return [(s['start'],s['end']) for s in e['scenes'] if s['scene']=='029']
 return []
def spans(row):
 key=keys(row);changes=direction_ranges(base.EPISODES[row['id']]);bounded=[]
 if not row.get('onlyDirection'):changes=[(row['start'],row['end']),(row['recapStart'],row['recapEnd'])]+changes
 for a,z in changes:
  aa=max(k for k in key if k<=round(a*60));zz=min(k for k in key if k>=round(z*60));bounded.append((aa,zz))
 merged=[]
 for a,z in sorted(bounded):
  if merged and a<=merged[-1][1]+120:merged[-1]=(merged[-1][0],max(merged[-1][1],z))
  else:merged.append((a,z))
 result=[];cursor=0
 for a,z in merged:
  if a>cursor:result.append(dict(start=cursor,end=a,changed=False))
  result.append(dict(start=a,end=z,changed=True));cursor=z
 if cursor<row['frames']:result.append(dict(start=cursor,end=row['frames'],changed=False))
 assert sum(s['end']-s['start'] for s in result)==row['frames'];return result
def bookend_graph(row,origin,end,g,inputs):
 ni=1+sum(x=='-i' for x in inputs)
 g=g.replace('[vout]','[booksrc]')
 g+=';[booksrc]setpts=PTS+'+str(origin)+'/TB,split=3[bookbase][opensrc][recapsrc];'
 g+='[opensrc]crop=1920:910:0:0,scale=820:388:flags=lanczos[openmovie];'
 g+='[recapsrc]crop=1920:910:0:0,scale=820:388:flags=lanczos[recapmovie];'
 current='bookbase';counter=0
 def overlay(file,a,z):
  nonlocal ni,g,current,counter
  if z<=origin or a>=end:return
  inputs.extend(['-i',str(HERE/'local/work'/row['slug']/file)]);target=f'book{counter}';counter+=1
  g+=f"[{current}][{ni}:v]overlay=0:0:enable='gte(t,{a})*lt(t,{z})'[{target}];";ni+=1;current=target
 overlay('overview.png',row['start'],row['end'])
 overlay('roadmap.png',row['roadmap'],row['end'])
 times=[row['recapStart']]+[max(row['recapStart'],x['at']) for x in row['recap']]+[row['recapEnd']]
 for n,(a,z) in enumerate(zip(times,times[1:])):overlay(f'recap-{n}.png',a,z)
 g+=f"[{current}][openmovie]overlay=1030:300:eof_action=pass:enable='gte(t,{row['start']})*lt(t,{row['end']})'[withopen];"
 current='withopen'
 if row['start']<end and row['end']>origin:
  # A single labelled revisit to the already inspected native hook; no loop,
  # frozen padding, guessed continuation, or unrelated early Unity character.
  inputs.extend(['-ss','2','-threads','2','-i',row['sources']['clean']['path']])
  g+=f'[{ni}:v]trim=duration={row["hookSeconds"]},setpts=PTS-STARTPTS+{row["start"]}/TB,crop=1536:864:192:48,scale=820:462:flags=lanczos[hookmovie];'
  g+=f"[withopen][hookmovie]overlay=1030:300:eof_action=pass:repeatlast=0:enable='gte(t,{row['start']})*lt(t,{min(row['end'],row['start']+row['hookSeconds'])})'[withhook];";current='withhook'
 g+=f"[{current}][recapmovie]overlay=1030:310:eof_action=pass:enable='gte(t,{row['recapStart']})*lt(t,{row['recapEnd']})'[withrecap];"
 g+=f'[withrecap]setpts=PTS-{origin}/TB,split=2[vout][capbase];[capbase]setpts=PTS+{origin}/TB,ass=captions.ko.ass,setpts=PTS-{origin}/TB[capout]'
 return inputs,g
def encode_span(row,span,i):
 e=base.EPISODES[row['id']];p=base.work(e);a=span['start']/60;z=span['end']/60;frames=span['end']-span['start']
 clean=p/f'patch-{i:02}.clean.mp4';cap=p/f'patch-{i:02}.captioned.mp4';receipt=p/f'patch-{i:02}.json'
 if receipt.exists() and clean.exists() and cap.exists() and read(receipt)['span']==span:return [clean,cap]
 raw=any(x<z and y>a for x,y in direction_ranges(e))
 if raw:
  source=Path(e['baselineOutputs']['clean']);inputs,g=base.graph(e,a,z)
  shutil.copy2(ROOT/'projects'/e['slug']/'production/local/teaching-sync-v2/workings.ass',p/'workings.ass')
 else:
  source=Path(row['sources']['clean']['path']);inputs=[];g='[0:v]setsar=1,fps=60,setpts=PTS-STARTPTS[vout]'
 old.prior.prepare_captions(e,p);inputs,g=bookend_graph(row,a,z,g,inputs)
 (p/f'patch-{i:02}.ffgraph').write_text(g,encoding='utf8')
 # Foreign GPU work keeps its lease. This revision uses bounded CPU encoding.
 codec=['-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-bf','2','-g','120','-sc_threshold','0','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
 args=['-threads','2','-ss',a,'-reinit_filter','0','-i',source,*inputs,'-filter_complex_threads','2','-/filter_complex',f'patch-{i:02}.ffgraph']
 for label,path in [('[vout]',clean),('[capout]',cap)]:args+=['-map',label,'-an','-frames:v',frames,*codec,path]
 save(p/'worker.json',dict(episode=row['id'],pid=os.getpid(),phase='rendering-visual-patch',span=span,rawAnalyticCompositor=raw,cpuThreads=4,otherGpuLeaseUntouched=True))
 ff(args,p,f'patch-{i:02}')
 for f in (clean,cap):assert int(stream(f)['nb_frames'])==frames,(f,stream(f)['nb_frames'],frames)
 save(receipt,dict(span=span,rawCompositor=raw,files=[dict(path=str(f),sha256=sha(f)) for f in (clean,cap)]));return [clean,cap]
def audio_hash(p):return ff(['-i',p,'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],capture=True).decode().strip()
def audio_clock(p):
 packets=json.loads(run([FP,'-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=pts,dts,duration:packet_side_data=side_data_type,skip_samples,discard_padding','-of','json',p],capture=True))
 return hashlib.sha256(json.dumps(packets,sort_keys=True).encode()).hexdigest()
def vcl_hash(p,start=None,count=None):
 args=(['-ss',start] if start is not None else [])+['-i',p,'-map','0:v:0','-an','-c:v','copy']
 if count is not None:args+=['-frames:v',count]
 return ff([*args,'-bsf:v','filter_units=remove_types=6|7|8|9','-f','hash','-hash','sha256','-'],capture=True).decode().strip()
def packet_grid(p,frames):
 rows=json.loads(run([FP,'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,dts,duration','-of','json',p],capture=True))['packets']
 assert len(rows)==frames
 pts=sorted(int(x['pts']) for x in rows);assert pts==list(range(0,frames*1500,1500)),('presentation grid',p)
 dts=[int(x['dts']) for x in rows];assert all(a<b for a,b in zip(dts,dts[1:])),('decode clock',p)
 assert all(int(x['dts'])<=int(x['pts']) for x in rows)
 return dict(presentation='Every packet exactly on the 60fps grid, no duplicated/dropped presentation timestamp',decode='Strictly increasing DTS; precedes presentation',packets=len(rows))
def destination(row):
 # Select an explicitly recorded local root without altering previous masters.
 choices=[DEST,Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingOutputs/game-math-direction-overview-20261115']
 choices.sort(key=lambda p:shutil.disk_usage(p.anchor).free,reverse=True);dest=choices[0]/row['slug'];dest.mkdir(parents=True,exist_ok=True);return dest
def episode(row,preview=False):
 p=build(row);es=spans(row);save(p/'spans.json',es)
 for kind,d in row['sources'].items():assert Path(d['path']).exists(),(row['id'],kind,'missing accepted baseline')
 if preview:
  pick=next((i,s) for i,s in enumerate(es) if s['changed']);return encode_span(row,pick[1],pick[0])
 receipt=HERE/'deliveries'/f'{row["id"]}.json';receipt.parent.mkdir(exist_ok=True)
 if receipt.exists():
  previous=read(receipt)
  if all(Path(v['path']).exists() and sha(v['path'])==v['sha256'] for v in previous['files'].values()):print(row['id']+' already assembled',flush=True);return
 patches={}
 for i,s in enumerate(es):
  if s['changed']:patches[i]=encode_span(row,s,i)
 dest=destination(row);files={};qaproofs=[]
 for ki,kind in enumerate(('clean','captioned')):
  segments=[];copied=[]
  for i,s in enumerate(es):
   if s['changed']:seg=patches[i][ki]
   else:
    seg=p/f'copy-{i:02}.{kind}.mp4';source=row['sources'][kind]['path']
    ff(['-ss',s['start']/60,'-i',source,'-map','0:v:0','-an','-frames:v',s['end']-s['start'],'-c:v','copy','-video_track_timescale','90000',seg],p,f'copy-{i:02}-{kind}')
    info=stream(seg);assert int(info['nb_frames'])==s['end']-s['start'],(row['id'],kind,s,info)
    assert abs(float(info['start_time']))<1/90000,(s,info['start_time']);copied.append(dict(span=s,path=str(seg)))
   segments.append((seg,s))
  concat=p/(kind+'.ffconcat');concat.write_text('ffconcat version 1.0\n'+''.join("file '"+f.as_posix()+"'\nduration "+f'{(s["end"]-s["start"])/60:.9f}'+'\n' for f,s in segments),encoding='utf8')
  out=dest/(row['slug']+'.'+kind+'.mp4');source=row['sources'][kind]['path']
  # Reconstructed pictures and copied NVENC GOPs use different B-frame decode
  # lead. Keep every presentation timestamp and use one safe decode cadence.
  ff(['-f','concat','-safe','0','-i',concat,'-i',source,'-map','0:v:0','-map','1:a:0','-c','copy','-bsf:v','setts=pts=PTS:dts=N*1500-4500:duration=1500','-video_track_timescale','90000','-movflags','+faststart',out],p,'assemble-'+kind)
  info=stream(out);assert int(info['nb_frames'])==row['frames'] and info['width']==1920 and info['height']==1080 and info['avg_frame_rate']=='60/1',(row['id'],kind,info)
  assert abs(float(info['duration'])-row['frames']/60)<1/90000
  expected=audio_hash(source);assert audio_hash(out)==expected,(row['id'],'audio content changed')
  ac=audio_clock(source);assert audio_clock(out)==ac,(row['id'],'audio clock changed')
  ff(['-threads','2','-v','error','-xerror','-i',out,'-map','0:v:0','-map','0:a:0','-f','null','-'],p,'decode-'+kind)
  grid=packet_grid(out,row['frames'])
  for part in copied:
   s=part['span'];expected_vcl=vcl_hash(part['path']);assert vcl_hash(out,s['start']/60,s['end']-s['start'])==expected_vcl
   part['unchangedVclHash']=expected_vcl
  files[kind]=dict(path=str(out),sha256=sha(out));qaproofs.append(dict(kind=kind,fullDecode='passed',audioPacketHash=expected,audioClockHash=ac,stream=info,packetGrid=grid,unchangedSpans=copied))
  # Only reproducible intermediates created by this worker are reclaimed.
  for f,s in segments:
   if not s['changed']:
    assert f.resolve().is_relative_to(p.resolve());f.unlink()
 for lang in ('ko','en'):
  f=dest/(row['slug']+'.'+lang+'.srt');shutil.copy2(row['sources'][lang]['path'],f);assert sha(f)==row['sources'][lang]['sha256'];files[lang]=dict(path=str(f),sha256=sha(f))
 save(receipt,dict(id=row['id'],title=row['title'],files=files,frames=row['frames'],duration=row['frames']/60,spans=es,qa=qaproofs,status='encoded-visual-review-pending',humanReviewed=False,ttsChanged=False,voiceTempo=1,platformChanged=False,reviewPage=str(dest/'index.html')))
 for i,fs in patches.items():
  for f in fs:
   assert f.resolve().is_relative_to(p.resolve());f.unlink()
 save(p/'worker.json',dict(episode=row['id'],pid=os.getpid(),phase='encoded-visual-review-pending',receipt=str(receipt)))
 print(row['id']+' encoded, full decode / unchanged AAC clock and subtitles passed',flush=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('episodes',nargs='*');ap.add_argument('--preview',action='store_true');a=ap.parse_args()
 plan=read(HERE/'plan.json')
 for row in plan['episodes']:
  if a.episodes and row['id'] not in a.episodes:continue
  episode(row,a.preview)
if __name__=='__main__':main()
