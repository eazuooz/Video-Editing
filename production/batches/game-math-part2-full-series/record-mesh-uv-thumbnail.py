"""Register this directly reviewed, essential delivery thumbnail only."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parents[3]
path='projects/game-math-mesh-uv/publish/assets/thumbnail.png'
p=R/path;digest=hashlib.sha256(p.read_bytes()).hexdigest()
assert digest=='79c76c4f84ca236bda21bfff093937f6886ec0537781f2b0ac2ed6a6b8f954c1'
now=datetime.now(timezone.utc).isoformat()
record={
 'tool':'built-in image_gen','useCase':'ads-marketing','generatedAtUtc':now,
 'original':'C:/Users/eazuo/.codex/generated_images/01a10594-7278-7761-b482-62c0269a3a18/exec-becce9f3-86f9-446d-9790-f77c44b16fd3.png',
 'file':path,'resolution':list(Image.open(p).size),'bytes':p.stat().st_size,'sha256':digest,
 'references':[{'path':'projects/game-math-projection-depth/publish/assets/thumbnail.png','role':'Channel style only; new mesh/normal subject'},
               {'path':'shared/assets/branding/yamyamcoding-cats-original.png','role':'Naturally integrated original calico and white cat identities'}],
 'prompt':'New16:9 illustrated thumbnail. Exact yellow header 게임수학 Part2 · 렌더링⑤, 얌얌코딩. Black 같은 정점인데, red 법선은 왜 다를까?, subtitle 인덱스 · 면 법선 · 정점 법선. Calico teacher points at shared corner with three distinct face-direction arrows on a blue cube; white cat examines an original triangulated rock. White ground,warm illustration,spatial faces and occlusion; no screenshot inset,source-game assets or flowchart.',
 'directVisualReview':{'status':'passed','reviewedAtUtc':now,'evidence':'Generated pixels directly viewed: exact complete Korean headline/header⑤/branding, natural cat identities, coherent cube faces with three outward face directions at the shared corner, separate triangulated rock. Readable at small scale; no screenshot/PPT inset.'},
 'platformSaveVerified':False
}
p.with_name('thumbnail-generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
register=R/'shared/git-essential-images.json';current=json.loads(register.read_text(encoding='utf-8-sig'))
current['entries']=[e for e in current['entries'] if e['path']!=path]
current['entries'].append({'path':path,'purpose':'delivery-thumbnail','reason':'Directly reviewed original illustration for the full mesh/normal lecture; follows the established yellow/white/black/red cat channel identity.','sha256':digest,'reviewedAt':now,'project':'game-math-mesh-uv'})
register.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ignore=R/'.gitignore';text=ignore.read_text(encoding='utf8');exception='!'+path
if exception not in text:ignore.write_text(text.rstrip()+'\n'+exception+'\n',encoding='utf8')
print('Registered one reviewed essential thumbnail; extracted QA images stay local.')
