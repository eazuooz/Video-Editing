"""Reconcile the selected sofa/Tripo-cat tutorial; reuse unchanged voice PCM only."""
from pathlib import Path
import json, shutil
H=Path(__file__).resolve().parent;P=H.parent;R=P.parents[1]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
names=['prepare-film-assets.py','build-film-audio.py','build-film-captions.py','complete-film.py','render-film.py','render-howto-storyboards.cjs','verify-film.py','make-thumbnail.cjs','prepare-wiki-frames.py','prepare-companion-v8.py','finalize-film-records.py','serve-review.py','build-request-reference.py','compose-howto-article.py','render-tutorial-v3-voice.py','verify-tutorial-v3-after-render.py']
backup=H/'local/full-video-v3/scripts-before-sofa-v4';backup.mkdir(exist_ok=True)
for name in names:
    f=H/name
    if not (backup/name).exists():shutil.copy2(f,backup/name)
    f.write_text(f.read_text('utf-8').replace('full-video-v3','full-video-v4').replace('living-room-v9','living-room-v10').replace('tutorial-v3.json','tutorial-v4.json').replace('compositor-v3','compositor-v4').replace('v9-26-to45','v10-26-to45'),'utf-8')
changed={
'03':('이미지 AI에 방의 기준 요청하기','먼저 이미지 생성에 방의 용도와 배치 조건을 함께 요청합니다. 따뜻한 목재 방, 청록색 옷의 캐릭터, 창밖의 숲과 달, 아이맥 한 대와 편안한 독서 자리를 적습니다. 여기에 가구 사이로 걸어갈 공간을 남기고, 고정된 대각선 카메라에서 방 전체가 보이게 해 달라고 덧붙입니다. 이렇게 얻은 그림은 색과 배치의 기준으로 저장하고, 다음에는 움직일 대상을 따로 만듭니다.','Ask the image model for the room’s purpose and layout: warm wood, a teal-clothed character, forest and moon outside, one all-in-one computer and a comfortable reading area. Specify walking clearance and a fixed three-quarter camera. Save the image as a palette and layout reference, then separate the moving assets.'),
'11':('Codex에 방과 가구 배치 요청하기','이제 유니티 프로젝트를 열고 코덱스에 방을 구성해 달라고 요청합니다. 고정 카메라와 미터 단위, 분리된 책상과 의자, 독서용 소파, 양쪽 책장과 벽난로를 조건으로 줍니다. 이 소파는 기존 라이브러리의 무료 에셋을 사용했습니다. 캐릭터 키에 맞춰 좌판과 등 쿠션, 발받침을 배치하고, 가구 사이 통로도 남깁니다. 필요한 모델이 이미 있다면 새로 생성하기보다 이렇게 가져와 조합해도 됩니다.','Ask Codex to compose the Unity room with a fixed camera, meter-scale units, separate desk and chair, a reading sofa, shelves and fireplace. This sofa is a free asset from the existing library. Fit the seat, back cushion and footrest to the character and preserve walking clearance. Reuse a suitable existing asset instead of generating every model.'),
'13':('Tripo 리깅과 기존 동작 연결하기','캐릭터를 움직이려면 리깅, 즉 뼈대와 표면을 연결하는 단계가 필요합니다. 트리포에서 걷기와 대기를 준비하고, 유니티 임포트의 리그를 휴머노이드로 맞춥니다. 추가 동작은 같은 인체 뼈대에 기존 클립을 대응시킵니다. 이 방은 케이킷의 앉기와 일어나기, 에맥스 아트 캐릭터 팩의 기대는 자세와 독서 동작을 조합했습니다. 모델과 동작을 분리해 두면 같은 캐릭터의 행동을 이렇게 늘릴 수 있습니다.','Rigging connects a skeleton to the surface. Prepare walking and idle in Tripo and configure the Unity rig as Humanoid. Retarget additional existing clips to the same human skeleton. This room combines KayKit sitting and standing with reclining and reading clips from EmacEArt’s character pack. Separating the model from motion makes it easier to expand its actions.'),
'18':('소파 독서는 몸을 받친 뒤 책 맞추기','독서는 소파에 앉고 쿠션에 등을 기댄 뒤 책을 펼치는 순서로 요청합니다. 기존 휴식 동작으로 몸과 다리를 두고, 독서 동작의 팔만 아바타 마스크로 섞습니다. 발받침은 발 아래에 맞춥니다. 그다음 책장을 얼굴 쪽으로 향하게 하고 양손은 표지 바깥에서 받칩니다. 아이케이, 역운동학은 손의 목표에서 팔 자세를 구하는 방법입니다. 손목 방향과 팔꿈치도 함께 맞추고, 앞과 옆에서 팔과 책이 겹치지 않는지 확인합니다.','For reading, request sitting on the sofa, settling against the cushion and then opening the book. Keep a native reclining body clip and blend the arms from a reading clip using an Avatar Mask. Fit the footrest beneath the feet. Aim the pages at the face and support the outer cover with both hands. Inverse kinematics solves arm poses from hand targets; also fit wrist orientation and elbow hints, then inspect clearance from the front and side.'),
'30':('잠든 삼색고양이는 사진에서 모델로','고양이는 실제로 몸을 둥글게 말고 잠든 삼색고양이 사진을 기준으로 만듭니다. 자유롭게 쓸 수 있는 사진을 고르고, 이미지 에이아이로 배경을 정리한 입력을 트리포에 넣습니다. 에이치 삼 점 일로 생성한 뒤 삼각형 면 목표 이만 개로 정리하고 사케이 텍스처와 함께 내보냈습니다. 유니티에서는 얼굴과 꼬리, 털 무늬를 돌려 보고 작은 호흡만 더합니다. 이 고양이의 생성과 메시 정리에는 구십 크레딧이 들었습니다.','Start with a real photo of a sleeping calico curled into a natural pose. Choose a freely usable photograph, clean its background with image AI and upload that derived image to Tripo. Generate with H3.1, retopologize to a target of twenty thousand triangles and export with 4K textures. In Unity, inspect the face, tail and coat, then add only subtle breathing. This cat used ninety credits for generation and retopology.')}
t=read(P/'script/tutorial-v3.json');old=read(H/'local/full-video-v3/narration.ko.json');oldBy={s['id']:s for s in old['scenes']}
for s in t['scenes']:
    if s['id'] in changed:s['title'],s['ko'],s['en']=changed[s['id']]
    if s['id']=='13':s['screen']='Walk / Idle + Sit / Recline / Read clips'
    if s['id']=='18':s['screen']='휴식 몸 + 독서 팔 / 쿠션·발받침 / 책·손 IK'
    if s['id']=='30':s.update(tool='사진 → 이미지 AI → Tripo H3.1',screen='CC0 사진 / Triangle 20K / 4K / 작은 호흡')
save(P/'script/tutorial-v4.json',t)
englishTitles={'03':'Request the room’s visual reference','11':'Ask Codex to arrange the room and sofa','13':'Connect Tripo rigging and existing motion','18':'Support the reading pose and fit the book','30':'From a sleeping calico photograph to a model'}
for lang in ('ko','en'):
    n=read(P/f'script/narration.{lang}.json')
    for s in n['scenes']:
        if s['id'] in changed:
            c=changed[s['id']];s['title']=c[0] if lang=='ko' else englishTitles[s['id']];s['lines']=[c[1] if lang=='ko' else c[2]]
    save(P/f'script/narration.{lang}.json',n);save(H/f'local/full-video-v4/narration.{lang}.json',n)
n=read(P/'script/narration.ko.json');(P/'script/full-narration.ko.txt').write_text('\n\n'.join('\n'.join(s['lines']) for s in n['scenes'])+'\n','utf-8')
reused=[];chunks=H/'local/full-video-v4/narration/chunks';chunks.mkdir(parents=True,exist_ok=True)
for s in n['scenes']:
    f=H/'local/full-video-v3/narration/chunks'/(s['id']+'-scene.wav')
    if s['lines']==oldBy[s['id']]['lines'] and f.exists():shutil.copy2(f,chunks/f.name);reused.append(s['id'])
j=read(P/'project.json');j['tts']['outputDir']='projects/ai-3d-lofi-gaming-room/production/local/full-video-v4/narration';j['status']='sofa-tripo-cat-v10-and-tutorial-v4-in-progress';save(P/'project.json',j)
r=read(P/'planning/reproduction-recipes.json')
for item in r['recipes']:
    for k,v in list(item.items()):
        if isinstance(v,str):item[k]=v.replace('가운데 빈백','편안한 독서 자리').replace('중앙 카펫의 빈백','중앙 카펫의 소파와 등 쿠션·발받침').replace('빈백 접근·눕기','소파 접근·착석·기대기')
    if item['id']=='actions':item['input']='확보한 Walk, Idle, SitDown, StandUp, Tourist_sit_03 휴식과 Tourist_sit_02_Map 독서 클립'
    if item['id']=='book-contact':
        item['input']='기존 기대는 휴식 클립, 독서 팔 클립, 책 Transform과 손목·손가락 기준'
        item['request']='기존 휴식 클립으로 몸과 다리 자세를 유지하고 독서 클립의 팔만 Avatar Mask로 섞어줘. 소파 좌판·등 쿠션·발받침에 몸을 맞추고 자리 잡은 뒤 책을 펼쳐줘. 책 면은 얼굴을 향하게 하고 양손은 표지 바깥에서 받치게 해줘. 손목 방향과 Avatar IK goal 축 차이를 반영하고 팔꿈치는 몸 밖으로 유도해줘. 접근·착석·독서·책 정리·기립 전환과 앞·옆 시점을 확인해줘.'
    if item['id']=='cat':item.update(tool='CC0 사진 + 이미지 생성 + Tripo + Unity',input='CC0 Calico Cat Asleep 사진과 배경 정리한 파생 이미지',request='권리가 확인된 잠든 삼색고양이 사진에서 자연스러운 웅크린 자세와 얼굴·꼬리·털 무늬를 유지해 배경 없는 입력을 만들어줘. Tripo Image to 3D H3.1로 생성한 뒤 Smart Mesh P1.0, Triangle 목표 20K로 정리하고 4K 텍스처를 FBX와 함께 내보내줘. Unity에서 실제 고양이 크기로 맞추고 비금속·무광 재질과 작은 호흡을 더해줘. 코드를 조합한 구형 몸체로 대체하지 말고 내려받은 모델을 사용해줘.',output='사진 기준의 Tripo 수면 삼색고양이 모델',check='얼굴·감긴 눈·접힌 앞발·연결된 꼬리, 19,398 triangles, 실제 4K 텍스처, CC0 사진 표시')
save(P/'planning/reproduction-recipes.json',r)
f=H/'render-howto-storyboards.cjs';s=f.read_text('utf-8').replace('책상 · 의자 · 빈백 분리','책상 · 의자 · 독서 소파').replace('기존 KayKit Sit / Lie clips','KayKit Sit + EmacEArt 휴식').replace('기존 Lie Down / Idle / Up','휴식 몸 + 독서 팔 Avatar Mask').replace('아이맥 한 대 · 가운데 빈백','아이맥 한 대 · 편안한 독서 자리').replace("30:['흰 바탕 · 적은 삼색 무늬','무광 표면 · 연속된 꼬리','작은 호흡 · 가끔 귀 반응']","30:['CC0 사진 → 배경 정리 이미지','Tripo H3.1 → Triangle 20K','4K 텍스처 · 실제 모델 · 작은 호흡']")
s=s.replace("if(id===6||id===13)","if(id===30){pic('tripo-cat',76,216,1120,630);steps(id);return;}\n if(id===6||id===13)")
f.write_text(s,'utf-8')
f=H/'render-film.py';s=f.read_text('utf-8').replace("n in (2,6,13)","n in (2,6,13,30)");f.write_text(s,'utf-8')
save(H/'tutorial-v4-voice-reuse.json',{'reusedExactTextScenePcm':reused,'newScenePcmRequired':sorted(changed),'oldPcmPreserved':True,'basis':'Exact Korean paragraph equality against completed v3 snapshot; titles do not affect spoken audio.'})
print('Prepared tutorial v4; reusable voices',len(reused),'new',len(changed))
