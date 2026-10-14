"""Preserve the sealed audio timeline while correcting evidenced native pixels.

This prepares editable input overrides and a source-review page only. It does
not render, approve final pixels or substitute an unmixed transcript for ASR.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, copy
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'production/research/game-lighting-history'
P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
plan_path=P/'part1-final-input-plan-v240.json';plan=read(plan_path)
base=read(P/'part1-final-visual-build-v245.json')
assert base['planSha256']==sha(plan_path) and base['frames']==89148
changes={
 'horizon-detail-motion:native':{
  'reason':'Normal playback showed heads in the outlined region before the source zoomed to embroidery. Enable embroidery marks after the zoom.',
  'tracking':{'label':'같은 자수 경계 · 화면 좌표 관찰','labelX':650,'labelY':96,'boxes':[
   {'from':0.75,'to':341/60,'x0':322,'y0':145,'x1':332,'y1':145,'width':310,'height':280,'color':'red'},
   {'from':0.75,'to':341/60,'x0':1281,'y0':145,'x1':1284,'y1':145,'width':310,'height':280,'color':'0x73c7c2'}]}},
 'outer-displayed-frames:native':{
  'reason':'The central source FPS card is left of the old rectangle; its later cards remain at the right, including the 5x view. Preserve the source top row.',
  'tracking':{'matteFrom':'bottom','label':'원본 표시 프레임 값 · 시뮬레이션 횟수 아님','labelX':470,'labelY':680,'boxes':[
   {'from':0,'to':2.6,'x0':740,'y0':200,'x1':740,'y1':200,'width':460,'height':440,'color':'red'},
   {'from':4,'to':980/60,'x0':1600,'y0':0,'x1':1600,'y1':0,'width':320,'height':340,'color':'red'}]}},
 'cyber-light-reconstruction:native':{
  'reason':'Replace the black title card with unused normal-speed actual city action. Keep complete original FPS/conditions and RTX badge instead of cropping the top. Only mark the actual FPS card where its position is directly established; do not outline unrelated faces.',
  'proposedCuts':[{'inFrame':480,'outFrame':617},{'inFrame':2790,'outFrame':3738}],
  'captionMatteHeight':0,
  'tracking':{'label':'빛·반사 관찰 / 원본 FPS는 묶음 조건의 값','labelX':440,'labelY':100,'boxes':[
   {'from':137/60,'to':137/60+4,'x0':745,'y0':240,'x1':745,'y1':240,'width':430,'height':445,'color':'red'},
   {'from':137/60+6,'to':1085/60,'x0':1600,'y0':0,'x1':1600,'y1':0,'width':320,'height':340,'color':'red'}]}},
 'cyber-surface-observation:native':{
  'reason':'Independent source playback found a Ray Reconstruction title at source32s. Replace it with unused actual sign action, retaining the wet-floor and reconstruction comparisons and their bottom labels.',
  'proposedCuts':[{'inFrame':618,'outFrame':710},{'inFrame':900,'outFrame':1764},{'inFrame':1980,'outFrame':2532}]
 },
 'fortnite-mobile-test:native':{
  'reason':'Normal playback at the start and end places the diagnostic graph above the virtual joystick. Tighten the outline to the graph rather than enclosing the joystick.',
  'tracking':{'label':'원본 진단 그래프 / 실제 표면 · 별도 자료','labelX':690,'labelY':90,'boxes':[
   {'from':0,'to':19,'x0':105,'y0':90,'x1':105,'y1':90,'width':545,'height':550,'color':'red'}]}
 }
}
effective=copy.deepcopy(plan['cuts'])
for c in effective:
 if c['id'] in changes:
  q=changes[c['id']]
  for key in ('proposedCuts','captionMatteHeight'):
   if key in q:c[key]=copy.deepcopy(q[key])
  assert sum(s['outFrame']-s['inFrame'] for s in c['proposedCuts'])==c['frames']
assert [(c['id'],c['kind'],c['frames'],c['fromFrame'],c['toFrame']) for c in effective]==[(c['id'],c['kind'],c['frames'],c['fromFrame'],c['toFrame']) for c in plan['cuts']]
rows=[]
cyber=next(c for c in effective if c['id']=='cyber-light-reconstruction:native')
for c in effective:
 if c['id'] not in changes:continue
 assert sha(ROOT/c['video']['path'])==c['video']['sha256']
 ranges=[[s['inFrame']/60,s['outFrame']/60] for s in c['proposedCuts']]
 rows.append({'id':c['id'],'path':c['video']['path'],'sha256':c['video']['sha256'],'ranges':ranges,'ko':next(p['ko'] for p in plan['paragraphs'] if p['id']==c['paragraphId'])})
source=(R/'local/part3-explanation-moving-input-review-v151.html').read_text('utf-8')
a=source.index('const rows=');b=source.index('];const pick',a)
source=source[:a]+'const rows='+json.dumps(rows,ensure_ascii=False)+source[b+1:]
source=source.replace('현재 2.5D 설명 입력의 정상 속도 검수','④-1 원본 수정 범위의 정상 속도 검수').replace('입력의 움직임 확인 · 최종 자막 합성 픽셀 승인과 구별','제목 카드 제외 · 정상 속도 · 원본 표시·조건 보존 · 합성 표식은 다음 검수')
html=R/'local/part1-native-overrides-review-v249.html';dest=P/'part1-input-overrides-v249.json'
if dest.exists():
 assert read(dest)['preparedOnly'] and not read(dest)['allCurrentMovingPixelsReviewed']
 assert not (P/'part1-native-pixels-execution-v250.json').exists(), 'Rendered overrides are immutable.'
html.write_text(source,'utf-8')
record={'preparedAt':datetime.now(timezone.utc).isoformat(),'preparedOnly':True,'inputPlan':{'path':rel(plan_path),'sha256':sha(plan_path)},'baselineVisual':{'path':base['path'],'sha256':base['sha256']},'changes':changes,'effectiveCuts':effective,'timelineEquivalence':{'same94CutIdsKindsLengthsAndStarts':True,'same89148FinalFrames':True,'same53057ActualAnd35371ExplanationFrames':True,'sameParagraphsPcmMixCaptionsAndChapters':True,'mixedAsrRequestRemainsBoundToUnchangedAudioPlan':True},'sourceReview':{'html':rel(html),'htmlSha256':sha(html),'rows':rows,'allNormalSourcePlaybackDirectlyReviewed':False},'allCurrentMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,'qaApproved':False,'uploaded':False,'sourceAudio':0,'loops':0,'slowdown':0,'newTts':0,'newGitImages':0,'humanPronunciation':'pending'}
dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'preparedRepairs':len(changes),'sameFrames':89148,'approved':False}))
