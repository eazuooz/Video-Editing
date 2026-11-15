"""Verify exact12 real final bundles; deliver one local page only when complete."""
from pathlib import Path
import argparse,datetime,hashlib,html,json,math
import av
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
CREDIT='Wholesome Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/'
ARTIFACTS=['captioned','clean','subtitlesKo','subtitlesEn','metadataKo','metadataEn']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
    with Path(p).open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    return dict(path=str(Path(p).resolve()),sha256=h,bytes=Path(p).stat().st_size)
def verify(item):
    base=MEDIA/item['slug']/'final-review-v1';path=base/'bundle.json'
    if not path.exists():return None
    d=read(path);assert d['slug']==item['slug'] and d['localFinalBundleComplete'] and d['humanApproval']is False and d['platformActions']==[]
    for key in ARTIFACTS:
        record=d['artifacts'][key];file=Path(record['path']).resolve();assert file.is_relative_to(base.resolve())and file.is_file();actual=pin(file);assert actual['sha256']==record['sha256']and actual['bytes']==record['bytes']
    for key in ['captioned','clean']:
        with av.open(d['artifacts'][key]['path'])as c:
            v=c.streams.video[0];a=c.streams.audio[0];assert(v.width,v.height)==(1080,1920)and v.average_rate==60;assert abs(float(v.duration*v.time_base)-d['actualMixSeconds'])<=1/60+.001
    for key in ['metadataKo','metadataEn']:assert Path(d['artifacts'][key]['path']).read_text(encoding='utf8').strip().endswith(CREDIT)
    assert d['captionWordAnchorsReviewed'] and d['voiceTechnicalReviewPassed'] and d['mixedAsrContentReviewed'] and d['nativeVisualReviewPassed'] and d['encodedAudioVideoQaPassed']
    for proof in d['evidence']:
        assert pin(proof['path'])['sha256']==proof['sha256']
    return dict(order=item['order'],slug=item['slug'],version=d['version'],bundle=pin(path),artifacts=d['artifacts'],actualMixSeconds=d['actualMixSeconds'],checks=d['checks'],humanApproval=False,platformActions=[])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--deliver',action='store_true');a=p.parse_args();batch=read(HERE/'batch.json');assert len(batch['projects'])==12
    complete=[];pending=[]
    for item in batch['projects']:
        result=verify(item)
        if result:complete.append(result)
        else:pending.append(item['slug'])
    result=dict(checkedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exactBatch=batch['batchId']if'batchId'in batch else'original-tech-twelve-20261115',exactProjectCount=12,verifiedFinalBundles=len(complete),pending=pending,humanApproval=False,platformActions=[],finalDelivery=False)
    if a.deliver:
        assert len(complete)==12 and not pending,'All twelve actual local bundles must pass before final delivery'
        manifest=HERE/'local-final-review-manifest-v1.json';page=HERE/'local-final-review-v1.html';assert not manifest.exists()and not page.exists(),'Existing delivery preserved'
        result.update(projects=complete,finalDeliveryPrepared=True,deliveryPostedInChat=False);manifest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');cards=[]
        for item,row in zip(batch['projects'],complete):
            title=read(ROOT/'projects'/row['slug']/'publishing/metadata-draft-v1.json')['titleKo'];files=row['artifacts'];links=' · '.join('<a href="'+html.escape(Path(files[k]['path']).as_uri())+'">'+label+'</a>'for k,label in [('clean','클린 영상'),('subtitlesKo','KO 자막'),('subtitlesEn','EN 자막'),('metadataKo','KO 제목·설명'),('metadataEn','EN 제목·설명')]);cards.append('<section><h2>'+str(row['order'])+'. '+html.escape(title)+'</h2><p>'+html.escape(row['version'])+' · '+format(row['actualMixSeconds'],'.3f')+'초 · 사람 검수 대기</p><video controls preload="metadata" src="'+html.escape(Path(files['captioned']['path']).as_uri())+'"></video><p>'+links+'</p><details><summary>자동 검사·기술 검수 및 파일 해시</summary><pre>'+html.escape(json.dumps(dict(checks=row['checks'],artifacts=files),ensure_ascii=False,indent=2))+'</pre></details></section>')
        page.write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>새 쇼츠12편 최종 로컬 검수</title><style>body{background:#0b1112;color:#eef5f0;font:17px sans-serif;margin:30px auto;max-width:1050px}h1,h2{color:#ebce85}section{border-top:1px solid #3f5753;padding:28px 0}video{display:block;max-width:100%;width:405px}a{color:#7fdbce}pre{white-space:pre-wrap;word-break:break-all;font-size:13px}</style><h1>새 쇼츠12편 최종 로컬 검수</h1><p>모든 항목은 실제 로컬 산출물과 파일 해시를 확인했습니다. 순서대로 재생하여 직접 검수할 수 있습니다. 자동 검사·기술 검수와 사람 승인은 구별되며 플랫폼 작업은 하지 않았습니다.</p>'+''.join(cards)+'</html>',encoding='utf8');result.update(page=pin(page),manifest=pin(manifest))
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
