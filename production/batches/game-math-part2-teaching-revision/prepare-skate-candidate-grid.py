"""Native source overview for candidate selection, no playback approval."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-candidates';src=ROOT/'shared/output/game-math-part2-teaching-revision/sources/TPkvx2W8CV8.mp4'
sheet=Image.new('RGB',(1600,8*245),'white');draw=ImageDraw.Draw(sheet)
for i,time in enumerate(range(0,600,20)):
 raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(time),'-i',str(src),'-frames:v','1','-vf','scale=400:225','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
 x=i%4*400;y=i//4*245;sheet.paste(Image.frombytes('RGB',(400,225),raw),(x,y));draw.text((x+8,y+227),f'Skate3 exact native {time}s',fill='black')
sheet.save(D/'skate-native-overview.jpg',quality=95)
info=json.loads(src.with_suffix('.info.json').read_text(encoding='utf8'))
record={'videoId':'TPkvx2W8CV8','url':info['webpage_url'],'title':info['title'],'channel':info['channel'],'description':info['description'],'observedBrowserDate':'2026-10-10','recordingReuseStatementVerified':True,'publicCreditConditionObserved':False,'gameIPHumanReview':'pending','candidateSelected':False,'sourceAudioWillBeDiscarded':True}
(ROOT/'production/batches/game-math-part2-teaching-revision/interpolation-skate-source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Thirty native overview frames and recording-permission provenance; native interval play/compare still pending.')
