from common import *
import runpy
P=R/'projects/game-math-rendering-light';H=P/'production/concept-fit-v2';authorized('M15')
for name in ['composition','qa','outputs','caption-pixel-coverage','timeline','audio-mix','render-progress']:
 dst=H/(name+'-before-guide-repair.json')
 if not dst.exists():save(dst,read(H/(name+'.json')))
src=B/'compose-m15.py';code=src.read_text(encoding='utf8');shots=runpy.run_path(str(src))['SHOTS']
shots['02']['track']=[]
shots['02']['track2']=[(3.5,.455,.52,56),(4,.464,.55,56),(4.5,.47,.60,56),(5,.51,.63,56),(5.5,.54,.52,56)]
shots['05-hole'].update(start=1595.65,track=[(.1,.875,.13,64),(.35,.90,.16,64),(.6,.80,.16,64),(.85,.80,.15,64),(1.10,.80,.15,64),(1.35,.88,.13,64)])
shots['08-preview'].update(seconds=2,phases=[(0,2,'문틀 미리 보기 → 설치된 표면')],track=[(1,.3,.52,67),(1.7,.3,.52,67)])
a=code.index('SHOTS=');b=code.index('\nENC=',a);src.write_text(code[:a]+'SHOTS='+repr(shots)+code[b:],encoding='utf8')
t=read(H/'timeline.json');next(x for x in t['scenes'] if x['id']=='08')['gameWindowSeconds']=8
t['actualFrames']=round(sum(x['gameWindowSeconds'] for x in t['scenes'])*60);t['actualShare']=t['actualFrames']/t['bodyFrames'];t['explanationFrames']=t['bodyFrames']-t['actualFrames'];t['explanationShare']=1-t['actualShare'];save(H/'timeline.json',t)
r=read(H/'render-progress.json');r['identity']=hashlib.sha256((sha(B/'m15-scenes.py')+sha(B/'m03-scenes.py')+sha(H/'timeline.json')).encode()).hexdigest();r['identityRenewalReason']='Only footage share changed; every model timeline/frame count and saved model SHA remains unchanged.';save(H/'render-progress.json',r)
c=read(H/'composition.json');c['scenes']=[s for s in c['scenes'] if s['id'] not in ['02','05','08']];c['completed']=False;c['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(src)).encode()).hexdigest();save(H/'composition.json',c)
p=read(H/'scene-visual-plan.json');p['sourceShots']=shots;p['finalGuideRepair']=dict(reason='Direct final-frame inspection found a hidden-character ring, a hole mark on the sky and an irrelevant build menu.',changes=['02 mark visible character only519–521 with observed keyframes; hide while occluded','05 replace head-up shot with1595.65–1597.15 visible round holes and background trees','08 cut742–744 only, remove menu744–745'],narrationAndCaptionTimingUnchanged=True,newTts=False);save(H/'scene-visual-plan.json',p)
e=read(H/'source-evidence.json');e['finalGuideRepair']=p['finalGuideRepair'];e['finalShots']=shots;save(H/'source-evidence.json',e)
save(H/'parent-pixel-review.json',dict(masterSha256=read(H/'outputs-before-guide-repair.json')['outputs'][1]['sha256'],checkedAt=now(),directlyViewed=dict(finalFrames=173,finalSheets=15,extraCaptionFrames=157,captionSheets=14,cues=218,mobileFrames=12),findings=p['finalGuideRepair'],otherScenes='No clipping/caption collision or material action mismatch found in the inspected unchanged scenes.',actualListening=False))
run(['C:/Python/python.exe','-X','utf8',B/'compose-m15.py'])
run([R/'qwen3-tts/.venv/Scripts/python.exe','-X','utf8',B/'mix-m15.py'])
print('Three compositions and source mix repaired. Do not replace parent master before its active playback ends.')
