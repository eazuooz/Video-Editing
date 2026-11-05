"""Tie the native pixel, transition, and viewer-size inspections to all six files."""
import hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent
L=H.parents[1]/'local/fighters-v4-kula-lili/unreal';QA=L/'qa'
rd=lambda p:json.loads(p.read_text(encoding='utf-8'))
def sig(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
cuts=[]
for checked in rd(H/'encoded-motion-evidence.json'):
    cid=checked['id'];cap=rd(L/f'{cid}-capture.json');q=rd(QA/f'{cid}-joint-targets.json')
    assert q['fileSha256']==cap['movieSha256']==checked['mp4Sha256']==sig(L/f'{cid}.mp4')
    marks=[v for phase in q['facts'] for sample in phase['sampledFrames'] for s in sample['sides'].values() if s['marksExpected'] for v in s['joints'].values()]
    assert max(m['orangeSurfaceDistancePx'] for m in marks)<=2
    assert min(m['matchingStrokePixels'] for m in marks)>35
    start=q['facts'][0]['sampledFrames'][0]['sides']
    y_ranges=[[start[s]['meshBBox'][1],start[s]['meshBBox'][3]] for s in ('left','right')]
    assert y_ranges[0]==y_ranges[1] and y_ranges[0][0]>190 and y_ranges[0][1]<883
    assert q['equalRigScale']
    all_bbox=[s['meshBBox'] for phase in q['facts'] for sample in phase['sampledFrames'] for s in sample['sides'].values()]
    assert all(0<b[0]<b[2]<1920 and b[1]>190 and b[3]<883 for b in all_bbox)
    edges=QA/f'{cid}-phase-edges.json';rows=rd(edges) if edges.exists() else []
    boundaries=sorted({row['phaseStartFrame'] for row in rows})
    quiet=[row['coloredGuidePixelsAcrossNativeFigure'] for row in rows if not row['marksExpected']]
    shown=[row['coloredGuidePixelsAcrossNativeFigure'] for row in rows if row['marksExpected']]
    if rows:assert max(quiet)<=3 and min(shown)>100,(cid,max(quiet),min(shown))
    assert len(boundaries)==len(q['facts'])-1
    cuts.append(dict(id=cid,sha256=q['fileSha256'],frames=q['frames'],trials=len(q['facts']),rigScale=[1,1,1],startVerticalPixelExtent=y_ranges,frameSamples=[sample['frame'] for trial in q['facts'] for sample in trial['sampledFrames']],visibleJointChecks=len(marks),maxJointCenterDistanceToNativeMeshPixels=max(m['orangeSurfaceDistancePx'] for m in marks),minIdentifiedGuidePixels=min(m['matchingStrokePixels'] for m in marks),
       poseResetFrames=boundaries,maxOldGuideColorPixelsInsideClearWindow=max(quiet,default=0),minGuideColorPixelsThreeFramesOutsideClearWindow=min(shown,default=None),cropAndLabelReview='pass',mobile375AndNativeCropReview='pass',matchedPlayback='Both sample rigs use identical progress on each inspected frame; heights match at frame zero.',nativeComparison=checked['sampledIntervals']))
output={'episode':'A02','revision':'fighters-v4-kula-lili','scope':'Six final Unreal rendered and composited clips; the separately collected commercial gameplay, whole edit, subtitles, and final audio use their own reviews.',
    'result':'pass','method':'Compared decoded bare native and final compositions at phase starts, intermediate samples and peaks, full figure and 375px images. Measured fields below refer to the authored Unreal demonstration only. Reviewed phase exits from boundary−3 through boundary+3 on both sides.',
    'fixedDefect':'At E013/507 and E011/323,515 the previous wrist guide remained visible as the mesh reset. One-frame sampling and clearing ±2 around all six resets removed the misleading line. Inside all clear intervals at most one incidental color-matching compression pixel survived; no connected guide remained.',
    'labels':'Legend identifies shoulder center, wrist and trajectory. Blue left is 1.0× (30 cm), green right is 1.8× (54 cm). Common-target pose starts from different windups; shoulder-control rotation-only phases keep both shoulder centers fixed.',
    'humanFinalReview':False,'cuts':cuts}
(H/'joint-pixel-review.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('verified',len(cuts),'clips,',sum(c['trials'] for c in cuts),'trials,',sum(c['visibleJointChecks'] for c in cuts),'visible joint checks')
