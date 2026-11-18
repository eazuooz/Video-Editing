"""Record verified Drive copies and point the exact-twelve review at one private folder."""
from pathlib import Path
import copy,hashlib,html,importlib.util,json,re
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
KEY='explicitOriginalTechTwelve20261115'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))

def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())

def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')

def canonical(d):return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
 plan=read(M/'mobile-unified-v175-plan.json');checks=read(M/'mobile-unified-v175-readbacks.json');listing=read(M/'mobile-unified-v175-folder-list.json')['structuredContent']['files'];folder=checks[0]['metadata'];old=read(H/'local-final-review-manifest-v6.json')
 assert len(checks)==13 and len(listing)==12 and [r['order']for r in plan['rows']]==list(range(1,13))
 assert set(x['id']for x in listing)==set(x['metadata']['id']for x in checks[1:])
 assert folder['shared']is False and all(p['role']=='owner'and p['type']=='user'for p in folder['permissions'])
 rows=[]
 for r,c in zip(plan['rows'],checks[1:]):
  meta=c['metadata'];source=old['projects'][r['order']-1]['artifacts']['captioned'];assert source==r['source'] and pin(source['path'])['sha256']==source['sha256']
  assert meta['title']==r['copyName'] and int(meta['size'])==source['bytes'] and meta['parent_ids']==[folder['id']] and meta['mime_type']=='video/mp4' and meta['shared']is False and all(p['role']=='owner'and p['type']=='user'for p in meta['permissions'])
  assert meta['id']!=r['originalDrive']['id']
  rows.append(dict(order=r['order'],title=r['title'],version=r['version'],source=source,originalDrive=r['originalDrive'],sourceMetadataReadback=r['sourceCurrentMetadata'],drive=meta,copyReceipt=pin(M/f'mobile-unified-v175-copy-{r["order"]:02}.json')))
 assert rows[1]['version']=='mario-title-and-paired-fixed-camera-v171' and rows[1]['originalDrive']['id']=='1XNShrw57mupJdOf_flYVaZEkfQ3ew9zB'
 receipt=H/'mobile-review-delivery-v175.json'
 save(receipt,dict(request=plan['request'],sourceManifest=pin(H/'local-final-review-manifest-v6.json'),folder=dict(id=folder['id'],url=folder['url'],name=folder['title'],ownerOnly=True,permissionReadbackVerified=True,actualMetadata=folder),projects=rows,folderListing=pin(M/'mobile-unified-v175-folder-list.json'),readbacks=pin(M/'mobile-unified-v175-readbacks.json'),count=12,latestSecondIncluded=True,fileNumbers=list(range(1,13)),suggestedPhoneSort='name-ascending',serverSideCopies=True,originalFilesAndFoldersPreserved=True,videoBytesReencoded=False,remoteSizeAndParentsVerified=True,remoteChecksumsVerified=False,actualPhonePlayback=False,humanApproval=False,publicPublication=False))
 manifest=copy.deepcopy(old);manifest.update(schemaVersion=7,previousDeliveredManifest=pin(H/'local-final-review-manifest-v6.json'),mobileFolder=folder['url'],mobileUnifiedDelivery=pin(receipt),mobileSelectedRevisionUrl=rows[1]['drive']['url'],deliveryPostedInChat=False)
 for row,mobile in zip(manifest['projects'],rows):row['mobileReviewUrl']=mobile['drive']['url']
 for a,b in zip(old['projects'],manifest['projects']):
  x,y=copy.deepcopy(a),copy.deepcopy(b);x.pop('mobileReviewUrl',None);y.pop('mobileReviewUrl',None);assert x==y
 mp=H/'local-final-review-manifest-v7.json';save(mp,manifest)
 text=(H/'local-final-review-v6.html').read_text('utf8').replace('검수표 v6','검수표 v7')
 text=text.replace('<p><a class="button" href="'+old['mobileSelectedRevisionUrl']+'">폰으로 최신2번 좌우 비교본 보기</a></p>','<p><a class="button" href="'+folder['url']+'">폰으로 최신12편 순서대로 검수하기</a></p><p>최신2번 수정본 포함 · 파일명01~12 · 폰에서 이름순(오름차순)으로 확인하세요.</p>')
 for r in rows:
  order=r['order'];url=html.escape(r['drive']['url']);pattern=rf'(<section id="v{order}">.*?</h2>)'
  text,n=re.subn(pattern,lambda m:m.group(1)+f'<p><a class="button" href="{url}">폰으로 {order:02}번 보기</a></p>',text,count=1,flags=re.S);assert n==1
 text=text.replace(old['mobileSelectedRevisionUrl'],rows[1]['drive']['url']).replace(Path(H/'local-final-review-manifest-v6.json').as_uri(),mp.as_uri()).replace(Path(H/'local-final-review-v5.html').as_uri(),Path(H/'local-final-review-v6.html').as_uri()).replace('이전 검수표 v5','이전 검수표 v6')
 assert folder['url']in text and text.count('<video ')==12
 page=H/'local-final-review-v7.html';assert not page.exists();page.write_text(text,'utf8')
 spec=importlib.util.spec_from_file_location('only_own_mobile_key175',H/'finalize-cpu-preparation-v1.py');sp=importlib.util.module_from_spec(spec);spec.loader.exec_module(sp);scopes=[]
 for name in ['video-production-control.json','video-worklist.json']:
  p=ROOT/'shared/publishing'/name;before=p.read_bytes();raw=before.decode('utf-8-sig');data=json.loads(raw);own=copy.deepcopy(data[KEY]);own.update(reviewPage=str(page.relative_to(ROOT)).replace('\\','/'),progressPage=str(page.relative_to(ROOT)).replace('\\','/'))
  own['latestUnifiedMobileReview']=dict(receipt=pin(receipt),folderUrl=folder['url'],count=12,latestSecondIncluded=True,numberedOrder='01..12',ownerOnly=True,originalCloudFilesPreserved=True,actualPhonePlayback=False,humanApproval=False)
  updated=sp.replace_value(raw,KEY,own);after=json.loads(updated);a,b=copy.deepcopy(data),copy.deepcopy(after);a.pop(KEY);b.pop(KEY);assert a==b;assert p.read_bytes()==before;p.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+updated.encode('utf8'));scopes.append(dict(path=str(p),ownKeySha256=canonical(own),rowSha256=None))
 sources=[Path(__file__),receipt,mp,page]
 save(H/'mobile-unified-validation-v175.json',dict(sourceInputs=[pin(p)for p in sources],scopedSharedInputs=scopes,scopedDocInputs=[],sourceManifest=pin(H/'local-final-review-manifest-v6.json'),allTwelveArtifactVersionsAndBytesPreserved=True,allRowsAndForeignKeysPreserved=True,latestSecondIncluded=True,privateFolderReadbackVerified=True,exactlyTwelveCopiedVideosVerified=True,progress=dict(finalVideos=12,mobileVideos=12,renderedVideos=0,latestSecondIncluded=True,phoneReviewReady=True,humanApproval=False),platformActions=['copy-exact-twelve-into-one-owner-private-review-folder']))
 print(json.dumps(dict(folderUrl=folder['url'],phoneVideos=12,latestSecondIncluded=True,localReview=str(page),newRenders=0)))

if __name__=='__main__':main()
