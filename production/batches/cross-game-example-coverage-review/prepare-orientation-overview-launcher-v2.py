"""Preserve the premedia guard failure; restrict worker inventory to executable workers."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,py_compile
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=B/'render-orientation-overview-v1.py';dest=B/'render-orientation-overview-v2.py';assert not dest.exists()
code=src.read_text('utf-8').replace("orientation/current34-overview-v1'","orientation/current34-overview-v2'").replace("current34-overview-render-execution-v1.json'","current34-overview-render-execution-v2.json'").replace("process_iter(['pid','cmdline'])","process_iter(['pid','name','cmdline'])").replace("c=p.info['cmdline'] or [];cmd=' '.join(c)","c=p.info['cmdline'] or [];cmd=' '.join(c)\n  if (p.info['name'] or '').lower() not in ['python.exe','ffmpeg.exe','node.exe']:continue")
assert code!=src.read_text('utf-8');dest.write_text(code,'utf-8');py_compile.compile(str(dest),doraise=True)
r=B/'record-orientation-overview-worker-v2.py';assert not r.exists();r.write_text((B/'record-orientation-overview-worker-v1.py').read_text('utf-8').replace('current34-overview-render-execution-v1','current34-overview-render-execution-v2'),'utf-8');py_compile.compile(str(r),doraise=True)
assert not (O/'current34-overview-render-execution-v1.json').exists() and not (ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-overview-v1').exists()
record=dict(recordedAt=datetime.now(timezone.utc).isoformat(),actualChunk='e55e04',actualOuterExitCode=1,sessionId=None,stateCreated=False,encodedMediaCreated=False,ttsModelStarted=False,sourceCode=src.relative_to(ROOT).as_posix(),sourceCodeSha256=sha(src),failure='Premedia own-worker inventory counted the PowerShell launch ancestor because its command text contains the render script. Inventory was not restricted to python/ffmpeg/node executable workers.',freshNoWorkerAndNoStateToolChunk='see actual tool result before this preparation',v2Change='Restrict executable worker inventory; preserve identical-argv direct Python launcher exemption and all resource/SHA/one-job guards.',v2=dest.relative_to(ROOT).as_posix(),v2Sha256=sha(dest),requestStarted=False,guardBypassed=False)
out=O/'current34-overview-premedia-launcher-failure-v1.json';assert not out.exists();out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print('PreparedV2 only; preserved actualpremedia exit1/noSTATE/noencodedmedia.')
