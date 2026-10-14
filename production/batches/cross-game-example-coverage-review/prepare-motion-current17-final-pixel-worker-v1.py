"""Prepare serial absolute-PTS final-pixel inspection; no images rendered."""
from pathlib import Path
import py_compile,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
p=ROOT/'production/batches/unpublished-teaching-clarity-revision/extract-motion-current-final-pixels-v2.py'
s=p.read_text('utf-8')
s=s.replace("production/revision-teaching-clarity-v1'","production/revision-cross-game-four-v1'")
s=s.replace("shared/output/unpublished-teaching-clarity-revision/motion/final-pixels-v2'","shared/output/cross-game-example-coverage/motion/current17-final-pixels-v1'")
s=s.replace('final-pair-execution-v2','current17-final-pair-execution-v2').replace('measured-additive-plan-v1','measured-current17-plan-v2').replace('final-pixel-execution-v2','current17-final-pixel-execution-v1')
a=s.index("    for c in plan['cuts']:");b=s.index('    for n in range(0,',a)
s=s[:a]+'''    assembly=read(R/'current17-assembly-inputs-v2.json')
    for c in assembly['pieces']:
        for n in [c['startFrame']-1,c['startFrame'],c['startFrame']+1,c['endFrame']-1,c['endFrame'],c['endFrame']+1]:add(n,'cut-boundary:'+c['id'])
        if not c.get('retainedByteIdentical'):
            for n in range(c['startFrame'],c['endFrame'],60):add(n,'new-moving-piece-one-second:'+c['id'])
    for scene in plan['scenes']:
        for n in [scene['startFrame']-1,scene['startFrame'],scene['endFrame']-1]:add(n,'scene-boundary:'+scene['id'])
        for voice in scene['voicePlacements']:
            a=voice['destinationStartSample']/400
            b=a+(voice['sourceEndSample']-voice['sourceStartSample'])/400
            for n in [int(a)-1,int(a),int(a)+1,int(b)-1,int(b),int(b)+1]:add(n,'exact-current-PCM-placement:'+scene['id'])
''' +s[b:]
a=s.index("        priorIndex=read(");b=s.index("        assert sha(source)==srcrow['sha256']",a)
s=s[:a]+s[b:]
s=s.replace('all179CuesAndCutBoundariesIncluded=True','all220CuesAnd37PieceCutBoundariesIncluded=True')
s=s.replace("q['execution'].update(currentSlug='motion-sickness-games',stage=cp['stage'],ownedJob=cp['ownedJob'],next=cp['next'])\n        next(x for x in q['items'] if x['slug']=='motion-sickness-games').update(status=cp['stage'],currentExecution=cp['ownedJob'])", "q['currentMotionReview'].update(stage=cp['stage'],status=cp['stage'],activeOwnedWorkers=0 if state['exitCode'] is not None else 1,currentPixelExecution=rel(sp));q.update(next=cp['next'])")
s=s.replace("allFinalPixelsApproved=False,qaApproved=False,next=", "activeOwnedWorkers=0 if state['exitCode'] is not None else 1,allFinalPixelsApproved=False,qaApproved=False,next=")
s=s.replace("captioned-pixels',exitCode=None", "captioned-pixels',exitCode=None")
p=B/'extract-motion-current17-final-pixels-v1.py';assert not p.exists();p.write_text(s,'utf-8');py_compile.compile(str(p),doraise=True)
print(json.dumps(dict(preparedOnly=True,all220CuesPlanned=True,pieceBoundaries=37,absolutePts=True,renderRuns=0,pixelApproval=False)))
