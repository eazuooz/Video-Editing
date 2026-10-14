"""Preserve the exact six-frame observation and propose only native-action replacement."""
from pathlib import Path
import importlib.util,json,re
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
OP=P/'part1-input-overrides-v289.json';overrides=m.read(OP)
c=next(c for c in overrides['effectiveCuts'] if c['id']=='cyber-surface-observation:native')
assert c['proposedCuts']==[{'inFrame':618,'outFrame':710},{'inFrame':900,'outFrame':1764},{'inFrame':1980,'outFrame':2532}]
assert c['frames']==1508 and c['fromFrame']==47974 and c['toFrame']==49482
new=[{'inFrame':618,'outFrame':716},{'inFrame':906,'outFrame':1764},{'inFrame':1980,'outFrame':2532}]
assert sum(x['outFrame']-x['inFrame'] for x in new)==1508
other=[(s['inFrame'],s['outFrame']) for a in overrides['effectiveCuts'] if a['id']!=c['id'] and a.get('video',{}).get('path')==c['video']['path'] for s in a.get('proposedCuts',[])]
assert all(not (a<716 and b>710) for a,b in other),other
assert m.sha(R/c['video']['path'])==c['video']['sha256']
images=[]
for n in ['before','after','first24']:
 p=R/f'production/research/game-lighting-history/local/cyber-promo-boundary-v315-{n}.png';images.append({'path':m.rel(p),'sha256':m.sha(p)})
proof={'createdAt':m.stamp(),'id':c['id'],'historicalBoard':208,'historicalIssuePreserved':True,'source':c['video'],'oldCuts':c['proposedCuts'],'proposedCuts':new,'sourcePromoFramesInclusive':[900,905],'finalPromoFramesInclusive':[48066,48071],'totalFrames':1508,'replacementUnusedSourceFramesExclusive':[710,716],'otherCurrentCutsSourceIntervals':other,'allOtherSourceMappingFromFinal48072Identical':True,'directBoundaryObservation':'The6x4 source900–923 grid shows a black promotional title only900–905;906–923 shows actual wet-alley action. Source710,724,737 show the same continuous neon plaza. Replace6titleframes with6unused plaza frames; no repeated frames, speed change or audio edit.','images':images,'allImagesDirectlyRead':True,'fullProposedSourceNormalSpeedReviewed':False,'audioCaptionPlanTimingChanged':False,'finalPixelsApproved':False,'uploaded':False,'newGitImages':0}
path=P/'part1-promo-boundary-proposal-v315.json';assert not path.exists();m.save(path,proof)
html=(R/'production/research/game-lighting-history/local/part1-vt-conversion-review-v306.html').read_text('utf8')
row={'id':c['id'],'path':c['video']['path'],'ranges':[[x['inFrame']/60,x['outFrame']/60] for x in new],'ko':'정상 속도로 실제 간판/광장→젖은 골목→재구성 비교를 확인. 소스900–905홍보6프레임은 제외하고710–715의 고유 실제 동작으로 대체. RTX ON/OFF와DLSSOff/3.5는 묶음 조건이며 단일기능 성능 증거가 아님.'}
html=re.sub(r'const rows=\[.*?\];const pick',lambda _: 'const rows='+json.dumps([row],ensure_ascii=False)+';const pick',html,flags=re.S)
html=html.replace('가상 텍스처 변환 · 실제 방향과 목록 타이밍 재검수','사이버펑크 · 홍보6프레임 대체 후보 검수')
hp=R/'production/research/game-lighting-history/local/part1-promo-source-review-v315.html';hp.write_text(html,'utf8')
print(json.dumps({'proof':m.rel(path),'html':m.rel(hp),'normalMovingApproved':False}))
