"""Finish the one-row ledger/publication step using already verified media."""
from pathlib import Path
import datetime, hashlib, importlib.util, json, re, subprocess
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

H=Path(__file__).resolve().parent
ROOT=H.parents[2]
SLUG='shorts-oot-ninja-show-z-targeting'
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
R=M/SLUG/'revision-ninja-turns-20261116'
BASE=R/'film-v78'
OUT=R/'local-review-v2'
PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
KEY='explicitOriginalTechTwelve20261115'


def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
    p=Path(p)
    with p.open('rb')as f:d=hashlib.file_digest(f,'sha256').hexdigest()
    return dict(path=str(p.resolve()),sha256=d)
def save(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def canonical(d):return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def replace_one_row(text,row):
    decoder=json.JSONDecoder();pos=re.search(r'"rows"\s*:\s*\[',text).end();changes=[]
    while True:
        while text[pos].isspace()or text[pos]==',':pos+=1
        if text[pos]==']':break
        value,n=decoder.raw_decode(text[pos:])
        if value.get('id')==row['id']:
            replacement=json.dumps(row,ensure_ascii=False,indent=2).replace('\n','\n    ')
            changes.append((pos,pos+n,replacement))
        pos+=n
    assert len(changes)==1
    a,z,replacement=changes[0]
    return text[:a]+replacement+text[z:]


class Links(HTMLParser):
    def __init__(self):super().__init__();self.videos=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='video':self.videos.append(d['src'])
        if tag=='a'and d.get('href','').startswith('file:'):self.links.append(d['href'])


def main():
    complete=R/'revision-complete-v80.json';assert not complete.exists()
    bundle=read(OUT/'bundle-v2.json');baseline=read(H/'local-final-review-manifest-v1.json')
    assert bundle['localRevisionPreviewComplete']and not bundle['publishingApproved']
    for mode in ['pilot','clean']:
        report=read(BASE/(mode+'-encoded-qa.json'))
        assert report['allAutomaticChecksPassed']and report['decodedVideoFrames']==4217
    assert read(BASE/'decoded-reference-equivalence-v75.json')['all32DecodedFramesMatchReviewedComposition']
    encoded=read(BASE/'pilot-encoded-qa.json');assert len(encoded['captionSamples'])==32
    for row in encoded['captionSamples']:assert pin(row['path'])==row
    visual=R/'actual-encoded-visual-review-v80.json'
    save(visual,dict(pilotProof=pin(BASE/'pilot-proof.json'),encodedQa=pin(BASE/'pilot-encoded-qa.json'),
         actualEncodedSamplesInspected=32,displayWidth=375,allFourContactSheetsInspected=True,
         findings=['The live Kyoto show appears before the authored chain explanation, labelled as later reference footage.',
                   'The two-Stalfos excerpt visibly distinguishes the selected opponent and the other enemy waiting; a later disjoint source span shows the next target after defeat.',
                   'All32 caption samples have readable fixed-size captions and source/model labels. The attack-turn model and actual-game examples remain distinct.',
                   'Decoded-reference verification independently confirms complete header/annotation pixels, including repeated areas omitted by the contact-sheet display preview.'],
         actualRealtimePlayback=False,actualFullListening=False,humanApproval=False,publishingApproved=False))
    manifestpath=H/'local-final-review-manifest-v2.json';manifest=read(manifestpath)
    assert manifest['projects'][1:]==baseline['projects'][1:]
    for row in manifest['projects']:
        for record in row['artifacts'].values():
            actual=pin(record['path']);assert actual['sha256']==record['sha256']
            assert Path(record['path']).stat().st_size==record['bytes']
    manifest['latestSelectedRevisionVisualReview']=pin(visual)
    manifest['selectedRevisionPreviewTechnicallyVerified']=True
    manifestpath.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    page=H/'local-final-review-v2.html';text=page.read_text('utf8')
    buttons='<p><button onclick="let v=this.closest(\'section\').querySelector(\'video\');v.currentTime=18.12;v.play()">18초 · 교토 닌자 실사</button> <button onclick="let v=this.closest(\'section\').querySelector(\'video\');v.currentTime=39.96;v.play()">40초 · 다른 적의 공격 대기</button></p>'
    assert '<button'not in text;text=text.replace('<video controls',buttons+'<video controls',1);page.write_text(text,'utf8')
    parser=Links();parser.feed(text);assert len(parser.videos)==12 and len(parser.links)==60
    for uri in parser.videos+parser.links:
        assert Path(unquote(urlparse(uri).path).lstrip('/')).is_file(),uri
    spec=importlib.util.spec_from_file_location('lockon_row_recovery_splice',H/'finalize-cpu-preparation-v1.py')
    sp=importlib.util.module_from_spec(spec);spec.loader.exec_module(sp)
    scopes=[]
    for name in ['video-production-control.json','video-worklist.json']:
        path=ROOT/'shared/publishing'/name;before=path.read_bytes();raw=before.decode('utf-8-sig');data=json.loads(raw)
        own=data[KEY];own.update(status='selected-lockon-private-revision-review-ready',
             automaticAdvanceWithinExactList=False,currentSelectedProject=None,activeRevisionScope=[],completedRevisionScope=[SLUG],
             reviewPage=str(page.relative_to(ROOT)).replace('\\','/'),
             latestSelectedRevision=dict(slug=SLUG,version=bundle['version'],page=str(page.relative_to(ROOT)).replace('\\','/'),
                 bundle=pin(OUT/'bundle-v2.json'),actualEncodedVisualReview=pin(visual),localRevisionPreviewComplete=True,
                 publishingApproved=False,liveShowReusePermissionVerified=False))
        new=sp.replace_value(raw,KEY,own)
        if name=='video-worklist.json':
            row=next(x for x in data['rows']if x['id']=='OT12-01')
            row.update(latestSelectedRevision=own['latestSelectedRevision'],reviewPage=own['reviewPage'],
                       reviewStatus='락온 수정 검수본 준비 / 공연 영상 공개 채택 보류 / 사람 검수 대기')
            new=replace_one_row(new,row)
        after=json.loads(new)
        left=json.loads(raw);right=json.loads(new)
        for d in [left,right]:
            d.pop(KEY,None)
            if 'rows'in d:d['rows']=[x for x in d['rows']if x.get('id')!='OT12-01']
        assert left==right,'Unrelated rows and controls must remain identical'
        assert path.read_bytes()==before,'Concurrent shared edit preserved'
        path.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+new.encode('utf8'))
        scopes.append(dict(path=str(path),ownKeySha256=canonical(after[KEY]),
             rowSha256=canonical([x for x in after.get('rows',[])if x.get('id','').startswith('OT12-')])if'rows'in after else None))
    checkpoint=ROOT/'projects'/SLUG/'production/revision-ninja-turns-v2.json'
    save(checkpoint,dict(status='private-local-revision-preview-complete',bundle=pin(OUT/'bundle-v2.json'),
         reviewPage=pin(page),actualEncodedVisualReview=pin(visual),rawAndMixedAudioUnchanged=True,
         otherElevenPreserved=True,publishingApproved=False,liveShowReusePermissionVerified=False,humanApproval=False,platformActions=[]))
    doc=ROOT/'docs/VIDEO_WORKLIST.md';before=doc.read_bytes();raw=before.decode('utf-8-sig')
    start='<!-- ORIGINAL-TECH-TWELVE-20261115 -->';end='<!-- ORIGINAL-TECH-TWELVE-20261115-END -->'
    a,z=raw.index(start),raw.index(end)+len(end);old=raw[a:z]
    note='락온 사용자 요청 수정본: 교토 닌자 공연 참고 실사와 두 스탈포스의 공격 차례를 추가한 [수정 검수표](../production/batches/original-tech-twelve-20261115/local-final-review-v2.html)를 준비했다. 자막·클린 영상 검사와32개 인코딩 자막 표본 검수를 완료했으며 원음·자막 타이밍과 다른11편은 보존했다. 공연 영상 재사용 허락 미확인으로 수정본은 로컬 검수용이고 공개 채택은 보류한다.'
    replacement=old[:old.index(end)].rstrip()+'\n\n'+note+'\n'+end
    assert doc.read_bytes()==before
    doc.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+(raw[:a]+replacement+raw[z:]).encode('utf8'))
    validation=H/'production-resume-validation-v80.json'
    save(validation,dict(sourceInputs=[pin(p)for p in [Path(__file__),page,manifestpath,checkpoint]],
        scopedSharedInputs=scopes,scopedDocInputs=[dict(path=str(doc),ownMarkerSha256=hashlib.sha256(replacement.encode('utf8')).hexdigest())],
        progress=dict(finalVideos=12,selectedRevisionPreviewComplete=True,publicationHeldForNinjaReusePermission=True),
        actualRevisionEvidence=[pin(OUT/'bundle-v2.json'),pin(visual),pin(BASE/'decoded-reference-equivalence-v75.json')],
        recovery='Only the one-row ledger finalization was repaired. Completed renders, voice, encoded QA and the baseline eleven bundles were reused.',
        humanApproval=False,platformActions=[]))
    receipt=read(R/'production-resume-git-receipt-v75.json');assert receipt['remoteVerified']
    source=(R/'publish-production-resume-v75.py').read_text('utf8')
    expected="parent=='c0aa8b578ba702fc37249ee91a02142fa22cc4f5'";assert expected in source
    source=source.replace('v75','v80').replace(expected,"parent=='"+receipt['commit']+"'")
    source=source.replace('Prepare finite lock-on revision and reviewed source-composition checks','Complete the requested lock-on preview and update only its review ledger row')
    publisher=R/'publish-production-resume-v80.py';assert not publisher.exists();publisher.write_text(source,'utf8')
    result=subprocess.run([str(PY),'-u','-X','utf8',str(publisher)],cwd=ROOT,capture_output=True,text=True,encoding='utf8',creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.returncode==0,result.stderr
    published=read(R/'production-resume-git-receipt-v80.json')
    save(complete,dict(page=pin(page),manifest=pin(manifestpath),bundle=pin(OUT/'bundle-v2.json'),
         actualEncodedVisualReview=pin(visual),localRevisionPreviewComplete=True,publishingApproved=False,
         publishedSourceCommit=published['commit'],humanApproval=False,platformActions=[],
         completedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    (R/'local-preview-status.js').write_text('window.onLockonRevisionStatus&&window.onLockonRevisionStatus('+json.dumps(dict(state='ready',href=page.resolve().as_uri(),publishingApproved=False))+');\n','utf8')
    print(json.dumps(read(complete)))


if __name__=='__main__':main()
