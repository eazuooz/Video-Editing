"""Publish the verified local revision to the M21 row only."""
import re
from datetime import datetime,timezone
from common import *
from teaching import BOARDS
from guides import STILLS
from symbol_pages import SCALARS
from samples import DEMOS
from unity_guides import NATIVE
from narration import LESSONS
STATUS='1080p60 · 산술 대입을 걷어내고 공식과 기호를 표면에 연결 · 재질 셰이더와 벡터 검수'
def now():return datetime.now(timezone.utc).isoformat()
def update():
    report=read(WORK/'final-qa/report.json');files=report['files'];master=files['captioned']['sha256']
    assert master==sha(OUT/(PROJECT.name+'.captioned.mp4'))
    assert len(report['reviewedCuts'])==85 and (WORK/'final-qa/mobile-inspection.json').exists()
    browser=read(WORK/'final-qa/browser-playback.json')
    catalog=BASE/'scene-catalog.json';evidence=BASE/'review-evidence.json'
    write(catalog,dict(basis='All V6 cut roles, narration, source images and formula boards reviewed. The seven commercial-game clips retain their existing bytes; numerical teaching examples are recut in both languages.',scenes=report['reviewedCuts']))
    write(evidence,dict(scope='M21 v7',at=now(),rules=['meaning-before-values-v1','surface-symbol-guides-v1'],files=files,cuts=85,
        changedExplanations=report['changedExplanations'],formulaBoards=len(BOARDS),newSpeech=report['voice'],nativeSpeed=True,gameplayCuts=7,shaderInputs={str(k):v[0] for k,v in DEMOS.items()},actualEngine='D3D11 WARP / HLSL shader model 5; Unity URP retains its original scene transforms',staticSymbols=sorted(STILLS),nativeTracked=sorted(NATIVE),
        browser=browser,mobile=read(WORK/'final-qa/mobile-inspection.json'),audioIntegrity=read(WORK/'pcm-integrity.json'),userReview=False,continuousListening=False))
    outputs={k:v['path'] for k,v in files.items()};outputs['index']=str(OUT/'index.html')
    content=WORK/'content-review.json';write(content,dict(status='four-files-available-integrated-review-pending',annotationRevision='teaching-v7',localFinalReviewReady=False,masterSha256=master,humanReview=False))
    paths=dict(technicalQa=str(WORK/'final-qa/report.json'),contentReview=str(content),teachingEvidence=str(evidence),sceneCatalog=str(catalog))
    plan=PROJECT/'planning/production-plan.json';data=read(plan);data['symbolTeachingRevision']=dict(version='teaching-v7',rules=['meaning-before-values-v1','surface-symbol-guides-v1'],scope='all numeric examples and symbol-bearing M21 explanation pages',sourceAudit=str(catalog.relative_to(ROOT).as_posix()),revoiced=sorted(LESSONS));write(plan,data)
    bat=ROOT/'production/batches/game-math-remaining-20261104'
    data=read(bat/'batch.json');item=next(i for i in data['items'] if i['id']=='M21');item.update(outputs=outputs,outputCandidatesAvailable=True,localReviewReady=False,humanReviewed=False,status='media-generated-internal-review-pending');item['evidence'].update(paths);write(bat/'batch.json',data)
    work=ROOT/'shared/publishing/video-worklist.json';data=read(work);r=next(i for i in data['rows'] if i['id']=='M21')
    r.update(productionStatus=STATUS,reviewStatus='연속 청취·사용자 시청 전',notes='M21 v7. 수치 대입 예시 전편 점검 · 표면 벡터와 값의 의미를 표시한 로컬 검수본.',localMasterAvailable=True,productionComplete=False);write(work,data)
    cp=PROJECT/'production/checkpoint.json';d=read(cp);d.update(stage=STATUS,updatedAt=now(),localReviewReady=False,humanReview=False,outputsReady=True,outputCandidates=outputs,nextAction='Review the local v7 master and continuous listening.');d['evidence'].update(paths);write(cp,d)
    led=PROJECT/'production/review-ledger.json';d=read(led);d['checks']=[x for x in d['checks'] if x.get('id')!='m21-teaching-v7']+[dict(id='m21-teaching-v7',at=now(),evidence=paths,masterSha256=master,continuousListening=False,humanReview=False)];d.update(updatedAt=now(),humanReview={'status':'v7-local-preview-available-not-human-reviewed'});write(led,d)
    url=f'http://127.0.0.1:9347/output/{OUT.name}/index.html'
    doc=ROOT/'docs/VIDEO_WORKLIST.md';s=doc.read_text('utf-8-sig');s=re.sub(r'^\| M21 \|.*$',lambda _:f"| M21 | 빛과 셰이딩 | ☐ {STATUS} | ☐ {r['reviewStatus']} | {r['platformStatus']} |",s,flags=re.M);s=re.sub(r'^\| M21 [^|]+ \|.*$',lambda _:f"| M21 빛과 셰이딩 | {r['notes']} |",s,flags=re.M);doc.write_text(s,'utf-8')
    doc=bat/'progress.md';s=doc.read_text('utf-8-sig');doc.write_text(re.sub(r'^\| M21 \|.*$',lambda _:f'| M21 | 빛과 셰이딩 | {STATUS} | 연속 청취 남음 | [로컬 검수본 재생]({url}) |',s,flags=re.M),'utf-8')
    hub=ROOT/'output/game-math-remaining-20261104/index.html';s=hub.read_text('utf-8');hub.write_text(re.sub(r'<tr><td>M21</td>.*?</tr>',lambda _:f'<tr><td>M21</td><td>빛과 셰이딩<br><a href="../{OUT.name}/index.html">수정본 재생</a></td><td>{STATUS}</td><td>{r["reviewStatus"]}</td></tr>',s,count=1),'utf-8')
    old=V6/'index.html';s=old.read_text('utf-8')
    if 'id="latest-m21-symbols"' not in s:old.write_text(s.replace('<h1>',f'<p id="latest-m21-symbols"><a href="../{OUT.name}/index.html">최신 수정본 · 구에 표시한 기호와 벡터 보기</a></p><h1>',1),'utf-8')
if __name__=='__main__':update()
