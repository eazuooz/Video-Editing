"""Register exact deliverable paths and deterministic fixed heading pixels."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,datetime
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
batch=read(B/'batch.json')
extraHeads={'shorts-viewfinder-mesh-slicing':['종이 사진을 놓았더니','진짜 길이 생겼다?'],'shorts-outer-wilds-gravity':['작은 행성에 현실 중력을','그대로 넣으면?']}
rootTitles={'shorts-d2r-renderer-logic-separation':'버튼 하나로 20년 전 그래픽이 되는 이유 #디아블로2 #게임개발 #Shorts','shorts-d2r-controller-input-adapter':'디아블로2를 패드로 만들 때, 길 찾기를 꺼버린 이유 #게임개발 #Shorts'}
for row in batch['projects']:
 slug=row['slug'];p=R/'projects'/slug;project=read(p/'project.json');final=project.get('currentFinalDirectory','production/local/final-reviewed-v1');project['currentFinalDirectory']=final
 project.setdefault('paths',{}).update(videoClean=f'projects/{slug}/{final}/clean.mp4',videoBurnedCaptions=f'projects/{slug}/{final}/captioned.mp4',captionsKo=f'projects/{slug}/production/local/audio-v1/captions.ko.srt',captionsEn=f'projects/{slug}/production/local/audio-v1/captions.en.srt',timeline=f'projects/{slug}/production/visual-timing.json')
 project['publishReady']=False;project['status']='production-ready-awaiting-voice';save(p/'project.json',project)
 ignore=p/'.gitignore';previous=ignore.read_text(encoding='utf8') if ignore.exists() else ''
 for line in ['production/local/','**/__pycache__/']:
  if line not in previous.splitlines():previous+=('\n' if previous and not previous.endswith('\n') else '')+line+'\n'
 ignore.write_text(previous,encoding='utf8')
 head=extraHeads.get(slug)
 if not head:
  config=next(x for x in [p/'production/visual-config.json',p/'production/scene-config.json'] if x.exists());head=read(config)['head']
 image=Image.new('RGB',(1080,440),'black');draw=ImageDraw.Draw(image)
 draw.text((196,117),'얌얌코딩',font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',34),fill='#B8C3BC',anchor='mm')
 sizes=[]
 for i,text in enumerate(head):
  size=64 if i==0 else 70
  while ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size).getlength(text)>950:size-=1
  sizes.append(size);draw.text((520,255+i*98),text,font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size),fill='white' if i==0 else '#FFD25A',anchor='mm')
 header=p/'production/local/static-header-v1.png';image.save(header)
 save(p/'production/header-layout.json',dict(path=f'projects/{slug}/production/local/static-header-v1.png',sha256=hashlib.file_digest(header.open('rb'),'sha256').hexdigest(),size=[1080,440],head=head,fontSizes=sizes,reason='Deterministic fixed heading avoids missing first-frame font rasterization. All dynamic term/picture labels below440px remain visible.'))
 finish=p/'production/finish-video.py';code=finish.read_text(encoding='utf8')
 old="    header='null' # Native Motion Canvas header is inspected at current frame and mobile size.\n    run(['ffmpeg','-v','error','-n','-i',str(visual),'-i',str(A/'final-mix.m4a'),'-map','0:v:0','-map','1:a:0','-vf',header,'-c:v','libx264','-threads','4','-preset','fast','-crf','16','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(L/'clean.mp4')])"
 new="    header=P/'production/local/static-header-v1.png'\n    assert header.exists(), 'Generate the inspected fixed brand heading first.'\n    run(['ffmpeg','-v','error','-n','-i',str(visual),'-i',str(A/'final-mix.m4a'),'-i',str(header),'-filter_complex','[0:v][2:v]overlay=0:0:format=auto[v]','-map','[v]','-map','1:a:0','-frames:v',str(c['frames']),'-c:v','libx264','-threads','4','-preset','fast','-crf','16','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(L/'clean.mp4')])"
 if old in code:finish.write_text(code.replace(old,new),encoding='utf8')
 elif 'static-header-v1.png' not in code:raise RuntimeError('Unexpected mixer source; review before editing '+slug)
 if slug in rootTitles:
  title=rootTitles[slug];mechanism='게임 상태를 계산하는 로직과 화면을 그리는 렌더링을 나누면, 같은 전투를 서로 다른 모습으로 표현할 수 있습니다.' if slug.endswith('logic-separation') else '클릭은 목적지를, 스틱은 방향을 전달합니다. 디아블로 II: 레저렉션은 입력을 연결하는 계층과 직접 이동에 맞춘 조작 방식을 함께 다듬었습니다.'
  source=read(p/'planning/production-plan.json')['source']
  desc=mechanism+'\n\n실제 게임 화면과 직접 만든 도식으로 원리를 살펴봅니다. 디아블로 II: 레저렉션 출시 당시 개발 설명을 바탕으로 구성했습니다. 도식의 위치·범위는 설명용이며 게임에서 측정한 수치가 아닙니다.\n\n자료와 크레딧\n개발자 설명: '+source+'\n공식 설명: https://news.blizzard.com/en-us/article/23722094/bringing-the-original-diablo-ii-experience-to-console\n게임 화면: Blizzard Entertainment 공식 게임플레이 B-roll 및 비교 영상\nhttps://blizzard.gamespress.com/en/Kit/Details/Diablo-II-Resurrected-Launch-Press-Kit\nhttps://diablo2.blizzard.com/en-us/\n음악: Pixel Peeker Polka - faster, Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0\nhttps://creativecommons.org/licenses/by/4.0/\n'
  save(p/'publishing/metadata-draft.json',dict(titleKo=title,descriptionKo=desc,status='draft-for-local-final-review',humanApproved=False))
  (p/'publishing/title.ko.txt').write_text(title+'\n',encoding='utf8');(p/'publishing/description.ko.txt').write_text(desc,encoding='utf8')
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();row.update(status='production-ready-awaiting-voice',updatedAt=now,humanReview='pending',platform='not-uploaded')
save(B/'batch.json',batch)
work=read(R/'shared/publishing/shorts-worklist.json');selected={x['slug'] for x in batch['projects']}
for row in work['rows']:
 if row.get('slug') in selected:row.update(production='production-ready-awaiting-voice',review='not-ready-for-final-review',youtube='not-uploaded',updatedAt=now)
work['updatedAt']=now;save(R/'shared/publishing/shorts-worklist.json',work)
save(B/'checkpoint.json',dict(status='ten-projects-prepared-awaiting-approved-voice',updatedAt=now,requestedVideos=10,completedVideos=0,scriptCaptionPreflight='10/10 pass; actual ASR/timing not yet available',storage='Only this new batch local media moved to verified C: targets; old media preserved.',gpu='User game active; finite voice queue waits for exit',next='Generate approved voice, align actual words, build native scenes/composites, mix, four outputs, full QA and human final review.',platformActionsPerformed=False))
print('Prepared all ten manifest paths, static heading assets and truthful production state.')
