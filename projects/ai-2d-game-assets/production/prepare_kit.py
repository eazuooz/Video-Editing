from pathlib import Path
import json,urllib.request,shutil,zipfile,hashlib
P=Path(__file__).resolve().parents[1];L=P/'production/local';K=L/'demo-kit';K.mkdir(exist_ok=True)
graph=json.loads((P/'production/comfy-style08-api.json').read_text('utf-8'))
info=json.load(urllib.request.urlopen('http://127.0.0.1:8191/object_info'))
links=[];nodes=[];lid=1
pos={'1':[20,20],'2':[380,20],'3':[760,20],'4':[760,250],'5':[380,440],'6':[1140,180],'7':[1540,180],'8':[1870,180]}
for nid,rec in graph.items():
 typ=rec['class_type'];desc=info[typ];required=desc['input']['required'];inputs=[];widgets=[]
 for name,definition in required.items():
  value=rec['inputs'][name]
  if isinstance(value,list):
   origin,slot=value;otype=info[graph[origin]['class_type']]['output'][slot]
   inputs.append({'name':name,'type':otype,'link':lid});links.append([lid,int(origin),slot,int(nid),len(inputs)-1,otype]);lid+=1
  else:
   widgets.append(value)
   if name=='seed':widgets.append('fixed')
 outputs=[{'name':(desc.get('output_name') or desc['output'])[i],'type':o,'links':None,'slot_index':i} for i,o in enumerate(desc.get('output',[]))]
 nodes.append({'id':int(nid),'type':typ,'pos':pos[nid],'size':[320,210 if typ=='KSampler' else 180],'flags':{},'order':int(nid)-1,'mode':0,'inputs':inputs,'outputs':outputs,'properties':{'Node name for S&R':typ},'widgets_values':widgets})
for link in links:
 output=next(n for n in nodes if n['id']==link[1])['outputs'][link[2]]
 if output['links'] is None:output['links']=[]
 output['links'].append(link[0])
workflow={'last_node_id':8,'last_link_id':lid-1,'nodes':nodes,'links':links,'groups':[],'config':{},'extra':{'ds':{'scale':.75,'offset':[20,40]}},'version':.4}
(P/'production/comfy-style08-workflow.json').write_text(json.dumps(workflow,ensure_ascii=False,indent=2)+'\n','utf-8')
for src in [P/'production/comfy-style08-api.json',P/'production/comfy-style08-workflow.json',P/'production/comfy-base-api.json',P/'sources/ASSET_PROVENANCE.md']:
 shutil.copy2(src,K/src.name)
for rel in ['character-turnaround-v1.png','character-palette24.png','workshop-generated-v1.png','workshop-pixeloe.png','comfy/base.png','comfy/style08.png','comfy/style08-nearest.png','comfy/style08-pixeloe.png','pixelbolt/forest-spirit.png','pixelbolt/forest-spirit.atlas.json','pixelbolt/forest-spirit.pixel.json','pixelbolt-sunset/sunset-spirit.png','pixelbolt-sunset/sunset-spirit.atlas.json','pixelbolt-sunset/sunset-spirit.pixel.json','pixelfx/fire/torch/torch.png','pixelfx/fire/torch/torch.json','pixelfx/melee/sword-slash/sword-slash.png','pixelfx/melee/sword-slash/sword-slash.json','pixelfx/ice/frost-nova/frost-nova.png','pixelfx/ice/frost-nova/frost-nova.json']:
 dest=K/'assets'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/'assets/local'/rel,dest)
for src in (P/'sources/licenses').glob('*'):
 d=K/'licenses'/src.name;d.parent.mkdir(exist_ok=True);shutil.copy2(src,d)
text='''# AI 2D asset video · demonstration kit

This kit contains the real outputs shown in the video, actual ComfyUI API graphs, and a UI workflow generated from the running server's node schema. Model weights are not included. No trained character LoRA is included or claimed.

## Reproduce the style comparison
1. Install ComfyUI using its official instructions.
2. Download Illustrious XL v0.1 and PixelArt SakuLike ILXL v0.1 from the links in the source ledger. Read the exact model/data/output conditions.
3. Put the files in models/checkpoints and models/loras. Use the names from the workflow, or select your actual file names in its nodes.
4. Load comfy-style08-workflow.json. The API graphs are also supplied for programmatic runs.
5. Keep seed20261108,768x1344,24steps,CFG6,euler_ancestral,normal. Compare both LoRA strengths0 and0.8.
6. Downscale the resulting image deliberately. The 8x example belongs to this LoRA's described pixel scale; it is not a general rule.

## Asset conventions
Character:96x168, hard alpha,20visible colors after a24-color maximum quantization. Workshop:426x240. The generated source images are retained for comparison.
Pixelbolt spirit:24x24 base frames; read the atlas metadata and animation sequence, not a guessed fixed FPS. pixelfx exports also contain their real frame durations and frame rectangles. Use Point/Nearest for crisp pixel enlargement.

## Rights and execution
pixelfx and Pixelbolt code/example artwork notices are in licenses. Generated character and workshop assets were created for this production. Other tools discussed in the video are not bundled. Read ASSET_PROVENANCE.md and the project source ledger for tested versus illustrated operations. Keep provider terms and model/data rights separate from the code license.
'''
(K/'README.md').write_text(text,'utf-8');(P/'production/DEMO_KIT.md').write_text(text,'utf-8')
shutil.copy2(P/'production/DEMO_KIT.ko.md',K/'README.ko.md')
archive=L/'ai-2d-demo-kit.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in K.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(K).as_posix())
print('Prepared kit',archive.stat().st_size,'bytes; UI nodes',len(nodes),'links',len(links))
