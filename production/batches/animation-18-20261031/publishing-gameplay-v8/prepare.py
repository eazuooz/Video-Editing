from pathlib import Path
import json,re,hashlib,datetime,difflib
from PIL import Image

ROOT=Path('D:/Github/VideoEditing')
B=ROOT/'production/batches/animation-18-20261031'
PUB=Path(__file__).parent
OUT=Path('C:/Users/1/Videos/YamyamCoding/animation-gameplay-v8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(16*1024*1024),b''):h.update(block)
 return h.hexdigest()
def norm(s):return re.sub('[^가-힣a-zA-Z0-9]','',s).lower()
def stamp(t):return f'{int(t)//60:02}:{int(t)%60:02}'
INFO={
 'A03':('Attack Phases | Why One Swing Needs Three Stages','몬스터 헌터 와일즈의 대검을 준비·타격·후속 동작으로 나눠 봅니다. 공격 판정, 히트 스톱, 다음 입력이 가능한 시점까지 한 흐름으로 연결합니다.','Break down a Monster Hunter Wilds great-sword swing into anticipation, impact and follow-through. Connect the poses to active hit detection, hit stop and the next actionable moment.'),
 'A04':('Fast, Impactful Anticipation | Make Attacks Feel Responsive','하데스 II의 도끼, 컵헤드의 사격, 제로 슈트 사무스의 잽으로 준비 동작의 역할을 비교합니다. 짧은 준비에서도 힘과 입력 반응을 함께 전달하는 방법을 살펴봅니다.','Compare anticipation in Hades II, Cuphead and Zero Suit Samus attacks. See how the first readable change, a held pose and timing can preserve both impact and responsiveness.'),
 'A05':('Attack Poses | Why Some Attacks Look More Powerful','하이파이 러시와 프린세스 피치 쇼타임의 공격을 멈춰 보며 자세의 힘을 살펴봅니다. 공격 방향, 몸의 비대칭, 실루엣과 카메라가 타격감을 어떻게 바꾸는지 비교합니다.','Study attack poses in Hi-Fi RUSH and Princess Peach: Showtime! Compare direction, asymmetry, silhouette, camera angle and the pose selected for hit stop.'),
 'A06':('Follow-Through | The Motion After Impact Creates Weight','몬스터 헌터 월드의 해머, 스트리트 파이터 6, 마리오 테니스 에이스를 통해 후속 동작의 역할을 살펴봅니다. 판정 종료·조작 재개·애니메이션 종료가 서로 다른 이유도 설명합니다.','Explore follow-through with Monster Hunter: World, Street Fighter 6 and Mario Tennis Aces. Distinguish the end of hit detection, the next actionable moment and the end of the animation.'),
 'A07':('Exaggeration and Information Loss | Why Motions Fade on Screen','캐릭터를 작게 보여주면 표정과 몸짓의 정보도 줄어듭니다. 루이지 맨션 3 등 실제 게임 장면을 확대·축소해 보며, 과장이 필요한 이유와 모션 캡처 이후의 작업을 살펴봅니다.','A smaller character loses readable facial and body detail. Compare game footage at different viewing sizes and see why motion capture still needs deliberate animation choices.'),
 'A08':('Posing Suggestions | Fixing an Awkward Character Pose','링 피트 어드벤처의 자세와 33원정대의 마엘을 보며 몸의 흐름, 팔 사이 공간, 디딤발을 읽어 봅니다. 작은 부분을 고친 뒤 전체 포즈를 다시 확인하는 순서를 설명합니다.','Read the body line, negative space and supporting foot in Ring Fit Adventure and Maelle from Clair Obscur: Expedition 33. Build a clear pose by checking the whole body after each adjustment.'),
 'A09':('Squash and Scale | How Shape Changes Bring Motion to Life','컵헤드의 구피 르 그란데 등 게임 장면과 원리 도식으로 압축과 늘이기를 비교합니다. 부피감, 변형 방향, 버텍스와 모프 타깃, 주먹 크기 과장의 차이까지 연결합니다.','Use Cuphead and principle diagrams to compare squash, stretch and scale. Explore volume, shape direction, vertex deformation, morph targets and the different purpose of enlarging a fist.'),
 'A10':('Damage Animations | Making a Hit Look Like a Hit','스트리트 파이터 6와 슈퍼 마리오 오디세이에서 피격 순간을 관찰합니다. 맞은 위치와 충격의 크기, 몸의 모양과 캐릭터 이동을 구분해 설득력 있는 반응을 만드는 방법입니다.','Observe damage reactions in Street Fighter 6 and Super Mario Odyssey. Separate body deformation from character translation and connect the reaction to the contact point and impact strength.'),
 'A11':('The Perils of Interpolation | Smooth Motion Can Lose Impact','철권 8 리리의 회전 발차기를 같은 길이로 비교합니다. 주요 자세가 같아도 중간 움직임에 시간을 어떻게 배분하느냐에 따라 속도감과 힘이 달라지는 이유를 살펴봅니다.','Compare Lili spinning kicks from TEKKEN 8 at matched durations. See how time distribution between key poses changes perceived speed and impact even when the endpoints stay the same.'),
 'A12':('Facial Animation | Expressions Are More Than a Moving Mouth','동물의 숲과 33원정대의 얼굴을 확대해 눈썹·눈·입의 관계를 살펴봅니다. 표정의 목표를 먼저 정하고 작은 화면에서도 감정이 읽히는지 확인하는 방법을 설명합니다.','Study eyebrows, eyes and mouth in Animal Crossing: New Horizons and Clair Obscur: Expedition 33. Set a clear expression goal and check whether the emotion remains readable at gameplay size.'),
 'A13':('Flipped Animation | Keeping Poses Readable in Both Directions','스트리트 파이터의 양쪽 방향 장면을 비교합니다. 스프라이트 반전과 3D 자세 조정의 차이, 손잡이와 무늬, 플레이 화면에서 얼굴이 잘 보이도록 만드는 설계를 살펴봅니다.','Compare actual opposite-facing scenes from Street Fighter. Explore sprite flipping, 3D pose adjustments, handedness, costume details and readability from the gameplay camera.'),
 'A14':('Animation Blending | Joining Two Different Motions Naturally','호라이즌 제로 던과 스플래툰 3 등의 움직임을 보며 애니메이션 블렌딩을 설명합니다. 이전 자세, 혼합 시간과 비중, 이동 방향과 상·하체 조합을 차례로 연결합니다.','Explore animation blending through Horizon Zero Dawn, Splatoon 3 and other game footage. Connect the previous pose, blend duration, blend weight, movement direction and upper/lower-body combinations.'),
 'A15':('Portraying Fingers | Why a Small Hand Needs So Much Work','하프라이프 알릭스의 물건 잡기와 고스트와이어 도쿄의 손동작을 관찰합니다. 손가락 관절, 잡는 각도, 준비된 포즈와 실시간 제어가 만드는 표현과 계산 비용을 비교합니다.','Observe object gripping in Half-Life: Alyx and hand gestures in Ghostwire: Tokyo. Compare finger joints, grip angles, prepared poses and real-time control, including their animation cost.'),
 'A16':('Attack Collision and Animation | Why a Visible Hit Can Miss','몬스터 헌터 월드의 창과 검, 엘든 링과 메트로이드 드레드의 장면으로 공격 경로와 판정을 살펴봅니다. 화면에서 겹친 모습과 실제 공간, 판정의 활성 시간을 함께 확인합니다.','Explore weapon paths and hit detection with Monster Hunter: World, Elden Ring and Metroid Dread. Connect screen-space overlap, the actual spatial path and active timing. Diagrams illustrate principles rather than extracted internal game hitboxes.'),
 'A17':('The Limits of Skeletons | When Joints Cannot Make the Pose','ARMS의 리본 걸과 컵헤드를 통해 뼈대만으로 표현하기 어려운 변형을 살펴봅니다. FK·IK와 제어점의 관계를 이해하고, 도구의 기본값보다 표현의 목표를 먼저 정합니다.','Use Ribbon Girl from ARMS and Cuphead to explore deformation beyond a conventional skeleton. Connect FK, IK and control points, then choose a rig around the expressive goal.'),
 'A18':('Rotation on Two Axes | Making a Turn Feel Alive','거위 게임과 루이지 맨션 3 등에서 고개와 몸의 회전을 관찰합니다. 같은 끝 자세라도 축별 경로와 시작 시점, 눈의 방향에 따라 움직임의 성격이 달라집니다.','Observe head and body turns in Untitled Goose Game, Luigi’s Mansion 3 and The Last Guardian. Compare axis paths, start times and eye direction while keeping the same final orientation.')
}
OVERRIDES={
 'A04':[(83.277,'한 자세로 힘 모으기','Holding an anticipation pose'),(110.327,'보간과 반응 속도','Interpolation and responsiveness'),(136.467,'짧은 공격과 반복 사격','Quick attacks and repeated fire'),(201.807,'긴 준비 동작의 역할','When longer anticipation helps')],
 'A05':[(98.793,'플레이 크기에서 읽히는 자세','Readability at gameplay size'),(121.083,'공격 방향과 경로','Attack direction and path'),(142.143,'몸의 양쪽에 다른 역할 주기','Asymmetry and support'),(193.939,'카메라와 실루엣','Camera and silhouette')]
}
EN_CHAPTERS={
 'A03':['Readable anticipation','The impact pose','Follow-through','When control returns','Shared production criteria'],
 'A06':['Responsiveness and recovery','Different attack timelines','Three different endings','The motion after impact','A pose ready for the next action','The complete attack'],
 'A07':['Information lost on screen','Beyond motion capture','Checking from a distant camera','Exaggeration and play rhythm','Preserving meaning'],
 'A08':['Comparing poses','The body line','Clothing and shoulders','Readable arms and hands','The supporting leg','Checking the complete pose','Practising observation'],
 'A09':['Two bouncing balls','Preserving volume','Different silhouettes','Deforming the surface','Enlarging a fist','Shape, material and force'],
 'A10':['Connecting strong pose changes','Body shape and character position','Contact point and impact strength','Different bodies','Readable limbs','A strong brief reaction'],
 'A11':['Time distribution in eight frames','Preserving key poses','Connecting three poses','Anticipation and extension','The return path','Interpolation and game rhythm'],
 'A12':['Set an expression goal','Eyes and teeth','Choosing how much to animate'],
 'A13':['Sprite flipping and 3D poses','Facing the gameplay camera','Asymmetric details and lettering'],
 'A14':['The previous pose matters','How long should a blend last?','Blending directions','Body and terrain combinations','Good clips and good transitions'],
 'A15':['Many joints in a small hand','Why hands cannot rank hardware','The cost across the whole screen'],
 'A16':['Screen overlap and spatial paths','When hit detection is active','Designing animation and collision together'],
 'A17':['Beyond a straight arm','The cost of more controls','Expression before tool defaults'],
 'A18':['Different routes to the same direction','Wrist and shoulder rotation','Timing the axes','Different character in the same final pose','Aim the eyes as well as the head']}
credits={x['id']:x for x in load(B/'contrast-v5/footage/source-summary.json')['records']}
footer=(ROOT/'shared/publishing/youtube-channel-description.ko.txt').read_text(encoding='utf-8').split('📚 수업 노트')[0].rstrip('━\n ')
footer_en='YamyamCoding | Game Programming\nDirectX, Unity, Unreal Engine and Computer Graphics.\n\n1:1 programming coaching\nhttps://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328\nDiscord\nhttps://discord.gg/wZuqe7fqkR\nMembership\nhttps://www.youtube.com/channel/UCOgtkPoyC0VXhCs7Xk3jvjQ/join'
approved=[];manifest=[]
for i in range(3,19):
 ep=f'A{i:02}';d=load(OUT/ep/'delivery.json');files={x['kind']:x for x in d['files']};master=Path(files['captioned.mp4']['path']);digest=sha(master)
 assert digest==files['captioned.mp4']['sha256'],ep
 for k in ['ko.srt','en.srt']:assert sha(Path(files[k]['path']))==files[k]['sha256'],(ep,k)
 thumbnail=PUB/'local/thumbnails'/f'{ep}.jpg';assert thumbnail.stat().st_size<2_000_000
 cues=[]
 for block in re.split(r'\n\s*\n',Path(files['ko.srt']['path']).read_text(encoding='utf-8-sig').strip()):
  lines=block.splitlines();v=lines[1].split(' --> ')[0];h,m,s=v.replace(',','.').split(':');cues.append((int(h)*3600+int(m)*60+float(s),' '.join(lines[2:])))
 chapters=[(0,'오늘의 질문','The question'),(d['overviewAt'],'핵심 원리와 관찰 순서','Principle and observation roadmap')]
 if ep in OVERRIDES:chapters+=OVERRIDES[ep]
 else:
  scenes=load(B/'scripts'/ep/'narration.ko.json')['scenes'][1:]
  for n,sc in enumerate(scenes):
   target=norm(sc['lines'][0])[:55];score,j=max((difflib.SequenceMatcher(None,target,norm(''.join(c[1] for c in cues[j:j+4]))[:len(target)]).ratio(),j) for j in range(len(cues)))
   if score>=.5:chapters.append((cues[j][0],sc['title'],EN_CHAPTERS[ep][n]))
 chapters.append((d['summaryAt'],'오늘의 핵심 정리','Key takeaways'))
 chapters=sorted(chapters);chapters=[c for n,c in enumerate(chapters) if n==0 or c[0]-chapters[n-1][0]>=10]
 if ep=='A03':
  ck='영상·게임 자료 출처\nMonster Hunter Wilds — tateyou · Monster Hunter Wilds - How Great Sword Actually Works in Real Combat\nhttps://www.youtube.com/watch?v=H69UChNQW0U\nSuper Smash Bros. Ultimate — Prodigy Gamer · Link vs Ganondorf – Can Link Survive This?!\nhttps://www.youtube.com/watch?v=VnFpz7ZwNq8\n녹화자가 표시한 CC BY에 따라 발췌·확대·속도 조절·해설과 표식을 추가했습니다. 게임 자체의 권리는 각 권리자에게 있습니다.\nhttps://creativecommons.org/licenses/by/4.0/'
  ce=ck.replace('영상·게임 자료 출처','Gameplay and source credits').replace('녹화자가 표시한 CC BY에 따라 발췌·확대·속도 조절·해설과 표식을 추가했습니다. 게임 자체의 권리는 각 권리자에게 있습니다.','Recordings marked CC BY; excerpted, cropped, retimed and annotated with original commentary. Game rights remain with their owners.')
 else:
  ck=credits[ep]['descriptionSourceCreditsBottomKo'];ce=credits[ep]['descriptionSourceCreditsBottomEn']
  ck=ck.replace('기존 출처 기록 및 사용 조건 확인 대상','게임 및 녹화 권리는 각 권리자에게 있습니다.')
  ce=ce.replace('Existing source record; unresolved use conditions require review.','Game and recording rights remain with their respective owners.')
 extra=(OUT/ep/'additional-sources.txt').read_text(encoding='utf-8').splitlines();extra='\n'.join(extra[3:]).strip()
 if extra:ck+='\n\n추가 분석 장면\n'+extra;ce+='\n\nAdditional analysis sources\n'+extra
 ck+='\n\n해설·편집·도식: 얌얌코딩\n음악: Nimbus — Eveningland · YouTube Audio Library\nhttps://www.youtube.com/audiolibrary'
 ce+='\n\nCommentary, editing and diagrams: YamyamCoding\nMusic: Nimbus — Eveningland · YouTube Audio Library\nhttps://www.youtube.com/audiolibrary'
 title_en,summary_ko,summary_en=INFO[ep]
 ko=summary_ko+'\n\n'+ '\n'.join(stamp(t)+' '+ko for t,ko,en in chapters)+'\n\n'+footer+'\n\n#게임애니메이션 #게임개발 #얌얌코딩\n\n'+ck
 en=summary_en+'\n\n'+'\n'.join(stamp(t)+' '+en for t,ko,en in chapters)+'\n\n'+footer_en+'\n\n#GameAnimation #GameDevelopment #YamyamCoding\n\n'+ce
 assert len(ko)<=5000 and len(en)<=5000 and len(title_en)<=100 and len(d['title'])<=100,(ep,len(ko),len(en))
 date=datetime.date(2027,1,1)+datetime.timedelta(days=i-3)
 row=dict(id=ep,titleKo=d['title'],titleEn=title_en,descriptionKo=ko,descriptionEn=en,chapters=[dict(seconds=t,ko=ko,en=en) for t,ko,en in chapters],master=str(master),masterSha256=digest,captions={k:str(Path(files[k+'.srt']['path'])) for k in ['ko','en']},thumbnail=str(thumbnail),thumbnailSha256=sha(thumbnail),scheduledFor=f'{date}T08:00:00+09:00',timezone='Asia/Seoul',playlistName='게임 애니메이션 | 움직임과 타격감의 비밀',durationSeconds=d['durationSeconds'],humanApproval='User approved current integrated review and requested these exact versions on YouTube.',advertiserAssessment='user-only',platformStatus='pending')
 save(PUB/ep/'metadata.json',row);(PUB/ep/'description.ko.txt').write_text(ko,encoding='utf-8');(PUB/ep/'description.en.txt').write_text(en,encoding='utf-8');manifest.append(row)
 approved.append(dict(id=ep,masterSha256=digest,approved=True,userMessage='검수했어~ 좋아. A03~A18 전부 이 버전으로 유튜브에 업로드해줘~'))
save(PUB/'upload-manifest.json',manifest);save(PUB/'human-approval.json',approved)
print('Prepared',len(manifest),'approved exact masters; descriptions',[(x['id'],len(x['descriptionKo']),len(x['descriptionEn'])) for x in manifest])
