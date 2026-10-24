from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
slug='game-math-euler-axis-angle';P=R/'projects'/slug/'production/concept-fit-v2'
sources=read(P/'composition.json')['sources']
for source in sources.values():source['rightsEvidence']='projects/'+slug+'/production/concept-fit-v2/source-evidence.json'
def patch(sid,src,start,seconds,title,phases,speech,observed):
 return dict(scene=sid,source=src,offset=0,duration=seconds,title=title,meaning='',segments=[dict(kind='motion',**{'in':start},seconds=seconds)],guides=[],phases=phases,modelCrop=[80,150,850,750],sourceReview=observed,speechMapping=speech)
patches=[
 patch('02','totk',279,14,'高리의 열린 방향을 바꾸고 붙이기'.replace('高','고'),[(0,4,'붙일 고리를 잡기'),(4,10,'열린 쪽의 방향을 돌리기'),(10,14,'판에 붙인 자세 확인')],
 'Introduction names hook opening; whole rotation/attachment observed while unchanged right model explains heading/pitch/bank. No game angles inferred.',
 'TotK279–293 inspected in totk-ring2fps sheet; detachment,rotation287–289,placement289–291,release. Stop before lifting entire platform.'),
 patch('14','dorf',46,9.5,'타일의 방향을 맞춘 뒤 배치하기',[(0,3,'풍차 타일을 놓을 곳 선택'),(3,6,'주변에 맞춰 방향 변경'),(6,9.5,'방향을 정한 뒤 배치')],
 '0–7.6s specifically names windmill tile rotation;7.6s target direction versus path starts while placement completes. Full sequence now ends before accelerated map expansion.',
 'Dorfromantik46–55.5 inspected at1fps; windmill tile selected47,placed preview49,turn50–51,confirmed52–53. Exclude rapid map montage56+.'),
 patch('20','totk',291,24,'회전한 고리를 옮겨 레일에 걸기',[(0,5,'판과 고리를 함께 들어 올리기'),(5,10,'고리를 레일 위로 이동'),(10,14,'내려놓아 걸린 결과 확인'),(14,24,'위치가 달라도 고리의 형태는 유지')],
 '0–8.7s lifting/hanging;8.7–18.5s position path versus rotation vector;18.5–24.9s moving camera is distinct. Native camera walk around attached assembly remains relevant, then return to defined model for numerical vectors.',
 'TotK291–315 inspected2fps; pickup292,translation294–300,release301,walk-around304–315. No object deformation or false measured rotation vectors.')]
d=dict(episode='M04',slug=slug,revision='gameplay-motion-v4',patchSet='reviewed-native-1',status='source-sequence-reviewed',newTts=False,sources=sources,patches=patches,coverage={'previousNativeSeconds':28.5,'newNativeSeconds':47.5,'examples':3,'qualityReview':'pending final encoded comparison'},preservation={'narration':'unchanged','explanation':'unchanged','totalFrames':'unchanged'},sourceReview={'method':'Ordered decoded frames,1fps/2fps; final audiovisual review pending','nativeSpeed':1,'analyticalFreeze':0})
(B/'m04-plan.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('M04:47.5native seconds, no added holds')
