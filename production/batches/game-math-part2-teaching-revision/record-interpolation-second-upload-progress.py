"""Record observed transfer progress without claiming delivery or processing QA."""
from pathlib import Path
import json, datetime
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-math-rotation-conversions-v2'
path=P/'publishing/youtube-upload.json'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
d=read(path)
assert d['videoId'] in [None,'n-k7zwaSum0']
d.update(videoId='n-k7zwaSum0',url='https://youtu.be/n-k7zwaSum0',status='actual private draft saved; transfer and processing pending',privateUploadComplete=False)
new=['Overview: numbers for the same orientation','Conventions before the conversion graph','Length and atan2 with small numbers','Euler angles and matrices: a round trip','Build matrix axes from a quaternion','Different numbers for the same body orientation','Protect division when extracting rotation','Recover a quaternion at a half turn','Connect Euler angles and quaternions','Recover axis and angle at zero and a half turn','Check an intermediate orientation and a round trip','Rotate and reverse the same vector','Conventions and verification','From rotation to lines and bounds','Membership thanks and programming coaching']
assert len(new)==len(d['chapters'])
for c,title in zip(d['chapters'],new):
    n=int(c['startSeconds']);stamp=f'{n//60:02}:{n%60:02}'
    for target in [d['englishMetadata'],d['descriptionBody']]:
        key='description' if 'description' in target else 'en'
        target[key]=target[key].replace(stamp+' '+c['en'],stamp+' '+title)
    c['en']=title
d['coachingCard'].update(status='saved-in-Studio; reopen verification pending',startSeconds=0,title='프로그래밍 과외',teaser='프로그래밍 과외',originalCatIdentityUsed=True)
d['endScreen'].update(status='saved-in-Studio; reopen verification pending',observedStart='13:51:02',observedEnd='14:01:02',platformTimebase='30fps display',memberProfilesNamesBadgesClear=True,originalThankYouTitleClear=True,printedCoachingUrlClear=True,layoutProof='shared/output/game-math-part2-teaching-revision/interpolation/second-endscreen-layout.png')
d['coachingEndingLink']['status']='saved-in-Studio; reopen verification pending'
d['subtitles'][0]['status']='manual-timed-file-saved-in-upload-dialog; language-row verification pending'
d['transferAndProcessing']='Observed uploading 86%; do not duplicate upload or infer HD/check completion.'
d['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
write(path,d)
m=read(P/'project.json');m['publishing'].update(actualVideoId=d['videoId'],privateUploadComplete=False);write(P/'project.json',m)
print('Actual private draft ID retained; pending checks preserved; English chapter labels corrected to their scene topics.')
