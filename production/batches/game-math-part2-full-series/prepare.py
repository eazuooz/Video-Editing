"""Prepare one reviewed lecture; preserve completed projects and all media."""
from pathlib import Path
import json,sys,shutil,subprocess,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).parent
slug=sys.argv[1]
from production_control import require_current_authorization
require_current_authorization(slug,'project preparation')
data=json.loads((BATCH/'lessons'/f'{slug}.json').read_text(encoding='utf8'))
candidate=BATCH/'candidates'/f'{slug}.json';c=json.loads(candidate.read_text(encoding='utf8'))
subprocess.run(['node','scripts/review-video-duplicates.cjs',slug,'--candidate-file',str(candidate),'--check'],cwd=ROOT,check=True)
base=ROOT/'projects'/slug;mc=ROOT/'motion-canvas/src/projects'/slug;man=ROOT/'manim/projects'/slug
assert not (base/'project.json').exists(),'Resume existing work; never overwrite a project manifest'
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ref=json.loads((ROOT/'projects/game-math-polar-2d/project.json').read_text(encoding='utf8'))
m={k:ref[k] for k in ['schemaVersion','delivery','membershipOutro','visualStyle','visualStyleGuide','editing','video','engines','tts','audio','paths','publishing','rendererDecision']}
m=json.loads(json.dumps(m).replace('game-math-polar-2d',slug))
m.update(slug=slug,status='full-lecture-production',titles={'ko':'게임수학 Part 2 · '+c['titleKo'],'en':'Game Math Part 2 · '+c['titleEn']},publishReady=False)
m['approvals']={'production':'2026-10-06: 2파트끝날때까지 쭉 나머지도 전부 진행해줘; preserve accepted40:60 lecture format, no BGM, approved narrator, full chapters split for concentration','humanListening':'pending','visualPixelReview':'pending','privateUpload':'Authorized by user production defaults; PRIVATE only; no public publishing or scheduling'}
m['video']['durationSeconds']=None;m['membershipOutro']['appliedToFinal']=False
m['audio']['mixStatus']='awaiting-narration-only-mix'
m['editing']={k:v for k,v in m['editing'].items() if not k.startswith('actual') and k!='finalBodyFrames'}
ed=m['editing'];ed.update(timingStatus='awaiting-measured-speech',explanationStyle='Independent Manim Community white2.5D/3D diagrams and worked calculations',ratioPolicyVersion='part2-full-series-40-60-20261005')
ed['ratioException']['scope']='All remaining Game Math PART2 chapters8–13, explicitly requested in the same approved lecture format on2026-10-05'
ed['exampleInterleaving']['reviewStatus']='planned-from-inspected-intervals-before-narration'
ed['openingOverview'].update(question=c['viewerQuestion'],outcome='Understand and calculate the viewer question using the covered source sections',orderedSteps=data['scenes'][0]['beats'][1:],reviewedBeforeTts=True,narrationSeconds=None)
m['tts']['maxNewTokens']=1536
m['paths'].update(productionData=f'production/batches/game-math-part2-full-series/lessons/{slug}.json',productionBuilder=f'projects/{slug}/production/build.py',sharedLectureBuilder='production/batches/game-math-part2-full-series/build.py',sharedManimLesson=f'manim/projects/game-math-part2-full-series/{data.get("renderModule","lesson")}.py')
m['lecture']={'chapter':data['chapter'],'part':data['part'],'totalParts':data['totalParts'],'baseline':'game-math-polar-2d and game-math-polar-3d','sourceNotion':c['sourceNotion'],'coveredSections':data['sourceSections'],'contract':data.get('contract',{}),'verbatimReproduction':False,'backgroundMusic':False}
write(base/'project.json',m);write(base/'planning/candidate.json',c)
for lang in ['ko','en']:write(base/f'script/narration.{lang}.json',{'title':m['titles'][lang],'scenes':[{'id':s['id'],'title':s['title'],'lines':s[lang]} for s in data['scenes']]})
sourceindex=json.loads((BATCH/'footage-index.json').read_text(encoding='utf8'));cuts=[]
for s in data['scenes']:
 if s['kind']!='actual':continue
 src=sourceindex[s['sourceId']];assert src['reviewedBeforeNarration'] and src['recordingPermissionObserved']
 cuts.append({'scene':s['id'],'in':s['in'],'maxSeconds':s['maxSeconds'],'duration':None,'sourceId':s['sourceId'],'sourceFile':src['file'],'sourceSegments':s['sourceSegments'],'credit':src['game']+' - '+src['uploader'],'licenseLabel':src['licenseLabel'],'focus':s['focus'],'claim':s['claim'],'action':src['visibleAction'],'connection':'Concept-matched observation connected to adjacent independent explanation; no proprietary implementation claim','inspection':src['inspection']})
write(base/'sources/gameplay-cuts.json',{'reviewedBeforeNarration':True,'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':{s['sourceId']:sourceindex[s['sourceId']] for s in data['scenes'] if s['kind']=='actual'},'cuts':cuts})
write(base/'sources/game-candidates.json',data['gameCandidates'])
write(base/'sources/SOURCES.md','# 출처와 검토\n\n'+f'- 사용자 Notion: {c["sourceNotion"]}. 핵심 절을 대조하고 쉬운 원래 예제로 설명. 원문 낭독이 아니다.\n'+ '\n'.join(f'- 실제 게임: {v["url"]}, {v["game"]}, {v["uploader"]}. 촬영자 허락: {v["recordingPermissionObserved"]}. 공개 전 게임IP 검토는 별도 대기. 원음 제외, 편집한 발췌, 화면 출처 표기.' for v in {s['sourceId']:sourceindex[s['sourceId']] for s in data['scenes'] if s['kind']=='actual'}.values())+'\n- 승인된 원본 회원·로고·개인 내레이터를 유지한다. BGM과 게임 오디오 없음. 개인 음성참조·영상은 Git 제외.\n')
write(base/'planning/outline.md','# 전체 강의 흐름\n\n'+'\n'.join(f'- {s["id"]} {s["kind"]}: {s["title"]}' for s in data['scenes'])+'\n\n첫 독립 도입에서 핵심 질문·학습 결과·실제 순서를 한영으로 설명한다. 설명 내용을 보존하고 실측 음성에 맞춰 실제 게임40% / 설명60%를 계산한다. 게임을 반복·느리게 재생해 비중을 채우지 않는다.\n')
write(base/'planning/coverage-audit.json',{'source':c['sourceNotion'],'sections':data['sourceSections'],'coverage':data.get('coverage',{}),'coreClaimsRetained':True,'examples':'Original guided calculations and inspected game observations, selected practice exercises; not a verbatim reproduction of every textbook exercise','scope':'Full source chapter divided into complementary topic lectures','overviewReviewedBeforeTts':True,'contract':data.get('contract',{}),'noBgm':True,'baselinePreserved':True})
shutil.copy2(ROOT/'projects/game-math-polar-2d/planning/manim-comparison.md',base/'planning/manim-comparison.md')
write(base/'README.md',f'# {m["titles"]["ko"]}\n\n노션 {data["chapter"]}장의 {data["part"]}/{data["totalParts"]}편. 실제게임40% / 설명60%, BGM 없이 승인된 내레이션만 사용한다. 원래 극좌표계 완성본을 유지한다.\n\n재제작: `python production/batches/game-math-part2-full-series/build.py {slug} <stage>`. 실측 음성과 한영 정렬 뒤 렌더한다. 사람 전체 청취와 공개 권리는 별도 대기.\n')
write(base/'production/build.py',"from pathlib import Path\nimport runpy\nrunpy.run_path(str(Path(__file__).resolve().parents[3]/'production/batches/game-math-part2-full-series/build.py'),run_name='__main__')\n")
mc.mkdir(parents=True,exist_ok=True)
player=ROOT/'motion-canvas/src/projects/game-math-polar-2d/scenes/play-clip.tsx';write(mc/'scenes/play-clip.tsx',player.read_text(encoding='utf8').replace('game-math-polar-2d',slug))
imports=["import {makeProject} from '@motion-canvas/core';","import audio from './assets/final-mix.wav';"]
entries=[('intro','brand-intro'),*[(f's{s["id"]}',f'scene{s["id"]}') for s in data['scenes']],('outro','membership-outro')]
for var,file in entries:
 imports.append(f"import {var} from './scenes/{file}?scene';");clip='intro' if var=='intro' else 'outro' if var=='outro' else var[1:]
 write(mc/f'scenes/{file}.tsx',f"import {{makeScene2D}} from '@motion-canvas/2d';\nimport {{playScene}} from './play-clip';\nimport clip from '../assets/{clip}.mp4';\nexport default makeScene2D(function*(view) {{yield* playScene(view,clip,'{clip}');}});\n")
write(mc/'project.ts','\n'.join(imports)+f"\nexport default makeProject({{name:'{slug}',audio,scenes:[{','.join(v for v,_ in entries)}]}});\n")
write(man/'scene.py',f"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parents[1]/'game-math-part2-full-series'))\nfrom {data.get('renderModule','lesson')} import make_scenes\nglobals().update(make_scenes('{slug}',__name__))\n")
registry=ROOT/'motion-canvas/projects.json';reg=json.loads(registry.read_text(encoding='utf8'));assert isinstance(reg,list)
assert f'./src/projects/{slug}/project.ts' not in reg;reg.append(f'./src/projects/{slug}/project.ts');write(registry,reg)
print('Prepared',slug,len(data['scenes']),'independent scenes; narrator preserved, no BGM',flush=True)
