"""Reflect the six selected review actions only; no platform, media or Git operations."""
from pathlib import Path
import argparse, copy, datetime, hashlib, json, re
from scoped_json import patch, parse

R = Path(__file__).resolve().parents[3]
H = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def cell(s): return str(s).replace('|', ' / ').replace('\n', ' ')
def ready_revision(slug):
    ref=f'projects/{slug}/production/clarity-v3/review-status.json'; p=R/ref
    if not p.exists():return None
    review=read(p)
    if review.get('status')!='local-review-ready' or review.get('fourOutputsVerified') is not True:return None
    folder=R/'projects'/slug/'production/local/clarity-v3/delivery/output'/slug
    reported=Path(review['localOutputDirectory'])
    if not reported.is_absolute():reported=R/reported
    assert reported.resolve()==folder.resolve(),'Unexpected ready revision output folder'
    paths={k:folder/(slug+suffix) for k,suffix in [('captionedVideo','.captioned.mp4'),('cleanVideo','.clean.mp4'),('captionsKo','.ko.srt'),('captionsEn','.en.srt')]}
    paths['index']=folder/'index.html'
    assert all(p.is_file() and p.stat().st_size>0 for p in paths.values()),'Ready receipt has missing delivery files'
    assert digest(paths['captionedVideo'])==review['captionedSha256'],'Ready receipt differs from delivered master'
    assert isinstance(review['durationSeconds'],(int,float)) and review['durationSeconds']>0
    return ref,review,{k:p.relative_to(R).as_posix() for k,p in paths.items()}
def upload_state(p):
    done=[]
    for key,label in [('thumbnailApplied','썸네일'),('descriptionApplied','설명'),('tagsApplied','태그')]:
        if p.get(key):done.append(label)
    if p.get('title'):done.insert(0,'제목')
    if p.get('playlist'):done.append('재생목록')
    for key,label in [('koManualSubtitles','수동 한국어 자막'),('enManualSubtitles','수동 영어 자막'),('englishMetadata','영문 제목·설명')]:
        if str(p.get(key,'')).startswith(('saved','published')):done.append(label)
    if p.get('card',{}).get('saved'):done.append('00:00 코칭 카드')
    if p.get('endScreen',{}).get('saved'):done.append('마지막 10초 엔딩')
    playback=p.get('playback',{})
    if playback.get('decoded')==[1920,1080] and '1080p60' in playback.get('qualityMenu',''):
        done.append('1080p60 재생 확인')
    if playback.get('privateLabel'):done.append('비공개 표시 확인')
    labels={'user-ad-self-assessment':'사용자 광고 평가','AI-field-user-confirmation-after-auto-review-rejection':'사용자 AI 표시 확인','final-workflow-save-and-readback':'최종 저장·재확인'}
    remaining=[labels.get(x,x) for x in p.get('remaining',[])]
    complete=p.get('finalWorkflowSaved') is True
    available=p.get('status')=='available-settings-complete-private-upload-draft'
    return done,remaining,complete,available
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true',help='Validate receipts without writing the worklist');args=ap.parse_args()
    auth = read(H/'authorization.json')
    path = R/'shared/publishing/video-worklist.json'
    before_raw=path.read_bytes(); initial_worklist_sha=hashlib.sha256(before_raw).hexdigest()
    before=json.loads(before_raw.decode('utf-8-sig')); data = copy.deepcopy(before)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    targets = {x['id']: x for x in auth['privateUploads'] + auth['revisions']}
    assert set(targets) == {'D25','D26','D27','D28','D29','D30'}
    rows = {r['id']: r for r in data['rows']}
    authref = 'production/batches/design-25-30-review-actions-20261029/authorization.json'
    for id, a in targets.items():
        r = rows[id]; assert r['slug'] == a['slug']
        old = copy.deepcopy(r['localReview'])
        history=r.setdefault('localReviewHistory', [])
        # Preserve real prior version records, without adding timestamp-only copies
        # of the same revision every time this helper is rerun.
        if not any(x.get('captionedSha256')==old.get('captionedSha256') and x.get('index')==old.get('index') for x in history):history.append(old)
        r['selectedBatch'] = H.name
        r['updatedAt'] = now
        if authref not in r['evidence']: r['evidence'].append(authref)
        if id in {'D25','D29'}:
            r['activeRevision'] = 'clarity-v3'
            r['productionStatus'] = 'v2 완성본 보존 · clarity-v3 수정 중'
            r['reviewStatus'] = '새 수정본 완성 후 재검수 필요'
            r['humanApproval'] = 'revision-requested'
            r['platformStatus'] = '미업로드 · 새 검수 전 보류'
            r['executionStatus'] = '설명 확장·새 시연 제작 중 · 로컬 재검수까지'
            r['internalQaStatus'] = 'unity-visual-v2 internal QA preserved; clarity-v3 pending'
            r['localReview']['status'] = 'prior-version-preserved-new-revision-requested'
            r['localReview']['feedbackEvidence'] = authref
            r['revisionInProduction'] = {**r.get('revisionInProduction',{}),'revision':'clarity-v3', 'baseMasterSha256':a['baseMasterSha256'],
                'userEvidence':auth['userEvidence'], 'humanWholeViewing':'not separately asserted',
                'newReviewRequired':True, 'privateUploadAuthorized':False,
                'plan':f"projects/{a['slug']}/production/clarity-v3", 'updatedAt':now}
            r['notes'] = ('사용자 피드백으로 색의 역할·흑백 비교 설명을 늘리고 Unity 시연을 상세화하는 clarity-v3 제작 중.' if id=='D25' else
                '사용자 피드백으로 초보자 친화 설계의 대전게임 예시를 공감하기 쉬운 사례로 수정하는 clarity-v3 제작 중.') + ' 기존 v2 영상·자막·검수 기록 보존. 새 로컬 4종 완성본 검수 전 업로드 보류.'
            ready=ready_revision(a['slug'])
            if ready:
                reviewref,review,paths=ready
                r.update(productionComplete=True,localMasterAvailable=True,
                    productionStatus='clarity-v3 수정본 4종 완성 · 이전 버전 보존',
                    reviewStatus='새 수정본 사용자 검수 대기',humanApproval='pending-new-revision-review',
                    platformStatus='미업로드 · 새 수정본 검수 대기',executionStatus='로컬 수정본 완성 · 사용자 검수까지',
                    internalQaStatus='clarity-v3 internal QA complete; user review pending')
                r['localReview']={**old,**paths,'status':'ready-for-human-local-review','captionedSha256':review['captionedSha256'],
                    'durationSeconds':review['durationSeconds'],'actualUserViewed':False,'humanWholeListening':'pending',
                    'updatedAt':now,'reviewEvidence':reviewref}
                r['revisionInProduction'].update(status='local-review-ready',captionedSha256=review['captionedSha256'],reviewEvidence=reviewref)
                if reviewref not in r['evidence']:r['evidence'].append(reviewref)
                r['notes']='clarity-v3 설명 보완과 로컬 영상·한영 자막 4종 검증 완료. 새 파일·해시로 사용자 검수 대기. 기존 v2 완성본·검수 기록 보존. 새 수정본 업로드 승인이나 사용자 전체 시청·청취를 주장하지 않음.'
        else:
            receiptref = f"projects/{a['slug']}/production/upload-20261029/youtube-progress.json"
            p = read(R/receiptref)
            assert p['masterSha256'] == a['sha256'] == old['captionedSha256']
            assert p['uploadComplete']
            done,remaining,complete,available=upload_state(p)
            r['reviewStatus'] = '업로드 승인 · 전체 청취 별도'
            r['humanApproval'] = 'approved-specific-master-for-private-upload'
            r['platformStatus'] = '비공개 업로드·설정 완료' if complete else '비공개 초안 · '+(' / '.join(remaining) or '최종 저장 확인 대기')
            r['executionStatus'] = '비공개 설정 저장 완료' if complete else ('가능한 설정 완료 · 사용자 확인 후 최종 저장' if available else '파일 업로드 완료 · 남은 설정 처리 중')
            r['videoId'],r['url'] = p['videoId'],p['url']
            r['internalQaStatus'] = 'complete; explicit master upload approval; whole viewing/listening not separately asserted'
            r['localReview']['status'] = 'approved-specific-master-for-private-upload'
            r['localReview']['uploadApprovalEvidence'] = authref
            r['localReview']['humanWholeListening'] = 'not separately asserted'
            r['userReview'] = {**r.get('userReview',{}),'status':'explicit-private-upload-approval-after-targeted-feedback',
                'masterSha256':a['sha256'], 'evidence':authref, 'humanWholeViewing':'not separately asserted',
                'humanWholeListening':'not separately asserted', 'updatedAt':now}
            r['uploadProgress'] = {**r.get('uploadProgress',{}),**copy.deepcopy(p)}
            r['uploadProgress']['evidence'] = receiptref
            r['uploadProgress']['fullSettingsComplete'] = complete
            if receiptref not in r['evidence']:r['evidence'].append(receiptref)
            r['notes'] = '해당 v2 master 해시의 명시 업로드 승인. 파일 업로드 완료. 실제 완료: '+', '.join(done)+'. '
            r['notes'] += ('최종 저장 완료. ' if complete else '남은 항목: '+(', '.join(remaining) or '최종 저장 상태 확인')+'. ')
            r['notes'] += '전체 연속 시청·청취를 별도로 주장하지 않음. 공개·예약·삭제 없음.'
    assert {k:v for k,v in data.items() if k!='rows'} == {k:v for k,v in before.items() if k!='rows'}
    assert [r for r in data['rows'] if r['id'] not in targets] == [r for r in before['rows'] if r['id'] not in targets]
    md = R/'docs/VIDEO_WORKLIST.md'; oldmd_raw=md.read_bytes(); initial_md_sha=hashlib.sha256(oldmd_raw).hexdigest()
    oldmd=oldmd_raw.decode('utf-8'); lines = oldmd.splitlines(); changed = []; matched=[]
    def title(r): return f"[{cell(r['title'])}]({r['url']})" if r.get('url') else cell(r['title'])
    for i,line in enumerate(lines):
        for id in targets:
            r=rows[id]; icon='☑' if id not in {'D25','D29'} else '☐'
            if re.match(r'^\| \d+ \| 게임디자인 \| '+id+r' ', line):
                matched.append((i,id))
                order=line.split('|')[1].strip()
                lines[i]=f"| {order} | 게임디자인 | {id} {title(r)} | {cell(r['executionStatus'])} | {icon} {cell(r['reviewStatus'])} |"
            elif line.startswith('| '+id+' | '):
                matched.append((i,id))
                lines[i]=f"| {id} | {title(r)} | {'☑' if r['productionComplete'] else '☐'} {cell(r['productionStatus'])} | {icon} {cell(r['reviewStatus'])} | {cell(r['platformStatus'])} |"
            elif line.startswith('| '+id+' '):
                matched.append((i,id))
                lines[i]=f"| {id} {cell(r['title'])} | {cell(r['notes'])} |"
        if line != lines[i]:changed.append(i+1)
    assert len(changed)<=18, ('Unexpected scoped worklist table matches',changed)
    assert len(matched) in (12,18) and all(sum(id==item[1] for item in matched) in (2,3) for id in targets), 'Selected rendered rows were not all found'
    # Existing rendered document intentionally remains byte-identical outside selected rows.
    assert len(lines)==len(oldmd.splitlines())
    beforehash=initial_worklist_sha; mdhash=initial_md_sha
    assert beforehash==digest(path) and mdhash==digest(md),'Worklist changed while preparing update; preserve concurrent edits'
    updated_raw=before_raw
    for i,row in enumerate(data['rows']):
        if row['id'] in targets:updated_raw=patch(updated_raw,['rows',i],row)
    assert json.loads(updated_raw.decode('utf-8-sig'))==data
    def without_owned_rows(raw):
        text=raw.decode('utf-8-sig');nodes=parse(text).c['rows'].c;last=0;parts=[]
        for node in nodes:
            if node.v['id'] in targets:parts.append(text[last:node.s]);last=node.e
        parts.append(text[last:]);return ''.join(parts)
    assert without_owned_rows(updated_raw)==without_owned_rows(before_raw),'Unrelated JSON bytes changed'
    original_lines=oldmd.splitlines(keepends=True)
    updated_md=''.join(new+original[len(old):] for new,old,original in zip(lines,oldmd.splitlines(),original_lines))
    assert updated_md.splitlines()==lines
    if args.dry_run:
        print(json.dumps({'status':'validated-no-write','scope':sorted(targets),'foreignRowsUnchanged':True,'topLevelFieldsUnchanged':True,
            'renderedChangedLines':changed,'rows':[{'id':id,'productionStatus':rows[id]['productionStatus'],'platformStatus':rows[id]['platformStatus'],
            'reviewStatus':rows[id]['reviewStatus'],'notes':rows[id]['notes']} for id in sorted(targets)],'gitMutation':False},ensure_ascii=False))
        return
    path.write_bytes(updated_raw)
    md.write_bytes(updated_md.encode('utf-8'))
    report={'updatedAt':now,'scope':sorted(targets),'foreignRowsUnchanged':True,'topLevelFieldsUnchanged':True,
      'unrelatedJsonBytesPreserved':True,'unrelatedMarkdownLinesAndEndingsPreserved':True,
      'renderedChangedLines':changed,'priorWorklistSha256':beforehash,'worklistSha256':digest(path),
      'priorMarkdownSha256':mdhash,'markdownSha256':digest(md),'platformMutation':False,'gitMutation':False}
    (H/'worklist-update-proof.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
if __name__=='__main__':main()
