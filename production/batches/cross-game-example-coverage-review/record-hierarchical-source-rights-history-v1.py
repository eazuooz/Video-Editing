"""Record primary-source permission context and bounded local recent-use findings."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=V/'source-primary-rights-and-recent-use-v1.json'
assert not out.exists()
source_v1=read(V/'source-acquisition-execution-v1.json')
source_v2=read(V/'source-research-v2/metadata-observation-v1.json')
stamp=datetime.now(timezone.utc).isoformat()
record=dict(recordedAt=stamp,scope='Source planning; permission context does not approve all final public rights, people, music, pronunciation or continuous pixels.',
    originalRetainedSource=dict(videoId='I-ccSZ5J1Bo',game='Two Point Museum',channel='Two Point Studios',
        preservedExactSource=True,redownloaded=False,baselineRightsRecordReused=True),
    officialCandidateSources=[dict(videoId=s['videoId'],game=s['game'],title=s['title'],
        localMediaPath=s['localMediaPath'],sha256=s['fileSha256'],wholeVideoDecodePassed=s['wholeDecode']['actualExitCode']==0,
        actionSelectionApproved=False) for s in source_v1['results']],
    additionalOfficialCandidate=dict(**source_v2['sources'][0],acquisitionState='source-acquisition-execution-v2.json',
        acquisitionStateIsAuthoritative=True),
    primaryPermissionObservations=[
        dict(url='https://www.hoodedhorse.com/influencers',observedAt=stamp,
            publisher='Hooded Horse',summary='Publisher FAQ permits monetized game videos, membership distribution, streaming and clipped videos/highlights; embargo rules remain applicable.',
            appliesToGames=['Manor Lords','Against the Storm'],
            officialRecordingOwnerBasis=['Hooded Horse official gameplay preview','Eremite Games official developer stream'],
            unrelatedCreatorRecordingPermissionInferred=False,sourceAudioAdopted=False,peopleRightsApproved=False),
        dict(url='https://www.moddb.com/games/timberborn/presskit',observedAt=stamp,
            author='Mechanistry sp. z o.o developer presskit linked to official timberborn.mechanistry.com',
            summary='Developer permits commercial and noncommercial video broadcasts containing Timberborn content/assets, including monetization.',
            thirdPartyUploaderPermissionInferred=False,sourceAudioAdopted=False,peopleRightsApproved=False),
        dict(url='https://mechanistry.com/press',observedAt=stamp,
            summary='Official press/content-creator page links the Timberborn press kit with screenshots, GIFs and videos. Its release chronology now includes1.1 September2026, so March2026 source controls are described as1.0-source observations, not verified current1.1 controls.',
            generalUnlimitedLicenceInferred=False)
    ],recentUseReview=dict(actualRgSession=82285,initialChunk='c571ee',completionChunk='e47bff',actualExitCode=0,
        roots=['projects','shared/publishing','production/batches'],extensions=['json','md'],
        patterns=['Manor Lords','Timberborn','Against the Storm','gVkhhrLARU8','Jsc7003gSu0','qaK2FWQB7DE','6TNjosDftog'],
        omitted=['info.json','inventory','duplicate','queue/session/resource observation records'],
        finding='Matches were the existing hierarchical-game-outlines research/source/candidate/history files, relevant Sakurai batch README and the newly owned metadata records. No adoption in another game project was found in this bounded search.',
        exhaustiveRemoteHistoryClaimed=False,baselineMuseumPriorUsePreserved=True),
    rejectedOrHeld=[
        dict(id='5rgASbqkeTI',reason='Previously inspected official1.0 launch trailer; edit lacks a complete selected input/result chain. Completed acquisition/pixels not repeated.'),
        dict(id='MtA1BAeeOAE',reason='Same launch content as the held trailer; not a new independent game or clearer cut.'),
        dict(id='Jsc7003gSu0',reason='All54native samples/9boards and normal1x source reviewed. Promotional edits omit configuration UI and mix fast weather/water transitions. Held; no actual-time allocation.'),
        dict(id='qaK2FWQB7DE',scope='Old browser-only coarse checkpoints123/1377/2295/3673seconds',reason='Historical coarse checkpoints held. This source was acquired only once now; new315..685 and2880..3490 native windows were independently read, with debugger/pause/static exclusions.'),
        dict(id='GDWC third-party Timberborn clip',reason='Unrelated recorder permission not established; not adopted.')
    ],newGameMinimumApproved=False,humanPublicRightsApproved=False,allPeopleRightsApproved=False,
    sourceAudioForFinal=False,sourceMusicForFinal=False,unrelatedFootageForQuota=False,
    next='Select precise normal-speed visible actions from the reviewed official sources. Preserve version/camera/UI limitations, then write matching causal KOEN additions and editable tracking. Current full4game/narration/final approval remains false.')
for sub in ['source-research-v1/metadata-observation-v1.json','source-research-v2/metadata-observation-v1.json','native-candidate-direct-review-v2.json']:
    p=V/sub;record.setdefault('boundLocalEvidence',[]).append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(path=out.relative_to(ROOT).as_posix(),primaryPermissionPages=3,sourceAudioAdopted=False,
    publicRightsApproved=False,acquisitionNewSourceOnly='6TNjosDftog')))
