"""Scoped shared-policy/ledger changes, preserving unrelated index and worktree edits."""
import importlib.util
from pathlib import PurePosixPath
import sys
from prepare import HERE, ROOT, WORK, OUTPUT, KEY, read, save, stamp

CONTROL='shared/publishing/video-production-control.json'
WORKLIST='shared/publishing/video-worklist.json'
TABLE='docs/VIDEO_WORKLIST.md'
RULES={'AGENTS.md':[
 ('After the original 2-second branding, use a natural 2–4-sentence overview: viewer question, benefit, two or three actual steps/examples in order, first-example connection.',
  'After the original 2-second branding, use a natural 2–4-sentence overview: viewer question, benefit, two or three actual steps/examples in order, first-example connection. User-directed 2026-11-14 `opening-overview-closing-recap-v1`: every future explicitly selected video also makes the opening overview an understandable mini-explanation: define the topic in plain language, show its essential relationship/prerequisite and the two or three learning steps alongside the relevant narrated game/example/diagram. Close by answering the same opening question and visibly recapping two or three useful points (about 10 seconds in long-form, before the existing member ending; proportionately brief in shorts). Integrate sufficient existing overview/recap speech and preserve approved audio rather than adding duplicate introductions, unspoken text-only summaries or unrelated chapters. The user selected A03–A18 for this visual overview revision; retain their v6 speech, native clips and 600-frame recaps, excluding uploaded A01/A02. This default is not authorization to remake unselected/completed videos.')],
 'docs/VIDEO_WORKFLOW.md':[
 ('기존 2–4문장 개요와 역할을 통합해 같은 내용을 연속해서 두 번 소개하지 않는다. 초반의 구체적인 대상·문제를 첫 설명으로 이어 주고 마지막 결론에서도 같은 질문에 답한다.',
  '기존 2–4문장 개요와 역할을 통합해 같은 내용을 연속해서 두 번 소개하지 않는다. 초반의 구체적인 대상·문제를 첫 설명으로 이어 주고 마지막 결론에서도 같은 질문에 답한다. 2026-11-14 사용자 지시 `opening-overview-closing-recap-v1`: 앞으로 명시적으로 선택한 모든 영상에는 앞의 개론과 끝의 정리를 기본으로 적용한다. 개론은 쉬운 뜻·필요한 전제/핵심 관계·실제로 볼 2~3단계 순서를 해당 게임/시연/도식과 함께 말로 설명하고, 첫 사례에서 생긴 질문을 본문으로 연결한다. 정리는 같은 질문에 답하면서 핵심 2~3개를 화면과 음성으로 되짚는다. 긴 영상은 기존 회원 안내 앞 약10초, 쇼츠는 분량에 맞춰 짧게 구성하며 고정 길이를 채우는 패딩은 넣지 않는다. 충분한 기존 개론·정리 대사는 통합·재사용하고 승인 음성을 보존한다. 중복 인사·목차 낭독·무음 글자 화면·새 주제 추가로 대신하지 않는다. 이번에는 A03–A18의 v6 음성·기존 클립·600프레임 정리를 보존하며 개론 시각 설명을 보강한다. 공개된 A01/A02와 다른 미선택 완성본은 자동 수정하지 않는다.'),
 ('질문·얻는 점·실제2–3단계 순서·첫 사례 연결. 본론에 없는 약속 금지.',
  '쉬운 뜻·핵심 관계/전제·질문·얻는 점·실제2–3단계 순서·첫 사례 연결을 장면과 동시 설명. 끝에는 같은 질문에 답하는 핵심2–3개 정리(긴 영상 약10초, 기존 회원 안내 앞). 충분한 기존 개론/정리 음성을 통합해 중복하지 않음. 본론에 없는 약속 금지.')]
}
START='<!-- ANIMATION-OVERVIEW-V7-20261114 -->'
END='<!-- ANIMATION-OVERVIEW-V7-20261114-END -->'
PREFIX=HERE.relative_to(ROOT).as_posix()+'/'
SPEC=WORK/'scoped-progress-commit.json'
helper=ROOT/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
module=importlib.util.spec_from_file_location('overview_scoped',helper)
scoped=importlib.util.module_from_spec(module);module.loader.exec_module(scoped)

def overlay(name,raw,spec):
    if name==CONTROL:
        raw=scoped.patch(raw,[KEY],spec['control'])
        return scoped.patch(raw,['openingOverviewClosingRecapPolicy20261114'],spec['policy'])
    if name==WORKLIST:
        for row in spec['rows']:
            matches=[i for i,q in enumerate(scoped.load(raw)['rows']) if q['id']==row['id']]
            assert len(matches)==1
            raw=scoped.patch(raw,['rows',matches[0],'overviewRevision'],row['revision'])
        return raw
    if name in RULES:
        for old,new in RULES[name]:
            a,b=old.encode(),new.encode()
            if b in raw:assert raw.count(b)==1;continue
            if name=='docs/VIDEO_WORKFLOW.md' and old.startswith('기존 2–4문장') and a not in raw:
                # An unrelated staged rewrite omitted the earlier Abstract paragraph.
                # Add ONLY this user's new policy, not that foreign paragraph.
                own=new[len(old)+1:].encode()
                anchor='다음 표를 채운 설계가 제작의 입력이다.'.encode()
                assert raw.count(anchor)==1
                if own not in raw:
                    nl=b'\r\n' if b'\r\n' in raw else b'\n'
                    raw=raw.replace(anchor,own+nl+nl+anchor,1)
                continue
            assert raw.count(a)==1,(name,old[:100],raw.count(a))
            raw=raw.replace(a,b,1)
        return raw
    if name==TABLE:
        first,last=raw.find(START.encode()),raw.find(END.encode())
        assert (first<0)==(last<0)
        nl='\r\n' if b'\r\n' in raw else '\n'
        block=spec['markdown'].replace('\n',nl).encode()
        return raw[:first]+block+raw[last+len(END):] if first>=0 else raw+(nl*2).encode()+block+nl.encode()
    raise AssertionError(name)

def validate(spec):
    assert spec['scope']==KEY
    assert [r['id'] for r in spec['rows']]==[f'A{i:02}' for i in range(3,19)]
    assert spec['control']['excludedUploaded']==['A01','A02']
    assert not any(spec['control'][k] for k in ['youtubeAuthorized','driveAuthorized','ttsAuthorized','schedulingAuthorized','deletionAuthorized'])
    for name in spec['ownedPaths']:
        p=PurePosixPath(name)
        assert name.startswith(PREFIX) and '..' not in p.parts and p.suffix in {'.py','.json','.md','.cjs'} and (ROOT/name).is_file()
    return sorted(spec['ownedPaths'])+sorted(scoped.SHARED)

def prepare():
    plan=read(HERE/'plan.json');done=[];rows=[];now=stamp()
    table=[START,'','## 애니메이션 개론·정리 통합 수정','','[16편 통합 검수](http://127.0.0.1:9301/)','','A03–A18만 선택. v6 전체 음성·본문·10초 정리 보존. 업로드된 A01/A02 제외. 플랫폼 변경 없음.','','| 편 | 주제 | 개론 보강 상태 | 사용자 검수 |','|---|---|---|---|']
    for row in plan['episodes']:
        ep=row['id'];receipt=OUTPUT/ep/'delivery.json'
        ready=receipt.exists() and not read(receipt).get('visualReviewPending',True)
        if ready:done.append(ep)
        status='개론·정리 통합본 검수 가능' if ready else '기존 개론 음성에 관계도·학습 순서 보강 중'
        revision=dict(revision='overview-v7',status=status,updatedAt=now,humanReviewed=False,platformChanged=False,
                      overviewRange=[row['startFrame']/60,row['endFrame']/60],summaryFrames=600,audioChanged=False,
                      reviewUrl=f'http://127.0.0.1:9301/{ep}/' if ready else None)
        if ready:
            revision['delivery']=str(receipt)
            revision['captionedMasterSha256']=next(f['sha256'] for f in read(receipt)['files'] if f['kind']=='captioned.mp4')
        rows.append(dict(id=ep,revision=revision));table.append(f'| {ep} | {row["title"].split("|")[0]} | {status} | 대기 |')
    table+=['',END]
    control=dict(id='animation-overview-v7',requestedAt=plan['selectedAt'],userEvidence=plan['userEvidence'],
        status='local-final-review-ready' if len(done)==16 else 'opening-visual-revision',scope=plan['scope'],excludedUploaded=['A01','A02'],
        renderAuthorized=True,ttsAuthorized=False,youtubeAuthorized=False,driveAuthorized=False,schedulingAuthorized=False,deletionAuthorized=False,
        audioStrategy='copy original AAC and SRT byte-for-byte; topic-specific diagrams synchronized to existing overview speech',
        checkpoint=str(HERE.relative_to(ROOT)/'checkpoint.json'),completed=done,reviewUrl='http://127.0.0.1:9301/',humanReviewed=False,platformChanged=False,updatedAt=now)
    policy=dict(id='opening-overview-closing-recap-v1',requestedOn='2026-11-14',scope='Future explicitly selected videos; finite A03–A18 visual opening revision',
        opening='Plain meaning, essential relationship/prerequisite and actual learning steps, narrated over relevant examples/diagrams after gameplay hook',
        closing='Answer the opening question and recap 2–3 points; about10s before existing membership ending in long-form, proportionate in shorts',
        preservation='Integrate sufficient approved speech; no duplicate intro, text-only silent summary, padding or automatic remake',source='Latest explicit user instruction')
    save(HERE/'checkpoint.json',dict(stage=control['status'],updatedAt=now,scope=plan['scope'],completed=done,
        remaining=[e for e in plan['scope'] if e not in done],humanReviewed=False,platformChanged=False,reviewUrl=control['reviewUrl']))
    markdown='\n'.join(table);(HERE/'review-table.md').write_text(markdown+'\n',encoding='utf-8')
    owned=sorted(p.relative_to(ROOT).as_posix() for p in HERE.iterdir() if p.is_file() and p.suffix in {'.py','.json','.md','.cjs'})
    save(SPEC,dict(scope=KEY,control=control,policy=policy,rows=rows,markdown=markdown,ownedPaths=owned))
    print(SPEC)

if __name__=='__main__':
    if sys.argv[1:]==['--prepare']:prepare()
    else:
        scoped.SHARED={CONTROL,WORKLIST,TABLE,*RULES}
        scoped.overlay,scoped.validate=overlay,validate
        scoped.main()
