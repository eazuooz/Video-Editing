"""Pin the measured D25 plan to completed native captures before audio/video jobs.

This prepares JSON only. It neither renders nor changes the current public review.
"""
from pathlib import Path
import argparse,copy,re
import audio_pipeline as a
import ui_compositor as ui
import video_pipeline as v

HERE=Path(__file__).resolve().parent

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--native-revision',default='final-v1')
 args=parser.parse_args()
 if not re.fullmatch(r'[A-Za-z0-9_-]+',args.native_revision):raise ValueError('Unsafe native revision')
 a.require_authorized('pin-measured-d25-final-plan')
 plan=copy.deepcopy(a.read(HERE/'edit-plan.draft.json'))
 cues=a.read(HERE/'unity-cues.json')
 jobs=a.read(HERE/'capture-jobs.json')
 assert cues['timingLocked'] is True and jobs['timingLocked'] is True
 jobmap={row['cutId']:row for row in jobs['jobs']}
 native=[];photos=[]
 for cut in plan['cuts']:
  if cut['kind']!='explanation':continue
  if cut['variant'] in ui.PHOTO_VARIANTS:
   assert cut['composition']=='official-photo-2d' and cut['id'] not in jobmap
   assert not cut.get('renderedSource')
   photos.append(cut['id']);continue
  job=jobmap[cut['id']]
  assert job['frames']==cut['frames'] and job['stageClass']=='D25ColorClarityStage'
  source=a.LOCAL/'render'/args.native_revision/cut['id']/'unity.mp4'
  done=a.read(source.parent/'render-success.json');request=a.read(source.parent/'request.json')
  assert (done['status'],done['cutId'],done['frames'],done['completed'])==('complete',cut['id'],cut['frames'],cut['frames'])
  assert done['compiledSourceFingerprint']==request['expectedFingerprint']
  assert done['renderRequest']=='RenderPipeline.StandardRequest (D25 world only; editorial UI composited separately)'
  for item in request['sourceFiles']:
   if a.sha(a.repo_path(item['path']))!=item['sha256']:raise ValueError('Native input changed: '+item['path'])
  v.assert_video(source,cut['frames'])
  cut['renderedSource']=a.relative(source)
  cut['nativeCapture']={'success':a.artifact(source.parent/'render-success.json'),'request':a.artifact(source.parent/'request.json'),'video':a.artifact(source),'compiledSourceFingerprint':done['compiledSourceFingerprint'],'savedScene':done['scene']}
  native.append(cut['id'])
 assert len(native)==18 and len(photos)==5 and set(native)==set(jobmap)
 plan['status']='measured-native-complete-ready-for-final-composition'
 plan['nativeRevision']=args.native_revision
 plan['measuredShare']=v.validate_plan(plan)
 plan['nativeTimingCues']=a.artifact(HERE/'unity-cues.json')
 plan['nativeJobs']=a.artifact(HERE/'capture-jobs.json')
 plan['postcompositedUi']=a.artifact(HERE/'ui_compositor.py')
 destination=HERE/'edit-plan.json'
 if destination.exists():
  if a.read(destination)!=plan:raise FileExistsError('Preserve existing pinned final plan; investigate before replacing it')
 else:a.save(destination,plan)
 a.save(HERE/'final-plan-pinning.json',{'status':'ready-for-final-composition','plan':a.artifact(destination),'nativeCuts':native,'photoOnlyCuts':photos,'audioAndFinalEncodedPixels':'not implied by plan pinning','humanWholeReview':'pending'})
 print('Pinned completed native18 + photo-only5 cuts; no rendering or final review claim.')

if __name__=='__main__':main()
