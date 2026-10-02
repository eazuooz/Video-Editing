from pathlib import Path
import io, json, subprocess
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[5]
DEST = Path(__file__).resolve().parent
groups = {
    'map': ('gm-tutorial', list(range(90, 190, 10))),
    'vignette': ('gm-tutorial', list(range(432, 562, 10))),
    'characters': ('gm-tutorial', list(range(725, 845, 10))),
    'inventory': ('gm-tutorial', list(range(909, 1029, 10))),
    'story-item': ('gm-tutorial', list(range(1205, 1325, 10))),
    'players': ('gm-tutorial', list(range(1650, 1720, 10))+list(range(1770, 1890, 10))),
    'dialogue': ('gameplay-overview', list(range(41, 59, 2))+list(range(118, 138, 2)))
}
for group, (name, timestamps) in groups.items():
    for offset in range(0, len(timestamps), 12):
        times = timestamps[offset:offset+12]
        sheet = Image.new('RGB', (1440, 1188), 'white'); draw = ImageDraw.Draw(sheet)
        for i, seconds in enumerate(times):
            data = subprocess.check_output(['ffmpeg','-v','error','-threads','2','-ss',str(seconds),'-i',str(ROOT/f'shared/assets/game-writing/raw/{name}.mp4'),'-frames:v','1','-vf','scale=480:270','-f','image2pipe','-vcodec','png','-threads','2','-'])
            frame = Image.open(io.BytesIO(data)).convert('RGB')
            x,y = (i%3)*480,(i//3)*297; sheet.paste(frame,(x,y))
            draw.text((x+8,y+276),f'{name} {seconds//60:02d}:{seconds%60:02d}',fill='black')
        target=DEST/f'detail-{group}-{offset//12+1}.jpg';sheet.save(target,quality=95)
        print(target.name,flush=True)
for name,seconds in [('vignette',484),('map',118),('story-item',1263),('players',1687),('dialogue',48)]:
    source='gameplay-overview' if name=='dialogue' else 'gm-tutorial'
    subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(seconds),'-i',str(ROOT/f'shared/assets/game-writing/raw/{source}.mp4'),'-frames:v','1','-threads','2','-y',str(DEST/f'native-{name}-{seconds}.png')],check=True)
