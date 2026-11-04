"""M26 additive V2: distinguish units, signs, magnitude and time in speech."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,math,shutil,subprocess

P=Path(__file__).resolve().parents[1]; R=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
local=P/'production/local';old=local/'audio-v1';new=local/'audio-v2'
assert not new.exists() and read(old/'finite-worker.json')['status']=='voice-generated-review-pending'
assert read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['productionAllowedNow']
# New narration keeps the number of meaning-group sentences and original examples.
changes={
 '017': [('비시지의 풍차에서는 중심 가까운 부분과 날개 끝이 함께 돕니다.',
          '풍차의 날개를 봐 주세요.'),
         ('중심에서 얼마나 떨어졌는지에 따라 한 바퀴 동안 지나가는 길이는 달라지죠.',
          '게임 비시지에서 날개 끝과 중심 가까운 부분은 함께 돌지만, 중심에서 떨어진 거리에 따라 한 바퀴 동안 지나가는 길이는 다릅니다.')],
 '021': [('칠 초에 영으로 돌아온 뒤에는 팔 초에 마이너스 일, 구 초에 마이너스 이로 갑니다.',
          '칠 초에 원점으로 돌아온 뒤에는 매초 한 칸씩 왼쪽으로 가서, 팔 초에는 원점 왼쪽 한 칸, 구 초에는 왼쪽 두 칸에 도착합니다.')],
 '023': [('오 점 오 초부터 육 점 오 초는 사인 구간입니다.',
          '사인 구간에서 시작 시각을 오 점 오 초, 끝 시각을 육 점 오 초로 잡아 볼게요.')],
 '026': [('사 점 일 초에서는 파이 코사인 사 점 일 파이를 계산합니다.',
          '이번에 속도를 구할 시각은 사 점 일 초이므로, 파이에 코사인 사 점 일 파이를 곱합니다.')],
 '028': [('영 점 일 초, 일 초, 일 점 구 초는 첫 구간이므로 가속도는 모두 마이너스 이입니다.',
          '영 점 일 초, 일 초, 일 점 구 초는 모두 첫 구간에 있고, 속도가 매초 두 단위씩 줄어서 가속도는 음수인 마이너스 이가 됩니다.')],
 '030': [('다음 발사체는 초기 위치가 영 피트, 십 피트이고, 초속 백오십 피트의 속력으로 수평에서 사십 도 위를 향해 출발합니다.',
          '다음 문제에서는 거리를 피트로 재고, 수평 위치 영, 높이 십 피트에서 초속 백오십 피트로 수평보다 사십 도 위를 향해 발사합니다.'),
         ('수평 속도는 백오십 코사인 사십 도로 약 백십사 점 구일, 수직 속도는 백오십 사인 사십 도로 약 구십육 점 사이입니다.',
          '초기 속력에 사십 도의 코사인을 곱하면 수평 성분이 초속 약 백십사 점 구일 피트, 사십 도의 사인을 곱하면 수직 성분이 초속 약 구십육 점 사이 피트가 됩니다.')],
 '031': [('약 구십육 점 사이 나누기 삼십이로 약 삼 점 영일삼 초입니다.',
          '처음 수직 속도는 초속 약 구십육 점 사이 피트이고, 일 초마다 초속 삼십이 피트씩 줄어드니 둘을 나누면 약 삼 점 영일삼 초가 걸립니다.'),
         ('이 시간을 수평 위치에 대입하면 약 삼백사십육 점 이이 피트입니다.',
          '그동안 가로로 간 거리는 수평 속도에 이 시간을 곱한 값, 약 삼백사십육 점 이이 피트가 됩니다.'),
         ('초기 십 피트를 더한 정점 높이는','출발 높이 십 피트를 더한 정점 높이는')],
 '032': [('따라서 정점까지 시간의 두 배, 약 육 점 영이육 초 뒤에 돌아옵니다.',
          '올라간 시간만큼 다시 내려오니, 같은 높이에 도착하는 시각은 약 육 점 영이육 초가 됩니다.'),
         ('수평 속도에 이 시간을 곱하면 수평 변위는','수평 속도에 방금 구한 비행 시간을 곱하면 수평 변위는')],
 '033': [('변위는 초기 속도 벡터 곱하기 시간 더하기 이분의 일 가속도 벡터 곱하기 시간 제곱입니다.',
          '먼저 초기 속도 벡터에 시간을 곱하고, 여기에 가속도 벡터와 시간 제곱을 곱한 값의 절반을 더하면 변위가 됩니다.'),
         ('이분의 일 에이 티 제곱 더하기 비 티 빼기 디는 영입니다.',
          '에이 곱하기 티 제곱의 절반에 비 곱하기 티를 더하고 디를 빼면 영입니다.')],
 '035': [('자연상수 이, 약 이 점 칠일팔의 지수를 아이 엑스로 둔 지수 함수를 급수로 펼쳐 보겠습니다.',
          '자연로그의 밑은 소문자 알파벳 이로 쓰고 그 값은 약 이 점 칠일팔인데, 이 수를 밑으로 하고 아이 엑스를 지수로 한 함수를 급수로 펼쳐 볼게요.')],
 '036': [('실수 항끼리 모으면 일 빼기 엑스 제곱 나누기 이 팩토리얼 더하기 엑스 사 제곱 나누기 사 팩토리얼입니다.','실수 항끼리 모으면 일에서 엑스 제곱을 이 팩토리얼로 나눈 값을 빼고, 다시 엑스의 네제곱을 사 팩토리얼로 나눈 값을 더하는 식으로 이어집니다.'),
         ('그래서 자연상수 이의 지수를 아이 엑스로 둔 값은',
          '그래서 자연로그의 밑에 아이 엑스를 지수로 올린 값은')],
}
prefix=('비시지의 풍차에서는','풍차의 날개를')
anchorChanges={('028','모두 마이너스 이'):'마이너스 이가 됩니다',('031','초기 십 피트'):'출발 높이 십 피트'}
# Verify source values independently before touching the frozen inputs.
v=150;theta=math.radians(40);vx=v*math.cos(theta);vy=v*math.sin(theta);t=vy/32
assert (round(t,3),round(vx*t,2),round(10+vy**2/64,2),round(2*t,3),round(2*vx*t,2))==(3.013,346.22,155.26,6.026,692.44)
assert 7-9==-2 and (math.sin(6.5*math.pi)-math.sin(5.5*math.pi))/(6.5-5.5)==2 and 2*(-1)==-2
names=['script/narration.ko.json','script/draft-narration.ko.json','planning/scene-bindings.json','planning/production-plan.json','planning/bilingual-caption-map.json','planning/script-integration.json']
backup=local/'worked-values-v1-inputs';assert not backup.exists()
oldscript=read(P/names[0]);newscript=json.loads(json.dumps(oldscript))
for scene in newscript['scenes']:
 sid=scene['id']
 if sid not in changes:continue
 line=scene['lines'][0]
 for a,b in changes[sid]:assert line.count(a)==1,(sid,a);line=line.replace(a,b)
 assert len(line.split('. '))==len(scene['lines'][0].split('. '))
 scene['lines'][0]=line
backup.mkdir()
for n in names:
 dest=backup/n;dest.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(P/n,dest)
proof=[]
for name in names[:4]:
 f=P/name;s=f.read_text(encoding='utf-8');before=sha(f)
 for pairs in changes.values():
  for a,b in pairs:s=s.replace(a,b)
 # The abbreviated old game prefix is a field of its own.
 s=s.replace('"'+prefix[0]+'"','"'+prefix[1]+'"')
 f.write_text(s,encoding='utf-8');proof.append(dict(file=name,before=before,after=sha(f)))
ko=read(P/names[0]);digest=sha(P/names[0])
b=read(P/names[2])
for row,s in zip(b['scenes'],ko['scenes']):
 assert row['speech']==s['lines'][0] and row['id']==s['id']
 for a in row['speechPhaseAnchors']:
  a['phrase']=anchorChanges.get((row['id'],a['phrase']),a['phrase'])
  if row['speech'][a['character']:].startswith(a['phrase']):continue
  assert row['speech'].count(a['phrase'])==1,(row['id'],a['phrase'])
  a['character']=row['speech'].index(a['phrase'])
 if row.get('actualGamePart'):assert row['actualGamePart']['speechTarget']['prefixKo'] in row['speech']
b.update(sourceNarrationSha256=digest);save(P/names[2],b)
d=read(P/names[3]);d['scriptReadthrough']['koSha256']=digest;save(P/names[3],d)
d=read(P/names[-1]);d['readThrough']['koSha256']=digest
d.setdefault('preVoiceCorrections',[]).append(dict(at=datetime.now(timezone.utc).isoformat(),scenes=sorted(changes),reason='Actual ASR highlighted numeric/unit/operator or proper-name ambiguity; clarify spoken examples without changing source math. No ASR transcription treated as proof of an audible fault.',sourceMath='4.5/5.5/6.5 s extrema; x(9)=-2; a=-2; 1/2; projectile xy and same-height flight verified numerically; exponential base e rather than 2.',sourceOrderPreserved=True,oldInputs=str(backup.relative_to(R)),files=proof,humanListening=False))
save(P/names[-1],d)
subprocess.run(['python','-X','utf8',str(P/'production/build-bilingual-map.py')],check=True,cwd=R)
new.mkdir();(new/'chunks').mkdir();copied=[]
for f in sorted((old/'chunks').glob('*.wav')):
 if f.name[:3] in changes:continue
 dst=new/'chunks'/f.name;shutil.copy2(f,dst);assert sha(f)==sha(dst);copied.append(dict(file=f.name,sha256=sha(f)))
assert len(copied)==40-len(changes)
m=read(P/'production/tts-manifest.json');m['tts']['outputDir']=new.relative_to(R).as_posix()
m['retake']=dict(scenes=sorted(changes),reason='Clarify worked values, units and algebra without changing teaching order.',preservedOriginal=old.relative_to(R).as_posix())
save(P/'production/tts-manifest-audio-v2.json',m);save(new/'retake-plan.json',dict(retakeScenes=sorted(changes),copiedUnchangedRawTakes=copied,originalPreserved=True,humanListening=False))
print(len(changes),'targeted retakes;',len(copied),'identical raw takes')
