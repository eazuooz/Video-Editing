"""Register only the two directly reviewed essential delivery thumbnails."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
entries=[('game-math-plane-distances-v2','03a67467710f46c2b4ca9c928d407d1e0080f8c5667a874b024572f8840b3206','exec-744b24e2-e622-43d1-a895-dfb00a285991.png','Finite floating platform, perpendicular distance and normal; illustrated cat naturally observes the diagram.'),('game-math-triangle-addresses-v2','1c1632dda761e337a86c05ae3f9ddc8ba8865df9957cf6d6fcd018c73b4aa9ab','exec-c4fd8148-60c0-4723-be32-1a6ade84901b.png','Three colored anchors and an interior point on a finite triangular platform; integrated illustrated cat; no video inset.')]
p=ROOT/'shared/git-essential-images.json';r=json.loads(p.read_text(encoding='utf8'));ignore=ROOT/'.gitignore';text=ignore.read_text(encoding='utf8')
for slug,digest,source,concept in entries:
 path=f'projects/{slug}/publishing/thumbnail-v2.png';f=ROOT/path;assert hashlib.sha256(f.read_bytes()).hexdigest()==digest
 proof={'reviewedAt':datetime.datetime.now().astimezone().isoformat(),'path':path,'sha256':digest,'sourceImage':f'C:/Users/eazuo/.codex/generated_images/01a10594-7278-7761-b482-62c0269a3a18/{source}','directGeneratedImagePixelsViewed':True,'concept':concept,'branding':'얌얌코딩 / 게임수학 Part2','style':'yellow header; white ground; large black/red Korean headline; illustrated scene','videoInset':False,'approvedForDeliveryThumbnail':True}
 (ROOT/f'projects/{slug}/publishing/thumbnail-review.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 if not any(x['path']==path for x in r['entries']):r['entries'].append({'path':path,'purpose':'delivery-thumbnail','reason':concept,'sha256':digest,'reviewedAt':proof['reviewedAt'],'project':slug})
 exception='!/'+path
 if exception not in text.splitlines():text+='\n'+exception+'\n'
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');ignore.write_text(text,encoding='utf8')
for slug,*_ in entries:
 mpath=ROOT/f'projects/{slug}/project.json';m=json.loads(mpath.read_text(encoding='utf8'));m['lecture'].update(part=m['lecture']['episode'],totalParts=2,baseline='game-math-planes-barycentric');mpath.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Only two reviewed essential thumbnails registered; auxiliary render/review images remain local.')
