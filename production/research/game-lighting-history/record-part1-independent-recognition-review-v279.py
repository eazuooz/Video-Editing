"""Direct full-model readings resolve information/quarter; preserve one unresolved onset."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, psutil
R=Path(__file__).resolve().parents[3]
P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
findings={
 'artifact-context-outer-comparison-before':(False,'All three complete paragraphs and every timestamp directly read through28.98s. Full32-decoder model still reads 수의 at5.88–6.10. Previous Turbo read5.90–6.22. No missing later sentence or invented ending, but initial 자 remains unresolved. Regenerate only this new guide paragraph as a preserved-baseline technical repair; do not alter original111 narration.'),
 'artifact-context-runtime-texture-consumer':(True,'All three complete paragraphs and every timestamp directly read through61.82s. Independent full model reads 정보 at17.72–17.98, corroborating current whole04 and unmixed contexts. This resolves the Turbo 전구 conflict for sentence coverage. 변위/변이, 예산/계산, 앞의/앞에 remain explicit pronunciation variants; 텍셀 is now recognized correctly.0.34s/0.04s word alignment overlaps are retained without an audio-repeat claim.'),
 'artifact-context-original-18t-3':(True,'All three complete paragraphs and every timestamp directly read through42.14s. Independent full model reads4분의1 at18.64–19.26 and21.88–22.50, resolving the Turbo numerical inversion from actual recognition rather than surrounding equations alone.8x4=32 and4x2=8 and the fixed-cost caveat are complete. 기하 is recognized correctly. No missing or repeated sentence.')}
ep=P/'part1-independent-recognition-execution-v275.json';e=read(ep)
assert e['status']=='complete' and e['exitCode']==0 and e['model']['decoderLayers']==32
w=e['worker']
if psutil.pid_exists(w['pid']):assert abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01
assert set(findings)=={r['label'] for r in e['results']}
rows=[]
for r in e['results']:
 assert sha(R/r['path'])==r['sha256']
 ok,note=findings[r['label']]
 rows.append({**r,'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,'contentApproved':ok,'observedResolution':note,'humanPronunciation':'pending'})
j={'reviewedAt':datetime.now(timezone.utc).isoformat(),'execution':{'path':ep.relative_to(R).as_posix(),'sha256':sha(ep)},
 'currentMixSha256':e['currentMixSha256'],'planSha256':e['planSha256'],'records':rows,
 'allFullTextsAndTimestampsDirectlyCompared':True,'approvedContexts':2,'allObservedRecognitionConcernsResolved':False,
 'unresolvedLabels':['artifact-context-outer-comparison-before'],'finalMixedAsrApproved':False,
 'next':'Generate only the existing outer-comparison-before new guide with identical KO/EN meaning; preserve every original PCM and prior guide takes. Measure/review new take before replacing any timing or mix.',
 'humanWholeListening':'pending','humanPronunciation':'pending','uploaded':False}
dest=P/'part1-independent-recognition-direct-review-v279.json';assert not dest.exists()
dest.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'fullModelRead':3,'resolved':2,'unresolved':1,'finalMixedApproval':False}))
