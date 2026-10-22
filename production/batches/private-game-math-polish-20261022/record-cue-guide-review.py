"""Record the directly inspected new floor/tower guides, not a full master."""
import datetime,subprocess
from polish_common import *
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
details={
 'M11':{'count':21,'sheets':3,'changed':['02','02-recap'],'finding':'Scene02 now has visible sand/wood-top regions at4–5s and5.5–7s and ground recap at37.5–40s. Current-source regions remain clear of weapons, HUD and fixed captions. Screen-space regions are editorial guides, not measured world planes.'},
 'M12':{'count':22,'sheets':3,'changed':['21','21-recap'],'finding':'Scene21 now follows the same left watchtower roof/upper wall at2.5–4s and39.5–41.5s. Regions hide outside the observed spans and before the damage overlay. No inferred mesh or shader data.'}}
for ident,d in details.items():
 e=Episode(ident);e.authorized();p=e.H/'observed-guide-preflight.json';pre=read(p)
 assert len(pre['samples'])==d['count'] and pre['sheets']==d['sheets'] and pre['assSha256']==sha(e.O/'composition-polish.ass')
 pre.update(status='passed-partial-still-inspection',reviewedAt=now,directlyInspectedSheets=[1,2,3],findings=[d['finding']],fullMasterReady=False,finalMovingReview='selected-preview-start-and-end-states-only; full-master-pending')
 save(p,pre)
 mp=e.H/'moving-available-guide-preflight.json';moving=read(mp)
 old=json.loads(subprocess.check_output(['git','show','HEAD:'+rel(mp)],cwd=R).decode('utf8'))
 prior={c['path']:c for c in old['clips']}
 for c in moving['clips']:
  assert sha(R/c['path'])==c['sha256']
  if c['name'] in d['changed']:
   c['currentPixels']='native-speed-browser-start-and-end-states-observed; intermediate-half-second-captioned-stills-inspected'
  elif c['path'] in prior and prior[c['path']]['sha256']==c['sha256']:
   c['currentPixels']='unchanged-preview-hash-prior-selected-playback-evidence-reused'
  else:c['currentPixels']='current-half-second-stills-inspected; prior-playback-context-only'
 moving.update(status='selected-native-playback-states-observed',reviewedAt=now,method='Observed start/end states during native-speed browser playback of the four new windows, together with all43 current captioned stills at375px; not full temporal coverage or listening approval.',fullMasterApproval=False)
 save(mp,moving)
 review=read(e.H/'available-guides-review.json')
 review.update(reviewedAt=now,preflightSha256=sha(p),sampleCount=d['count'],sheetCount=d['sheets'],selectedPlaybackSha256=sha(mp),findings=[d['finding'],'Previously checked unchanged Noita clips retain their prior evidence; current composed stills were reinspected.','Remaining source replacements, exact narration correspondence and whole-master QA remain pending.'],fullMasterReady=False)
 save(e.H/'available-guides-review.json',review)
 additions=read(e.H/'cue-guide-additions.json');additions.update(status='passed-partial-current-composited-review',review=rel(e.H/'available-guides-review.json'),reviewedAt=now);save(e.H/'cue-guide-additions.json',additions)
checkpoint=read(B/'checkpoint.json');checkpoint.update(updatedAt=now)
checkpoint['cueGuideRepair']={'reviewedAt':now,'M11':'02 floor/top-surface guides added and current375px+selected native playback checked','M12':'21 same-roof/wall guides added and current375px+selected native playback checked','additionalFullMasters':0}
checkpoint['nextAction']='Finish Uncle native-FHD replacement action/cue inspection from uncle-cut-review-v2 (same scene durations, revised internal excerpts to exclude falls/resets); M17-14 orbit/occlusion cue repair and remaining Portal2/village FHD sources remain. Do not rerun completed16 FHD restores or11 ready masters.'
save(B/'checkpoint.json',checkpoint)
blockers=read(B/'source-blockers.json')
for ident in details:
 blockers[ident]['updatedAt']=now;blockers[ident]['guideGapRepair']=details[ident]['finding']
save(B/'source-blockers.json',blockers)
w=read(R/'shared/publishing/video-worklist.json');w['privateMathPolish']['cueGuideRepair']=checkpoint['cueGuideRepair'];w['privateMathPolish']['updatedAt']=now;w['updatedAt']=now;save(R/'shared/publishing/video-worklist.json',w)
print('M11/M12 cue-guide gaps repaired;11 full masters ready,5 remain incomplete.')
