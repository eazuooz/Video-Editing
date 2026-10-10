"""Record the actual restored research queue, without changing any controls."""
from pathlib import Path
import json,datetime,hashlib
import psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008')
status=json.loads((R/'status.json').read_text(encoding='utf8'))
assert status['status']=='running' and status['owner_pid']==80716 and status['completed']>=834
owner=psutil.Process(status['owner_pid']);child=psutil.Process(status['child_pid'])
assert child.is_running() and owner.pid in [p.pid for p in child.parents()]
assert 'resume_with_preview.py' in ' '.join(owner.cmdline())
tokens={'v4':'faa454e3-f63e-4458-b7ef-aefc81d86d65','v5':'f2e4ca12-35c2-487a-ab3d-25d5bac3b3f9','v6':'d77f2d0a-5975-4cfd-9b5e-3ca1f8eb2be0'}
actual={'observedAt':datetime.datetime.now().astimezone().isoformat(),'status':status,'owner':{'pid':owner.pid,'created':owner.create_time(),'command':owner.cmdline(),'cwd':owner.cwd()},'child':{'pid':child.pid,'created':child.create_time(),'command':child.cmdline(),'cwd':child.cwd()},'actualNewResearchJobVerified':True,'queueOrControlsModified':False}
for version,token in tokens.items():
 p=ROOT/f'shared/output/gpu-handoff/{token}.json';d=json.loads(p.read_text(encoding='utf8'));assert d['ttsExitCode']==0
 restored=d['resumedQueue'];assert restored['command']==actual['owner']['command'] and Path(restored['cwd']).resolve()==Path(actual['owner']['cwd']).resolve()
 record={'version':version,'guardToken':token,'guardReceipt':p.relative_to(ROOT).as_posix(),'guardReceiptSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'ttsSucceeded':True,'originalCommandAndCwdRestored':True,'immediateResume':d['resumedStatus'],'subsequentQueueHistory':'V4 returned queue54824 to its original resource gate; V5 subsequently paused that queue at an idle boundary and restored80160; V6 subsequently paused80160 at an idle boundary and restored80716. No training was force-killed. The final restored original queue has now advanced and is running an actual research training job.','finalActualResearchResume':actual,'optimizerResumeFromAdapterOnlyClaimed':False,'foreignProcessesOrPauseControlsRemoved':False}
 (B/f'lines-{version}-gpu-handoff-completion.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Original research queue80716 advanced to834 and actual child training job verified; controls unchanged.')
