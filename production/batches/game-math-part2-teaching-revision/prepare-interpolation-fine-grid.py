"""Fine native-source observations for selection; never grants moving approval."""
from pathlib import Path
import subprocess,json,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-candidates'
src=ROOT/'shared/output/game-math-part2-teaching-revision/sources/TPkvx2W8CV8.mp4'
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(src)]))
v=next(s for s in info['streams'] if s['codec_type']=='video')
assert v['avg_frame_rate']=='30000/1001', 'Inspect a changed source time base before sampling'
records=[]
for ident,start,end in [('S1',105,140),('S2',392,442)]:
 times=list(range(start,end,2));sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*250),'white');draw=ImageDraw.Draw(sheet)
 for i,time in enumerate(times):
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(time),'-i',str(src),'-frames:v','1','-vf','scale=400:225','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  x=i%4*400;y=i//4*250;sheet.paste(Image.frombytes('RGB',(400,225),raw),(x,y));draw.text((x+6,y+228),f'{ident} requested source {time}s',fill='black')
 file=D/f'{ident}-fine-native.jpg';sheet.save(file,quality=95)
 records.append({'candidate':ident,'interval':[start,end],'requestedSeconds':times,'sampling':'first decoded native frame at each seek; not a 60fps stride','sheet':str(file.relative_to(ROOT)).replace('\\','/'),'pixelObservation':False})
(D/'skate-fine-sampling.json').write_text(json.dumps({'source':str(src.relative_to(ROOT)).replace('\\','/'),'width':v['width'],'height':v['height'],'nativeFps':v['avg_frame_rate'],'nativeFrameCount':int(v['nb_frames']),'sourceTitle60FpsDoesNotMatchDownloadedStream':True,'records':records},indent=2)+'\n',encoding='utf8')
print('Prepared fine observations; candidate choice and moving review remain separate.')
