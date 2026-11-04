from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json
P=Path(__file__).resolve().parent
items={'donkey-kong':'K7IsUGeFXP0','kirby':'1FPJs_c3qY4','luigi':'LlNXKM3sHWU','wii-fit':'kJbHRv4nCBw','mii':'qdSKO-mc2n8','krool':'pKcXgSV8PTE'}
def run(x):
 name,vid=x
 out=P/f'smash-{name}.%(ext)s'
 r=subprocess.run(['yt-dlp','-f','bv*[height=1080]+ba/b[height=1080]','--merge-output-format','mp4','--write-info-json','--no-playlist','--no-warnings','--no-progress','-o',str(out),'https://www.youtube.com/watch?v='+vid],capture_output=True,text=True,encoding='utf-8',errors='replace')
 (P/f'smash-{name}.download.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
 print(name,r.returncode,flush=True)
 return dict(key=name,id=vid,returnCode=r.returncode)
with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,items.items()))
(P/'additional-download-status.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
