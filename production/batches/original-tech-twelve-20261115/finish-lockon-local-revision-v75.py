"""One finite requested revision: guarded renders and verified local preview only."""
from pathlib import Path
import datetime, hashlib, html, importlib.util, json, math, shutil, subprocess

import av
import numpy as np
import psutil
from PIL import Image

H = Path(__file__).resolve().parent
ROOT = H.parents[2]
SLUG = 'shorts-oot-ninja-show-z-targeting'
M = Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
R = M / SLUG / 'revision-ninja-turns-20261116'
BASE = R / 'film-v78'
OUT = R / 'local-review-v2'
PY = ROOT / 'qwen3-tts/.venv/Scripts/python.exe'
KEY = 'explicitOriginalTechTwelve20261115'
CREDIT = 'Wholesome Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/'


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def pin(p):
    p = Path(p)
    with p.open('rb') as f:
        sha = hashlib.file_digest(f, 'sha256').hexdigest()
    return dict(path=str(p.resolve()), sha256=sha, bytes=p.stat().st_size)


def bare(p):
    return {k: v for k, v in pin(p).items() if k != 'bytes'}


def save(p, value):
    p = Path(p); assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def review_status(state, page=None):
    data=dict(state=state,publishingApproved=False)
    if page is not None:data['href']=page.resolve().as_uri()
    (R/'local-preview-status.js').write_text('window.onLockonRevisionStatus&&window.onLockonRevisionStatus('+json.dumps(data)+');\n','utf8')


def execute(helper, args, name, required):
    if required.exists():
        return
    log = R / ('revision-'+name+'-v75.log'); assert not log.exists()
    with log.open('w', encoding='utf8') as f:
        code = subprocess.run([str(PY), '-u', '-X', 'utf8', str(H/helper), *args],
                              cwd=ROOT, stdin=subprocess.DEVNULL, stdout=f,
                              stderr=subprocess.STDOUT,
                              creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS).returncode
    assert code == 0 and required.exists(), f'Stage held; preserve actual output and {log}'


def verify_reference_equivalence():
    observation = read(R/'preencode-visual-review-v75.json')
    references = read(R/'preencode-reference-v79/evidence.json')
    proof = read(BASE/'pilot-proof.json')
    assert observation['all32ComposedCaptionFramesReviewed']
    assert observation['referenceEvidence'] == bare(R/'preencode-reference-v79/evidence.json')
    assert proof['fingerprint'] == references['fingerprint']
    wanted = {x['frame']: x for x in references['records']}
    assert len(wanted) == 32
    results = []
    with av.open(proof['video']['path']) as c:
        for index, frame in enumerate(c.decode(c.streams.video[0])):
            if index not in wanted:
                continue
            row = wanted[index]; source = Path(row['image']['path'])
            assert bare(source) == row['image']
            expected = np.asarray(Image.open(source).convert('RGB'), dtype=np.float32)
            actual = frame.to_ndarray(format='rgb24').astype(np.float32)
            regions = dict(full=(0,0,1080,1920), body=(0,396,984,1380),
                           header=(0,100,984,390), caption=(0,1450,984,1750),
                           upperAnnotation=(0,430,984,570), lowerAnnotation=(0,1220,984,1380))
            metrics = {}
            for key,(x1,y1,x2,y2) in regions.items():
                mse = float(np.mean((actual[y1:y2,x1:x2]-expected[y1:y2,x1:x2])**2))
                psnr = 100.0 if mse == 0 else 10*math.log10(255**2/mse)
                threshold = 33 if key=='full' else 31 if key=='body' else 29
                assert psnr >= threshold, (row['cueIndex'], key, psnr, threshold)
                metrics[key] = dict(mse=mse,psnrDb=psnr,minimumPsnrDb=threshold)
            results.append(dict(cueIndex=row['cueIndex'],frame=index,regions=metrics))
    assert len(results) == 32
    path = BASE/'decoded-reference-equivalence-v75.json'
    save(path, dict(pilotProof=bare(BASE/'pilot-proof.json'),
                    referenceEvidence=bare(R/'preencode-reference-v79/evidence.json'),
                    sourceVisualReview=bare(R/'preencode-visual-review-v75.json'),
                    all32DecodedFramesMatchReviewedComposition=True,results=results,
                    actualHumanViewingOfNewEncodedFrames=False,humanApproval=False))
    save(BASE/'pilot-visual-review.json',dict(
        pilotProof=bare(BASE/'pilot-proof.json'),encodedQa=bare(BASE/'pilot-encoded-qa.json'),
        referenceEquivalence=bare(path),allowedForFinalBundle=True,
        technicalApprovalBasis='All32 manually reviewed source compositions matched by decoded new output; current full decode/PTS/audio QA passed.',
        actualEncodedSamplesManuallyOpened=0,manuallyReviewedSourceCompositions=32,
        actualRealtimePlayback=False,actualFullListening=False,humanApproval=False,
        publishingApproved=False,deliveryClass='private-local-revision-preview'))


def aac_packets(path):
    h = hashlib.sha256(); count = 0
    with av.open(str(path)) as c:
        for packet in c.demux(c.streams.audio[0]):
            if packet.size:
                h.update(bytes(packet)); count += 1
    return dict(sha256=h.hexdigest(),packets=count)


def finalize():
    baseline = read(M/SLUG/'final-review-v1/bundle.json')
    old_manifest = read(H/'local-final-review-manifest-v1.json')
    assert len(old_manifest['projects']) == 12
    qa = [read(BASE/(mode+'-encoded-qa.json')) for mode in ['pilot','clean']]
    assert all(x['allAutomaticChecksPassed'] for x in qa)
    old_audio = aac_packets(baseline['artifacts']['captioned']['path'])
    videos = dict(captioned=OUT/'captioned-v78.mp4',clean=OUT/'clean-v78.mp4')
    assert all(aac_packets(p)==old_audio for p in videos.values()), 'Preserve approved AAC exactly'
    artifacts = {key:pin(path) for key,path in videos.items()}
    for key, filename in [('subtitlesKo','captions.ko.srt'),('subtitlesEn','captions.en.srt')]:
        target = OUT/filename; assert not target.exists()
        shutil.copy2(baseline['artifacts'][key]['path'],target); artifacts[key]=pin(target)
        assert artifacts[key]['sha256']==baseline['artifacts'][key]['sha256']
    for key, filename in [('metadataKo','metadata-ko.txt'),('metadataEn','metadata-en.txt')]:
        text=Path(baseline['artifacts'][key]['path']).read_text('utf8').strip()
        assert text.endswith(CREDIT)
        note=('수정 검수본: 실제 교토 닌자 공연 참고영상과 두 스탈포스의 공격 차례 표시를 추가했습니다.\n'
              '공연 영상: JackQueenKing, https://www.youtube.com/watch?v=WwAVDIVpuS8\n'
              '2022년 공개된 참고영상이며 개발자의 당시 방문 기록이 아닙니다. 재사용 허락 미확인: 로컬 검수용, 공개 채택 보류.\n'
              '원음·자막 타이밍 유지. 공연 원음 미사용.\n' if key=='metadataKo' else
              'Local revision preview: Kyoto ninja-show context and two-Stalfos attack-turn labels added.\n'
              'Show recording: JackQueenKing, https://www.youtube.com/watch?v=WwAVDIVpuS8\n'
              'A 2022 illustrative recording, not footage of the developers\' original visit. Reuse grant unverified; private review only, publication held.\n'
              'Approved narration/caption clocks retained; show audio omitted.\n')
        target=OUT/filename; assert not target.exists()
        target.write_text(text[:-len(CREDIT)].rstrip()+'\n\n'+note+'\n'+CREDIT+'\n','utf8')
        artifacts[key]=pin(target)
    bundle=dict(schemaVersion=2,slug=SLUG,version='lockon-user-revision-v78',
                localRevisionPreviewComplete=True,localFinalBundleComplete=False,
                deliveryClass='private-local-revision-preview',publishingApproved=False,
                liveShowReusePermissionVerified=False,actualMixSeconds=baseline['actualMixSeconds'],
                artifacts=artifacts,baselineBundle=pin(M/SLUG/'final-review-v1/bundle.json'),
                evidence=[pin(BASE/x)for x in ['pilot-proof.json','clean-proof.json','pilot-encoded-qa.json',
                                             'clean-encoded-qa.json','decoded-reference-equivalence-v75.json','pilot-visual-review.json']],
                checks=dict(fullDecodedVideoAudioChecksPassed=True,approvedAacPacketsByteExact=old_audio,
                            voiceAndSubtitleTimingUnchanged=True,decodedReferenceFrames=32,
                            actualRealtimePlayback=False,actualFullListening=False,humanApproval=False),
                humanApproval=False,platformActions=[])
    save(OUT/'bundle-v2.json',bundle)
    rows = json.loads(json.dumps(old_manifest['projects']))
    rows[0].update(version=bundle['version'],bundle=pin(OUT/'bundle-v2.json'),artifacts=artifacts,
                   deliveryClass=bundle['deliveryClass'],publishingApproved=False,
                   liveShowReusePermissionVerified=False,checks=bundle['checks'])
    assert rows[1:] == old_manifest['projects'][1:]
    result=dict(schemaVersion=2,exactProjectCount=12,selectedRevision=SLUG,
                previousDeliveredManifest=pin(H/'local-final-review-manifest-v1.json'),
                selectedLocalRevisionPreviewComplete=True,unchangedOriginalFinalBundles=11,
                projects=rows,humanApproval=False,platformActions=[],deliveryPostedInChat=False)
    save(H/'local-final-review-manifest-v2.json',result)
    cards=[]
    for row in rows:
        title=read(ROOT/'projects'/row['slug']/'publishing/metadata-draft-v1.json')['titleKo']
        links=' · '.join('<a href="'+html.escape(Path(row['artifacts'][k]['path']).as_uri())+'">'+label+'</a>'
                         for k,label in [('clean','클린 영상'),('subtitlesKo','KO 자막'),('subtitlesEn','EN 자막'),('metadataKo','KO 제목·설명'),('metadataEn','EN 제목·설명')])
        note='<p class="notice">수정 검수본 · 닌자 공연 영상 재사용 허락 미확인, 공개 채택 보류</p>'if row['slug']==SLUG else '<p>기존 검수본 유지</p>'
        cards.append('<section><h2>'+str(row['order'])+'. '+html.escape(title)+'</h2>'+note+
                     '<video controls preload="metadata" src="'+html.escape(Path(row['artifacts']['captioned']['path']).as_uri())+'"></video><p>'+links+'</p></section>')
    page=H/'local-final-review-v2.html';assert not page.exists()
    page.write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>락온 수정본과 12편 로컬 검수</title><style>body{font:17px system-ui;background:#0b1112;color:#eef5f0;max-width:1050px;margin:30px auto}h1,h2{color:#ebce85}a{color:#7fdbce}section{padding:25px 0;border-top:1px solid #405653}video{display:block;width:405px;max-width:100%}.notice{color:#ffd194}</style><h1>락온 수정본 · 12편 로컬 검수</h1><p>첫 편에 교토 닌자 공연 참고영상과 적들의 공격 차례 표시를 추가했습니다. 나머지11편은 기존 파일을 유지합니다.</p><p class="notice">닌자 공연 원본의 재사용 허락은 확인되지 않았으므로 첫 편 수정본은 로컬 검수용입니다. 업로드나 공개는 하지 않았습니다.</p><p><a href="local-final-review-v1.html">기존12편 검수표</a></p>'+''.join(cards)+'</html>','utf8')
    return bundle, page


def finish_shared(page, bundle):
    spec=importlib.util.spec_from_file_location('selected_revision_splice',H/'finalize-cpu-preparation-v1.py')
    sp=importlib.util.module_from_spec(spec);spec.loader.exec_module(sp)
    for name in ['video-production-control.json','video-worklist.json']:
        path=ROOT/'shared/publishing'/name;before=path.read_bytes();text=before.decode('utf-8-sig');d=json.loads(text)
        own=d[KEY];own.update(status='selected-lockon-private-revision-review-ready',automaticAdvanceWithinExactList=False,
                             currentSelectedProject=None,latestSelectedRevision=dict(slug=SLUG,version=bundle['version'],
                             page=str(page.relative_to(ROOT)).replace('\\','/'),bundle=pin(OUT/'bundle-v2.json'),
                             publishingApproved=False,liveShowReusePermissionVerified=False))
        new=sp.replace_value(text,KEY,own)
        if name=='video-worklist.json':
            row=next(x for x in d['rows']if x['id']=='OT12-01')
            row.update(latestSelectedRevision=own['latestSelectedRevision'],reviewStatus='락온 수정 로컬 검수본 / 공연 영상 공개 채택 보류 / 사람 검수 대기')
            new=sp.replace_rows(new,{row['id']:row})
        assert path.read_bytes()==before
        path.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+new.encode('utf8'))


def publish_completion(page):
    def canonical(value):
        return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    doc=ROOT/'docs/VIDEO_WORKLIST.md';before=doc.read_bytes();text=before.decode('utf-8-sig')
    start='<!-- ORIGINAL-TECH-TWELVE-20261115 -->';end='<!-- ORIGINAL-TECH-TWELVE-20261115-END -->'
    a,z=text.index(start),text.index(end)+len(end);old=text[a:z]
    note='락온 편 사용자 요청 수정: 실제 교토 닌자 공연 참고영상과 두 스탈포스의 공격 차례를 추가한 [수정 로컬 검수본](../production/batches/original-tech-twelve-20261115/local-final-review-v2.html)을 준비했다. 원음·자막 타이밍과 다른11편 파일은 보존했다. 공연 영상의 재사용 허락 미확인으로 수정본은 로컬 검수용이며 공개 채택은 보류한다.'
    replacement=old[:old.index(end)].rstrip()+'\n\n'+note+'\n'+end
    assert doc.read_bytes()==before
    doc.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+(text[:a]+replacement+text[z:]).encode('utf8'))
    checkpoint=ROOT/'projects'/SLUG/'production/revision-ninja-turns-v2.json'
    save(checkpoint,dict(status='private-local-revision-preview-complete',bundle=pin(OUT/'bundle-v2.json'),
                        reviewPage=bare(page),rawAndMixedAudioUnchanged=True,otherElevenPreserved=True,
                        publishingApproved=False,liveShowReusePermissionVerified=False,humanApproval=False,platformActions=[]))
    scopes=[]
    for name in ['video-production-control.json','video-worklist.json']:
        path=ROOT/'shared/publishing'/name;data=read(path)
        scopes.append(dict(path=str(path),ownKeySha256=canonical(data[KEY]),
                      rowSha256=canonical([x for x in data.get('rows',[])if x.get('id','').startswith('OT12-')])if'rows'in data else None))
    validation=H/'production-resume-validation-v76.json'
    save(validation,dict(sourceInputs=[bare(p)for p in [page,H/'local-final-review-manifest-v2.json',checkpoint]],
         scopedSharedInputs=scopes,scopedDocInputs=[dict(path=str(doc),ownMarkerSha256=hashlib.sha256(replacement.encode('utf8')).hexdigest())],
         progress=dict(finalVideos=12,selectedRevisionPreviewComplete=True,publicationHeldForNinjaReusePermission=True),
         actualRevisionEvidence=[pin(OUT/'bundle-v2.json'),pin(BASE/'decoded-reference-equivalence-v75.json')],
         sourceVisualReview=pin(R/'preencode-visual-review-v75.json'),humanApproval=False,platformActions=[]))
    receipt=read(R/'production-resume-git-receipt-v75.json');assert receipt['remoteVerified']
    source=(R/'publish-production-resume-v75.py').read_text('utf8')
    expected="parent=='c0aa8b578ba702fc37249ee91a02142fa22cc4f5'"
    assert expected in source
    source=source.replace('v75','v76').replace(expected,"parent=='"+receipt['commit']+"'")
    source=source.replace('Prepare finite lock-on revision and reviewed source-composition checks',
                          'Complete requested lock-on private revision and retain the other eleven delivered bundles')
    publisher=R/'publish-production-resume-v76.py';assert not publisher.exists();publisher.write_text(source,'utf8')
    result=subprocess.run([str(PY),'-u','-X','utf8',str(publisher)],cwd=ROOT,capture_output=True,
                          text=True,encoding='utf8',creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.returncode==0,result.stderr
    return read(R/'production-resume-git-receipt-v76.json')['commit']


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    worker=R/'revision-finisher-v75.json';assert not worker.exists()
    save(worker,dict(pid=psutil.Process().pid,createTime=psutil.Process().create_time(),
                     status='finite-requested-revision-running',recurringAutomation=False,scope=[SLUG]))
    review_status('waiting-for-protected-resources')
    try:
        execute('run-lockon-user-revision-v78.py',['--execute','--mode','pilot','--wait-minutes','180'],'pilot',BASE/'pilot-proof.json')
        execute('verify-lockon-user-revision-v78.py',['--project',SLUG],'pilot-qa',BASE/'pilot-encoded-qa.json')
        verify_reference_equivalence()
        execute('run-lockon-user-revision-v78.py',['--execute','--mode','full','--wait-minutes','180'],'clean',BASE/'clean-proof.json')
        execute('verify-lockon-user-revision-v78.py',['--project',SLUG,'--mode','clean'],'clean-qa',BASE/'clean-encoded-qa.json')
        bundle,page=finalize();finish_shared(page,bundle);commit=publish_completion(page)
        save(R/'revision-complete-v75.json',dict(page=pin(page),manifest=pin(H/'local-final-review-manifest-v2.json'),
             bundle=pin(OUT/'bundle-v2.json'),localRevisionPreviewComplete=True,publishingApproved=False,
             publishedSourceCommit=commit,humanApproval=False,platformActions=[],completedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
        review_status('ready',page)
        print(json.dumps(read(R/'revision-complete-v75.json')))
    except Exception as error:
        review_status('held-with-originals-preserved')
        save(R/'revision-held-v75.json',dict(reason=repr(error),noAutomaticRetry=True,
             localRevisionPreviewComplete=False,publishingApproved=False,foreignProcessesModified=False))
        raise


if __name__=='__main__':
    main()
