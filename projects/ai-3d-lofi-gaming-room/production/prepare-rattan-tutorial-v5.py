"""Apply the user's wood/rattan furniture and sleeping-motion revision once."""
from pathlib import Path
import json,shutil
H=Path(__file__).resolve().parent;P=H.parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
names=['prepare-film-assets.py','build-film-audio.py','build-film-captions.py','complete-film.py','render-film.py','render-howto-storyboards.cjs','verify-film.py','make-thumbnail.cjs','prepare-wiki-frames.py','prepare-companion-v8.py','finalize-film-records.py','serve-review.py','build-request-reference.py','compose-howto-article.py','render-tutorial-v3-voice.py','verify-tutorial-v3-after-render.py','build-tutorial-edit-records.py']
backup=H/'local/full-video-v4/scripts-before-rattan-v5';backup.mkdir(exist_ok=True)
for name in names:
 f=H/name
 if not (backup/name).exists():shutil.copy2(f,backup/name)
 f.write_text(f.read_text('utf-8').replace('full-video-v4','full-video-v5').replace('living-room-v10','living-room-v11').replace('tutorial-v4.json','tutorial-v5.json').replace('compositor-v4','compositor-v5').replace('tutorial-v4-voice-reuse','tutorial-v5-voice-reuse'),'utf-8')
changed={
'11':('목재·라탄 소파와 테이블 만들기','소파와 테이블도 각각의 입력 이미지로 준비합니다. 밝은 목재 프레임과 라탄 짜임을 요청하고, 소품이 없는 단독 이미지로 트리포에서 생성합니다. 면 수를 줄이고 텍스처와 함께 유니티로 넘긴 뒤 코덱스에 배치를 요청합니다. 소파는 등을 기댈 자리, 낮은 테이블은 발을 올릴 자리입니다. 캐릭터 크기에 맞춰 높이와 간격을 조절하고, 옆으로 걸어갈 통로를 남깁니다.','Prepare the sofa and table as separate input images. Request pale wood frames and woven rattan, generate each isolated object in Tripo, retopologize and export it with textures for Unity. Ask Codex to arrange the sofa for leaning back and the low table for resting the feet. Fit their heights and spacing to the character and preserve a side approach path.'),
'18':('소파에 기대고 테이블에 발 올리기','독서는 소파에 앉고 등을 기댄 뒤 책을 펼치는 순서로 요청합니다. 기존 휴식 동작으로 몸과 다리를 두고, 독서 동작의 팔만 아바타 마스크로 섞습니다. 발은 낮은 테이블 상판에 닿도록 골반과 발목 목표를 함께 맞춥니다. 그다음 책장은 얼굴을 향하게 하고 양손은 표지 바깥에서 받칩니다. 아이케이, 역운동학은 손이나 발의 목표에서 팔다리 자세를 구하는 방법입니다. 앞과 옆에서 몸과 가구, 팔과 책 사이의 간격을 확인합니다.','For reading, request sitting on the sofa, leaning back and then opening the book. Keep the native reclining body and leg motion, and blend only the reading arms with an Avatar Mask. Fit the pelvis and ankle targets so the feet rest on the low tabletop. Aim the pages at the face and support the outer cover with both hands. Inverse kinematics solves limb poses from hand or foot targets. Inspect body/furniture and arm/book clearance from the front and side.'),
'30':('잠든 삼색고양이와 작은 수면 동작','고양이는 실제로 몸을 말고 잠든 삼색고양이 사진을 기준으로 만듭니다. 자유롭게 쓸 수 있는 사진의 배경을 이미지 에이아이로 정리하고 트리포에 넣습니다. 에이치 삼 점 일로 생성한 뒤 게임용으로 면 수를 줄이고 사케이 텍스처와 함께 가져옵니다. 움직임은 원래 모델에서 몸통과 꼬리 영역을 나눠 더합니다. 얼굴과 앞발은 안정적으로 두고, 몸통은 천천히 숨 쉬고 꼬리 끝은 작게 움직이게 합니다. 눈앞에서 털 무늬나 몸의 형태가 무너지지 않는지 확인합니다.','Start with a freely usable photograph of a real sleeping calico curled into a natural pose. Clean its background with image AI, generate with Tripo H3.1, retopologize for the game and import it with 4K textures. Add motion to localized chest and tail regions of the original mesh. Keep the face and forepaws stable, let the chest breathe slowly and move the tail tip gently. Inspect the coat and silhouette up close for unwanted deformation.')}
t=read(P/'script/tutorial-v4.json');old=read(H/'local/full-video-v4/narration.ko.json');oldBy={s['id']:s for s in old['scenes']}
for s in t['scenes']:
 if s['id'] in changed:s['title'],s['ko'],s['en']=changed[s['id']]
 if s['id']=='11':s.update(tool='이미지 AI → Tripo → Codex + Unity',screen='밝은 목재 · 라탄 / 소파와 테이블 분리 / 몸에 맞는 치수')
 if s['id']=='18':s['screen']='휴식 몸 + 독서 팔 / 테이블 발 접촉 / 책·손 IK'
 if s['id']=='30':s['screen']='실제 Tripo 모델 / 몸통 호흡 / 작은 꼬리 움직임'
save(P/'script/tutorial-v5.json',t)
titles={'11':'Create the wood and woven sofa and table','18':'Lean back with feet resting on the table','30':'A sleeping calico with localized breathing and tail motion'}
for lang in ('ko','en'):
 n=read(P/f'script/narration.{lang}.json')
 for s in n['scenes']:
  if s['id'] in changed:s['title']=changed[s['id']][0] if lang=='ko' else titles[s['id']];s['lines']=[changed[s['id']][1 if lang=='ko' else 2]]
 save(P/f'script/narration.{lang}.json',n);save(H/f'local/full-video-v5/narration.{lang}.json',n)
n=read(P/'script/narration.ko.json');(P/'script/full-narration.ko.txt').write_text('\n\n'.join('\n'.join(s['lines']) for s in n['scenes'])+'\n','utf-8')
chunks=H/'local/full-video-v5/narration/chunks';chunks.mkdir(parents=True,exist_ok=True);reused=[]
for s in n['scenes']:
 f=H/'local/full-video-v4/narration/chunks'/(s['id']+'-scene.wav')
 if s['lines']==oldBy[s['id']]['lines'] and f.exists():shutil.copy2(f,chunks/f.name);reused.append(s['id'])
save(H/'tutorial-v5-voice-reuse.json',{'reusedExactTextScenePcm':reused,'newScenePcmRequired':sorted(changed),'oldPcmPreserved':True,'basis':'Exact paragraph match against the completed v4 voice snapshot; only wood/rattan furniture, table contact and cat motion narration changes.'})
j=read(P/'project.json');j['tts']['outputDir']='projects/ai-3d-lofi-gaming-room/production/local/full-video-v5/narration';j['status']='rattan-cat-motion-v11-and-tutorial-v5-in-progress';save(P/'project.json',j)
f=H/'finalize-film-records.py';s=f.read_text('utf-8').replace('full-video-v3/narration/chunks','full-video-v4/narration/chunks').replace('LofiSofaRoomV10','LofiRattanRoomV11').replace('web-v10','web-v11').replace('12 frames','12 frames');f.write_text(s,'utf-8')
f=H/'render-film.py';s=f.read_text('utf-8').replace("('living-room-v11', 68, 6)","('living-room-v11', 84, 6)").replace("('living-room-v11', 61, 7)","('living-room-v11', 77, 7)").replace("('living-room-v11', 53, 8)","('living-room-v11', 69, 8)").replace("('living-room-v11', 45, 8)","('living-room-v11', 45, 24)");f.write_text(s,'utf-8')
f=H/'prepare-film-assets.py';s=f.read_text('utf-8').replace("'living-room-v11',57","'living-room-v11',73").replace("'living-room-v11',70","'living-room-v11',86").replace("'living-room-v11',65","'living-room-v11',80").replace("'living-room-v11',49","'living-room-v11',55");f.write_text(s,'utf-8')
print('Prepared v5; reused',len(reused),'scene PCM files, new',len(changed))
