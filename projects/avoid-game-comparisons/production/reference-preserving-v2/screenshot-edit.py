"""Render only changed diagrams; reuse actual clips and the exact encoded audio."""
from pathlib import Path
import json,subprocess,hashlib,argparse,math
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[4];V=Path(__file__).parent;P=V.parent.parent
B=P/'production/local/reference-preserving-v2/edit';O=P/'production/local/reference-preserving-v2/screenshots-v1';Q=O/'qa';Q.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):return subprocess.run(a,cwd=R,capture_output=True,check=True).stdout
def ff(a,name):
 with (O/(name+'.log')).open('w',encoding='utf8') as f:
  r=subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*a],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError((O/(name+'.log')).read_text(encoding='utf8',errors='replace')[-3000:])
def frames(p):
 s=read_probe(p)['streams'][0];assert(s['width'],s['height'],s['r_frame_rate'])==(1920,1080,'60/1');return int(s['nb_frames'])
def read_probe(p):return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
enc=['-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000']
plan=read(V/'edit-plan.json');changed=[c for c in plan['cuts'] if c['kind']=='explanation'];ass=(B/'captions.ko.ass').relative_to(R).as_posix()
ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['preflight','slices','pair','verify','pixels']);a=ap.parse_args()
if a.stage=='preflight':
 start=(17405+420)/60;src=R/'shared/output/motion-canvas/avoid-comparisons-screenshots-preflight.mp4'
 ff(['-i',str(src),'-vf',f'setpts=PTS+{start}/TB,ass={ass},setpts=PTS-STARTPTS','-an',*enc,str(O/'preflight-captioned.mp4')],'preflight')
 for n,sec in enumerate([.8,2.8,4.8]):
  ff(['-ss',str(sec),'-i',str(O/'preflight-captioned.mp4'),'-frames:v','1','-update','1',str(Q/f'preflight-{n}.png')],f'preflight-{n}')
  with Image.open(Q/f'preflight-{n}.png') as im:im.resize((375,211)).save(Q/f'preflight-mobile-{n}.png')
 print('Actual captions at current global times applied to 5-second preflight')
elif a.stage=='slices':
 control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name
 src=R/'shared/output/motion-canvas/avoid-comparisons-screenshots-v1.mp4';assert frames(src)==plan['mcFrames'];digest=sha(src)
 for c in changed:
  out=O/(c['id']+'.mp4');receipt=O/(c['id']+'-slice.json');sig={'sourceSha256':digest,'startFrame':c['mcStartFrame'],'frames':c['frames']}
  if not(out.exists() and receipt.exists() and read(receipt)==sig):
   ff(['-ss',str(c['mcStartFrame']/60),'-i',str(src),'-an','-frames:v',str(c['frames']),'-vf','fps=60,setsar=1',*enc,str(out)],c['id']);write(receipt,sig)
  assert frames(out)==c['frames']
 files=[B/'branding.mp4',*[(O if c['kind']=='explanation' else B)/(c['id']+'.mp4') for c in plan['cuts']],B/'membership.mp4']
 assert sum(frames(p) for p in files)==plan['totalFrames']
 (O/'concat.txt').write_text('\n'.join("file '"+p.as_posix()+"'" for p in files)+'\n',encoding='utf8')
 write(O/'retained-inputs.json',{'audio':{'path':str(B/'final-mix.m4a'),'sha256':sha(B/'final-mix.m4a')},'captions':{'assSha256':sha(B/'captions.ko.ass'),'koSha256':sha(B/'captions.ko.srt'),'enSha256':sha(B/'captions.en.srt')},'retainedClips':[{'path':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in files if p.parent==B]})
 print('Six new clips; twenty actual clips plus branding/member referenced without modification')
elif a.stage=='pair':
 control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name
 graph=f'[0:v]fps=60,setsar=1,split=2[clean][capin];[capin]ass={ass}[captioned]'
 args=['-f','concat','-safe','0','-i',str(O/'concat.txt'),'-i',str(B/'final-mix.m4a'),'-filter_complex',graph]
 for kind in ['clean','captioned']:args+=['-map',f'[{kind}]','-map','1:a','-frames:v',str(plan['totalFrames']),'-t',str(plan['totalFrames']/60),*enc,'-c:a','copy','-movflags','+faststart',str(O/f'avoid-game-comparisons-screenshots-v1-{kind}.mp4')]
 ff(args,'pair');print('Both screenshot masters encoded with copied AAC')
elif a.stage=='verify':
 results=[]
 for kind in ['clean','captioned']:
  p=O/f'avoid-game-comparisons-screenshots-v1-{kind}.mp4';digest=sha(p);receipt=Q/(kind+'-integrity.json')
  if receipt.exists() and read(receipt).get('sha256')==digest:results.append(read(receipt));continue
  assert frames(p)==plan['totalFrames'];run(['ffmpeg','-v','error','-xerror','-i',str(p),'-f','null','-'])
  lines=run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',str(p)]).decode().splitlines()
  pts=[float(s.split(',')[0]) for s in lines if s.strip() and s.split(',')[0].strip()]
  assert len(pts)==plan['totalFrames'] and all(abs(y-x-1/60)<.00004 for x,y in zip(pts,pts[1:]))
  adts=hashlib.sha256(run(['ffmpeg','-v','error','-i',str(p),'-map','0:a','-c:a','copy','-f','adts','-'])).hexdigest()
  assert adts=='0686ba6400fcc2f4898f0de2fae3aea69cb07a91bb211b726c644eddb0a9906d'
  r={'kind':kind,'path':p.relative_to(R).as_posix(),'sha256':digest,'bytes':p.stat().st_size,'frames':len(pts),'resolution':[1920,1080],'fps':60,'durationSeconds':plan['totalFrames']/60,'fullDecodePassed':True,'ptsMonotonicAndUniform':True,'aacSha256':adts};write(receipt,r);results.append(r)
 retained=read(O/'retained-inputs.json');assert all(sha(R/r['path'])==r['sha256'] for r in retained['retainedClips']);assert sha(B/'final-mix.m4a')==retained['audio']['sha256']
 assert sum(c['frames'] for c in plan['cuts'] if c['kind']=='independent-gameplay')==plan['bodyFrames']*.6
 write(Q/'integrity.json',{'outputs':results,'bodyFrames':plan['bodyFrames'],'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'ratioErrorFrames':0,'unchangedSourceCutsVerified':True,'audioEvidenceReused':'Identical encoded AAC, narration and timestamps; previous ASR and continuity findings retained including pending listening','pixelReview':'pending','humanListening':'pending'});print('Full decode/PTS/FHD60 passed; AAC exactly identical; 60:40 exact')
else:
 samples={};layout=read(B/'caption-layout.json')
 def sample(f,label):samples.setdefault(max(0,min(plan['totalFrames']-1,f)),[]).append(label)
 for c in changed:
  for k in [0,1,15,c['frames']-15,c['frames']-1]:sample(c['startFrame']+k,c['id']+' edge')
  for cue in c['cues']:
   for dt in [.1,.35,.8]:
    off=round((cue+dt)*60)
    if off<c['frames']:sample(c['startFrame']+off,c['id']+' moving reveal')
  for row in layout['rows']:
   if row['end']>c['startFrame']/60 and row['start']<c['endFrame']/60:
    lo=max(row['start'],c['startFrame']/60);hi=min(row['end'],c['endFrame']/60);sample(round((lo+hi)/2*60),f"caption{row['cue']}")
  sample(c['startFrame']-1,c['id']+' join before');sample(c['endFrame'],c['id']+' join after')
 rows=[{'frame':f,'time':f/60,'labels':ls} for f,ls in sorted(samples.items())];write(Q/'pixel-index.json',rows)
 def balanced(xs):
  if len(xs)==1:return xs[0]
  m=len(xs)//2;return '('+balanced(xs[:m])+'+'+balanced(xs[m:])+')'
 vf="select='"+balanced([f'eq(n,{r["frame"]})' for r in rows])+"',scale=640:360:flags=lanczos"
 ff(['-i',str(O/'avoid-game-comparisons-screenshots-v1-captioned.mp4'),'-an','-vf',vf,'-fps_mode','vfr','-c:v','mjpeg','-q:v','2','-threads','1',str(Q/'frame-%04d.jpg')],'pixels')
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
 for page in range(math.ceil(len(rows)/8)):
  chunk=rows[page*8:(page+1)*8];sheet=Image.new('RGB',(1280,390*math.ceil(len(chunk)/2)),'#181818');d=ImageDraw.Draw(sheet)
  for k,row in enumerate(chunk):
   x=k%2*640;y=k//2*390
   with Image.open(Q/f'frame-{page*8+k+1:04d}.jpg') as im:sheet.paste(im,(x,y))
   d.text((x+8,y+364),f"{row['time']:.3f}s {' / '.join(row['labels'])[:48]}",fill='white',font=font)
  sheet.save(Q/f'contact-{page:02d}.jpg')
 print(len(rows),'samples;',math.ceil(len(rows)/8),'contact sheets')
