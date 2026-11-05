"""Generate editable English candidates only; editorial review precedes episode binding."""
from pathlib import Path
import sys,json,re
B=Path(__file__).resolve().parent;R=B.parents[2]
tools=R/'projects/animation-attack-poses/production/local/series-v1/subtitle-tools'
sys.path.insert(0,str(tools/'packages'))
from transformers import MarianMTModel,MarianTokenizer
import torch
torch.set_num_threads(3);model=MarianMTModel.from_pretrained(str(tools/'model'),local_files_only=True);model.eval()
tokenizer=MarianTokenizer.from_pretrained(str(tools/'model'),local_files_only=True)
work=json.loads((R/'shared/publishing/video-worklist.json').read_text('utf-8-sig'))['rows']
for n in range(6,19):
 ep=f'A{n:02}';slug=next(x['slug'] for x in work if x['id']==ep)
 p=R/'projects'/slug/'production/local/series-v1';p.mkdir(parents=True,exist_ok=True)
 raw=json.loads((B/'scripts'/ep/'narration.ko.json').read_text('utf-8-sig'))
 groups=[]
 for scene in raw['scenes']:
  segments=[s.strip() for l in scene['lines'] for s in re.split(r'(?<=[.!?])\s+',l) if s.strip()]
  with torch.inference_mode():
   x=tokenizer(segments,return_tensors='pt',padding=True,truncation=True)
   pred=model.generate(**x,num_beams=4,max_new_tokens=112)
  strings=tokenizer.batch_decode(pred,skip_special_tokens=True);groups.append(list(zip(segments,strings)))
 (p/'translation-candidates.json').write_text(json.dumps({'status':'draft-only, terminology and factual equivalence unreviewed','model':'Helsinki-NLP/opus-mt-ko-en','groups':groups},ensure_ascii=False,indent=2),encoding='utf-8')
 print('English candidates',ep,flush=True)
