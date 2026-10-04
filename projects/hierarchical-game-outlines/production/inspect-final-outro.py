from pathlib import Path
import hashlib, json, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
WORK=ROOT/'projects/hierarchical-game-outlines/production/final-v1'
DEST=WORK/'outro-pixel-review-v2'
assert not DEST.exists(), 'Review existing extraction; no duplicates.'
DEST.mkdir()
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
PROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
file=ROOT/'shared/output/motion-canvas/hierarchical-game-outlines-membership-outro.mp4'
probe=json.loads(subprocess.check_output([PROBE,'-v','error','-show_streams','-show_format','-of','json',str(file)],text=True))
video=next(s for s in probe['streams'] if s['codec_type']=='video')
assert int(video['nb_frames'])==600 and video['width']==1920 and video['height']==1080 and video['r_frame_rate']=='60/1'
assert not any(s['codec_type']=='audio' for s in probe['streams'])
decode=subprocess.run([FF,'-v','error','-threads','2','-i',str(file),'-f','null','-'],capture_output=True,text=True)
assert decode.returncode==0 and not decode.stderr.strip(), decode.stderr
rows=[]
page=Image.new('RGB',(1920,1120),'white');draw=ImageDraw.Draw(page)
for i,t in enumerate([.6,3,6,9.4]):
    png=DEST/f'{t:.1f}.png'
    subprocess.run([FF,'-v','error','-ss',str(t),'-i',str(file),'-frames:v','1',str(png)],check=True)
    img=Image.open(png);img.thumbnail((960,540));x=(i%2)*960;y=(i//2)*560
    page.paste(img,(x,y+20));draw.text((x+10,y+3),f'Original member outro / {t}s',fill='black')
    rows.append({'time':t,'file':png.relative_to(ROOT).as_posix()})
page.save(DEST/'page.jpg',quality=95)
(DEST/'index.json').write_text(json.dumps({'file':file.relative_to(ROOT).as_posix(),
    'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'frames':600,'seconds':10,
    'audioStreams':0,'width':1920,'height':1080,'fps':60,'fullDecodeExitCode':0,
    'views':rows,'directReview':'pending','historicalReelOutroRejected':True},indent=2)+'\n',encoding='utf-8')
print('600-frame original-identity outro decoded; four pixel views pending direct review.')
