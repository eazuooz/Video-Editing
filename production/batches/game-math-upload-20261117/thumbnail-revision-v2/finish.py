"""Record the 13 visually verified thumbnail replacements; no platform actions."""
import datetime,hashlib,html,json
from pathlib import Path
from PIL import Image

ROOT=Path('D:/Github/VideoEditing')
HERE=Path(__file__).resolve().parent
BATCH=HERE.parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    manifest=rd(HERE/'manifest.json');platform=rd(HERE/'platform-progress.json')
    assert len(platform['rows'])==13 and len({r['id'] for r in platform['rows']})==13
    assert all(r['status'] in ('saved-and-reopened','server-save-confirmed-and-reopened') for r in platform['rows'])
    batch=rd(BATCH/'batch.json');registry=rd(ROOT/'shared/git-essential-images.json')
    entries={r['path']:r for r in registry['entries']};rows=[]
    for i,row in enumerate(batch['rows']):
        id=row['id'];asset=HERE/id/'thumbnail.png';old=BATCH/id/'thumbnail.png'
        assert row['actualVideoId']==next(x['videoId'] for x in platform['rows'] if x['id']==id)
        assert row['scheduledKst']==f'2027-01-{17+i:02d}T08:00:00+09:00'
        image=Image.open(asset);w,h=image.size
        assert w>=1280 and abs(w/h-16/9)<.01 and asset.stat().st_size<2097152
        saved=(HERE/f'evidence/{id}-saved.txt').read_text(encoding='utf8')
        assert row['actualVideoId'] in saved and 'text 예약됨' in saved
        assert (HERE/f'evidence/{id}-saved.jpg').is_file()
        current={'version':'illustrated-v2','path':str(asset),'sha256':sha(asset),
            'width':w,'height':h,'bytes':asset.stat().st_size,
            'method':'built-in image_gen','style':'natural calico-cat action illustration',
            'brandText':'얌얌코딩','mobileReview':'readable at approximately 327px',
            'storedAndReopenedInStudio':True,'actualSavedImageVisuallyReviewed':True,
            'savedProof':str(HERE/f'evidence/{id}-saved.jpg'),'verifiedAtKst':now}
        package=rd(BATCH/id/'package.json');receipt=rd(BATCH/id/'youtube-upload.json')
        before={'path':str(old),'sha256':sha(old),'status':'rejected-by-user',
            'reason':'Simple shapes with small pasted mascot did not satisfy the natural protagonist illustration rule.'}
        receipt['thumbnailRevision20261117']={'before':before,'after':current,
            'scope':'thumbnail-only','titleDescriptionSchedulePreserved':True}
        receipt['settings']['thumbnailApplied']=True;wr(BATCH/id/'youtube-upload.json',receipt)
        package.update(thumbnail=str(asset),thumbnailSha256=current['sha256'],thumbnailRevision20261117=current)
        row.update(thumbnail=str(asset),thumbnailSha256=current['sha256'],thumbnailRevision20261117=current)
        wr(BATCH/id/'package.json',package)
        rel=asset.relative_to(ROOT).as_posix()
        entries[rel]={'path':rel,'purpose':'delivery-thumbnail',
            'reason':'Final requested replacement thumbnail, individually generated and inspected: original channel calico cat actively demonstrates the episode concept; verified saved on the existing scheduled YouTube video.',
            'sha256':current['sha256'],'reviewedAt':now,'project':row['slug']}
        rows.append({'id':id,'videoId':row['actualVideoId'],'scheduledKst':row['scheduledKst'],
            'before':before,'after':current,'status':'saved-and-visually-verified'})
    registry['entries']=list(entries.values());wr(ROOT/'shared/git-essential-images.json',registry)
    wr(BATCH/'batch.json',batch)
    manifest.update(status='all-13-saved-and-visually-verified',verifiedAtKst=now,
        naturalCatActionsReviewed=True,koreanTextAndMobileLegibilityReviewed=True,
        technicalDirectionsReviewed=True,platformRows=rows,
        rejectedRendererRetired=True,serverSaveCompletionRequired=True,
        initialSaveRace={'found':'Some first attempts reloaded before the server save completed.',
            'resolved':'Reapplied M22–M33; waited for all-changes-saved response before reloading; inspected all 13 actual saved images.'})
    wr(HERE/'manifest.json',manifest)
    platform['status']='all-13-saved-and-visually-verified';platform['verifiedAtKst']=now
    wr(HERE/'platform-progress.json',platform)
    plan=rd(HERE/'plan.json');plan.update(status=manifest['status'],currentManifest=str(HERE/'manifest.json'));wr(HERE/'plan.json',plan)
    summary={'status':manifest['status'],'count':13,'report':str(HERE/'review.html'),
        'manifest':str(HERE/'manifest.json'),'method':'built-in image_gen',
        'existingIdsSchedulesTitlesDescriptionsPreserved':True,'verifiedAtKst':now}
    for file,kind in [('shared/publishing/video-worklist.json','worklist'),('shared/publishing/video-production-control.json','control')]:
        d=rd(ROOT/file)
        target=d['mathPublishing20261117'] if kind=='worklist' else d['scopedPublishingAuthorizations']['mathPublishing20261117']
        target['thumbnailRevision20261117']=summary
        if kind=='worklist':
            for r in d['rows']:
                if r['id'] in {x['id'] for x in rows}:
                    r['publishing20261117']['thumbnailRevision20261117']=summary
        wr(ROOT/file,d)
    d=rd(BATCH/'summary.json');d['thumbnailRevision20261117']=summary;wr(BATCH/'summary.json',d)
    d=rd(BATCH/'package-review.json');d['initialThumbnailReviewInvalidatedByUser']=True
    d['thumbnailRevision20261117']=summary;wr(BATCH/'package-review.json',d)
    note='2026-11-17 썸네일 수정: 단순 도형+작은 고양이 구성을 폐기하고, 주제를 직접 관찰·조작하는 큰 고양이 삽화로 13편 모두 교체했다. 서버 저장 완료 응답 후 재열람·실제 새 그림 대조 완료. 제목·설명·영상 ID·예약일 유지. [수정 썸네일 검수표](../production/batches/game-math-upload-20261117/thumbnail-revision-v2/review.html).'
    for f in ['docs/VIDEO_WORKLIST.md','docs/GAME_MATH_PRIVATE_POLISH.md']:
        p=ROOT/f;text=p.read_text(encoding='utf-8-sig');mark='<!-- MATH-PUBLISHING-20261117-END -->'
        if note not in text:text=text.replace(mark,note+'\n'+mark)
        p.write_text(text,encoding='utf8')
    cards=''.join(f"<article><h2>{r['id']}</h2><a href='https://youtu.be/{r['videoId']}'><img src='{r['id']}/thumbnail.png' alt='{html.escape(r['id'])} 주제별 고양이 삽화 썸네일'></a><p>저장·재열람·실제 그림 검수 완료</p><a href='evidence/{r['id']}-saved.jpg'>Studio 적용 증거</a></article>" for r in rows)
    page="""<!doctype html><html lang='ko'><meta charset='utf-8'><title>게임수학 썸네일 수정 검수</title><style>body{font:16px/1.6 'Malgun Gothic',sans-serif;background:#fffdf7;color:#181a18;margin:28px}h1{font-size:30px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:24px}article{border-bottom:2px solid #ffd342;padding-bottom:18px}img{width:100%;height:auto}h2{margin:0}a{color:#184f78}</style><h1>게임수학 M21–M33 · 썸네일 수정 완료</h1><p>단순 도형과 작은 고양이를 붙였던 기존 구성을 교체했습니다. 고양이가 각 강의 주제에 맞게 직접 관찰·조작하는 삽화, 노란 띠·흰 배경·검정/빨강 큰 한글·얌얌코딩 표기를 적용했습니다.</p><p>13편 모두 서버 저장 완료 후 재열람하여 새 그림을 확인했습니다. 기존 영상 ID·제목·설명·1월17~29일 오전8시 예약은 유지됩니다. <a href='manifest.json'>제작 프롬프트·수정 이력·해시</a></p><main>"""+cards+'</main></html>'
    (HERE/'review.html').write_text(page,encoding='utf8')
    mainpage=BATCH/'review.html';text=mainpage.read_text(encoding='utf8')
    text=text.replace("<h2>실제 Studio 예약 목록</h2>","<h2>썸네일 규칙 수정 완료</h2><p><a href='thumbnail-revision-v2/review.html'>새 삽화 썸네일 13편과 실제 적용 검수 보기</a></p><img src='thumbnail-revision-v2/studio-verify-board.jpg' alt='13편 새 썸네일 실제 Studio 저장 검수'><h2>최초 예약 기록</h2>")
    mainpage.write_text(text,encoding='utf8')
    (HERE/'README.md').write_text('# 게임수학 썸네일 수정\n\n13편 교체·서버 저장·재열람·실제 새 그림 검수 완료.\n\n[검수표](review.html) · [프롬프트·해시·이력](manifest.json)\n\n생성 방식: built-in image_gen. 승인 참조 그림체와 원래 고양이를 유지하고 주제별 행동 삽화를 개별 제작.\n\n기존 SVG 도형 렌더러를 폐기하고 재준비 시에도 검수된 삽화를 재사용하도록 변경했다. PNG 13개만 필수 납품 썸네일로 등록하고 QA 스크린샷·보드는 Git에서 제외한다.\n',encoding='utf8')
    print('13 final illustrated PNGs registered; current receipts and review pages updated.')

if __name__=='__main__':main()
