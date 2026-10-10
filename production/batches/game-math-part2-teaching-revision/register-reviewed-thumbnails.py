from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
registry=ROOT/'shared/git-essential-images.json';r=json.loads(registry.read_text(encoding='utf8'))
for slug in ['game-math-quaternion-foundations-v2','game-math-quaternion-calculations-v2']:
 path=f'projects/{slug}/publishing/thumbnail-v2.png';file=ROOT/path
 review=ROOT/f'shared/output/game-math-part2-teaching-revision/qa/{slug}-thumbnail-mobile.jpg'
 prompt=ROOT/f'projects/{slug}/publishing/thumbnail-prompt.json';p=json.loads(prompt.read_text(encoding='utf8'))
 p['deliveryVersion']=path;p['deliveryPixels']=[1280,720]
 p['review']['mobileReview']=True;p['review']['mobileReviewPixels']=[480,270]
 p['review']['observations']='Exact Korean headline and channel branding directly viewed at 480×270; toy-plane and cat comparison remain recognizable. Episode2 misleading X/Y arrows removed in the preserved generated edit.'
 prompt.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 entry={'path':path,'purpose':'delivery-thumbnail','reason':'Directly viewed final 1280×720 and mobile480×270 illustration: yellow channel strip, white ground, readable Korean headline, natural cat/toy-plane concept; no footage inset.','sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'reviewedAt':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'project':slug}
 r['entries']=[x for x in r['entries'] if x['path']!=path]+[entry]
 ignore=ROOT/'.gitignore';text=ignore.read_text(encoding='utf8');exception='!/'+path
 if exception not in text.splitlines():ignore.write_text(text.rstrip()+'\n'+exception+'\n',encoding='utf8')
registry.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Registered only the two directly reviewed delivery thumbnails; reproducible QA/source frames remain local.')
