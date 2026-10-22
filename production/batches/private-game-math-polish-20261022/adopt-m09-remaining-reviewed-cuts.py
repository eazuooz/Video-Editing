"""Adopt four directly inspected source cuts; full moving/master QA remains separate."""
import datetime, math, shutil
from polish_common import *
e=Episode('M09');e.authorized();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
permission=read(B/'uncle-fhd-scene-candidates.json')['permission']
assert sha(R/permission['permissionMetadata'])==permission['permissionMetadataSha256']
observed={
 '05':'52 one-second states: visible hand-to-rock links, retargeting, release and landing. Direction/length concepts are illustrative; no game-world distance inferred. At31s the connection and later free movement remain distinct.',
 '08':'54 one-second states: upward and diagonal links at1–5s and19–22s, release/landing, another link at40s and48–52s. Screen steepness is not claimed as a measured world axis. No source resets or tutorial overlay.',
 'LG02':'39 one-second states: opening links now appear at3.5–4.5s during the red-line instruction, retarget at6.5–8.5s, further links and free movement before reaching a platform. The final distinct excerpt shows release and a bright landing instead of a poorly visible cave target. General movement wording spans flight and its landing result.',
 'LG03':'38 one-second states: opening connection at0.5–2.5s, release/landing, different later connection20.5–23.5s, free movement/landing and another link32–36s. First excerpt ends before the rejected dark/reset period;16–19.9s is a different unmeasured perspective traversal, not a continuous geographic path.'}
anchors={
 '05':[(5.5,545,299,330,211),(5.75,545,299,321,201),(6,545,299,295,217),(6.25,545,299,292,230),(6.5,545,299,300,235),(6.75,545,299,304,234),(7,545,299,326,236)],
 '08':[(2,545,299,410,64),(2.25,545,299,414,78),(2.5,545,299,415,91),(2.75,545,299,420,99),(3,545,299,422,110),(3.25,545,299,410,63),(3.5,545,299,407,53),(3.75,545,299,414,54),(4,545,299,409,60)],
 'LG02':[(3.5,549,307,400,140),(3.75,550,300,400,122),(4,549,299,399,120),(4.25,561,341,407,117),(4.5,529,269,407,85),(7,545,299,400,178),(7.25,545,299,400,157),(7.5,545,299,400,126),(7.75,545,299,400,101),(8,545,299,400,80)],
 'LG03':[(1,545,299,400,200),(1.25,545,299,400,175),(1.5,545,299,429,146),(1.75,545,299,438,118),(2,545,299,441,90),(2.25,545,299,433,112),(2.5,545,299,418,174)]}
circle=lambda x,y,r:[[x+r*math.cos(i*math.pi/16),y+r*math.sin(i*math.pi/16)] for i in range(32)]
mp=e.H/'fhd-replacement-cuts.json';mapping=read(mp)
rp=e.H/'gameplay-restoration.json';record=read(rp)
ap=e.H/'cue-guide-additions.json';additions=read(ap)
for sid in ['05','LG02','LG03','08']:
 e.authorized();p=e.H/f'uncle-remaining-candidate-{sid}.json';d=read(p)
 assert len(d['samples'])=={'05':52,'08':54,'LG02':39,'LG03':38}[sid]
 assert sha(R/d['rawClip'])==d['rawClipSha256'] and sha(R/d['preview'])==d['previewSha256']
 assert sha(R/d['source']['path'])==d['source']['sha256']
 slot=next(s for s in e.T['scenes'] if s['id']==sid)
 assert d['frames']==slot['frames']==sum(s['frames'] for s in d['segments'])
 review=e.H/f'uncle-remaining-source-review-{sid}.json'
 save(review,{'status':'passed-source-cut-inspection','reviewedAt':now,'candidateSha256':sha(p),
  'previewSha256':d['previewSha256'],'rawClipSha256':d['rawClipSha256'],'directStates':len(d['samples']),
  'directSheets':d['sheets'],'observed':observed[sid],
  'inspectionMethod':'Direct inspection of actual captioned one-second sampled pixels and the dense guide-target states; not continuous playback/listening approval.',
  'movingCompositionReview':'pending','fullMasterApproval':False,'humanReview':'pending'})
 target=e.H/f'uncle-remaining-targets-{sid}.json';targets=read(target)
 assert targets['sourceSha256']==d['rawClipSha256']
 targets.update(status='direct-target-stills-inspected',reviewedAt=now,selectedAnchorCount=len(anchors[sid]));save(target,targets)
 cut={'status':'approved-source-cut','sourceId':'5u3sUKuncSU','game':permission['game'],
  'sourceFile':d['source']['path'],'sourceSha256':d['source']['sha256'],'sourceUrl':permission['url'],
  'sourceSpeed':1,'frames':slot['frames'],'segments':d['segments'],'sourceAudioUsed':False,
  'permissionMetadata':permission['permissionMetadata'],'permissionMetadataSha256':permission['permissionMetadataSha256'],
  'permissionEvidence':permission['permissionEvidence'],'requiredDescriptionCredit':permission['requiredCredit'],
  'reviewedInternalExcerptChanges':True,'sourceReview':rel(review),'sourceReviewSha256':sha(review),
  'originalSceneOrderAndDurationPreserved':True,
  'difference':'Independent FHD grapple traversal; changed internal excerpts inspected against unchanged speech. Original low-resolution tracking is replaced with observed screen-pixel guides.'}
 mapping['scenes'][sid]=cut
 dst=e.O/f'clips/{sid}.mp4';assert not dst.exists() or sha(dst)==d['rawClipSha256']
 if not dst.exists():shutil.copy2(R/d['rawClip'],dst)
 e.verify(dst,slot['frames']);assert sha(dst)==d['rawClipSha256']
 record['scenes'][sid]={'path':rel(dst),'sha256':sha(dst),'frames':slot['frames'],'speed':1,
  'sources':[{'sourceSha256':d['source']['sha256'],'source':d['source']['path'],'sourceIn':s['in'],'frames':s['frames'],'vf':'fps=60; native1920x1080'} for s in d['segments']],
  'originalCutOrderAndDuration':False,'originalSceneOrderAndDuration':True,'internalExcerptChangesReviewed':True,
  'sourceKind':'reviewed-same-game-FHD-replacement','sourceReview':rel(review),'currentMovingPixelReview':'pending',
  'annotationPolish':'pending','sourceAudio':'Unchanged original narration-only upload; replacement source audio unused'}
 keys=[]
 for t,hx,hy,x,y in anchors[sid]:
  k={'t':t,'object':f'{sid}-connection-'+('second' if sid=='LG02' and t>=7 else 'first')}
  if sid=='05':k.update(red=circle(hx,hy,20),blue=circle(x,y,17))
  else:k.update(left=[hx,hy],right=[x,y])
  keys.append(k)
 track=e.H/f'cue-track-{sid}-connection.json'
 save(track,{'sourceFile':rel(dst),'sourceSha256':sha(dst),'coordinatePixels':[800,450],'keyframes':keys,
  'maxInterpolationGapSeconds':.26,'manualHideIntervals':[],'closed':True,'coordinateFrame':'screen pixels',
  'meaning':'Editorial visible hand-to-rock connection endpoints; straight red segment is a geometric guide, not the actual lightning curve, body path, engine ray or measured world vector.',
  'tracking':'Manually inspected quarter-second anchors. Hidden at all other times, absent beams, off-screen endpoints, occlusions and source cuts.',
  'sourceEvidence':rel(target),'sourceEvidenceSha256':sha(target),'measurement':False})
 additions['scenes'][sid]={'useReviewedLocalClip':True,'landmarkSources':[rel(track)],
  'revealAtLine':0,'redAtLine':0,'blueAtLine':0,'tealAtLine':0,'hideMathNote':True,
  'redLabel':'빨강: 손 쪽 끝' if sid=='05' else '손 → 바위 · 화면 연결선',
  'blueLabel':'파랑: 바위 쪽 끝 · 화면 표식'}
save(mp,mapping);record['replacementCutMap']={'path':rel(mp),'sha256':sha(mp)};save(rp,record);save(ap,additions)
save(e.H/'fhd-cut-review.json',{'status':'passed-source-cut-inspection','cutMapSha256':sha(mp),
 'sceneReviews':{k:v['sourceReview'] for k,v in mapping['scenes'].items()},'fullMasterApproval':False,'humanReview':'pending'})
status=read(B/'gameplay-restoration-status.json')
actual={s['id'] for s in e.T['scenes'] if s['classification']=='actual'}
status['M09']={'status':'partial-gameplay-restored','restoredScenes':sorted(record['scenes']),
 'missingScenes':sorted(actual-record['scenes'].keys()),'annotationPolish':'new-four-cues-pending-current-composition-QA','fullMasterReady':False}
save(B/'gameplay-restoration-status.json',status)
old=read(e.H/'uncle-remaining-candidate-LG03-v1.json')
save(e.H/'uncle-remaining-candidate-LG03-v1-rejection.json',{'status':'rejected','candidate':old,
 'reason':'Dark/fall/reset-like interruption at17.5s did not help the unchanged parametric explanation. End the first excerpt earlier and use separately observed traversal; preserve2294frames and narration.',
 'replacementCandidate':rel(e.H/'uncle-remaining-candidate-LG03.json')})
print('M09 five of six FHD slots restored; four new guide compositions require inspection',flush=True)
