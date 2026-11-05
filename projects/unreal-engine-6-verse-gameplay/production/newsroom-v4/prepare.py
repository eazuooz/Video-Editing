from pathlib import Path
import json
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/newsroom-v4';L.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(R).as_posix()
groups=[[(k.strip(),e.strip()) for k,e in (line.split(' | ') for line in block.splitlines())] for block in (H/'passages.txt').read_text(encoding='utf-8').strip().split('\n\n')]
for lang in ('ko','en'):
 save(H/f'added.{lang}.json',{'scenes':[{'id':f'{i+1:02d}','title':('UE5 Actor and Pawn','Effect of the Tokyo announcement')[i],'lines':[' '.join(s[lang=='en'] for s in g)]} for i,g in enumerate(groups)]})
m=read(P/'production/newsroom-v3/tts-manifest.json');m['revision']='newsroom-v4';m['paths']={'script':rel(H/'added.ko.json'),'scriptEn':rel(H/'added.en.json')};m['tts'].update(outputDir=rel(L/'voice'),filenameStem='pawn');m['delivery']['localStorageRoot']=rel(L/'delivery')
save(H/'tts-manifest.json',m)
