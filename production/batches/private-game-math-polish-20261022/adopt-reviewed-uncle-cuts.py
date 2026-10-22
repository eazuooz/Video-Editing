"""Adopt byte-verified reviewed previews without re-encoding their source cuts.

Internal excerpt positions may change under the user's same-game/action FHD
decision. The original scene order, frame count, narration and audio do not.
"""
import datetime,shutil,sys
from polish_common import *
permission=read(B/'uncle-fhd-scene-candidates.json')['permission']
for ident in sys.argv[1:]:
 assert ident in ['M11','M12']
 e=Episode(ident);e.authorized();p=e.H/'uncle-cut-review-v2.json';d=read(p)
 review=read(e.H/'uncle-source-cut-review.json')
 assert review['status']=='passed-source-cut-inspection' and review['candidateSha256']==sha(p)
 assert review['previewSha256']==sha(R/d['preview'])
 assert sha(R/d['rawClip'])==d['rawClipSha256'] and sha(R/d['source']['path'])==d['source']['sha256']
 assert sha(R/permission['permissionMetadata'])==permission['permissionMetadataSha256']
 sid=d['scene'];slot=next(s for s in e.T['scenes'] if s['id']==sid)
 assert d['frames']==slot['frames']==sum(s['frames'] for s in d['segments'])
 for i,s in enumerate(d['segments']):
  for z in d['segments'][i+1:]:assert s['in']+s['frames']/60<=z['in'] or z['in']+z['frames']/60<=s['in']
 e.verify(R/d['rawClip'],slot['frames'])
 cut={'status':'approved-source-cut','sourceId':'5u3sUKuncSU','game':permission['game'],
  'sourceFile':d['source']['path'],'sourceSha256':d['source']['sha256'],'sourceUrl':permission['url'],
  'sourceSpeed':1,'frames':slot['frames'],'segments':d['segments'],'sourceAudioUsed':False,
  'permissionMetadata':permission['permissionMetadata'],'permissionMetadataSha256':permission['permissionMetadataSha256'],
  'permissionEvidence':permission['permissionEvidence'],'requiredDescriptionCredit':permission['requiredCredit'],
  'reviewedInternalExcerptChanges':True,'sourceReview':rel(e.H/'uncle-source-cut-review.json'),
  'sourceReviewSha256':sha(e.H/'uncle-source-cut-review.json'),'originalSceneOrderAndDurationPreserved':True,
  'difference':'Different independently recorded grapple traversal; original low-resolution tracking is not reused. Internal source cuts changed to remove resets/tutorial interruptions and match existing speech.'}
 mp=e.H/'fhd-replacement-cuts.json';mapping=read(mp) if mp.exists() else {'episode':ident,'scenes':{}}
 mapping.update(status='approved-source-cuts',originalTimelineSha256=sha(e.P/'production/timeline.json'),originalNarrationAudioAndTimingPreserved=True)
 mapping['scenes'][sid]=cut;save(mp,mapping)
 save(e.H/'fhd-cut-review.json',{'status':'passed-source-cut-inspection','cutMapSha256':sha(mp),
  'sceneReviews':{k:v['sourceReview'] for k,v in mapping['scenes'].items()},'fullMasterApproval':False,'humanReview':'pending'})
 dst=e.O/f'clips/{sid}.mp4';dst.parent.mkdir(exist_ok=True)
 assert not dst.exists() or sha(dst)==d['rawClipSha256'],'Do not overwrite a different existing production cut'
 if not dst.exists():shutil.copy2(R/d['rawClip'],dst)
 assert sha(dst)==d['rawClipSha256'];e.verify(dst,slot['frames'])
 rp=e.H/'gameplay-restoration.json';record=read(rp) if rp.exists() else {'scenes':{}}
 record['scenes'][sid]={'path':rel(dst),'sha256':sha(dst),'frames':slot['frames'],'speed':1,
  'sources':[{'sourceSha256':d['source']['sha256'],'source':d['source']['path'],'sourceIn':s['in'],'frames':s['frames'],'vf':'fps=60; native1920x1080'} for s in d['segments']],
  'originalCutOrderAndDuration':False,'originalSceneOrderAndDuration':True,'internalExcerptChangesReviewed':True,
  'sourceKind':'reviewed-same-game-FHD-replacement','sourceReview':cut['sourceReview'],
  'currentMovingPixelReview':'source playback only; annotated composition pending','annotationPolish':'pending',
  'sourceAudio':'unchanged original narration-only upload retained; replacement source audio unused'}
 record['replacementCutMap']={'path':rel(mp),'sha256':sha(mp)};save(rp,record)
 actual={s['id'] for s in e.T['scenes'] if s['classification']=='actual'};missing=sorted(actual-record['scenes'].keys())
 status=read(B/'gameplay-restoration-status.json');status[ident]={'status':'partial-gameplay-restored' if missing else 'gameplay-restored',
  'restoredScenes':sorted(record['scenes']),'missingScenes':missing,'annotationPolish':'pending','fullMasterReady':False};save(B/'gameplay-restoration-status.json',status)
 print(ident,sid,'reviewed FHD source adopted; annotated QA pending',flush=True)
