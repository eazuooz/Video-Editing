"""Source-matched A12 facial passages; no narration or original media mutation."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, io
from PIL import Image, ImageDraw, ImageFont

H=Path(__file__).resolve().parents[1]; R=H.parents[3]
O=Path('C:/Users/1/Videos/YamyamProduction/animation-contrast-v5-work/visual-corrections/A12')
BG='#080c0a'; WHITE='#f3f2ec'; YELLOW='#f2d787'; TEAL='#81cfc5'; RED='#f18b81'; MUTED='#a9b2ac'
FONT={}
SOURCES={
 'acnh-catch-expression':{'file':H/'footage/local/acnh-catch-expression.mp4','sha256':'e6208d06ddd4f31c546e4cba0407c138f867b1b4ab70400b85ad61ae30e174de','audit':H/'footage/acnh-face-detail-audit.json'},
 'lune-clean-camp':{'file':H/'footage/team-b/local/lune-clean-camp.mp4','sha256':'dc41229a4bb9b82243f7d31328fd5767da6019de550fcce65ba6ef57a259448b','audit':H/'footage/team-b/lune-clean-camp.json'}}

def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def rel(p):
 try:return Path(p).resolve().relative_to(R.resolve()).as_posix()
 except ValueError:return Path(p).resolve().as_posix()
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.pending');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(tmp,p)
def text(d,xy,s,size=42,fill=WHITE):
 if size not in FONT:FONT[size]=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size)
 d.text(xy,s,font=FONT[size],fill=fill)
def frame_at(key,t):
 p=O/'source-frames'/f'{key}-{t:06.3f}.png';p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():subprocess.run(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(SOURCES[key]['file']),'-frames:v','1','-threads','1',str(p)],check=True)
 return Image.open(p).convert('RGB'),p
def header(title,kind):
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 text(d,(52,17),title,42,YELLOW)
 if kind=='정지 분석':
  # Match the shared speech-hold chip position inside its x1618 mask.
  text(d,(1630,47),kind,32,YELLOW)
 else:
  text(d,(1450,23),kind,30,WHITE)
 return im
def acnh_panel():
 im=header('Animal Crossing: New Horizons','정지 분석');d=ImageDraw.Draw(im)
 labels=['눈을 뜬 상태','눈을 감는 순간','다시 뜬 눈'];evidence=[]
 for idx,t in enumerate([11.0,11.5,12.0]):
  src,p=frame_at('acnh-catch-expression',t);crop=[700,100,1200,660]
  x=100+idx*610;im.paste(src.crop(crop).resize((500,560),Image.Resampling.LANCZOS),(x,226))
  text(d,(x,140),labels[idx],39,TEAL if idx!=1 else RED)
  text(d,(x,800),f'실제 화면 {t:.1f}초 · 부분 확대',27,MUTED)
  if idx==1:d.rounded_rectangle((x+125,346,x+324,425),radius=12,outline=RED,width=6)
  if idx<2:
   d.line((x+527,487,x+578,487),fill=YELLOW,width=5);d.polygon([(x+580,487),(x+564,476),(x+564,498)],fill=YELLOW)
  evidence.append({'time':t,'file':rel(p),'sha256':sha(p),'cropXYXY':crop,'displayXYWH':[x,226,500,560]})
 return im,evidence
def lune_analysis():
 im=header('Clair Obscur: Expedition 33','정지 분석');d=ImageDraw.Draw(im)
 ev=[]
 for t,crop,x,label in [(13.366,[950,260,1950,960],60,'아래로 향한 시선'),(22.277,[1350,220,2350,920],990,'입 모양과 고개의 방향')]:
  src,p=frame_at('lune-clean-camp',t);im.paste(src.crop(crop).resize((870,609),Image.Resampling.LANCZOS),(x,210));text(d,(x,124),label,39,TEAL if x<100 else YELLOW)
  text(d,(x,835),f'루네 · 실제 화면 {t:.3f}초 · 부분 확대',27,MUTED)
  ev.append({'time':t,'file':rel(p),'sha256':sha(p),'cropXYXY':crop,'displayXYWH':[x,210,870,609]})
 return im,ev
def frames_native(key,start,n):
 # Fixed source aspect; native speed. Keep all source UI and embedded black bars.
 cmd=['ffmpeg','-v','error','-threads','1','-ss',str(start),'-i',str(SOURCES[key]['file']),'-frames:v',str(n),'-vf','fps=60,scale=1516:800:force_original_aspect_ratio=decrease,pad=1516:800:(ow-iw)/2:(oh-ih)/2:color=0x080c0a','-threads','1','-f','rawvideo','-pix_fmt','rgb24','-']
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);size=1516*800*3
 try:
  for _ in range(n):
   data=p.stdout.read(size)
   if len(data)!=size:raise RuntimeError(('short decode',len(data),p.stderr.read().decode('utf8','replace')))
   im=header('Clair Obscur: Expedition 33','실제 게임 · 1×');im.paste(Image.frombytes('RGB',(1516,800),data),(202,80));yield im
 finally:
  p.stdout.close();err=p.stderr.read();rc=p.wait()
  if rc:raise RuntimeError(err.decode('utf8','replace'))
def encode(name,frames,n):
 out=O/(name+'.mp4');log=O/(name+'.log')
 cmd=['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','1','-bf','0','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-frames:v',str(n),'-movflags','+faststart',str(out)]
 count=0
 with log.open('wb')as f:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=f,stderr=f)
  for im in frames:p.stdin.write(im.tobytes());count+=1
  p.stdin.close();rc=p.wait()
 assert rc==0 and count==n,(rc,count,n)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,nb_read_frames','-of','json',str(out)],text=True))['streams'][0]
 assert probe['width']==1920 and probe['height']==1080 and probe['avg_frame_rate']=='60/1' and int(probe['nb_read_frames'])==n
 receipt={'file':rel(out),'sha256':sha(out),'frames':n,'probe':probe,'codeSha256':sha(__file__),'newAudio':False};save(O/(name+'.json'),receipt);return out,receipt
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');a=ap.parse_args();O.mkdir(parents=True,exist_ok=True)
 control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert'A12'in control['episodes']and control['renderAuthorized']
 for key,s in SOURCES.items():assert sha(s['file'])==s['sha256'],key
 ac,ae=acnh_panel();lu,le=lune_analysis()
 for name,im in [('acnh-analysis',ac),('lune-analysis',lu)]:im.save(O/(name+'.png'));im.resize((375,211),Image.Resampling.LANCZOS).save(O/(name+'-375.png'))
 plan={'episode':'A12','scope':'Two source-matched facial passages, visual only','ranges':{'001':[494,644],'038':[15341,15802]},'nativeLuneWindows':[[13,16],[21,24]],'sourceFrames':ae+le,'narrationPreserved':True,'publisherAudioStatus':'Existing conditional/source records unchanged; no audio adopted','sourceEvidence':{k:{'file':rel(v['file']),'sha256':v['sha256'],'audit':rel(v['audit'])}for k,v in SOURCES.items()}}
 save(H/'visual-corrections/A12-plan.json',plan)
 if not a.render:return
 names=['A12-correction-000494-000644-blink-analysis','A12-correction-015341-015802-lune-face']
 def lune_frames():
  yield from frames_native('lune-clean-camp',13,180);yield from frames_native('lune-clean-camp',21,180)
  for _ in range(101):yield lu
 outputs=[encode(names[0],(ac for _ in range(150)),150),encode(names[1],lune_frames(),461)]
 rows=[];timing=H/'baseline-sentence-timing.json'
 for index,(out,receipt)in enumerate(outputs):
  sid=['001','038'][index];start,end=plan['ranges'][sid];key=['acnh-catch-expression','lune-clean-camp'][index]
  segments=([{'kind':'still-analysis','offsetFrame':0,'frames':150,'sourceKey':key,'sourceLocalIn':11,'sourceLocalOut':12,'sourceFrameTimes':[11,11.5,12],'sourceSha256':SOURCES[key]['sha256']}]if index==0 else[{'kind':'native-gameplay','offsetFrame':0,'frames':180,'sourceKey':key,'sourceLocalIn':13,'sourceLocalOut':16,'sourceSha256':SOURCES[key]['sha256']},{'kind':'native-gameplay','offsetFrame':180,'frames':180,'sourceKey':key,'sourceLocalIn':21,'sourceLocalOut':24,'sourceSha256':SOURCES[key]['sha256']},{'kind':'still-analysis','offsetFrame':360,'frames':101,'sourceKey':key,'sourceLocalIn':13.366,'sourceLocalOut':22.277,'sourceFrameTimes':[13.366,22.277],'sourceSha256':SOURCES[key]['sha256']}])
  rows.append({'id':names[index],'kind':'authored-explanation','startFrame':start,'endFrame':end,'newFrames':end-start,'picture':rel(out),'pictureSha256':receipt['sha256'],'sourceStartFrame':0,'sourceVerified':True,'narrationEvidence':{'path':rel(timing),'sha256':sha(timing),'sentenceIds':[sid]},'reason':['Retain native catching observation, then hold actual blink close-up comparisons through sentence ending.','Keep Lune visibly present throughout named-character sentence; final close-up analysis survives positive extension.'][index],'mediaSegments':segments,'visualEvidence':plan,'captionSafeBottomY':880,'newAudio':False,'newTts':False,'receipt':rel(O/(names[index]+'.json'))})
 save(H/'visual-corrections/A12.json',{'schemaVersion':1,'episode':'A12','clock':'relations-v4','readyForAssembly':False,'pictureEdits':rows,'sourceCode':rel(__file__),'sourceCodeSha256':sha(__file__),'retainsUsefulNarrationAndOrder':True,'preservesOtherNativeGamePlates':True,'nativeGameplayFramesInPatch':360,'humanFullWatch':False,'modelVisualReview':'Pending actual encoded caption preview before adoption.'})
 print(json.dumps({'readyForQa':True,'outputs':[x[1]for x in outputs]},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
