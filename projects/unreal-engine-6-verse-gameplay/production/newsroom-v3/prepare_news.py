"""Create the newsroom script and independent Qwen input for this revision."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent
P=H.parents[1]; R=P.parents[1]; L=P/'production/local/newsroom-v3'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(R).as_posix()
titles=['블루프린트 작업 화면','6월 시카고 로드맵','11월 도쿄 발표','포트나이트의 전환','시카고 에디터 시연','언리얼을 계속 쓰는 이유','고도와 유니티의 조건','출시 뒤 엔진 비용']
aliases={'언리얼 엔진 6':'언리얼 엔진 식스','엔진 5.8':'엔진 오 점 팔','엔진 5.9':'엔진 오 점 구','엔진 5':'엔진 파이브','UEFN':'유 이 에프 엔','C++':'씨 플러스 플러스','C#':'씨 샵','Verse':'버스','MCP':'엠 씨 피','AI':'에이 아이','MIT':'엠 아이 티','1.5배':'한 배 반','4배':'네 배','2027년':'이천이십칠 년','11월 3일':'십일월 삼일','11월':'십일월','6월':'유월','12개월':'십이 개월','120만':'백이십만','100만':'백만','20만':'이십만','1만':'일만','0원':'영 원','2,310':'이천삼백십','5퍼센트':'오 퍼센트'}
groups=[[(s.split(' | ')[0],s.split(' | ')[1]) for s in t.splitlines()] for t in (H/'caption-pairs.txt').read_text(encoding='utf-8').strip().split('\n\n')]
assert len(groups)==len(titles)
for lang in ['ko','en','spoken-ko']:
 scenes=[]
 for i,g in enumerate(groups):
  line=' '.join(row[lang=='en'] for row in g)
  if lang=='spoken-ko':
   for a,b in aliases.items():line=line.replace(a,b)
  scenes.append({'id':str(i+1).zfill(2),'title':titles[i],'lines':[line]})
 dump(H/f'narration.{lang}.json',{'scenes':scenes})
tem=read(P/'production/engine-comparison-v2-voice.json')
tem.update(revision='newsroom-v3',title='블루프린트가 사라지면 언리얼을 왜 쓸까? | 두 발표로 본 언리얼 엔진 6')
tem['titles']={'ko':tem['title']};tem['tts'].update(outputDir=rel(L/'voice'),filenameStem='narration')
tem['paths']={'script':rel(H/'narration.spoken-ko.json'),'scriptEn':rel(H/'narration.en.json')}
tem['delivery']['localStorageRoot']=rel(L/'delivery')
dump(H/'tts-manifest.json',tem)
