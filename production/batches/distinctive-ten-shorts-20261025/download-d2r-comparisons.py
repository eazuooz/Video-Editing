"""Preserve the official site's independent old/new gameplay comparison captures."""
from pathlib import Path
import requests,re,json,subprocess,hashlib
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[3];L=Path(__file__).parent/'local/d2r-official/comparison';L.mkdir(parents=True,exist_ok=True)
page='https://diablo2.blizzard.com/en-us/'
t=requests.get(page,timeout=30);t.raise_for_status()
urls=sorted(set(re.findall(r'https?[^\s\"<>]+?\.mp4',t.text)))
rows=[]
for url in urls:
    p=L/url.rsplit('/',1)[-1]
    if 'comparison_slider' not in p.name:continue
    if not p.exists():
        r=requests.get(url,timeout=60);r.raise_for_status();p.write_bytes(r.content)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
    v=next(s for s in probe['streams'] if s['codec_type']=='video')
    rows.append(dict(sourceUrl=page,fileUrl=url,path=p.relative_to(R).as_posix(),sha256=hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),width=v['width'],height=v['height'],fps=v['r_frame_rate'],duration=float(probe['format']['duration']),audio='no stream' if not any(s['codec_type']=='audio' for s in probe['streams']) else 'present',kind='official independent gameplay comparison capture',actualViewing='pending'))
    print(p.name,v['width'],v['height'],flush=True)
(L/'receipt.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
