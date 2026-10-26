"""Initialize the six expressly selected game-design episodes, metadata only.

Preserves D22 and all unrelated control fields, worklist rows and staging.
Runtime copies derive from the validated D22 pipeline; no job runs on import.
"""
from pathlib import Path
from datetime import datetime, timezone
import ast
import json
import os
import uuid

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BATCH = HERE.name
REVISION = 'batch-v1'
ROWS = [
    ('D25', 'limited-color-world', '색이 적은 세계', 'obnjR8KJ9nk'),
    ('D26', 'computer-controlled-players', '컴퓨터가 조종하는 플레이어', 'uleauI0IwZM'),
    ('D27', 'in-game-cutscenes', '게임 안의 컷신', 'VZRh0P40RAM'),
    ('D28', 'start-with-climax', '클라이맥스부터 시작하기', 'eAd0pt-uv8g'),
    ('D29', 'kind-to-beginners', '초보자에게 친절하기', 'R7rd4-ua2AI'),
    ('D30', 'respect-player-time', '플레이어의 시간 존중', '-49L25Q0YAU'),
]


def read(p):
    return json.loads(p.read_text('utf-8-sig'))


def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    temp = p.with_name(p.name + '.' + uuid.uuid4().hex + '.tmp')
    temp.write_bytes(raw)
    os.replace(temp, p)


def write_new(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and p.read_text('utf-8-sig') != text:
        raise ValueError('Preserve different existing runtime: ' + str(p))
    if not p.exists():
        p.write_text(text, 'utf-8')


STORAGE = '''"""Only this selected episode's verified C-backed local route."""
from pathlib import Path
import json, os
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
SLUG=PROJECT.name
LOCAL=PROJECT/'production/local/batch-v1'
PHYSICAL=Path('C:/Users/1/.codex/video-production/design-finish-six-20261026')/SLUG/'batch-v1'
def absolute(v):
 p=Path(v);return Path(os.path.abspath(p if p.is_absolute() else ROOT/p))
def route():
 d=json.loads((HERE/'storage-routing.json').read_text('utf-8-sig'))
 if d['slug']!=SLUG or absolute(d['logicalRoot'])!=absolute(LOCAL) or absolute(d['physicalRoot'])!=absolute(PHYSICAL):raise ValueError('Wrong scoped storage record')
 if not LOCAL.is_dir() or LOCAL.resolve()!=absolute(PHYSICAL) or PHYSICAL.resolve()!=absolute(PHYSICAL):raise ValueError('Exact local junction must exist')
def logical_path(v):
 p=absolute(v)
 if p.is_relative_to(absolute(PHYSICAL)):
  route();logical=LOCAL/p.relative_to(absolute(PHYSICAL))
 elif p.is_relative_to(absolute(ROOT)):logical=p
 else:raise ValueError('Outside repository and exact media route')
 if logical.is_relative_to(LOCAL):
  route()
  if not p.resolve().is_relative_to(absolute(PHYSICAL)):raise ValueError('Nested local path escapes selected C root')
 elif not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Foreign junction not authorized')
 return logical
def repo_path(v):
 logical=logical_path(v)
 return logical.resolve()
def relative(v):return logical_path(v).relative_to(ROOT).as_posix()
def local_output(v):
 logical=logical_path(v)
 if not logical.is_relative_to(LOCAL):raise ValueError('Media output outside current local root')
 return repo_path(logical)
def write_path(v):return repo_path(v)
def same_logical_tree(v,a):return logical_path(v).is_relative_to(logical_path(a))
'''

GUARD = '''def require_authorized(stage):
    policy = read(ROOT / 'shared/publishing/video-production-control.json')
    approval = read(Path(__file__).resolve().parent / 'authorization.json')
    batch = policy.get('finiteBatchAuthorizations', {}).get('design-finish-six-20261026', {})
    if (approval.get('slug'),approval.get('revision')) != (SLUG,REVISION):
        raise ValueError('Wrong selected episode/revision authorization')
    if approval.get('fullProductionAuthorized') is not True or SLUG not in batch.get('slugs', []):
        raise ValueError('Actual explicit six-episode selection required')
    if batch.get('localProductionAuthorized') is not True or batch.get('automaticOutsideBatch') is not False:
        raise ValueError('Preserve the finite local-only boundary')
    voice=approval.get('voice',{})
    if voice.get('provider')!='ElevenLabs' or voice.get('approvedSample')!='B':
        raise ValueError('Existing own-voice Sample B required')
    return {'stage':stage,'project':SLUG,'revision':REVISION,
            'authorizationSha256':sha(Path(__file__).resolve().parent/'authorization.json'),
            'controlSha256':sha(ROOT/'shared/publishing/video-production-control.json'),
            'observedSharedSelection':policy.get('selectedVideo'),'controlSelectionChanged':False,
            'youtubeUploadPerformed':False}
'''


def main():
    now = datetime.now(timezone.utc).isoformat()
    batch = dict(id=BATCH, userMessage='25~30도 한번에 만들어줘 그리고 검수표 만들어서 보여줘',
        requestedAt=now, episodeIds=[x[0] for x in ROWS], slugs=[x[1] for x in ROWS],
        localProductionAuthorized=True, fullSixBeforeReview=True,
        boundary='Six complete local captioned/clean/KO/EN deliveries, internal QA, joint review index and selective Git.',
        youtubeAuthorized=False, driveAuthorized=False, schedulingAuthorized=False,
        deleteAuthorized=False, automaticOutsideBatch=False, automationAuthorized=False,
        preserveExistingOutputs=True, preserveD22PendingSchedule=True,
        resourcePolicy='Independent research in parallel; root sequences paid voice, GPU ASR and heavy renders. Never pause/kill foreign jobs.',
        voice='Existing own-voice ElevenLabs Sample B; existing credits only, no purchase or plan changes.',
        backgroundMusic='Approved Nimbus at -28LUFS with normal speech ducking; preserve original game sound where reviewed.',
        status='source-research', completed=0, total=6)
    if not (HERE / 'authorization.json').exists():
        save(HERE / 'authorization.json', batch)
    control_file=ROOT/'shared/publishing/video-production-control.json'
    control=read(control_file)
    control.setdefault('finiteBatchAuthorizations', {})[BATCH]=batch
    control['scopedProductionAuthorizations'].update({slug:dict(
        selectedOn=now, selectedVideo=slug, revision=REVISION, fullProductionAuthorized=True,
        batchId=BATCH, userEvidence=batch['userMessage'], privateUploadAuthorized=False,
        driveAuthorized=False, scheduleAuthorized=False, deleteAuthorized=False,
        automaticNextVideo=False, automaticOutsideBatch=False, status='source-research')
        for _ep,slug,_title,_video in ROWS})
    save(control_file,control)
    work_file=ROOT/'shared/publishing/video-worklist.json'
    work=read(work_file)
    runtime_base=ROOT/'projects/similar-game-design/production/reference-preserving-v2'
    for episode,slug,title,video in ROWS:
        project=ROOT/'projects'/slug
        local=project/'production/local'/REVISION
        physical=Path('C:/Users/1/.codex/video-production')/BATCH/slug/REVISION
        if local.resolve()!=physical:raise ValueError('Root must create exact media junction first')
        runtime=project/'production'/REVISION
        auth=dict(slug=slug,revision=REVISION,episode=episode,batchId=BATCH,
            fullProductionAuthorized=True,userEvidence=batch['userMessage'],voice=dict(
                provider='ElevenLabs',approvedSample='B',voiceId='jIRSnF8OWAsWEChVwCuK',
                settings=dict(stability=.5,similarity=.75,speed=1,audioTags=False)),
            automaticNextVideo=False,privateUploadAuthorized=False,driveAuthorized=False,
            scheduleAuthorized=False,deleteAuthorized=False)
        save(runtime/'authorization.json',auth)
        save(runtime/'storage-routing.json',dict(slug=slug,revision=REVISION,
            logicalRoot=str(local),physicalRoot=str(physical),sourceFilesPreserved=True))
        write_new(runtime/'storage_paths.py',STORAGE)
        for module in ['audio_pipeline.py','video_pipeline.py','caption_pipeline.py']:
            text=(runtime_base/module).read_text('utf-8-sig')
            if module=='audio_pipeline.py':
                tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='require_authorized')
                lines=text.splitlines(keepends=True);text=''.join(lines[:node.lineno-1])+GUARD+'\n'+''.join(lines[node.end_lineno:])
                text=text.replace('NARRATION = ROOT / "shared" / "output" / "narration" / SLUG / REVISION','NARRATION = LOCAL / "voice"')
                text=text.replace('float(settings.get("musicLufs", -31))','float(settings.get("musicLufs", -28))')
                text=text.replace('threshold=0.025:ratio=3:attack=35:release=400[bg]','threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[bg]')
                text=text.replace('afade=t=in:st=0:d=1,afade=t=out:st={max(0, duration - 2)}:d=2','afade=t=in:st=0:d=0.45,afade=t=out:st={max(0, duration - .45)}:d=0.45')
            ast.parse(text)
            write_new(runtime/module,text)
        row=next(x for x in work['rows'] if x.get('id')==episode)
        row.update(executionStatus='명시된 여섯 편 일괄 제작 중',productionStatus='원본 분석·독립 자료 확보',
                   activeRevision=REVISION,selectedBatch=BATCH,reviewStatus='완성 후 로컬 사용자 검수',
                   productionComplete=False,platformStatus='미업로드',notes='사용자25~30 유한 제작 지시. 기존 완성본·예약 보존. 업로드·예약 승인 아님.')
    save(work_file,work)
    ignore=ROOT/'.gitignore'
    text=ignore.read_text('utf-8-sig')
    for _ep,slug,_title,_video in ROWS:
        line='/projects/'+slug+'/production/local/'
        if line not in text.splitlines():text+='\n'+line+'\n'
    temp=ignore.with_name(ignore.name+'.'+uuid.uuid4().hex+'.tmp');temp.write_text(text,'utf-8');os.replace(temp,ignore)
    save(HERE/'checkpoint.json',dict(batchId=BATCH,status='research-and-scripting',updatedAt=now,
        completed=0,total=6,mediaJobs=[],youtubeMutation=False,driveMutation=False,
        episodes=[dict(id=e,slug=s,title=t,sourceUrl='https://www.youtube.com/watch?v='+v,
                       stage='source-research',productionComplete=False,humanReview='pending') for e,s,t,v in ROWS]))
    print('Initialized6 explicit local episodes; runtime/storage guards active; all other state preserved')


if __name__=='__main__':main()
