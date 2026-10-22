"""Record actual, version-bound M10 observations, without human approval."""
import datetime
from polish_common import *

e=Episode('M10'); e.authorized()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
digest='57fd721c5a99fb4edbf19f0552af35f2b6f8b7cf25690f89e3201a106965a4ac'
assert sha(e.D/f'{e.slug}.captioned.mp4')==digest
samples=read(e.H/'final-pixel-samples.json')
assert samples['captionedMasterSha256']==digest and len(samples['samples'])==531
save(e.H/'visual-review.json',{
 'status':'passed','captionedSha256':digest,'reviewedAt':now,
 'sampleManifest':rel(e.H/'final-pixel-samples.json'),
 'directlyInspectedSheets':list(range(1,46)),
 'directlyInspectedNativeImages':['0241.png','0207.png','0423.png'],
 'coverage':'All531 current encoded samples on45 sheets with375px-wide tiles: every216 caption cue, scene/source joins, representative diagram states and guide interval boundaries/midpoints. Three native1920x1080 frames inspected. Discrete samples and selected browser start/end observations, not continuous whole-film watching or listening.',
 'findings':[
  {'scene':'LG05 Portal2','status':'passed-sampled','description':'Red selected visible cube-face contour and blue screen-aligned bounds match the observed upper face at463.37s and sampled interval states. Guides clear before the target exits. Removed math card leaves scene context visible. Existing caption explicitly distinguishes editorial screen bounds from internal collision data.'},
  {'scene':'bounds/code/formulas','status':'passed-sampled','description':'Five-point bounds min(-5,-7,-5), max(7,11,8), center(1,2,1.5), half(6,9,6.5) stay readable with semantic code colors and separate line frame. AABB/OBB, overlap/touch caveat, failed two-corner rotation, full-corner transform and e-prime=elementwise-abs(A)e retain baseline order and useful distinctions.'},
  {'scene':'LB05 reflected interval','status':'passed-sampled','description':'For x-prime=-2x+1, endpoints3 and7 map to-5 and-13, sorted interval[-13,-5], center-9, half4. Colored endpoint identity stays consistent. Native and375px views keep worked numbers and fixed captions clear.'},
  {'scene':'remaining games and joins','status':'passed-sampled','description':'SeriousSam visible body/bridge parts and village pole/panel guides follow reviewed screen targets and clear at source cuts/occlusion. They are labeled selected visible parts, not measured engine geometry. All caption cues, overview, closing calculation and ending sampled; no new obstruction or crop issue found.'}
 ],
 'browserCheck':{
  'url':'http://127.0.0.1:9248/projects/game-math-bounds-transform-v2/production/local/private-polish-v1/moving-review.html',
  'source':'current captioned master','decodedDimensions':[1920,1080],
  'durationSeconds':983.04,'displayWidths':[850,375],
  'seekStartSeconds':[461.5,602,694,789],
  'observedAdvancingSeconds':[469.68,616.29,756.91,810.74],
  'playbackAndSeek':'passed-selected-start/end-observations; elapsed intervals were not continuously watched',
  'audio':'muted; no listening claim','temporaryTabClosed':True
 },
 'wholeListening':'pending-user; recovered compressed audio preserved by decoded hash, not claimed as original PCM',
 'humanReview':'pending','readyForHumanReview':True
})
qa=read(e.H/'technical-qa.json');qa['directVisualReview']=rel(e.H/'visual-review.json');save(e.H/'technical-qa.json',qa)
cp=read(B/'checkpoint.json');cp['updatedAt']=now
cp['ready']=sorted(set(cp.get('ready',[])+['M10']))
cp['active']=[x for x in cp['active'] if x!='M10']
cp['deliverySummary'].update(readyCount=len(cp['ready']),ready=cp['ready'],productionCount=len(cp['active']),production=cp['active'],blockedCount=0,sourceBlocked=[],allSixteenComplete=False,humanReview='pending')
cp['completedJobs'].append('M10 current57fd721c5a99: all531 final encoded samples on45 sheets and native0241/0207/0423 inspected; selected current-master playback/seek at850px/375px observed. Both1080p60 outputs pass full decode/frame/audio/caption tests. Four local outputs ready; actual human review/listening pending.')
cp['nextAction']='M10 now locally ready, total13/16. Preserve finite worker72568; read approved-portal-finish-job.json and directly review finished M11/M12/M17 masters after technical QA/sampling. No TTS or platform actions.'
summary='13편 검수대기(M10 추가). 남은 M11·M12·M17은 모든 게임·설명 장면 복원 및 사전 점검 완료, 전체1080p60 렌더·최종 검수 진행 중. FHD 게임24장면·설명66장면 유지, 승인된 Portal2 원래 해상도10장면만 예외 적용.'
cp['sourceReplacementDecision']['summaryKo']=summary
save(B/'checkpoint.json',cp)
w=read(R/'shared/publishing/video-worklist.json')
w['privateMathPolish']['sourceReplacementDecision']['summaryKo']=summary
save(R/'shared/publishing/video-worklist.json',w)
c=read(R/'shared/publishing/video-production-control.json')
c['scopedBatchAuthorizations']['private-math-overnight-polish-20261022']['sourceReplacementDecision']['summaryKo']=summary
c['updatedAt']=now;save(R/'shared/publishing/video-production-control.json',c)
print('M10 locally ready; 13/16; human review pending.')
