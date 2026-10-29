"""Record verified local outputs without implying user review or platform permission."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];SLUG=P.name
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for data in iter(lambda:f.read(8*1024*1024),b''):h.update(data)
    return h.hexdigest()
def main():
    q=read(P/'production/local/documentary-v3/technical-qa.json')
    assert q['technicalDecodePassed'] and q['pairedAudioIdentical'] and q['audioLoudnessPassed']
    v=read(P/'production/local/final-qa/visual-review.json');assert v['status']=='passed-inspected-encoded-frames'
    a=read(P/'production/local/final-qa/audio-review.json');assert a['technicalPassed'] and a['wholeMixAsrCompared']
    master_hash=q['outputs']['captioned']['sha256']
    assert a['masterSha256']==master_hash and v['masterSha256']==master_hash,'Review must match the delivered master.'
    for item in q['outputs'].values():assert digest(item['file'])==item['sha256'],'Encoded master changed after review.'
    now=datetime.now(timezone.utc).isoformat()
    stem=f'output/{SLUG}-v3/{SLUG}'
    paths={'videoBurnedCaptions':stem+'.captioned.mp4','videoClean':stem+'.clean.mp4','captionsKo':stem+'.ko.srt','captionsEn':stem+'.en.srt',
        'captionAlignmentReview':f'projects/{SLUG}/production/caption-alignment-final.json',
        'timeline':f'projects/{SLUG}/production/timeline.json','script':f'projects/{SLUG}/script/narration.ko.json'}
    assert all((ROOT/s).is_file() for s in paths.values())
    manifest=read(P/'project.json');manifest.update(status='local-final-review-ready',publishReady=False)
    manifest.setdefault('titles',{})['ko']=manifest['titleKo']
    manifest.setdefault('paths',{}).update(paths)
    manifest['video']['durationSeconds']=float(q['outputs']['captioned']['probe']['format']['duration'])
    manifest['delivery'].update(status='technical-and-encoded-frame-review-complete-awaiting-user',directory=f'output/{SLUG}',
        masterDirectory=f'output/{SLUG}-v3',captionedSha256=q['outputs']['captioned']['sha256'],humanReview=False,humanListening=False)
    manifest['capture'].update(recordingActive=False,originalSaveHashesUnchanged=True)
    save(P/'project.json',manifest)
    cp=read(P/'production/checkpoint.json');cp.update(updatedAt=now,stage='local-final-review-ready',inProgress=[],
        pending=['User full local viewing/listening, including four marked pronunciation candidates','Any platform action requires a separate explicit request'],
        localOutputs=paths,captionedSha256=q['outputs']['captioned']['sha256'],humanFinalReview=False)
    cp['completed']=list(dict.fromkeys(cp['completed']+[
        'Own prototype121.183s actual FHD60capture;26 runtime checks and selected cut review',
        '17 paragraph Qwen voice331.080s; whole source ASR and complete content comparison; no missing or repeated sentences',
        'Fourteen ASR-timed diagrams with77 cue anchors; source code and state contrast reviewed',
        'Final1080p60 clean/captioned pair decoded throughout, identical audio and95KO/114EN captions',
        'Final encoded visual/caption samples and whole final mix ASR/loudness/continuity evidence recorded']))
    cp['evidenceLimits']=['374rule/32integration/26capture checks cover our implementation, not full original-game equivalence',
        'Final visual review covers documented encoded frames/transitions; full human playback and listening remain pending',
        'Four suspected ASR pronunciation differences have context clips; not declared proven synthesis faults',
        'REA inspected shipped readable scripts; Ghidra/Tripo were not used; no original recovered source/assets redistributed']
    cp['corrections']=[
        {'issue':'Mixed S16/FLOAT concat demuxer corrupted audio and doubled body duration in never-delivered v1',
         'fix':'Decode each input separately into float before filter concat; exact sample comparison and all stream durations verified'},
        {'issue':'v2 AAC reconstructed peak -1.2dBTP exceeded -1.5dBTP limit',
         'fix':'Final limiter ceiling -2.0dB; v3 encoded peak remeasured; video packets and narration PCM unchanged'}]
    cp['reviewEvidence']={'technical':'production/local/documentary-v3/technical-qa.json',
        'visual':'production/local/final-qa/visual-review.json','audio':'production/local/final-qa/audio-review.json'}
    save(P/'production/checkpoint.json',cp)
    save(P/'production/final-review.json',{'checkedAt':now,'status':'local-review-ready-user-review-pending',
        'captionedSha256':master_hash,'durationSeconds':manifest['video']['durationSeconds'],
        'width':1920,'height':1080,'fps':60,'pairedAudioIdentical':True,
        'encodedTruePeakDbtp':q['encodedTruePeakDbtp'],'captionCues':{'ko':95,'en':114},
        'visualReviewStatus':v['status'],'wholeFinalMixAsrCompared':a['wholeMixAsrCompared'],
        'evidence':{k:{'path':path,'sha256':digest(P/path)} for k,path in cp['reviewEvidence'].items()},
        'humanViewing':False,'humanListening':False,'platformMutationPerformed':False,
        'remaining':cp['pending'],'limits':cp['evidenceLimits'],'corrections':cp['corrections']})
    control=read(ROOT/'shared/publishing/video-production-control.json')
    control['scopedSetupAuthorizations'][SLUG].update(status='local-final-review-ready',humanReview=False,captionedSha256=cp['captionedSha256'])
    save(ROOT/'shared/publishing/video-production-control.json',control)
    work=read(ROOT/'shared/publishing/video-worklist.json');row=next(r for r in work['rows'] if r.get('id')=='S-BUCKSHOT-RE')
    row.update(productionComplete=True,productionStatus='1080p60 전체 검수본·독립 플레이 실험 완료',
        reviewStatus='기술·인코딩 프레임·전체 ASR 검수 완료; 사용자 시청·발음 청취 대기',
        humanApproval='제작 승인만 확인; 현재 완성본 사용자 시청 승인 전',executionStatus='로컬 검수 대기; 업로드·자동 다음 영상 없음',
        localReviewPath=f'output/{SLUG}/index.html',captionedSha256=cp['captionedSha256'])
    save(ROOT/'shared/publishing/video-worklist.json',work)
    md=ROOT/'docs/VIDEO_WORKLIST.md';s=md.read_text(encoding='utf-8-sig')
    start='<!-- BUCKSHOT-RE-SETUP-20261028-START -->';end='<!-- BUCKSHOT-RE-SETUP-20261028-END -->'
    block=f'''{start}
## 벅샷 룰렛 리버스 엔지니어링 실험

| 영상 | 분석·구현 | 영상 | 검수 | 상태 |
|---|---|---|---|---|
| [벅샷 룰렛 분석·독립 재구현](../output/{SLUG}/index.html) | REA3,572파일·195스크립트; 자체 규칙374·통합32·촬영26검사 | 1080p60·약5분43초·자막/무자막·한영SRT | 기술·인코딩 프레임·전체ASR 확인; 사용자 시청/청취 대기 | 로컬 검수본 준비, 업로드 없음 |

원작 저장 파일 네 개의 해시는 촬영 전후 동일하다. 독립 프로토타입은 원작 자산·복원 코드를 로드하지 않는다. 원작 전체와의 완전한 동등성을 검증한 결과는 아니다. 네 발음 후보의 문맥 청취 클립을 검수 페이지에 연결했다.
{end}'''
    assert start in s and end in s
    md.write_text(s[:s.index(start)]+block+s[s.index(end)+len(end):],encoding='utf-8')
    print(json.dumps({'status':manifest['status'],'captionedSha256':cp['captionedSha256'],'humanReview':False}))
if __name__=='__main__':main()
