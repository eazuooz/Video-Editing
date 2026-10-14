"""Preserve pre-model failure and prepare one corrected CPU ASR attempt."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,psutil,py_compile
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=read(R/'current17-mixed-whole-asr-execution-v2.json')
assert s['exitCode']==1 and s['completed']==0 and 'No module named' in s['error']
try:alive=abs(psutil.Process(s['pid']).create_time()-s['createTime'])<.01
except psutil.NoSuchProcess:alive=False
assert not alive
mix=read(R/'current-mix-execution-v2.json')
for x in mix['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
p=R/'current17-asr-premodel-runtime-failure-v2.json';assert not p.exists()
p.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),actualShellChunk='05a5a8',actualOuterExitCode=1,actualSessionId=None,workerCurrentlyAlive=False,stateSha256=sha(R/'current17-mixed-whole-asr-execution-v2.json'),pid=s['pid'],createTime=s['createTime'],commandLine=s['commandLine'],completedRecognitions=0,modelLoaded=False,existingSlicesPreserved=True,all71ProtectedInputsUnchanged=True,error=s['error'],correctedRuntime='D:/Github/Video-Editing/qwen3-tts/.venv/Scripts/python.exe',runtimeImportCheckActualChunk='b67568',runtimeImportCheckExitCode=0),ensure_ascii=False,indent=2)+'\n','utf-8')
src=(B/'review-motion-current17-mix-v2.py').read_text('utf-8')
src=src.replace("asr-execution-v2.json","asr-execution-v3.json").replace("asr-v2'","asr-v3'").replace("asr-v2.log","asr-v3.log")
out=B/'review-motion-current17-mix-v3.py';assert not out.exists();out.write_text(src,'utf-8');py_compile.compile(str(out),doraise=True)
src=(B/'observe-motion-current17-cpu-resource-v4.py').read_text('utf-8').replace('current17-cpu-resource-v4.json','current17-cpu-resource-v5.json')
out=B/'observe-motion-current17-cpu-resource-v5.py';assert not out.exists();out.write_text(src,'utf-8');py_compile.compile(str(out),doraise=True)
src=(B/'record-motion-current17-asr-exit-v2.py').read_text('utf-8').replace('asr-execution-v2.json','asr-execution-v3.json').replace('asr-v2/asr.json','asr-v3/asr.json')
out=B/'record-motion-current17-asr-exit-v3.py';assert not out.exists();out.write_text(src,'utf-8');py_compile.compile(str(out),doraise=True)
print(json.dumps(dict(failurePreserved=True,workerAlive=False,recognitionResults=0,preparedAttemptVersion=3,protected=71)))
