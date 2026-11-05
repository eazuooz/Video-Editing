"""Update M21's review entries only, after comparing the four artifacts with the checked hashes."""
import re
from build import WORK,OUTPUT,V5,PROJECT,ROOT,SLUG,original
from inspect_master import utc
from notation import PAIRS
from voice import read,write,VOICE
from pathlib import Path

BASE=Path(__file__).parent
STATUS='1080p60 · 영어·한국어 용어 제목과 수식·코드 적용 · 여덟 문장 수정 · 로컬 재생 확인'
def main():
    report=read(WORK/'final-qa/report.json');browser=read(WORK/'final-qa/browser-playback.json')
    files=report['files'];master=files['captioned']['sha256'];assert master==original.sha(OUTPUT/(SLUG+'.captioned.mp4'))
    takes=read(VOICE/'mix.json');speech=read(VOICE/'speech-check.json');assert len(takes)==len(speech)==8
    if not (WORK/'final-qa/mobile-viewed.json').is_file():raise RuntimeError('Inspect the actual mobile contact sheet before recording.')
    note=read(WORK/'final-qa/mobile-viewed.json')
    source_refs={'radiometry':'https://pbr-book.org/4ed/Radiometry,_Spectra,_and_Color/Radiometry','vertexInterpolation':'https://learn.microsoft.com/en-us/windows/win32/direct3d9/triangle-interpolation','reflect':'https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-reflect'}
    catalog=[dict(scene=e['scene'],title=e['heading'],masterSeconds=e['at'],equation=(PAIRS[int(e['scene'])].equation if int(e['scene']) in PAIRS else None),code=(list(PAIRS[int(e['scene'])].code) if int(e['scene']) in PAIRS else None)) for e in report['samples']]
    write(BASE/'scene-catalog.json',dict(source='v5 sphere studies and original independent gameplay',sources=source_refs,chapters=catalog))
    evidence=BASE/'review-evidence.json'
    write(evidence,dict(revision='terms-v6',checkedAt=utc(),rule='english-first-terms-math-above-code-v1',files=files,headings=report['encodedHeadings'],pairedMathAndCode=report['equationAndCodePairs'],gameplayCuts=report['gameplayCutsReused'],voiceChanges=[dict(scene=t['scene'],old=t['old'],spoken=t['spoken'],tempo=t['tempo'],asr=r['heard'],asrMatch=r['match']) for t,r in zip(takes,speech)],sourceReferences=source_refs,browser=browser,mobileReview=note,fullContinuousListening=False,userReview=False))
    detail=read(evidence);detail['pcmIntegrity']=report['pcmIntegrity'];write(evidence,detail)
    content=WORK/'content-review.json';write(content,dict(status='four-files-available-integrated-review-pending',annotationRevision='terms-v6',localFinalReviewReady=False,humanReview=False,masterSha256=master))
    bas=ROOT/'production/batches/game-math-remaining-20261104'
    paths=dict(technicalQa=str(WORK/'final-qa/report.json'),contentReview=str(content),termsEvidence=str(evidence),sceneCatalog=str(BASE/'scene-catalog.json'))
    out={k:v['path'] for k,v in files.items()};out['index']=str(OUTPUT/'index.html')
    batch=read(bas/'batch.json');item=next(x for x in batch['items'] if x['id']=='M21')
    item.update(outputs=out,outputCandidatesAvailable=True,humanReviewed=False,localReviewReady=False,status='media-generated-internal-review-pending');item['evidence'].update(paths);write(bas/'batch.json',batch)
    work=ROOT/'shared/publishing/video-worklist.json';d=read(work);r=next(x for x in d['rows'] if x['id']=='M21')
    r.update(productionStatus=STATUS,localMasterAvailable=True,productionComplete=False,reviewStatus='연속 청취·사용자 시청 전',notes='M21 v6 로컬 영어 용어·수학식 수정본. 78개 설명 장면과 한영 자막, 레디언스·이레디언스 음성 수정. 사용자 시청 대기.');write(work,d)
    cp=PROJECT/'production/checkpoint.json';d=read(cp);d.update(stage=STATUS,updatedAt=utc(),outputCandidates=out,outputsReady=True,localReviewReady=False,humanReview=False,nextAction='Review v6 continuous listening and user feedback locally.');d['evidence'].update(paths);write(cp,d)
    led=PROJECT/'production/review-ledger.json';d=read(led);d['checks']=[x for x in d['checks'] if x.get('id')!='m21-terms-v6']+[dict(id='m21-terms-v6',at=utc(),masterSha256=master,evidence=paths,fullContinuousListening=False,humanReview=False)];d.update(updatedAt=utc(),humanReview={'status':'v6-local-preview-available-not-human-reviewed'});write(led,d)
    doc=ROOT/'docs/VIDEO_WORKLIST.md';s=doc.read_text('utf-8-sig');s=re.sub(r'^\| M21 \|.*$',lambda _:f"| M21 | 빛과 셰이딩 | ☐ {STATUS} | ☐ {r['reviewStatus']} | {r['platformStatus']} |",s,flags=re.M);s=re.sub(r'^\| M21 [^|]+ \|.*$',lambda _:f"| M21 빛과 셰이딩 | {r['notes']} |",s,flags=re.M);doc.write_text(s,'utf-8')
    url='http://127.0.0.1:9347/output/'+OUTPUT.name+'/index.html'
    doc=bas/'progress.md';s=doc.read_text('utf-8');doc.write_text(re.sub(r'^\| M21 \|.*$',lambda _:f'| M21 | 빛과 셰이딩 | {STATUS} | 연속 청취 남음 | [로컬 수정본 재생]({url}) |',s,flags=re.M),'utf-8')
    hub=ROOT/'output/game-math-remaining-20261104/index.html';s=hub.read_text('utf-8');hub.write_text(re.sub(r'<tr><td>M21</td>.*?</tr>',lambda _:f'<tr><td>M21</td><td>빛과 셰이딩<br><a href="../{OUTPUT.name}/index.html">수정본 재생</a></td><td>{STATUS}</td><td>{r["reviewStatus"]}</td></tr>',s,count=1),'utf-8')
    old=V5/'index.html';s=old.read_text('utf-8')
    if 'id="latest-m21-terms"' not in s:
        s=s.replace('<h1>',f'<p id="latest-m21-terms"><a href="../{OUTPUT.name}/index.html">v6 · 영어 용어와 수학식 수정본 보기</a></p><h1>',1);old.write_text(s,'utf-8')
if __name__=='__main__':main()
