"""Frame-accurate replacement masks, one serialized encode for each clean/captioned pair."""
from common import *
from visuals import draw,picture,fit,BG,WHITE,MUTED,text,game_label,scaled_picture
from studies import SOURCES
import argparse,ast,types,math,time,shutil,socket
from PIL import Image,ImageDraw,ImageFont
import numpy as np

def guard(ep):
 c=read(ROOT/'shared/publishing/video-production-control.json')[KEY]
 assert ep in c['scope'] and c['renderAuthorized'] and not c['youtubeAuthorized']
 assert ep!='A06'

def caption_ass(ep):
 # Same measured 48px fixed boxes as the approved delivery. No typography guessing.
 p=ROOT/'projects/animation-breaking-down-attack-animations/production/grid-v1/caption_pipeline.py'
 tree=ast.parse(p.read_text(encoding='utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'measured_font','geometry','ass_events','ass_stamp'}]
 ns=dict(ImageFont=ImageFont,Path=Path,math=math,FONT_SIZE=48,MAX_WIDTH=1570,LINE_HEIGHT=62,EMPHASIS_COLORS={'term':'0b6b66','result':'1a7f37','problem':'b42318'})
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns)
 header=(ROOT/'projects/animation-breaking-down-attack-animations/production/local/grid-v1/captions.ko.ass').read_text(encoding='utf-8-sig').split('Dialogue:')[0]
 measured=ns['measured_font'](Path('C:/Windows/Fonts/NotoSansKR-VF.ttf'),500);events=[];cues=[]
 for c in srt(WORK/ep/'ko.srt'):
  q=dict(start=c['start'],end=c['end'],ko=c['text'],emphasis={'ko':None});g=ns['geometry'](q['ko'],measured,None,None)
  assert len(g.get('lines',[]))<=2,(ep,c)
  events.append(ns['ass_events'](q,g,'ko'));cues.append(dict(**q,geometry=g))
 dest=WORK/ep/'captions.ko.ass';dest.write_text(header+''.join(events),encoding='utf-8');save(WORK/ep/'caption-layout.json',dict(cues=cues));return dest

def opening_art(e,n):
 p=Path('C:/Users/1/Videos/YamyamProduction/animation-overview-v7')/e['id']
 im=Image.open(p/'overview.png').convert('RGB')
 if n>=e['opening']['roadmapFrame']:
  with Image.open(p/'roadmap.png') as road:im.paste(road,(0,0),road if road.mode=='RGBA' else None)
 return im
def summary_art(e):
 p=Path('C:/Users/1/Videos/YamyamProduction/animation-native-clips-v6')/e['id']/'assembly/summary-layout.png'
 return Image.open(p).convert('RGB')

def merge_intervals(xs):
 ys=[]
 for a,b in sorted(xs):
  if ys and a<=ys[-1][1]:ys[-1]=(ys[-1][0],max(b,ys[-1][1]))
  else:ys.append((a,b))
 return ys

def encoder_options(folder):
 # The user's sharing restriction concerns GPU voice inference. This bounded
 # hardware video encode uses no engine capture or model, and runs after TTS.
 observed=run(['nvidia-smi','--query-gpu=memory.free,utilization.encoder','--format=csv,noheader,nounits'],True).decode().strip().splitlines()[0]
 free,usage=[int(x.strip()) for x in observed.split(',')]
 hardware=free>=1536 and usage<=45
 opts=['-c:v','h264_nvenc','-preset','p5','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-rc-lookahead','0','-bf','3'] if hardware else ['-c:v','libx264','-threads','2','-preset','veryfast','-crf','18']
 save(folder/'encoder.json',dict(encoder='h264_nvenc' if hardware else 'libx264',freeVramMiB=free,existingEncoderPercent=usage,
  gpuInference=False,engineCapture=False,reason='Use bounded hardware encode only with free memory and encoder headroom; sharing-related GPU TTS restriction remains intact.',options=opts,checkedAt=stamp()))
 return opts

def render_signature(e):
 ep=e['id'];a=read(WORK/ep/'audio.json')
 return dict(renderer={n:sha(HERE/n) for n in ['render.py','visuals.py','studies.py']},
  story={k:e.get(k) for k in ['opening','summaryAt','openingGameBank','studyDefinitions','replacementSpans','nativeLeads']},
  baseline=[dict(kind=f['kind'],sha256=f['sha256']) for f in e['baselineFiles']],
  audioSha256=a['audioSha256'],captions={l:sha(WORK/ep/(l+'.srt')) for l in ['ko','en']})

def render_episode(e,limit=None):
 ep=e['id'];guard(ep);scaled_picture.cache_clear();picture.cache_clear();folder=WORK/ep;dest=OUTPUT/ep;dest.mkdir(parents=True,exist_ok=True)
 audio=read(folder/'audio.json');changes=audio['changes'];frames=audio['frames']
 assert not audio.get('captionAlignmentPending'),(ep,'guided clauses need actual-word caption alignment')
 e=dict(e,renderNarrationCues=srt(folder/'ko.srt'))
 files={r['kind']:Path(r['path']) for r in e['baselineFiles']}
 for r in e['baselineFiles']:assert sha(r['path'])==r['sha256'],(ep,'baseline changed')
 ass=caption_ass(ep);audiofile=folder/'final-audio.m4a'
 if not audiofile.exists() or not (folder/'aac.json').exists() or read(folder/'aac.json')['pcmSha256']!=audio['audioSha256']:
  ff('-i',audio['audio'],'-c:a','aac','-b:a','192k','-ar',48000,audiofile);save(folder/'aac.json',dict(pcmSha256=audio['audioSha256'],aacSha256=sha(audiofile)))
 intervals=[(x['start'],x['end']) for x in e['replacementSpans']]
 intervals += [(e['opening']['startFrame'],e['opening']['endFrame']),(round(e['summaryAt']*60),round(e['summaryAt']*60)+600)]
 newintervals=merge_intervals([(map_frame(a,changes),map_frame(b,changes)) for a,b in intervals])
 enable='+'.join(f'gte(t,{a/60:.9f}-0.0000001)*lt(t,{b/60:.9f}-0.0000001)' for a,b in newintervals)
 pts='PTS'+''.join(f'+if(gte(T,{r["oldEndFrame"]/60:.9f}),{r["deltaFrames"]/60:.9f},0)/TB' for r in changes if r['deltaFrames'])
 assarg=ass.as_posix().replace(':','\\:')
 filters=f"[1:v]setpts='{pts}',fps=60[base];[0:v]scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[replacement];[base][replacement]overlay=0:0:enable='{enable}'[picture];[picture]split=2[clean][tocap];[tocap]ass=filename='{assarg}'[captioned]"
 clean=dest/(files['clean.mp4'].stem+'.mp4');captioned=dest/(files['captioned.mp4'].stem+'.mp4')
 if limit:clean=folder/'sample-clean.mp4';captioned=folder/'sample-captioned.mp4';frames=min(frames,round(limit*60))
 cleanpart=clean.with_suffix('.partial.mp4');cappart=captioned.with_suffix('.partial.mp4')
 transport=socket.socket(socket.AF_INET,socket.SOCK_STREAM);transport.bind(('127.0.0.1',0));transport.listen(1);transport.settimeout(60)
 port=transport.getsockname()[1]
 args=['ffmpeg','-nostdin','-v','warning','-y','-filter_complex_threads','2','-thread_queue_size','8','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i',f'tcp://127.0.0.1:{port}',
  '-threads','2','-i',str(files['clean.mp4']),'-i',str(audiofile),'-filter_complex',filters]
 enc=encoder_options(folder)+['-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000',
  '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','copy','-movflags','+faststart']
 args+=['-map','[clean]','-map','2:a:0','-frames:v',str(frames),'-t',f'{frames/60:.9f}',*enc,str(cleanpart),
        '-map','[captioned]','-map','2:a:0','-frames:v',str(frames),'-t',f'{frames/60:.9f}',*enc,str(cappart)]
 bank=e['openingGameBank'];banklength=round((SOURCES[bank][2]-SOURCES[bank][1])*60)
 overview=[opening_art(e,e['opening']['startFrame']),opening_art(e,e['opening']['roadmapFrame'])];summary=summary_art(e)
 blank=Image.new('RGB',(1920,1080),BG).tobytes();spans=e['replacementSpans'];spanidx=0
 started=time.monotonic();last_notice=started
 with (folder/'render.log').open('wb') as log:
  proc=__import__('subprocess').Popen(args,stdin=__import__('subprocess').DEVNULL,stdout=__import__('subprocess').DEVNULL,stderr=log,
   creationflags=__import__('subprocess').CREATE_NO_WINDOW|__import__('subprocess').BELOW_NORMAL_PRIORITY_CLASS)
  try:
   channel,_=transport.accept();transport.close();channel.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,4*1024*1024)
   for newn in range(frames):
    oldn=old_frame(newn,changes)
    while spanidx<len(spans) and oldn>=spans[spanidx]['end']:spanidx+=1
    a,b=e['opening']['startFrame'],e['opening']['endFrame'];recap=round(e['summaryAt']*60)
    if a<=oldn<b:
     im=overview[1 if oldn>=e['opening']['roadmapFrame'] else 0].copy()
     fit(im,picture(bank,(oldn-a)%banklength),(980,258,880,495));data=im.tobytes()
    elif recap<=oldn<recap+600:
     im=summary.copy();fit(im,picture(bank,(oldn-recap)%banklength),(948,266,880,496));data=im.tobytes()
    elif spanidx<len(spans) and spans[spanidx]['start']<=oldn<spans[spanidx]['end']:
     span=dict(spans[spanidx],newFrame=newn);local=newn-map_frame(span['start'],changes)
     lead=next((r for r in e.get('nativeLeads',[]) if map_frame(r['start'],changes)<=newn<map_frame(r['start'],changes)+3*r['framesPerPass']),None)
     if lead:span['nativeLeadFrame']=newn-map_frame(lead['start'],changes);span['nativeLeadBank']=lead['bank']
     else:
      completed=next((r for r in e.get('nativeLeads',[]) if span['start']<r['end'] and span['end']>r['start'] and newn>=map_frame(r['start'],changes)+3*r['framesPerPass']),None)
      if completed:local=newn-map_frame(completed['start'],changes)-3*completed['framesPerPass'];span['nativeLeadCompleted']=True
     im=draw(ep,e,span,local,oldn);data=im.tobytes()
    else:data=blank
    channel.sendall(data)
    if time.monotonic()-last_notice>45:
     print(ep,f'{newn/frames:.0%}',f'{newn/max(.1,time.monotonic()-started):.1f} fps',flush=True);last_notice=time.monotonic()
   channel.shutdown(socket.SHUT_WR);channel.close();code=proc.wait()
  except BaseException:
   transport.close();proc.terminate();proc.wait();raise
 if code:raise RuntimeError((folder/'render.log').read_text(encoding='utf-8',errors='replace')[-5000:])
 cleanpart.replace(clean);cappart.replace(captioned)
 if limit:return
 result=[]
 for kind,p in [('clean.mp4',clean),('captioned.mp4',captioned)]:
  info=__import__('json').loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',p],True))['streams'][0]
  assert (info['width'],info['height'],info['avg_frame_rate'],int(info['nb_frames']))==(1920,1080,'60/1',frames),(ep,kind,info)
  from qa import extract_during_decode,packet_clock
  if kind=='captioned.mp4':extract_during_decode(e,audio,p)
  else:ff('-threads',2,'-i',p,'-map','0:v','-map','0:a','-f','null','NUL')
  clock=packet_clock(p,frames)
  result.append(dict(kind=kind,path=str(p),sha256=sha(p),fullDecode='passed',frames=frames,packetClock=clock))
 for lang in ['ko','en']:
  p=dest/files[lang+'.srt'].name;shutil.copy2(folder/(lang+'.srt'),p);result.append(dict(kind=lang+'.srt',path=str(p),sha256=sha(p)))
 # Both deliveries use exactly the one prepared AAC bitstream.
 hashes=[]
 for p in [clean,captioned]:
  hashes.append(ff('-i',p,'-map','0:a','-c:a','copy','-vn','-f','hash','-hash','sha256','-',capture=True).decode().strip())
 assert len(set(hashes))==1
 receipt=dict(id=ep,title=e['title'],renderSignature=render_signature(e),revision='gameplay-v8',files=result,frames=frames,durationSeconds=frames/60,
  originalReceipt=e['baselineReceipt'],overviewAt=map_frame(e['opening']['startFrame'],changes)/60,overviewEnd=map_frame(e['opening']['endFrame'],changes)/60,
  summaryAt=map_frame(round(e['summaryAt']*60),changes)/60,summaryFrames=600,memberEndingFrames=600,
  replacements=len(spans),sourceStudies=list(e['studyDefinitions']),fourOutputs=True,cleanCaptionedIdenticalAac=True,audioChanges=audio['changes'],
  originalPcmUnchangedOutsideReplacements=True,openingAndRecapSpeechPreserved=True,principleDiagramsLabeled=True,
  internalQa='FHD60/frame count/full decode/AAC passed; encoded topic/transition/mobile inspection pending',
  visualReviewPending=True,humanReviewed=False,platformChanged=False,updatedAt=stamp())
 save(dest/'delivery.json',receipt);print(ep,'four outputs encoded and decoded',flush=True)
 from qa import check_episode
 check_episode(ep)

def preserve_a06(e):
 dest=OUTPUT/'A06';dest.mkdir(parents=True,exist_ok=True);files=[]
 for r in e['baselineFiles']:
  p=dest/Path(r['path']).name
  if not p.exists():shutil.copy2(r['path'],p)
  assert sha(p)==r['sha256'];files.append(dict(r,path=str(p),preservedExactly=True))
 d=read(e['baselineReceipt']);d.update(files=files,revision='gameplay-v8-preserve-A06',preservedExactly=True,sourceReceipt=e['baselineReceipt'],platformChanged=False,
  visualReviewPending=False,noChangedVisuals=True,qaReusedFrom=e['baselineReceipt'])
 save(dest/'delivery.json',d);print('A06 four files retained with identical SHA256',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--episode');p.add_argument('--sample-seconds',type=float);a=p.parse_args()
 for e in read(HERE/'plan.json')['episodes']:
  if a.episode and e['id']!=a.episode:continue
  if e['id']=='A06':preserve_a06(e);continue
  receipt=OUTPUT/e['id']/'delivery.json'
  if receipt.exists() and not a.sample_seconds:
   d=read(receipt)
   if d.get('renderSignature')==render_signature(e) and all(Path(f['path']).exists() and sha(f['path'])==f['sha256'] for f in d['files']):continue
  render_episode(e,a.sample_seconds)
