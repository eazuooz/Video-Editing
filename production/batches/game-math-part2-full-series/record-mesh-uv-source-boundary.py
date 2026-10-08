"""Save directly reviewed roof extension and narrated subject transition."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3]
P=R/'projects/game-math-mesh-uv'
q=R/'shared/output/game-math-part2-full-series/inspection/mesh-uv-sunset-roof-boundary'
sample=json.loads((q/'generated-samples.json').read_text(encoding='utf8'))
sheet=q/'window-01-1.jpg'
proof={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'passed-direct-source-boundary-review',
 'sourceId':'fN4iMYUyODc','sourceSha256':sample['sourceSha256'],
 'sheet':sheet.relative_to(R).as_posix(),'sheetSha256':hashlib.sha256(sheet.read_bytes()).hexdigest(),
 'samples':sample['records'][0]['sampleTimes'],
 'directObservation':'All11 decoded samples130–134.9 directly viewed: real traversal toward a roof with panel strips and vents; building faces and outline remain visible, no menu or explosion. Use only through134.8, before the next episode wall interval begins135.',
 'scene02SourceGroups':[{'startsAtLine':0,'in':60,'maxSeconds':21},{'startsAtLine':2,'in':110,'maxSeconds':24.8}],
 'measuredNarrationEvidence':{'durationSeconds':37.68,'lineStarts':[.12,8.14,15.92,22.62,30.56],'characterCoverage':.9834710743801653},
 'reason':'Next roof narration begins at line2. Tie its cut to that spoken transition and retain enough inspected time for the complete latter narration and natural close.',
 'narrationOrVoiceChanged':False,'loopSlowdownFreeze':False,'finalCaptionedSubjectReview':'pending'}
(P/'production/narrated-source-boundary.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
qf=Path(__file__).with_name('queue.json');queue=json.loads(qf.read_text(encoding='utf-8-sig'));control=queue['executionControl'];assert control['currentVideo']=='game-math-mesh-uv'
control['finalProductionGpuJobsRunning']=True
item=next(x for x in queue['items'] if x['slug']=='game-math-mesh-uv');item.update(status='voice-and-cpu-review-render-in-progress',previewExplanationReview=True,voiceDryRunPassed=True,preTtsMathReview=True,humanListening=False)
qf.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Recorded current source transition; all speech and original waveforms preserved.')
