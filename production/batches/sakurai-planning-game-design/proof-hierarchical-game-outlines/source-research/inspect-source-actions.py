"""Read-only source frames and contact sheets; not a cut/content approval."""
import argparse, json, math, re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[4]
FF = Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
FP = FF.with_name('ffprobe.exe')
parser = argparse.ArgumentParser()
parser.add_argument('video_id')
parser.add_argument('--step', type=float, required=True)
parser.add_argument('--start', type=float, default=0)
parser.add_argument('--end', type=float)
parser.add_argument('--label', default='overview')
parser.add_argument('--seek-overview', action='store_true', help='Coarse discovery only; not exact final-cut frame evidence')
args = parser.parse_args()
source = ROOT / 'shared/assets/game-footage/hierarchical-game-outlines' / (args.video_id + '.mp4')
target = BASE / 'frames' / (args.video_id + '-' + args.label)
target.mkdir(parents=True, exist_ok=True)
data = json.loads(subprocess.check_output([str(FP), '-v','error','-show_streams','-show_format','-of','json',str(source)]))
video = next(x for x in data['streams'] if x['codec_type']=='video')
rate = video['r_frame_rate'].split('/')
fps = float(rate[0])/float(rate[1])
stop = min(args.end or float(data['format']['duration']),float(video.get('duration',data['format']['duration'])))
points = []
t = args.start
while t < stop:
    points.append(round(t * fps))
    t += args.step
expr = '+'.join('eq(n\\,%d)' % n for n in points)
command = [str(FF),'-hide_banner','-threads','2','-i',str(source),'-to',str(stop),'-an','-vf',"select='"+expr+"',showinfo,scale=640:-1",'-fps_mode','vfr','-q:v','3',str(target/'frame-%04d.jpg')]
if args.seek_overview:
    times=[]; logs=[];commands=[]
    for index, n in enumerate(points,1):
        t=n/fps
        cmd=[str(FF),'-hide_banner','-v','error','-threads','1','-ss',str(t),'-i',str(source),'-an','-frames:v','1','-vf','scale=640:-1','-q:v','3',str(target/('frame-%04d.jpg'%index))]
        result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
        commands.append(cmd);logs.append('seek %.6f: %s'%(t,result.stderr))
        if result.returncode: raise RuntimeError('Coarse source seek failed at %.6f'%t)
        times.append(t)
    (target/'extraction.log').write_text('\n'.join(logs),encoding='utf-8')
    command=commands
else:
    result = subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace')
    (target/'extraction.log').write_text(result.stderr,encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Native-frame extraction failed. See log.')
    times = [float(x) for x in re.findall(r'pts_time:([\d.]+)',result.stderr)]
files = sorted(target.glob('frame-*.jpg'))
if len(times)!=len(files) or len(files)!=len(points):
    raise RuntimeError('Unexpected frame sample count: %r' % (len(points),len(times),len(files)))
try:
    font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf',20)
except OSError:
    font = ImageFont.load_default()
sheets = []
rows=[]
for start in range(0,len(files),24):
    chosen=files[start:start+24]
    sheet=Image.new('RGB',(1920,math.ceil(len(chosen)/6)*205),(242,243,242))
    draw=ImageDraw.Draw(sheet)
    for local,f in enumerate(chosen):
        index=start+local
        x=(local%6)*320;y=(local//6)*205
        img=Image.open(f).convert('RGB');img.thumbnail((320,180))
        sheet.paste(img,(x,y))
        draw.text((x+4,y+181),'%03d | %.3fs'%(index+1,times[index]),fill=(0,0,0),font=font)
        rows.append({'index':index+1,'nativeFrame':None if args.seek_overview else points[index],'ptsSeconds':None if args.seek_overview else times[index],'seekSeconds':times[index] if args.seek_overview else None,'file':str(f.relative_to(ROOT)).replace('\\','/')})
    out=target/('sheet-%02d.jpg'%(len(sheets)+1));sheet.save(out,quality=94)
    sheets.append(str(out.relative_to(ROOT)).replace('\\','/'))
record={'videoId':args.video_id,'source':str(source.relative_to(ROOT)).replace('\\','/'),'method':'coarse seek discovery; exact native boundaries still pending' if args.seek_overview else 'linear native-frame selection, source video only; no random seek','start':args.start,'end':stop,'step':args.step,'fps':fps,'command':command,'exitCode':result.returncode,'frameCount':len(rows),'sheets':sheets,'frames':rows,'directReview':'pending','finalCutApproval':False}
(target/'index.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'videoId':args.video_id,'frameCount':len(rows),'sheets':sheets,'status':'awaiting-direct-visual-review'}))
