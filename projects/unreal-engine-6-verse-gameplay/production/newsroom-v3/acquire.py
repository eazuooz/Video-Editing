"""Fetch independent Epic recordings at native FHD for local editorial selection."""
from pathlib import Path
import subprocess,sys,json
from concurrent.futures import ThreadPoolExecutor
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/newsroom-v3';D=L/'sources';D.mkdir(parents=True,exist_ok=True)
CLIPS={'chicago':('mGuaRAWdXPA',None),'bp-preview':('-8xYy39z4fI',None),'graph':('Av2NITegK_0',None),'mcp':('F2cWJFcTft4',None)}
def download(item):
    name,(key,section)=item
    args=['yt-dlp','--js-runtimes','node','--no-playlist','--no-progress','--no-overwrites','--write-info-json','-f','bv[width>=1920][height=1080]/b[width>=1920][height=1080]','--remux-video','mp4','-o',str(D/(name+'.%(ext)s'))]
    if section:args+=['--download-sections',section]
    with (D/(name+'.log')).open('w',encoding='utf-8') as f:
        rc=subprocess.call(args+['https://www.youtube.com/watch?v='+key],stdout=f,stderr=f)
    print(name,rc,flush=True)
    if rc:print((D/(name+'.log')).read_text(encoding='utf-8',errors='replace')[-400:])
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(download,CLIPS.items()))
