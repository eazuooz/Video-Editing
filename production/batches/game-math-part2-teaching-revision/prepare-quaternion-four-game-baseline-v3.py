"""Freeze both delivered quaternion episodes before additive cross-game work.

Does not change completed projects, schedule entries, foreign jobs or media.
"""
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).parent
REVIEW = BATCH/'cross-game-review-20261011/quaternion-four-game-v3'
REVIEW.mkdir(parents=True,exist_ok=True)

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

target=REVIEW/'baseline.json'
if target.exists():
    print('Existing preservation snapshot retained; no baseline overwrite')
    raise SystemExit(0)
entries=[]
for slug in ['game-math-quaternion-foundations-v2','game-math-quaternion-calculations-v2']:
    project=ROOT/'projects'/slug
    manifest=read(project/'project.json')
    ko=read(project/'script/narration.ko.json')
    en=read(project/'script/narration.en.json')
    timeline=read(project/'production/timeline.json')
    assert [s['id'] for s in ko['scenes']]==[s['id'] for s in en['scenes']]==[s['id'] for s in timeline['scenes']]
    files=[]
    for rel in ['project.json','script/narration.ko.json','script/narration.en.json','script/final.ko.srt','script/final.en.srt',
                'production/lesson.json','production/timeline.json','production/qa.json','production/current-pixel-review.json',
                'publishing/youtube-upload.json','sources/gameplay-cuts.json']:
        source=project/rel
        if not source.exists():continue
        destination=REVIEW/'baseline'/slug/rel
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,destination)
        files.append({'path':source.relative_to(ROOT).as_posix(),'sha256':sha(source),'snapshot':destination.relative_to(ROOT).as_posix()})
    media=[]
    for key in ['narration','videoClean','videoBurnedCaptions']:
        source=ROOT/manifest['paths'][key]
        assert source.exists(),source
        media.append({'kind':key,'path':source.relative_to(ROOT).as_posix(),'bytes':source.stat().st_size,'sha256':sha(source),'copied':False})
    slots=[]
    for s in timeline['scenes']:
        source=ROOT/'shared/output'/slug/'clips'/f"{s['id']}.mp4"
        assert source.exists(),source
        slots.append({'id':s['id'],'frames':s['frames'],'seconds':s['seconds'],'voiceSha256':s.get('voiceSha256'),
                      'preservedSamplesSha256':s.get('preservedSamplesSha256'),'clip':source.relative_to(ROOT).as_posix(),'clipSha256':sha(source)})
    receipt=read(project/'publishing/youtube-upload.json')
    entries.append({'slug':slug,'newSlug':slug[:-2]+'v3','sceneIds':[s['id'] for s in ko['scenes']],
                    'completeApprovedSceneDictionariesRetained':True,'files':files,'media':media,'sceneClips':slots,
                    'actualVideoId':receipt['videoId'],'scheduledAt':receipt.get('scheduledAt'),
                    'durationSeconds':manifest['video']['durationSeconds'],'baselineDistinctGames':['Riders Republic'],
                    'revisionReason':'One game cannot demonstrate transfer across character, build-object and vehicle contexts.',
                    'sourceAndFinalReview':'pending new candidate playback; existing delivery evidence retained'})
record={'recordedAt':datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),'baselineProjectsChanged':False,
        'preserveAllApprovedKOENSceneDictionariesOrderPCMAndClips':True,'ratio':{'actual':.4,'explanation':.6},
        'audio':'narration-only; no BGM or source sound','palette':'preserve already-started white Manim',
        'gamesPerIndependentEpisode':4,'humanWholeListening':'pending','gameIPReview':'pending','episodes':entries,
        'candidates':['Trailmakers','Space Engineers','Tiny Glade'],
        'candidateNamesAreNotAdoption':True,'candidateIntervalsMustBePlayedComparedAndAnnotatedBeforeTTS':True,
        'approximateEpisodeLength':'retain two complete conceptual episodes; refine additions after measured narration',
        'newTtsStarted':False,'newRenderStarted':False,'newUploadsStarted':False,'fullTaskComplete':False}
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
queue=read(BATCH/'queue.json')
queue.setdefault('execution',{}).update({'currentSlug':'game-math-quaternion-operations',
    'stage':'quaternion-four-game-v3-baseline-preserved-and-source-candidates-being-compared',
    'fourGameBaseline':target.relative_to(ROOT).as_posix(),'fullTaskComplete':False})
(BATCH/'queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'preservedEpisodeSceneCounts':[len(e['sceneIds']) for e in entries],
                  'actualVideoIds':[e['actualVideoId'] for e in entries],'newTtsStarted':False},ensure_ascii=False))
