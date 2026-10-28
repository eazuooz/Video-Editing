"""Compose measured static UI states over authentic Unity world-only clips.

Five official-image/inspection explanation cuts use a plain black2D stage.
All motion/change cues remain in the canonical measured unity-cues.json.
"""
from pathlib import Path
import json,hashlib
import audio_pipeline as a
import ui_compositor as ui
H=Path(__file__).resolve().parent

def prepare(plan,output):
 cues=a.read(H/'unity-cues.json')
 if not cues.get('timingLocked'):raise ValueError('Final UI needs measured locked speech cues')
 return ui.prepare(plan,cues,Path(output)/'explanation-ui')

def render_cut(cut,plan,output,manifest,v):
 row=next(x for x in manifest['cuts'] if x['cutId']==cut['id']);n=cut['frames']
 assert row['frames']==n and row['phases'][0]['startFrame']==0 and row['phases'][-1]['endFrame']==n
 assert all(x['endFrame']==y['startFrame'] for x,y in zip(row['phases'],row['phases'][1:]))
 native=None;inputArgs=[]
 if row['worldRequired']:
  source=a.repo_path(cut['renderedSource']);meta=v.assert_video(source,n)
  if cut.get('renderedStartFrame',0)!=0:raise ValueError('New native scenes begin at frame0')
  request=a.read(source.parent/'request.json');done=a.read(source.parent/'render-success.json')
  if (done.get('status'),done.get('cutId'),done.get('frames'),done.get('completed'))!=('complete',cut['id'],n,n):raise ValueError('Native capture is incomplete or belongs to another cut')
  if done.get('renderRequest')!='RenderPipeline.StandardRequest (D25 world only; editorial UI composited separately)':raise ValueError('Native render is not the approved world-only path')
  if done['compiledSourceFingerprint']!=request['expectedFingerprint']:raise ValueError('Native compiled input mismatch')
  for item in request['sourceFiles']:
   if a.sha(a.repo_path(item['path']))!=item['sha256']:raise ValueError('Frozen native dependency changed after capture: '+item['path'])
  native={'video':a.artifact(source),'request':a.artifact(source.parent/'request.json'),'success':a.artifact(source.parent/'render-success.json'),'scene':done['scene'],'compiledSourceFingerprint':done['compiledSourceFingerprint'],'metadata':meta}
  inputArgs=['-threads','2','-i',str(source)]
 else:
  if cut['variant'] not in ui.PHOTO_VARIANTS:raise ValueError('Only authored photo diagrams may omit native world')
  inputArgs=['-f','lavfi','-i',f'color=c=black:s=1920x1080:r=60:d={n/60:.9f}']
 phases=row['phases'];graph=['[0:v]setpts=N/(60*TB),setsar=1,format=rgba[base0]']
 for i,phase in enumerate(phases):
  asset=phase['image'];source=a.repo_path(asset['path'])
  if a.sha(source)!=asset['sha256']:raise ValueError('Prepared UI PNG changed')
  inputArgs+=['-loop','1','-framerate','60','-i',str(source)]
  begin,end=phase['startFrame']/60,phase['endFrame']/60
  graph.append(f'[{i+1}:v]format=rgba,setpts=N/(60*TB)[ui{i}]')
  graph.append(f"[base{i}][ui{i}]overlay=x=0:y=0:format=auto:enable='gte(t,{begin-1e-8:.9f})*lt(t,{end-1e-8:.9f})'[base{i+1}]")
 # Match the native capture's explicit full-range RGB -> limited BT.709 step.
 # Output metadata alone must not choose the RGB conversion matrix implicitly.
 graph.append(f'[base{len(phases)}]scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,settb=1/60000,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709[out]')
 signature={'cut':cut,'codeSha256':a.sha(Path(__file__)),'pipelineSha256':a.sha(Path(v.__file__)),'uiModuleSha256':a.sha(Path(ui.__file__)),'cueFile':a.artifact(H/'unity-cues.json'),'ui':row,'native':native,'encoder':v.ENCODER}
 # PIL size tuples become JSON arrays in receipts; compare one representation.
 signature=json.loads(json.dumps(signature,ensure_ascii=False))
 destination=Path(output)/(cut['id']+'.mp4');receipt=Path(output)/(cut['id']+'-render.json')
 if destination.exists() and receipt.exists():
  old=a.read(receipt)
  if old.get('signature')==signature and old.get('outputSha256')==a.sha(destination):v.assert_video(destination,n);print(cut['id'],'composite cached',flush=True);return
  raise FileExistsError('Preserve prior completed explanation encode; revise output folder for changed inputs')
 temp=destination.with_suffix('.partial.mp4')
 if temp.exists():raise FileExistsError('Preserve unregistered partial explanation encode')
 v.run([*inputArgs,'-an','-filter_complex',';'.join(graph),'-map','[out]','-frames:v',str(n),*v.ENCODER,'-movflags','+faststart',str(temp)],Path(output)/(cut['id']+'-render.log'))
 v.assert_video(temp,n);temp.replace(destination)
 a.save(receipt,{'signature':signature,'outputSha256':a.sha(destination),'visualMotionReview':'pending exact final pixels','sourceClassification':'explanation','uiPostprocessIndependent':True,'nativeGrayscaleTruth':bool(native)})
 print(cut['id'],n,'frames; native world + measured UI' if native else 'frames; official-image explanation',flush=True)
