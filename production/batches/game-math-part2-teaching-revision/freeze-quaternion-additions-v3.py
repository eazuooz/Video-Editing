"""Review/freeze only authorized additions; approved v2 data and media stay exact."""
from pathlib import Path
import copy,datetime,hashlib,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
baseline=read(R/'baseline.json');additions=read(R/'additions.json');mapping=read(R/'tts-map.json')
master=ROOT/'projects/game-math-quaternion-cross-game-additions-v3';manifest=read(master/'project.json')
assert not list((ROOT/manifest['tts']['outputDir']).glob('**/*.wav')),'Do not revise frozen spoken lines after synthesis.'
for s in additions['scenes']:
 if s['id']=='QF20':s['title']='스페이스 엔지니어스: 부품 방향과 전체 자세 구분'
 if s['id']=='QF31':
  s['ko']=[x.replace('모형에서 오른쪽 방향과 위쪽 방향','모형에서 한쪽 날개 방향과 위쪽 방향') for x in s['ko']]
  s['en']=[x.replace('rightward and upward directions','one-wing and upward directions') for x in s['en']]
 if s['kind']=='actual':
  stem={'trailmakers-JvTCVUEc1ZE':'trail','space-engineers-XvpNC9lkLwQ':'gear-v3','besiege-uWKEJ92486U':'besiege'}[s['sourceId']]
  path=R/(stem+'-screen-track.json');track=read(path)
  assert sha(ROOT/track['video'])==track['videoSha256']
  assert len(track['frames'])==round(s['maximumSeconds']*60)
  s['annotation'].update(tracksPrepared=True,trackFile=path.relative_to(ROOT).as_posix(),trackSha256=sha(path))
byid={s['id']:s for s in additions['scenes']};write(R/'additions.json',additions)
originals=0;baseline_hashes=[]
for e in baseline['episodes']:
 p=ROOT/'projects'/e['newSlug'];lesson=read(p/'production/lesson.json')
 old=read(R/'baseline'/e['slug']/'production/lesson.json')['scenes'];oldids={s['id'] for s in old}
 lesson['scenes']=[copy.deepcopy(byid.get(s['id'],s)) for s in lesson['scenes']]
 assert [s for s in lesson['scenes'] if s['id'] in oldids]==old
 originals+=len(old);write(p/'production/lesson.json',lesson)
 for lang in ['ko','en']:
  script=read(p/f'script/narration.{lang}.json');script['scenes']=[dict(id=s['id'],title=s['title'],lines=s[lang]) for s in lesson['scenes']]
  write(p/f'script/narration.{lang}.json',script)
 for entry in e['files']:
  assert sha(ROOT/entry['path'])==entry['sha256'],entry['path']
  baseline_hashes.append(dict(path=entry['path'],sha256=entry['sha256']))
 for lang in ['ko','en']:
  path=master/f'script/narration.{lang}.json';script=read(path)
  for item in mapping:
   s=byid[item['additionId']];target=next(x for x in script['scenes'] if x['id']==item['ttsScene'])
   target.update(title=s['title'],lines=s[lang])
  write(path,script)
assert originals==80
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
from quaternion import qaxis,qmul,qinverse,qrotate
x=qaxis([1,0,0],np.pi/2);y=qaxis([0,1,0],np.pi/2);z=qaxis([0,0,1],np.pi/2)
a=qaxis([0,0,1],np.pi/6);b=z;d=qmul(b,qinverse(a))
checks=[]
for name,result,expected in [
 ('x90 keeps front',qrotate(x,[1,0,0]),[1,0,0]),('x90 sends one wing up',qrotate(x,[0,1,0]),[0,0,1]),
 ('exact inverse restores model',qrotate(qinverse(z),qrotate(z,[1,0,0])),[1,0,0]),
 ('fixed x then y',qrotate(qmul(y,x),[0,0,1]),[0,-1,0]),('fixed y then x',qrotate(qmul(x,y),[0,0,1]),[1,0,0]),
 ('world delta reaches target',qmul(d,a),b),('vector z height unchanged',qrotate(z,[1,0,1]),[0,1,1]),
 ('rigid dot preserved',[np.dot(qrotate(x,[0,1,0]),qrotate(x,[0,0,1]))],[0])]:
  checks.append(dict(name=name,result=np.asarray(result).tolist(),expected=np.asarray(expected).tolist(),passed=bool(np.allclose(result,expected,atol=1e-12))))
assert all(c['passed'] for c in checks)
for s in additions['scenes']:
 if s['kind']=='actual':assert sha(ROOT/s['sourceFile'])==s['sourceSha256']
reviews=[]
for e,label in zip(baseline['episodes'],['foundations','calculations']):
 report=ROOT/f'production/preflight/{e["newSlug"]}.json';studio=R/f'studio-{label}-schedule.txt'
 assert report.exists() and studio.exists()
 reviews.append(dict(newSlug=e['newSlug'],oldSlug=e['slug'],actualOldVideoId=e['actualVideoId'],decision='authorized additive replacement of same episode',duplicateReview=report.relative_to(ROOT).as_posix(),duplicateReviewSha256=sha(report),actualStudioEvidence=studio.relative_to(ROOT).as_posix(),studioEvidenceSha256=sha(studio),preserveActualOldVideoUntilReplacementVerified=True))
write(R/'authorized-replacement-review.json',dict(userRequest='아직 게시 되지 않은것 (예약된거 포함) ... 설명하기 위한 게임목록을 더 늘려주고 최소 4가지 이상 ... 수정이 필요하면 너가 진행해줘',reviews=reviews,distinctNewTopicClaimed=False,masterStandaloneUploadAllowed=False))
audit=dict(createdAt=datetime.datetime.now().astimezone().isoformat(),project=manifest['slug'],original80DictionariesAndOrderExact=True,baselineFilesStillExact=baseline_hashes,baselineAudioOverwritten=False,projectManifestSha256=sha(master/'project.json'),scriptSha256={lang:sha(master/f'script/narration.{lang}.json') for lang in ['ko','en']},voiceSettingsExact=manifest['tts'],voiceReferenceSha256={key:sha(ROOT/manifest['tts'][key]) for key in ['reference','referenceText']},additionsSha256=sha(R/'additions.json'),checks=checks,sourceTracksPrepared=True,sourceGameWorldAnglesMeasured=False,fullGameInverseAsserted=False,gpuBoundaryHandoffRequired=True,besiegeDescriptionException='pending user answer before external upload',humanWholeListening='pending',finalMovingCaptionAndNarrationReview='pending',finalRatioAfterMeasuredNarration='pending')
write(R/'pretts-frozen-audit.json',audit)
print('Frozen 14 new-only bilingual scenes;80 approved dictionaries/order and22 baseline records remain exact;8 numerical checks passed.')
