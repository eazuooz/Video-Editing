"""Local KO/EN metadata;preserve introduction/links and use measured current chapters."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
basep=ROOT/'projects/game-math-orientation-matrices/publishing/youtube-upload.json';base=rd(basep)
chapterp=O/'current34-measured-chapters-v1.json';chapters=rd(chapterp)['chapters']
en={'01':'Lecture overview','02a':'What to observe during flight','02':'Separate direction from orientation',
'03':'An arrow versus a complete orientation','03b':'Position and orientation on a bicycle','04':'Three axes attached to an object',
'05':'Body up versus screen up','06a':'Read body axes in a world frame','06':'Fix column vectors and transform direction',
'07':'Calculate a90-degree rotation','07b':'Read an aircraft nose and wings together','08':'Local forward and world direction',
'09a':'Axis components and the transpose','09':'Why inverse rotation uses the transpose','10':'Direction cosines as dot products',
'10b':'From aircraft orientation to component placement','11':'The same object in different frames','12':'Compose nested orientations',
'13a':'Check lengths and right angles first','13':'Two conditions for a proper rotation','14':'Rotation versus apparent stretching',
'15':'Reject reflection and scaling','16a':'Remove a parallel component','16':'Small errors and matrix drift',
'17':'Visible flight and internal calculations','18':'Nine stored values and memory','19':'Name transform direction in code',
'20':'The frame used by game commands','21a':'Validate intermediate orientations too','21':'Why mixing matrix entries can collapse',
'22':'Two worked problems','23':'Read orientation during flight','24':'Three things to remember'}
def tc(t):
 s=int(t);return f'{s//60:02d}:{s%60:02d}'
# The six-second01b comparison bridge stays within the opening chapter.
platform=[c for c in chapters if c['scene']!='01b']
assert len(chapters)==34 and len(platform)==33 and set(en)=={c['scene'] for c in platform}
rows=[dict(**c,timecode=tc(0 if c['scene']=='01' else c['start']),enTitle=en[c['scene']]) for c in platform]
rows.append(dict(scene='outro',title='멤버십 감사와 프로그래밍 과외 안내',start=65317/60,startFrame=65317,timecode=tc(65317/60),enTitle='Membership thanks and programming coaching'))
folder=O/'publishing';folder.mkdir(exist_ok=True)
out=folder/'metadata-text-plan-v1.json';assert not out.exists()
texts={}
footer_ko=base['metadata']['description'].split('\n\n🎮',1)[1]
footer_en=base['englishMetadata']['description'].split('\n\n🎮',1)[1]
for lang in ['ko','en']:
 old_body=base['descriptionBody'][lang]
 head=old_body.split('\n\n'+('챕터' if lang=='ko' else 'Chapters'),1)[0]
 introduction=head.split('\n\n',1)[0]
 addition=('Superflight의 비행, Descenders의 자전거, Trailmakers의 조립 비행기, Space Engineers의 부품 배치를 연결해 같은 자세 표현 원리를 비교합니다.' if lang=='ko' else
 'We connect flight in Superflight, bicycle orientation in Descenders, an assembled aircraft in Trailmakers and component placement in Space Engineers to compare the same representation of orientation.')
 head=head.replace(introduction,introduction+'\n\n'+addition,1)
 chapter_text='\n'.join(c['timecode']+' '+c['title' if lang=='ko' else 'enTitle'] for c in rows)
 body=head+'\n\n'+('챕터' if lang=='ko' else 'Chapters')+'\n'+chapter_text
 text=body+'\n\n🎮'+(footer_ko if lang=='ko' else footer_en)
 assert len(text)<=5000 and introduction in text
 for url in ['https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328','https://discord.gg/wZuqe7fqkR','https://www.youtube.com/channel/UCOgtkPoyC0VXhCs7Xk3jvjQ/join']:
  assert url in text
 target=folder/f'upload-description.{lang}.txt';assert not target.exists();target.write_text(text+'\n','utf-8')
 texts[lang]=dict(path=target.relative_to(ROOT).as_posix(),sha256=sha(target),characters=len(text),title=base['metadata' if lang=='ko' else 'englishMetadata']['title'],body=body)
comment=folder/'pinned-comment.ko.txt';assert not comment.exists();comment.write_bytes((ROOT/'projects/game-math-orientation-matrices/publishing/pinned-comment.ko.txt').read_bytes())
data=dict(preparedAt=datetime.now(timezone.utc).isoformat(),baselineReceipt=basep.relative_to(ROOT).as_posix(),baselineReceiptSha256=sha(basep),
 measuredChapters=chapterp.relative_to(ROOT).as_posix(),measuredChaptersSha256=sha(chapterp),internal34ChaptersPreserved=True,
 platformOpeningGroupsSixSecond01bBridge=True,platformChapterRows=rows,texts=texts,pinnedComment=dict(path=comment.relative_to(ROOT).as_posix(),sha256=sha(comment),status='pending-private-video-comments-unavailable'),
 originalIntroductionAndChannelLinksPreserved=True,platformMetadataSaved=False,newActualVideoId=None)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(localMetadataPrepared=True,chapterRows=len(rows),koCharacters=texts['ko']['characters'],enCharacters=texts['en']['characters'],platformSaved=False)))
