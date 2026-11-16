"""Read actual finite workers/proofs and update only this selected revision key."""
from pathlib import Path
import copy,importlib.util,json
import psutil
H=Path(__file__).resolve().parent;ROOT=H.parents[2];M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');KEY='explicitOriginalTechTwelve20261115'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def main():
 rows=[];active=[]
 for r in read(H/'selected-clarity-narration-preparation-v84.json')['projects']:
  slug=r['slug'];base=M/slug;v=base/'voice-repair-v84/voice-generation-complete-proof.json';ast=base/'asr-repair-v84/status.json';s=read(ast)if ast.exists()else{};rp=Path(s['review']['path'])if'review'in s else None
  rows.append(dict(order=r['order'],slug=slug,sourceVoiceGenerated=v.exists(),sourceAsrComplete=bool(rp and rp.is_file()),sourceLevelsComplete=bool(rp and(rp.parent/'levels.json').exists()),revisionVideoComplete=False))
  for folder in ['voice-repair-v84','asr-repair-v84']:
   p=base/folder/'worker.json'
   if p.exists():
    d=read(p)
    try:
     proc=psutil.Process(d['pid']);valid=abs(proc.create_time()-d['createTime'])<.001 and slug in proc.cmdline()
    except(psutil.Error,KeyError):valid=False
    if valid:active.append(dict(slug=slug,phase=folder,pid=d['pid'],createTime=d['createTime']))
 assert len(active)<=1,active
 spath=H/'finalize-cpu-preparation-v1.py';spec=importlib.util.spec_from_file_location('clarity_scope_progress',spath);sp=importlib.util.module_from_spec(spec);spec.loader.exec_module(sp)
 for name in ['video-production-control.json','video-worklist.json']:
  path=ROOT/'shared/publishing'/name;raw=path.read_bytes().decode('utf-8-sig');before=json.loads(raw);own=copy.deepcopy(before[KEY]);own['activeRevisionProgress'].update(sourceStages=rows,actualCurrentWorker=active[0]if active else None,sourceVoiceGenerated=sum(x['sourceVoiceGenerated']for x in rows),sourceAsrComplete=sum(x['sourceAsrComplete']for x in rows),sourceLevelsComplete=sum(x['sourceLevelsComplete']for x in rows))
  own['currentSelectedProject']=active[0]['slug']if active else None;updated=sp.replace_value(raw,KEY,own);after=json.loads(updated)
  assert {k:v for k,v in before.items()if k!=KEY}=={k:v for k,v in after.items()if k!=KEY}
  if updated!=raw:path.write_bytes(updated.encode('utf8'))
 print(json.dumps(dict(sourceVoices=sum(x['sourceVoiceGenerated']for x in rows),sourceAsr=sum(x['sourceAsrComplete']for x in rows),sourceLevels=sum(x['sourceLevelsComplete']for x in rows),active=active),ensure_ascii=False))
if __name__=='__main__':main()
