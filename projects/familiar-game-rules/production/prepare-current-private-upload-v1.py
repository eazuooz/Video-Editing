"""Prepare current reviewed delivery; performs no external upload."""
from final_cpu_common import ROOT, FINAL, PROOF, read, write, sha, now, STOP, update_checkpoint
from pathlib import Path
import subprocess

note = read(FINAL/'current-input-change-before-private-v1.json')
for row in note['changed']:
    assert sha(ROOT/row['path']) == row['sha256'], 'Foreign input changed again: reread it before updating review'
note.update(directContentReview=True, reviewedAt=now(),
    review='Both changed files were read in full: lines/bounds manifest and actual avLKKfQBV_U upload-in-progress receipt including KO/EN text. Parametric/implicit lines, circle/sphere, AABB broad phase and affine transformed bounds concern geometry calculations. Current familiar-controls question concerns remapping, device capabilities, simultaneous actions, prompts and target choices; distinct. Foreign scripts unchanged since full review. Foreign pending end screen/checks/pixels remain pending; 40:60/no-BGM exception not copied.',
    currentStudio={'query':'익숙한 게임 조작','actualVisibleResult':'동영상(0)','observedAt':now(),'tabId':'61','url':'https://studio.youtube.com/channel/UCOgtkPoyC0VXhCs7Xk3jvjQ'},
    foreignFilesModified=False)
write(FINAL/'current-input-change-before-private-v1.json',note)
report = read(ROOT/'production/batches/sakurai-planning-game-design/preflight/familiar-game-rules.json')
reason = report['contentReview'] + ' 최신 기하 직선/경계상자 manifest와 avLKKfQBV_U 실제 진행 receipt 한영본문 두 변경파일을 전체 직접 읽었다. 대본 변경은 없으며 선/구/AABB 계산은 조작약속·재배치·장치기능 질문과 구별된다. 현재 Studio 익숙한 게임 조작 검색 동영상(0)을 실제 확인했다. 상세 근거: projects/familiar-game-rules/production/final-v1/current-input-change-before-private-v1.json.'
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','familiar-game-rules','--decision','distinct','--reason',reason,'--studio-evidence',report['studioEvidence']],cwd=ROOT,check=True)
subprocess.run([node,'scripts/review-video-duplicates.cjs','familiar-game-rules','--check'],cwd=ROOT,check=True)
pub = ROOT/'projects/familiar-game-rules/publishing'
receipt = pub/'youtube-upload.json'
assert not receipt.exists(), 'Preserve existing actual upload receipt'
p=read(pub/'publishing-prepared-v1.json');d=read(ROOT/'projects/familiar-game-rules/production/delivery-output.json');qa=read(FINAL/'QA.json')
files={f['name']:f for f in d['files']};cap=files['familiar-game-rules.captioned.mp4']
assert cap['sha256']=='560ce85b9c2dd063c3a28be1955ad01f8c49ff8208ef126184f4b5cc89fd9e4d'
upload=dict(schemaVersion=1,preparedAt=now(),status='prepared-only-not-uploaded',videoId=None,actualVideoId=None,uploaded=False,scheduled=False,
    video=dict(path='output/familiar-game-rules/'+cap['name'],bytes=cap['bytes'],sha256=cap['sha256'],seconds=p['seconds'],frames=p['frames']),
    metadata=dict(title=p['metadata']['title'],description=p['metadata']['descriptionBody'],privacyStatus='private',language='ko'),
    englishMetadata=dict(title=p['englishMetadata']['title'],description=p['englishMetadata']['descriptionBody']),
    descriptionBody=dict(ko=p['metadata']['descriptionBody'],en=p['englishMetadata']['descriptionBody']),
    subtitles=[],thumbnail=dict(path='projects/familiar-game-rules/publishing/thumbnail.png',sha256=sha(pub/'thumbnail.png'),status='prepared-not-saved'),
    thumbnailSaved=False,fullSettingsVerified=False,qa='projects/familiar-game-rules/production/final-v1/QA.json',delivery='projects/familiar-game-rules/production/delivery-output.json',
    pendingHumanReview=d['notices'][1:],stopAfterCurrent=STOP,chapters=p['chapters'])
for language,count in [('ko',253),('en',118)]:
    f=files['familiar-game-rules.'+language+'.srt'];upload['subtitles'].append(dict(language=language,path='output/familiar-game-rules/'+f['name'],bytes=f['bytes'],sha256=f['sha256'],cues=count,status='pending'))
write(receipt,upload)
subprocess.run([node,'scripts/prepare-youtube-upload.cjs','familiar-game-rules'],cwd=ROOT,check=True)
update_checkpoint('current-four-files-collected-private-upload-prepared','Upload current captioned delivery once privately; verify settings/pixels, selectively push and pause24. No next queued item.',collected=True,deliveryOutput='projects/familiar-game-rules/production/delivery-output.json',uploaded=False,privateSaved=False)
