"""Record the observed pot-breaking action, without confusing a concurrent HUD notice."""
from pathlib import Path
import json,datetime,subprocess
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';V=P/'production/reference-preserving-v2';L=P/'production/local/reference-preserving-v2';S=P/'script/reference-preserving-v2'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for name in ['narration.ko.json','narration.tts.ko.json']:
 p=S/name;j=read(p);s=next(x for x in j['scenes'] if x['id']=='07')
 s['lines'][3]=s['lines'][3].replace('오치','와치')
 s['lines'][4]='와치가 몸으로 들이받는 돌진을 쓰면, 항아리가 깨지고 안에 있던 물건이 드러납니다. 대원들에게 일을 맡기는 것과 함께, 동료의 능력도 활용하는 거죠.'
 write(p,j)
ko=read(S/'narration.ko.json');(S/'narration.ko.txt').write_text('\n\n'.join('\n'.join(x['lines']) for x in ko['scenes'])+'\n',encoding='utf8')
p=S/'narration.en.json';j=read(p);s=next(x for x in j['scenes'] if x['id']=='07');s['lines'][4]='Oatchi can Rush forward to smash the pots, revealing the items inside. Alongside assigning jobs to Pikmin, the player can use the companion’s abilities.';write(p,j)
evidence={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'pikmin4-day2','correctedAction':'Oatchi Rush breaks pots and exposes items; not dirt-mound excavation','reason':'The dirt-mound excavation-completed HUD notice concerns a separate task. Consecutive source frames341–349 distinguish the pot attack at347 and exposed items at348.','usefulSourceRanges':[[331.5,336.8],[341.5,349.5]],'occlusionRangeToExclude':[337,341],'correctedScreenshots':{'before':333.5,'action':336.5,'result':348},'canonicalNames':{'ko':'와치 · 돌진','en':'Oatchi · Rush','sources':['https://www.nintendo.com/kr/switch/ampya/','https://www.nintendo.com/kr/switch/ampya/guide/index.html','https://en-americas-support.nintendo.com/app/answers/detail/a_id/62986/p/1076']},'ttsChange':'scene07 only; completed unchanged scenes preserved; restart current job at scene06 boundary before old scene07 is synthesized','newAudioReview':'pending'}
p=P/'planning/chapter-plan.json';j=read(p);rev=j['currentRevision'];rev['actionMatchCorrection']=evidence
for s in rev['scenes']:
 if s['id']=='07':s['sourceActionCorrection']=evidence
write(p,j)
p=P/'production/review-ledger.json';j=read(p);j['actionMatchCorrection']=evidence;j['footageInspection']['sourceActionMatch']='Wall instruction/result confirmed. Oatchi action corrected from concurrent excavation notice to visible Rush/pot break/items at331.5–336.8 and341.5–349.5.';write(p,j)
for name,sec in [('oatchi-before',333.5),('oatchi-work',336.5),('oatchi-result',348)]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(sec),'-i',str(L/'media/pikmin4-day2.mp4'),'-frames:v','1',str(L/'assets'/(name+'.png'))],check=True)
p=L/'assets/provenance.json';j=read(p)
for e in j:
 if e['name'] in ['oatchi-before','oatchi-work','oatchi-result']:e['time']={'oatchi-before':333.5,'oatchi-work':336.5,'oatchi-result':348}[e['name']]
write(p,j)
print('Scene07 action and Korean official naming corrected; new snapshot evidence recorded.')
