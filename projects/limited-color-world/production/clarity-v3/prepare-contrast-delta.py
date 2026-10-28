"""Prepare six visual corrections without changing any existing media or audio."""
from pathlib import Path
import copy,json,shutil
import audio_pipeline as a
import video_pipeline as v
H=Path(__file__).resolve().parent
NATIVE={'c025','c026','c027','c030','c032'}
CHANGED=NATIVE|{'c028'}

def copy_verified(src,dst):
 src,dst=Path(src),Path(dst);before=a.sha(src)
 if dst.exists():assert a.sha(dst)==before
 else:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 assert a.sha(src)==before and a.sha(dst)==before
 return {'source':a.artifact(src),'copy':a.artifact(dst),'identicalBytes':True}

def main():
 a.require_authorized('six-cut-visual-only-contrast-and-target-correction')
 current=H/'edit-plan.json';backup=H/'edit-plan.before-contrast-v2.json'
 copy_verified(current,backup)
 old=a.read(backup);plan=copy.deepcopy(old);oldout=a.repo_path(old['outputDir']);out=a.LOCAL/'edit-contrast-v2'
 out.mkdir(parents=True,exist_ok=True)
 proposal=a.read(H/'c028-distant-scenery-refinement.json');scope=proposal['editScope']
 copies=[];native=[]
 for c in plan['cuts']:
  if c['id'] in NATIVE:
   movie=a.LOCAL/'render/contrast-v2'/c['id']/'unity.mp4';done=a.read(movie.parent/'render-success.json');request=a.read(movie.parent/'request.json')
   assert (done['status'],done['cutId'],done['frames'],done['completed'])==('complete',c['id'],c['frames'],c['frames'])
   assert done['compiledSourceFingerprint']==request['expectedFingerprint']
   for item in request['sourceFiles']:assert a.sha(a.repo_path(item['path']))==item['sha256'],item['path']
   assert 'RenderRevisions/contrast-v2/' in done['scene']
   v.assert_video(movie,c['frames'])
   c['renderedSource']=a.relative(movie)
   c['nativeCapture']={'success':a.artifact(movie.parent/'render-success.json'),'request':a.artifact(movie.parent/'request.json'),'video':a.artifact(movie),'compiledSourceFingerprint':done['compiledSourceFingerprint'],'savedScene':done['scene']}
   native.append(c['nativeCapture'])
  elif c['id']=='c028':
   for m in c['marks']:
    if m['id'] in scope['markIds']:
     assert [k['t'] for k in m['keyframes']]==[k['t'] for k in scope['newKeyframes']]
     m['keyframes']=copy.deepcopy(scope['newKeyframes'])
   v.annotations(c,plan)
  else:
   assert c==next(x for x in old['cuts'] if x['id']==c['id'])
   for suffix in ['.mp4','-render.json']:
    copies.append(copy_verified(oldout/(c['id']+suffix),out/(c['id']+suffix)))
   receipt=a.read(out/(c['id']+'-render.json'))
   assert receipt['signature']['cut']==c and receipt['outputSha256']==a.sha(out/(c['id']+'.mp4'))
 # Same current narration/game/music bytes. Reuse, never mix or encode audio.
 audio=a.read(oldout/'audio-build.json');copy_verified(oldout/'audio-build.json',out/'audio-build.original.json')
 for item in audio['outputs']:
  src=a.repo_path(item['path']);assert a.sha(src)==item['sha256']
  dst=out/src.name;copies.append(copy_verified(src,dst));item['path']=a.relative(dst)
 for name in ['branding.mp4','membership.mp4','captions.ko.srt','captions.en.srt','captions.ko.ass','captions.json','caption-alignment.json','final-mix-asr.json','final-mix-text-comparison.json']:
  copies.append(copy_verified(oldout/name,out/name))
 audio['visualOnlyReuse']={'originalReceipt':a.artifact(oldout/'audio-build.json'),'originalPlan':a.artifact(backup),'reason':'Only six visual cuts changed; full audio contract and all PCM/AAC bytes are identical. No new synthesis/mix/recognition.'}
 a.save(out/'audio-build.json',audio)
 plan.update(outputDir=a.relative(out),outputStem='limited-color-world-clarity-v3-contrast-v2',captionsAss=a.relative(out/'captions.ko.ass'),mixFile=a.relative(out/'final-mix.wav'),nativeRevision='measured-v1 + five-cut contrast-v2')
 assert a.audio_plan_contract(plan)==a.audio_plan_contract(old)==audio['inputs']['audioPlanContract']
 plan['visualCorrection']={'baselinePlan':a.artifact(backup),'baselineMasterSha256':proposal['basisCaptionedSha256'],'nativeCutIds':sorted(NATIVE),'annotationCutId':'c028','nativeSourceSnapshot':'production/batches/design-25-30-review-actions-20261029/contrast-repair-source-snapshot.json','narrationTimingAudioCaptionsUnchanged':True}
 plan['measuredShare']=v.validate_plan(plan)
 target=H/'edit-plan.contrast-v2.json'
 if target.exists():assert a.read(target)==plan
 else:a.save(target,plan)
 # Preserve mark authoring baseline, then only replace the two geometries.
 marksPath=H/'source-marks.json';markBackup=H/'source-marks.before-contrast-v2.json'
 if not markBackup.exists():copy_verified(marksPath,markBackup)
 marks=a.read(markBackup)
 for row in marks['marks']:
  if row['cutId']=='c028' and row['mark']['id'] in scope['markIds']:row['mark']['keyframes']=copy.deepcopy(scope['newKeyframes'])
 marks['geometryRefinement']=a.artifact(H/'c028-distant-scenery-refinement.json');a.save(marksPath,marks)
 a.save(H/'contrast-delta-preparation.json',{'status':'prepared-not-final-reviewed','plan':a.artifact(target),'baselinePlan':a.artifact(backup),'changedCutIds':sorted(CHANGED),'unchangedCutIds':[c['id'] for c in old['cuts'] if c['id'] not in CHANGED],'byteCopies':copies,'native':native,'sameAudioContract':True,'oldMediaModified':False,'fullFinalAsrReusedForSameAac':True})
 print('Prepared29 identical cut encodes +6 scoped changes; all audio/captions preserved.')
if __name__=='__main__':main()
