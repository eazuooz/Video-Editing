"""Record observed Studio results; never perform platform actions or rerender."""
import copy, datetime, hashlib, html, json
from pathlib import Path

ROOT = Path('D:/Github/VideoEditing')
HERE = Path(__file__).resolve().parent
KEY = 'mathPublishing20261117'
START = '<!-- MATH-PUBLISHING-20261117-START -->'
END = '<!-- MATH-PUBLISHING-20261117-END -->'
IDS = ['4bh4TqO-6z8','ZTw3CrsxpAE','_NvlqXhk0d8','9tPjrIf4b7g',
       'G3aQDpwqMro','XNKEAUHyGjk','f7un7rBl24E','wsUtovhaado',
       'WSliRWlkKEY','7sCfXJiLPRg','S8H4GHSLMsw','quCPht9lvE8','oMdJs2fFnWc']
ROW_FIELDS = ['videoId','url','platformStatus','reviewStatus','humanApproval',
              'executionStatus','publishing20261117']

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def write(p, data):
    Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def replace_block(path, block):
    p=ROOT/path; old=p.read_text(encoding='utf-8-sig')
    if START in old:
        old=old[:old.index(START)]+block+old[old.index(END)+len(END):]
    else:
        old=old.rstrip()+'\n\n'+block+'\n'
    p.write_text(old,encoding='utf8')

def main():
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    batch=read(HERE/'batch.json'); progress=read(HERE/'platform-progress.json')
    table=(HERE/'evidence/saved-schedule-overview.txt').read_text(encoding='utf8')
    receipts=[]
    for i, row in enumerate(batch['rows']):
        ident=row['id']; vid=IDS[i]; day=17+i
        assert f'27. 1. {day}. 8:00' in table and vid in table
        details=(HERE/f'evidence/{ident}-saved-details.txt').read_text(encoding='utf8')
        english=(HERE/f'evidence/{ident}-saved-english.txt').read_text(encoding='utf8')
        assert f'2027. 1. {day}.' in details and '오전 8:00' in details and 'GMT+0900' in details
        assert '고화질 완료' in details and '게임 수학(Game Math) PART 2' in details
        assert '수동 자막' in english and '게시됨' in english
        if i:
            quality=(HERE/f'evidence/{ident}-playback-quality.txt').read_text(encoding='utf8')
            assert '1080p60' in quality and '자막 사용 안함' in quality
        evidence={}
        for p in sorted((HERE/'evidence').glob(f'{ident}-*')):
            if p.is_file(): evidence[p.name]={'path':str(p),'sha256':digest(p)}
        receipt={
            'id':ident,'actualVideoId':vid,'url':'https://youtu.be/'+vid,
            'status':'scheduled','scheduledKst':f'2027-01-{day:02d}T08:00:00+09:00',
            'titleKo':row['titleKo'],'titleEn':row['titleEn'],
            'approvedCaptionedMaster':row['video'],'manualSubtitles':row['subtitles'],
            'captionedMasterFormat':'1920x1080 / 60fps',
            'userReviewedAndUploadAuthorized':True,
            'userAuthorization':batch['userEvidence'],
            'playlistId':batch['playlistId'],'playlistName':'게임 수학(Game Math) PART 2',
            'settings':{
                'koTitleDescription':True,'englishTitleDescription':True,
                'manualKoSrtPublished':True,'manualEnSrtPublished':True,
                'englishLanguage':'en-US' if i<3 else 'en',
                'thumbnailApplied':True,'playlistApplied':True,
                'languageKo':True,'madeForKids':False,'category':'Education',
                'monetizationOn':True,
                'adSelfCertification':progress['rows'][ident]['adSelfCertification'],
                'automaticCopyrightCheck':'complete-no-issues',
                'automaticAdSuitabilityCheck':'complete-no-issues',
                'coachingCard':{'startSeconds':0,'title':'프로그래밍 과외',
                    'teaser':'프로그래밍 과외','url':'https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328'},
                'last10sEndScreen':['math-part2-playlist','own-channel-subscribe','canonical-coaching-link'],
                'sdHdProcessing':'complete','savedSettingsReopened':True,
                'uploadedFrameWithCcOff':'visually-inspected',
                'youtube1080p60Available':True,
                'pinnedComment':'prepared-pending-video-publication',
                'automaticDubbing':'platform-processing-not-manually-reviewed'
            },
            'evidence':evidence,
            'm21QualityObservation':'CUA quality menu displayed automatic (1080p60 HD), CC off; then 1080p60 selected.' if i==0 else None,
            'verifiedAtKst':now,'existingVideosDeletedOrRescheduled':False,
            'continuousHumanListeningClaimed':False
        }
        write(HERE/ident/'youtube-upload.json',receipt);receipts.append(receipt)
        row.update(status='scheduled',actualVideoId=vid,scheduledKst=receipt['scheduledKst'],
                   receipt=str(HERE/ident/'youtube-upload.json'))
        package=read(HERE/ident/'package.json')
        package.update({k:copy.deepcopy(row[k]) for k in ['status','actualVideoId','scheduledKst','receipt']})
        write(HERE/ident/'package.json',package)
        progress['rows'][ident].update(status='scheduled-verified',enSrt=True,
            englishLocalization=True,savedSettingsReopened=True,sdHdProcessing='complete',
            uploadedFrameWithCcOff='visually-inspected',youtube1080p60Available=True)
    batch.update(status='all-13-scheduled-verified',actualFirstKst=receipts[0]['scheduledKst'],
        actualLastKst=receipts[-1]['scheduledKst'],completedAtKst=now,
        pinnedComments='prepared-pending-video-publication')
    write(HERE/'batch.json',batch);progress['updatedAt']=now;write(HERE/'platform-progress.json',progress)
    summary={'scope':[r['id'] for r in receipts],'status':'all-13-scheduled-verified',
        'firstKst':receipts[0]['scheduledKst'],'lastKst':receipts[-1]['scheduledKst'],
        'timeZone':'Asia/Seoul','cadence':'one-per-day',
        'existingAnchorVideoId':batch['actualExistingLastScheduledVideoId'],
        'existingAnchorKst':batch['actualExistingLastScheduledKst'],
        'playlistId':batch['playlistId'],'userEvidence':batch['userEvidence'],
        'all13UploadedOnce':True,'all13SavedSettingsReopened':True,
        'all13ManualKoEnSrt':True,'all13EnglishMetadata':True,
        'all13ActualPlayback1080p60CcOff':True,'existingVideosChanged':False,
        'platformActionsComplete':True,'pinnedComments':'pending-video-publication',
        'receipts':[str(HERE/r['id']/'youtube-upload.json') for r in receipts],
        'report':str(HERE/'review.html'),'verifiedAtKst':now}
    write(HERE/'summary.json',summary)
    w=read(ROOT/'shared/publishing/video-worklist.json');w[KEY]=copy.deepcopy(summary)
    for r in w['rows']:
        if r.get('id') not in summary['scope']:continue
        receipt=receipts[int(r['id'][1:])-21]
        r.update(videoId=receipt['actualVideoId'],url=receipt['url'],platformStatus='예약됨',
            reviewStatus='최종본 사용자 승인·업로드 설정 재열람 완료',
            humanApproval='사용자: 잘만들어진거같아 전부 업로드·예약 요청',
            executionStatus='예약 완료',publishing20261117={
                'status':'scheduled','scheduledKst':receipt['scheduledKst'],
                'receipt':str(HERE/r['id']/'youtube-upload.json'),
                'masterSha256':receipt['approvedCaptionedMaster']['sha256']})
    write(ROOT/'shared/publishing/video-worklist.json',w)
    c=read(ROOT/'shared/publishing/video-production-control.json')
    c.setdefault('scopedPublishingAuthorizations',{})[KEY]=copy.deepcopy(summary)
    write(ROOT/'shared/publishing/video-production-control.json',c)
    lines=[START,'### 게임수학 M21–M33 업로드·예약 완료 (2026-11-17)','',
        '사용자가 승인한 최신 captioned FHD60 마스터 13편을 각각 한 번 업로드했다. 기존 마지막 예약 2027-01-16 08:00 다음 날부터 매일 08:00 KST로 예약했다. 재생목록은 게임 수학(Game Math) PART 2다.','',
        '| 편 | 제목 | 공개일 (한국 시간 오전 8시) | 검수·플랫폼 상태 |',
        '|---|---|---|---|']
    for r in receipts:
        lines.append(f"| {r['id']} | [{r['titleKo']}]({r['url']}) | {r['scheduledKst'][:10]} | 예약·설정 재열람 완료 |")
    lines+=['','전편 수동 KO/EN SRT·영문 제목/설명·브랜드 썸네일·챕터/출처·00:00 코칭 카드·마지막10초 재생목록/구독/코칭 링크 적용. 수익 사용, 자기평가 제출, 자동 저작권/광고 검사 문제 없음, SD/HD 처리 및 실제 YouTube CCoff·1080p60 재생 확인. 고정 댓글은 공개 후 등록 대기. 기존 영상 삭제·교체·예약 변경 없음.','',f'[업로드 검수표](../production/batches/game-math-upload-20261117/review.html) · [실제 Studio 예약 화면](../production/batches/game-math-upload-20261117/evidence/studio-final-schedule-table.jpg)',END]
    block='\n'.join(lines)
    for doc in ['docs/VIDEO_WORKLIST.md','docs/GAME_MATH_PRIVATE_POLISH.md']:replace_block(doc,block)
    (HERE/'README.md').write_text('\n'.join(lines[1:-1])+'\n',encoding='utf8')
    trs=''.join(f"<tr><td>{r['id']}</td><td><a href='{r['url']}'>{html.escape(r['titleKo'])}</a></td><td>2027-01-{17+i:02d} 08:00</td><td>예약·검증 완료</td><td><a href='{r['id']}/youtube-upload.json'>설정 기록</a></td></tr>" for i,r in enumerate(receipts))
    page="""<!doctype html><html lang='ko'><meta charset='utf-8'><title>게임수학 13편 예약 완료</title><style>body{font:16px/1.7 'Malgun Gothic',sans-serif;margin:36px;color:#182028}h1{font-size:28px}table{border-collapse:collapse;width:100%}td,th{padding:12px;border-bottom:1px solid #d9dfe4;text-align:left}thead{background:#fff2a2}a{color:#174e78}img{max-width:100%;border:1px solid #ddd}p{max-width:1100px}</style><h1>게임수학 M21–M33 · 13편 예약 완료</h1><p>2027년 1월 17일~29일 · 매일 오전 8시 (한국 시간). 기존 마지막 예약 1월 16일 다음 날부터 하루에 한 편씩 공개됩니다. 게임 수학(Game Math) PART 2 재생목록에 추가했습니다.</p><p>전편 제목·설명·챕터·출처·브랜드 썸네일·수동 한영 SRT·영문 제목/설명·코칭 카드·엔딩 화면 저장 및 재열람 확인. 저작권/광고 검사 문제 없음. 실제 YouTube CCoff 및 1080p60 재생 확인. 고정 댓글은 공개 후 등록 대기입니다.</p><table><thead><tr><th>편</th><th>영상</th><th>공개 시각 KST</th><th>상태</th><th>검수 기록</th></tr></thead><tbody>"""+trs+"""</tbody></table><h2>실제 Studio 예약 목록</h2><img src='evidence/studio-final-schedule-table.jpg' alt='실제 YouTube Studio에 저장된 예약 목록'><h2>실제 업로드 재생 검수</h2><img src='evidence/playback-contact-sheet.jpg' alt='13편의 실제 YouTube CCoff 재생 화면'><p>기존 영상·예약·파일은 보존했습니다. 이 기록은 사용자 연속 청취나 자동 더빙 검수를 완료했다고 주장하지 않습니다.</p></html>"""
    (HERE/'review.html').write_text(page,encoding='utf8')
    write(HERE/'evidence-index.json',{p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted((HERE/'evidence').iterdir()) if p.is_file()})
    print('Recorded 13 observed schedules, settings, English metadata and playback checks.')

if __name__=='__main__':main()
