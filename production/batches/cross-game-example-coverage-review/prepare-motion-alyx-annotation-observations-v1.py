"""Record directly read destination/arrival samples without inventing tracking."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
execution=json.loads((R/'source-clearance-execution-v1.json').read_text('utf-8-sig'))
selected=[3039,3051,3063,3069,3075,3081]
rows=[]
for frame in selected:
    x=next(x for x in execution['transition']['samples'] if x['nativeFrame']==frame)
    assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
    visible=frame<=3063
    rows.append({**x,'sampleSize':[1280,720], 'sourceNativeSize':[1920,1080],
        'directlyRead':True,'destinationFeetVisible':visible,
        'viewpointState':'before-near-door-arrival' if visible else 'after-near-door-arrival',
        'destinationAnnotationRule':'Point to actual yellow feet only while visibly present.' if visible
            else 'Hide destination leader/marker; use doorway and adjacent wall as arrival context.'})
out=R/'alyx-annotation-observation-plan-v1.json'
assert not out.exists()
v=dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),samples=rows,
    sourcePath='shared/assets/responsive-game-feedback/raw/alyx-official.mp4',
    sourceSha256='696eac2cf843d0c0a33d5019726a71c0ceb4a1b0f1cf92d8922d3f07b1d854cd',
    transitionBracketNativeFrames=[3063,3069], exactFirstTransitionFrameKnown=False,
    annotationRules=['Do not interpolate a destination marker across the viewpoint jump.',
        'Do not draw a predicted movement trajectory; the yellow curve is the game\u2019s destination selection UI.',
        'Keep the observed yellow feet/curve visible above fixed bottom narration captions.',
        'Preserve the separate subsequent board-removal task instead of claiming one continuous comfort test.'],
    planningSamplesDirectlyCompared=True, allIntermediateFramesReviewed=False,
    coordinatesPrepared=False, movingAnnotationApproved=False, narrationTimed=False,
    allFinalCuesApproved=False, comfortOutcomeClaim=False, gitImagesAdded=0)
out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Six current destination/arrival samples sealed; transition bracket, not exact transition or moving approval.')
