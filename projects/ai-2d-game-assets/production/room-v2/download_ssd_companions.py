from pathlib import Path
import requests,json,hashlib
BASE=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/Sprite-Sheet-Diffusion/ModelTraining/pretrained_model')
items=[
('https://huggingface.co/patrolli/AnimateAnyone/resolve/main/pose_guider.pth','moore_pose_guider.pth'),
('https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/unet/config.json','stable-diffusion-v1-5/unet/config.json'),
('https://huggingface.co/stabilityai/sd-vae-ft-mse/resolve/main/config.json','sd-vae-ft-mse/config.json'),
('https://huggingface.co/stabilityai/sd-vae-ft-mse/resolve/main/diffusion_pytorch_model.safetensors','sd-vae-ft-mse/diffusion_pytorch_model.safetensors'),
('https://huggingface.co/lambdalabs/sd-image-variations-diffusers/resolve/main/image_encoder/config.json','image_encoder/config.json'),
('https://huggingface.co/lambdalabs/sd-image-variations-diffusers/resolve/main/image_encoder/pytorch_model.bin','image_encoder/pytorch_model.bin')]
records=[]
for url,name in items:
 dest=BASE/name;dest.parent.mkdir(parents=True,exist_ok=True);part=dest.with_suffix(dest.suffix+'.part')
 print(json.dumps({'file':name,'stage':'download'}),flush=True)
 try:
  if not dest.exists():
   with requests.get(url,stream=True,timeout=90) as r:
    r.raise_for_status()
    with part.open('wb') as f:
     for b in r.iter_content(4*1024*1024):f.write(b)
   part.replace(dest)
  h=hashlib.sha256()
  with dest.open('rb') as f:
   for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
  rec={'file':name,'url':url,'bytes':dest.stat().st_size,'sha256':h.hexdigest(),'complete':True}
 except Exception as e:rec={'file':name,'url':url,'complete':False,'error':str(e)}
 records.append(rec);(BASE/'companion-download-record.json').write_text(json.dumps(records,indent=2),encoding='utf8');print(json.dumps(rec),flush=True)
