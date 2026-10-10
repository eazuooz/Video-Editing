"""Prepare bilingual reviewed metadata; never overwrite an upload receipt."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1]
assert slug in ['game-math-plane-distances-v2','game-math-triangle-addresses-v2']
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
P=ROOT/'projects'/slug;D=P/'publishing';m=read(P/'project.json');t=read(P/'production/timeline.json');part=m['lecture']['episode']
assert m['finalRender']['currentPixelApproval']
assert not (D/'youtube-upload.json').exists(),'Preserve the actual prepared/uploaded receipt.'
ko=('앞 강의에서는 연결선과 물체의 범위를 구했습니다. 이제 그 범위에서 고른 점이 실제 표면에서 얼마나 떨어졌는지 계산합니다. 바닥을 따라가는 방향과 수직 방향을 구분하고, 같은 점으로 대입값·거리·가장 가까운 위치를 차례로 확인합니다. 이어서 세 점과 순서 있는 경계로 면의 방향을 구합니다. 표면까지 도착해도 유한한 발판 안인지는 남는 질문입니다. 그 질문을 다음 편의 삼각형 좌표로 이어갑니다. 평면과 삼각형 두 편 중 첫 번째 강의입니다.' if part==1 else '앞 편에서 표면까지의 거리와 가장 가까운 점을 찾았습니다. 하지만 평면 위에 있다는 것만으로 유한한 발판 안인지 알 수는 없습니다. 같은 삼각형과 점을 유지하면서 넓이, 세 꼭짓점의 가중합, 주어진 점의 가중치 계산으로 이어갑니다. 화면에서 같은 위치로 보이는 점도 실제 평면 위인지 따로 확인합니다. 마지막에는 찾은 위치에 같은 가중치를 적용해 색 같은 표면 값을 계산합니다. 평면과 삼각형 두 편 중 두 번째 강의입니다.')
en=('The previous lecture calculated connections and object bounds. Now we ask how far a selected point is from a surface. We distinguish directions along the floor from its normal, then follow the same point through equation residual, perpendicular distance and closest position. Next, three points and an ordered boundary give us the surface direction. Reaching the infinite plane still leaves the finite-platform question, which motivates triangle coordinates in the next lecture. This is the first of two lectures on planes and triangles.' if part==1 else 'The first lecture found the distance to a surface and its closest point. Being on an infinite plane still does not establish that a point lies inside a finite platform. We retain the same triangle and point while moving from area to weighted vertex sums and then reading weights from the given point. Matching projected screen positions also requires a separate coplanarity check. Finally, the same weights transfer surface values such as color at that position. This is the second of two lectures on planes and triangles.')
links=[('게임수학 PART2 수업 자료','Game Math PART2 course materials','https://www.yamyamcoding.com/1ea0b1ff-a61e-803f-bd54-cac4f028f6b3'),('얌얌코딩 홈페이지','YamYamCoding website','https://www.yamyamcoding.com/'),('얌얌위키 전체 수업 노트','YamYamWiki course notes','https://www.yamyamcoding.com/0d2adf45-5d1a-43be-a37c-61c94b1ae2c8')]
ko+='\n\n'+'\n\n'.join(a+'\n'+u for a,b,u in links);en+='\n\n'+'\n\n'.join(b+'\n'+u for a,b,u in links)
english={
 'PF01':'From a bounding-box candidate to the actual surface','01':'Distance to a floor and position inside a triangle',
 '02':'Observe the platform surface as a reference','PB01':'Directions along the floor and perpendicular to it',
 'PG01':'Leave the floor and return to a surface','03':'Separate a plane’s direction and position',
 'PB02':'Why can the residual double for the same floor?','04':'Separate an equation value from actual distance',
 'PG02':'Observe position and slope separately','05':'Terrain height and its reference',
 'PB03':'From a distance to the point we should reach','06':'The closest point on a plane',
 'PB04':'Build a normal from the surface we observed','07':'Construct a normal from three points',
 '08':'Observe a visible triangular floor marking','PG03':'Follow boundary order as surface direction changes',
 'PC09':'From three points to a boundary with more vertices','09':'Multiple vertices require an order',
 'PF02':'Reaching the plane can still miss the platform','PF03':'Find an address inside a finite triangle',
 '10':'Connect edge lengths and angles','11':'Locate a point between three references',
 'PB05':'Why does area help determine a point’s location?','PG04':'Being on a plane does not establish passage membership',
 '12':'Calculate the same area in three ways','PB06':'From two-point interpolation to three vertex weights',
 '13':'Describe a triangle position with three numbers','14':'Move the triangle’s reference together',
 '15':'Calculate positions inside and outside','PB07':'Read the address back from the point we created',
 '16':'Recover weights from area ratios','17':'Observe surfaces at different heights',
 'PB08':'A projected address differs from the actual point','18':'Projection does not establish coplanarity',
 'PG06':'Separate an airborne object from its floor projection','19':'Track three observed corners together',
 'PB09':'Use the address to retrieve a surface value','20':'Interpolate color with the same weights',
 'PG07':'Separate surface position from its stored value','21':'Observe surface location and color together',
 '22':'Check distance, plane membership and weights together'}
chapters=[{'startSeconds':0 if i==0 else s['start'],'ko':s['title'],'en':english[s['id']]} for i,s in enumerate(t['scenes'])]
chapters.append({'startSeconds':t['seconds']-10,'ko':'멤버십 감사와 프로그래밍 과외 안내','en':'Membership thanks and programming coaching'})
assert all(int(b['startSeconds'])-int(a['startSeconds'])>=10 for a,b in zip(chapters,chapters[1:]))
def stamp(s):n=int(s);return f'{n//60:02}:{n%60:02}'
ko+='\n\n실제 게임40%·설명60%, 배경음악 없이 진행하는 강의입니다.\n\n챕터\n'+'\n'.join(stamp(c['startSeconds'])+' '+c['ko'] for c in chapters)
en+='\n\n40% actual gameplay and60% explanation, narrated without background music.\n\nChapters\n'+'\n'.join(stamp(c['startSeconds'])+' '+c['en'] for c in chapters)
def file_record(path):
 f=ROOT/path;return {'path':path,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
video=file_record(f'output/{slug}/{slug}.captioned.mp4');video['seconds']=t['seconds'];assert video['sha256']==read(P/'production/current-pixel-review.json')['sha256']
record={'slug':slug,'status':'prepared-reviewed-local; actual Studio upload pending','video':video,
 'metadata':{'title':m['titles']['ko'],'description':ko,'privacyStatus':'private','language':'ko'},
 'englishMetadata':{'title':m['titles']['en'],'description':en,'language':'en-US','status':'pending'},
 'descriptionBody':{'ko':ko,'en':en},'subtitles':[{**file_record(f'output/{slug}/{slug}.{lang}.srt'),'language':lang,'status':'pending-platform-upload','cueCount':len(t['koCaptions'])} for lang in ['ko','en']],
 'thumbnail':{**file_record(f'projects/{slug}/publishing/thumbnail-v2.png'),'status':'prepared-reviewed; platform pending'},
 'videoId':None,'scheduled':False,'fullPublishingSettingsComplete':False,'humanListening':'pending',
 'rightsReview':'Preserved recording permissions and Valve policy; game-IP/human review pending','baselinePreserved':'wsxSYEEj8aQ','chapters':chapters}
write(D/'youtube-upload.json',record)
subprocess.run(['node',str(ROOT/'scripts/prepare-youtube-upload.cjs'),slug],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
m['paths'].update(publishingKo=f'projects/{slug}/publishing/upload-description.ko.txt',publishingEn=f'projects/{slug}/publishing/upload-description.en.txt')
write(P/'project.json',m)
