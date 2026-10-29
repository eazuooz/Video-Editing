"""Publish v4 local-review state only after hash-bound internal QA; no platform action."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];SLUG=P.name
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def main():
    q=read(P/'production/local/documentary-v4/technical-qa.json')
    v=read(P/'production/local/final-qa-v4/visual-review.json')
    a=read(P/'production/local/final-qa-v4/audio-review.json')
    c=read(P/'production/caption-alignment-v4.json')
    master=q['outputs']['captioned']['sha256']
    assert q['technicalDecodePassed'] and q['pairedAudioIdentical'] and q['audioLoudnessPassed']
    assert v['status']=='passed-inspected-encoded-frames' and v['masterSha256']==master
    assert a['technicalPassed'] and a['wholeMixAsrCompared'] and a['masterSha256']==master
    assert c['approved'] and c['manualSemanticReview'] and c['allParagraphTextsRetained'] and c['paragraphCount']==19
    for output in q['outputs'].values():assert sha(Path(output['file']))==output['sha256']
    for cap in c['captions']:assert sha(ROOT/cap['path'])==cap['sha256']
    now=datetime.now(timezone.utc).isoformat();stem=f'output/{SLUG}-v4/{SLUG}'
    paths={'videoBurnedCaptions':stem+'.captioned.mp4','videoClean':stem+'.clean.mp4',
      'captionsKo':stem+'.ko.srt','captionsEn':stem+'.en.srt',
      'captionAlignmentReview':f'projects/{SLUG}/production/caption-alignment-v4.json',
      'timeline':f'projects/{SLUG}/production/timeline-v4.json',
      'script':f'projects/{SLUG}/script/revision-v4/narration.ko.json',
      'scriptEn':f'projects/{SLUG}/script/revision-v4/narration.en.json'}
    assert all((ROOT/value).is_file() for value in paths.values())
    for key,target in [('clean','videoClean'),('captioned','videoBurnedCaptions')]:
        assert Path(q['outputs'][key]['file']).resolve()==(ROOT/paths[target]).resolve()
    for lang,target in [('ko','captionsKo'),('en','captionsEn')]:
        entry=next(item for item in c['captions'] if item['language']==lang)
        assert (ROOT/entry['path']).resolve()==(ROOT/paths[target]).resolve()
    assert c['sourceAudioSha256']==sha(P/'production/local/audio-v4/narration.wav')
    # Resolve every ledger target before writing any completion state.
    manifest=read(P/'project.json');cp=read(P/'production/checkpoint.json')
    control=read(ROOT/'shared/publishing/video-production-control.json')
    assert control['scopedSetupAuthorizations'][SLUG]['productionAllowedNow'] is True
    assert manifest['revision']['id']=='v4'
    work=read(ROOT/'shared/publishing/video-worklist.json');row=next(x for x in work['rows'] if x.get('id')=='S-BUCKSHOT-RE')
    path=ROOT/'docs/VIDEO_WORKLIST.md';text=path.read_text(encoding='utf-8-sig')
    begin='<!-- BUCKSHOT-RE-SETUP-20261028-START -->';end='<!-- BUCKSHOT-RE-SETUP-20261028-END -->'
    assert text.count(begin)==1 and text.count(end)==1 and text.index(begin)<text.index(end)
    manifest.update(status='local-final-review-ready',publishReady=False)
    manifest['paths'].update(paths);duration=float(q['outputs']['captioned']['probe']['format']['duration'])
    manifest['video']['durationSeconds']=duration
    manifest['delivery'].update(status='v4-internal-review-complete-awaiting-user',directory=f'output/{SLUG}',
      masterDirectory=f'output/{SLUG}-v4',captionedSha256=master,humanReview=False,humanListening=False)
    manifest['revision']['completedAt']=now
    review_evidence={'technical':'production/local/documentary-v4/technical-qa.json',
      'visual':'production/local/final-qa-v4/visual-review.json','audio':'production/local/final-qa-v4/audio-review.json',
      'captions':'production/caption-alignment-v4.json','plan':'planning/revision-v4-workflow.json'}
    cp.update(updatedAt=now,stage='local-final-review-ready',inProgress=[],
      pending=['User final viewing/listening of v4; new REA/workflow narration and retained pronunciation candidates',
               'Any platform action remains outside this revision'],localOutputs=paths,captionedSha256=master,humanFinalReview=False,
      reviewEvidence=review_evidence)
    cp['completed']=list(dict.fromkeys(cp['completed']+[
      'v4: result-first original/prototype comparison, general workflow, REA/agent/MCP explanation and actual-route conclusion',
      'v4: five newly generated paragraphs; fourteen original paragraphs and all original body cuts preserved',
      'v4: current complete audio ASR/content comparison, encoded audio/duration checks and selected encoded visual/caption inspection']))
    cp['evidenceLimits']=['REA CLI and readable GDScript were used; Ghidra and Tripo MCP are optional paths, not executed tools',
      'No measured time-saving figure; prototype has documented scope, not full original-game equivalence',
      'Internal QA uses complete decode/ASR and documented visual samples, not human whole-video viewing/listening',
      'Original source/assets are not distributed; unchanged original saves and implementation checks retain their evidence']
    final={'checkedAt':now,'revision':'v4','status':'local-review-ready-user-review-pending','captionedSha256':master,
      'durationSeconds':duration,'width':1920,'height':1080,'fps':60,'pairedAudioIdentical':True,
      'encodedTruePeakDbtp':q['encodedTruePeakDbtp'],
      'captionCues':{x['language']:x['cues'] for x in c['captions']},'visualReviewStatus':v['status'],
      'wholeFinalMixAsrCompared':True,'evidence':{key:{'path':path,'sha256':sha(P/path)} for key,path in review_evidence.items()},
      'humanViewing':False,'humanListening':False,'platformMutationPerformed':False,
      'remaining':cp['pending'],'limits':cp['evidenceLimits'],'baselinePreserved':'output/'+SLUG+'-v3'}
    control['scopedSetupAuthorizations'][SLUG].update(status='local-final-review-ready',humanReview=False,captionedSha256=master,revision='v4')
    row.update(productionComplete=True,productionStatus='v4 REA·전체 제작 흐름 보강, 1080p60 검수본 완료',
      reviewStatus='기술·인코딩 화면·전체 ASR 검수 완료; 사용자 시청·청취 대기',
      humanApproval='제작 승인만 확인; v4 최종 사용자 시청 승인 전',executionStatus='로컬 검수 대기; 업로드·자동 다음 영상 없음',
      localReviewPath=f'output/{SLUG}/index.html',captionedSha256=master)
    seconds=round(duration)
    block=f'''{begin}
## REA와 AI로 만드는 게임 기반 프로토타입

| 영상 | 분석·구현 | 수정본 | 검수 | 상태 |
|---|---|---|---|---|
| [기존 게임 분석 → 새 프로토타입](../output/{SLUG}/index.html) | REA 3,572파일·195스크립트; 규칙374·통합32·촬영26검사 | v4 · 1080p60 · {seconds//60}분 {seconds%60:02}초 · 자막/무자막·한영SRT | 현재 파일 기술·전체ASR·표본화면 확인; 사용자 시청·청취 대기 | 로컬 검수본 준비, 업로드 없음 |

전체 제작 흐름과 REA·AI 에이전트·MCP 설명을 도입에 추가했다. 실제 실행은 REA CLI → GDScript 분석 → 자체 코드·Blender Python 모델 → Godot 프로토타입이며 Ghidra·Tripo MCP는 일반 선택지로 구분했다. 본문 14문단의 원본 PCM과 기존 영상 컷을 보존했다. v3는 별도 보관한다.
{end}'''
    assert begin in text and end in text
    save(P/'project.json',manifest);save(P/'production/checkpoint.json',cp)
    save(P/'production/final-review-v4.json',final);save(P/'production/final-review.json',final)
    save(ROOT/'shared/publishing/video-production-control.json',control)
    save(ROOT/'shared/publishing/video-worklist.json',work)
    path.write_text(text[:text.index(begin)]+block+text[text.index(end)+len(end):],encoding='utf-8')
    print(json.dumps({'revision':'v4','status':manifest['status'],'duration':duration,'sha256':master}))
if __name__=='__main__':main()
