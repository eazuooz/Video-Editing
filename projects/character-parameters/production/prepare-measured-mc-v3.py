"""Prepare twelve independent black scenes at the current measured PCM clock.

Only black intervals are exported. Every interval evaluates the original
chapter's absolute time, preserving camera/phase state across gameplay cuts.
This prepares render inputs, never a pixel or final timing approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,o):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([NODE,'scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
plan_path=BASE/'measured-timeline-candidate-v3.json';plan=read(plan_path)
assert sha(ROOT/plan['currentVoiceSelection'])==plan['currentVoiceSelectionSha256']
assert sha(ROOT/plan['currentKoScript'])==plan['currentKoScriptSha256']
assert sha(ROOT/plan['currentEnScript'])==plan['currentEnScriptSha256']
mc=ROOT/'motion-canvas/src/projects/character-parameters'
old=mc/'spatial-character-explanation-frame-exact-v1.tsx'
assert sha(old)=='eb8ea1b30b3e7a97173a6fbf182aa5cf1a86ab73302336571f67cb0457a08685'
new=mc/'spatial-character-explanation-measured-v3.tsx'
proof=BASE/'measured-mc-preparation-v3.json';assert not proof.exists() and not new.exists()
text=old.read_text('utf-8')
text=text.replace('export type CharacterTiming={durationSeconds:number;paragraphStarts:number[];measured:boolean};',
 'export type CharacterTiming={durationSeconds:number;paragraphStarts:number[];measured:true;blackIntervals:{startFrame:number;frames:number}[]};')
text=text.replace('characterExplanationFrameExact','characterExplanationMeasured')
text=text.replace('이번 턴의 상태와 영구 기본값 구분','이번 턴의 상태와 고정된 기본 능력치 구분')
old_loop=''' const frames=Math.round(timing.durationSeconds*fps);
 if(fps!==60||Math.abs(frames/fps-timing.durationSeconds)>1e-7)throw Error('Measured input must use an integer 60fps duration');
 for(let frame=0;frame<frames;frame++){t(frame/fps);yield;}
 t(timing.durationSeconds);'''
new_loop=''' const frames=Math.round(timing.durationSeconds*fps);
 if(fps!==60||Math.abs(frames/fps-timing.durationSeconds)>1e-7)throw Error('Measured input must use an integer 60fps duration');
 let end=0;
 for(const interval of timing.blackIntervals){
  if(!Number.isInteger(interval.startFrame)||!Number.isInteger(interval.frames)||interval.frames<=0||interval.startFrame<end||interval.startFrame+interval.frames>frames)throw Error('Invalid selected black interval');
  for(let frame=0;frame<interval.frames;frame++){t((interval.startFrame+frame)/fps);yield;}
  end=interval.startFrame+interval.frames;
 }
 t(end/fps);'''
assert old_loop in text;text=text.replace(old_loop,new_loop)
new.write_text(text,'utf-8');scenes=mc/'scenes-measured-v3';scenes.mkdir()
rows=[];cumulative=0
for c in plan['chapters']:
 p=scenes/(c['id']+'.tsx');assert not p.exists()
 timing=dict(durationSeconds=c['frames']/60,paragraphStarts=c['motionParagraphStarts'],measured=True,
             blackIntervals=[dict(startFrame=i['startFrame'],frames=i['frames']) for i in c['blackIntervals']])
 p.write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {characterExplanationMeasured} from '../spatial-character-explanation-measured-v3';\n"+
              f"export default makeScene2D(function* (view){{yield* characterExplanationMeasured(view,{json.dumps(c['id'])},{json.dumps(timing,separators=(',',':'))});}});\n",'utf-8')
 for i in c['blackIntervals']:
  rows.append(dict(segmentId=i['segmentId'],chapter=c['id'],renderStartFrame=cumulative,frames=i['frames'],chapterAbsoluteStartFrame=i['startFrame'],scene=rel(p),sceneSha256=sha(p)));cumulative+=i['frames']
 assert len(c['motionParagraphStarts'])==len(c['narrationParagraphStarts'])
entry=mc/'black-measured-v3.ts';assert not entry.exists()
entry.write_text("import {makeProject} from '@motion-canvas/core';\n"+
 '\n'.join(f"import s{i} from './scenes-measured-v3/{c['id']}?scene';" for i,c in enumerate(plan['chapters']))+
 "\nexport default makeProject({name:'character-parameters-black-measured-v3',scenes:["+','.join('s'+str(i) for i in range(12))+']});\n','utf-8')
live=mc/'black-structural-preflight-v1.ts';old_entry=live.read_bytes()
snapshot=BASE/'live-prototype-entry-before-measured-v3.ts';assert not snapshot.exists();snapshot.write_bytes(old_entry)
live.write_text("export {default} from './black-measured-v3';\n",'utf-8')
assert cumulative==9071
save(proof,dict(schemaVersion=3,preparedAt=now(),candidate=rel(plan_path),candidateSha256=sha(plan_path),engine=rel(new),engineSha256=sha(new),
 oldEnginePreservedSha256=sha(old),prototypeEntrySnapshot=rel(snapshot),prototypeEntrySnapshotSha256=sha(snapshot),independentScenes=12,pairedParagraphs=37,
 renderFrames=9071,nominalDurationSeconds=9071/60,renderIntervals=rows,entry=rel(entry),entrySha256=sha(entry),
 liveEntry=rel(live),liveEntrySha256=sha(live),blackStyle='research-black-v1',absoluteChapterClock=True,
 measuredMotionCanvasCreated=True,renderStarted=False,allContinuousPixelsReviewed=False,finalTimingApproved=False,finalCaptionsApproved=False,finalQa=False,
 prototypeRendersPreserved=True,newMedia=0,newRasterGitAdditions=0))
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='measured-black-and-native-inputs-prepared',measuredMotionCanvasCreated=True,
 measuredMc=rel(proof),ownedJob=None,nextAction='Fresh resources, scoped TypeScript, one CPU2 measured black export; native clips and all captions/pixels pending.');save(BASE/'latest-checkpoint.json',cp)
print(json.dumps(dict(independentScenes=12,paragraphs=37,blackFrames=cumulative,preparedOnly=True)))
