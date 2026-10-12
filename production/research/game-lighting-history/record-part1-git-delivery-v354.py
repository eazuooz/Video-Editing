"""Persist only an already observed normal push; never predict this file's commit."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess

ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'production/research/game-lighting-history';Q=ROOT/'projects/game-lighting-history-04-1'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,j): p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
v=read(R/'part1-selective-git-verification-v353.json')
assert v['actualVideoId']=='YOsG939kaBw' and v['remoteMatches'] and v['normalPush'] and v['pushExitCode']==0
assert v['externalIndexByteIdentical'] and v['externalEntriesIdentical'] and v['allCommittedBlobsVerified']
assert v['mediaAdded']==0 and len(v['imagesAdded'])==2
assert git('rev-parse','HEAD')==v['commit']
assert git('ls-remote','origin','refs/heads/main').split()[0]==v['commit']
now=datetime.now(timezone.utc).isoformat()
delivery={'status':'verified-normal-push','commit':v['commit'],'remoteSha':v['remoteSha'],'verifiedAt':v['verifiedAt'],'verification':'production/research/game-lighting-history/part1-selective-git-verification-v353.json','externalIndexByteIdentical':True,'mediaAdded':0,'essentialImagesAdded':2,'evidencePersistence':'Actual completed production push; following evidence commit is not predicted.'}
p=Q/'publishing/youtube-upload.json';receipt=read(p)
assert receipt['privateSaved'] and receipt['fullSettingsVerified'] and receipt['checksPassed']
receipt['gitDelivery']=delivery;receipt['verifiedAt']=now
save(p,receipt)
p=Q/'project.json';j=read(p);j['status']='reviewed-private-and-git-delivered';j['publishReady']=False
j['publishing']['gitDelivery']=delivery;save(p,j)
p=R/'part1-private-observations-v350.json';j=read(p);j['gitDelivery']=delivery
j['nextAction']='Resume unfinished rendering-history checkpoints: 04-2 candidate selection and production, 01/02 final production, and03 current four-game teaching audit. Preserve completed04-1/04-3, their media/receipts, unrelated research and staged changes. Entire series remains unfinished.'
save(p,j)
(Q/'README.md').write_text('# Game rendering history 04-1\n\nActual private video: https://youtu.be/YOsG939kaBw\n\nReviewed delivery: 1,485.8 seconds, 89,148 frames at 1080p60. The body retains 53,057 actual-footage and 35,371 explanation frames (60:40, 0.2-frame rounding), 77 full narration paragraphs, 335 Korean and 409 English cues. Current pair345 and QA347 supersede historical candidates. Two complete decodes passed; PTS are continuous and both masters carry identical AAC.\n\nBlack projected 2.5D explanations connect Horizon Forbidden West, The Outer Worlds2, Cyberpunk2077 and Fortnite. The original branding and 12-row, 10-second member ending remain. Uploaded1080p game/PPT captions were directly inspected with CC off. Illustrated thumbnail, manual KO/EN subtitles, English metadata, coaching card and three end-screen elements were saved and reopened. Automatic ad checking completed with monetization enabled; no copyright claims were observed.\n\nReviewed metadata/code, the necessary thumbnail and one minimal publishing screenshot were normally pushed at `'+v['commit']+'`; the actual remote SHA matched. External Git index bytes/entries stayed unchanged. Raw source media, audio, extracted frames and repeated QA screenshots remain local. The shared global rebuild-index write was locked; the own rebuilt manifest and exact scoped `node scripts/build-rebuild-manifests.cjs game-lighting-history-04-1 --check` passed.\n\nPrivate and unscheduled while earlier series episodes remain unfinished. Whole human listening/pronunciation, final public rights, original Nimbus verification, truncated original member handles, external backup, optional playerCC propagation, dubbing and private-comment posting remain pending. This record does not complete or publicly approve the whole series.\n',encoding='utf-8')
p=R/'checkpoint.json';c=read(p)
c['episode04Part1GitV353']=delivery;c['episode04Part1PrivateObservedV350']=j
c['episode04Part1LatestReality']={'updatedAt':now,**j}
c['ownedActiveWork']={'status':'no-active-owned-media-worker','next':j['nextAction']}
c['nextAction']=j['nextAction'];c['updatedAt']=now;save(p,c)
print(json.dumps({'actualVideoId':'YOsG939kaBw','productionCommit':v['commit'],'remoteMatches':True,'wholeSeriesComplete':False,'next':j['nextAction']},ensure_ascii=False,indent=2))
