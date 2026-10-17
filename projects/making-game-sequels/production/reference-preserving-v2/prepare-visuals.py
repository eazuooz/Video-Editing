from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';L=P/'production/local/reference-preserving-v2';A=L/'assets';A.mkdir(exist_ok=True);M=R/'motion-canvas/src/projects/making-game-sequels/revision-v2'
shots=[('gt-turn','gt7-sunday',32),('pikmin-task','pikmin4-day2',48),('pikmin-wall','pikmin4-day2',233),('pikmin-open','pikmin4-day2',249),('wiiu-fight','smash-wiiu',64),('ultimate-fight','smash-ultimate',21),('oatchi-before','pikmin4-day2',330),('oatchi-work','pikmin4-day2',334),('oatchi-result','pikmin4-day2',344)]
for name,source,sec in shots:
 target=A/(name+'.png')
 if not target.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(sec),'-i',str(L/'media'/(source+'.mp4')),'-frames:v','1',str(target)],check=True)
(A/'provenance.json').write_text(json.dumps([dict(name=n,source=s,time=t,classification='explanation screenshot; not actual footage seconds') for n,s,t in shots],indent=2)+'\n')
kinds=['overview','layers','work','test','teams','experience','oatchi','value','conclusion']
for i,kind in enumerate(kinds,1):
 (M/f'scene-{i:02}.tsx').write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from './visuals';\nexport default makeScene2D(function*(view){yield* lesson(view,"+json.dumps(kind)+",{duration:12,cues:[0,1.5,3.5,5.5,7.5]});});\n",encoding='utf8')
(M/'project.ts').write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(f"import s{i} from './scene-{i:02}?scene';" for i in range(1,10))+"\nexport default makeProject({scenes:["+','.join('s'+str(i) for i in range(1,10))+']});\n',encoding='utf8')
plan=json.loads((P/'planning/chapter-plan.json').read_text(encoding='utf8'))
for scene in plan['currentRevision']['scenes']:scene['sceneSaveStatus']='saved; initial visual timing is preflight only, production timing follows approved PCM'
(P/'planning/chapter-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('9 editable scenes and9 independently sourced screenshots prepared')
