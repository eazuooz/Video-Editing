"""Bind finite right-pane assets to the root's measured raw-voice clock.

Writes a compositing plan only. No Unity, FFmpeg, TTS, media generation or GPU.
The scene compositor consumes still/video segments and crop-only overlayLayers.
Native motions may continue under the following confirmation sentence; no
silence, stretch, looping or paragraph-start autoplay is introduced.
"""
from pathlib import Path
import argparse,importlib.util,json,re

H=Path(__file__).resolve().parent
def module(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
M=module('v7_right_prepare',H/'right-prepare.py');S=M.S
T=module('v7_right_word_clock',H/'timing.py')
ROOT,P,O=M.ROOT,M.P,M.O
FPS=60;RECT=[980,180,900,660]

def cropped_layers(asset,obj,kind,file,sourceStartFrame=0,sourceFrames=1):
    x=0 if obj=='a'else 450;y=486 if obj=='a'else 565;hh=78 if obj=='a'else 95
    common={'kind':kind,'file':file,'sourceStartFrame':sourceStartFrame,'sourceFrames':sourceFrames,
        'sourceTotalFrames':asset['frames']if kind=='video'else 1,'dimensions':[900,660],
        'freezeFrame':None,'nativeSpeed':1,'sourceGroupId':asset['sourceBeatId']+'-'+obj}
    return [dict(common,cropRect=[x,135,450,350],rect=[x,135,450,350]),
        dict(common,cropRect=[0,y,900,hh],rect=[0,y,900,hh])]

def statefile(asset,frame):
    for row in asset.get('nativeStateFiles',[]):
        if row['sourceFrame']==frame:return row['file']
    if frame==0:return asset['firstFrame']
    if frame==asset['frames']-1:return asset['lastFrame']
    raise ValueError(f'Actual source-state PNG missing: {asset["sourceBeatId"]} frame{frame}')

def segment(scene,start,end,file,kind='still',sourceStartFrame=0,**extra):
    return dict(sceneId=scene,startFrame=start,endFrameExclusive=end,file=file,kind=kind,
        sourceStartFrame=sourceStartFrame,sourceFrames=end-start if kind=='video'else 1,
        freezeFrame=None,rect=RECT,dimensions=[900,660],overlayLayers=[],nativeSpeed=1,**extra)

def literal_frame(clock,sid,line,phrase):
    return round(clock.literal(sid,line,phrase)*FPS)

def base_segment(asset,scene,start,end,frame=0):
    return segment(scene,start,end,statefile(asset,frame),sourceBeatId=asset['sourceBeatId'],sourceStateFrame=frame)

def still_end(asset,scene,start,end,sourceFrame,obj=None,other='last'):
    if not obj:return base_segment(asset,scene,start,end,sourceFrame)
    base=asset['firstFrame']if other=='first'else asset['lastFrame']
    value=segment(scene,start,end,base,sourceBeatId=asset['sourceBeatId'],sourceStateFrame=sourceFrame,
        pairRecomposition={'movingObject':obj,'otherExactState':other})
    value['overlayLayers']=cropped_layers(asset,obj,'still',statefile(asset,sourceFrame))
    return value

def motion_segment(asset,scene,start,lo,hi,obj=None,other='last'):
    duration=hi-lo+1;end=start+duration
    if not obj:return segment(scene,start,end,asset['clip'],'video',lo,sourceBeatId=asset['sourceBeatId'],sourceEndFrameExclusive=hi+1,sourceTotalFrames=asset['frames'])
    value=segment(scene,start,end,asset['firstFrame']if other=='first'else asset['lastFrame'],sourceBeatId=asset['sourceBeatId'],
        pairRecomposition={'movingObject':obj,'otherExactState':other})
    value['overlayLayers']=cropped_layers(asset,obj,'video',asset['clip'],lo,duration)
    return value

def normalize_cut(row,start,end):
    out=dict(row);delta=start-row['startFrame'];out.update(startFrame=start,endFrameExclusive=end)
    if out['kind']=='video':out.update(sourceStartFrame=row['sourceStartFrame']+delta,sourceFrames=end-start)
    out['overlayLayers']=[dict(x,sourceStartFrame=x.get('sourceStartFrame',0)+(delta if x['kind']=='video'else 0),
        sourceFrames=end-start if x['kind']=='video'else 1)for x in row.get('overlayLayers',[])]
    return out

def overlay_intervals(base,overrides,start,end):
    # Finite motion overrides may continue under the next spoken confirmation.
    # A later motion wins only after the earlier motion's native frames finish.
    boundaries=sorted({start,end}|{max(start,min(end,r[k]))for r in base+overrides for k in ['startFrame','endFrameExclusive']})
    out=[]
    for a,b in zip(boundaries,boundaries[1:]):
        if b<=a:continue
        chosen=next((r for r in reversed(overrides)if r['startFrame']<=a and r['endFrameExclusive']>=b),None)
        if chosen is None:chosen=next(r for r in base if r['startFrame']<=a and r['endFrameExclusive']>=b)
        out.append(normalize_cut(chosen,a,b))
    assert out[0]['startFrame']==start and out[-1]['endFrameExclusive']==end
    assert all(a['endFrameExclusive']==b['startFrame']for a,b in zip(out,out[1:]))
    return out

def board_segments(asset,clock,caps,sid,line,start,end,text):
    # Prefer literal terms on a board; otherwise reveal with actual consecutive
    # clause cues. Both are measured speech events, never arbitrary seconds.
    clauses=[c for c in caps if c['scene']==sid and c['line']==line]
    events=[(start,0,'definition title over retained controlled model')]
    previous=start
    for i,row in enumerate(asset['rows'],1):
        terms=[s for s in re.findall(r'[가-힣]{2,}|\d+(?:\.\d+)?',row)if s in text]
        literal=min((text.index(s),s)for s in terms)[1]if terms else None
        at=literal_frame(clock,sid,line,literal)if literal else clauses[min(i-1,len(clauses)-1)]['startFrame']
        at=max(start,previous,min(end-1,at));previous=at
        events.append((at,i,'exact literal '+literal if literal else'current measured clause; check semantic reveal in paired QA'))
    collapsed={at:(count,reason)for at,count,reason in events};times=sorted(collapsed)
    result=[]
    for j,a in enumerate(times):
        b=times[j+1]if j+1<len(times)else end
        if b>a:
            count,reason=collapsed[a];state=asset['states'][count]
            result.append(segment(sid,a,b,state['file'],sourceBeatId=asset['sourceBeatId'],boardRevealCount=count,revealReason=reason))
    return result

def tasks_for(row,asset,clock,line):
    sid=row['targetScene'];pid=row['targetParagraphId'];lineNo=row['targetParagraph'];tasks=[]
    def task(a,phrase,lo,hi,obj=None,other='last'):
        tasks.append(dict(asset=a,nominal=literal_frame(clock,sid,lineNo,phrase),phrase=phrase,lo=lo,hi=hi,obj=obj,other=other))
    if row.get('withinParagraphAssets'):
        return [('switch',x)for x in row['withinParagraphAssets']]
    if row.get('pairActions'):
        for action in row['pairActions']:
            obj=action['object'];wins=[w for w in asset['motionWindows']if w['object']==obj]
            phrases=action.get('stepCues',[])
            if phrases and len(phrases)==len(wins):
                for p,w in zip(phrases,wins):task(asset,p,*w['nativeMotionFrames'],obj,action['fixedOtherFrame'])
            else:task(asset,action['cue'],0,asset['frames']-1,obj,action['fixedOtherFrame'])
    elif row.get('explicitNativeWindows'):
        for w in row['explicitNativeWindows']:task(asset,w['cue'],*w['sourceFrames'])
    else:
        cues=row.get('actionCuePhrases',[])
        wins=[w for w in asset['motionWindows']if w['object']=='a']
        if len(cues)>1 and len(cues)==len(wins):
            for cue,w in zip(cues,wins):task(asset,cue,*w['nativeMotionFrames'])
        else:
            phrase=cues[0]if cues else None
            at=literal_frame(clock,sid,lineNo,phrase)if phrase else line['startFrame']
            tasks.append(dict(asset=asset,nominal=at,phrase=phrase,lo=0,hi=asset['frames']-1,obj=None,other='last'))
    return tasks

def make():
    M.authorized();clock=T.Clock();caps=M.read(P/'production/local/revision-v7-part1/captions/captions.json')['cues']
    data=M.read(O/'right-assets.json');assert data['complete'] and data['scriptSha256']==M.sha(S.SCRIPT)
    assets={x['sourceBeatId']:x for x in data['assets']};plan=M.read(O/'paragraph-plan.json');bindings={x['targetParagraphId']:x for x in plan['paragraphs']}
    scenes=[];warnings=[]
    for scene in clock.timeline['scenes']:
        sid=scene['id'];base=[];overrides=[];last_motion_end=scene['startFrame']
        for j,line in enumerate(scene['lines']):
            pid=line['paragraphId'];row=bindings[pid];asset=assets[row['sourceBeatId']]
            start=scene['startFrame']if j==0 else line['startFrame'];end=scene['lines'][j+1]['startFrame']if j+1<len(scene['lines'])else scene['endFrame']
            canonical=data.get('canonicalAliasComparison',{})
            if pid==canonical.get('targetParagraph'):
                events=[(start,0)]+[(literal_frame(clock,sid,line['line'],cue),i)for i,cue in enumerate(canonical['cues'],1)]
                for i,(a,state)in enumerate(events):
                    b=events[i+1][0]if i+1<len(events)else end
                    if b>a:base.append(segment(sid,a,b,canonical['states'][state]['file'],sourceBeatId=asset['sourceBeatId'],sourceStateFrame=asset['frames']-1,
                        canonicalRepresentativeFocus=state,kindOfPicture='Same exact controlled3D end pose; equivalent angle representatives, not intermediate physical interpolation'))
                continue
            if asset.get('renderer')=='code-native semantic2D overlay':
                base.extend(board_segments(asset,clock,caps,sid,line['line'],start,end,clock.script[sid]['lines'][line['line']-1]));continue
            frame=asset['frames']-1 if row['playState']=='last exact state'else 0
            base.append(base_segment(asset,sid,start,end,frame))
            if row.get('coincidentConfirmationCue'):
                ghost=asset.get('alignedConfirmation');assert ghost
                at=literal_frame(clock,sid,line['line'],row['coincidentConfirmationCue'])
                overrides.append(segment(sid,at,end,ghost['file'],sourceBeatId=asset['sourceBeatId'],kindOfPicture='controlled-model analytical overlap'))
            if not row['nativeMotion']:continue
            tasks=tasks_for(row,asset,clock,line)
            if tasks and isinstance(tasks[0],tuple):
                tasks=[dict(asset=assets[x['sourceBeatId']],nominal=literal_frame(clock,sid,line['line'],x['cue']),phrase=x['cue'],lo=0,hi=assets[x['sourceBeatId']]['frames']-1,obj=None,other='last')for _,x in tasks]
            for n,task in enumerate(tasks):
                a=task['asset'];nominal=task['nominal'];at=max(nominal,last_motion_end)
                if at!=nominal:warnings.append(dict(paragraphId=pid,kind='native-action-after-previous-action',phrase=task['phrase'],nominalCueFrame=nominal,actualStartFrame=at,shiftFrames=at-nominal,needsPairedQA=True))
                motion=motion_segment(a,sid,at,task['lo'],task['hi'],task['obj'],task['other']);motion['paragraphId']=pid;motion['actionCue']=task['phrase'];overrides.append(motion)
                stop=motion['endFrameExclusive'];last_motion_end=stop
                if stop>end:warnings.append(dict(paragraphId=pid,kind='motion-continues-under-following-speech',frames=stop-end,needsPairedQA=True))
                tailEnd=max(stop,min(end,tasks[n+1]['nominal']if n+1<len(tasks)else end))
                if tailEnd>stop:overrides.append(still_end(a,sid,stop,tailEnd,task['hi'],task['obj'],task['other']))
        assert last_motion_end<=scene['endFrame'],(sid,'native action exceeds scene; resolve without stretching voice')
        merged=overlay_intervals(base,overrides,scene['startFrame'],scene['endFrame'])
        for row in merged:
            if int(sid[4:6])<3:
                current=next((l for l in reversed(scene['lines'])if l['startFrame']<=row['startFrame']),scene['lines'][0])
                patch=data.get('pretermReadoutOverrides',{}).get(current['paragraphId'])
                if patch:row['overlayLayers'].append(dict(patch,sourceStartFrame=0,sourceFrames=1,freezeFrame=None))
            assert (ROOT/row['file']).exists()
            if row['kind']=='video':assert row['sourceStartFrame']>=0 and row['sourceFrames']<=assets[row['sourceBeatId']]['frames']-row['sourceStartFrame']
            for layer in row['overlayLayers']:
                assert(ROOT/layer['file']).exists()
                if layer['kind']=='video':assert layer['sourceFrames']<=assets[row['sourceBeatId']]['frames']-layer['sourceStartFrame']
        scenes.append(dict(sceneId=sid,startFrame=scene['startFrame'],endFrameExclusive=scene['endFrame'],visualSegments=merged))
    out={'schemaVersion':1,'part':1,'fps':60,'rightPane':RECT,'inputs':{'timelineSha256':M.sha(H/'timeline.json'),'captionSha256':M.sha(P/'production/local/revision-v7-part1/captions/captions.json'),'rightAssetsSha256':M.sha(O/'right-assets.json'),'implementationSha256':M.sha(Path(__file__))},
        'scenes':scenes,'visualSegments':[r for s in scenes for r in s['visualSegments']],'warnings':warnings,'bodyCoverageNoFrameGaps':True,'nativeSpeed':1,'forcedSilenceFrames':0,'newMediaRendered':False,'status':'exact clock plan; timing warnings and moving paired pixels still require actual review'}
    M.save(O/'right-visual-segments.json',out);print(json.dumps(dict(scenes=len(scenes),segments=len(out['visualSegments']),warnings=len(warnings))))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--build-plan',action='store_true');a=ap.parse_args()
    if a.build_plan:make()
    else:ap.print_help()
