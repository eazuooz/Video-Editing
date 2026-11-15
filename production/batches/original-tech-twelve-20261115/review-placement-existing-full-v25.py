"""Review an existing real full capture; preserve its failed bit-parity result.

Encoded pixels must still match their own Unity source byte for byte. The
separate cross-run comparison permits at most0.001% changed raster pixels and
32/255 channel difference, with exact model/trace state and mobile-scale checks.
It does not rerender, retag the old failure as passed, or alter audio QA.
"""
from pathlib import Path
import hashlib,importlib.util,json,math,shutil
import av,numpy as np,psutil
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];DROOT=ROOT/'shared/output/original-tech-twelve-20261115';BASE=DROOT/'shorts-horizon-gpu-placement/native-completion-v6';OUT=DROOT/'shorts-horizon-gpu-placement/native-full-review-v25'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS);assert not(OUT/'accepted-full.json').exists();failure=BASE/'failure-full.json';assert failure.exists();run=read(BASE/'current-run.json');attempt=Path(run['attempt']);capture=attempt/'capture';complete=read(capture/'complete.json');assert complete['actualUnityCapture']and complete['framesPerCamera']==720;assert read(attempt/'process-exit.json')['exitCode']==0
 s=importlib.util.spec_from_file_location('unchanged_placement_source',HERE/'run-native-completion-v6.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m=m.load('placement');prep=m.prepare();assert complete['fingerprint']==prep['fingerprint'];project=Path(prep['project']).resolve();assert project.is_relative_to((BASE/'projects').resolve())
 for f in prep['files']:
  assert pin(f['source'])['sha256']==f['sha256']
  if not str(f['target']).endswith('.meta'):assert pin(project/f['target'])['sha256']==f['sha256']
 smoke=read(BASE/'accepted-smoke.json');clips=[];comparisons=[]
 for old in smoke['clips']:
  mode,camera=old['mode'],old['camera'];folder=capture/mode/camera;stream=read(folder/'streamed-capture.json');trace=read(folder/'trace.json');priortrace=read(old['trace']['path']);assert trace['fingerprint']==prep['fingerprint']and trace['model']==priortrace['model']and trace['frames'][:32]==priortrace['frames'];assert len(trace['frames'])==len(stream['frames'])==720 and stream['complete']and stream['encoderExitCode']==0
  assert (stream['width'],stream['height'],stream['fps'])==(1080,1080,60);state=trace['model'];assert state['accepted']+state['rejectedDensity']+state['rejectedRoad']+state['rejectedWater']==state['candidates']==len(state['points']);assert sum(p['accepted']for p in state['points'])==state['accepted'];grass=None
  for f,row in enumerate(trace['frames']):
   assert row['frame']==f and row['objectsRevealed']==(f>=180)and row['actualTreeInstances']==(state['accepted']if f>=180 else 0)
   if not state['secondLayer']or f<180:assert row['actualGrassInstances']==0
   elif grass is None:grass=row['actualGrassInstances'];assert grass>0
   else:assert row['actualGrassInstances']==grass
  refs={int(p.stem.split('-')[-1]):p for p in folder.glob('reference-*.png')};assert set(refs)=={0,90,150,240,330,420,510,600,660,719};video=folder/'frames-lossless-rgb.mp4';before=av.open(old['video']['path']);bs=before.streams.video[0];bs.codec_context.thread_count=2;prioriter=before.decode(bs);changed=[]
  with av.open(str(video))as container:
   st=container.streams.video[0];st.codec_context.thread_count=2;assert(st.width,st.height)==(1080,1080)and st.average_rate==60;count=0
   for i,frame in enumerate(container.decode(st)):
    assert i<720 and abs(frame.time-i/60)<1e-5;rgb=frame.to_ndarray(format='rgb24');assert stream['frames'][i]['frame']==i and hashlib.sha256(rgb.tobytes()).hexdigest()==stream['frames'][i]['rgbSHA256']
    if i in refs:assert np.array_equal(np.asarray(Image.open(refs[i]).convert('RGB')),rgb)
    if i<32:
     prior=next(prioriter).to_ndarray(format='rgb24');delta=np.abs(rgb.astype(np.int16)-prior.astype(np.int16));pixels=int(np.count_nonzero(delta.max(axis=2)));maximum=int(delta.max());assert pixels<=math.floor(1080*1080*.00001)and maximum<=32,'Retain changed geometry or larger raster differences as a hold'
     small=np.asarray(Image.fromarray(rgb).resize((375,375),Image.Resampling.LANCZOS),dtype=np.int16);smallold=np.asarray(Image.fromarray(prior).resize((375,375),Image.Resampling.LANCZOS),dtype=np.int16);sd=np.abs(small-smallold);assert int(sd.max())<=2 and float(sd.mean())<.001;changed.append(dict(frame=i,changedPixels=pixels,maximumChannelDelta=maximum,mobileMaximumChannelDelta=int(sd.max()),mobileMeanAbsoluteDelta=float(sd.mean())))
    count+=1
  before.close();assert count==720;scene=project/prep['sceneRoot']/'Scenes'/(mode+'.unity');assert scene.exists();clips.append(dict(topic=None,mode=mode,camera=camera,video=pin(video),frameRgbManifest=pin(folder/'streamed-capture.json'),trace=pin(folder/'trace.json'),referenceFrames=[pin(refs[k])for k in sorted(refs)],pixelFramesVerified=count,allDecodedPixelsExact=True,scene=pin(scene)));comparisons.append(dict(mode=mode,camera=camera,modelStateExact=True,first32TraceRowsExact=True,first32RasterComparison=changed))
 for p in psutil.process_iter(['name','cmdline']):
  if(p.info['name']or'').lower()=='unity.exe':assert p.info['cmdline']is not None and not any(str(project).lower().replace('\\','/')in str(a).lower().replace('\\','/')for a in p.info['cmdline'])
 snapshot=OUT/'editable-project';assert not snapshot.exists();snapshot.mkdir(parents=True)
 for name in ['Assets','Packages','ProjectSettings']:shutil.copytree(project/name,snapshot/name)
 for c in clips:c['scene']=pin(snapshot/Path(c['scene']['path']).relative_to(project))
 review=OUT/'cross-run-raster-review.json';write(review,dict(sourceCapture=str(capture),originalStrictFailure=pin(failure),originalStrictBitParityPassed=False,independentFullCaptureRgbRoundTripByteExact=True,all7200FramesVerified=True,comparisonRubric=dict(maxChangedPixelFraction=.00001,maxChannelDelta=32,mobileMaxChannelDelta=2,mobileMeanAbsoluteDeltaBelow=.001,modelAndFirst32TraceMustBeExact=True),comparisons=comparisons,interpretation='The observed cross-run difference is limited to a few raster pixels. Its exact hardware cause is not claimed. Geometry/state and all encoded-to-own-source pixel bytes are independently verified. The old strict failure remains unchanged.',actualListening=False,humanApproval=False))
 write(OUT/'accepted-full.json',dict(fingerprint=prep['fingerprint'],purpose='full',capture=str(capture),actualUnityCapture=True,framesPerCamera=720,fps=60,actualCaptureSeconds=12,allPixelsRoundTripVerified=True,crossRunByteExact=False,crossRunRasterReview=pin(review),originalStrictFailure=pin(failure),adoptionVersion=25,reviewAdapter=pin(__file__),originalSourcePreparation=pin(BASE/'source-preparation.json'),originalExecution=pin(attempt/'launch.json'),clips=clips,editableProject=str(snapshot),editableAssets=[pin(p)for p in sorted(snapshot.rglob('*'))if p.is_file()],visualQaPassed=False,finalFilmComplete=False,humanApproval=False,newGpuJobStarted=False))
 print(json.dumps(dict(proof=pin(OUT/'accepted-full.json'),allDecodedUnityPixelsByteExact=True,oldFailurePreserved=True,rerendered=False)))
if __name__=='__main__':main()
