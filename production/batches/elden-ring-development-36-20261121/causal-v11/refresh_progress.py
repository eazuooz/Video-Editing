"""Record only hash-verified current artifacts; never promote render to completed QA."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha
WORK=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11')
CURRENT={'08':'08-r2','09':'09-r2','12':'12-r2'}

def pin(p):return dict(path=str(p),sha256=sha(p))

def main():
    state=read(HERE/'checkpoint.json');voice={};locked={};render={};unique=set()
    for p in sorted((HERE/'locked').glob('*.json')):
        n=read(p)['id']
        if p.stem!=CURRENT.get(n,n):continue
        locked[n]=pin(p);root=WORK/'voice'/n/sha(p)[:12];proof=root/'voice-generation-v2.json'
        if not proof.exists():continue
        q=read(proof);assert q['identity']['planSha256']==sha(p)
        assert len(q['takes'])==4
        for t in q['takes'].values():assert sha(root/'approved-voice'/t['file'])==t['sha256']
        source=[]
        for a in sorted((root/'voice-qa-source').glob('*.json')):
            data=read(a);assert data['sha256']==sha(root/'approved-voice'/f'{a.stem}.wav')
            source.append(dict(**pin(a),similarity=data['similarity']))
        voice[n]=dict(lock=pin(p),generation=pin(proof),sourceAsr=source,localAudioContextReview='pending')
    for p in (WORK/'voice').glob('*/*/voice-generation-v2.json'):
        for t in read(p)['takes'].values():
            assert sha(p.parent/'approved-voice'/t['file'])==t['sha256'];unique.add(t['sha256'])
    for p in sorted((WORK/'render').glob('*/*/render-proof.json')):
        q=read(p);n=q['episode']
        if n not in locked or q['voiceLockSha256']!=locked[n]['sha256']:continue
        for flavor in ['clean','captioned']:assert sha(p.parent/q[flavor]['path'])==q[flavor]['sha256']
        item=dict(proof=pin(p),finalEpisodeComplete=False,humanReview='pending')
        mixed=p.parent/'voice-qa-mix'/f'{n}.json'
        if mixed.exists():
            data=read(mixed);assert data['sha256']==q['captioned']['sha256']
            item['mixedAsr']=dict(**pin(mixed),similarity=data['similarity'],differences=data['differences'])
        render[n]=item
    adoption=HERE/'reference-adoption-20261128.json'
    adopted=adoption.exists()
    state.update(state=('reference-structure-adopted; beat-timeline-recut-and-remaining-production' if adopted else 'revised-renders-internal-qa; remaining-source-lock-and-production'),
      newVoiceTakes=len(unique),currentVoiceTakes=len(voice)*4,voiceLockedEpisodes=sorted(locked),
      lockedSourceRecords=locked,currentVoiceArtifacts=voice,currentRenderArtifacts=render,
      renderedEpisodesPendingQa=sorted(render),newUnityCuts=len(render)*2,
      newCompletedEpisodes=[],finalReviewDelivered=False,
      remainingAudioReview='Whole mix recognitions recorded per exact file. Local source/stem/mix levels and contextual review remain separate. No human listening claim.',
      nextActions=['Finish changed09/10 timed native pilots and full capture.','Resolve03 last-sentence recognition using one independent complete context.',
        'Continue approved source-locked narration, matched native capture and full render for the exact36.',
        'Complete audio/visual checks and assemble one PC review; preserve v10 and platform state.'])
    if adopted:
        state.update(latestEditorialProfile=read(adoption)['profile'],referenceAdoption=pin(adoption),
          referenceRecutRequiredForInterimRenders=sorted(render),
          nextActions=['Map each episode to observed gameplay, problem, cause, solution, verification and payoff beats.',
            'Replace fixed four-cut and equal adjacent-pair assumptions before reference-style production.',
            'Preserve existing audio and capture evidence; resolve only changed or unresolved contexts.',
            'Finish the exact36 and assemble one PC review after technical and comprehension checks.'])
    save(HERE/'checkpoint.json',state)
    worklist=REPO/'shared/publishing/video-worklist.json';data=read(worklist)
    scoped=data['eldenRingDevelopment36_20261121']['causalRevisionV11']
    scoped.update(state=state['state'],renderedEpisodesPendingQa=sorted(render),currentVoiceTakes=len(voice)*4,
      nativeTimedCuts=len(render)*2,voiceLockedEpisodes=sorted(locked),newCompletedEpisodes=[],newCompleteEpisodes=[],finalReviewDelivered=False)
    if adopted:
        scoped.update(latestEditorialProfile=state['latestEditorialProfile'],referenceAdoption=pin(adoption))
    save(worklist,data)
    doc=REPO/'docs/VIDEO_WORKLIST.md';text=doc.read_text('utf8');marker='<!-- ELDEN-CAUSAL-V11-20261128 -->'
    assert text.count(marker)==1
    # This owned block is the existing trailing section; preserve all preceding sections.
    prefix=text.split(marker)[0]
    doc.write_text(prefix+marker+'\n'+f'2026-11-28 승인된 인과관계 개선안으로 정확36편을 재제작 중이다. '
      f'현재 자료·대본을 잠근 편은{len(locked)}편, 현행 승인 목소리는{len(voice)}편/{len(voice)*4}문단이다. '
      f'내부 검수용 새 렌더는{len(render)}편({"·".join(sorted(render))}), 새 완료 판정은0편이다. '
      '실제 게임과 설명 본문50:50, 기존 목소리·쇼츠 양식·음악 출처를 유지한다. 08번에는 요청된 실제 전투10초 부록이 있다. '
      '전체 전달·사람 청취/승인은 아직이며, 인식/음량/움직임 검수는 각각 분리 기록한다. '
      '[제작 계획](../production/batches/elden-ring-development-36-20261121/causal-v11/plan.json) · '
      '[실제 진행 기록](../production/batches/elden-ring-development-36-20261121/causal-v11/checkpoint.json). 기존v10과 다른 작업은 보존한다.\n'+
      ('2026-11-28 사용자 참고 영상의 질문→문제·제약→해결→확인 실험→실제 응용→답 구조를 채택했다. '
       '현재 내부 렌더는 참고 구조 적용 전 작업본이며 다시 대조한다. 네 컷 고정·쌍별 동일 길이를 강제하지 않는다. '
       '[참고 분석과 제작 규칙](SHORTS_REFERENCE_WORKER_STACKING_20261128.md).\n' if adopted else ''),encoding='utf8')
    print(dict(locked=len(locked),currentVoiceEpisodes=len(voice),uniqueGeneratedTakes=len(unique),rendered=list(render)))

if __name__=='__main__':main()
