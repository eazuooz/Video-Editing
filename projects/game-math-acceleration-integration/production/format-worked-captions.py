"""Typeset the measured quantities in this lesson without changing its voice."""
from pathlib import Path
import hashlib,json,math
P=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
a=P/'planning/caption-reading-adjustments.json';old=read(a) if a.is_file() else {'groups':[]}
m=read(P/'planning/bilingual-caption-map.json')
groups={(s['id'],g['koStart']):g['en'] for s in m['scenes'] for g in s['groups']}
# Check the same numbers the viewer will see, before accepting their typography.
assert [round(sum(32*k*d*d for k in range(n)),2) for d,n in [(.4,6),(.2,12),(.1,24)]]==[76.80,84.48,88.32]
assert math.isclose(32*2.4**2/2,92.16)
t=math.sqrt(2*1353/32);assert round(t,3)==9.196 and round(32*t,2)==294.27
v=1353/12-.5*32*12;assert v==-79.25 and round(-v/32,3)==2.477 and round(-2*v/32,3)==4.953
edits={
 ('002',0):'Velocity is measured in m/s. Acceleration is the change in velocity per second, measured in m/s².',
 ('002',2):'From rest at 4 m/s², velocity reaches 4 m/s after 1 s and 8 m/s after 2 s.',
 ('002',3):'Near Earth’s surface, gravity is about 9.8 m/s². For the following example in feet, use 32 ft/s² consistently.',
 ('003',1):'At a constant 32 ft/s² from rest, v = 32t in ft/s when t is in seconds.',
 ('003',2):'At t = 2.4 s, v = 76.8 ft/s.',
 ('007',0):'Divide 2.4 s into 6 intervals of 0.4 s.',
 ('007',2):'The first interval contributes 0 ft. In the next, multiply 12.8 ft/s by 0.4 s.',
 ('007',3):'The 6 rectangles sum to 76.8 ft.',
 ('008',0):'With 12 intervals of 0.2 s, the estimate is 84.48 ft.',
 ('008',1):'With 24 intervals of 0.1 s, it is 88.32 ft.',
 ('009',0):'The triangle has a base of 2.4 s and a height of 76.8 ft/s.',
 ('009',1):'Half their product is 92.16 ft.',
 ('009',3):'At time t the height is at. From rest, displacement is ½at².',
 ('010',0):'An initial velocity v₀ adds a rectangle under the line.',
 ('010',2):'Displacement is Δx = v₀t + ½at².',
 ('011',2):'The numerator uses −v₀ and the square root. The denominator is a, so a must be nonzero.',
 ('012',0):'Keep downward positive. Drop an object from rest to a point 1,353 ft below.',
 ('012',1):'Initial velocity is 0 and acceleration is 32 ft/s².',
 ('012',2):'The positive time is √(2 × 1,353 / 32) ≈ 9.196 s.',
 ('012',3):'Multiply by 32 ft/s²: the impact velocity is about 294.27 ft/s downward.',
 ('013',0):'This time, reach the same point exactly 12 s after launch.',
 ('013',1):'Solve for initial velocity: v₀ = Δx/t − ½at.',
 ('013',2):'1,353 / 12 = 112.75. Half of 32 × 12 is 192.',
 ('013',3):'The difference is −79.25 ft/s.',
 ('013',4):'Down is positive, so delaying arrival requires an upward throw at 79.25 ft/s.',
 ('014',2):'Solve −79.25 + 32t = 0. The apex is at about 2.477 s.',
 ('014',3):'At the starting height, displacement is 0. Factoring out t gives 0 s at launch and about 4.953 s on return.',
 ('015',1):'Subtract v₀t from the target displacement. Then a = 2(Δx − v₀t)/t².',
 ('015',2):'To cover 15 m in 3 s from 2 m/s, the initial speed supplies 6 m. Acceleration supplies the remaining 9 m: a = 2 m/s².',
 ('018',3):'Gravity’s magnitude g is positive; vertical acceleration is −g.',
 ('018',5):'From the launch point, x = v₀ₓt and y = v₀ᵧt − ½gt².',
 ('019',0):'At the apex, vertical velocity is 0, so the time to the apex is v₀ᵧ/g.',
 ('019',1):'Substituting that time gives a height gain of v₀ᵧ²/(2g).',
 ('020',1):'With launch speed s₀ and angle θ above horizontal, the components are s₀ cos θ and s₀ sin θ.',
 ('020',3):'Substitute into the range formula and use the double-angle identity. At equal launch and landing heights, range is s₀² sin(2θ)/g.',
 ('023',1):'Set the maximum height to 2 m and the time to the apex to 1 s.',
 ('023',2):'For height H and time T to the apex, g = 2H/T² and the initial vertical speed is 2H/T.',
 ('023',3):'That gives g = 4 m/s² and an initial vertical speed of 4 m/s.',
 ('023',4):'Returning to the same height takes 2 s. At 3 m/s horizontally, the jump covers 6 m.',
 ('025',1):'Split the interval into n equal pieces. Each has width Δx = (b − a)/n.',
 ('025',4):'The i-th left endpoint is a + (i − 1)Δx.',
 ('028',3):'At a constant 100 W for 2 s, the energy is 200 J. For varying power, accumulate the area under the graph.',
 ('031',1):'An antiderivative of t² is t³/3. Differentiating gives t² again.',
 ('031',2):'The power rule for integration excludes exponent −1: the new exponent would be 0.',
 ('031',3):'On an interval where t ≠ 0, an antiderivative of 1/t is ln|t|.',
 ('032',1):'Both t² + 3 and t² + 10 have derivative 2t.',
 ('032',2):'The indefinite integral of 2t is the family t² + C.',
 ('033',1):'If f is continuous and F is its antiderivative, its integral from a to b is F(b) − F(a): final value minus initial value.',
 ('034',0):'For a model with velocity v(t) = 2t in m/s, find the displacement from 1 s to 3 s.',
 ('034',1):'An antiderivative is t². Subtract the endpoint values: 9 − 1 = 8 m.',
}
ko={
 '구 점 팔 미터 매 초 제곱':'9.8 m/s²','매 초 제곱 삼십이 피트':'32 ft/s²',
 '이 점 사 초':'2.4초','초속 칠십육 점 팔 피트':'76.8 ft/s','초속 십이 점 팔 피트':'12.8 ft/s',
 '영 점 사 초':'0.4초','영 점 이 초':'0.2초','영 점 일 초':'0.1초',
 '칠십육 점 팔 피트':'76.8피트','팔십사 점 사팔 피트':'84.48피트','팔십팔 점 삼이 피트':'88.32피트','구십이 점 일육 피트':'92.16피트',
 '천삼백오십삼 피트':'1,353피트','구 점 일구육 초':'9.196초','초속 이백구십사 점 이칠 피트':'294.27 ft/s',
 '마이너스 칠십구 점 이오':'−79.25','초속 칠십구 점 이오 피트':'79.25 ft/s',
 '이 점 사칠칠 초':'2.477초','사 점 구오삼 초':'4.953초','백십이 점 칠오':'112.75',
 '브이 영 티 더하기 이분의 일 에이 티 제곱':'v₀t + ½at²','이분의 일 에이 티 제곱':'½at²','로그 티의 절댓값':'ln|t|',
 '티 세제곱 나누기 삼':'t³/3','티 제곱 더하기 상수 씨':'t² + C','초속 삼 미터':'3 m/s','매 초 제곱 사 미터':'4 m/s²',
}
text=[s['displayLines'][0] for s in read(P/'script/narration.ko.json')['scenes']]
# The additive V2 voice explains these operators in words; keep only exact
# literal display spans that still occur in the selected text.
ko={k:v for k,v in ko.items() if any(k in s for s in text)}
prior={(x['scene'],x['koStart']):x for x in old['groups']}
for key,caption in edits.items():
 if key in prior:assert prior[key]['caption']==caption,'Preserve another editor’s wording'
 prior[key]=dict(scene=key[0],koStart=key[1],source=groups[key],caption=caption,reason='Keep stated physical units, sign convention, assumptions and worked values legible at narration speed.')
old.update(groups=list(prior.values()),koPrintedForms={**old.get('koPrintedForms',{}),**ko},status='Worked quantities checked against source and recomputed; final speech alignment and encoded review pending.')
a.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(edits),'English meaning groups;',len(ko),'Korean printed forms. Source voice unchanged.')
