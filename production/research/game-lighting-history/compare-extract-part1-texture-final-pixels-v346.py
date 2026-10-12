"""Reuse only decoded-identical reviewed pixels; extract every changed prior QA point."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw,ImageFont
spec=importlib.util.spec_from_file_location('m',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT;R=ROOT/'production/research/game-lighting-history';P=ROOT/'projects/game-lighting-history-04/production'
bp=P/'part1-reviewed-pair-build-v345.json';pair=m.read(bp)
assert m.read(P/'part1-reviewed-pair-execution-v345.json')['status']=='complete'
assert pair['identicalAacPayloadPtsDuration'] and all(pair[k]['wholeDecode']['exitCode']==0 and pair[k]['frames']==89148 for k in ['clean','captioned'])
video=ROOT/pair['captioned']['path'];assert m.sha(video)==pair['captioned']['sha256']
layout=m.read(P/'part1-caption-layout-v309.json');visual=m.read(P/'part1-final-visual-build-v344.json')
assert layout['planSha256']==visual['planSha256']==pair['planSha256'] and layout['cueCount']==335
hashes={
 '293':R/'local/part1-decoded-comparison-v314/old293.framemd5',
 '323':R/'local/part1-current-pixel-qa-v324/current323.framemd5',
 '333':R/'local/part1-road-final-pixel-qa-v335/current333.framemd5'}
expected={'293':'4e6219a177417d8dcb12e36aa6af8c3ce65c5a2399844401ec0a23d7e9913b55','323':'a8f17b308981c3f98d55cb7a2a442c62f387743d067e0beab0845cd1e2b7f7ea','333':'e9f39b0f9ee0ca19d240c89831b9fd694c4a4fc1f5257d551fbe7eef379521c9'}
for label,path in hashes.items():assert m.sha(path)==expected[label]
expaths={'293':P/'part1-final-pixel-review-execution-v294.json','323':P/'part1-current-pixel-qa-execution-v327.json','333':P/'part1-road-final-pixel-qa-execution-v335.json'}
reviewpaths={'293':P/'part1-final-board-direct-progress-v297.json','323':P/'part1-current-board-direct-progress-v325.json','333':P/'part1-road-final-direct-review-v337.json'}
exs={};reviews={}
for label,p in expaths.items():
    exs[label]=m.read(p);reviews[label]=m.read(reviewpaths[label]);assert exs[label]['status']=='complete' and exs[label]['exitCode']==0
assert all(b['directlyRead'] for b in reviews['293']['records']) and len(reviews['293']['records'])==378
assert reviews['323']['allNewCurrentBoardsDirectlyRead'] and len(reviews['323']['records'])==96
assert reviews['333']['all17BoardsDirectlyRead'] and all(b['allConstituentFramesDirectlyRead'] for b in reviews['333']['boards'])
out=R/'local/part1-texture-final-pixel-qa-v346';sp=P/'part1-texture-final-pixel-qa-execution-v346.json'
assert not out.exists() and not sp.exists();resources=m.resources();out.mkdir();fd=out/'frames';fd.mkdir()
state=dict(startedAt=m.stamp(),status='comparing-current-decoded-frames',worker=m.worker(),active=None,resources=resources,commands=[],images=[],boards=[],newGitImages=0,allFinalPixelsReviewed=False,qaApproved=False)
def checkpoint():
    cp=R/'checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
    j['episode04Part1TextureFinalPixelsV346']=dict(execution=m.rel(sp),status=state['status'],worker=state['worker'],active=state['active'],images=len(state['images']),boards=len(state['boards']),allFinalPixelsReviewed=False)
    j['ownedActiveWork']=dict(type='one-final-texture-decoded-comparison-and-extraction',execution=m.rel(sp),worker=state['worker'],active=state['active'],cpuThreads=2,gpuJobs=0,next='Direct all changed final boards and every changed full moving interval') if state['status'] not in ['complete','failed'] else dict(status='no-active-owned-media-worker',execution=m.rel(sp),next='Direct changed final boards/full intervals then consolidate current QA')
    m.save(cp,j)
def parse(p):
    rows=[x.split(',') for x in p.read_text().splitlines() if x and not x.startswith('#')]
    assert len(rows)==89148 and [int(x[2]) for x in rows]==list(range(89148))
    return [x[-1].strip() for x in rows]
def runs(ns):
    out=[]
    for n in sorted(ns):
        if out and out[-1][1]==n:out[-1][1]=n+1
        else:out.append([n,n+1])
    return out
m.save(sp,state);checkpoint()
try:
    currentHash=out/'current345.framemd5'
    m.run([m.FF,'-n','-v','error','-nostdin','-threads','2','-i',video,'-map','0:v:0','-an','-fps_mode','passthrough','-c:v','rawvideo','-threads','2','-f','framemd5',currentHash],'current-decoded-frames',state,sp,out)
    cur=parse(currentHash);prior={label:parse(path) for label,path in hashes.items()};changed={i for i,(a,b) in enumerate(zip(cur,prior['333'])) if a!=b}
    ids={'texture-stack-uv:native','texture-project-tile-settings:native'};selected=[c for c in visual['cuts'] if c['id'] in ids];assert len(selected)==2
    permitted=set()
    for c in selected:permitted.update(range(c['fromFrame']-300,c['toFrame']+300))
    assert changed and changed<=permitted,'Distant unexpected encoder changes require inspection before reuse'
    points={}
    def add(f,reason):
        if not 0<=f<89148:return
        p=points.setdefault(f,dict(frame=f,reasons=[]))
        if reason not in p['reasons']:p['reasons'].append(reason)
    for c in selected:
        a,b=c['fromFrame'],c['toFrame']
        for f in range(a,b,30):add(f,'current-texture-motion')
        for f in [a-1,a,a+1,b-1,b,b+1]:add(f,'texture-cut-edge')
        for q in layout['metrics']:
            lo,hi=max(a,q['assFirstFrame']),min(b,q['assExclusiveEndFrame'])
            if hi>lo:
                for f in [lo-1,lo,(lo+hi-1)//2,hi-1,hi]:add(f,'current-texture-ass-cue-edge')
    for a,b in runs(changed):
        for f in [a-1,a,a+1,b-1,b]:add(f,'encoder-difference-edge')
    reuse=[];coverage={}
    for label,ex in exs.items():
        for p in ex['images']:
            f=p['frame'];coverage.setdefault(f,[]).append(label)
            if cur[f]==prior[label][f]:reuse.append(dict(reviewVersion=label,index=p['index'],frame=f,path=p['path'],sha256=p['sha256'],currentDecodedPixelIdentical=True))
    reused={p['frame'] for p in reuse}
    for f,labels in coverage.items():
        if f not in reused:
            for label in labels:
                p=next(p for p in exs[label]['images'] if p['frame']==f)
                for reason in p['reasons']:add(f,reason)
    # Current centisecond ASS positions, including changes that differ from raw SRT
    # planning frames, must be covered by direct current images or exact reviewed pixels.
    requiredCurrent=set()
    for q in layout['metrics']:
        a,b=q['assFirstFrame'],q['assExclusiveEndFrame']
        for f in [a-1,a,(a+b-1)//2,b-1,b]:
            if 0<=f<89148:
                requiredCurrent.add(f)
                if f not in reused:add(f,'all335-current-ass-cue-coverage')
    for c in visual['cuts']:
        a,b=c['fromFrame'],c['toFrame']
        for f in [a-1,a,b-1,b]:
            if 0<=f<89148:
                requiredCurrent.add(f)
                if f not in reused:add(f,'all94-current-cut-coverage')
    assert requiredCurrent<=reused|set(points)
    assert set(coverage)<=reused|set(points)
    allcuts=[dict(id='original-branding',kind='branding',fromFrame=0,toFrame=120),*visual['cuts'],dict(id='original-membership',kind='membership',fromFrame=88548,toFrame=89148)]
    for p in points.values():
        qs=[q for q in layout['metrics'] if q['assFirstFrame']<=p['frame']<q['assExclusiveEndFrame']]
        c=next(c for c in allcuts if c['fromFrame']<=p['frame']<c['toFrame'])
        p.update(visibleCueIds=[q['id'] for q in qs],expectedCaptions=[q['text'] for q in qs],input=c['id'],kind=c['kind'],localFrame=p['frame']-c['fromFrame'])
    moving=[]
    for c in allcuts:
        a,b=c['fromFrame'],c['toFrame'];versions=[label for label in ['333','323','293'] if cur[a:b]==prior[label][a:b]]
        moving.append(dict(id=c['id'],rangeSeconds=[a/60,b/60],frames=b-a,fullIntervalExactVersions=versions,needsFreshCurrentMovingReview=not bool(versions),sourceSha256=pair['captioned']['sha256']))
    comparison=dict(createdAt=m.stamp(),sourceSha256=pair['captioned']['sha256'],frames=89148,exactTo333=89148-len(changed),changedFrames=len(changed),changedRangesExclusive=runs(changed),allChangesConfinedToTwoTextureInputsAndEncoderEdges=True,hashFiles=[dict(path=m.rel(p),sha256=m.sha(p)) for p in [*hashes.values(),currentHash]],movingIntervals=moving)
    comp=P/'part1-texture-current-decoded-comparison-v346.json';m.save(comp,comparison)
    request=dict(preparedAt=m.stamp(),sourceSha256=pair['captioned']['sha256'],pairBuildSha256=m.sha(bp),captionLayoutSha256=m.sha(P/'part1-caption-layout-v309.json'),comparisonSha256=m.sha(comp),points=[points[f] for f in sorted(points)],exactReviewedPixelReuse=reuse,allChangedPriorQaPointsExtracted=True,allHistoricalQaFramesCovered=True,all335CuePlanPreserved=True,all335ActualAssCueBoundariesAnd94CutEdgesCovered=True,requiredCurrentFrameCount=len(requiredCurrent),allFinalPixelsReviewed=False,newGitImages=0,historicalBoardReviews=[dict(path=m.rel(p),sha256=m.sha(p)) for p in reviewpaths.values()])
    m.save(P/'part1-texture-final-pixel-qa-request-v346.json',request)
    state.update(status='extracting-current-texture-pixels');m.save(sp,state);checkpoint()
    filt=out/'exact-current-frames.filter';filt.write_text('select='+'+'.join(f'eq(pts\\,{f*1500})' for f in sorted(points))+'\n','utf8')
    m.run([m.FF,'-n','-v','error','-threads','2','-filter_threads','2','-reinit_filter','0','-i',video,'-filter_script:v',filt,'-fps_mode','vfr','-an','-threads','2',fd/'frame-%05d.png'],'changed-frame-extraction',state,sp,out)
    files=sorted(fd.glob('frame-*.png'));assert len(files)==len(points)
    for i,(file,p) in enumerate(zip(files,request['points'])):
        with Image.open(file) as im:assert im.size==(1920,1080)
        state['images'].append(dict(index=i+1,path=m.rel(file),sha256=m.sha(file),**p))
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
    for i in range(0,len(files),6):
        group=state['images'][i:i+6];board=Image.new('RGB',(2880,1204),(25,25,25));draw=ImageDraw.Draw(board)
        for j,p in enumerate(group):
            x,y=j%3*960,j//3*602
            with Image.open(ROOT/p['path']) as im:board.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,y+62))
            draw.text((x+10,y+6),f"#{p['index']} f{p['frame']} {p['input']} cue{p['visibleCueIds']}",font=font,fill='white')
            draw.text((x+10,y+32),','.join(p['reasons'])[:68],font=font,fill='#e5c873')
        dest=out/f'board-{i//6+1:03d}.png';board.save(dest);state['boards'].append(dict(board=i//6+1,path=m.rel(dest),sha256=m.sha(dest),imageIndices=[p['index'] for p in group],directlyRead=False))
    state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None,source=m.rel(video),sourceSha256=pair['captioned']['sha256'],pairBuildSha256=m.sha(bp),exactReviewedPointsReused=len(reuse));m.save(sp,state);checkpoint()
    print(json.dumps(dict(images=len(files),boards=len(state['boards']),freshFullMovingIntervals=[p['id'] for p in moving if p['needsFreshCurrentMovingReview']],approved=False)))
except BaseException as e:
    state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(sp,state);checkpoint();raise
