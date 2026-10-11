"""Repair two directly observed annotation defects, preserving all prior evidence."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=m.ROOT/'projects/game-lighting-history-04/production'
direct=m.read(P/'part3-final-board-direct-progress-v158.json')
assert direct['directlyReadBoards']==direct['plannedBoards']==362
assert len(direct['records'])==362 and all(r['directlyRead'] for r in direct['records'])
previous=m.read(P/'part3-annotated-visual-build-v148.json')
assert previous['wholeDecodeExitCode']==0 and previous['frames']==92038
assert m.sha(m.ROOT/previous['path'])==previous['sha256']
source=Path(__file__).with_name('build-part3-annotated-visual-v148.py').read_text('utf-8')
source=source.replace('v148','v159').replace('V148','V159')
source=source.replace("'windows':[[4.2333,10.05],[13,16.9333]]", "'windows':[[4.2333,7.25],[13,16.9333]]")
source=source.replace("'게임의 Talk 안내는 접근 후 나타납니다',1050,150", "'게임의 Talk 안내는 접근 후 나타납니다',50,150")
source=source.replace("label(10.05,13,'카메라 이동 후 같은 면을 다시 잡습니다'", "label(7.25,13,'카메라 이동 후 같은 면을 다시 잡습니다'")
source=source.replace('prepared=[]', "tracks={k:v for k,v in tracks.items() if k in ['hogwarts-courtyard-ui','grade-shared-reference']}\nprepared=[]")
source=source.replace("request={'preparedAt'", "request={'priorFinalBoardDirectReview':{'path':m.rel(P/'part3-final-board-direct-progress-v158.json'),'sha256':m.sha(P/'part3-final-board-direct-progress-v158.json'),'directlyReadBoards':362},'specificRepairs':['Move courtyard external note from 1050,150 to 50,150 to uncover Nellie Oggspire name','Hide lowest-face marker during fast camera motion at local 7.25–13 seconds and show explicit reacquisition note'],'previousNativeResourceCropsPreserved':True,'preparedAt'")
source=source.replace("byid={r['id']:r for r in base['cuts']}", "byid={r['id']:r for r in previous['cuts']};basebyid={r['id']:r for r in base['cuts']}")
source=source.replace("if c['id'] in byass:\n   ass=", "if c['id'] in byass:\n   native=basebyid[c['id']];src=ROOT/native['path'];assert m.sha(src)==native['sha256']\n   ass=")
source=source.replace("elif c['id'].startswith('resource-') and i+1 in [75,76,83,84]:", "elif False: # Four completed editor crops are preserved byte-for-byte.")
source=source.replace("'repairedCutCount':7", "'repairedCutCount':2,'previousVisualProofSha256':m.sha(P/'part3-annotated-visual-build-v148.json'),'preservedCutCount':91")
source=source.replace("'sevenNativeRepairs':7", "'twoObservedAnnotationRepairs':2")
source=source.replace("'part3-native-annotation-repair'", "'part3-two-observed-annotation-repairs'")
source=source.replace("Direct moving annotation review and gated final pair", "Direct two repaired moving shots then gated final pair; preserve remaining 91 inputs")
assert "'windows':[[4.2333,7.25],[13,16.9333]]" in source
assert "'게임의 Talk 안내는 접근 후 나타납니다',50,150" in source
exec(compile(source,str(Path(__file__)), 'exec'))
