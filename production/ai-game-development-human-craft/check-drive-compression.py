"""Frame-aligned compression evidence; semantic review stays tied to prior source."""
from pathlib import Path
import json,subprocess,re,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
O=ROOT/'shared/output'/SLUG;Q=O/'drive-compression-qa';Q.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r=read(O/'drive-optimization.json')
assert r['status'].startswith('encoded')
old=ROOT/r.get('preservedSource',r['source']);new=ROOT/r['target']
assert sha(old)==r['sourceSha256'] and sha(new)==r['sha256']
args=['ffmpeg','-hide_banner','-v','info','-i',str(old),'-i',str(new),'-filter_complex',
      '[0:v]setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]ssim=stats_file=frames.txt:shortest=1',
      '-an','-fps_mode','passthrough','-f','null','-']
stats=Q/'frames.txt'
if not stats.exists():
    with (Q/'compare.log').open('wb') as log:subprocess.run(args,cwd=Q,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
values=[]
for line in stats.read_text().splitlines():
    n=int(re.search(r'n:(\d+)',line)[1]);v=float(re.search(r'All:([\d.]+)',line)[1]);assert n==len(values)+1;values.append(v)
assert len(values)==88732
data=read(ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json')
selected=set(sorted(range(len(values)),key=lambda i:values[i])[:30]);ranges=[]
for s in data['scenes']:
    a=120+round(s['start']*60);b=a+round(s['duration']*60)
    worst=min(range(a,b),key=lambda i:values[i]);selected.add(worst);ranges.append({'scene':s['id'],'startFrame':a,'endFrame':b,'minSsim':values[worst],'worstFrame':worst})
selected.update([0,119,120,2232,88131,88132,88731]);selected=sorted(selected)
def expr(v):
    if len(v)==1:return f'eq(round(t*60),{v[0]})'
    m=len(v)//2;return '('+expr(v[:m])+'+'+expr(v[m:])+')'
frames=Q/'frames';frames.mkdir(exist_ok=True)
stamp={'sha256':r['sha256'],'frames':selected}
if not (Q/'input.json').exists():
    assert not list(frames.glob('*.png'))
    (Q/'filter.txt').write_text("select='"+expr(selected)+"',scale=640:360",encoding='ascii')
    subprocess.run(['ffmpeg','-v','error','-i',str(new),'-/filter:v',str(Q/'filter.txt'),'-fps_mode','passthrough',str(frames/'%04d.png')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    (Q/'input.json').write_text(json.dumps(stamp,indent=2)+'\n')
else:assert read(Q/'input.json')==stamp
assert len(list(frames.glob('*.png')))==len(selected)
pages=[]
for start in range(0,len(selected),9):
    page=Image.new('RGB',(1920,1140),(30,30,30));draw=ImageDraw.Draw(page)
    for j,f in enumerate(selected[start:start+9]):
        x=j%3*640;y=j//3*380;page.paste(Image.open(frames/f'{start+j+1:04d}.png'),(x,y));draw.text((x+5,y+361),f'frame {f}  t={f/60:.3f}  SSIM={values[f]:.6f}',fill='white')
    p=Q/f'contact-{start//9+1:02d}.jpg';page.save(p,quality=93);pages.append(p.relative_to(ROOT).as_posix())
result={'status':'pending-direct-compression-quality-review','sourceSha256':r['sourceSha256'],'currentSha256':r['sha256'],'framesCompared':len(values),'meanSsim':sum(values)/len(values),'minSsim':min(values),'comparison':'Every frame aligned by unchanged60fps timestamps; compression evidence, not a substitute for prior semantic/action review.','sceneRanges':ranges,'selectedFrames':selected,'pages':pages}
(Q/'review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['sceneRanges','selectedFrames']}))
