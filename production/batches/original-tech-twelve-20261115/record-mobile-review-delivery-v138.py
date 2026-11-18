"""Record the user's explicit owner-private phone review delivery for these twelve."""
from pathlib import Path
import copy, datetime, hashlib, importlib.util, json, sys
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
ROOT=H.parents[2]
KEY='explicitOriginalTechTwelve20261115'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def canonical(d):return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
def main():
    vp=H/'mobile-review-publication-validation-v138.json';assert not vp.exists()
    receipt=H/'mobile-review-delivery-v137.json';d=read(receipt)
    assert len(d['projects'])==12 and [x['order']for x in d['projects']]==list(range(1,13))
    assert d['folder']['ownerOnly']and d['folder']['permissionReadbackVerified']
    assert not d['publicPublication']and not d['actualPhonePlayback']and not d['humanApproval']
    for row in d['projects']:
        meta=row['drive'];assert meta['mime_type']=='video/mp4'and int(meta['size'])==row['source']['bytes']
        assert meta['shared']is False and meta['parent_ids']==[d['folder']['id']]
        assert meta['permissions']and all(x['type']=='user'and x['role']=='owner'for x in meta['permissions'])
    sp=module('mobile_owner_key_splice_v138',H/'finalize-cpu-preparation-v1.py')
    rowsp=module('mobile_owner_row_splice_v138',H/'finish-lockon-revision-ledger-v80.py')
    scopes=[]
    summary=dict(request=d['request'],authorizationScope='Only current exact12 captioned masters to a new owner-only Drive folder for phone review.',
        receipt=pin(receipt),folder=d['folder'],sourceManifest=d['sourceManifest'],verifiedFiles=12,
        originalVideoBytesPreserved=True,transcoding=False,publicPublication=False,
        youtubeActions=[],actualPhonePlayback=False,humanApproval=False,postedInChat=False)
    for name in ['video-production-control.json','video-worklist.json']:
        p=ROOT/'shared/publishing'/name;before=p.read_bytes();raw=before.decode('utf-8-sig');data=json.loads(raw)
        own=copy.deepcopy(data[KEY]);own['mobileReviewDelivery']=summary
        new=sp.replace_value(raw,KEY,own)
        if 'rows'in data:
            for item in d['projects']:
                row=copy.deepcopy(next(x for x in data['rows']if x.get('id')==f"OT12-{item['order']:02d}"))
                row['mobileReviewDelivery']=dict(fileId=item['drive']['id'],url=item['drive']['url'],folderUrl=d['folder']['url'],
                    version=item['version'],sourceSha256=item['source']['sha256'],sourceBytes=item['source']['bytes'],
                    ownerOnly=True,permissionReadbackVerified=True,actualPhonePlayback=False,humanApproval=False,receipt=pin(receipt))
                row['platformStatus']='YouTube 미업로드 / Drive 비공개 폰 검수본 준비'
                new=rowsp.replace_one_row(new,row)
        after=json.loads(new);f1=copy.deepcopy(data);f2=copy.deepcopy(after)
        for x in [f1,f2]:
            x.pop(KEY)
            if 'rows'in x:x['rows']=[row for row in x['rows']if not row.get('id','').startswith('OT12-')]
        assert f1==f2
        assert p.read_bytes()==before
        p.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+new.encode('utf8'))
        scopes.append(dict(path=str(p),ownKeySha256=canonical(after[KEY]),rowSha256=canonical([x for x in after['rows']if x.get('id','').startswith('OT12-')])if'rows'in after else None))
    docscopes=[];start='<!-- ORIGINAL-TECH-TWELVE-20261115 -->';end='<!-- ORIGINAL-TECH-TWELVE-20261115-END -->'
    for name in ['VIDEO_WORKFLOW.md','VIDEO_WORKLIST.md']:
        p=ROOT/'docs'/name;before=p.read_bytes();raw=before.decode('utf-8-sig');a,z=raw.index(start),raw.index(end)+len(end);old=raw[a:z]
        note=f"2026-11-18 사용자의 휴대폰 검수 명시 요청에 따라 최신 v4 목록의 정확12편 자막 포함 완성본을 [폰 검수용 Drive 폴더]({d['folder']['url']})에 01~12번으로 올렸다. 새 폴더와 각 파일의 본인 계정만 접근하는 권한·용량·부모 폴더를 읽어 확인했다. 재인코딩 없이 기존 완성본 바이트를 사용했고 제작 마스터·클린본·KO/EN 자막·원래 검수표·다른 배치를 보존했다. 이 요청 범위의 비공개 검수 전달이며 YouTube 업로드·공개·예약이나 사람 검수 승인을 뜻하지 않는다. 실제 폰 재생은 사용자 확인 대기다. 1번 교토 공연 영상의 기존 공개 채택 보류도 유지한다."
        assert note not in old
        updated=old[:-len(end)].rstrip()+'\n\n'+note+'\n'+end
        new=raw[:a]+updated+raw[z:];assert new[:a]==raw[:a]and new[a+len(updated):]==raw[z:]
        assert p.read_bytes()==before
        p.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+new.encode('utf8'))
        docscopes.append(dict(path=str(p),ownMarkerSha256=hashlib.sha256(updated.encode('utf8')).hexdigest()))
    validation=dict(sourceInputs=[pin(receipt),pin(Path(__file__))],scopedSharedInputs=scopes,scopedDocInputs=docscopes,
        progress=dict(finalVideos=12,mobileReviewVideos=12,ownerOnly=True,originalBytesPreserved=True,humanApproval=False,platformActions=['Exact12 owner-private Drive phone-review delivery requested by user']))
    vp.write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(videos=12,ownerOnly=True,folder=d['folder']['url'],foreignContentPreserved=True,humanApproval=False)))
if __name__=='__main__':main()
