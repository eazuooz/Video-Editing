"""Register the user's finite 111-film selection without starting platform/GPU jobs."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
BATCH_ID = HERE.name
AUTH_KEY = 'explicitArchitectural111Batch20261106'
EVIDENCE = '111개 전체 제작 들어가줘'

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    temp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    temp.write_text(data, encoding='utf-8')
    os.replace(temp, path)

def add_shared(path, key, value):
    # Preserve concurrent unrelated updates. A changing file must be retried by the caller.
    path = ROOT / path
    before = path.read_bytes()
    obj = json.loads(before.decode('utf-8-sig'))
    if key in obj:
        if obj[key].get('batch') != value.get('batch'):
            raise RuntimeError('Conflicting existing batch authorization')
        return
    obj[key] = value
    if path.read_bytes() != before:
        raise RuntimeError('Concurrent shared-file edit; retry initialization')
    save(path, obj)

def main():
    spec = importlib.util.spec_from_file_location('level_catalog', ROOT/'production/research/architectural-level-design/build_catalog.py')
    cat = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cat)
    rows = cat.load()
    assert len(rows) == len({r['id'] for r in rows}) == 111
    ordered = sorted(rows, key=lambda r: (r['rank'] is None, r['rank'] or 0, r['ch'], r['first']))
    now = datetime.now().astimezone().isoformat()
    catalog_hash = hashlib.sha256((ROOT/'production/research/architectural-level-design/topics.txt').read_bytes()).hexdigest()
    batch_path = f'production/batches/{BATCH_ID}/batch.json'
    items = []
    for order, r in enumerate(ordered, 1):
        slug = 'shorts-leveldesign-' + r['id'].replace('.', '-')
        project_dir = ROOT/'projects'/slug
        item = dict(order=order, topicId=r['id'], slug=slug, title=r['hook'], chapter=r['ch'],
                    chapterName=cat.CHAPTERS[r['ch']], printPages=r['span'], pdfPages=[r['first'],r['last']],
                    project=f'projects/{slug}/project.json', status='preproduction-in-progress' if order == 1 else 'script-preparation',
                    productionComplete=False, humanApproval=False, platformStatus='not-uploaded')
        items.append(item)
        if not (project_dir/'project.json').exists():
            save(project_dir/'project.json', dict(schemaVersion=1, slug=slug, batchId=BATCH_ID,
                authorizationKey=AUTH_KEY, topicId=r['id'], batchOrder=order, title=r['hook']+' #게임개발 #레벨디자인',
                type='short', format=dict(width=1080,height=1920,fps=60, duration='concept-sized; no fixed ceiling'),
                formatStatus='provisional-all-shorts; optional format preference pending', mediaRoot=(MEDIA/slug).as_posix(),
                source=dict(kind='user-supplied-book',path=cat.BOOK.as_posix(),printPages=r['span'],
                            pdfPages=[r['first'],r['last']],sha256='0278712f4c11636f0605f4c73c7600bcc7f17c90d3c23b9c2e910cd6617df3be'),
                concept=r['principle'], proposedDemonstration=r['demo'], previousOverlapNote=r['overlap'],
                rendererPolicy='Unity for spatial/game-state explanation; Motion Canvas labels and diagram overlays; Manim if derivation needs it',
                outputContract=['clean.mp4','captioned.mp4','ko.srt','en.srt'],
                status=item['status'], localFinalReviewOnly=True, youtubeAuthorized=False, driveAuthorized=False,
                scriptSourceVerification='pending-full-script-and-visual-audit', footageSelection='pending-independent-FHD-source-review'))
        if not (project_dir/'checkpoint.json').exists():
            save(project_dir/'checkpoint.json', dict(schemaVersion=1,updatedAt=now,batchId=BATCH_ID,topicId=r['id'],
                stage=item['status'],completedStages=[],resourceGate='respect shared cooperative GPU lease; no overlapping expensive jobs',
                sourceMappingStatus='draft-in-parallel',footageVerified=False,voiceGenerated=False,
                editableUnityScenesSaved=[],finalOutputsVerified=False,humanReview='not-delivered',platformActions=[]))
    if not (HERE/'batch.json').exists():
        save(HERE/'batch.json', dict(schemaVersion=1,batchId=BATCH_ID,authorizationId=AUTH_KEY,recordedAt=now,
            userEvidence=EVIDENCE,scope='Exactly all 111 topics of the delivered architectural level-design catalog',
            fullProductionAuthorized=True,finiteBatch=True,automaticAdvanceWithinExactList=True,
            automaticAdvanceOutsideList=False,localFinalReviewOnly=True,youtubeActions=False,driveActions=False,
            schedulingActions=False,deletionActions=False,recurringAutomationCreated=False,
            sourceCatalog='production/research/architectural-level-design/topics.txt',sourceCatalogSHA256=catalog_hash,
            sourceBookSHA256='0278712f4c11636f0605f4c73c7600bcc7f17c90d3c23b9c2e910cd6617df3be',
            mediaRoot=MEDIA.as_posix(),productionOrderBasis='Five recommended visual topics first, then remaining topics in book order; no duplicate topic',
            resourcePolicy='One costly production stage at a time, shared GPU lease respected, no user app termination, no unrelated queue changes',
            formatAssumption='All 111 vertical 1080x1920/60fps Shorts with concept-sized duration; optional user format answer may revise unrendered topics',
            scriptPolicy='Independently phrased, source-page-mapped KO/EN, causes and prerequisites retained; candidate footage is not verified footage',
            projects=items))
    MEDIA.mkdir(parents=True,exist_ok=True)
    if not (HERE/'checkpoint.json').exists():
        save(HERE/'checkpoint.json',dict(schemaVersion=1,batchId=BATCH_ID,updatedAt=now,
            phase='parallel-script-and-source-preparation',topicCount=111,selectedFirstTopic='03.02',
            completedLocalReviewCount=0,completedVoiceCount=0,scriptDraftCount=0,verifiedFootageCount=0,
            workers=dict(a='Chapters 0-4: 42 topics',b='Chapters 5-9: 39 topics',c='Chapters 10-14: 30 topics'),
            currentResourceConstraint='Another game-math pipeline holds shared/output/GPU_HANDOFF.json; preserve it and continue CPU work',
            ownGPUJobStarted=False,ownFiniteQueueRunning=False,recurringAutomationCreated=False,
            decisions=[dict(id='finite-111-local-production',evidence=EVIDENCE,reason='Latest explicit user request selects all 111; no platform actions inferred'),
                       dict(id='five-visual-first',reason='Start with the five concrete one-variable topics already recommended; then source order'),
                       dict(id='media-on-c',reason='C has more free disk space; preserve other files on D')],
            remainingStages=['independent source footage and rights/FHD review','source-to-script and scene audit','editable Unity scenes and capture',
                             'Qwen narration and independent ASR','timed KO/EN captions, mix and four outputs','technical/mobile/realtime QA and local human review'],
            platformActions=[]))
    pointer=dict(id=AUTH_KEY,requestedOnKst='2026-11-06',userEvidence=EVIDENCE,batch=batch_path,
        worklist=f'production/batches/{BATCH_ID}/worklist.json',checkpoint=f'production/batches/{BATCH_ID}/checkpoint.json',
        scope='Exact 111 selected topics to local final review',status='preproduction-in-progress',
        automaticAdvanceWithinExactList=True,automaticAdvanceOutsideList=False,recurringAutomation=False,
        humanFinalReviewRequired=True,youtubeAuthorized=False,driveAuthorized=False,schedulingAuthorized=False,deletionAuthorized=False)
    add_shared('shared/publishing/video-production-control.json', AUTH_KEY, pointer)
    add_shared('shared/publishing/video-worklist.json', 'architectural111Batch20261106', pointer)
    add_shared('shared/publishing/shorts-worklist.json', 'architectural111Batch20261106', pointer)
    if not (HERE/'worklist.json').exists():
        save(HERE/'worklist.json',dict(schemaVersion=1,batchId=BATCH_ID,updatedAt=now,rows=items))
    print(json.dumps(dict(topics=len(items),firstFive=[r['topicId'] for r in items[:5]],mediaRoot=MEDIA.as_posix(),
                          fullReviewOutputs=0,gpuJobsStarted=0),ensure_ascii=False))

if __name__ == '__main__':
    main()
