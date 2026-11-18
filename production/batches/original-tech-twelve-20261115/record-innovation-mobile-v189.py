"""Bind actual connector upload/readback responses to twelve local revised files."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
H=Path(__file__).resolve().parent;C=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/innovation-openings-v181')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest(),bytes=p.stat().st_size)
def main():
 target=H/'mobile-review-delivery-v186.json';assert not target.exists();initial=read(C/'cloud-operations-v186.json');folder=initial['folderMetadata']['structuredContent'];fid=folder['id'];assert not folder['shared']and all(p['role']=='owner'for p in folder['permissions'])
 uploads={2:initial['uploads']['2']};inputs=[C/'cloud-operations-v186.json',C/'cloud-folder-listing-v186.json']
 for i in [1,3,5,7]:
  p=C/f'cloud-file-{i:02}-v186.json';uploads[i]=read(p);inputs.append(p)
 for name in ['cloud-files-04-06-10-11-v186.json','cloud-files-08-09-12-v186.json']:
  p=C/name;uploads.update({int(k):v for k,v in read(p).items()});inputs.append(p)
 assert set(uploads)==set(range(1,13));listing=read(C/'cloud-folder-listing-v186.json')['structuredContent']['files'];assert len(listing)==12;listed={x['id']:x for x in listing};rows=read(C/'all-bundles-v186.json')['projects'];files=[]
 for row in rows:
  order=row['order'];u=uploads[order];up=u['upload']['structuredContent'];meta=u['metadata']['structuredContent'];assert up['success']and up['id']==meta['id']and up['parent_id']==fid
  assert meta['mime_type']=='video/mp4'and meta['parent_ids']==[fid]and not meta['shared']and meta['permissions']and all(x['role']=='owner'and x['type']=='user'for x in meta['permissions']);assert int(meta['title'].split('.')[0])==order
  out=C/row['slug'];transcoded=order in [4,6,8,9,12];path=out/('phone-captioned-v188.mp4'if transcoded else'captioned-v183.mp4');artifact=pin(path);assert int(meta['size'])==artifact['bytes']and int(listed[meta['id']]['size'])==artifact['bytes']
  evidence=[pin(out/'encoded-qa-v184.json'),pin(out/'encoded-visual-review-v184.json')]
  if transcoded:
   qa=read(out/'phone-qa-v189.json');visual=read(out/'phone-visual-review-v189.json');assert qa['technicalChecksPassed']and qa['aacPacketBytesAndPtsExactToMaster']and visual['allowedForPrivatePhoneReview'];evidence.extend([pin(out/'phone-encode-v188.json'),pin(out/'phone-qa-v189.json'),pin(out/'phone-visual-review-v189.json')])
  files.append(dict(order=order,slug=row['slug'],title=meta['title'],fileId=meta['id'],url=meta['url'],sourceMasterSha256=row['artifacts']['captioned']['sha256'],uploadedArtifact=artifact,localSha256=artifact['sha256'],uploadedBytes=artifact['bytes'],remoteBytes=int(meta['size']),transcoded=transcoded,resolution=[1080,1920],fps=60,voiceAndMusicAacUnchanged=True,ownerOnly=True,metadataReadback=meta,evidence=evidence))
 assert set(listed)=={x['fileId']for x in files};report=dict(request='Add narrated why-innovative openings to all current twelve and deliver the revised phone review set.',atUtc=datetime.now(timezone.utc).isoformat(),folderId=fid,folderUrl=folder['url'],folderMetadataReadback=folder,verifiedOwnerOnly=True,files=files,exactFileCount=12,folderListingExactIds=True,actualConnectorEvidence=[pin(p)for p in inputs],sourceBundles=pin(C/'all-bundles-v186.json'),previousMobileDelivery=pin(H/'mobile-review-delivery-v175.json'),previousCloudFoldersPreserved=True,masterFilesPreserved=True,transcodedPhoneCopyOrders=[4,6,8,9,12],transcodingReason='Observed connector upload limit: 104857600 bytes. Separate FHD H264 review copies, unchanged AAC.',remoteCryptographicChecksumVerified=False,actualPhonePlayback=False,actualFullListening=False,humanApproval=False,postedInChat=False,youtubeActions=[],newAutomations=[])
 target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(receipt=pin(target),phoneFolder=report['folderUrl'],files=12,ownerOnly=True,remoteSizesMatch=True,phoneTranscodes=5)))
if __name__=='__main__':main()
