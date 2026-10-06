"""Record observed private delivery; never uploads, renders, resumes or starts a queue item."""
from final_cpu_common import ROOT, BASE, FINAL, PROOF, read, write, sha, now

pub = ROOT / 'projects/familiar-game-rules/publishing'
u = read(pub / 'youtube-upload.json')
observation = read(pub / 'proof/final-observations-v1.json')
assert observation['videoId'] == u['videoId'] == 'NLEHMC0XMtg'
assert observation['privateSaved'] and observation['uploadComplete']
assert observation['burnedGameWithCcOff'] and observation['burnedWhiteWithCcOff']
assert observation['koManualPublished'] and observation['enManualPublished']
assert observation['englishMetadataReopened'] and observation['cardZeroReopened']
assert observation['endThreeReopened'] and observation['noSchedule']
qa = read(FINAL / 'QA.json')
assert qa['technicalReviewApproved'] and qa['allFinalPixelsDirectlyReviewed']
assert qa['all38MixedSpeechWindowsDirectlyCompared']
images = [
    ('thumbnail.png', 'delivery-thumbnail', 'One directly reviewed prepared final thumbnail for the single current video; platform daily limit remains pending.'),
    ('proof/private-saved-v1.png', 'minimal-publishing-proof', 'One actual saved private/no-schedule Studio proof for NLEHMC0XMtg, including uploaded captioned filename and current processing state.'),
    ('proof/end-screen-saved-v1.png', 'minimal-publishing-proof', 'One reopened saved final-screen proof of the playlist, own-channel subscription and canonical coaching link, preserving the original twelve member identities.'),
    ('proof/watch-game-cc-off-v1.png', 'minimal-publishing-proof', 'One actual uploaded gameplay frame demonstrating burned fixed-bottom Korean captions while player CC is off.'),
    ('proof/watch-white-cc-off-v1.png', 'minimal-publishing-proof', 'One actual uploaded white explanation frame demonstrating burned fixed-bottom Korean captions while player CC is off.'),
]
registry_path = ROOT / 'shared/git-essential-images.json'
registry = read(registry_path)
new_entries = []
for name, purpose, reason in images:
    p = pub / name
    assert p.is_file()
    entry = dict(path=p.relative_to(ROOT).as_posix(), purpose=purpose, reason=reason,
                 sha256=sha(p), reviewedAt=observation['observedAt'], project='familiar-game-rules')
    new_entries.append(entry)
paths = {e['path'] for e in new_entries}
registry['entries'] = [e for e in registry['entries'] if e['path'] not in paths] + new_entries
write(registry_path, registry)
ignore_path = ROOT / '.gitignore'
ignore = ignore_path.read_text(encoding='utf-8')
for entry in new_entries:
    line = '!' + entry['path']
    if line not in ignore.splitlines():
        ignore = ignore.rstrip() + '\n' + line + '\n'
ignore_path.write_text(ignore, encoding='utf-8')
write(FINAL / 'essential-delivery-images-v1.json', dict(reviewedAt=now(), entries=new_entries,
    count=5, newQaImages=0, newVideoAudioArchives=0, allOtherRastersLocalOnly=True))

stop = dict(slug='familiar-game-rules', userEvidence='논문 실험 먼저 진행해야 해서 이것까지만 완료되면 일단 정지해줘~',
            policy='Current video only; keep automation24 PAUSED, no next queued production or GPU TTS. Preserve paper experiments and GPU_TTS_HOLD.',
            status='current-private-delivery-complete-git-pending', nextQueuedStarted=False)
u.update(status='private-saved-verified-thumbnail-followup', uploaded=True, privateSaved=True,
         privacyStatus='private', scheduled=False, savedAt=observation['observedAt'],
         videoUrl='https://youtu.be/NLEHMC0XMtg', fullSettingsVerified=False, thumbnailSaved=False,
         availableSettingsVerified=True, verification=observation, stopAfterCurrent=stop,
         explicitWizardCompletionObserved=observation['explicitWizardCompletionObserved'])
for subtitle in u['subtitles']:
    subtitle.update(status='manual-published-verified', savedAndReopened=True)
u['englishMetadata'].update(status='published-reopened-verified')
u['coachingCard'].update(status='saved-reopened-verified')
u['endScreen'].update(status='saved-reopened-verified', studioStart='6:22:25', studioEnd='6:32:25',
                      playlistName='Planning & Game Design & Tech', ownChannelId='UCOgtkPoyC0VXhCs7Xk3jvjQ',
                      memberIdentitiesUnobscured=True)
u['coachingEndingLink'].update(status='saved-reopened-verified')
u['burnedCaptionVerification'].update(status='actual-uploaded-game-and-white-cc-off-verified',
                                    playerQuality=observation['playerQuality'])
u['monetization'] = observation['monetization']
u['automaticChecks'] = observation['automaticChecks']
write(pub / 'youtube-upload.json', u)

project_path = ROOT / 'projects/familiar-game-rules/project.json'
project = read(project_path)
project.update(status='private-delivered-awaiting-human-review-thumbnail-followup', publishReady=False, stopAfterCurrent=stop)
project['publishing'].update(receipt='projects/familiar-game-rules/publishing/youtube-upload.json',
                             videoId=u['videoId'], privateSaved=True, scheduled=False,
                             availableSettingsVerified=True, fullSettingsVerified=False, thumbnailSaved=False)
write(project_path, project)
qpath = PROOF.parent / 'queue.json'
queue = read(qpath)
item = next(i for i in queue['items'] if i['slug'] == 'familiar-game-rules')
item.update(status='uploaded-private-awaiting-user-review', stage='private-delivery-verified-selective-git-pending',
            updatedAt=now(), uploaded=True, privateSaved=True, videoId=u['videoId'], rendered=True, collected=True,
            qaComplete=True, fullSettingsVerified=False, thumbnailSaved=False, availableSettingsVerified=True,
            publishing='projects/familiar-game-rules/publishing/youtube-upload.json',
            publishingFollowups=u['publishingFollowups'], allFinalCaptionPixelsReviewed=True, stopAfterCurrent=stop,
            nextAction='Selectively commit/push current reviewed records, verify actual remote SHA, then remain paused; no next item.')
item['checkpoints'].update(script=True, narration=True, footage=True, scenes=True, mix=True, render=True,
                           qa=True, collected=True, privateUploadSaved=True, publishingSettingsVerified=False,
                           gitDelivery=False)
item['execution'].update(alive=False, cpuProductionJobs=0, gpuSynthesisJobs=0, uploads=0,
                         status='completed', nextTask='Selective Git delivery then pause')
queue.update(status='paused-after-current-git-pending', updatedAt=now(), lastProgressAt=now(),
             currentSlug='familiar-game-rules', stopAfterCurrent=stop)
queue['automation'].update(status='PAUSED', intervalMinutes=30, observedAt=now(),
    actualConfig='C:/Users/eazuo/.codex/automations/24/automation.toml',
    checkpointPromptVerified='Actual automation24 is PAUSED; finish only current local delivery and do not resume.')
queue['progress'].update(rendered=13, collected=13, uploaded=13, productionRendered=13,
    productionCollected=13, privateSaved=13, productionDelivered=13, publishingFollowups=1,
    fullSettingsDelivered=12, remainingProduction=10, remaining=10, inProgress=0, queued=10)
queue['publishingFollowups'] = [f for f in queue.get('publishingFollowups', []) if f.get('videoId') != u['videoId']] + u['publishingFollowups']
write(qpath, queue)
for p in [BASE/'latest-checkpoint.json', PROOF/'latest-checkpoint.json']:
    cp = read(p)
    cp.update({k: item[k] for k in ['status', 'stage', 'updatedAt', 'uploaded', 'privateSaved', 'videoId',
                                  'fullSettingsVerified', 'thumbnailSaved', 'availableSettingsVerified',
                                  'publishing', 'publishingFollowups', 'stopAfterCurrent', 'nextAction', 'execution']})
    write(p, cp)
mc_path = ROOT / 'motion-canvas/projects.json'
mc = read(mc_path)
for entry in ['./src/projects/familiar-game-rules/project.ts', './src/projects/familiar-game-rules/timed-white-reel-project-v1.ts']:
    if entry not in mc:
        mc.append(entry)
write(mc_path, mc)
print('Actual current private delivery recorded; thumbnail/human review pending, automation paused, next queued untouched.')
