"""Remove mismatched later shapes; place the inspected square-processing cut on its clause."""
from common import *
import runpy
P=R/'projects/game-math-polygon-partition-v2';H=P/'production/concept-fit-v2';authorized('M14')
for name in ['composition','qa','outputs','caption-pixel-coverage','timeline']:
 dst=H/(name+'-before-square-cue.json')
 if not dst.exists():save(dst,read(H/(name+'.json')))
src=B/'compose-m14.py';code=src.read_text(encoding='utf8');data=runpy.run_path(str(src));shots=data['SHOTS']
shots['QG06'].update(seconds=1.1,offset=2.4,phases=[(0,1.1,'사각형 절단 · 아래 기계에서 조각 회전')])
a=code.index('SHOTS=');b=code.index('\nENC=',a);code=code[:a]+'SHOTS='+repr(shots)+code[b:];src.write_text(code,encoding='utf8')
t=read(H/'timeline.json');s=next(x for x in t['scenes'] if x['id']=='QG06');s['gameWindowSeconds']=1.1
t['actualFrames']=round(sum(x['gameWindowSeconds'] for x in t['scenes'])*60);t['actualShare']=t['actualFrames']/t['bodyFrames'];t['explanationFrames']=t['bodyFrames']-t['actualFrames'];t['explanationShare']=1-t['actualShare'];save(H/'timeline.json',t)
r=read(H/'render-progress.json');r['identity']=hashlib.sha256((sha(B/'m14-scenes.py')+sha(B/'m03-scenes.py')+sha(H/'timeline.json')).encode()).hexdigest();save(H/'render-progress.json',r)
c=read(H/'composition.json');c['scenes']=[x for x in c['scenes'] if x['id']!='QG06'];c['completed']=False;c['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(src)).encode()).hexdigest();save(H/'composition.json',c)
p=read(H/'scene-visual-plan.json');p['sourceShots']=shots;p['squareCueRepair']=dict(reason='The later star cut did not match the spoken square. Keep only the native square cut and place it on the square-cutting clause; own continuous model explains the complete action.',sourceStart=42.8,sourceEnd=43.9,sceneOffset=2.4,slowdown=False,repeat=False,audioAndCaptionTimingUnchanged=True);save(H/'scene-visual-plan.json',p)
e=read(H/'source-evidence.json')
for x in e['selected']:
 if x['scene']=='QG06':x.update(seconds=1.1,offset=2.4,role='Only actual square cutter and subsequent rotators; remove later star processing')
e['squareSubsetNativePlayback']=dict(tool='cua_repl tab69',start=42.8,end=44.388041,rate=1,actualListening=False);save(H/'source-evidence.json',e)
run(['C:/Python/python.exe','-X','utf8',B/'compose-m14.py'])
print('One scene recomposited; parent playback must finish before final master replacement')
