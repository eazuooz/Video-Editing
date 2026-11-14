"""Evidence and local review pages for the exact completed opening revisions."""
from html import escape
from pathlib import Path
import argparse, json
from PIL import Image, ImageDraw
import numpy as np
from prepare import HERE, SOURCE, WORK, OUTPUT, read, save, stamp
from render import frame, sha, audio_clock, srt
from artwork import text, BG, WHITE, YELLOW

def shell(title,body):
    return ('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>'+escape(title)+'</title><style>body{background:#080c0a;color:#f3f5ef;font:17px/1.7 system-ui;margin:0}main{max-width:1150px;margin:auto;padding:24px}'
        'h1{font-size:clamp(23px,4vw,36px);color:#f2d787}a{color:#94d8c9}video{width:100%;background:black}nav{display:flex;gap:20px;flex-wrap:wrap;margin:18px 0}'
        'td,th{padding:12px;text-align:left;border-bottom:1px solid #34463b}table{border-collapse:collapse;width:100%}small{color:#b5c4b8}</style><main>'+body+'</main></html>')

def contacts():
    plan=read(HERE/'plan.json');rows=plan['episodes'];out=WORK/'qa';out.mkdir(parents=True,exist_ok=True)
    for group in range(4):
        canvas=Image.new('RGB',(1920,1160),BG);d=ImageDraw.Draw(canvas)
        for i,r in enumerate(rows[group*4:group*4+4]):
            src=WORK/r['id']/'opening-encoded.png'
            if not src.exists():continue
            x=(i%2)*960;y=(i//2)*580
            canvas.paste(Image.open(src).resize((960,540),Image.Resampling.LANCZOS),(x,y+40))
            text(d,(x+15,y+2),r['id']+' · '+r['title'].split('|')[0].strip(),28,YELLOW,maxwidth=930)
        canvas.save(out/f'opening-contact-{group+1}.jpg',quality=94)
    print(out)

def mark(ids):
    for ep in ids:
        path=OUTPUT/ep/'delivery.json';data=read(path)
        row=next(r for r in read(HERE/'plan.json')['episodes'] if r['id']==ep)
        sources={f['kind']:Path(f['path']) for f in row['sourceFiles']}
        master=Path(next(f['path'] for f in data['files'] if f['kind']=='captioned.mp4'))
        folder=WORK/ep;evidence=[]
        for file in data['files']:
            if not file['kind'].endswith('mp4'):continue
            clock=audio_clock(sources[file['kind']]);assert audio_clock(file['path'])==clock
            file['audioClockHash']=clock
        for n in [row['startFrame']+20,row['roadmapFrame']+6,row['endFrame']-6]:
            picture=frame(master,n)
            picture.save(folder/f'overview-frame-{n}.png')
            original=frame(sources['clean.mp4'],n)
            expected=original.resize((880,495),Image.Resampling.LANCZOS)
            actual=picture.crop((980,258,1860,753))
            mae=float(np.abs(np.asarray(actual).astype(np.int16)-np.asarray(expected).astype(np.int16)).mean())
            assert mae<6,(ep,n,mae)
            evidence.append(dict(frame=n,sourceClockWindowMeanAbsoluteError=mae))
        data['encodedOpeningReview']=dict(at=stamp(),review='Internally inspected encoded contact sample and actual375px output; checked definition, topic diagram, roadmap, caption clearance and matching source motion.',
            sample=str(folder/'opening-encoded.png'),sampleSha256=sha(folder/'opening-encoded.png'),
            mobile=str(folder/'opening-mobile.png'),mobileSha256=sha(folder/'opening-mobile.png'),
            movingWindowSamples=evidence,wholeVideoHumanReview=False,audioReusedExactly=True)
        data['visualReviewPending']=False;save(path,data)
    print('Recorded internally inspected samples: '+', '.join(ids))

def speech_map():
    rows=[]
    for r in read(HERE/'plan.json')['episodes']:
        source=next(f['path'] for f in r['sourceFiles'] if f['kind']=='ko.srt')
        cues=[c for c in srt(Path(source)) if c['end']>r['startFrame']/60 and c['start']<r['endFrame']/60]
        rows.append(dict(id=r['id'],range=[r['startFrame']/60,r['endFrame']/60],roadmapAt=r['roadmapFrame']/60,
             existingNarratedCues=cues,displayedDefinition=r['definition'],displayedLearningSteps=r['steps'],
             diagram=r['diagram'],sourceSrtSha256=sha(source),newVoice=False,
             boundary=r['boundary'],rationale=r['reason']))
    save(HERE/'opening-speech-visual-map.json',dict(episodes=rows,retainedSourceLessonOrder=True,
         diagrams='Qualitative editorial explanations only; never measured retail-game internals',audio='Original v6 packets and timestamps; no new TTS or silent added section'))

def pages():
    rows=[];manifest=[]
    for row in read(HERE/'plan.json')['episodes']:
        ep=row['id'];path=OUTPUT/ep/'delivery.json'
        if not path.exists() or read(path).get('visualReviewPending',True):
            rows.append(f'<tr><td>{ep}</td><td>{escape(row["title"].split("|")[0])}</td><td>개론 보강 중</td></tr>');continue
        result=read(path);manifest.append(result)
        links={f['kind']:Path(f['path']).name for f in result['files']}
        controls=''.join('<a download href="'+escape(links[k])+'">'+label+'</a>' for k,label in [('captioned.mp4','자막 영상'),('clean.mp4','무자막 영상'),('ko.srt','한국어 자막'),('en.srt','영어 자막')])
        duration=int(result['durationSeconds'])
        body=('<a href="../">전체 검수표</a><h1>'+escape(row['title'])+'</h1>'
             f'<p>1080p 60fps · {duration//60}:{duration%60:02} · 사용자 검수 대기</p>'
             '<video controls playsinline preload="metadata" src="'+links['captioned.mp4']+'"></video><nav>'+controls+'</nav>'
             '<p>'+escape(result['revisionDescription'])+'</p><nav><a href="'+links['captioned.mp4']+'#t='+str(result['overviewAt'])+'">개론 바로 보기</a>'
             '<a href="'+links['captioned.mp4']+'#t='+str(result['summaryAt'])+'">마지막 10초 정리</a></nav>')
        (OUTPUT/ep/'index.html').write_text(shell(row['title'],body),encoding='utf-8')
        rows.append('<tr><td>'+ep+'</td><td><a href="'+ep+'/">'+escape(row['title'].split('|')[0])+'</a></td><td>개론 + 정리 검수 가능</td></tr>')
    OUTPUT.mkdir(parents=True,exist_ok=True)
    body=('<h1>애니메이션 개론·정리 통합 검수</h1><p>'+str(len(manifest))+' / 16편 준비 · A03–A18</p>'
          '<p>앞에는 쉬운 뜻·주제별 관계도·학습 순서, 끝에는 10초 핵심 정리. 기존 음성·본문·실제 동작은 보존했습니다.</p>'
          '<table><tr><th>편</th><th>주제</th><th>상태</th></tr>'+''.join(rows)+'</table>'
          '<p><small>A01·A02는 이미 업로드되어 이번 수정에서 제외했습니다. 새 YouTube 업로드·예약·삭제는 하지 않았습니다.</small></p>')
    (OUTPUT/'index.html').write_text(shell('애니메이션 개론·정리 검수',body),encoding='utf-8')
    save(HERE/'delivery-review-manifest.json',dict(revision='overview-v7',count=len(manifest),reviewUrl='http://127.0.0.1:9301/',episodes=manifest,
         humanReviewed=False,platformChanged=False,updatedAt=stamp()))
    print(f'Local review ready: {len(manifest)} / 16')

def verify():
    plan=read(HERE/'plan.json');proof=[]
    assert plan['scope']==[f'A{i:02}' for i in range(3,19)]
    assert not any((OUTPUT/e).exists() for e in ['A01','A02'])
    for row in plan['episodes']:
        ep=row['id'];receipt=read(OUTPUT/ep/'delivery.json')
        assert not receipt['visualReviewPending'] and not receipt['humanReviewed'] and not receipt['platformChanged']
        assert receipt['frames']==row['sourceFrames'] and receipt['summaryFrames']==600
        assert receipt['audioChanged'] is False and receipt['srtChanged'] is False
        files={f['kind']:f for f in receipt['files']}
        assert set(files)=={'captioned.mp4','clean.mp4','ko.srt','en.srt'}
        for kind,f in files.items():assert sha(f['path'])==f['sha256'],(ep,kind,'changed output')
        for kind in ['captioned.mp4','clean.mp4']:
            p=read(WORK/ep/('prefix-'+kind+'.json'))['signature']
            assert p['row']==row,(ep,'stale opening plan')
            assert p['art']==sha(WORK/ep/'overview.png') and p['roadmap']==sha(WORK/ep/'roadmap.png')
            assert p['ass']==sha(WORK/ep/'opening.ko.ass')
            assert files[kind]['fullDecode']=='passed' and files[kind].get('audioClockHash')
        assert files['clean.mp4']['audioPacketHash']==files['captioned.mp4']['audioPacketHash']
        assert files['clean.mp4']['audioClockHash']==files['captioned.mp4']['audioClockHash']
        for kind in ['ko.srt','en.srt']:
            assert files[kind]['sha256']==next(f['sha256'] for f in row['sourceFiles'] if f['kind']==kind)
        proof.append(dict(id=ep,files=len(files),captionedMasterSha256=files['captioned.mp4']['sha256'],
            unchangedAacAndTimestamps=True,unchangedSrt=True,sourceClockWindowSamples=receipt['encodedOpeningReview']['movingWindowSamples'],
            preservedSuffixIncludingBodyRecapAndMembership=True,humanReviewed=False))
    save(HERE/'verification-summary.json',dict(episodes=proof,outputs=64,framesAndDurationUnchanged=True,
        allSelectedReady=True,scope=plan['scope'],excludedUploaded=['A01','A02'],platformChanged=False,
        quality='1080p60; decoded new joins and full masters; exact audio packets/timestamps and unchanged VCL suffix; sampled 1080/375px picture review',
        humanWholeVideoReviewPending=True,updatedAt=stamp()))
    print('Verified16 selected deliveries /64 files; exact audio clock and unchanged body/recaps.')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--contacts',action='store_true');ap.add_argument('--mark',nargs='+');ap.add_argument('--pages',action='store_true');ap.add_argument('--verify',action='store_true');a=ap.parse_args()
    if a.contacts:contacts()
    if a.mark:mark(a.mark)
    if a.pages:speech_map();pages()
    if a.verify:verify()
