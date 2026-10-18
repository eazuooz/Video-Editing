from pathlib import Path
import json,hashlib,ast
R=Path(__file__).resolve().parents[3];P=R/'projects/game-math-euler-axis-angle';sp=P/'script/revision-v2'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ko=read(sp/'narration.ko.json');en=read(sp/'narration.en.json');lesson=read(P/'production/revision-v2/lesson.json')
def scene(d,i):return next(s for s in d['scenes'] if s['id']==i)
def replace(d,i,j,before,after):
 old=scene(d,i)['lines'][j]
 if after in old:return
 assert before in old,(i,j,old)
 scene(d,i)['lines'][j]=old.replace(before,after)
replace(ko,'16',2,'항등 자세에서 이 두 숫자 묶음','아무것도 돌리지 않은 항등 자세에서 이 두 숫자 묶음')
replace(en,'16',2,'Interpolate from identity to each triple.','Interpolate from the unrotated identity orientation to each triple.')
replace(ko,'22',2,'그 길이는 파이를 루트 이로 나눈 값, 약 백이십칠 점 이팔 도입니다.','그 길이는 파이를 루트 이로 나눈 라디안 값입니다. 도로 바꾸면 약 백이십칠 점 이팔 도입니다.')
scene(en,'22')['lines'][2]='Its magnitude is pi divided by the square root of two radians, which is approximately127.28 degrees after conversion. Rotating the model shows a different final orientation from the sequential pair.'
replace(ko,'11',0,'윤곽선은 화면에서 보이는 몸의 자세를 따라갑니다.','원형 표시는 화면에서 보이는 몸의 자세를 짚어 줍니다.')
scene(en,'11')['lines'][0]='Watch the body tilt sharply and point upward or downward. The circular mark highlights the visible body orientation on the screen.'
replace(ko,'17',0,'처음과 마지막 표시 사이에도','움직이는 동안에도');replace(ko,'17',3,'시작과 끝 표시도 새로 잡습니다.','관찰 표시도 지우고 새로 잡습니다.')
scene(en,'17')['lines'][0]='Watch the body change direction while passing beside the structures. The visible torso and wingsuit keep changing orientation throughout the motion.'
scene(en,'17')['lines'][3]='At each source cut, clear the observation marks and start again. Do not join separate flights into one continuous trajectory.'
replace(ko,'20',0,'몸통 중심에 찍은 점','몸통 중심 부근을 가리키는 점');replace(ko,'20',5,'지나간 경로와 관찰 표시도','관찰 표시도')
scene(en,'20')['lines'][0]='Watch the dot near the middle of the visible body. Its movement between structures shows a change in screen position.'
scene(en,'20')['lines'][5]='Clear the observation marks at each source cut. Follow translation and orientation separately within each excerpt.'
replace(ko,'23',1,'중심점의 이동과 몸의 회전은','움직이는 위치와 몸의 회전은')
scene(en,'23')['lines'][1]='Complex movement can be considered as individual orientations and changes between them. Moving position and body rotation carry different information.'
scene(ko,'19')['lines'][0]='단위축 엔에 라디안 각도 세타를 곱한 벡터 이, 즉 세타 엔을 회전벡터라고 부릅니다. 여기서는 회전각을 영 이상으로 골랐습니다. 영이 아닐 때 방향은 축이고, 길이는 그 회전각입니다.'
scene(en,'19')['lines'][0]='Multiply unit axis n by radian angle theta to obtain e equals theta n: a rotation vector. Here we choose a nonnegative angle. For a nonzero vector, its direction is the axis and its length is that angle.'
for s in lesson['scenes']:s['ko']=scene(ko,s['id'])['lines'];s['en']=scene(en,s['id'])['lines']
scene(lesson,'22')['beats'][2]='||e_sum||=π/√2 rad≈2.22144 rad≈127.28°'
scene(lesson,'19')['beats'][0]='e=θn / θ≥0 / θ=||e||'
for f,d in [(sp/'narration.ko.json',ko),(sp/'narration.en.json',en),(P/'production/revision-v2/lesson.json',lesson)]:write(f,d)
audit=read(R/'shared/output/game-math-selection-audit/content-audit.json');audit['parentFollowup']={'scope':'Parent read fullnewKO; independent fullKOENreviewcaughtprerequisite, signedangle, units andmarkpromiseitems; corrected beforeTTS','newHashes':{f.as_posix().split('/VideoEditing/')[-1]:hashlib.sha256(f.read_bytes()).hexdigest() for f in [sp/'narration.ko.json',sp/'narration.en.json',P/'production/revision-v2/lesson.json']},'remaining':'New speech and realized pixels not yet checked'};write(P/'production/content-review-v2.json',audit)
plan=read(P/'planning/production-plan.json');plan.update(status='full-script-and-scene-design-review',terminology=audit['glossary'],contentReview='production/content-review-v2.json')
plan['audio']={'voice':'ApprovedQwen3-TTS1.7B/reference unchanged','sourcePcmRestoration':'Old rawPCM unavailable; StudioAAC isreviewonly. All26continuousscenes rewritten, so freshselectedvoicebatchneeded. Historicalfilespreserved.','music':'Nimbus — Eveningland','musicInitialLufs':-31,'musicLicense':'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md','sourceAudio':'excluded; soundtrackrightsnotcleared','humanListening':'pending'}
for s in plan['scenes']:
 steps=audit['learningSteps'];s['learningSteps']=[x for x in steps if isinstance(x,dict) and x.get('scene')==s['id']] if isinstance(steps,list) else steps.get(s['id'],steps)
 s['currentScript']=f'script/revision-v2/narration.ko.json#{s["id"]}'
 s['transitionToNext']=next((x for x in audit['chapterJoins'] if x.get('from')==s['id'] or x.get('fromScene')==s['id']),{'review':'WholeadjacentKOENpairsread; exactpairsincontent-review-v2.json'})
write(P/'planning/production-plan.json',plan)
outline=['# 같은 각도인데 왜 다르게 돌까? — 오일러 각과 축·각','기존26장면·핵심내용순서유지. 실제Superflight40% / 설명60%,1920×1080/60fps. 완성본은Drive사용자검수후YouTube업로드.']
for s in ko['scenes']:outline+=['## '+s['id']+' · '+s['title']]+s['lines']
(P/'planning/outline.md').write_text('\n\n'.join(outline)+'\n',encoding='utf8')
for name in ['render-voice-v2.py','review-voice-v2.py','align-voice-v2.py']:ast.parse((P/'production'/name).read_text(encoding='utf8'))
assert all(len(scene(ko,s['id'])['lines'])==len(scene(en,s['id'])['lines']) for s in ko['scenes'])
assert all(s['ko']==scene(ko,s['id'])['lines'] and s['en']==scene(en,s['id'])['lines'] for s in lesson['scenes'])
assert not any(term in ' '.join(v for s in ko['scenes'] for v in s['lines']) for term in ['원문','사쿠라이','책에서는'])
print('157KOENpairs; identity/signedangle/radians/markpromisesfixed; wholeKOENcorrespondenceverified.')
