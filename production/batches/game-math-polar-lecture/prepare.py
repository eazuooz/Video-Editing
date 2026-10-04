"""Create only the explicitly requested two-part lecture; preserve the sample."""
from pathlib import Path
import json,sys,shutil,subprocess
ROOT=Path(__file__).resolve().parents[3]
slug=sys.argv[1];all_data=json.loads((Path(__file__).parent/'lesson-data.json').read_text(encoding='utf8'));all_data.update(json.loads((Path(__file__).parent/'part2-data.json').read_text(encoding='utf8')));data=all_data[slug]
base=ROOT/'projects'/slug;mc=ROOT/'motion-canvas/src/projects'/slug;man=ROOT/'manim/projects'/slug
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
candidate=ROOT/'tmp'/('polar-2d-candidate.json' if data['part']==1 else 'polar-3d-candidate.json')
subprocess.run(['node','scripts/review-video-duplicates.cjs',slug,'--candidate-file',str(candidate),'--check'],cwd=ROOT,check=True)
assert not (base/'project.json').exists(),'Never reset an existing lecture project'
m=json.loads((ROOT/'projects/game-math-polar-sample/project.json').read_text(encoding='utf8'))
m=json.loads(json.dumps(m).replace('game-math-polar-sample',slug))
c=json.loads(candidate.read_text(encoding='utf8'));m['titles']={'ko':c['titleKo'],'en':c['titleEn']}
m['status']='full-lecture-production';m.pop('finalRender',None);m['video']['durationSeconds']=None
m['approvals']={'production':'2026-10-04 user requested the full chapter, two videos, actual40/explanation60, no background music; reuse approved narrator.','humanListening':'pending','privateUpload':'Authorized by user production defaults; never publish or schedule.'}
m['audio'].update(backgroundMusic={'enabled':False,'required':False,'approvalStatus':'user-requested-no-background-music','approvedAt':'2026-10-04','approvalEvidence':'이번에는 강의 영상이라서 배경음악은 없애줘야해'},bgmPlacement='none',musicFallbackScenes=[],mixStatus='awaiting-narration-only-mix',sourceAudioPolicy='Narration only throughout this lecture. No background music, game OST, third-party speech or source sound is mixed.')
m['membershipOutro']['appliedToFinal']=False
ed=m['editing'];ed['ratioPolicy']='User lecture exception: actual existing-game footage40% / original explanation60% of body; exclude branding2s and membership10s.';ed['ratioPolicyVersion']='full-lecture-40-60-20261004';ed['ratioException']['scope']='Two full polar-coordinate lectures requested on2026-10-04; completed sample preserved.'
for k in list(ed):
 if k.startswith('actual') or k=='finalBodyFrames':ed.pop(k)
ed['timingStatus']='awaiting-measured-speech';ed['openingOverview'].update(question=c['viewerQuestion'],orderedSteps=data['scenes'][0]['beats'][1:],reviewedBeforeTts=True)
m['paths']['scriptEn']=f'projects/{slug}/script/narration.en.json'
m['paths']['productionData']='production/batches/game-math-polar-lecture/'+('lesson-data.json' if data['part']==1 else 'part2-data.json')
m['paths']['productionBuilder']='production/batches/game-math-polar-lecture/build.py'
m['lecture']={'part':data['part'],'totalParts':2,'baseline':'game-math-polar-sample','sourceNotion':'https://app.notion.com/p/3e10b1ffa61e819389adc39e17f9bc88','coveredSections':data['sourceSections'],'verbatimReproduction':False,'backgroundMusic':False}
write(base/'project.json',m);write(base/'planning/candidate.json',c)
for lang in ['ko','en']:
 write(base/f'script/narration.{lang}.json',{'title':m['titles'][lang],'scenes':[{'id':s['id'],'title':s['title'],'lines':s[lang]} for s in data['scenes']]})
src={'id':'eDL84EC5mkQ','game':'Brotato','uploader':'MezzyGameplay','url':'https://www.youtube.com/watch?v=eDL84EC5mkQ','file':'shared/output/game-math-polar-sample/sources/eDL84EC5mkQ.mp4','permission':'YouTube Creative Commons Attribution metadata and free-to-use uploader description inspected; attribution recorded here and on footage. Game-IP publication review remains pending.','priorUse':'Reviewed as a rejected candidate in the sample; no counted footage from this source in any existing project.','sourceAudioUsed':False}
if data['part']==2:src.update(id='WJVRoLR6KvY',game='Descenders',url='https://www.youtube.com/watch?v=WJVRoLR6KvY',file='shared/output/game-math-polar-lecture/sources/WJVRoLR6KvY.mp4',priorUse='No matching source ID or game title found in existing project source history. Fresh recording for this lecture.',permission='Uploader YouTube metadata explicitly Creative Commons Attribution license (reuse allowed), inspected2026-10-04. This clears the recording permission signal, not independently all game IP.')
cuts=[{'scene':s['id'],'in':s['in'],'maxSeconds':s['maxSeconds'],'duration':None,'action':'Continuous live wave combat: player translation, attached weapons and outgoing shots','focus':s['focus'],'claim':s['claim'],'connection':'Adjacent explanatory scene models this observed relative direction/displacement; no proprietary implementation claim.','inspection':'All selected windows inspected at3s intervals before narration; menus and wave completion excluded.','sourceFile':src['file']} for s in data['scenes'] if s['kind']=='actual']
if data['part']==2:
 for cut in cuts:cut.update(action='Actual downhill bicycle riding, jumps and a following viewpoint; loading, menus and results excluded',credit='Descenders - MezzyGameplay')
write(base/'sources/gameplay-cuts.json',{'reviewedBeforeNarration':True,'reviewedAt':'2026-10-04','source':src,'cuts':cuts})
write(base/'sources/game-candidates.json',{'reviewedAt':'2026-10-04','candidates':[{'game':src['game'],'selected':True,'source':src['id'],'reason':'Fresh inspected intervals visibly match relative position/direction and the chapter; no invented gameplay.'},{'game':'Enter the Gungeon','selected':False,'reason':'Already used in the three-minute baseline. Prefer fresh games in the full lecture.'},{'game':'Clustertruck','selected':False,'reason':'CC permission checked and recording inspected; frequent level/menu interruptions make a sustained lecture observation harder than Descenders.'},{'game':'Combat Master','selected':False,'reason':'Uploader title alone says no copyright; no explicit license/description permission was established.'}]})
write(base/'sources/SOURCES.md',f'# 출처와 검토\n\n- 사용자 Notion 극좌표계7장: {m["lecture"]["sourceNotion"]}.7.1~7.5를 대조하고 쉬운 예제로 다시 설명. 원문 전체를 낭독하지 않는다.\n- 수학 검증: https://gamemath.com/book/polarspace.html\n- 실제 자료: {src["url"]}, {src["game"]}, {src["uploader"]}. {src["permission"]}\n- CC attribution: {src["uploader"]}, {src["url"]}, https://creativecommons.org/licenses/by/4.0/ ; edited excerpts, source audio excluded. YouTube metadata does not independently clear game IP.\n- 원본 회원·로고와 승인된 개인 내레이터는 기존 자산 그대로. 개인 음성참조는 Git 제외.\n- 이번 강의는 사용자 요청으로 BGM 없음. Nimbus는 샘플에만 남기고 이 강의 입력에는 사용하지 않는다.\n')
write(base/'README.md',f'# {m["titles"]["ko"]}\n\n사용자가 요청한 극좌표계 전체 챕터의 {data["part"]}/2편. 기존3분 샘플은 보존한다. 실제 게임40%·Manim 설명60%, 고양이2초·회원10초 제외. 강의 집중을 위해 배경음악과 게임 원음을 제외하고 승인된 내레이션만 사용한다.\n\n재제작: `python production/batches/game-math-polar-lecture/build.py {slug} <stage>`. Qwen 장면 단위 합성 및 Whisper 받아쓰기/자막 정렬을 먼저 완료한다. 사람의 전체 청취와 공개 권리 검토는 별도 대기 상태로 보존한다.\n')
write(base/'planning/outline.md','# 두 편 구성과 도입 검토\n\n'+ '\n'.join(f'- {s["id"]} {s["kind"]}: {s["title"]}' for s in data['scenes'])+'\n\n도입: 핵심 질문·시청 후 얻는 점·실제 순서를 독립 한영4문장으로 작성하고 TTS 전에 본론과 대조했다. 실제 사례40%, 설명60%; 실측 음성을 보존하며 필요한 실제 컷을 확보한다. 반복·느린 재생으로 비중을 채우지 않는다.\n')
shutil.copy2(ROOT/'projects/game-math-polar-sample/planning/manim-comparison.md',base/'planning/manim-comparison.md')
write(base/'planning/coverage-audit.json',{'source':'Notion chapter7 complete7.1–7.5','scope':'Full chapter split into two complementary lectures, not a longer sample','covered':data['sourceSections'],'examples':'Original guided examples and game observations; not a verbatim list of every textbook exercise','coreClaimsRetained':True,'otherPart':2 if data['part']==1 else 1,'noBgm':True,'baselinePreserved':True})
mc.mkdir(parents=True,exist_ok=True)
sourceplayer=ROOT/'motion-canvas/src/projects/game-math-polar-sample/play-clip.tsx'
if not sourceplayer.exists():sourceplayer=ROOT/'motion-canvas/src/projects/game-math-polar-sample/scenes/play-clip.tsx'
write(mc/'scenes/play-clip.tsx',sourceplayer.read_text(encoding='utf8').replace('game-math-polar-sample',slug))
imports=["import {makeProject} from '@motion-canvas/core';","import audio from './assets/final-mix.wav';"]
entries=[('intro','brand-intro',2),*[(f's{s["id"]}',f'scene{s["id"]}',30) for s in data['scenes']],('outro','membership-outro',10)]
for var,file,duration in entries:
 imports.append(f"import {var} from './scenes/{file}?scene';")
 clip='intro' if var=='intro' else 'outro' if var=='outro' else var[1:]
 write(mc/f'scenes/{file}.tsx',f"import {{makeScene2D}} from '@motion-canvas/2d';\nimport {{playScene}} from './play-clip';\nimport clip from '../assets/{clip}.mp4';\nexport default makeScene2D(function*(view) {{yield* playScene(view,clip,'{clip}');}});\n")
write(mc/'project.ts','\n'.join(imports)+f"\nexport default makeProject({{name:'{slug}',audio,scenes:[{','.join(v for v,_,_ in entries)}]}});\n")
write(man/'scene.py',f"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parents[1]/'game-math-polar-lecture'))\nfrom lesson import make_scenes\nglobals().update(make_scenes('{slug}',__name__))\n")
registry=ROOT/'motion-canvas/projects.json';reg=json.loads(registry.read_text(encoding='utf8'))
if isinstance(reg,list):reg.append(f'./src/projects/{slug}/project.ts')
else:raise ValueError('Inspect registry schema')
write(registry,reg)
print('Prepared',slug,len(data['scenes']),'independent scenes; no BGM')
