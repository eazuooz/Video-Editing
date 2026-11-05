"""Prepare five new scenes without regenerating the delivered first twelve."""
from pathlib import Path
import json,subprocess,sys,time
P=Path(__file__).resolve().parents[1];R=P.parents[1]
S=P/'script/engine-comparison-v2';O=P/'production/local/engine-comparison-v2'
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(R).as_posix()
titles=['이래도 언리얼을 선택할까?','고도는 상용 게임도 무료','유니티는 팀과 좌석을 본다','같은 게임의 엔진 비용','우리 팀에 남는 선택']
alias={'120만':'백이십만','100만':'백만','20만':'이십만','1만':'일만','4,620':'사천육백이십','2,310':'이천삼백십','12개월':'십이 개월','0원':'영 원','0달러':'영 달러','5퍼센트':'오 퍼센트','1년':'일 년','GDScript':'지디 스크립트','C#':'씨 샵','PC':'피씨','MIT':'엠 아이 티','엔진 5':'엔진 파이브'}
raw=[[(line.split(' | ')[0],line.split(' | ')[1]) for line in block.splitlines()] for block in (S/'caption-pairs.txt').read_text(encoding='utf-8').strip().split('\n\n')]
assert len(raw)==len(titles)==5
def phon(text):
    text=text.replace('UEFN','유 이 에프 엔')
    for a,b in alias.items():text=text.replace(a,b)
    return text
for lang in ['ko','en','spoken-ko']:
    items=[]
    for i,group in enumerate(raw):
        txt=' '.join(pair[lang=='en'] for pair in group)
        items.append(dict(id=str(i+13),title=titles[i],lines=[phon(txt) if lang=='spoken-ko' else txt]))
    save(S/f'narration.{lang}.json',{'scenes':items})
m=json.loads((P/'project.json').read_text(encoding='utf-8'))
m['paths']={'script':rel(S/'narration.spoken-ko.json'),'scriptEn':rel(S/'narration.en.json')}
m['tts']['outputDir']=rel(O/'voice');m['tts']['filenameStem']='comparison';m['revision']='engine-comparison-v2'
manifest=P/'production/engine-comparison-v2-voice.json';save(manifest,m)
base=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))['scenes']
(S/'전체대본.md').write_text('# 블루프린트가 사라지면 언리얼을 왜 쓸까? | 언리얼 6·고도·유니티 비교\n\n'+'\n\n'.join([s['lines'][0] for s in base]+[' '.join(k for k,e in group) for group in raw])+'\n',encoding='utf-8')
if '--run' in sys.argv:
    # Complete A02's ordered MRQ reservation before starting another Qwen session.
    capture=R/'projects/animation-exaggeration/production/local/fighters-v4-kula-lili/unreal'
    while len(list(capture.glob('A02-E*-capture.json')))<6:time.sleep(5)
    subprocess.run([sys.executable,'-u','-X','utf8','qwen3-tts/render_narration.py','--project',P.name,'--manifest',rel(manifest),'--batch-size','1'],cwd=R,check=True)
