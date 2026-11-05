from pathlib import Path
import json
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/unreal-kit-v2'
read=lambda f:json.loads(f.read_text(encoding='utf-8-sig'))
def save(f,d):f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(f):return f.relative_to(R).as_posix()
pairs=[[(k.strip(),e.strip()) for k,e in (line.split(' | ') for line in block.splitlines())] for block in (H/'commentary-pairs.txt').read_text('utf-8').strip().split('\n\n')]
titles=['보이는 걷기 지시','두 시점의 참고 포즈','정지 동작의 지지발','방향 전환 검수']
for lang in ['ko','en']:
 save(H/f'added.{lang}.json',{'scenes':[{'id':f'{i+1:02}','title':titles[i],'lines':[' '.join(pair[lang=='en'] for pair in group)]} for i,group in enumerate(pairs)]})
m=read(R/'projects/animation-breaking-down-attack-animations/production/grid-v1/tts-manifest.json');m.update(slug=P.name,title=read(P/'project.json')['title'],revision='unreal-kit-v2',sourceReference='https://www.youtube.com/watch?v=fV8xIP480qk',sources=['https://dev.epicgames.com/documentation/en-us/unreal-engine/game-animation-sample-project-in-unreal-engine']);m['titles']={'ko':m['title']};m['authorization']=rel(H/'stage-plan.json')
m['tts'].update(outputDir=rel(L/'voice'),filenameStem='additions');m['paths']={'script':rel(H/'added.ko.json'),'scriptEn':rel(H/'added.en.json')};m['delivery']={'localStorageRoot':rel(L/'delivery')};m['editing']={'revisionScope':'preserve the existing actual gameplay and the prior scope-specific ratio; replace the native demonstration shots.'}
save(H/'tts-manifest.json',m)
