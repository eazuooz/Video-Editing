from pathlib import Path
import gdown,hashlib,json,time
BASE=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/Sprite-Sheet-Diffusion/ModelTraining/pretrained_model')
BASE.mkdir(parents=True,exist_ok=True)
items=[('1oZq9I4l3QEu6-x7CQbxc5V0XDKY2PbcC','denoising_unet.pth',3438374293),('1wS4X6Pqsw4pwEGtW2etuRrZZd9WjgX3C','reference_unet.pth',3438323817),('1dn00MEEmjjhWAWQK6zJ-L-XUKt_l-XwF','motion_module.pth',1817900227)]
records=[]
for ident,name,size in items:
    dest=BASE/name
    print(json.dumps({'file':name,'stage':'download','expectedBytes':size}),flush=True)
    try:
        if not dest.exists() or dest.stat().st_size!=size:
            gdown.download(id=ident,output=str(dest),quiet=True,use_cookies=False,resume=True,timeout=60,retries=2)
        assert dest.stat().st_size==size,(name,dest.stat().st_size,size)
        h=hashlib.sha256()
        with dest.open('rb') as f:
            for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
        rec={'file':name,'bytes':size,'sha256':h.hexdigest(),'publicSource':'https://drive.google.com/file/d/'+ident+'/view','complete':True}
    except Exception as e:rec={'file':name,'complete':False,'error':str(e)}
    records.append(rec);(BASE/'download-record.json').write_text(json.dumps(records,indent=2),encoding='utf8');print(json.dumps(rec),flush=True)
