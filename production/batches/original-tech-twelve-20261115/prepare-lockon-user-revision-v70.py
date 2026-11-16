"""Prepare only the requested lock-on revision; preserve the delivered twelve."""
from pathlib import Path
import datetime, hashlib, importlib.util, json

H = Path(__file__).resolve().parent
ROOT = H.parents[2]
P = ROOT / 'projects/shorts-oot-ninja-show-z-targeting'
M = Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
R = M / P.name / 'revision-ninja-turns-20261116'
KEY = 'explicitOriginalTechTwelve20261115'


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def pin(p):
    with p.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    return dict(path=str(p.resolve()), sha256=digest)


def save(p, d):
    assert not p.exists(), p
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    request = H / 'lockon-requested-revision-source-v70.json'
    assert not request.exists()
    baseline = H / 'local-final-review-manifest-v1.json'
    original = read(baseline)
    assert original['verifiedFinalBundles'] == 12
    show = R / 'WwAVDIVpuS8-private-research-f137.mp4'
    metadata = read(R / 'WwAVDIVpuS8-metadata-v1.json')
    assert metadata['id'] == 'WwAVDIVpuS8' and metadata['duration'] == 16
    plan = read(P / 'planning/film-beats-v3.json')
    # Existing speech already explains attack turns and the Stalfos example.
    # Keep every approved sample/word boundary; make those claims visible.
    for para in plan['paragraphs']:
        if para['id'] == 'p001':
            para['beats'][0]['sourceStartSeconds'] = 224.0
        elif para['id'] == 'p003':
            old = para['beats'][0]
            para['beats'] = [dict(firstClauseIndex=0, kind='live', source=pin(show),
                                 sourceStartSeconds=1.4, sourceSpeed=1, sourceAudio='none',
                                 label='교토 닌자 공연 · 2022년 참고 영상',
                                 rightsStatus='private-review-only-unconfirmed-reuse'),
                             dict(old, firstClauseIndex=2)]
        elif para['id'] == 'p005':
            first = para['beats'][0]
            para['beats'] = [dict(first, sourceStartSeconds=203.0,
                                 annotation='two-stalfos-waiting'),
                             dict(first, firstClauseIndex=3, sourceStartSeconds=216.65,
                                  annotation='next-stalfos-target')]
    plan.update(schemaVersion=4, requestedRevision='ninja-live-footage-and-visible-attack-turns',
                previousPlan=pin(P / 'planning/film-beats-v3.json'),
                audioAndCaptionTimingUnchanged=True,
                showFootageIsLaterIllustrationNotHistoricalVisit=True,
                liveShowReusePermissionVerified=False, publishingApproved=False,
                deliveryClass='private-local-revision-preview')
    planpath = P / 'planning/film-beats-user-revision-v4.json'
    save(planpath, plan)
    save(request, dict(
        requestedAtKst=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
        userRequest='젤다 락온 영상에 실제 교토 닌자영상과 한 적을 주목할 때 다른 적이 공격 차례를 기다리는 현상을 추가',
        selectedProject=P.name, previousDeliveredManifest=pin(baseline),
        previousBundle=pin(M / P.name / 'final-review-v1/bundle.json'),
        otherElevenPreserved=original['projects'][1:],
        plan=pin(planpath), captionTiming=pin(P / 'production/caption-timing-v3.json'),
        reviewedAudioMix=pin(M / P.name / 'audio-mix-v3/audio-build.json'),
        sourceOrderRetained=True, approvedNarrationPcmUnchanged=True,
        noTtsOrAsrRerunNeeded=True,
        primaryReference='https://www.nintendo.com/en-gb/Iwata-Asks/Iwata-Asks-The-Legend-of-Zelda-Ocarina-of-Time-3D/Vol-2-Original-Development-Staff-Part-1/3-Let-s-Go-to-Toei-Kyoto-Studio-Park-/3-Let-s-Go-to-Toei-Kyoto-Studio-Park--231680.html',
        primaryClaimScope='The cited two-Stalfos example and coordinated attack participation; not universal immunity while holding lock-on.',
        observedGameRanges=[dict(start=203.0,end=209.28,meaning='Targeted enemy attacks while the other is visible waiting early in the range'),
                            dict(start=216.65,end=219.89,meaning='Defeat, camera/target transfer, next enemy'),
                            dict(start=224.0,end=228.48,meaning='Separate opening target-facing fight; no replay of the waiting example')],
        actualLiveShow=dict(source=pin(show), metadata=pin(R/'WwAVDIVpuS8-metadata-v1.json'),
                           url=metadata['webpage_url'], uploader=metadata['uploader'],
                           uploadDate=metadata['upload_date'], size=[1920,1080],
                           sourceRole='later-live-show-context-not-1990s-recording',
                           selectedSourceRange=[1.4,5.44], reusePermissionVerified=False,
                           publishingApproved=False, localPreviewOnly=True),
        sourceScreenReviews=[pin(R/'WwAV-contact-v1.jpg'),pin(R/'oot-turns-A-contact-v1.jpg'),pin(R/'oot-turns-B-contact-v1.jpg')],
        excludedCandidates=['pWEBHz-30t4 and 7-qA81fF8as are mechanical ninja figures, not a human show.',
                            'gKWS_V75gUc is a samurai demonstration, not the requested ninja performance.',
                            'Ninja-Do material is from Osaka, not the Kyoto venue.'],
        rightsDecision='The located human Kyoto show has no verified reuse grant. This revision is a private local preview only; no public/publish-ready adoption, upload or rights approval is asserted.',
        humanApproval=False, platformActions=[]))
    spec = importlib.util.spec_from_file_location('revision_own_scope_splice', H/'finalize-cpu-preparation-v1.py')
    sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
    for name in ['video-production-control.json', 'video-worklist.json']:
        path = ROOT/'shared/publishing'/name
        before = path.read_bytes(); text = before.decode('utf-8-sig'); data = json.loads(text)
        own = data[KEY]
        own.update(status='selected-lockon-user-revision-local-preview',
                   automaticAdvanceWithinExactList=True,
                   currentSelectedProject='projects/'+P.name+'/project.json',
                   activeRevisionScope=[P.name],
                   automaticAdvanceOutsideRevisionScope=False,
                   revisionSource=pin(request), intermediateApprovalRequired=False)
        new = sp.replace_value(text, KEY, own)
        assert path.read_bytes() == before
        path.write_bytes((b'\xef\xbb\xbf' if before.startswith(b'\xef\xbb\xbf') else b'') + new.encode('utf8'))
    print(json.dumps(dict(sourceReview=pin(request), plan=pin(planpath), scope=[P.name],
                          deliveryClass='private-local-preview', publishingApproved=False)))


if __name__ == '__main__':
    main()
