"""Decode-only pair-clock diagnostics. No master encoding or source changes.

--reinit1 --legacy --frames240 reproduces the boundary reset. Default reinit0
uses the exact production clock prefix read as a literal from render_pair.
--paired includes the actual ASS/split and checks BOTH branch output clocks.
No fps resampling, frame duplication, silence or source edits are permitted.
"""
import argparse
import ast
import inspect
import json
from pathlib import Path
import re
import subprocess
import time
import video_pipeline as v


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',default=str(v.HERE/'edit-plan-final.json'))
    parser.add_argument('--tag',required=True)
    parser.add_argument('--frames',type=int)
    parser.add_argument('--reinit',choices=['0','1'],default='0')
    parser.add_argument('--legacy',action='store_true')
    parser.add_argument('--paired',action='store_true')
    args=parser.parse_args()
    if not re.fullmatch('[a-z0-9-]+',args.tag):
        raise ValueError('Unsafe diagnostic tag')
    plan=v.load(v.current_plan(args.plan));out=v.current_local_output(plan['outputDir'])
    diagnostic=out/'pair-join'/'clock-probes';diagnostic.mkdir(parents=True,exist_ok=True)
    log=diagnostic/(args.tag+'.log');receipt=diagnostic/(args.tag+'.json')
    if log.exists() or receipt.exists():
        raise ValueError('Preserve prior diagnostic files; select a new tag')
    expected=args.frames or plan['totalFrames']
    source=inspect.getsource(v.render_pair)
    assignments=[n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Assign)
                 and any(isinstance(t,ast.Name) and t.id=='clock_prefix' for t in n.targets)]
    prefix=ast.literal_eval(assignments[0].value)
    if args.legacy:
        prefix='[0:v]setpts=N/(60*TB),settb=1/60000,setsar=1,format=yuv420p'
    branches=['clean','captioned'] if args.paired else ['clean']
    if args.paired:
        ass=v.path(plan.get('captionsAss',str(out/'captions.ko.ass')))
        graph=prefix+',split=2[rawclean][capin];[rawclean]showinfo@clean=checksum=0[clean];[capin]ass='+v.filter_path(ass)+',showinfo@captioned=checksum=0[captioned]'
    else:
        graph=prefix+',showinfo@clean=checksum=0[clean]'
    command=[v.binary('ffmpeg'),'-hide_banner','-nostdin','-v','info','-threads','4',
        '-filter_threads','1','-filter_complex_threads','1','-f','concat','-safe','0',
        '-reinit_filter',args.reinit,'-i',str(out/'pair-concat.txt'),'-filter_complex',graph]
    for branch in branches:
        command+=['-map','['+branch+']','-an']
        if args.frames:
            command+=['-frames:v',str(expected)]
        command+=['-fps_mode','passthrough','-f','null','-']
    states={name:{'frames':0,'nResets':0,'filterResetEvents':0,'ptsErrors':0,'firstPts':None,'lastPts':None,'lastFilterN':None,'boundedLookaheadFrames':0,'errors':[]} for name in branches}
    pattern=re.compile(r'showinfo@(clean|captioned).*?\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:')
    started=time.monotonic()
    with log.open('w',encoding='utf-8') as stream:
        process=subprocess.Popen(command,cwd=v.ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,
            text=True,encoding='utf-8',errors='replace')
        for line in process.stderr:
            stream.write(line)
            match=pattern.search(line)
            if not match:
                continue
            branch,n,pts=match.group(1),int(match.group(2)),int(match.group(3))
            state=states[branch];serial=state['frames'];target=serial*1000
            if args.frames and serial>=expected:
                state['boundedLookaheadFrames']+=1
                continue
            if state['lastFilterN'] is not None and n<=state['lastFilterN']:
                state['filterResetEvents']+=1
            state['lastFilterN']=n
            if n!=serial:
                state['nResets']+=1
            if pts!=target:
                state['ptsErrors']+=1
                if len(state['errors'])<12:
                    state['errors'].append({'serial':serial,'filterN':n,'pts':pts,'expectedPts':target})
            if state['firstPts'] is None:
                state['firstPts']=pts
            state['lastPts']=pts;state['frames']+=1
            if branch=='clean' and state['frames']%3000==0:
                print(f"decoded {state['frames']}/{expected}; PTS errors {state['ptsErrors']}",flush=True)
        code=process.wait()
    passed=code==0 and all(s['frames']==expected and s['ptsErrors']==s['nResets']==0
                          and s['firstPts']==0 and s['lastPts']==(expected-1)*1000 for s in states.values())
    result={'status':'pass-exact-decoded-frame-clock' if passed else 'failed-decoded-frame-clock',
        'expectedFramesPerBranch':expected,'timeBase':'1/60000','expectedStepPts':1000,
        'expectedFirstSeconds':0,'expectedLastSeconds':(expected-1)/60,
        'reinitFilter':int(args.reinit),'legacyMetadataNormalization':args.legacy,
        'actualProductionPrefix':not args.legacy,'graph':graph,'branches':states,
        'elapsedSeconds':time.monotonic()-started,'returnCode':code,
        'concat':v.routed_relative(out/'pair-concat.txt'),'concatSha256':v.sha(out/'pair-concat.txt'),
        'pipelineSha256':v.sha(Path(v.__file__)),'log':v.routed_relative(log),'logSha256':v.sha(log),
        'masterEncodingPerformed':False,'frameRateConversionPerformed':False,'sourceMediaModified':False}
    v.save(receipt,result)
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    if not passed:
        raise SystemExit(2)


if __name__=='__main__':
    main()
