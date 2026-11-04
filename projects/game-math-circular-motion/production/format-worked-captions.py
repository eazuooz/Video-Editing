"""Canonical printed forms for M26's worked examples; retain spoken wording."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf8'))
file=P/'planning/caption-reading-adjustments.json'
mapping=read(P/'planning/bilingual-caption-map.json')
groups={(s['id'],g['koStart']):g['en'] for s in mapping['scenes'] for g in s['groups']}
replacements={
 ('018',1):'A pascal is 1 newton per square meter; a psi is 1 pound-force per square inch.',
 ('018',3):'1 pound-force is about 4.4482 N, and 1 inch is 0.0254 m.',
 ('018',5):'So 1 psi is about 6,894.757 Pa.',
 ('019',0):'We need psi per pascal. Take the reciprocal: 1 Pa ≈ 0.000145038 psi.',
 ('020',1):'From 0 to just before 2 s, position is 2t − t².',
 ('020',2):'From 2 to just before 4 s, it stays at 0. From 4 to just before 7 s, it oscillates as sin(πt).',
 ('020',3):'From 7 s onward, it follows 7 − t in the negative direction.',
 ('021',0):'Starting at 0, it reaches position 1 at 1 s and returns to 0 at 2 s.',
 ('021',1):'It then rests at 0 for 2 seconds.',
 ('021',2):'During the sine segment, position is 1 at 4.5 s, −1 at 5.5 s, and 1 again at 6.5 s.',
 ('021',3):'It returns to 0 at 7 s. At 8 s it is one step left of the origin (−1), and at 9 s it is two steps left (−2).',
 ('022',0):'Average velocity is the change in position divided by the elapsed time.',
 ('022',1):'From 0 to 1 s, position goes from 0 to 1. The average velocity is 1.',
 ('022',2):'From 1 to 2 s, position goes from 1 back to 0, so the average velocity is −1.',
 ('022',3):'Over the full 0–2 s interval, both displacement and average velocity are 0, even though the particle traveled a nonzero distance.',
 ('023',0):'From 5.5 to 6.5 s, position goes from −1 to +1. The change is +2 in one second, so the average velocity is 2.',
 ('023',2):'Between 0 and 9 s, the endpoints are 0 and −2. The average velocity is −2/9.',
 ('024',1):'The derivative of 2t − t² is 2 − 2t. The derivative of the constant 0 is 0.',
 ('024',2):'By the chain rule, the derivative of sin(πt) is π cos(πt).',
 ('024',3):'The derivative of 7 − t is −1.',
 ('024',4):'At 2, 4 and 7 s, the left and right slopes differ. The ordinary derivative is undefined at those joins.',
 ('025',0):'At 0.1 s, velocity is 2 − 0.2 = 1.8.',
 ('025',1):'At 1 s, velocity is 0. At 1.9 s, it is 2 − 3.8 = −1.8.',
 ('026',0):'At 4.1 s, evaluate π cos(4.1π).',
 ('026',1):'Cosine is periodic, so this equals π cos(0.1π), or about 2.988.',
 ('026',2):'At 5 s, cos(5π) = −1, so velocity is −π. At 6.5 s, the cosine is 0, so velocity is 0.',
 ('026',3):'At 8 and 9 s, velocity is −1 on the final straight segment.',
 ('027',1):'Differentiating 2 − 2t gives −2, and differentiating the constant 0 gives 0.',
 ('027',2):'Differentiating π cos(πt) gives −π² sin(πt). Cosine supplies the minus sign; the inner derivative supplies the extra π.',
 ('027',3):'The derivative of the constant −1 is 0.',
 ('028',0):'At 0.1, 1 and 1.9 s, velocity drops by two units each second. Acceleration is −2 throughout the first segment.',
 ('028',1):'At 4.1 s, acceleration is −π² sin(0.1π), or about −3.05.',
 ('028',2):'At 5 s, sine is 0 and acceleration is 0. At 6.5 s, sine is 1, so acceleration is −π².',
 ('028',3):'At 8 and 9 s, velocity is constant and acceleration is 0.',
 ('030',0):'The projectile starts at x = 0 ft, y = 10 ft. Its launch speed is 150 ft/s at 40° above horizontal.',
 ('030',1):'Take upward as positive and use 32 ft/s² for the magnitude of gravity.',
 ('030',2):'Horizontally, 150 cos(40°) ≈ 114.91 ft/s. Vertically, 150 sin(40°) ≈ 96.42 ft/s.',
 ('031',0):'Divide the initial vertical speed by gravity: about 96.42 ft/s divided by 32 ft/s² gives 3.013 s to the apex.',
 ('031',2):'Multiplying the horizontal speed by that time gives x ≈ 346.22 ft.',
 ('031',3):'For the apex height, add the rise to the initial 10 ft.',
 ('031',4):'The initial vertical speed squared, divided by 64, gives a rise of about 145.26 ft. Adding 10 ft puts the apex at about 155.26 ft.',
 ('032',0):'The target is the launch height of 10 ft, above ground level.',
 ('032',1):'The return time is twice the time to the apex: about 6.026 s.',
 ('032',2):'Multiply by horizontal speed to get a horizontal displacement of about 692.44 ft.',
 ('033',1):'Displacement is initial velocity times t plus half of acceleration times t². Dot both sides with acceleration to get a scalar equation.',
 ('033',3):'Set A = a·a, B = v₀·a and D = Δr·a, using acceleration, initial velocity and displacement. Then ½At² + Bt − D = 0.',
 ('034',0):'The quadratic formula gives t = (−B ± √(B² + 2AD)) / A.',
 ('035',0):'The imaginary unit i satisfies i² = −1.',
 ('035',1):'Use the natural base e ≈ 2.718. Substituting ix into the exponential series gives 1 + ix + (ix)²/2! + …',
 ('035',3):'The powers starting at i⁰ cycle through 1, i, −1 and −i.',
 ('036',0):'The real terms give 1 − x²/2! + x⁴/4! − …, the cosine series.',
 ('036',2):'The terms multiplying i give x − x³/3! + …, the sine series.',
 ('036',3):'So exp(ix) = cos(x) + i sin(x). This is Euler’s formula.',
 ('037',0):'Model a space station’s orbit as a circle. The exercise gives an altitude of 340 km and a speed of 27,740 km/h.',
 ('037',3):'The orbital radius starts at Earth’s center. Add the altitude to the assumed Earth radius of 6,371 km.',
 ('037',5):'That gives a radius of 6,711,000 m. The speed is about 7,705.56 m/s.',
 ('038',0):'Divide the circumference, 2πr, by speed. One orbit takes about 5,472 s, or 91.2 minutes.',
 ('038',1):'Speed squared divided by the radius gives a centripetal acceleration of about 8.85 m/s².',
}
adjust=read(file) if file.exists() else {}
existing={(a['scene'],a['koStart']):a for a in adjust.get('groups',[])}
for key,caption in replacements.items():
 old=existing.get(key);assert not old or old['caption']==caption
 existing[key]=dict(scene=key[0],koStart=key[1],source=groups[key],caption=caption,reason='Readable canonical mathematical notation with the same worked example and its conditions.')
printed={
 '영 점 영이오사 미터':'0.0254m','사 점 사사팔이 뉴턴':'4.4482N',
 '육천팔백구십사 점 칠오칠 파스칼':'6,894.757Pa',
 '영 점 영영영일사오영삼팔':'0.000145038',
 '영 점 일 초':'0.1초','일 점 구 초':'1.9초','사 점 일 초':'4.1초',
 '사 점 오 초':'4.5초','오 점 오 초':'5.5초','육 점 오 초':'6.5초',
 '칠 초에':'7초에','팔 초에':'8초에','구 초에':'9초에','구 초 전체':'9초 전체',
 '마이너스 삼 점 영오':'−3.05','마이너스 일 점 팔':'−1.8','이 점 구팔팔':'2.988',
 '삼 점 영일삼 초':'3.013초','육 점 영이육 초':'6.026초','삼백사십육 점 이이 피트':'346.22피트',
 '구십육 점 사이 피트':'96.42피트','백십사 점 구일 피트':'114.91피트',
 '백사십오 점 이육 피트':'145.26피트','백오십오 점 이육 피트':'155.26피트',
 '육백구십이 점 사사 피트':'692.44피트','이 점 칠일팔':'2.718',
 '마이너스 파이 제곱':'−π²','영 점 일 파이':'0.1π','사 점 일 파이':'4.1π',
}
scenes=read(P/'script/narration.ko.json')['scenes']
# Only register forms actually present in this approved script.
present={k:v for k,v in printed.items() if any(k in s['displayLines'][0] for s in scenes)}
adjust.update(groups=list(existing.values()),koPrintedForms=present,status='Worked-example EN meaning groups and KO printed values reviewed; final speech timing and encoded captions pending.')
file.write_text(json.dumps(adjust,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(replacements),'English meaning groups;',len(present),'printed Korean quantities. Narration unchanged.')
