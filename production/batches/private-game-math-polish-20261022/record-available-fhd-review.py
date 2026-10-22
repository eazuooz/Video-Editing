"""Record directly observed partial sources/guides; never approve a full master."""
import datetime
from polish_common import *
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
counts={'M10':(59,8),'M11':(5,1),'M12':(11,2),'M17':(13,2)}
findings={
 'M10':['LG04: removed stale torch track; manually observed approaching-head anchors replace8.0–9.1s; labels moved above the head.',
        'LG06: removed later blue weapon/ambiguous components; retained only731–732.14 source seconds of observed blue body/head region.',
        'Red contours identify selected visible parts, blue boxes their screen extents; no engine bounds or world orientation measured.',
        'Several retained tracks are very brief. All59 sampled visible states inspected, but full-scene annotation timing/coverage still needs final review.'],
 'M11':['Water-surface line/reference point remain on the observed water surface, clear of game UI and fixed captions.',
        'Scene02 original short track is suppressed by the original renderer; an appropriate floor guide is still needed.'],
 'M12':['Scene17 triangle was wrongly labeled a visible terrain boundary. Changed the label to an editorial explanation triangle, not an observed mesh.',
        'Noita platform/edge guides and mathematical note panels remain separated from the fixed captions.',
        'Scene21 has no retained visible guide after the original short-track filter; further source-matched guide work remains.'],
 'M17':['Existing-roof region remains stable during adjacent construction; the same-building roof region follows the observed camera orbit at3–5s.',
        '32 source-target states on4 sheets directly inspected, plus12 restored-source states on2 sheets. No inferred camera matrix or world-space measurement.',
        'Scene14 at13.5–17s shows construction from a fixed viewpoint while the preserved speech describes orbit/occlusion. No false orbit/occlusion guide added; exact action-to-cue repair remains pending.'],
}
all_reviews={}
for ident,(count,sheets) in counts.items():
 e=Episode(ident);e.authorized()
 p=e.H/'observed-guide-preflight.json';d=read(p)
 assert len(d['samples'])==count and d['sheets']==sheets
 assert d['assSha256']==sha(e.O/'composition-polish.ass')
 d.update(status='passed-partial-still-inspection',reviewedAt=now,partial=True,
  directlyInspectedSheets=list(range(1,sheets+1)),findings=findings[ident],fullMasterReady=False,
  finalMovingReview='selected-preview-observations-only; whole-master-review-pending')
 save(p,d)
 moving=e.H/'moving-available-guide-preflight.json';m=read(moving)
 assert m['assSha256']==sha(e.O/'composition-polish.ass')
 for clip in m['clips']:
  assert sha(R/clip['path'])==clip['sha256']
  clip['currentPixels']='selected-native-playback-states-observed'
 m.update(status='selected-native-playback-states-observed',reviewedAt=now,
  method='Native-speed local browser playback with successive screenshot observations, together with current captioned375px contact sheets.',
  scope='Short selected preview windows only; not every frame, full episode, whole-film listening or human approval.',
  findings=findings[ident],fullMasterApproval=False)
 save(moving,m)
 record={'reviewedAt':now,'status':'partial-guides-inspected-full-episode-pending','partial':True,
  'preflight':rel(p),'preflightSha256':sha(p),'sampleCount':count,'sheetCount':sheets,
  'selectedPlayback':rel(moving),'selectedPlaybackSha256':sha(moving),
  'sourceRestoration':rel(e.H/'gameplay-restoration.json'),
  'restoredSceneCount':len(read(e.H/'gameplay-restoration.json')['scenes']),
  'findings':findings[ident],'humanReview':'pending','fullMasterReady':False,
  'newTts':False,'narrationRewrite':False,'timelineChanged':False,'platformMutation':False}
 save(e.H/'available-guides-review.json',record);all_reviews[ident]=rel(e.H/'available-guides-review.json')
 if ident in ['M11','M17']:
  raw=e.H/'restored-source-review-actual.json';r=read(raw)
  r.update(status='passed-selected-source-still-inspection',reviewedAt=now,
   directlyInspectedSheets=list(range(1,r['sheets']+1)),fullMasterReady=False,
   scope='Only listed restored-source samples; this does not establish every narration/action correspondence or final master approval.')
  save(raw,r)
 if ident=='M17':
  tp=e.H/'available-guide-targets.json';target=read(tp)
  # The guide plan binds the source sample manifest. Keep that manifest stable
  # and put the later review in its own receipt.
  for key in ['reviewedAt','directlyInspectedSheets','findings']:target.pop(key,None)
  target['status']='await-direct-source-target-inspection'
  save(tp,target)
  save(e.H/'available-guide-targets-review.json',{'status':'direct-source-target-inspection-with-pending-cue-mismatch',
   'reviewedAt':now,'sourceManifest':rel(tp),'sourceManifestSha256':sha(tp),'sampleCount':32,
   'directlyInspectedSheets':[1,2,3,4],'findings':findings[ident],'fullMasterApproval':False})
  assert read(e.H/'observed-guides.json')['sourceEvidenceSha256']==sha(tp)

checkpoint=read(B/'checkpoint.json')
checkpoint.update(updatedAt=now,active=[],currentJobs=[],stage='eleven-ready-five-source-and-cue-matching')
checkpoint['partialFhdRestoration']={'worker':rel(B/'available-fhd-job.json'),'status':'finite-worker-finished',
 'restoredSlots':16,'episodes':{'M10':7,'M11':2,'M12':4,'M17':3},'guideReviews':all_reviews,
 'masterCountAdded':0,'fullMastersReady':11,'remainingEpisodes':5,'sourceReadyIsNotMasterApproval':True}
checkpoint['nextAction']='Do not rerun completed FHD restoration. Continue exact Uncle cut matching (M11 start342 candidate; reject325), M10 village search and genuine FHD Portal2 source search. Preserve official-source narration constraints. Remaining guide gaps: M11-02 floor, M12-21, M17-14 exact orbit/occlusion cue correspondence; short old contour coverage requires final review. No new TTS, rewrite, low-resolution upscale, upload or full-master approval without actual QA.'
save(B/'checkpoint.json',checkpoint)
blockers=read(B/'source-blockers.json')
for ident in ['M09','M10','M11','M12','M17']:
 blockers[ident]['updatedAt']=now
 if ident in all_reviews:
  blockers[ident]['partialFhdReview']=all_reviews[ident]
  blockers[ident]['shortStatus']='남은 FHD·발화 대응·표식 확인 중'
  blockers[ident]['availableOriginalFhdRestored']={'M10':7,'M11':2,'M12':4,'M17':3}[ident]
 if ident=='M17':blockers[ident]['additionalCueGap']='Scene14 local13.5–17s building edits do not show the narrated camera orbit/occlusion; keep pending, never fabricate a tracking result.'
save(B/'source-blockers.json',blockers)
w=read(R/'shared/publishing/video-worklist.json')
w['privateMathPolish']['partialFhdRestoration']=checkpoint['partialFhdRestoration']
w['privateMathPolish']['sourceReplacementDecision']['summaryKo']='M07·M08 FHD 교체·최종 QA 완료. 남은5편은 설명 보강·검수 완료. M10 7개/M11 2개/M12 4개/M17 3개 원본 FHD 장면 복원 및 일부 표식 점검. 남은 FHD·발화 대응·표식은 미완료. 대본·음성·길이 유지.'
w['privateMathPolish']['updatedAt']=now;w['updatedAt']=now
save(R/'shared/publishing/video-worklist.json',w)
print('Partial source/guide evidence recorded; eleven full masters remain ready, five pending.')
