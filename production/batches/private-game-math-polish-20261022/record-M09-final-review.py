"""Record the directly inspected M09 final master; never infer human approval."""
import datetime
from polish_common import *

e=Episode('M09'); e.authorized()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
digest='514aaa1e0802efc9a65823f5fee82b05565ec692c23ed039332854542dfd7769'
assert sha(e.D/f'{e.slug}.captioned.mp4') == digest
samples=read(e.H/'final-pixel-samples.json')
assert samples['captionedMasterSha256']==digest and len(samples['samples'])==412
save(e.H/'visual-review.json',{
 'status':'passed','captionedSha256':digest,'reviewedAt':now,
 'sampleManifest':rel(e.H/'final-pixel-samples.json'),
 'directlyInspectedSheets':list(range(1,36)),
 'directlyInspectedNativeImages':['0163.png','0290.png'],
 'coverage':'All412 current encoded samples on35 sheets with375px-wide tiles: every150 caption cue, scene/source joins, representative diagram states and restored guide interval boundaries/midpoints. Two native1920x1080 frames inspected. Discrete samples and selected browser start/end observations, not continuous whole-film watching or listening.',
 'findings':[
  {'scene':'LG01','status':'passed-sampled','description':'Restored approved Portal2 shot: line follows the visible beam, clears across cuts, and the removed math note leaves the exit indicators visible. Existing caption geometry remains clear. Overlay is an editorial screen-space guide, not engine measurement.'},
  {'scene':'parameter/normal representations','status':'passed-sampled','description':'Circle translation, p=o+t delta, segment/line/ray domains, the (5,2.5) midpoint and normal-form example remain ordered and legible with separated semantic colors.'},
  {'scene':'remaining games and joins','status':'passed-sampled','description':'Inspected endpoint/connector states, source cut resets, caption bounds, original palette, branding and ending; no new issue found in reviewed samples.'}
 ],
 'browserCheck':{
  'url':'http://127.0.0.1:9248/projects/game-math-lines-circles-v2/production/local/private-polish-v1/moving-review.html',
  'source':'current captioned master','decodedDimensions':[1920,1080],
  'durationSeconds':667.95,'displayWidths':['large viewport','375px'],
  'seekStartSeconds':[210,378,493], 'observedAdvancingSeconds':[227.22,405.04,515.68],
  'playbackAndSeek':'passed-selected-start/end-observations',
  'audio':'muted; no listening claim','temporaryTabClosed':True
 },
 'wholeListening':'pending-user; recovered compressed audio preserved by decoded hash, not claimed as original PCM',
 'humanReview':'pending','readyForHumanReview':True
})
qa=read(e.H/'technical-qa.json'); qa['directVisualReview']=rel(e.H/'visual-review.json');save(e.H/'technical-qa.json',qa)
cp=read(B/'checkpoint.json'); cp['updatedAt']=now
cp['ready']=sorted(set(cp.get('ready',[])+['M09']))
cp['active']=[x for x in cp['active'] if x!='M09']
cp['deliverySummary'].update(readyCount=len(cp['ready']),ready=cp['ready'],productionCount=len(cp['active']),production=cp['active'],blockedCount=0,sourceBlocked=[],allSixteenComplete=False,humanReview='pending')
cp['completedJobs'].append('M09 current514aaa1e0802: all412 final encoded samples on35 sheets and native frames0163/0290 inspected; selected current-master browser playback/seek at large/mobile sizes observed. Both1080p60 outputs pass full decode/frame/audio/caption tests. Four local outputs ready; actual human review/listening pending.')
cp['nextAction']='M09 now locally ready, total12/16. Do not duplicate or terminate finite worker72568; read approved-portal-finish-job.json and review current finished M10/M11/M12/M17 masters after technical QA/sampling. No TTS or platform actions.'
save(B/'checkpoint.json',cp)
print('M09 locally ready; 12/16; human review pending.')
