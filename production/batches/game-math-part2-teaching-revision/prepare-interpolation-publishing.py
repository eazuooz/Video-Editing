"""Prepare exact new bilingual metadata, never copy baseline platform proof."""
from pathlib import Path
import json,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1]
assert slug in ['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
P=ROOT/'projects'/slug;D=P/'publishing';m=read(P/'project.json');t=read(P/'production/timeline.json');part=m['lecture']['episode']
assert m['finalRender']['currentPixelApproval']
assert not (D/'youtube-upload.json').exists(),'Preserve an already prepared/uploaded receipt; edit that receipt explicitly.'
ko=('두 자세를 알고 있다면 그 사이의 자연스러운 움직임은 어떻게 만들까요? 같은 몸체와 기준축을 유지하며 각도의 짧은 경로, 선형 보간, 쿼터니언 보간, 시간에 따른 속도를 차례로 연결합니다. 마지막에는 같은 시작과 끝을 두고 시간 함수를 바꿨을 때 중간 자세가 어떻게 달라지는지 작은 숫자로 확인합니다. 두 편 중 첫 번째 강의입니다.' if part==1 else '앞 강의에서 만든 자세를 각도·쿼터니언·행렬로 바꿔 적어도 같은 회전일까요? 같은 물체의 앞쪽과 위쪽을 따라가며 좌표와 곱셈 순서의 약속을 정하고, 변환과 역변환을 연결합니다. 마지막에는 벡터를 실제로 돌리고 되돌려 같은 방향과 길이가 나오는지 계산합니다. 보간과 회전 변환 두 편 중 두 번째 강의입니다.')
en=('Given two orientations, how do we create a natural motion between them? Keeping the same body and reference axes, we connect the short angular path, linear interpolation, quaternion interpolation and speed over time. We then use small numbers to compare intermediate orientations when the time function changes but both endpoints stay the same. This is the first of two lectures.' if part==1 else 'Does an orientation remain the same when we rewrite it as angles, a quaternion or a matrix? Following the same body’s forward and up directions, we establish coordinate and multiplication conventions, then connect conversion with reversal. Finally, we rotate and reverse a vector to check that its direction and length are restored. This is the second lecture on interpolation and rotation conversions.')
links=[('게임수학 PART2 수업 자료','Game Math PART2 course materials','https://www.yamyamcoding.com/1ea0b1ff-a61e-803f-bd54-cac4f028f6b3'),('얌얌코딩 홈페이지','YamYamCoding website','https://www.yamyamcoding.com/'),('얌얌위키 전체 수업 노트','YamYamWiki course notes','https://www.yamyamcoding.com/0d2adf45-5d1a-43be-a37c-61c94b1ae2c8')]
ko+='\n\n'+'\n\n'.join(a+'\n'+url for a,b,url in links);en+='\n\n'+'\n\n'.join(b+'\n'+url for a,b,url in links)
ids=['IF01','01','03','IP01','05','06','07','09','10','12','IP07','14','IP03','IF02'] if part==1 else ['IF03','16','IP04','18','19','20','IP05','21','22','24','25','IP08','26','IP06']
english=['Overview: the motion between two orientations','What this lecture will explain','Blending numbers while preserving a rotation','A small-number rotation example','An endpoint does not record the full path','SLERP follows a unit-sphere arc','Nearly identical orientations and invalid inputs','Calculate the middle of a ninety-degree rotation','NLERP preserves rotation but changes speed','Constant speed also requires a time condition','Linear and squared time on the same endpoints','Read body directions in flight and skiing','Pass the intermediate orientation to the next task','Recap and the next question'] if part==1 else ['Overview: numbers for the same orientation','Conventions before the conversion graph','Length and atan2 with small numbers','Euler angles and matrices: a round trip','Build matrix axes from a quaternion','Different numbers for the same body orientation','Protect division when extracting rotation','Recover a quaternion at a half turn','Connect Euler angles and quaternions','Recover axis and angle at zero and a half turn','Check an intermediate orientation and a round trip','Rotate and reverse the same vector','Conventions and verification','From rotation to lines and bounds']
chapters=[]
for ident,title in zip(ids,english):
 s=next(x for x in t['scenes'] if x['id']==ident);chapters.append({'startSeconds':0 if ident in ['IF01','IF03'] else s['start'],'ko':s['title'],'en':title})
if part==1:
 # The preserved original overview starts at9.35s. Keep its narration and
 # pixels, but use a single opening chapter so YouTube's10s minimum holds.
 chapters=[c for c in chapters if c['startSeconds']!=next(s['start'] for s in t['scenes'] if s['id']=='01')]
chapters.append({'startSeconds':t['seconds']-10,'ko':'멤버십 감사와 프로그래밍 과외 안내','en':'Membership thanks and programming coaching'})
assert all(b['startSeconds']-a['startSeconds']>=10 for a,b in zip(chapters,chapters[1:]))
def stamp(s):
 n=int(s);return f'{n//60:02}:{n%60:02}'
ko+='\n\n실제 게임40%·설명60%, 배경음악 없이 진행하는 강의입니다.\n\n챕터\n'+'\n'.join(stamp(c['startSeconds'])+' '+c['ko'] for c in chapters)
en+='\n\n40% actual gameplay and 60% explanation, narrated without background music.\n\nChapters\n'+'\n'.join(stamp(c['startSeconds'])+' '+c['en'] for c in chapters)
def file_record(path):
 f=ROOT/path;return {'path':path,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
video=file_record(f'output/{slug}/{slug}.captioned.mp4');video['seconds']=t['seconds']
assert video['sha256']==read(P/'production/current-pixel-review.json')['sha256']
record={'slug':slug,'status':'prepared-reviewed-local; actual Studio upload pending','video':video,'metadata':{'title':m['titles']['ko'],'description':ko,'privacyStatus':'private','language':'ko'},'englishMetadata':{'title':m['titles']['en'],'description':en,'language':'en-US','status':'pending'},'descriptionBody':{'ko':ko,'en':en},'subtitles':[{**file_record(f'output/{slug}/{slug}.{lang}.srt'),'language':lang,'status':'pending-platform-upload','cueCount':len(t['koCaptions'])} for lang in ['ko','en']],'thumbnail':{**file_record(f'projects/{slug}/publishing/thumbnail-v2.png'),'status':'prepared-reviewed; platform pending'},'videoId':None,'scheduled':False,'fullPublishingSettingsComplete':False,'humanListening':'pending','rightsReview':'Recording reuse statements retained; game-IP/human review pending','baselinePreserved':'mGBYkpSC9Mw','chapters':chapters}
write(D/'youtube-upload.json',record)
subprocess.run(['node',str(ROOT/'scripts/prepare-youtube-upload.cjs'),slug],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
