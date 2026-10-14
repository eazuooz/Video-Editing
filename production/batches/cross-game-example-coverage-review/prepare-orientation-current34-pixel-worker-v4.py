"""New finalV5 selected pixels; inherit only exact cached reviewed V4 pixels."""
from pathlib import Path
import py_compile
B=Path(__file__).resolve().parent
s=(B/'extract-orientation-current34-pixels-v3.py').read_text('utf-8')
for a,b in [('current34-{a.mode}-pixel-v3','current34-{a.mode}-pixel-v4'),('current34-{a.mode}-pixel-execution-v3','current34-{a.mode}-pixel-execution-v4'),('current34-final-pair-execution-v4','current34-final-pair-execution-v5'),("priorp=O/'current34-pair-pixel-execution-v2.json'","priorp=O/'current34-pair-pixel-execution-v3.json'"),("priorreviewp=O/'current34-final-pixels-partial-direct-review-v1.json'","priorreviewp=O/'current34-final-v4-pixels-partial-direct-review-v1.json'"),("assert priorreview['pixelExecutionSha256']==sha(priorp) and priorreview['samplesDirectlyRead']==3168 and priorreview['boardsDirectlyRead']==792","assert priorreview['executionSha256']==sha(priorp) and priorreview['allNewDirectPixelsRead'] and priorreview['samplesDirectlyRead']==818 and priorreview['boardsDirectlyRead']==205"),("bindingp=O/'current34-clearance-caption-bindings-execution-v1.json'","bindingp=O/'current34-06a-caption-clearance-execution-v1.json'"),("bindingreviewp=O/'current34-clearance-caption-pixels-partial-direct-review-v1.json'","bindingreviewp=O/'current34-06a-caption-clearance-sampled-direct-review-v1.json'"),("bindingreview['allSelectedPixelsDirectlyRead'] and bindingreview['samplesDirectlyRead']==557","bindingreview['all32SamplesDirectlyRead'] and len(bindingreview['samples'])==32"),('current34-assembly-inputs-v4','current34-assembly-inputs-v5'),("inputs['changedPieceCount']==8 and inputs['reusedPreparedByteExactPieces']==29","inputs['changedPieceCount']==1 and inputs['reusedPreparedByteExactPieces']==36")]:
 assert a in s,a;s=s.replace(a,b)
needle="    local.mkdir(parents=True);me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)\n"
assert s.count(needle)==1
s=s.replace(needle,"""    me=psutil.Process();own=[]
    for p in psutil.process_iter(['pid','name','cmdline']):
        try:
            c=p.info['cmdline'] or [];cmd=' '.join(c)
            if p.pid==me.pid or (me.parent() and p.pid==me.parent().pid and c[1:]==me.cmdline()[1:]):continue
            if (p.info['name'] or '').lower() in ['python.exe','ffmpeg.exe','node.exe'] and 'cross-game-example-coverage-review' in cmd and any(v in cmd for v in ['review-orientation','render-orientation','extract-orientation','build-orientation','assemble-orientation','review-motion','render-motion','extract-motion']):own.append(p.pid)
        except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    assert not own and read(O/'latest-checkpoint.json')['activeOwnedWorkers']==0
    local.mkdir(parents=True);me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
""")
out=B/'extract-orientation-current34-pixels-v4.py';assert not out.exists();out.write_text(s,'utf-8');py_compile.compile(str(out),doraise=True)
s=(B/'record-orientation-current34-pixels-worker-v3.py').read_text('utf-8').replace('current34-{a.mode}-pixel-execution-v3','current34-{a.mode}-pixel-execution-v4')
out=B/'record-orientation-current34-pixels-worker-v4.py';assert not out.exists();out.write_text(s,'utf-8');py_compile.compile(str(out),doraise=True)
print('Prepared finalV5 QA with prior3170 cached selected pixels, newly repaired06a and all cue/cut points. No old redisplay or old decode.')
