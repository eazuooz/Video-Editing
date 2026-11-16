"""Remove confirmed recorder commentary from NEW excerpts; retain residual game effects."""
import os,math,subprocess
os.environ['CUDA_VISIBLE_DEVICES']=''
from prepare import *
def main():
 import torch,torchaudio,numpy as np,soundfile as sf
 torch.set_num_threads(8)
 bundle=torchaudio.pipelines.HDEMUCS_HIGH_MUSDB_PLUS;model=bundle.get_model().to('cpu').eval();sr=bundle.sample_rate;vocal=model.sources.index('vocals')
 sources=read(HERE/'sources.json');plan=read(HERE/'plan.json');voices={x['key']:x for x in read(HERE/'voice.json')['items']};folder=pathlib.Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingWork/game-math-concept-examples-20261116/source-audio';folder.mkdir(parents=True,exist_ok=True)
 unique={};mapping={};records=[]
 for e in plan['episodes']:
  for s in e['inserts']:
   if s['source'] not in ('showroom','maker','train'):continue
   duration=max(voices[s['key']]['seconds']+.6,min(18,s['sourceOut']-s['sourceIn']));frames=math.ceil(duration*60-1e-7);key=(s['source'],s['sourceIn'],frames);unique.setdefault(key,[]).append(s['key'])
 for (src,start,frames),keys in unique.items():
  row=sources[src];duration=frames/60;path=folder/(f'{src}-{start:.3f}-{frames}.wav');meta=path.with_suffix('.json')
  if meta.exists() and path.exists() and read(meta).get('sha256')==sha(path):record=read(meta)
  else:
   a=max(0,start-1);z=min(row['duration'],start+duration+1)
   data=subprocess.check_output([FF,'-v','error','-nostdin','-threads','1','-ss',str(a),'-t',str(z-a),'-i',row['file'],'-map','0:a:0','-af','loudnorm=I=-23:TP=-3:LRA=11','-ac','2','-ar',str(sr),'-f','f32le','-'],creationflags=subprocess.CREATE_NO_WINDOW)
   mix=torch.from_numpy(np.frombuffer(data,dtype='<f4').copy().reshape(-1,2).T.copy());ref=mix.mean(0);mu=ref.mean();std=ref.std().clamp_min(1e-6);x=(mix-mu)/std
   length=x.shape[-1];chunk=8*sr;overlap=sr;hop=chunk-overlap;acc=torch.zeros((2,length));weight=torch.zeros(length)
   for offset in range(0,length,hop):
    end=min(length,offset+chunk);part=x[:,offset:end];valid=part.shape[-1]
    if valid<chunk:part=torch.nn.functional.pad(part,(0,chunk-valid))
    with torch.inference_mode():estimate=model(part[None])[0,vocal,:,:valid]
    w=torch.ones(valid)
    if offset>0:
     n=min(overlap,valid);w[:n]=torch.linspace(0,1,n)
    if end<length:
     n=min(overlap,valid);w[-n:]=torch.linspace(1,0,n)
    acc[:,offset:end]+=estimate*w;weight[offset:end]+=w
    if end==length:break
   vocals=acc/weight.clamp_min(1e-6)*std
   # Subtraction, rather than summing musical stems, keeps unmodeled game SFX.
   bed=mix-vocals;begin=round((start-a)*sr);count=frames*(sr//60);bed=bed[:,begin:begin+count];assert bed.shape[-1]==count
   sf.write(path,bed.T.numpy(),sr,subtype='FLOAT')
   record=dict(path=str(path),sha256=sha(path),source=src,sourceSha256=row['sha256'],sourceIn=start,frames=frames,seconds=frames/60,sampleRate=sr,alreadyNormalizedBeforeSeparation=True,originalRecordingTargetLufs=-23,noPostSeparationBoost=True,method='CPU TorchAudio HDEMUCS_HIGH_MUSDB_PLUS; subtract estimated vocal stem from original, preserve residual game effects',samples=count,remainingRmsDbfs=float(20*torch.log10(bed.square().mean().sqrt().clamp_min(1e-12))),humanListening=False)
   save(meta,record)
  records.append(record)
  for key in keys:mapping[key]=record
  print('Recorder voice separated',src,start,'for',','.join(keys),flush=True)
 save(HERE/'speech-free-game-audio.json',dict(status='prepared-awaiting-residual-audio-review',model='TorchAudio HDEMUCS_HIGH_MUSDB_PLUS',device='cpu',reference='https://docs.pytorch.org/audio/stable/tutorials/hybrid_demucs_tutorial.html',items=mapping,uniqueExcerpts=records,limitation='Vocal separation is estimated, not guaranteed perfect isolation; residual content and actual final mix must be reviewed. No synthetic replacement SFX or lecture BGM.'))
if __name__=='__main__':main()
