"""Bind measured editorial decisions to completed, hash-pinned local media.

Run again as scoped native captures finish. Unfinished sources remain explicit;
this does not generate media, overwrite review masters, or assert final QA.
"""
from pathlib import Path
import copy
import audio_pipeline as ap
import video_pipeline as vp
H=Path(__file__).resolve().parent
L=H.parent/'local/grid-v1'
R=H.parents[3]

def main():
 plan=ap.read(H/'measured-edit-plan.proposal.json')
 plan.update(episode='A01',status='assembly-prepared-final-media-and-QA-pending',scope='A01/grid-v1 local final-review production only')
 cuts=plan['cuts'];by={c['id']:c for c in cuts}
 # The first Samus grab throws backward; the next uncut source shot throws up.
 a,b=by['A01-E019'],by['A01-E020']
 a['frames']+=17;a['endFrame']+=17
 b['startFrame']+=17;b['frames']-=17
 b['sourceStart']=4.9049;b['sourceEndExclusive']=4.9049+b['frames']/60
 b['reviewedSourceEnd']=6.006;b['sourceNativeCutsInside']=[]
 b['sourceFactCorrection']='samus-throw-fact-check.json: Mario upward throw; old Luigi backward throw excluded'
 # An entrance roar is not an idle loop. Show an actual self-authored idle.
 c=by['A01-E028'];following=by['A01-E029']
 c['kind']='explanation';c['frames']+=following['frames'];c['endFrame']=following['endFrame']
 c['explanationMode']='idle-intent';c['renderer']='Unity';c['sourceKind']='self-authored animation comparison'
 c['teachingPurpose']='Same Idle_A and phase, contrasting upper-body posture; no commercial entrance presented as idle'
 for key in ['source','sourceFile','sourceUrl','sourceSha256','sourceVideoDimensions','sourceNativeFps','sourceAttribution','rights','sourceStart','sourceEndExclusive','sourceNativeCutsInside','sourceAudioEnabled']:
  c.pop(key,None)
 c['marks']=[];c['sourceCorrection']='Krool entrance/roar excluded from idle explanation'
 cuts.remove(following)
 native_profiles={p['id']:p for p in ap.read(R/'unity/VideoEditing/Assets/VideoScenes/animation-series-v1/animation-grid-presentations.json')['presentations']}
 stills=ap.read(H/'still-annotations.json')['cuts']
 actual_path=H/'actual-annotations.json'
 actual_rows=ap.read(actual_path).get('cuts',{}) if actual_path.exists() else {}
 actual={row['id']:row for row in actual_rows} if isinstance(actual_rows,list) else actual_rows
 audio_path=H/'source-audio-selection.json'
 audio_review=ap.read(audio_path) if audio_path.exists() else None
 audio_rows={row['id']:row for row in audio_review['cuts']} if audio_review else {}
 missing=[];native_queue=[]
 for c in cuts:
  key=c['id']
  if c['kind']=='independent-gameplay':
   c['viewport']=[160,0,1600,900]
   s=c['source']
   c['gameLabel']='バーチャファイター' if False else ('VIRTUA FIGHTER' if s=='vf' else 'Untitled Goose Game' if s.startswith('goose') else '대난투 스매시브라더스 얼티밋')
   c['pictureLabel']='공개 개발 영상' if s=='vf' else '2017년 개발 중 영상' if s=='goose-prealpha' else '실제 게임 영상'
   c['sourceAudioEnabled']=True
   c['sourceAudioDecision']='Retain the source action/audio in this private local critique review under recorded conditional publisher policies; soundtrack identity/final listening remains explicitly pending. Not separate music extraction.'
   c['rightsFinalized']=False
   if key in audio_rows:
    row=audio_rows[key]
    assert (row['sourceSha256'],row['sourceStart'],row['frames'])==(c['sourceSha256'],c['sourceStart'],c['frames']),key+' stale audio selection'
    for field in ('sourceAudioEnabled','sourceAudioReviewStatus','sourceAudioDecision','pendingFinalListening'):c[field]=row[field]
   if key in actual:
    row=actual[key]
    assert (row['sourceSha256'],row['sourceStart'],row['frames'],row['viewport'])==(c['sourceSha256'],c['sourceStart'],c['frames'],c['viewport']),key+' stale actual annotation'
    c['marks']=row.get('marks',[]);c['annotationEvidence']=row
   continue
  spec_path=H/'still-specs'/f'{key}.json'
  if key in stills and stills[key].get('marks') is not None and key!='A01-E028':
   spec=ap.read(spec_path);receipt_path=ap.repo_path(spec['outputDir'])/'explanation-render.json';receipt=ap.read(receipt_path)
   assert receipt['frames']==c['frames'],key
   row=stills[key]
   assert row['imageOutput']['sha256']==receipt['imageOutput']['sha256'],key+' stale still annotation'
   c['renderedSource']=receipt['movie']['path'];c['renderedSourceSha256']=receipt['movie']['sha256'];c['renderedStartFrame']=0
   c['explanationRender']={'kind':'annotated-still','receipt':ap.relative(receipt_path),'receiptSha256':ap.sha(receipt_path)}
   c['nativeCapture']=None;c['marks']=row['marks'];c['annotationEvidence']=row
   c['sourceStillTimestamp']=spec['frameTimeSeconds'];c['sourceStart']=spec['frameTimeSeconds']
   c['captureState']='complete-still-plate-final-annotations-pending-encoded-QA';c['renderer']='inspected source-frame composition'
   if key=='A01-E038':
    c['annotationRequests'][0]['target']='Visible beak and radio handle in the inspected radio-pickup still; no invented release or hidden path'
    c['annotationRequests'][0]['coordinatesStatus']='Superseded by hash-bound annotationEvidence and actual output marks'
  else:
   mode=c['explanationMode'];revision=key+'-v1';directory=L/'render'/revision/mode
   source=directory/'unity.mp4';success=directory/'render-success.json';request=directory/'request.json'
   c['renderedSource']=ap.relative(source);c['renderedStartFrame']=0;c['renderedSourceSha256']=None
   c.pop('explanationRender',None)
   native_queue.append({'id':key,'mode':mode,'frames':c['frames'],'revision':revision,'presentation':key if key in native_profiles else '',
                        'startFrame':c['startFrame'],'endFrame':c['endFrame']})
   if all(p.exists() for p in [source,success,request]):
    receipt=ap.read(success);q=ap.read(request);digest=ap.sha(source)
    assert receipt['status']=='complete' and receipt['completed']==c['frames'] and q['frames']==c['frames'],key
    c['renderedSourceSha256']=digest
    c['nativeCapture']={'movieSha256':digest,'successReceipt':ap.relative(success),'successSha256':ap.sha(success),
                        'request':ap.relative(request),'requestSha256':ap.sha(request),'compiledFingerprint':receipt['compiledSourceFingerprint']}
    c['captureState']='full-native-capture-complete-final-QA-pending'
   else:
    missing.append(key);c['nativeCapture']={'status':'pending actual capture'};c['captureState']='pending actual capture'
 gameplay=sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay')
 plan['expectedGameplayShare']=gameplay/plan['bodyFrames'];plan['ratioToleranceFrames']=1
 plan['ratioChoice']={'path':ap.relative(H/'editorial-ratio-choice.json'),'sha256':ap.sha(H/'editorial-ratio-choice.json')}
 plan['ratioDecision']={'mode':'measured episode-specific clarity choice','actualFrames':gameplay,'explanationFrames':plan['bodyFrames']-gameplay,'actualHumanApproval':False}
 plan['outputDir']=ap.relative(L/'edit');plan['outputStem']='animation-assigning'
 plan['captionsAss']=ap.relative(L/'edit/captions.ko.ass')
 music=R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'
 assert ap.sha(music)=='06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08'
 plan['audio']['music']={'path':ap.relative(music),'sha256':ap.sha(music),'licenseRecord':'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md','title':'Nimbus','artist':'Eveningland'}
 plan['audio']['musicLufs']=-28;plan['audio'].pop('musicBindingStatus',None)
 plan['sourceCorrections']=[ap.artifact(H/'samus-throw-fact-check.json'),{'cut':'A01-E028/E029','change':'239-frame Unity idle replaces commercial entrance roar; source footage preserved outside cut'}]
 if audio_review:
  assert len(audio_rows)==sum(c['kind']=='independent-gameplay' for c in cuts)
  plan['audioSourceReviewPending']=False
  plan['sourceAudioSelection']=ap.artifact(audio_path)
  plan['actualSourceAudioListeningPerformed']=False
  plan['finalMixedAudioListeningPending']=True
 plan['nativeCaptureQueue']=native_queue
 plan['pendingBeforeRender']={'nativeCaptures':missing,'actualAnnotations':not actual_path.exists(),'finalAudioListening':True,'finalEncodedQA':True}
 vp.validate_plan(plan)
 ap.save(H/'edit-plan.json',plan)
 print('Bound',len(cuts),'cuts; gameplay',gameplay,'/',plan['bodyFrames'],'; native missing',len(missing))

if __name__=='__main__':main()
