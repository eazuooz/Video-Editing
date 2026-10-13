from pathlib import Path
import json,hashlib,datetime,psutil
P=Path(__file__).resolve().parent;R=P.parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
state=read(P/'voice-repair08-execution-v1.json');assert state['status']=='generated-pending-current-asr'
ident=state['worker']
try:assert abs(psutil.Process(ident['pid']).create_time()-ident['createTime'])>.01
except psutil.NoSuchProcess:pass
assert not (R/'shared/output/GPU_HANDOFF.json').exists()
res=read(P/'voice-repair08-resource.json');research=Path('C:/Users/eazuo/renderformer/tmp/gi_ao_runtime_steady_20261013/status.json')
assert sha(research)==res['researchSha256']
for row in state['completed']:assert sha(R/row['path'])==row['sha256']
assert sha(R/'projects/hierarchical-game-outlines/project.json')==state['baselineSha256']
write(P/'voice-repair08-closure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sessionId=50397,actualOuterExitCode=0,completionChunk='416a0d',workerDead=True,ownedLeaseReleased=True,researchUnchanged=True,researchRestarted=False,baselinePreserved=True))
src=(P/'review-ambiguity.py').read_text(encoding='utf-8')
src=src.replace("S=P/'voice-ambiguity.json'", "S=P/'voice-repair08-asr.json'")
src=src.replace("src=P/'generated-narration/chunks/08p01-scene.wav';x,sr=sf.read(src);part=P/'08p01-second-sentence-local.wav';sf.write(part,x[round(3.08*sr):],sr,subtype='PCM_16')", "src=P/'repair08-narration/chunks/08p01s02-scene.wav';x,sr=sf.read(src);part=src")
src=src.replace("contextStart=3.08", "contextStart=0")
src=src.replace("영상 주제와 세부 설명을 묶거나, 공부할 내용과 질문을 정리할 때도 사용할 수 있습니다.", "영상 주제에 세부 설명을 더하거나, 공부할 내용과 질문을 정리할 때도 사용할 수 있습니다.")
(P/'review-repair08.py').write_text(src,encoding='utf-8')
print('Verified actual repair closure; prepared one current repair ASR.')
