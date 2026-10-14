"""Prepare eight additive narration scenes; retain all 56 original dictionaries."""
from pathlib import Path
import copy,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
I=B/'cross-game-review-20261011/interpolation-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
draft=read(I/'additions-draft.json');audit=read(I/'numeric-and-preservation-draft-audit.json');base=read(I/'baseline.json')
assert audit['preTtsDraftAuditPassed'] and audit['draftSha256']==sha(I/'additions-draft.json')
assert read(B/'queue.json')['execution']['mode']=='active'
MASTER='game-math-interpolation-cross-game-additions-v3';p=ROOT/'projects'/MASTER
assert not p.exists(),'Do not overwrite a previously prepared/synthesized master'
voice=copy.deepcopy(read(ROOT/'projects/game-math-quaternion-cross-game-additions-v3/project.json')['tts'])
voice['outputDir']=f'shared/output/narration/{MASTER}/qwen3-1.7b-balanced-v1'
voice['filenameStem']=f'{MASTER}-qwen3-1.7b-balanced-v1'
for lang in ['ko','en']:
 script=dict(schemaVersion=1,language='Korean' if lang=='ko' else 'English',
  scenes=[dict(id=s['id'],title=s['title'],lines=s[lang]) for s in draft['scenes']])
 write(p/f'script/narration.{lang}.json',script)
manifest=dict(schemaVersion=1,slug=MASTER,title='보간과 회전 변환 네 게임 비교 추가 내레이션',
 status='CPU scripts prepared; current closest quaternion delivery finishes first',
 standaloneUploadAllowed=False,authorizationQueue=B.relative_to(ROOT).as_posix()+'/queue.json',
 paths=dict(script=f'projects/{MASTER}/script/narration.ko.json',scriptEn=f'projects/{MASTER}/script/narration.en.json',
  captionsKo=f'projects/{MASTER}/script/voice-aligned.ko.srt',captionsEn=f'projects/{MASTER}/script/voice-aligned.en.srt'),
 tts=voice,editing=dict(exampleSeconds=0,narrationPlacement='additions beside retained explanations',backgroundMusic=False),
 preservation=dict(baselineAudioOverwritten=False,originalScenes=56,existingVoiceReferencePreserved=True),
 contract=dict(handedness='right-handed',vectors='column',frame='local-to-world',componentOrder='wxyz',
  product='Hamilton',vectorRotation='q [0,v] q^-1',angles='radians in formulas'),
 scheduling=dict(gpuTtsStarted=False,guardRequired='Wait for the current training job checkpoint/validation/done marker; exclusive TTS; restore the original queue and verify its actual state.'),
 planning=dict(draft=I.relative_to(ROOT).as_posix()+'/additions-draft.json',
  audit=I.relative_to(ROOT).as_posix()+'/numeric-and-preservation-draft-audit.json'))
write(p/'project.json',manifest)
maps=[]
for ep in base['episodes']:
 old=ROOT/'projects'/ep['slug'];rows=[s for s in draft['scenes'] if s['episode']==ep['newSlug']]
 combined={}
 for lang in ['ko','en']:
  original=read(old/f'script/narration.{lang}.json');scenes=copy.deepcopy(original['scenes'])
  for row in rows:
   index=next(i for i,s in enumerate(scenes) if s['id']==row['after'])+1
   scenes.insert(index,dict(id=row['id'],title=row['title'],lines=row[lang]))
  assert [s for s in scenes if s['id'] in ep['sceneIds']]==original['scenes']
  combined[lang]=dict(original,scenes=scenes)
  write(I/'proposed-scripts'/ep['newSlug']/f'narration.{lang}.json',combined[lang])
 maps.append(dict(newSlug=ep['newSlug'],baselineSlug=ep['slug'],videoId=ep['videoId'],
  targetDatePlan=ep['newSchedule'],preserveOriginalSceneOrderAndDictionaries=True,
  sceneIds=[s['id'] for s in combined['ko']['scenes']],originalScenes=len(ep['sceneIds']),
  newScenes=len(rows),additionalGames=['Trailmakers'],bodyRatio=dict(actual=.4,explanation=.6),
  newNarrationProject=MASTER,originalProjectNotChanged=True,currentScheduledVideoNotChanged=True))
write(I/'cpu-preparation.json',dict(preparedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),episodes=maps,
 masterManifestSha256=sha(p/'project.json'),scriptsSha256={lang:sha(p/f'script/narration.{lang}.json') for lang in ['ko','en']},
 source=read(I/'candidate-comparison.json'),
 next=['Finish closest actual quaternion replacements','Save current Studio date evidence and authorized replacement duplicate review',
  'Freeze exact scripts/reference hashes','Cooperative GPU boundary and actual restoration',
  'Measure new narration and solve exact40:60 slots without loops','Independent Manim scenes and new narration-timed tracks',
  'Current mixed audio, whole moving pixels, captions and private settings review'],
 newTtsStarted=False,newRenderStarted=False,humanListeningComplete=False,rightsHumanReviewComplete=False))
print(json.dumps(dict(retainedScenes=56,newScenes=8,cpuOnly=True,baselineProjectsUnchanged=True,newTtsStarted=False)))
