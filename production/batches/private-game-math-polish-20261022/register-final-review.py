"""Register already written direct-review evidence; never create approval."""
import datetime, sys
from polish_common import *

ident=sys.argv[1]
assert ident in {'M11','M12','M17'}
e=Episode(ident);e.authorized()
v=read(e.H/'visual-review.json');qa=read(e.H/'technical-qa.json')
samples=read(e.H/'final-pixel-samples.json')
digest=sha(e.D/f'{e.slug}.captioned.mp4')
assert v['status']=='passed' and v['captionedSha256']==digest
assert samples['captionedMasterSha256']==digest
assert v['directlyInspectedSheets']==list(range(1,samples['sheets']+1))
assert v['humanReview']=='pending' and v['readyForHumanReview'] is True
assert len(qa['outputs'])==2 and all(x['fullDecode'] for x in qa['outputs'])
assert next(x for x in qa['outputs'] if x['kind']=='captioned')['sha256']==digest
qa['directVisualReview']=rel(e.H/'visual-review.json');save(e.H/'technical-qa.json',qa)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
cp=read(B/'checkpoint.json');cp['updatedAt']=now
cp['ready']=sorted(set(cp.get('ready',[])+[ident]))
cp['active']=[x for x in cp['active'] if x!=ident]
cp['deliverySummary'].update(readyCount=len(cp['ready']),ready=cp['ready'],productionCount=len(cp['active']),production=cp['active'],blockedCount=0,sourceBlocked=[],allSixteenComplete=len(cp['ready'])==16,humanReview='pending')
cp['completedJobs'].append(f'{ident} current{digest[:12]}: all{len(samples["samples"])} final encoded samples on{samples["sheets"]} sheets and listed native frames directly inspected; selected current-master playback observed. Both1080p60 masters pass full decode/frame/audio/caption tests. Four local outputs ready; actual human review/listening pending.')
cp['nextAction']=('All16 ready for local human review. Verify final delivery evidence, selectively commit/push and stop only automation16 through its official tool. No upload or other-video advancement.' if len(cp['ready'])==16 else f'{len(cp["ready"])}/16 locally ready. Preserve finite worker72568. Review remaining {", ".join(cp["active"])} current masters after technical QA/sampling. No TTS/platform actions.')
summary=f'{len(cp["ready"])}편 검수대기. '+('16편 내부 QA 및 로컬 전달 준비 완료; 사용자 검수 대기.' if not cp['active'] else '남은 '+ '·'.join(cp['active'])+' 전체1080p60 렌더·최종 화면 검수 진행 중.')+' FHD 게임24장면·설명66장면 유지, 승인된 Portal2 원래 해상도10장면만 예외 적용.'
cp['sourceReplacementDecision']['summaryKo']=summary
save(B/'checkpoint.json',cp)
w=read(R/'shared/publishing/video-worklist.json');w['privateMathPolish']['sourceReplacementDecision']['summaryKo']=summary;save(R/'shared/publishing/video-worklist.json',w)
c=read(R/'shared/publishing/video-production-control.json');c['scopedBatchAuthorizations']['private-math-overnight-polish-20261022']['sourceReplacementDecision']['summaryKo']=summary;c['updatedAt']=now;save(R/'shared/publishing/video-production-control.json',c)
print(f'{ident} locally ready; {len(cp["ready"])}/16; human review pending.')
