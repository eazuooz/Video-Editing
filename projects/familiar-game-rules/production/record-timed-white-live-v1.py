from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
obs=read(PROOF/'timed-white-live-process-observation-v1.json')
assert len(obs['encoder'])==1 and len(obs['vite'])==1 and len(obs['sourceServer'])==1
e=obs['encoder'][0];assert e['ParentProcessId']==obs['vite'][0]['ProcessId']
assert '-threads 2' in e['CommandLine'] and 'familiar-game-rules-timed-white-v1.mp4' in e['CommandLine']
state_path=PROOF/'timed-white-input-render-execution-v1.json';s=read(state_path)
s.update(status='running-single-silent-white-input-render',pid=e['ProcessId'],commandLine=e['CommandLine'],
         actualEncoderCommandObserved=True,creationDate=e['CreationDate'],observedAt=obs['observedAt'],alive=True,
         observation='production/batches/sakurai-planning-game-design/proof-familiar-game-rules/timed-white-live-process-observation-v1.json')
state_path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n','utf-8')
server=read(PROOF/'browser-word-action-review-server-v1.json');server.update(sessionId=48108,observed=obs['sourceServer'][0],alive=True)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    j=read(p);j.update(updatedAt=obs['observedAt'],timedWhiteInputRender=s,browserReviewServer=server)
    p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
p=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(p);it=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
it.update(timedWhiteInputRender=s,browserReviewServer=server);q['updatedAt']=obs['observedAt'];p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(pid=s['pid'],alive=True,threads=2,expectedFrames=9140,finalVideoApproved=False)))
