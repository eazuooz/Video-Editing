from pathlib import Path
import json,subprocess,io,re,math,struct
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;R=P.parents[3];L=P/'local'
inv={e['id']:e for e in json.loads((P/'inventory.json').read_text('utf-8'))};f=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
targets={'A06':[133,137,141,145,149,153],'A08':[268,272,276,280,284,288],'A13':[152,155,158,161,164,167],'A14':[167,170,173,176,179,182],'A15':[70,73,76,79,82,85],'A18':[367,369,371,373,375,377]}
for ep,times in targets.items():
 sh=Image.new('RGB',(1920,800),'#101010');d=ImageDraw.Draw(sh);d.text((15,10),ep+' | spoken claim → actual encoded picture',font=f,fill='white')
 for n,t in enumerate(times):
  b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(R/inv[ep]['video']['path']),'-frames:v','1','-vf','scale=640:360','-threads','2','-f','image2pipe','-vcodec','png','-'])
  x=n%3*640;y=40+n//3*380;sh.paste(Image.open(io.BytesIO(b)),(x,y));d.text((x+10,y+360),f'{t//60:02d}:{t%60:02d}',font=f,fill='#ffee99')
 sh.save(L/(ep+'-targeted.jpg'),quality=94)
 print(ep,'targeted',flush=True)
# Distinguish absent narration captions from literal silence in the real encoded mix.
silence=[]
for ep,start,dur in [('A01',15,6),('A04',31,6),('A08',63,6),('A13',46,6)]:
 b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(R/inv[ep]['video']['path']),'-t',str(dur),'-vn','-ac','1','-ar','16000','-f','f32le','-'])
 v=struct.unpack('<'+'f'*(len(b)//4),b);rms=math.sqrt(sum(x*x for x in v)/len(v));peak=max(abs(x) for x in v)
 silence.append({'id':ep,'start':start,'duration':dur,'mixRmsDbfs':20*math.log10(max(rms,1e-12)),'peakDbfs':20*math.log10(max(peak,1e-12)),'method':'Decoded actual captioned MP4 audio; whole mix, not isolated voice. Does not certify listening.'})
(P/'targeted-evidence.json').write_text(json.dumps({'samples':targets,'audioWindows':silence},indent=2)+'\n','utf-8')
