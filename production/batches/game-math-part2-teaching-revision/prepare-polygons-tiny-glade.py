"""Download developer Steam trailer pixels for comparison, without source audio."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,urllib.request,urllib.parse
ROOT=Path(__file__).resolve().parents[3]
parent=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates'
D=parent/'tiny-glade';D.mkdir(exist_ok=True)
metadata=json.loads((parent/'tiny-glade-appdetails.json').read_text(encoding='utf-8-sig'))['2198150']['data']
rows=[]
for movie in metadata['movies']:
    url=movie['hls_h264'];assert urllib.parse.urlparse(url).hostname=='video.akamai.steamstatic.com'
    master=urllib.request.urlopen(url).read().decode();variants=[]
    for spec,relative in re.findall(r'#EXT-X-STREAM-INF:([^\n]+)\n([^#\n]+)',master):
        resolution=re.search(r'RESOLUTION=(\d+)x(\d+)',spec)
        if resolution:variants.append((int(resolution[1])*int(resolution[2]),urllib.parse.urljoin(url,relative.strip())))
    assert variants
    selected=max(variants)[1];file=D/f'tiny-glade-{movie["id"]}.mp4'
    if not file.exists():
        subprocess.run(['ffmpeg','-v','error','-threads','2','-i',selected,'-map','0:v:0','-c:v','copy','-an','-y',str(file)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(file)],creationflags=subprocess.CREATE_NO_WINDOW))
    assert all(s['codec_type']=='video' for s in info['streams'])
    rows.append({'id':f'tiny-glade-{movie["id"]}','name':movie['name'],'file':file.name,'seconds':float(info['format']['duration']),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'primarySource':'https://store.steampowered.com/app/2198150/Tiny_Glade/','hlsSource':url,'selectedVideoVariant':selected,'selectionApproved':False,'rights':'Developer-supplied public Steam footage; human/IP review pending; availability is not licensing approval.'})
    print('Downloaded comparison candidate:',rows[-1]['id'],rows[-1]['seconds'],flush=True)
(D/'inputs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
source=Path(__file__).with_name('prepare-polygons-fresh-review.py').read_text(encoding='utf8')
source=source.replace("O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates'","O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade'")
exec(compile(source,str(Path(__file__).with_name('prepare-polygons-fresh-review.py')),'exec'))
