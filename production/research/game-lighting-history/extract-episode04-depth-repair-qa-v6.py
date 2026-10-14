"""Extract observed encoded source-view samples; never approve final video pixels."""
import hashlib, json, os, pathlib, subprocess, sys, datetime
from PIL import Image, ImageDraw, ImageFont

root = pathlib.Path(__file__).resolve().parents[3]
os.chdir(root)
base = pathlib.Path('production/research/game-lighting-history/local/episode04-depth-repairs-v6')
plan = json.loads((base/'plan.json').read_text(encoding='utf-8'))
job = next(j for j in plan['jobs'] if j['name'] == sys.argv[1])
verification_path = pathlib.Path(job['output']).with_suffix('.verification.json')
verification = json.loads(verification_path.read_text(encoding='utf-8'))
if verification['wholeDecodeExitCode'] != 0 or not verification['allPacketPtsAndDurationsApproved']:
    raise RuntimeError('Observed exact PTS and complete decode required')
media = pathlib.Path(verification['media']['path'])
if hashlib.sha256(media.read_bytes()).hexdigest() != verification['media']['sha256']:
    raise RuntimeError('Verified media changed')
live = subprocess.run(['powershell.exe','-NoProfile','-Command',
    "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'ffmpeg.exe' -and $_.CommandLine -match 'game-lighting-history' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],
    capture_output=True,text=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
if live.stdout.strip():
    raise RuntimeError('Another owned FFmpeg worker is live')
out = base/'encoded-qa'/job['name']
if out.exists():
    raise RuntimeError('Preserve existing extraction')
out.mkdir(parents=True)
points = {}
def add(frame, label):
    if not 0 <= frame < job['frames']:
        raise RuntimeError('Frame outside actual media')
    points.setdefault(frame, []).append(label)
for segment in job['scenes']:
    scene = next(s for s in plan['scenes'] if s['id'] == segment['id'])
    start = segment['fromFrame']
    for delta in (-2,-1,0,1,2):
        if 0 <= start+delta < job['frames']:
            add(start+delta, scene['id']+' start boundary '+str(delta))
    add(segment['toFrame']-1, scene['id']+' end')
    for i,cue in enumerate(scene['cues']):
        add(start+(cue['fromFrame']+cue['toFrame']-1)//2,scene['id']+f' cue {i+1}')
    for i,stage in enumerate(scene['stages']):
        add(start+stage['toFrame']-1,scene['id']+f' motion {i+1} end')
frames = sorted(points)
selection = '+'.join(f'eq(n\\,{n})' for n in frames)
cmd = ['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-v','error','-threads','2','-i',str(media),
    '-vf','select='+selection,'-fps_mode','vfr','-frames:v',str(len(frames)),str(out/'frame-%04d.png')]
record_path = out/'extraction.json'
record = {'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':os.getpid(),
    'source':verification['media'],'verification':str(verification_path),'command':cmd,
    'status':'extracting','cpuThreads':2,'gpuJobs':0,'sampling':'Every cue midpoint, every semantic motion end, each scene start/end. Source-view sampling only; all final cue/cut pixels are a separate gate.',
    'frames':frames,'allFinalPixelsReviewed':False,'newGitImages':0}
record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result = subprocess.run(cmd,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
record['ffmpegExitCode'] = result.returncode
if result.returncode:
    record['status']='failed';record['error']=result.stderr
    record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    raise RuntimeError(result.stderr)
images = sorted(out.glob('frame-*.png'))
if len(images) != len(frames):
    raise RuntimeError('Actual image count differs from frame plan')
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
items=[]
for frame, source in zip(frames,images):
    items.append({'frame':frame,'labels':points[frame],'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
boards=[]
for offset in range(0,len(items),4):
    group=items[offset:offset+4]
    board=Image.new('RGB',(1920,1180),'#222222');draw=ImageDraw.Draw(board)
    for cell,item in enumerate(group):
        x=(cell%2)*960;y=(cell//2)*590
        img=Image.open(item['path']).convert('RGB');img.thumbnail((960,540),Image.Resampling.LANCZOS)
        board.paste(img,(x,y+50));draw.text((x+8,y+8),f"f{item['frame']} | {item['labels'][0]}",fill='white',font=font)
    target=out/f'board-{offset//4+1:03d}.jpg';board.save(target,quality=95)
    boards.append({'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'frames':[i['frame'] for i in group]})
record.update(status='complete',completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),items=items,boards=boards,imageCount=len(images),boardCount=len(boards),allSourceSamplesDirectlyReviewed=False)
record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'job':job['name'],'images':len(images),'boards':len(boards),'allFinalPixelsReviewed':False}))
