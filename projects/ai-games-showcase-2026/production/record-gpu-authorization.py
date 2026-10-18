"""Record the user's availability answer without changing other video scope."""
from pathlib import Path
import datetime,json
R=Path(__file__).resolve().parents[3];P=R/'projects/ai-games-showcase-2026'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
c=read(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']==P.name
c['selectedDelivery'].update(stage='GPU-authorized-bounded-voice-production',gpuStatus='authorized-capacity-checked-at-launch',gpuUserAvailabilityConfirmed=True,gpuUserEvidence='사용 끝났어. GPU 작업 진행해',gpuConfirmedAt=now)
save(R/'shared/publishing/video-production-control.json',c)
m=read(P/'production/tts-manifest.json');m['executionState']='GPU-authorized-ready-for-bounded-batch';m['tts'].update(gpuMinimumFreeMiB=9000,gpuProfileReason='User explicitly confirmed game/Unity use ended. Same approved1.7B model/reference,bfloat16,scene batch1; local weight files total4539706836bytes. Run with hard PyTorch allocator cap8192MiB and minimum9000MiB free; record actual peak per generation. OOM fails this owned job without terminating other applications or CPU fallback. This is a bounded selected-video capacity trial, not a generic threshold change.');save(P/'production/tts-manifest.json',m)
p=read(P/'project.json');p['status']='production';p['tts']['status']='GPU-authorized-bounded-batch';save(P/'project.json',p)
k=read(P/'production/checkpoint.json');k.update(updatedAt=now,stage='GPU-authorized-voice-production',blockers=[],nextAction='Run bounded GPU scene batch; review actual PCM and selected cuts, finish edit and Drive review delivery.');k['gpuAuthorization']={'userEvidence':'사용 끝났어. GPU 작업 진행해','at':now,'forceCloseApplications':False,'CPUFallback':False};save(P/'production/checkpoint.json',k)
p=read(P/'planning/production-plan.json');p['stages']['tts']='GPU-authorized-bounded-batch';p['audio']['gpu']={'authorization':'User confirmed use ended','profile':'GPU-only BF16 scene batch1,9000MiB free,8192MiB allocator cap; measure actual peaks','preserveForeignApplications':True};save(P/'planning/production-plan.json',p)
