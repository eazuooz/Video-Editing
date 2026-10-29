"""Prepare the explicitly selected BOTW revision without touching prior media."""
from pathlib import Path
import datetime, hashlib, json, sys

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
BASE=PROJECT/'production/clarity-v3'

def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')

def main():
    for name in ['audio_pipeline.py','video_pipeline.py','caption_pipeline.py','verify_audio.py','extract_review.py']:
        dst=HERE/name
        if not dst.exists():
            text=(BASE/name).read_text('utf-8-sig').replace('clarity-v3','botw-v4')
            dst.write_text(text,'utf-8')
    local=PROJECT/'production/local/botw-v4'
    local.mkdir(parents=True,exist_ok=True)
    assert local.resolve()==local.absolute(), 'New revision must stay directly inside D repository'
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    auth={'schemaVersion':1,'slug':PROJECT.name,'revision':'botw-v4','userDirectedOn':'2026-10-29',
          'userEvidence':'응 29편 야숨으로 바꿔서 대본이랑 유니티 설명도 같이 수정하고 검수본 다시 만들어줘~',
          'scope':'Replace Mario Kart with Breath of the Wild, revise narration and Unity explanations, retain source claim order and Unpacking/A Short Hike, complete new local four-output review.',
          'localProductionAuthorized':True,'newNarrationAuthorized':True,'newTts':'root-coordinated-Sample-B',
          'gpuUserCondition':'user-confirmed-game-ended; check fresh resource state before heavy work',
          'noUiOrFocus':True,'platformMutation':False,'otherVideosAuthorized':False,
          'preserveRevision':'clarity-v3','priorCaptionedSha256':'bb2b401177e86718597de5510b4d40b10133ed4ab6c08a8f5954d6de75862271',
          'updatedAt':now}
    save(HERE/'authorization.json',auth)
    prior=HERE/'prior-project-manifest.json'
    if not prior.exists(): prior.write_bytes((PROJECT/'project.json').read_bytes())
    save(HERE/'checkpoint.json',{'slug':PROJECT.name,'revision':'botw-v4','status':'script-and-independent-footage-preparation',
        'updatedAt':now,'priorOutputsPreserved':True,'humanWholeReview':'pending-new-output','platformMutation':False,
        'productionChoice':'New local media on D directly; 357GB free observed. Keep existing C junction baselines read-only.'})
    sys.path.insert(0,str(ROOT/'production/batches/design-25-30-review-actions-20261029'))
    from scoped_json import patch
    path=ROOT/'shared/publishing/video-production-control.json';raw=path.read_bytes()
    key='design-25-30-review-actions-20261029';control=json.loads(raw.decode('utf-8-sig'))
    entry=control['finiteBatchAuthorizations'][key]
    entry['selectedD29Revision']={'revision':'botw-v4','status':'production','userEvidence':auth['userEvidence'],
        'localProductionAuthorized':True,'newNarrationAuthorized':True,'newTtsAuthorized':True,
        'boundary':'New complete local review; no platform mutation before human review','record':str(HERE.relative_to(ROOT)).replace('\\','/')+'/authorization.json'}
    path.write_bytes(patch(raw,['finiteBatchAuthorizations',key],entry))
    print('Prepared isolated pipeline, authorization and current scoped control entry; old manifests/media preserved.')

if __name__=='__main__':main()
