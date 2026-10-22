"""Adopt directly inspected same-source camera excerpts without changing speech."""
import datetime, shutil
from polish_common import *
e=Episode('M17');e.authorized(); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=e.H/'camera-cue-review-v2.json'; r=read(p); src=R/r['sourceFile']; raw=R/r['rawClip']
assert sha(src)==r['sourceSha256'] and sha(raw)==r['rawClipSha256']
slot=next(s for s in e.T['scenes'] if s['id']=='14');assert r['frames']==slot['frames']==6156
e.verify(raw,6156)
assert len(r['samples'])==103
for sample in r['samples']:assert sha(R/sample['path'])==sample['sha256']
evidence=e.H/'camera-cue-repair-review.json'
save(evidence,dict(status='passed-source-cut-inspection',reviewedAt=now,candidate=rel(p),candidateSha256=sha(p),
    directStillSamples=103,directSheets=12,sourceGuideSamples=33,
    playback='Browser playback launched at12s and79s; start and later/end frames directly observed. This is selected playback observation, not continuous frame-by-frame or full audio listening.',
    observations=['Low/front view and camera orbit at12–14.5s reveal changing occlusion by the front roof; the top of the rear tower remains visible. Do not label the entire tower hidden.',
      'Higher view at26–27.5s reveals the courtyard. Existing narration distinguishes observed building/orbit occlusion from unobserved near clipping.',
      'Native-speed wide and closer views now overlap81.52–85.28s same-building narration;83.25–85.25s shows a recognizable gabled roof before and after zoom.',
      'Internal source jump at80s lies before the zoom comparison; clear every guide at the cut. No loop, retime or repeated source range.'],
    limitations=['Gameplay does not establish internal camera matrices, clipping values or world-space bounds.','Full episode, moving composited guides and human review remain pending.'],
    fullMasterApproval=False,humanReview=False))
meta=src.with_suffix('.mp4.info.json');m=read(meta)
assert m['id']=='FRfnXAIbA-M' and 'FREE TO USE GAMEPLAY' in m['title']
cut=dict(status='approved-source-cut',sourceId=m['id'],game='Townscaper',sourceFile=rel(src),sourceSha256=sha(src),
 sourceUrl='https://www.youtube.com/watch?v=FRfnXAIbA-M',sourceSpeed=1,frames=6156,
 segments=[dict(x,sourceFile=rel(src)) for x in r['segments']],sourceAudioUsed=False,
 permissionMetadata=rel(meta),permissionMetadataSha256=sha(meta),
 permissionEvidence='Existing source title explicitly labels FREE TO USE GAMEPLAY; description says shout-outs are optional. Original rights record retained.',
 requiredDescriptionCredit='Townscaper gameplay: Handheld belt gameplay archive — https://www.youtube.com/watch?v=FRfnXAIbA-M',
 reviewedInternalExcerptChanges=True,sourceReview=rel(evidence),sourceReviewSha256=sha(evidence),originalSceneOrderAndDurationPreserved=True,
 difference='Same original FHD recording; excerpt starts at647s and735s to align orbit and zoom with existing speech. Original scene and full lesson frames unchanged.')
mapping=e.H/'fhd-replacement-cuts.json'
save(mapping,dict(episode=e.id,scenes={'14':cut},status='approved-source-cuts',originalTimelineSha256=sha(e.P/'production/timeline.json'),originalNarrationAudioAndTimingPreserved=True))
save(e.H/'fhd-cut-review.json',dict(status='passed-source-cut-inspection',cutMapSha256=sha(mapping),review=rel(evidence),reviewSha256=sha(evidence),fullMasterApproval=False))
rest=e.H/'gameplay-restoration.json'; old=read(rest); previous=old['scenes']['14']; dst=e.O/'clips/14.mp4'
if sha(dst)!=r['rawClipSha256']:
 assert sha(dst)==previous['sha256']
 backup=e.O/'camera-cue-review-v2/original-14.mp4'
 if not backup.exists():shutil.copy2(dst,backup)
 assert sha(backup)==previous['sha256']
 shutil.copy2(raw,dst)
 previous['preservedAt']=rel(backup)
 save(e.H/'camera-cue-original-14.json',previous)
assert sha(dst)==r['rawClipSha256']
old['scenes']['14']=dict(path=rel(dst),sha256=sha(dst),sources=[dict(source=rel(src),sourceSha256=sha(src),sourceIn=s['in'],frames=s['frames']) for s in r['segments']],
 frames=6156,speed=1,originalCutOrderAndDuration=False,originalSceneOrderAndDuration=True,sourceKind='reviewed-same-source-FHD-cue-repair',
 currentMovingPixelReview='selected raw preview inspected; final composite pending',annotationPolish='pending-current-preflight',sourceAudio='unchanged recovered original narration retained')
old['replacementCutMap']=dict(path=rel(mapping),sha256=sha(mapping));save(rest,old)
plan=read(e.H/'observed-guides.json');plan['guides']=[g for g in plan['guides'] if g['scene']!='14']
def guide(label,keys,pos):
 return dict(scene='14',label=label,role='focus',shape='ring',labelPosition=pos,
  keyframes=[[k[0],*[v*4 for v in k[1:]]] for k in keys],meaning=label,
  coordinateFrame='observed-screen-projection',tracking='Hand-observed quarter-second480x270 source states; open attention region, not segmentation or world geometry.',
  occlusion='Hide outside inspected span and at80s internal cut; no hidden target extrapolation.')
plan['guides'] += [guide('앞 지붕',[
 [12,144,150,82,36],[12.25,170,118,80,32],[12.5,170,118,80,32],[12.75,150,114,78,36],[13,153,116,78,36],
 [13.25,181,88,66,45],[13.5,190,79,53,55],[13.75,212,65,46,54],[14,239,64,44,53],[14.25,241,64,44,53],[14.5,241,64,44,53]], [1560,650]),
 guide('같은 지붕',[[83.25,205,82,22,14],[83.5,200,83,26,16],[83.75,200,83,26,16],[84,189,62,31,18],
 [84.25,187,62,31,18],[84.5,183,71,32,18],[84.75,184,71,33,18],[85,184,71,33,18],[85.25,184,71,33,18]],[300,160])]
plan.update(selectedScenes=['05','08','14'],sourceCueRepair=rel(evidence),sourceCueRepairSha256=sha(evidence),
 sourceGuideEvidence=rel(e.H/'camera-cue-guide-source.json'),sourceGuideEvidenceSha256=sha(e.H/'camera-cue-guide-source.json'),
 status='draft-camera-cue-repair-await-current-pixel-preflight',remaining=['Portal2 native FHD inputs remain unresolved.'],internalCutBoundaries={'14':[80]})
save(e.H/'observed-guides.json',plan)
print('M17-14 reviewed same-source cue repair adopted; exact6156 frames, composite QA pending')
