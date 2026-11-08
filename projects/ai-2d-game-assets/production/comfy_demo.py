from pathlib import Path
import json, urllib.request, time, sys, shutil, hashlib
P=Path(__file__).resolve().parents[1]; ROOT=P.parents[1]
T=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/ComfyUI')
sys.path.insert(0,str(ROOT/'qwen3-tts'))
from gpu_handoff_guard import schedule_gpu_handoff
URL='http://127.0.0.1:8191'
def api(route,data=None):
    req=urllib.request.Request(URL+route,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'})
    payload=urllib.request.urlopen(req,timeout=120).read()
    return json.loads(payload) if payload else {}
out=P/'assets/local/comfy'; out.mkdir(parents=True,exist_ok=True)
if not (out/'execution.json').exists():
    while True:
        try:
            schedule_gpu_handoff('ai-2d-game-assets','cuda:0',False,8192)
            break
        except SystemExit as e:
            print(str(e),flush=True);time.sleep(15)
    report=[]
    try:
        for strength in (0.0,0.8):
            tag='base' if strength==0 else 'style08'
            graph={
              '1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':'Illustrious-XL-v0.1.safetensors'}},
              '2':{'class_type':'LoraLoader','inputs':{'model':['1',0],'clip':['1',1],'lora_name':'SakuLike_ILXL.safetensors','strength_model':strength,'strength_clip':strength}},
              '3':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',1],'text':'masterpiece, best quality, full body, solo, adult woman, standing, auburn bob haircut, yellow hairclip, teal jacket, ochre scarf, navy pants, brown boots, brown shoulder bag, simple grey background, game character design'}},
              '4':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',1],'text':'low quality, worst quality, text, watermark, logo, cropped, extra limbs, bad hands, nude, nsfw'}},
              '5':{'class_type':'EmptyLatentImage','inputs':{'width':768,'height':1344,'batch_size':1}},
              '6':{'class_type':'KSampler','inputs':{'model':['2',0],'positive':['3',0],'negative':['4',0],'latent_image':['5',0],'seed':20261108,'steps':24,'cfg':6.0,'sampler_name':'euler_ancestral','scheduler':'normal','denoise':1.0}},
              '7':{'class_type':'VAEDecode','inputs':{'samples':['6',0],'vae':['1',2]}},
              '8':{'class_type':'SaveImage','inputs':{'images':['7',0],'filename_prefix':'yamyam-ai2d-'+tag}}
            }
            (P/f'production/comfy-{tag}-api.json').write_text(json.dumps(graph,indent=2),encoding='utf-8')
            start=time.time(); pid=api('/prompt',{'prompt':graph,'client_id':'yamyam-ai2d'})['prompt_id']
            print('Queued',tag,pid,flush=True)
            while True:
                hist=api('/history/'+pid)
                if pid in hist: break
                time.sleep(3)
            h=hist[pid]
            if h.get('status',{}).get('status_str')=='error': raise RuntimeError(h)
            img=h['outputs']['8']['images'][0]
            source=T/'output'/img['subfolder']/img['filename']
            target=out/(tag+'.png');shutil.copy2(source,target)
            report.append({'tag':tag,'promptId':pid,'elapsed':time.time()-start,'strength':strength,'seed':20261108,'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'history':h})
            print('Completed',tag,round(time.time()-start,1),flush=True)
        (out/'execution.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    finally:
        api('/free',{'unload_models':True,'free_memory':True})
else: print('Existing demo execution retained')
