"""Record manual inspection of the repaired, hash-bound M05 delivery."""
import datetime
from polish_common import *
e=Episode('M05');e.authorized();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
digest='dd5610d372dcbe93e1b4cc8b81d7d0ccf02ef897cdb5ca1a222e1728af598a3b'
assert sha(e.D/f'{e.slug}.captioned.mp4')==digest
samples=read(e.H/'final-pixel-samples.json');assert samples['captionedMasterSha256']==digest and len(samples['samples'])==697
save(e.H/'visual-review.json',{
 'status':'passed','captionedSha256':digest,'reviewedAt':now,'sampleManifest':rel(e.H/'final-pixel-samples.json'),
 'directlyInspectedSheets':list(range(1,60)),'directlyInspectedNativeImages':['0074.png'],
 'coverage':'All697 final encoded samples on59 sheets, with375px-wide tiles: every277 caption cue, every scene and source join, representative animation states, dense repaired GA06 guide and QF20 UI-clearance sequences. Native1920x1080 repaired N02 frame0074 inspected. Discrete/dense samples, not continuous whole-film viewing.',
 'findings':[
  {'scene':'N02/N09 and remaining repaired multiline beats','status':'passed','description':'Retained words and cue times; repaired64px line advance separates multiline text above fixed captions in the actual encoded master.'},
  {'scene':'GA06','status':'passed','description':'Dense213.2–216.22s samples follow the visible torso, then clear. Guide is editorial screen-space evidence, not engine orientation data.'},
  {'scene':'QF20','status':'passed','description':'Aspect-preserving game inset keeps native controls above fixed captions; source cuts reset tracked overlays. Dense encoded samples and375px browser playback checked.'},
  {'scene':'whole delivery','status':'passed-sampled','description':'Expected original palette, diagram order, numeric examples, caption bounds, branding and member ending remain. No new issue found in reviewed samples.'}
 ],
 'browserCheck':{'url':'http://127.0.0.1:9248/projects/game-math-quaternion-foundations-v3/production/local/private-polish-v1/moving-review.html','source':'current captioned master','decodedDimensions':[1920,1080],'durationSeconds':1349.083333,'displayWidths':['large viewport','375px'],'seekStartSeconds':[208.7,351.4,1128.0],'observedAdvancingSeconds':[228.32,245.36,389.08,1137.00,1138.66],'playbackAndSeek':'passed','audio':'muted; no listening claim','temporaryTabClosed':True},
 'wholeListening':'pending-user; recovered audio stream remains unchanged by decoded hash',
 'finalRepairedMasterReview':'completed sampled visual review and playback/seek checks','humanReview':'pending','readyForHumanReview':True
})
qa=read(e.H/'technical-qa.json');qa['directVisualReview']=rel(e.H/'visual-review.json');save(e.H/'technical-qa.json',qa)
cp=read(B/'checkpoint.json');cp['updatedAt']=now;cp['ready']=sorted(set(cp.get('ready',[])+['M05']));cp['active']=[x for x in cp['active'] if x!='M05']
cp['completedJobs'].append('M05 repaired master dd5610d372dc: all697 current final samples on59 sheets plus native multiline frame inspected; large/mobile browser playback and seek checked. Technical1080p60/full-decode/frame/audio/caption checks passed; four outputs now locally ready for human review. Human approval remains pending; no upload.')
cp['nextAction']='M05 is locally ready for user review. Do not duplicate or terminate existing queues: PID9600 now assembles M15, then PID43600 M06, PID60248 M16, PID41764 M18, PID29088 M19, PID67440 M20, PID34688 M13/M14. Inspect each current final encoded output before marking ready. Polygon numeric font/header-safe mapping preflight is being revised; preserve original logical geometry/clock. M07-M12/M17 await the existing source decision. No upload or work beyondM20.'
for job in cp.get('jobs',[]):
 p=R/job.get('statusFile','')
 if p.is_file():job.update(read(p))
save(B/'checkpoint.json',cp)
print('M05 manual review recorded; human approval pending')
