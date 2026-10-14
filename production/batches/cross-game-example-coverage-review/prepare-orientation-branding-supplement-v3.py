"""Prepare three missing branding-middle samples; do not repeat the3168 audit."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
s=(B/'extract-orientation-current34-pixels-v2.py').read_text('utf-8-sig')
s=s.replace("choices=['pair']","choices=['branding']").replace('current34-{a.mode}-pixel-v2','current34-{a.mode}-pixel-v3').replace('current34-{a.mode}-pixel-execution-v2','current34-{a.mode}-pixel-execution-v3')
start=s.index("    timing=read(O/'current34-measured-timing-plan-v1.json'); tasks=[]")
end=s.index('    local.mkdir(parents=True);me=psutil.Process()',start)
s=s[:start]+"""    worker=read(O/'current34-final-pair-execution-v3.json')
    assert worker['actualOuterExitCode']==0 and worker['workerDead'] and worker['frames']==65917
    pair=worker['pair'][1]
    tasks=[dict(id='branding-middle',video=pair['path'],videoSha256=pair['sha256'],frames=worker['frames'],points={f:['original-branding-middle-not-in-prior3168'] for f in [30,60,90]})]
"""+s[end:]
p=B/'extract-orientation-branding-supplement-v3.py';assert not p.exists();p.write_text(s,'utf-8');compile(s,str(p),'exec')
rec=(B/'record-orientation-current34-pixels-worker-v2.py').read_text('utf-8-sig').replace("choices=['guides','pair']","choices=['branding']").replace('current34-{a.mode}-pixel-execution-v2','current34-{a.mode}-pixel-execution-v3')
rec=rec.replace("ap.add_argument('--session',type=int,required=True)","ap.add_argument('--session',type=int)")
rec=rec.replace("    assert a.completion and not alive and s['exitCode']==a.outer_exit and read(ss)['sessionId']==a.session", "    assert a.completion and not alive and s['exitCode']==a.outer_exit\n    if ss.exists():assert read(ss)['sessionId']==a.session\n    else:assert a.session is None")
p=B/'record-orientation-branding-supplement-v3.py';assert not p.exists();p.write_text(rec,'utf-8');compile(rec,str(p),'exec')
print('Prepared only: three original branding middle frames30/60/90; no media regenerated.')
