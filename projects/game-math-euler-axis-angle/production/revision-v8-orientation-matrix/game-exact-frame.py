"""Root-authorized finite one-frame native endpoint inspection, CPU only."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import ctypes,json,hashlib
from pathlib import Path
import av

H=Path(__file__).resolve().parent; R=H.parents[3]
P=R/'projects/game-math-euler-axis-angle';G=P/'production/local/revision-v8-orientation-matrix/game'
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
target=60195
plan=json.loads((H/'game-inputs.json').read_text(encoding='utf8'));src=R/plan['source']['sourcePath']
dest=G/'stills/held-translate-end.png';receipt=G/'held-translate-end.json'
if dest.exists():
 assert receipt.exists(),'Never overwrite an unbound frame'
 print(receipt.read_text(encoding='utf8'))
else:
 with av.open(str(src)) as container:
  stream=container.streams.video[0];stream.codec_context.thread_count=1
  container.seek(int((target/60)/float(stream.time_base)),stream=stream,backward=True,any_frame=False)
  selected=None;decoded=0
  for frame in container.decode(stream):
   decoded+=1;assert decoded<=600,'Only a bounded seek window is permitted'
   actual=round(float(frame.pts*frame.time_base)*60)
   if actual==target:selected=frame;break
   assert actual<target,('Exact target frame not found',actual,target)
  assert selected is not None and (selected.width,selected.height)==(1920,1080)
  actual_seconds=float(selected.pts*selected.time_base)
  assert abs(actual_seconds-target/60)<float(stream.time_base)*.51
  selected.to_image().save(dest)
  data=dict(schemaVersion=1,id='held-translate-end',file=dest.relative_to(R).as_posix(),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
    sourceFile=plan['source']['sourcePath'],sourceSha256=plan['source']['sourceSha256'],sourceFrame=target,sourceSeconds=actual_seconds,
    sourcePts=selected.pts,sourceTimeBase=str(selected.time_base),dimensions=[1920,1080],decodedFramesInBoundedSeek=decoded,
    classification='gameplay-derived-analysis',countsAs='explanation',sourceSpeedChanged=False,sourceAudioTouched=False,
    request='Root explicit one-FHD-frame CPU-thread1 endpoint continuity check; no source/full encode/decode.',
    visualReview='pending direct image inspection')
  receipt.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  print(json.dumps(data,ensure_ascii=False))
