"""Independent current narration sources and measured black render entry; prepared only."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
MC=ROOT/'motion-canvas/src/projects/presenting-game-scores'
planp=BASE/'measured-timeline-candidate-v7.json';plan=read(planp)
voices=read(BASE/'current-voice-selection-v7.json')
native=read(BASE/'measured-native-inputs-execution-v8.json')
assert native['exitCode']==0 and native['actualOuterExitCode']==0 and native['completed']==12
assert native['planSha256']==sha(planp)
out=MC/'measured-scenes-v7';assert not out.exists();out.mkdir()
engine=MC/'measured-score-explanation-v7.tsx';assert not engine.exists()
text=(MC/'spatial-score-explanation.tsx').read_text('utf-8')
text=text.replace('export function* scoreExplanation(view:View2D,id:string,timing:ExplanationTiming){',
'''export function* scoreExplanationMeasuredV7(view:View2D,requestedId:string,timing:ExplanationTiming){
 const snapshot=requestedId==='06-observed-2920'?1:requestedId==='06-observed-141'?2:0;
 const id=snapshot?'06-relative-gap':requestedId;
 if(!timing.measured)throw Error('Measured current voice timing required');''')
text=text.replace('const phase=(i:number,d=1.3)=>smooth((t()-timing.paragraphStarts[i])/d);',
 'const phase=(i:number,d=1.3)=>snapshot&&i===2?(snapshot===1?0:1):smooth((t()-timing.paragraphStarts[i])/d);')
text=text.replace("<Txt text={HEADINGS[id][1]} y={-306}",
 "<Txt text={snapshot===1?'앞서 본 같은 27줄의 순간':snapshot===2?'다른 관찰 순간: 줄 수와 점수의 앞섬':HEADINGS[id][1]} y={-306}")
text=text.replace("note('서로 다른 관찰 순간 · 중간 점수 차이가 최종 승리는 아닙니다');",
 "note(snapshot===1?'같은 줄 수 · 다른 점수 · 차이 2,920':snapshot===2?'29줄 / 32줄 · 왼쪽 +141 · 최종 승리와 구분':'서로 다른 관찰 순간 · 중간 점수 차이가 최종 승리는 아닙니다');")
text=text.replace('// Prepared timing only: final timing replaces each independent scene contract\n // after current-hash narration and source allocation, without cutting voice.',
 '// Current sample-measured candidate timing. Final encoded caption/motion pixels\n // and final mixed ASR remain mandatory gates; this is a silent input renderer.')
engine.write_text(text,'utf-8')
black=[s for s in plan['segments'] if s['role']=='explanation']
imports=[];files=[]
for index,s in enumerate(black):
    path=out/(s['id']+'.tsx')
    timing=dict(durationSeconds=s['frames']/60,paragraphStarts=s['paragraphMotionStarts'],measured=True)
    path.write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {scoreExplanationMeasuredV7} from '../measured-score-explanation-v7';\n"
        +"// Selected measured explanation input; silent render, all final pixel gates pending.\n"
        +f"export default makeScene2D(function* (view) {{yield* scoreExplanationMeasuredV7(view,{json.dumps(s['diagram'])},{json.dumps(timing)});}});\n",'utf-8')
    imports.append(f"import scene{index:02} from './measured-scenes-v7/{s['id']}?scene';")
    files.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),segmentId=s['id'],frames=s['frames']))
entry=MC/'measured-black-v7.ts';assert not entry.exists()
entry.write_text('\n'.join(["import {makeProject} from '@motion-canvas/core';"]+imports)+
    "\nexport default makeProject({name:'presenting-game-scores-measured-black-v7',scenes:["+
    ','.join(f'scene{i:02}' for i in range(len(black)))+"]});\n",'utf-8')

# Each script scene retains an independent editable MC source. The authoring
# previews are not additional final footage/quota; the measured segment plan
# is the sole compositor authority for the final interleaving.
native_by_id={r['id']:r for r in native['results']}
guide_sources={'11-observe-separate-updates':'classic-01','12-observe-equal-quantity':'classic-02',
 '13-observe-action-label':'modern-01','14-observe-notice-and-record':'modern-02',
 '18-observe-stable-reading':'classic-04','19-observe-reading-audit':'modern-05',
 '24-observe-named-fields-clear-start':'classic-03'}
authoring=[];author_imports=[]
for index,r in enumerate(voices['scenes']):
    sid=r['id'];path=out/(sid+'.tsx')
    if sid in guide_sources:
        source=native_by_id[guide_sources[sid]]
        url='/@fs/'+(ROOT/source['path']).as_posix()
        body="import {makeScene2D,Video} from '@motion-canvas/2d';\nimport {waitFor} from '@motion-canvas/core';\n"
        body+=f"export default makeScene2D(function* (view) {{view.add(new Video({{src:{json.dumps(url)},width:1920,height:1080,play:true,loop:false,playbackRate:1}}));yield* waitFor({r['seconds']});}});\n"
        kind='actual guide authoring preview; not extra final source reuse'
    else:
        diagram='06-observed-2920' if sid.startswith('15-') else '06-observed-141' if sid.startswith('16-') else sid
        phases=[0,1.5,3.5] if sid.startswith(('15-','16-')) else [n/24000 for n in plan['paragraphBoundaries'][sid][:-1]]
        if sid=='06-relative-gap':phases=[0,3.775,8.145]
        timing=dict(durationSeconds=r['seconds'],paragraphStarts=phases,measured=True)
        body="import {makeScene2D} from '@motion-canvas/2d';\nimport {scoreExplanationMeasuredV7} from '../measured-score-explanation-v7';\n"
        body+=f"export default makeScene2D(function* (view) {{yield* scoreExplanationMeasuredV7(view,{json.dumps(diagram)},{json.dumps(timing)});}});\n"
        kind='independent measured narrative authoring preview; selected render intervals use candidate segment plan'
    path.write_text('// Independent editable script scene. Authoring source only; final interleaving is measured-timeline-candidate-v7.json.\n'+body,'utf-8')
    authoring.append(dict(id=sid,path=path.relative_to(ROOT).as_posix(),sha256=sha(path),seconds=r['seconds'],scope=kind))
    author_imports.append(f"import scene{index:02} from './measured-scenes-v7/{sid}?scene';")
author_entry=MC/'current19-authoring-v7.ts';assert not author_entry.exists()
author_entry.write_text('\n'.join(["import {makeProject} from '@motion-canvas/core';"]+author_imports)+
    "\n// Authoring preview only, never the final actual60:explanation40 compositor.\n"
    +"export default makeProject({name:'presenting-game-scores-current19-authoring-v7',scenes:["+
    ','.join(f'scene{i:02}' for i in range(19))+"]});\n",'utf-8')

# Reuse the registered live9251 entry through module hot reload. Preserve its
# prior exact source and rendered prototype media, without restarting Vite.
live=MC/'black-explanation-preflight-v1.ts';history=MC/'black-explanation-preflight-history-v3.ts'
assert not history.exists();old=live.read_bytes();history.write_bytes(old)
live.write_text("// Measured current input render; prior prototype entry preserved in black-explanation-preflight-history-v3.ts.\nexport {default} from './measured-black-v7';\n",'utf-8')
proof=dict(schemaVersion=7,preparedAt=datetime.now(timezone.utc).isoformat(),plan=planp.relative_to(ROOT).as_posix(),
 planSha256=sha(planp),currentNarratives=19,independentNarrativeSources=authoring,
 measuredBlackSegments=files,totalBlackFrames=7333,renderEntry=entry.relative_to(ROOT).as_posix(),
 renderEntrySha256=sha(entry),engine=engine.relative_to(ROOT).as_posix(),engineSha256=sha(engine),
 priorPrototypeEntry=history.relative_to(ROOT).as_posix(),priorPrototypeEntrySha256=sha(history),
 priorPrototypeMediaPreserved=True,liveRegisteredEntry=live.relative_to(ROOT).as_posix(),
 liveRegisteredEntrySha256=sha(live),serverRestarted=False,newRenderStarted=False,
 authoringPreviewCountedAsAdditionalActualFootage=False,preparedOnly=True,
 measuredAnimatedPixelsApproved=False,allFinalPixels=False,finalTimingApproved=False,finalMixedAsrApproved=False,
 newImagesGitAdded=0,sourceAudio=False)
p=BASE/'measured-mc-preparation-v7.json';assert not p.exists();p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(independentNarrativeScenes=19,selectedBlackSegments=12,blackFrames=7333,
 priorPrototypeMediaPreserved=True,serverRestarted=False,preparedOnly=True)))
