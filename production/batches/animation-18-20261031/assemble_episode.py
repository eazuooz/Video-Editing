"""Build the local timeline, mixed audio, edited picture and four-file review for one selected animation episode."""
from pathlib import Path
import json,sys,hashlib,math,subprocess,shutil,re
from datetime import datetime,timezone
from fractions import Fraction
from concurrent.futures import ThreadPoolExecutor
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw,ImageFont
BATCH=Path(__file__).resolve().parent;R=BATCH.parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rel(p):return p.relative_to(R).as_posix()
EP=sys.argv[1];row=next(x for x in read(R/'shared/publishing/video-worklist.json')['rows'] if x['id']==EP)
assert EP in read(BATCH/'batch.json')['episodeIds'] and row['productionAuthorized']
P=R/'projects'/row['slug'];H=P/'production/series-v1';L=P/'production/local/series-v1'
A01=R/'projects/animation-assigning/production/local/grid-v1/edit'
V=L/'picture';V.mkdir(exist_ok=True);visual=read(H/'visual-plan.json')
sys.path.insert(0,str(R/'projects/animation-breaking-down-attack-animations/production/grid-v1'))
import caption_pipeline as cp
def ff(args,name):
 with (L/(name+'.log')).open('wb') as f:rc=subprocess.call(['ffmpeg','-y','-nostdin','-hide_banner',*map(str,args)],stdout=f,stderr=f,cwd=R)
 if rc:raise RuntimeError((L/(name+'.log')).read_text('utf-8',errors='replace')[-1700:])
def probe(p):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',p]))
def timing():
 timing=read(L/'voice/narration.timing.json');assert read(L/'voice/narration.asr-review.json')['complete']
 groups=[[(a.strip(),b.strip()) for a,b in (line.split(' | ') for line in group.splitlines())] for group in (H/'narration-pairs.txt').read_text('utf-8').strip().split('\n\n')]
 font=cp.measured_font(Path('C:/Windows/Fonts/NotoSansKR-VF.ttf'),500);bold=cp.measured_font(Path('C:/Windows/Fonts/NotoSansKR-VF.ttf'),700)
 cues=[];rows=[];checks=[]
 aliases={'버추어':'버추얼','제로슈트':'제로슈트','스매시브라더스':'스매시브라더스','예순':'60','열두':'12','영점이':'02','몬스터헌터':'몬스터헌터','쿠퍼':'쿠파','프레임':'frame','첫프레임':'첫frame'}
 aliases.update(visual.get('pronunciationAliases',{}))
 for i,(entry,g,shotgroup) in enumerate(zip(timing['entries'],groups,visual['shots'])):
  sid=entry['scene_id'];file=L/'voice/chunks'/(sid+'-scene.wav');source=read(L/'voice/asr'/(sid+'.json'));assert source['audio_sha256']==sha(file)
  assert len(g)==len(shotgroup),(sid,len(g),len(shotgroup))
  duration=sf.info(file).duration;offset=2+entry['start'];words=[];last=0.
  for w in source['words']:
   a,b=w['timestamp'];a=max(last,a or 0);b=min(duration,b if b is not None else duration)
   if b>a+.0001:words.append(dict(text=w['text'],timestamp=[a,b]));last=b
  text=' '.join(k for k,e in g);start,end,qa=cp.align_characters(text,words,duration,aliases,.90);checks.append({'scene':sid,'coverage':qa['matchingCharacterCoverage'],'hash':sha(file)})
  ix=0
  for (ko,en),shot in zip(g,shotgroup):
   n=len(cp.normalized(ko,aliases));t0=round(offset+start[ix],2);t1=round(offset+end[ix+n-1],2);ix+=n
   c={'start':t0,'end':t1,'ko':ko,'en':en,'scene':sid,'cue':len(cues)+1,'emphasis':{'ko':None,'en':None}}
   for lang in ('ko','en'):
    lines=cp.wrap(c[lang],font);assert lines,(sid,c[lang]);c[lang]='\n'.join(lines)
   assert t1>t0 and (not cues or t0>=cues[-1]['end']-.001),(sid,t0,t1)
   cues.append(c);rows.append(dict(chapter=sid,start=round(t0*60),key=shot[0],sourcePoint=shot[1],focus=shot[2],cue=c['cue']))
 total=math.ceil((2+timing['duration_seconds'])*60)+600;rows[0]['start']=120
 for i,s in enumerate(rows):s['frames']=(rows[i+1]['start'] if i+1<len(rows) else total-600)-s['start']
 for lang in ('ko','en'):
  (L/f'captions.{lang}.srt').write_text(''.join(f"{c['cue']}\n{cp.srt_stamp(c['start'])} --> {cp.srt_stamp(c['end'])}\n{c[lang]}\n\n" for c in cues),encoding='utf-8')
  events=[cp.ass_events(c,cp.geometry(c[lang],font,bold,c['emphasis'][lang]),lang) for c in cues]
  (L/f'captions.{lang}.ass').write_text(cp.ass_header('Noto Sans KR')+''.join(events),encoding='utf-8')
 sources={}
 for k,raw in visual['gameFiles'].items():
  file=R/raw;v=probe(file);stream=next(s for s in v['streams'] if s['codec_type']=='video')
  assert int(stream['width'])>=1920 and int(stream['height'])>=1080,(k,stream['width'],stream['height'])
  sources[k]={'file':raw,'sha256':sha(file),'dimensions':[stream['width'],stream['height']],'fps':stream['avg_frame_rate'],'seconds':float(v['format']['duration'])}
 for s in rows:
  if s['key'] in sources:assert s['sourcePoint']+s['frames']/60 <=sources[s['key']]['seconds'],s
 plan={'episode':EP,'framesPerSecond':60,'totalFrames':total,'bodyFrames':total-720,'cuts':rows,'sourceEvidence':sources,'wordAlignment':checks}
 game=sum(s['frames'] for s in rows if s['key'] in sources)
 plan['initialGameFrames']=game;plan['gameFrames']=game
 target=round(.60*plan['bodyFrames'])
 if 'balance' in visual:
  chosen=next(i for i,s in enumerate(rows) if s['cue']==visual['balance']['cue'])
  s=rows[chosen];extra=game-target
  if extra>0:
   assert s['key'] in sources and s['frames']-extra>=60
   following=dict(s,key=visual['balance']['study'],sourcePoint=0,start=s['start']+s['frames']-extra,frames=extra)
   s['frames']-=extra;rows.insert(chosen+1,following);plan['gameFrames']=target
 if EP=='A04':
  rows[0]['mark']="drawbox=x=357:y=262:w=520:h=370:color=0x4AB6FA@0.9:t=8:enable='between(t,0.1,1.10)'"
 save(L/'cue-review.json',cues);save(L/'timeline.json',plan);print('Timeline',total,'game',round(game/plan['bodyFrames'],3),'cues',len(cues),flush=True)
def mix():
 t=read(L/'timeline.json');sr=48000;n=t['totalFrames']*800
 wav=L/'voice/narration.wav';ff(['-i',wav,'-af','acompressor=threshold=0.2:ratio=4:attack=3:release=70:makeup=1,loudnorm=I=-16:TP=-2.8:LRA=8','-ar',sr,'-ac',2,'-c:a','pcm_s24le',L/'vo.wav'],'voice-normalize')
 voice,r=sf.read(L/'vo.wav',dtype='float32');dest=np.zeros((n,2),dtype=np.float32);dest[2*sr:2*sr+len(voice)]=voice
 bed=R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3';assert sha(bed)=='06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08'
 ff(['-stream_loop','-1','-i',bed,'-t',n/sr,'-af','loudnorm=I=-33:TP=-9:LRA=8','-ac',2,'-ar',sr,'-c:a','pcm_s24le',L/'music.wav'],'music')
 music,r=sf.read(L/'music.wav',dtype='float32');assert r==sr and len(music)>=n-100
 padded=np.zeros_like(dest);padded[:min(n,len(music))]=music[:n]
 fade=sr//3;padded[:fade]*=np.linspace(0,1,fade)[:,None];padded[-sr:]*=np.linspace(1,0,sr)[:,None]
 dest+=padded;peak=float(np.max(np.abs(dest)));dest*=min(1.,.77/max(.001,peak))
 sf.write(L/'final-mix.wav',dest,sr,subtype='PCM_24')
 ff(['-i',L/'final-mix.wav','-ac',2,'-ar',48000,'-c:a','aac','-b:a','192k',L/'audio.m4a'],'aac')
enc=['-r','60','-c:v','h264_nvenc','-preset','p4','-cq','19','-b:v','0','-bf','0','-g','120','-pix_fmt','yuv420p','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
def typeface(px,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('malgunbd.ttf' if bold else 'malgun.ttf'),px)
def overlay(s,native):
 im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im);key=s['key']
 game=visual['gameTitles'].get(key,'언리얼 · 자체 동작 시연');focus=s['focus']
 f=typeface(34,True);width=math.ceil(d.textlength(game,font=f))+48
 d.rounded_rectangle((42,37,42+width,100),radius=11,fill=(12,26,22,238));d.text((65,49),game,font=f,fill='#e7efe7')
 if native:
  f=typeface(40,True)
  for i,txt in enumerate(visual['studyLabels'][key]):
   x=90+i*920;w=math.ceil(d.textlength(txt,font=f))+48;d.rounded_rectangle((x,130,x+w,202),radius=8,fill='#28443a');d.text((x+18,142),txt,font=f,fill='white')
 f=typeface(35,True);width=math.ceil(d.textlength(focus,font=f))+42
 d.rounded_rectangle((46,804,46+width,870),radius=9,fill=(15,26,22,235));d.text((65,815),focus,font=f,fill='#f5d983')
 file=V/f"label-{s['index']:03}.png";im.save(file);return file
def picture():
 t=read(L/'timeline.json');pieces=t['cuts'];files=[]
 def cut(job):
  ix,s=job;s['index']=ix;key=s['key'];n=s['frames'];own=key not in t['sourceEvidence'];file=(L/(key+'.mp4')) if own else (R/t['sourceEvidence'][key]['file']);mark=overlay(s,own);dst=V/f'cut-{ix:03}.mp4'
  if own:
   # A native-rate run first, followed by frame-by-frame inspection of the same authored action.
   # Build a 6-second study sequence: 2 seconds original + 2 seconds at 1/4 + two held poses.
   # Animation is explicitly identified as an illustration; actual game shots always retain native rate.
   src=L/(key+'.mp4')
   if not src.exists():raise FileNotFoundError(src)
   raw=['-stream_loop','-1','-i',V/(key+'-study.mp4')]
  else:raw=['-ss',s['sourcePoint'],'-i',file]
  g='[0:v]fps=60,setsar=1[v];[v][1:v]overlay=0:0,format=yuv420p[out]'
  if not own and s.get('mark'):
   g=g.replace('fps=60,setsar=1','fps=60,setsar=1,'+s['mark'])
  ff(['-filter_complex_threads','2','-threads','3',*raw,'-i',mark,'-filter_complex',g,'-map','[out]','-an','-frames:v',n,*enc,dst],f'encode-{ix:03}')
  count=int(next(z for z in probe(dst)['streams'] if z['codec_type']=='video')['nb_frames']);assert count==n,(ix,n,count)
  return dst
 for key in visual['rigs']:
  src=L/(key+'.mp4')
  samples=visual.get('studyObservationFrames',{}).get(key,[16,27])
  first,second=samples
  graph=(f'[0:v]split=4[a][b][c][d];[a]trim=start_frame=8:end_frame=63,setpts=PTS-STARTPTS[a0];'
         f'[b]trim=start_frame=14:end_frame={max(second+2,37)},setpts=4*(PTS-STARTPTS),fps=60[b0];'
         f'[c]trim=start_frame={first}:end_frame={first+1},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=1.15[c0];'
         f'[d]trim=start_frame={second}:end_frame={second+1},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0.78[d0];'
         '[a0][b0][c0][d0]concat=n=4:v=1:a=0[out]')
  ff(['-filter_complex_threads','2','-threads','2','-i',src,'-filter_complex',graph,'-map','[out]','-an',*enc,V/(key+'-study.mp4')],'study-'+key)
 with ThreadPoolExecutor(max_workers=2) as pool:files=list(pool.map(cut,enumerate(pieces)))
 listing=V/'parts.txt';listing.write_text(''.join("file '"+f.name+"'\n" for f in files),encoding='ascii')
 ff(['-f','concat','-safe','0','-i',listing,'-c','copy',L/'body.mp4'],'body')
 args=['-filter_complex_threads','2']
 for f in [A01/'branding.mp4',L/'body.mp4',A01/'membership.mp4']:args+=['-threads','2','-i',f]
 args+=['-i',L/'audio.m4a','-filter_complex',';'.join(f'[{i}:v]setsar=1,settb=1/60,setpts=N[v{i}]' for i in range(3))+';[v0][v1][v2]concat=n=3:v=1:a=0,settb=1/60,setpts=N,split=2[c][r];[r]ass='+rel(L/'captions.ko.ass')+'[b]']
 for tag,name in [('c','clean'),('b','captioned')]:args+=['-map','['+tag+']','-map','3:a','-frames:v',t['totalFrames'],'-t',t['totalFrames']/60,*enc,'-c:a','copy','-movflags','+faststart',L/(name+'.mp4')]
 ff(args,'pair')
def verify_collect():
 import importlib.util
 folder=R/'projects/unreal-engine-6-verse-gameplay/production';sys.path.insert(0,str(folder))
 spec=importlib.util.spec_from_file_location('episode_checks',folder/'finish.py');checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker);checker.L=L
 t=read(L/'timeline.json');checker.verify(t);v=read(L/'encoded-verification.json')
 project=read(P/'project.json');project.update(status='local-delivery-user-review-pending',publishReady=False,platformStatus='local-only')
 project['paths'].update(videoClean=rel(L/'clean.mp4'),videoBurnedCaptions=rel(L/'captioned.mp4'),captionsKo=rel(L/'captions.ko.srt'),captionsEn=rel(L/'captions.en.srt'),audioMix=rel(L/'final-mix.wav'),timeline=rel(H/'edit-plan-final.json'))
 project['delivery']['captionedMasterSha256']=v['masters']['captioned']['sha256'];save(H/'edit-plan-final.json',t);save(P/'project.json',project)
 subprocess.run(['node','scripts/collect-video-output.cjs',P.name],cwd=R,check=True)
 dest=L/'delivery/output'/P.name;report=read(P/'production/delivery-output.json');assert all(sha(dest/f['name'])==f['sha256'] for f in report['files'])
 (dest/'sources.txt').write_text('\n'.join(visual['sources'])+'\n',encoding='utf-8');save(dest/'delivery-manifest.json',report)
 save(H/'checkpoint.json',{'episode':EP,'slug':P.name,'revision':'series-v1','status':'local-delivery-user-review-pending','captionedMasterSha256':v['masters']['captioned']['sha256'],'durationSeconds':t['totalFrames']/60,'frames':t['totalFrames'],'gameplayShare':t['gameFrames']/t['bodyFrames'],'bilingualCues':len(read(L/'cue-review.json')),'directory':rel(dest),'files':report['files'],'technicalChecks':v,'sourceSelection':rel(H/'source-selection.json'),'userViewed':False,'wholeHumanListening':False,'platformMutation':False})
if __name__=='__main__':
 {'timing':timing,'mix':mix,'picture':picture,'verify':verify_collect}[sys.argv[2]]()
