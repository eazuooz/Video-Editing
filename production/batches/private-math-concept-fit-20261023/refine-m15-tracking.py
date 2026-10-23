from common import *
import ast,shutil
P=R/'projects/game-math-rendering-light';H=P/'production/concept-fit-v2';authorized('M15')
for name in ['composition','outputs','qa','caption-pixel-coverage']:
 dst=H/f'{name}-before-tracking-refine.json'
 if not dst.exists():shutil.copy2(H/f'{name}.json',dst)
p=B/'compose-m15.py';s=p.read_text(encoding='utf8');a=s.index('SHOTS=')+6;b=s.index('\nENC=',a);shots=ast.literal_eval(s[a:b])
centers=[(.454,.464),(.433,.464),(.433,.467),(.450,.500),(.466,.533),(.468,.548),(.473,.555),(.466,.564),(.472,.545),(.481,.491),(.490,.491),(.491,.558),(.510,.570),(.522,.573),(.511,.555),(.524,.527)]
shots['02']['track2']=[(3.5+i*.125,x,y,65) for i,(x,y) in enumerate(centers)]
s=s[:a]+repr(shots)+s[b:];p.write_text(s,encoding='utf8')
c=read(H/'composition.json');c['scenes']=[x for x in c['scenes'] if x['id']!='02'];c['completed']=False;c['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(p)).encode()).hexdigest();save(H/'composition.json',c)
save(H/'tracking-refinement.json',dict(checkedAt=now(),scene='02',reason='0.5s keys missed the short vertical jump; dense0.125s inspected centers follow the actual character.',sourceFrames='shared/output/private-math-concept-fit-20261023/candidates/m15-wall-jump',track=shots['02']['track2'],actualPixelReview='16 source frames on2 sheets directly inspected',otherSceneCompositesUnchanged=21))
page=R/'output/m15-source-review/selected.html';t=page.read_text(encoding='utf8').replace('data-a="1621" data-b="1625.5">05-hole 1621–1625.5','data-a="1595.65" data-b="1597.15">05-hole repaired 1595.65–1597.15');page.with_name('hole-repaired.html').write_text(t,encoding='utf8')
run(['C:/Python/python.exe','-X','utf8',p])
run(['C:/Python/python.exe','-X','utf8',B/'assemble-m15.py'])
run(['C:/Python/python.exe','-X','utf8',B/'qa-m15-guide-delta.py'])
