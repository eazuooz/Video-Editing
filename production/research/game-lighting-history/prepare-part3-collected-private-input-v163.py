"""Prepare one verified collected captioned input and the essential thumbnail."""
from pathlib import Path
import importlib.util, shutil
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=m.ROOT/'projects/game-lighting-history-04-3';p=base/'publishing'
receipt=m.read(p/'youtube-upload.json');delivery=m.read(base/'production/delivery-output.json')
qa=m.read(m.ROOT/'projects/game-lighting-history-04/production/part3-final-qa-v162.json')
assert qa['qaApproved'] and len(delivery['files'])==4
for f in delivery['files']:
 assert m.sha(m.ROOT/delivery['directory']/f['name'])==f['sha256']
captioned=next(f for f in delivery['files'] if f['name'].endswith('.captioned.mp4'))
assert captioned['sha256']==qa['captionedSha256'] and receipt['cleanUploadAllowed'] is False
source=m.ROOT/receipt['thumbnail']['path'];target=p/'thumbnail-v1.png'
assert m.sha(source)==receipt['thumbnail']['sha256']
if target.exists(): assert m.sha(target)==m.sha(source)
else: shutil.copyfile(source,target)
entry=dict(path=m.rel(target),purpose='delivery-thumbnail',reason='One reviewed illustrated delivery thumbnail for physical rendering-history04-3: yellow YamyamCoding header, readable black/red Korean headline and cat inspecting geometry/pixels; no video inset. Parent preparation duplicate and all QA images remain local.',reviewedAt=m.stamp(),sha256=m.sha(target))
reg=m.ROOT/'shared/git-essential-images.json';j=m.read(reg)
found=[r for r in j['entries'] if r['path']==entry['path']]
if found: assert found[0]['sha256']==entry['sha256']
else: j['entries'].append(entry);m.save(reg,j)
ignore=base/'.gitignore';assert not ignore.exists();ignore.write_text('# Only the directly reviewed delivery thumbnail is essential.\n!/publishing/thumbnail-v1.png\n','utf-8')
receipt.update(collected=True,status='reviewed-collected-ready-for-one-private-captioned-upload',uploadSha256=captioned['sha256'],deliveryEvidence=m.rel(base/'production/delivery-output.json'))
receipt['thumbnail']['preparedParentPath']=receipt['thumbnail']['path'];receipt['thumbnail']['path']=m.rel(target)
receipt['privacyStatus']='private';receipt['scheduled']=False
m.save(p/'youtube-upload.json',receipt)
cp=m.read(m.ROOT/'production/research/game-lighting-history/checkpoint.json');cp['updatedAt']=m.stamp();cp['episode04Part3CollectedV163']=dict(slug=receipt['slug'],delivery=m.rel(base/'production/delivery-output.json'),qaApproved=True,collected=True,actualVideoId=None,uploaded=False,next='Single private captioned upload via CUA; saved settings and CC-off pixels; selective normal Git push.')
m.save(m.ROOT/'production/research/game-lighting-history/checkpoint.json',cp)
print(m.json.dumps(dict(collected=True,captionedSha256=captioned['sha256'],essentialImage=entry,uploaded=False)))
