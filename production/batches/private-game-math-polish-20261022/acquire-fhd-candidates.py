"""Finite, explicitly selected inbound candidates; acquisition is not cut approval."""
import sys,datetime,subprocess,os
from polish_common import *
O=R/'shared/output/private-game-math-polish-20261022/fhd-candidates'
O.mkdir(parents=True,exist_ok=True)
selected=sys.argv[1:]
catalog=read(B/'fhd-candidate-catalog.json')
report_path=B/'fhd-candidate-acquisition.json'
report=read(report_path) if report_path.exists() else {}
job=B/'fhd-candidate-job.json'
def state(stage,**kw):save(job,dict(pid=os.getpid(),stage=stage,updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),selected=selected,newTts=False,platformMutation=False,**kw))
for ident in selected:
 auth=read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations']['private-math-overnight-polish-20261022']
 assert auth['status']=='active' and auth['sourceReplacementDecision']['mode']=='same-game-same-action-fhd-replacement'
 item=catalog[ident];target=O/(ident+'.mp4');log=O/(ident+'-download.log')
 if target.exists() and report.get(ident,{}).get('verifiedFhd') and sha(target)==report[ident]['sha256']:continue
 state('downloading',current=ident)
 command=[R/'qwen3-tts/.venv/Scripts/python.exe','-m','yt_dlp','--no-playlist','--no-warnings','--retries','2','--socket-timeout','25','--format','bv[height>=1080][height<=1440][fps>=50]/bv[height>=1080][height<=1440]/bv[height>=1080]','--remux-video','mp4','--write-info-json','-o',target,item['url']]
 with log.open('w',encoding='utf8') as f:result=subprocess.run([str(x) for x in command],stdout=f,stderr=subprocess.STDOUT,cwd=R)
 if result.returncode:
  report[ident]=dict(status='acquisition-failed',log=rel(log),verifiedFhd=False);save(report_path,report);continue
 info=probe(target);v=next(s for s in info['streams'] if s['codec_type']=='video');valid=v['width']>=1920 and v['height']>=1080
 report[ident]=dict(status='acquired-await-actual-footage-and-rights-review',path=rel(target),sha256=sha(target),width=v['width'],height=v['height'],fps=v['r_frame_rate'],duration=float(info['format']['duration']),verifiedFhd=valid,sourceUrl=item['url'],metadata=rel(target.with_suffix('.info.json')),fullMasterApproval=False)
 save(report_path,report);print(ident,report[ident]['status'],v['width'],v['height'],flush=True)
state('finite-acquisition-finished',report=rel(report_path))
