"""Prepare the exact private-upload payload. Studio submission is recorded separately."""
from pathlib import Path
import json,hashlib,html,subprocess
P=Path(__file__).resolve().parents[2];R=P.parents[1];H=Path(__file__).parent
A=P/'production/local/grid-v1/delivery/output'/P.name
L=P/'production/local/studio-grid-v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
slug=P.name;master=A/(slug+'.captioned.mp4');project=read(P/'project.json')
assert sha(master)==project['delivery']['captionedMasterSha256']
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,nb_frames','-of','json',str(master)]))['streams'][0]
assert [probe['width'],probe['height'],probe['avg_frame_rate']]==[1920,1080,'60/1']
srt=[next(A.glob('*.'+lang+'.srt')) for lang in ['ko','en']];assert all(p.stat().st_size>500 for p in srt)
thumb=H/'thumbnail.jpg';assert 0<thumb.stat().st_size<2000000
cut=read(P/'production/grid-v1/edit-plan.json')
credits={'vf':'SEGA · New VIRTUA FIGHTER Project','mii':'Nintendo · Mii Fighter','donkey-kong':'Nintendo · Donkey Kong','samus':'Nintendo · Samus','inkling':'Nintendo · Inkling','mario':'Nintendo · Mario','goose-retail':'House House · Untitled Goose Game','goose-prealpha':'House House · Untitled Goose Game (pre-alpha)','luigi':'Nintendo · Luigi'}
sources={c['source']:c['sourceUrl'] for c in cut['cuts'] if c.get('sourceUrl')};assert set(sources)==set(credits)
links='\n'.join(credits[k]+' — '+url for k,url in sources.items())+'\nRG Poly · Cartoon City Massive Pack Characters (CC0) — https://rg-poly.itch.io/cartoon-city-massive-pack-characters\nNimbus — Eveningland · YouTube Audio Library — https://www.youtube.com/audiolibrary'
community='https://discord.gg/wZuqe7fqkR';join='https://www.youtube.com/channel/UCOgtkPoyC0VXhCs7Xk3jvjQ/join';coach='https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328'
intro=['“멋지게 움직여 주세요”라는 한 줄을 받으면 애니메이터는 어디서부터 시작할까요? 버추어 파이터의 회피 동작과 직접 만든 포즈 자료를 나란히 보며 원하는 움직임을 정확히 전달하는 방법을 알아봅니다.','What does “make it look cool” tell an animator? A Virtua Fighter dodge and our own pose references show how to turn a vague direction into a motion brief an animator can actually use.']
chapters=[['원하는 동작을 전달하는 일','동작 목록과 시간 조건','말을 포즈 자료로 바꾸기','자료와 완성 동작을 나란히 보기','몸에 맞는 참고 자료','문서에서 움직임으로','결과를 고치고 경험을 공유하기'],['Communicating the movement','Listing moves and durations','Turning words into poses','Reference and finished motion','Finding a body reference that fits','From brief to movement','Revisions and shared experience']]
for j,lang in enumerate(['ko','en']):
 timeline=[]
 for i,(scene,title) in enumerate(zip(cut['scenes'],chapters[j],strict=True)):
  sec=0 if i==0 else int(scene['startFrame']/60)
  timeline.append(f'{sec//60:02}:{sec%60:02} {title}')
 desc=f"{intro[j]}\n\n"+'\n'.join(timeline)+f'\n\n'+('프로그래밍 코칭' if j==0 else 'Programming coaching')+'\n'+coach+'\nDiscord\n'+community+'\n'+('멤버십' if j==0 else 'Membership')+'\n'+join+'\n\n'+('영상·음악 출처' if j==0 else 'Footage and music credits')+'\n'+links+'\n'
 assert len(desc)<5000; (H/f'description.{lang}.txt').write_text(desc,encoding='utf-8')
receipt={'target':'YouTube Studio / private','authorization':'User explicitly requested A1 upload; no public release or schedule requested.','state':'prepared; not sent','blocker':'Windows Computer Use could not verify the current browser URL and stopped before Studio interaction.','studioDuplicateCheck':'pending live Studio access','titleKo':project['title'],'titleEn':'Assigning Animation | Why “Make It Look Cool” Is Not Enough','master':str(master.relative_to(R)),'masterSHA256':sha(master),'bytes':master.stat().st_size,'probe':probe,'thumbnail':str(thumb.relative_to(R)),'thumbnailSha256':sha(thumb),'thumbnailSource':'Brand-reference ImageGen calico / 1280×720 JPEG','captions':[str(p.relative_to(R)) for p in srt],'actualUserWholeViewing':'unconfirmed','youtubeVideoId':None}
(H/'upload.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
items=[(master,'업로드할 영상'),(thumb,'썸네일'),(H/'description.ko.txt','한국어 설명'),(H/'description.en.txt','영어 설명'),(srt[0],'한국어 자막'),(srt[1],'영어 자막'),(H/'upload.json','제목 및 파일 정보')]
(L/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>A01 업로드 파일</title><h1>A01 업로드 파일</h1><p>'+html.escape(project['title'])+'</p><ul>'+''.join('<li><a href="'+html.escape(p.as_uri())+'">'+label+'</a></li>' for p,label in items)+'</ul>',encoding='utf-8')
print(master.stat().st_size,sha(master),len(sources))
