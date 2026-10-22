"""Record inspected scene02 and plan hand/rock endpoint markers only."""
import datetime,math
from polish_common import *
e=Episode('M09');e.authorized();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=e.H/'uncle-cut-review-v3.json';d=read(p)
assert d['frames']==2700 and len(d['samples'])==45 and sha(R/d['preview'])==d['previewSha256']
save(e.H/'uncle-source-cut-review.json',{'status':'passed-source-cut-inspection','reviewedAt':now,
 'candidateSha256':sha(p),'previewSha256':d['previewSha256'],'rawClipSha256':d['rawClipSha256'],
 'directStates':45,'directSheets':d['sheets'],'sourceSpeed':1,
 'observed':'Hand-to-rock connection at6-15s, retarget/release/landing and another link at32-37s. Revised21-29s shows connection becoming visibly longer/steeper with the camera before release; no metres inferred.',
 'correctedFrom':'uncle-cut-v2-rejection.json: beam-absent length explanation replaced by source374-382s without repeating frames.',
 'playbackObserved':'Native browser start and end states observed, not continuous temporal coverage or listening approval.',
 'guideTargets':'15 quarter-second source states directly inspected; hide unobserved/off-screen endpoint periods.',
 'fullMasterApproval':False,'humanReview':'pending'})
target=e.H/'new-uncle-guide-targets.json';r=read(target);r.update(status='direct-target-stills-inspected',reviewedAt=now);save(target,r)
# Beam endpoints are editorial points on the visible connection, not a measured
# physics origin, world coordinate, or a detector output.
anchors=[(12,438,89),(12.25,403,81),(12.5,371,93),(12.75,355,105),(13,378,130),(13.25,392,135),
 (25.5,385,60),(25.75,372,26),(26,363,60),(26.25,352,53)]
circle=lambda x,y,r:[[x+r*math.cos(i*math.pi/16),y+r*math.sin(i*math.pi/16)] for i in range(32)]
track=e.H/'cue-track-02-hand-rock.json'
save(track,{'sourceFile':rel(e.O/'clips/02.mp4'),'sourceSha256':d['rawClipSha256'],'coordinatePixels':[800,450],
 'keyframes':[{'t':t,'object':'visible-connection-ends' if t<20 else 'visible-perspective-connection-ends','red':circle(545,299,20),'blue':circle(x,y,17)} for t,x,y in anchors],
 'maxInterpolationGapSeconds':.26,'manualHideIntervals':[],'closed':True,
 'coordinateFrame':'screen pixels','meaning':'Red hand-side endpoint region; blue rock-side endpoint region. The actual luminous beam remains visible between them.',
 'tracking':'Manual quarter-second anchors, limited to inspected visible endpoints. Hidden before and after each window; no cross-cut interpolation.',
 'sourceEvidence':rel(target),'sourceEvidenceSha256':sha(target),'measurement':False})
save(e.H/'cue-guide-additions.json',{'episode':'M09','scenes':{'02':{'useReviewedLocalClip':True,'landmarkSources':[rel(track)],
 'revealAtLine':0,'redAtLine':0,'blueAtLine':0,'tealAtLine':0,'hideMathNote':True,
 'redLabel':'빨강: 손 쪽 끝','blueLabel':'파랑: 바위 쪽 끝 · 화면 표식'}}})
print('M09 inspected revised cut and endpoint guide plan recorded')
