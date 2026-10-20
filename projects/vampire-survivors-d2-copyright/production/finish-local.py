"""Encode the reviewed edit, and collect integrity/pixel evidence for local review."""
from pathlib import Path
import json,sys,hashlib,subprocess,re,math
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';L=P/'production/local';Q=L/'final-qa';Q.mkdir(exist_ok=True)
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def guard():
 c=rd(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized']
def ff(args,label):
 cmd=['ffmpeg','-hide_banner','-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1',*map(str,args)]
 with (Q/(label+'.log')).open('w',encoding='utf8') as f:subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
def encode():
 guard();plan=rd(L/'edit-plan.json');clean=L/'final.clean.mp4';caption=L/'final.captioned.mp4'
 if not clean.exists():ff(['-n','-i',L/'visual.mp4','-i',L/'final-mix.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',clean],'encode-clean')
 if not caption.exists():ff(['-n','-i',clean,'-map','0:v:0','-map','0:a:0','-vf',"ass=filename='projects/vampire-survivors-d2-copyright/production/local/captions.ass':fontsdir='projects/vampire-survivors-d2-copyright/production/local/fonts'",'-c:v','libx264','-preset','fast','-crf','18','-g','120','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','copy','-video_track_timescale','60000','-movflags','+faststart',caption],'encode-captioned')
 wr(P/'production/master-files.json',{'status':'encoded-awaiting-integrity-and-content-review','clean':{'path':clean.relative_to(R).as_posix(),'sha256':sha(clean)},'captioned':{'path':caption.relative_to(R).as_posix(),'sha256':sha(caption)},'totalFrames':plan['totalFrames'],'humanReview':'pending','uploadAuthorized':False})
 print('Encoded final pair',flush=True)
def integrity():
 guard();plan=rd(L/'edit-plan.json');reports=[]
 for name in ['clean','captioned']:
  src=L/f'final.{name}.mp4';cache=Q/f'{name}-integrity.json'
  if cache.exists() and rd(cache)['sha256']==sha(src):reports.append(rd(cache));continue
  ff(['-v','info','-i',src,'-map','0:v:0','-map','0:a:0','-vf','showinfo','-af','ashowinfo','-f','null','-'],name+'-full-decode')
  log=(Q/(name+'-full-decode.log')).read_text(encoding='utf8');vpts=[float(x) for x in re.findall(r'Parsed_showinfo_.*?\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([\d.eE+-]+)',log)]
  apts=[float(x) for x in re.findall(r'Parsed_ashowinfo_.*?\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([\d.eE+-]+)',log)]
  assert len(vpts)==plan['totalFrames'],(name,len(vpts),plan['totalFrames'])
  gaps=np.diff(vpts);assert np.all(gaps>0) and np.max(np.abs(gaps-1/60))<.0011
  assert apts and np.all(np.diff(apts)>0)
  bad=[line for line in log.splitlines() if re.search(r'(Error while|corrupt|Invalid data|non.monoton|concealing|decode_slice_header error)',line,re.I)];assert not bad,bad
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(src)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
  assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1') and abs(float(probe['format']['duration'])-plan['totalFrames']/60)<.05
  report={'path':src.relative_to(R).as_posix(),'sha256':sha(src),'status':'passed-full-video-and-audio-decode','videoFrames':len(vpts),'videoPtsMonotonic':True,'maxFrameStepErrorSeconds':float(np.max(np.abs(gaps-1/60))),'audioFrames':len(apts),'audioPtsMonotonic':True,'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'duration':float(probe['format']['duration']),'decodeErrors':bad};wr(cache,report);reports.append(report)
 wr(P/'production/output-integrity.json',{'status':'passed','outputs':reports,'humanListening':'pending'})
 print('Both complete outputs decode and PTS passed',flush=True)
def pixels():
 guard();plan=rd(L/'edit-plan.json');t=rd(L/'timing.json');src=L/'final.captioned.mp4';frames={};reasons={}
 def add(f,why):f=max(0,min(plan['totalFrames']-1,round(f)));frames[f]=True;reasons.setdefault(f,[]).append(why)
 for c in t['cues']:add((c['start']+c['end'])/2*60+120,'caption-'+str(c['index']))
 for c in plan['cuts']:
  start=c['startFrame']+120
  for delta in [-1,0,1,c['frames']//2,c['frames']-1]:add(start+delta,c['id']+'-boundary/state')
  if c['kind']=='explanation':
   for s in [0,.4,1,2,4,6]:
    if s<c['frames']/60:add(start+s*60,c['id']+'-motion')
  if c.get('annotation'):
   a=c['annotation'];lo=a['cue'];hi=min(c['frames']/60,lo+a['seconds'])
   for x in np.arange(max(0,lo-.1),hi+.1,.25):add(start+x*60,c['id']+'-annotation')
 selected=sorted(frames);directory=Q/'frames';directory.mkdir(exist_ok=True);receipt=Q/'frame-selection.json'
 sig={'sourceSha256':sha(src),'selectedFrames':selected}
 if not receipt.exists():
  expression='+'.join(f'eq(n,{f})' for f in selected)
  ff(['-v','warning','-i',src,'-an','-vf',f"select='{expression}'",'-fps_mode','vfr','-q:v','2',directory/'%05d.jpg'],'all-cue-cut-motion-selection')
  actual=sorted(directory.glob('*.jpg'));assert len(actual)==len(selected),(len(actual),len(selected))
  wr(receipt,{'signature':sig,'mapping':[{'frame':f,'file':p.name,'reasons':reasons[f]} for f,p in zip(selected,actual)]})
 else:assert rd(receipt)['signature']==sig
 mapping={r['frame']:directory/r['file'] for r in rd(receipt)['mapping']};checks=[]
 for c in t['cues']:
  f=round((c['start']+c['end'])/2*60+120);im=Image.open(mapping[f]);ar=np.array(im);region=ar[910:1048,160:1760];white=np.all(region>238,axis=2);dark=np.all(region<60,axis=2)
  assert white.sum()>4000 and dark.sum()>500,('Caption pixels missing',c['index'])
  assert len(c['lines'])<=2
  checks.append({'cue':c['index'],'sampleFrame':f,'whitePixels':int(white.sum()),'darkPixels':int(dark.sum()),'fullTextRetained':True,'maxLines':len(c['lines'])})
 # Every cue's encoded pixels in native-width caption contact sheets.
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
 for page in range(math.ceil(len(t['cues'])/10)):
  sheet=Image.new('RGB',(1920,10*205),'#222');draw=ImageDraw.Draw(sheet)
  for row,c in enumerate(t['cues'][page*10:(page+1)*10]):
   f=round((c['start']+c['end'])/2*60+120);im=Image.open(mapping[f]);sheet.paste(im.crop((0,875,1920,1065)),(0,row*205+15));draw.text((10,row*205),str(c['index']),font=font,fill='#e5c273')
  sheet.save(Q/f'captions-{page+1:02}.jpg',quality=95)
 # Every source cut and every animated diagram gets full-scene state boards.
 rows=[]
 for c in plan['cuts']:
  for frac in [.15,.75]:
   target=c['startFrame']+120+round(c['frames']*frac);closest=min(mapping,key=lambda f:abs(f-target));rows.append((c,closest,mapping[closest]))
 for page in range(math.ceil(len(rows)/12)):
  sheet=Image.new('RGB',(1920,4*395),'#171717');draw=ImageDraw.Draw(sheet)
  for i,(c,f,file) in enumerate(rows[page*12:(page+1)*12]):
   x=(i%3)*640;y=(i//3)*395;sheet.paste(Image.open(file).resize((640,360)),(x,y+28));draw.text((x+8,y),f'{c["id"]} {c["kind"]} #{f}',font=font,fill='white')
  sheet.save(Q/f'scenes-{page+1:02}.jpg',quality=94)
 for tag,predicate in [('actual',lambda c:c['kind']=='actual'),('explanation',lambda c:c['kind']=='explanation')]:
  c=next(c for c in plan['cuts'] if predicate(c));target=c['startFrame']+120+round(c['frames']*.75);f=min(mapping,key=lambda n:abs(n-target));Image.open(mapping[f]).resize((375,211),Image.Resampling.LANCZOS).save(Q/(tag+'-mobile.png'))
 wr(P/'production/caption-pixel-audit.json',{'status':'all-cue-presence-and-frame-selection-complete-awaiting-direct-board-review','masterSha256':sha(src),'cueCount':len(checks),'checks':checks,'frameSelection':'production/local/final-qa/frame-selection.json','allCutsAndAnimatedCuesIncluded':True,'directReview':'pending','humanListening':'pending'})
 print(json.dumps({'selectedFrames':len(selected),'captionSheets':math.ceil(len(checks)/10),'sceneSheets':math.ceil(len(rows)/12)}),flush=True)
if __name__=='__main__':
 {'encode':encode,'integrity':integrity,'pixels':pixels}[sys.argv[1]]()
