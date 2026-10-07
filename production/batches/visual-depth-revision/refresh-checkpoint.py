"""Observe owned execution files/processes; never infer completion from a missing PID."""
from pathlib import Path
import json,datetime,psutil
ROOT=Path(__file__).resolve().parents[3];folder=ROOT/'production/batches/visual-depth-revision';qpath=folder/'queue.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
q=read(qpath);now=datetime.datetime.now(datetime.timezone.utc).isoformat()
owned=[];foreign=[]
for p in psutil.process_iter(['pid','name','cmdline','create_time']):
 try:
  command=p.info['cmdline'] or [];line=' '.join(command)
  if p.info['name'] not in ['python.exe','pythonw.exe','node.exe','ffmpeg.exe']:continue
  if 'visual-depth-revision' in line and 'refresh-checkpoint.py' not in line:owned.append(p.info)
  elif any(t in line for t in ['train_multiview.py','phase1_train_all_modes','gpu_queue.py','YamYamStudio']):foreign.append(p.info)
 except psutil.Error:pass
for item in q['items']:
 p=ROOT/'projects'/item['slug']/'production/visual-depth-v1'
 preflight=p/'white-preflight-direct-review.json'
 if preflight.exists():
  r=read(preflight);item['preflightDirectReview']=preflight.relative_to(ROOT).as_posix();item['preflightBoardsRead']=r['boardsDirectlyRead'];item['preflightSamplesRead']=r['framesDirectlyRead']
 thumb=ROOT/'projects'/item['slug']/'publishing/thumbnail-depth-v1.json'
 if thumb.exists():item['thumbnailPrepared']=True;item['thumbnailReview']=thumb.relative_to(ROOT).as_posix()
 if not item.get('renderApproved') and item['slug']!='picking-sides' and preflight.exists() and not item.get('pipelineExecution'):item['stage']='authored-preflight-directly-reviewed-awaiting-single-cpu-render'
 if item.get('pipelineExecution'):
  pipeline=read(ROOT/item['pipelineExecution'])
  if pipeline.get('slug')==item['slug'] and pipeline['status']=='running':
   item.update(stage=pipeline['stage'],pipelinePid=pipeline['pid'],activePid=pipeline.get('activePid'),pipelineSessionId=25661)
 if item['slug']=='picking-sides' and not item.get('renderApproved'):
  pair=read(p/'pair-execution.json');boundary=read(p/'boundary-pixel-execution.json') if (p/'boundary-pixel-execution.json').exists() else None
  active=boundary if boundary and boundary['status']=='running' else pair
  item['stage']='post-outro-fix-decoded-body-pixel-comparison' if boundary and boundary['status']=='running' else pair['status']
  item['execution']=(p/('boundary-pixel-execution.json' if active is boundary else 'pair-execution.json')).relative_to(ROOT).as_posix()
  item['sessionId']=50597 if active is boundary else 68399
  for key in ['pid','activePid']:
   pid=active.get(key);live=next((proc for proc in owned if proc['pid']==pid),None)
   if not live and pid:
    try:
     proc=psutil.Process(pid);cmd=proc.cmdline();live=proc.info if hasattr(proc,'info') else dict(pid=pid,cmdline=cmd)
     if not any('visual-depth-v1' in arg for arg in cmd):live=None
    except psutil.Error:live=None
   item[key]=pid if live else None
q['updatedAt']=now;q['currentResourceObservation']=dict(checkedAt=now,method='psutil; CIM permission denied earlier',owned=owned,foreignPreserved=foreign,gpuTtsStarted=0,newTopicsStarted=0)
qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(updatedAt=now,ownedPids=[p['pid'] for p in owned],foreignPreservedPids=[p['pid'] for p in foreign])))
