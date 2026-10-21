"""Restore already selected public FHD game recordings; no new source selection."""
from pathlib import Path
import json,subprocess,hashlib,sys,re
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=R/'shared/output/private-game-math-polish-20261022';O.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
selected=set(sys.argv[1:] or ['M05']);inventory=read(B/'source-restoration-inventory.json');report=read(B/'source-restoration-results.json') if (B/'source-restoration-results.json').exists() else {}
for entry in inventory:
 if not selected.intersection(entry['episodes']):continue
 name=Path(entry['path']).stem
 if len(name)==11:ident=name
 elif name.startswith(('trailmakers-','besiege-','space-engineers-')):ident=name[-11:]
 else:continue
 assert re.fullmatch('[A-Za-z0-9_-]{11}',ident)
 auth=read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations']['private-math-overnight-polish-20261022'];assert auth['status']=='active' and selected<=set(auth['ids'])
 target=R/entry['path'];target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and report.get(entry['path'],{}).get('verifiedFhd'):continue
 log=O/f'download-{ident}.log'
 command=[R/'qwen3-tts/.venv/Scripts/python.exe','-m','yt_dlp','--no-playlist','--no-warnings','--retries','2','--socket-timeout','25','--format','bv[height>=1080][height<=1440][fps>=50]/bv[height>=1080][height<=1440]/bv[height>=1080]','--remux-video','mp4','--write-info-json','-o',target,'https://www.youtube.com/watch?v='+ident]
 with log.open('w',encoding='utf8') as f:result=subprocess.run([str(x) for x in command],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if result.returncode:
  report[entry['path']]=dict(status='download-failed',log=log.relative_to(R).as_posix(),verifiedFhd=False);save(B/'source-restoration-results.json',report);print('Source download needs followup',ident,flush=True);continue
 data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)]));v=next(s for s in data['streams'] if s['codec_type']=='video');valid=v['width']>=1920 and v['height']>=1080
 h=hashlib.sha256()
 with target.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 report[entry['path']]=dict(status='restored-needs-current-cut-review' if valid else 'excluded-low-resolution',sourceUrl='https://www.youtube.com/watch?v='+ident,sha256=h.hexdigest(),width=v['width'],height=v['height'],fps=v['r_frame_rate'],duration=data['format']['duration'],verifiedFhd=valid,rights='Existing project selection/rights retained; record current-cut correspondence before production',cutReview='pending');save(B/'source-restoration-results.json',report);print('Restored',ident,v['width'],v['height'],flush=True)
