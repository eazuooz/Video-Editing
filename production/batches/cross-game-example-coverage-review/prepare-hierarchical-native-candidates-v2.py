"""Prepare new Timberborn discovery and distinct subsecond Manor/Storm points only."""
from pathlib import Path
import ast
import json

ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'production/batches/cross-game-example-coverage-review'
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
extract=B/'extract-hierarchical-native-candidates-v2.py'
observer=B/'observe-hierarchical-native-cpu-resource-v2.py'
recorder=B/'record-hierarchical-native-worker-v2.py'
assert all(not p.exists() for p in [extract,observer,recorder])
code=(B/'extract-hierarchical-native-candidates-v1.py').read_text('utf-8-sig')
code=code.replace('native-candidate-pixels-v1','native-candidate-pixels-v2')
code=code.replace('native-cpu-resource-verification-v1','native-cpu-resource-verification-v2')
code=code.replace('native-candidate-extraction-execution-v1','native-candidate-extraction-execution-v2')
code=code.replace('native-candidate-extraction-plan-v1','native-candidate-extraction-plan-v2')
old="source_state=read(V/'source-acquisition-execution-v1.json')\nsources={s['videoId']:s for s in source_state['results']}"
new="""source_state=read(V/'source-acquisition-execution-v1.json')
additional_closed=read(V/'source-acquisition-execution-v2.session.json')
assert additional_closed['actualOuterExitCode']==0 and additional_closed['exactWorkerDead'] and additional_closed['exactChildrenDead']
additional_state=read(V/'source-acquisition-execution-v2.json')
assert len(additional_state['results'])==1
sources={s['videoId']:s for s in source_state['results']+additional_state['results']}
previous_review=read(V/'native-candidate-direct-review-v2.json')
assert previous_review['viewedBoardCount']==64 and previous_review['reviewedBoundNativeSampleCount']==371
previous_pts={(s['sourceId'],s['actualDecodedSourcePtsSeconds'])
    for g in previous_review['groups'] for s in read(ROOT/g['indexPath'])['samples']}"""
assert old in code;code=code.replace(old,new)
begin=code.index('source_groups=[');end=code.index('\nfor g in source_groups:',begin)
code=code[:begin]+"""source_groups=[
    dict(id='manor-placement-fine',sourceId='gVkhhrLARU8',offset=18,end=34,times=[18.25+i*.5 for i in range(32)]),
    dict(id='manor-market-fine',sourceId='gVkhhrLARU8',offset=80,end=91,times=[80.25+i*.5 for i in range(22)]),
    dict(id='storm-housing-fine',sourceId='qaK2FWQB7DE',offset=2930,end=2971,times=[2930.25+i*.5 for i in range(82)]),
    dict(id='storm-mine-fine',sourceId='qaK2FWQB7DE',offset=2990,end=3019,times=[2990.25+i*.5 for i in range(58)]),
    dict(id='storm-fishing-fine',sourceId='qaK2FWQB7DE',offset=3080,end=3117,times=[3080.25+i*.5 for i in range(74)]),
    dict(id='timber-early-settlement',sourceId='6TNjosDftog',offset=670,end=1084,times=[float(t) for t in range(670,1084,4)]),
    dict(id='timber-automation',sourceId='6TNjosDftog',offset=2306,end=2814,times=[float(t) for t in range(2306,2814,4)])]
assert sum(len(g['times']) for g in source_groups)==499
assert not any((g['sourceId'],t) in previous_pts for g in source_groups for t in g['times'])
verified_sources=set()"""+code[end:]
code=code.replace("role='coarse candidate discovery, not final cut/caption approval'", "role='additional Timberborn discovery and new precise action points; not final narration/caption approval',\n    previous371PointsRepeated=0,inputDurationBoundedBeforeDecode=True")
old="        assert sha(ROOT/source['localMediaPath'])==source['fileSha256']"
new="""        if g['sourceId'] not in verified_sources:
            assert sha(ROOT/source['localMediaPath'])==source['fileSha256']
            verified_sources.add(g['sourceId'])"""
assert old in code;code=code.replace(old,new)
old="'-i',str(ROOT/source['localMediaPath']),'-to',str(g['end']),"
new="'-t',str(g['end']-g['offset']),'-i',str(ROOT/source['localMediaPath']),"
assert old in code;code=code.replace(old,new)
ast.parse(code)
extract.write_text(code,'utf-8')
code=(B/'observe-hierarchical-native-cpu-resource-v1.py').read_text('utf-8-sig')
for old,new in [('native-cpu-resource-verification-v1','native-cpu-resource-verification-v2'),
    ('native-resource-v1.cim','native-resource-v2.cim'),('one bounded native candidate extraction','one additional Timberborn discovery plus distinct subsecond Manor/Storm native points')]:
    code=code.replace(old,new)
ast.parse(code);observer.write_text(code,'utf-8')
code=(B/'record-hierarchical-native-worker-v1.py').read_text('utf-8-sig')
code=code.replace('native-candidate-extraction-execution-v1','native-candidate-extraction-execution-v2')
code=code.replace("state['sampleCount']==371 and state['boardCount']==64", "state['sampleCount']==499 and state['boardCount']==87")
code=code.replace('nativeCandidateActualSession','additionalNativeCandidateActualSession')
code=code.replace('nativeExecution=','additionalNativeExecution=')
code=code.replace('actualNativeOuterSession=','additionalNativeOuterSession=')
code=code.replace('actualNativeOuterExitCode=','additionalNativeOuterExitCode=')
code=code.replace('Read64new boards/371native samples once','Read87new boards/499native samples once; previous64boards/371samples remain exact unchanged inherited proof')
ast.parse(code);recorder.write_text(code,'utf-8')
print(json.dumps(dict(preparedOnly=True,newPoints=499,newBoards=87,previous371PointsRepeated=0,
    inputTimeBounded=True,additionalSourceClosureRequired=True,files=[p.relative_to(ROOT).as_posix() for p in [extract,observer,recorder]])))
