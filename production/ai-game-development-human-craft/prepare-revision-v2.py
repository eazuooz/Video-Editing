"""Apply the user's standalone-narration revision; preserve the delivered v1."""
from pathlib import Path
import json, hashlib, shutil
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]; SLUG='ai-game-development-human-craft'
P=ROOT/'projects'/SLUG; OUT=ROOT/'shared/output'/SLUG/'revision-v2'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
control=read(ROOT/'shared/publishing/video-production-control.json');assert control['selectedVideo']==SLUG
assert not (OUT/'prepared.json').exists(),'Revision is already prepared; resume its checkpoint'
spec=read(Path(__file__).with_name('revision-v2-edits.json'));m=read(P/'project.json')
old=read(P/'script/narration.ko.json');en=read(P/'script/narration.en.json')
assert old['revision']==3
backup=OUT/'before';backup.mkdir(parents=True,exist_ok=True)
paths=[P/'project.json',P/'script/narration.ko.json',P/'script/narration.en.json',P/'planning/outline.md',P/'production/checkpoint.json',P/'production/review-ledger.json',ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json',ROOT/f'motion-canvas/src/projects/{SLUG}/actual-footage.json']
for path in paths:
 dst=backup/path.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dst)
ko=read(P/'script/narration.ko.json');byko={s['id']:s for s in ko['scenes']};byen={s['id']:s for s in en['scenes']}
outline=(P/'planning/outline.md').read_text(encoding='utf-8');changes=[]
for edit in spec['edits']:
 sid=edit['scene'];i=edit['paragraph'];previous=byko[sid]['lines'][i]
 changes.append(dict(edit,previousKo=previous,previousEn=byen[sid]['lines'][i]))
 byko[sid]['lines'][i]=edit['ko'];byen[sid]['lines'][i]=edit['en'];outline=outline.replace(previous,edit['ko'])
changed=sorted({e['scene'] for e in changes});ko['revision']=4;ko['status']='standalone-narration-revision-in-production';en['sourceRevision']=4
ko['edits'].append({'revision':4,'userRequest':'2026-10-15 remove source-video framing and smooth narration; improve TTS opening/joins','changes':changes})
for s in ko['scenes']:s['narrationStatus']='standalone-text-reviewed-audio-pending' if s['id'] in changed else 'unchanged-approved-pcm'
current='\n'.join(t for s in ko['scenes'] for t in s['lines'])
assert not any(word in current for word in ['원영상','원 영상','제공된 자막','Wild Ox Studios','원작자'])
write(P/'script/narration.ko.json',ko);write(P/'script/narration.en.json',en)
(P/'planning/outline.md').write_text(outline.replace('전체 대본과 화면 구성 검수본 · 2026-10-14','전체 대본과 화면 구성 검수본 · 2026-10-15 · 수정2차'),encoding='utf-8')
oldout=ROOT/m['tts']['outputDir'];newout=oldout.parent/'qwen3-1.7b-natural-v2';newout.mkdir(parents=True,exist_ok=True)
retained=[]
for s in ko['scenes']:
 if s['id'] in changed:continue
 for sub,name in [('chunks',s['id']+'-scene.wav'),('asr',s['id']+'.json')]:
  src=oldout/sub/name;dst=newout/sub/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(src)==sha(dst)
 retained.append(s['id'])
m['tts'].update(outputDir=newout.relative_to(ROOT).as_posix(),filenameStem=SLUG+'-qwen3-natural-v2',sceneGapSeconds=.40,qualityRevision='natural-narration-joins-v1')
m['paths']['narration']=(newout/(m['tts']['filenameStem']+'.wav')).relative_to(ROOT).as_posix()
m['status']='revision-v2-narration-in-progress'
m['delivery']['driveReviewHistory']=[m['delivery']['driveReview']]
m['delivery']['driveReview']={'version':'v2','status':'revision-in-progress-not-uploaded','previousVersionUrl':m['delivery']['driveReviewHistory'][-1]['url']}
m['revision']={'id':'v2','scriptRevision':4,'changedScenes':changed,'retainedPcmScenes':retained,'previousArtifacts':backup.relative_to(ROOT).as_posix(),'userFeedback':'원영상 언급 제거와 자연스러운 연결; 인사/음성 끊김 개선','status':'text-revised-audio-pending'}
write(P/'project.json',m)
now=datetime.now(timezone.utc).isoformat();cp=read(P/'production/checkpoint.json');cp.update(updatedAt=now,stage='revision-v2-narration',activeJobs=[],pending=['Revised TTS opening/joins and current full narration readback','Changed timing/visual/captions/mix and new output integrity','Drive v2 complete review delivery'],nextAction='Generate and verify changed scene audio with approved voice; preserve v1 and unchanged PCM.')
cp['revision']=m['revision'];cp['finalReviewDeliveryHistory']=[cp['finalReviewDelivery']];cp['finalReviewDelivery']=m['delivery']['driveReview'];write(P/'production/checkpoint.json',cp)
control['updatedAt']=now;control['newProductionAuthorization']['latestSteering']='2026-10-15: standalone narration without source-video framing; smooth opening and TTS interruptions; revise this video through Drive review delivery'
write(ROOT/'shared/publishing/video-production-control.json',control)
write(OUT/'prepared.json',{'changedScenes':changed,'retainedScenes':retained,'changes':changes,'oldTtsDirectory':oldout.relative_to(ROOT).as_posix(),'newTtsDirectory':newout.relative_to(ROOT).as_posix(),'oldNarrationSha256':sha(oldout/(read(backup/P.relative_to(ROOT)/'project.json')['tts']['filenameStem']+'.wav')),'textReview':'complete continuous KO read and aligned EN updates; illustration roles retained; biography replaced with clearly general examples','humanListening':'pending'})
print(json.dumps({'changedScenes':changed,'retainedScenes':retained,'paragraphEdits':len(changes)}))
