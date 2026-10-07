"""Stop only the verified orchestration parent, preserving its active composition child."""
from pathlib import Path
import json,datetime,psutil
ROOT=Path(__file__).resolve().parents[3];batch=ROOT/'production/batches/visual-depth-revision'
path=batch/'local-review-pipeline-execution.json';s=json.loads(path.read_text('utf-8-sig'))
if s['status']!='running':raise RuntimeError('Inspect current state; no repeated stop')
p=psutil.Process(s['pid']);cmd=p.cmdline()
if len(cmd)!=2 or not cmd[1].replace('\\','/').endswith('production/batches/visual-depth-revision/continue-local-reviews.py'):raise RuntimeError('Owner identity changed')
child=psutil.Process(s['activePid']);childcmd=child.cmdline()
if s['slug']!='hierarchical-game-outlines' or not any(a.replace('\\','/').endswith('/build-reviewed-pair.py') for a in childcmd) or 'hierarchical-game-outlines' not in childcmd:raise RuntimeError('Active job changed; inspect before stopping parent')
observed=dict(parentPid=p.pid,parentCommand=cmd,parentCreatedAt=p.create_time(),preservedChildPid=child.pid,preservedChildCommand=childcmd,reason='Motion exact encoded pixels reject caption-hidden diagram footers and original-outro frame0 flash. Later sources contain the same risky footer region; pause future render dispatch before targeted layout preflight fixes.',checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
p.terminate();p.wait(timeout=5)
s.update(status='dispatch-paused-for-caption-safe-preflight-fixes',pauseObservation=observed,parentAlive=False,activeChildPreserved=child.is_running(),allFinalPixelsReviewed=False)
path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n','utf-8')
(batch/'caption-safe-dispatch-pause.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(parentStopped=True,childPreserved=child.is_running(),childPid=child.pid,foreignProcessesChanged=False)))
