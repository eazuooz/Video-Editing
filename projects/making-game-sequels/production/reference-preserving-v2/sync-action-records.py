"""Keep current scene records and their regeneration recipes on the verified action."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';V=P/'production/reference-preserving-v2'
replacements={
 '피크민4의 오치':'피크민4의 와치',
 '우주견 오치':'우주견 와치',
 '지금은 오치에게 흙더미를 파게 한 뒤, 흙더미가 사라지고 안에 묻혀 있던 물건이 드러납니다.':'와치가 몸으로 들이받는 돌진을 쓰면, 항아리가 깨지고 안에 있던 물건이 드러납니다.',
 'Here Oatchi is sent to excavate a dirt mound, removing the soil and revealing a buried object.':'Oatchi can Rush forward to smash the pots, revealing the items inside.',
 '피크민4에서 오치에게 흙더미 파기 지시, 발굴과 묻힌 물건 노출.':'피크민4에서 와치가 돌진해 항아리를 깨고 물건이 나타나는 행동.',
 '동료 선택 → 일 맡김 → 상태 변화':'항아리 선택 → 와치 돌진 → 파괴와 물건 등장',
 'pikmin4-day2:327–347,520–565':'pikmin4-day2:331.5–336.8,341.5–349.5,520–565',
 '330전상태/334작업/344결과 실제스샷.':'333.5전상태/336.5파괴/348결과 실제스샷.',
 'Removed unsupported claim that Oatchi excavation opens a traversable path; show removal of soil and exposure of buried object':'Corrected concurrent excavation HUD notice versus actual Oatchi Rush, pot destruction and exposed items; Korean official name 와치',
 'wall instruction/result and Oatchi soil removal confirmed; game actions and HUD match current narration':'wall instruction/result and Oatchi Rush/pot break/items confirmed; distinguish concurrent excavation HUD notice',
 '피크민: 오치 발굴':'피크민: 와치 돌진과 항아리',
 "'pikmin4-day2',327,347":"'pikmin4-day2',331.5,349.5",
 '331.5–337.8':'331.5–336.8',
 '[[331.5,337.8]':'[[331.5,336.8]',
 '[338,341]':'[337,341]'
}
def walk(v):
 if isinstance(v,str):
  for a,b in replacements.items():v=v.replace(a,b)
  return v
 if isinstance(v,list):return [walk(x) for x in v]
 if isinstance(v,dict):return {k:walk(x) for k,x in v.items()}
 return v
for name in ['finalize-design.py','record-design.py','prepare-revision.py','write-script.py','source-review-page.py','correct-action-match.py']:
 p=V/name;s=p.read_text(encoding='utf8')
 for a,b in replacements.items():s=s.replace(a,b)
 p.write_text(s,encoding='utf8')
p=P/'planning/chapter-plan.json';j=json.loads(p.read_text(encoding='utf8'));r=walk(j['currentRevision']);r['currentAnnotationPlan']='production/reference-preserving-v2/source-annotations.json'
r['canonicalActionTerms']=[{'ko':'와치','en':'Oatchi','meaning':'피크민4의 동료 구조견','firstScene':'07','source':'https://www.nintendo.com/kr/switch/ampya/'},{'ko':'돌진','en':'Rush','meaning':'몸으로 빠르게 들이받는 와치의 능력','firstScene':'07','source':'https://www.nintendo.com/kr/switch/ampya/guide/index.html'}]
r['scriptInternalReview']['continuousSourceMotionReview']='Representative native playback and consecutive source frames inspected; full selected-cut moving output remains pending'
j['currentRevision']=r;p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Current plan and generation recipes synchronized; historical baseline preserved.')
