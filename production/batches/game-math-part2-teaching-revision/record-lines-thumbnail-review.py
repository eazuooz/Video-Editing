"""Register only the two directly reviewed essential delivery thumbnails."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
entries=[('game-math-lines-circles-v2','28d9f4639762c93a5ff21794dedaa8bdc4394e610a9dd5b45f1c5faa100d2c5e','exec-4902885b-23e9-4ff9-a20a-c1e047d09194.png','Connection from two points, with a midpoint and circle; naturally integrated illustrated cat.'),('game-math-bounds-transform-v2','8e1b80c94d0b58e5d34105b9b667aa093fcb96674197913ee79309e2abed7297','exec-cd522eaa-15cc-45a7-ad02-5992a66fb920.png','Before/after rotation with a newly enclosing blue box and illustrated cat; no video inset.')]
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
 mpath=ROOT/f'projects/{slug}/project.json';m=json.loads(mpath.read_text(encoding='utf8'));m['lecture'].update(part=m['lecture']['episode'],totalParts=2,baseline='game-math-lines-bounds');mpath.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Only two reviewed essential thumbnails registered; auxiliary render/review images remain local.')
