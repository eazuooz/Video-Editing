from pathlib import Path
import hashlib
P=Path(__file__).resolve().parent
original=(P/'seal-source-bank-v2.py').read_text('utf-8')
imports=original.split("sp=P/'plant-endpoints-execution-v6.json'")[0]
resume='''sp=P/'plant-endpoints-execution-v6.json';d=read(sp)
assert d['exitCode']==0 and d['actualOuterExitCode']==0 and d['actualOuterExitToolObservation']=='c81b32'
out=P/'plant-contour-endpoints-direct-review-v6.json';r=read(out);c=d['cuts'][0]
assert r['all6EndpointSamplesAndOneBoardDirectlyRead'] and r['allHashesAndNativePtsVerified']
assert r['executionSha256']==sha(sp) and r['actualExitTool']=='c81b32'
for s in c['samples']:assert s['pts']==s['nativeFrame']*256 and sha(ROOT/s['path'])==s['sha256'] and sha(ROOT/s['captionTestPath'])==s['captionTestSha256']
for b in c['boards']:assert sha(ROOT/b['path'])==b['sha256']
assert all(sha(ROOT/p)==h for p,h in d['protectedInputs'].items()) and all(sha(ROOT/p)==h for p,h in d['protectedOriginal8Pcm'].items())
'''
body=original[original.index("v4=read(P/'extra-native-action-execution-v4.json')"):].replace("P/'content-studio-change-review-v6.json'","P/'content-studio-change-review-v7.json'")
body=body.replace("cp.update(recordedAt=now(),stage=", "cp.update(recordedAt=now(),sourceBankSealRecoveredAfterDuplicateRefresh=True,sourceBankFirstSealExitCode=1,sourceBankFirstSealTool='7ba4b7',stage=")
dest=P/'seal-source-bank-resume-v3.py';assert not dest.exists();dest.write_text(imports+resume+body,'utf-8')
print(hashlib.sha256(dest.read_bytes()).hexdigest())
