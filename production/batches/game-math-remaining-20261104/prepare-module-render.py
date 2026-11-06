"""Bind a reviewed module sandbox to measured speech. Never launches rendering."""
from pathlib import Path
import argparse,hashlib,json,math
from part2.edition import retain_circle_speed
R=Path(__file__).resolve().parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--sandbox',required=True);ap.add_argument('--audio-revision',default='audio-v1');ap.add_argument('--revision',default='render-v1');a=ap.parse_args()
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow'] and a.project in c['projectSlugs'] and a.project!='game-math-shading-lights'
P=R/'projects'/a.project;S=P/'production/unity-staging';sandbox=(S/a.sandbox).resolve();assert sandbox.is_relative_to(S)
assert __import__('re').fullmatch(r'audio-v\d+',a.audio_revision) and __import__('re').fullmatch(r'render-v\d+',a.revision)
audio=P/'production/local'/a.audio_revision;edit=P/'production/local'/a.audio_revision.replace('audio-','edit-');timeline=edit/'word-aligned-timeline.json';t=read(timeline)
edition=P/'planning/part2-delivery-edition.json'
if edition.is_file():
    assert read(edition)['audioRevision']==a.audio_revision,'The measured speech belongs to an earlier edition'
    spoken=read(audio/'narration.timing.json')['entries']
    current=read(P/'script/narration.ko.json')['scenes']
    assert [(e['scene_id'],e['text']) for e in spoken]==[(s['id'],line) for s in current for line in s['lines']], 'Do not capture scenes against superseded narration'
assert not t['flags'],'Resolve actual speech, caption and phase differences first'
assert t['bindingsSha256']==sha(P/'planning/scene-bindings.json') and t['narrationSha256']==sha(audio/'narration.wav')
assert t['timingSha256']==sha(audio/'narration.timing.json') and t['captionReadingAdjustmentsSha256']==sha(P/'planning/caption-reading-adjustments.json'),'Caption wording or measured speech changed; align this revision again'
marker=read(sandbox/'MATH_CAPTURE_SANDBOX.json')
# Some families share their implementation plan at the first episode. The
# actual episode/slug pair always belongs to the selected production plan.
episode=read(P/'planning/production-plan.json')['episode']
assert __import__('re').fullmatch(r'M(2[2-9]|3[0-3])',episode or '') and marker['projectSlug']==P.name
assert any(i['id']==episode and i['slug']==P.name for i in read(Path(__file__).parent/'batch.json')['items'])
factories={'game-math-skinning-normal-map':'SkinNormalSceneBuilder','game-math-pipeline-shaders':'PipelineSceneBuilder'}
# Read the factory from a prepared, source-matched preview for other modules.
preview_jobs=[]
for q in S.glob('local-preflight-*/queue.json'):
 d=read(q)
 if d['fingerprint']==marker['fingerprint']:preview_jobs.extend(d['jobs'])
assert preview_jobs,'This exact sandbox needs a prepared diagnostic queue'
factory=read(Path(preview_jobs[0]))['factoryType'];assert factory==factories.get(P.name,factory)
out=P/'production/local'/a.revision;assert not out.exists(),'Preserve prior media and evidence; select an additive revision'
picture_plan=P/'planning/part2-picture-plan.json'
plan=read(picture_plan) if picture_plan.exists() else {}
cue_edits=plan.get('nativeCueRevisions',{}).get(a.revision,{})
radius_comparisons=plan.get('fixedSpeedRadiusComparisons',{}).get(a.revision,[])
jobs=[];cuts=[];pending_files=[]
for row in t['scenes']:
 sid=row['id'];frames=row['endFrame']-row['startFrame'];assert frames>0
 shot=dict(row['shot'],durationSeconds=frames/60);game=row.get('actualGamePart');gameframes=0;game_start=row.get('actualGameStartFrame',0)
 if sid in cue_edits:
  seconds=list(shot['stepSeconds'])
  for index,phrase in cue_edits[sid].items():
   matches=[c for c in t['ko'] if c['scene']==sid and c['spoken'].startswith(phrase)]
   assert len(matches)==1 and 0<int(index)<len(seconds)-1,(sid,phrase)
   seconds[int(index)]=round(matches[0]['start']*60-row['startFrame'])/60
  assert all(a<b for a,b in zip(seconds,seconds[1:]))
  shot['stepSeconds']=seconds
 if sid in radius_comparisons:
  retain_circle_speed(shot)
 if game:
  assert game['playbackRate']==1 and not game['freezePadding'] and not game['loop']
  handoff=row.get('actualGameEndFrame')
  available=(handoff if handoff is not None else frames)-game_start
  gameframes=min(available,math.floor((game['sourceOut']-game['sourceIn'])*60+.0001))
  assert gameframes>=60,'Reject a token flash of the game'
  required_out=game.get('minimumObservedResultOut',game['sourceOut'])
  assert game['sourceIn']+gameframes/60+.017>=required_out, f'{sid}: native action/result would be truncated; inspect a shorter complete source window or adjust its speech handoff, never freeze/slow/pad'
  cuts.append(dict(scene=sid,kind='actual-gameplay',sourceId=game['sourceId'],sourceIn=game['sourceIn'],sourceOut=game['sourceIn']+gameframes/60,originalAudioIn=game.get('fullOriginalAudioIn',game['sourceIn']),frames=gameframes,globalStartFrame=row['startFrame']+game_start,nativeSpeed=True,freeze=False,loop=False,originalSelectedOut=game['sourceOut'],minimumObservedResultOut=required_out,speechStartEvidence=row.get('actualGameStartEvidence'),speechEndEvidence=row.get('actualGameEndEvidence'),review='Confirm observed before/action/result and the source-to-Unity spoken handoff in final encoded output'))
  if 'sourceSoundDecision' in game:cuts[-1]['sourceSoundDecision']=game['sourceSoundDecision']
  if 'nativeDetailInset' in game:cuts[-1]['nativeDetailInset']=game['nativeDetailInset']
  if 'insertVersion' in game:
   assert __import__('re').fullmatch(r'[a-z0-9-]+',game['insertVersion'])
   cuts[-1]['insertVersion']=game['insertVersion']
 if frames==gameframes:continue
 shotfile=out/'shots'/(sid+'.json');pending_files.append((shotfile,shot))
 job=dict(id=episode.lower()+'-body-'+sid,projectSlug=P.name,command='render',expectedFingerprint=marker['fingerprint'],shotFile=str(shotfile),factoryType=factory,output=str(out/'unity'/sid),frames=frames,sampleFrames=[0,frames//2,frames-1],speechTimingVerified=True,sceneId=sid,ffmpeg='C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
 jp=out/'jobs'/(sid+'.json');pending_files.append((jp,job));jobs.append(str(jp))
 if game_start>0:cuts.append(dict(scene=sid,kind='explanation',file=str(Path(job['output'])/'unity.mp4'),sourceIn=0,frames=game_start,globalStartFrame=row['startFrame']))
 after=game_start+gameframes
 if after<frames:cuts.append(dict(scene=sid,kind='explanation',file=str(Path(job['output'])/'unity.mp4'),sourceIn=after/60,frames=frames-after,globalStartFrame=row['startFrame']+after))
cuts.sort(key=lambda x:x['globalStartFrame'])
cursor=0
for cut in cuts:assert cut['globalStartFrame']==cursor;cursor+=cut['frames']
assert cursor==t['scenes'][-1]['endFrame']
for path,payload in pending_files:save(path,payload)
save(out/'queue.json',dict(project=P.name,episode=episode,sandbox=str(sandbox),fingerprint=marker['fingerprint'],unity='C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe',jobs=jobs,wordAlignment=str(timeline),wordAlignmentSha256=sha(timeline),audioDirectory=str(audio),editDirectory=str(edit),bodyFrames=cursor,cuts=cuts,actualGameplayFrames=sum(x['frames'] for x in cuts if x['kind']=='actual-gameplay'),automation=False,finalReviewReady=False))
print(f'{len(jobs)} actual-speech capture jobs, {len(cuts)} contiguous cuts prepared; no renderer started')
