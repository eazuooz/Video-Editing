from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1';B=Path(__file__).parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=R/'extra-annotation-pieces-execution-v1.json';state=read(sp)
try:
    p=psutil.Process(state['pid']);assert abs(p.create_time()-state['createTime'])>=.01
except psutil.NoSuchProcess:pass
assert not state['pieces']
assert not list((ROOT/'shared/output/cross-game-example-coverage/motion/extra-annotation-pieces-v1').rglob('*.mp4'))
for x in read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
state.update(status='failed-before-decoder-encoder-media',actualOuterExitCode=1,actualOuterSession=None,
             actualOuterCompletion='aca856',finishedAt=datetime.now(timezone.utc).isoformat(),originalWorkerAlive=False,
             error='TypeError Object of type function is not JSON serializable: preparedAt=stamp instead of stamp().',
             decoderEncoderStarted=False,encodedMediaCreated=False,protected71ShaMatchedAfterFailure=True)
sp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
src=B/'render-motion-extra-annotation-pieces-v1.py';dst=B/'render-motion-extra-annotation-pieces-v2.py'
assert not dst.exists()
text=src.read_text('utf-8').replace('extra-annotation-pieces-v1','extra-annotation-pieces-v2').replace('pieces-execution-v1','pieces-execution-v2').replace('pieces-current-cim-v1','pieces-current-cim-v2').replace('pieces-v1.py','pieces-v2.py').replace('preparedAt=stamp,','preparedAt=stamp(),')
compile(text,str(dst),'exec');dst.write_text(text,'utf-8')
cp_path=R/'latest-checkpoint.json';cp=read(cp_path)
cp.update(ownedJob=dict(status='failed-before-media',active=False,sessionId=None,exitCode=1,completion='aca856'),activeOwnedWorkers=0)
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(actualFailure='aca856',exitCode=1,encodedMedia=0,protected=71,recoveryPrepared=dst.name)))
