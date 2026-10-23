from common import *
import runpy
H=R/'projects/game-math-mesh-uv/production/concept-fit-v2';p=B/'compose-m19.py';s=p.read_text(encoding='utf8');shots=runpy.run_path(str(p))['SHOTS']
shots['02']['track']=[(1.5,.76,.43,85),(2,.76,.43,85),(2.5,.76,.42,85),(3,.78,.27,85),(3.5,.78,.25,85),(4,.79,.25,85),(4.9,.79,.24,85)]
a=s.index('SHOTS=');z=s.index('ENC=',a);p.write_text(s[:a]+'SHOTS='+repr(shots)+'\n'+s[z:],encoding='utf8')
for name in ['source-evidence.json','scene-visual-plan.json']:
 f=H/name;r=read(f);r['sourceShots']=shots;r['sourceGuideReview']='Roof focus ring follows observed34–39s roof editing at0.5s keyframes; clears at source cut. Screen-space attention cue, not a projected world-axis/measurement.';save(f,r)
print('M19 roof tracking guide saved')
