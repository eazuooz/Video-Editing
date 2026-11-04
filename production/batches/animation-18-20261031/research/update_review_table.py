"""Refresh A01/A02 production rows only; preserve other episodes and source audits."""
import hashlib, html, json, re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
stamp=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
host='http://127.0.0.1:9237/@fs/D:/Github/VideoEditing/'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def artifact(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return {'path':p.relative_to(ROOT).as_posix(),'sha256':h.hexdigest(),'bytes':p.stat().st_size}

report=read(HERE/'review-table.json')
rows={r['episode']:r for r in report['rows']}
assert len(rows)==18
h1=ROOT/'projects/animation-assigning/production/grid-v1'
d=ROOT/'projects/animation-assigning/production/local/grid-v1/delivery/output/animation-assigning'
m=read(d/'delivery-manifest.json')
assert m['episode']=='A01' and m['verification']['structuralFinalPair']=='pass' and len(m['files'])==4
for f in m['files']:
    assert Path(f['name']).name==f['name'] and artifact(d/f['name'])['sha256']==f['sha256']
screen=read(h1/'final-screen-review.json'); pixels=read(h1/'final-caption-pixel-review.json')
assert screen['master']['sha256']==pixels['master']['sha256']==m['captionedMasterSha256']
assert not screen['blockingFindings'] and not pixels['blockingFindings']
asr=read(h1/'final-mix-asr-review.json')
assert asr['fullTextDirectReview'] and asr['all17ParagraphsRead']
r=rows['A01']
r['script'].update(status='frozen-ko-en-and-paired-captions',displayKo='한국어·영문 동결 · 177개 대응 자막 확정',timingLocked=True)
r['voice'].update(status='final-asr-continuity-reviewed-human-listening-pending',displayKo='최종 음성 ASR·연속성 확인 · 직접 청취 대기',evidence=artifact(h1/'final-mix-asr-review.json'),humanListening=False)
r['video'].update(status='local-four-output-review-delivery-ready',displayKo='검수본 완성 · 6분 55초 · 1080p 60fps',completedReviewMaster=True,technicalQaComplete=True,sampledEncodedPixelsReviewed=True,finalAudioVisualQaComplete=False,humanFinalReviewRecorded=False,uploadAuthorizedByBatch=False,qaScopeKo='구조·연속 음성·표본 화면·177개 자막 확인. 사용자 전체 시청·청취 대기.')
r['delivery']={'directory':d.relative_to(ROOT).as_posix(),'indexUrl':host+(d/'index.html').relative_to(ROOT).as_posix(),'captionedUrl':host+(d/'animation-assigning.captioned.mp4').relative_to(ROOT).as_posix(),'manifestUrl':host+(d/'delivery-manifest.json').relative_to(ROOT).as_posix(),'captionedMasterSha256':m['captionedMasterSha256'],'manifest':artifact(d/'delivery-manifest.json'),'fourOutputs':m['files'],'userFinalReview':False,'uploadsPerformed':False}
r['nextActionKo']='완성 검수본 전체 시청·청취 및 사용자 검수'
r['evidenceSnapshot']={'checkedAtKst':stamp,'delivery':artifact(d/'delivery-manifest.json'),'captionPixels':artifact(h1/'final-caption-pixel-review.json'),'screenSamples':artifact(h1/'final-screen-review.json')}

a2=ROOT/'projects/animation-exaggeration'
l2=a2/'production/local/grid-v1'
voice=l2/'voice/voice-generation.json'; assert voice.exists()
script=read(a2/'script/grid-v1/narration.ko.json'); units=read(a2/'script/grid-v1/caption-units.json')
assert sum(len(s['lines']) for s in script['scenes'])==14
assert sum(len(p) for s in units['byScene'].values() for p in s.values())==100
native=[{'mode':p.parent.name,'receipt':artifact(p)} for p in sorted((l2/'preflight/nominal-preflight-v1').glob('*/preflight-success.json')) if read(p).get('status')=='complete']
asr2=l2/'voice/whole-source-asr-cpu-v2.json'
r=rows['A02']
r['script'].update(status='frozen-ko-en-and-paired-units-source-bound',path='projects/animation-exaggeration/script/grid-v1/narration.ko.json',displayKo='한국어·영문 14문단 · 대응 자막 100개 · 실영상 연결',ttsReady='generated-from-parent-frozen-script',timingLocked=False)
r['voice'].update(status='sample-b-generated-source-asr-text-review-pending',displayKo='샘플 B 음성 생성 · 전체 ASR 확인 중 · 직접 청취 대기',evidence=artifact(voice),humanListening=False)
r['voice']['cpuAsr']={'available':asr2.exists(),'evidence':artifact(asr2) if asr2.exists() else None,'fullTextReviewedByThisSnapshot':False}
asr_review2=a2/'production/grid-v1/source-asr-review-v2.json'
if asr_review2.exists():
    review2=read(asr_review2)
    assert review2['recommendation']['preferredSourceAsr']['sha256']==artifact(asr2)['sha256']
    assert review2['all14ParagraphsRead'] and review2['coverage']['wordCount']==554
    r['voice'].update(status='sample-b-whole-source-text-and-word-coverage-reviewed',displayKo='샘플 B 생성 · 전체 14문단·554단어 확인 · 직접 청취 대기')
    r['voice']['cpuAsr'].update(fullTextReviewedByThisSnapshot=True,review=artifact(asr_review2),lastWordEndSeconds=272.06)
r['video'].update(status='native-engineering-preflight-in-progress',displayKo=f'Unity 기술 검증 중 · {len(native)}개 모드 표본 캡처',completedReviewMaster=False,finalAudioVisualQaComplete=False,humanFinalReviewRecorded=False,uploadAuthorizedByBatch=False,qaScopeKo='명목 시간의 기술 검증 단계. 최종 렌더·검수본은 아직 없습니다.')
r['video']['nativePreflight']={'completedCaptureModes':native,'timing':'nominal-not-final-speech-locked','captureSuccessDoesNotMeanFinalVisualApproval':True}
r['nextActionKo']='전체 ASR 대조 → 문장 시간 결합 → Unity 동작 검수·최종 제작'
r['evidenceSnapshot']={'checkedAtKst':stamp,'voiceGeneration':artifact(voice),'nativePreflightCount':len(native),'basis':'Actual files inspected. No A03 completion inferred.'}
completed=1
delivery2=l2/'delivery/output/animation-exaggeration'
if (delivery2/'delivery-manifest.json').exists():
    m2=read(delivery2/'delivery-manifest.json')
    assert m2['episode']=='A02' and m2['verification']['structuralFinalPair']=='pass' and len(m2['files'])==4
    for f in m2['files']:
        assert Path(f['name']).name==f['name'] and artifact(delivery2/f['name'])['sha256']==f['sha256']
    h2=a2/'production/grid-v1'
    assert not read(h2/'final-screen-review.json')['blockingIssues']
    assert not read(h2/'final-caption-pixel-review.json')['blockingIssues']
    r['script'].update(displayKo='한국어·영문 14문단 · 자막 100개 · 음성 시간 확정',timingLocked=True)
    r['voice'].update(status='final-asr-continuity-reviewed-human-listening-pending',displayKo='최종 14문단 ASR·연속성 확인 · 직접 청취 대기',evidence=artifact(h2/'final-mix-asr-review.json'))
    r['video'].update(status='local-four-output-review-delivery-ready',displayKo='검수본 완성 · 4분 44초 · 1080p 60fps',completedReviewMaster=True,technicalQaComplete=True,sampledEncodedPixelsReviewed=True,finalAudioVisualQaComplete=False,qaScopeKo='31컷·100개 자막 표본 화면과 연속 음성 검사 완료. 사용자 전체 시청·청취 대기.')
    r['delivery']={'directory':delivery2.relative_to(ROOT).as_posix(),'indexUrl':host+(delivery2/'index.html').relative_to(ROOT).as_posix(),'captionedUrl':host+(delivery2/'animation-exaggeration.captioned.mp4').relative_to(ROOT).as_posix(),'manifestUrl':host+(delivery2/'delivery-manifest.json').relative_to(ROOT).as_posix(),'captionedMasterSha256':m2['captionedMasterSha256'],'manifest':artifact(delivery2/'delivery-manifest.json'),'fourOutputs':m2['files'],'userFinalReview':False,'uploadsPerformed':False}
    r['nextActionKo']='완성 검수본 전체 시청·청취 및 사용자 검수'
    r['evidenceSnapshot']={'checkedAtKst':stamp,'delivery':artifact(delivery2/'delivery-manifest.json'),'captionPixels':artifact(h2/'final-caption-pixel-review.json'),'screenSamples':artifact(h2/'final-screen-review.json')}
    completed=2
report.update(updatedAtKst=stamp,purposeKo='18편의 연구·제작·로컬 검수 현황입니다. 완성 검수본과 사용자 검수 완료를 구분합니다.')
report['counts'].update(completedReviewVideosClaimed=completed,completedLocalReviewMasters=completed,voiceGenerated=2,humanFinalReviewsRecorded=0)
report['validation'].update(a01PairedUnits=177,encodedSubtitlePixelReview=True,actualAudioTimingReview='source-word-timing-and-final-asr-reviewed-not-human-listening',a02Paragraphs=14,a02PairedUnits=100)
report['deliveryServer']={'host':'127.0.0.1','port':9237,'readOnly':True,'futureDeliveriesRequireValidHashBoundManifest':True}
(HERE/'review-table.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

esc=html.escape
page=(HERE/'review-table.html').read_text(encoding='utf-8')
page=page.replace('애니메이션 18편 연구·대본 검수표','애니메이션 18편 제작·검수표')
note=(f'<p class="note"><strong>로컬 검수본 {completed}편 · 사용자 최종 검수 0편.</strong> '+('A01·A02 전체 영상과 한영 자막을 열 수 있습니다. A03는 제작 준비 단계입니다. ' if completed==2 else 'A01 전체 영상과 한영 자막을 열 수 있습니다. A02는 제작 중입니다. ')+'18편 원본 본문·관련 화면 검토와 대본 초안은 완료됐으며, 원본 강의는 연구 자료로만 사용합니다.</p>')
page=re.sub(r'<p class="note">.*?</p>',note,page,flags=re.S)
for eid in ('A01','A02'):
    r=rows[eid]; video=esc(r['video']['displayKo'])
    if 'delivery' in r:
        video+=f'<small><a href="{esc(r["delivery"]["indexUrl"])}">영상·자막 보기</a> · <a href="{esc(r["delivery"]["captionedUrl"])}">전체 영상</a></small>'
    replacement='<tr>'+f'<td data-label="편">{eid}</td>'+f'<td data-label="제목 / 원제"><strong>{esc(r["titleKo"])}</strong><small><a href="{esc(r["sourceUrl"])}">{esc(r["sourceTitleEn"])}</a></small></td>'+f'<td data-label="원본 검토">{esc(r["research"]["displayKo"])}</td>'+f'<td data-label="대본">{esc(r["script"]["displayKo"])}</td>'+f'<td data-label="음성">{esc(r["voice"]["displayKo"])}</td>'+f'<td data-label="영상·최종 검수">{video}<small>{esc(r["video"]["qaScopeKo"])}</small></td></tr>'
    page,count=re.subn(r'<tr><td data-label="편">'+eid+r'</td>.*?</tr>',lambda _:replacement,page,count=1,flags=re.S)
    assert count==1
page=re.sub(r'<footer>.*?</footer>',f'<footer>갱신: {esc(stamp)} · 실제 파일과 검수 기록에 근거한 현황입니다. 표본 화면과 ASR·연속성 검사는 사람의 전체 시청·청취를 뜻하지 않습니다. 업로드·예약은 수행하지 않았습니다.</footer>',page,flags=re.S)
(HERE/'review-table.html').write_text(page,encoding='utf-8')
print(json.dumps({'rows':18,'completedLocalReviewMasters':completed,'humanFinalReviews':0,'a01Hash':m['captionedMasterSha256'],'a02NativeCaptures':23 if completed==2 else len(native),'a03CompletionClaimed':False,'sourceAuditsModified':False},ensure_ascii=False))
