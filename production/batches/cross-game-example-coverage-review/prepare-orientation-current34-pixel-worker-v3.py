"""New V4 output QA, retaining cached exact approved pixels without redisplaying them."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
s=(B/'extract-orientation-current34-pixels-v2.py').read_text('utf-8')
s=s.replace('current34-{a.mode}-pixel-v2','current34-{a.mode}-pixel-v3').replace('current34-{a.mode}-pixel-execution-v2','current34-{a.mode}-pixel-execution-v3')
start=s.index("    timing=read(O/'current34-measured-timing-plan-v1.json'); tasks=[]")
end=s.index('    local.mkdir(parents=True);',start)
s=s[:start]+'''    pairp=O/'current34-final-pair-execution-v4.json';worker=read(pairp)
    assert worker['actualOuterExitCode']==0 and worker['workerDead'] and len(worker['pair'])==2
    priorp=O/'current34-pair-pixel-execution-v2.json';prior=read(priorp)
    priorreviewp=O/'current34-final-pixels-partial-direct-review-v1.json';priorreview=read(priorreviewp)
    assert priorreview['pixelExecutionSha256']==sha(priorp) and priorreview['samplesDirectlyRead']==3168 and priorreview['boardsDirectlyRead']==792
    bindingp=O/'current34-clearance-caption-bindings-execution-v1.json';binding=read(bindingp)
    bindingreviewp=O/'current34-clearance-caption-pixels-partial-direct-review-v1.json';bindingreview=read(bindingreviewp)
    assert bindingreview['executionSha256']==sha(bindingp) and bindingreview['allSelectedPixelsDirectlyRead'] and bindingreview['samplesDirectlyRead']==557
    inputs=read(O/'current34-assembly-inputs-v4.json');assert inputs['changedPieceCount']==8 and inputs['reusedPreparedByteExactPieces']==29
    old_by_frame={x['frame']:x for x in prior['results'][0]['samples']}
    points={x['frame']:list(x['reasons'])+['cached-prior-selected-frame'] for x in old_by_frame.values()}
    changed_ids={x['id'] for x in inputs['pieces'] if x['clearanceRepaired']}
    offsets={};boundaries=set();offset=0
    def put(f,reason):
        f=max(0,min(worker['frames']-1,int(f)));points.setdefault(f,[]).append(reason)
    for piece in worker['pieces']:
        offsets[piece['id']]=(offset,offset+piece['frames'])
        for f in [offset-1,offset,offset+piece['frames']-1,offset+piece['frames']]:
            f=max(0,min(worker['frames']-1,f));boundaries.add(f);put(f,'new-assembled-piece-boundary-'+piece['id'])
        offset+=piece['frames']
    assert offset==65917
    for scene in binding['scenes']:
        for x in scene['samples']:put(x['absoluteFrame'],'new-reviewed-current-caption-binding-'+scene['id'])
    for f in [0,59,119,65317,65617,65916]:boundaries.add(f);put(f,'new-final-branding-or-member-boundary')
    alignment=read(O/'current34-caption-alignment-v1.json');assert len(alignment['entries'])==244
    for x in alignment['entries']:
        first=int(x['start']*60+.999999);last=int(x['end']*60+.999999)-1
        for f,k in [(first,'first'),((first+last)//2,'mid'),(last,'last')]:put(f,f'new-final-cue{x["id"]:03d}-{k}')
    pair=worker['pair'][1]
    tasks=[dict(id='captioned',video=pair['path'],videoSha256=pair['sha256'],frames=worker['frames'],points=points)]
''' +s[end:]
s=s.replace("allFinalPixelsApproved=False,newImageGit=0,researchChanges=0)","allFinalPixelsApproved=False,newImageGit=0,researchChanges=0,pairExecution=rel(pairp),pairExecutionSha256=sha(pairp),priorPixelExecution=rel(priorp),priorPixelExecutionSha256=sha(priorp),priorCompleteReview=rel(priorreviewp),priorCompleteReviewSha256=sha(priorreviewp),clearanceBindingReview=rel(bindingreviewp),clearanceBindingReviewSha256=sha(bindingreviewp))")
needle="            boards=[]\n            for off in range(0,len(rows),4):\n"
assert s.count(needle)==1
s=s.replace(needle,'''            direct=[];inherited=[]
            for row in rows:
                sid=next(k for k,(lo,hi) in offsets.items() if lo<=row['frame']<hi)
                row['scene']=sid
                old=old_by_frame.get(row['frame']);exact=False
                if old and sid not in changed_ids and row['frame'] not in boundaries:
                    assert sha(ROOT/old['path'])==old['sha256']
                    exact=row['sha256']==old['sha256']
                    if not exact:
                        with Image.open(ROOT/row['path']) as cur,Image.open(ROOT/old['path']) as prev:
                            exact=cur.size==prev.size and cur.convert('RGB').tobytes()==prev.convert('RGB').tobytes()
                    if exact:row.update(cachedPriorExactPixels=True,priorSamplePath=old['path'],priorSampleSha256=old['sha256'])
                row['requiresNewDirectReview']=not exact
                (inherited if exact else direct).append(row)
            boards=[]
            for off in range(0,len(direct),4):
''')
s=s.replace("enumerate(rows[off:off+4])","enumerate(direct[off:off+4])")
s=s.replace("samples=rows,boards=boards,allSelectedEncodedPtsExact=True,allSamplesDirectlyRead=False)","samples=rows,directReviewSamples=direct,inheritedExactPixelSamples=inherited,boards=boards,allSelectedEncodedPtsExact=True,allSamplesDirectlyRead=False,cachedPriorReviewRedisplayed=False)")
s=s.replace("samples=len(rows),boards=len(boards),exitCode=0)","samples=len(rows),newDirectSamples=len(direct),inheritedExactSamples=len(inherited),boards=len(boards),exitCode=0)")
p=B/'extract-orientation-current34-pixels-v3.py';assert not p.exists();p.write_text(s,'utf-8')
s=(B/'record-orientation-current34-pixels-worker-v2.py').read_text('utf-8').replace('current34-{a.mode}-pixel-execution-v2','current34-{a.mode}-pixel-execution-v3')
s=s.replace('Directly inspect every planned encoded sample and normal UI playback.', 'Directly inspect only new changed/differing pixels and boundaries; inherit only cached prior exact-pixel SHA evidence, with no redisplay or old decode.')
p=B/'record-orientation-current34-pixels-worker-v3.py';assert not p.exists();p.write_text(s,'utf-8')
print('Prepared new finalV4 pixel QA: all244 cue boundaries, all8 repairs, cuts; only exact cached unchanged pixels inherited.')
