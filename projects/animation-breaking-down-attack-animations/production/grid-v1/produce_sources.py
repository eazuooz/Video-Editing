"""Acquire separate editor-cleared recordings in their native presentation form."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,sys
P=Path(__file__).resolve().parents[2];D=P/'production/local/grid-v1/sources';D.mkdir(parents=True,exist_ok=True)
def fetch(item):
 name,vid,start,end=item
 base=['yt-dlp','--no-playlist','--js-runtimes','node','--no-warnings']
 url='https://www.youtube.com/watch?v='+vid
 info=json.loads(subprocess.check_output(base+['--skip-download','-J',url]))
 print(name,info.get('license'),info['title'],info['duration'],flush=True)
 (D/(name+'.metadata.json')).write_text(json.dumps({k:info.get(k) for k in ('id','title','uploader','channel','license','description','webpage_url','duration','upload_date')},ensure_ascii=False,indent=2),encoding='utf-8')
 if 'Creative Commons' not in (info.get('license') or ''):return
 path=D/(name+'.mp4')
 if not path.exists():
  args=base+['--no-progress','--no-overwrites','-f','bv[width=1920][height=1080]+ba/b[width=1920][height=1080]','--merge-output-format','mp4','--remux-video','mp4','-o',str(D/(name+'.%(ext)s'))]
  if start is not None:args+=['--download-sections',f'*{start}-{end}','--force-keyframes-at-cuts']
  with (D/(name+'.log')).open('wb') as f:subprocess.run(args+[url],stdout=f,stderr=f,check=True)
 w,h=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',str(path)]).decode().strip().split(',')
 assert [int(w),int(h)]==[1920,1080]
 subprocess.run(['ffmpeg','-hide_banner','-v','error','-y','-i',str(path),'-vf','fps=1/5,scale=270:152,tile=5x6','-frames:v','1',str(D/(name+'-contact.jpg'))],check=True)
if __name__=='__main__':
 jobs=[('duel','VnFpz7ZwNq8',None,None),('great','H69UChNQW0U',15,200)]
 with ThreadPoolExecutor(max_workers=3) as ex:
  for fut in [ex.submit(fetch,j) for j in jobs]:
   try:fut.result()
   except Exception as e:print(type(e).__name__,str(e)[:300],flush=True)
