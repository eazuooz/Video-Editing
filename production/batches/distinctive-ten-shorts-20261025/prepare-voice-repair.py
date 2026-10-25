"""Preserve an entire prior audio attempt and reuse only exact unchanged takes."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parents[2]
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025').resolve()

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slug', required=True)
    parser.add_argument('--changed-take', action='append', required=True)
    parser.add_argument('--reason', required=True)
    args=parser.parse_args()
    allowed={r['slug'] for r in read(BATCH/'batch.json')['projects']}
    assert args.slug in allowed
    auth=read(ROOT/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations']['explicit-ten-distinctive-shorts-20261025']
    assert auth['status']=='active' and auth['fullProductionAuthorized']
    project=ROOT/'projects'/args.slug
    local=(project/'production/local').resolve()
    assert local.is_relative_to(MEDIA)
    original=local/'audio-v1'
    record=read(original/'tts-execution.json')
    assert record['state']=='completed'
    takes={r['key']:r for r in record['takes']}
    current={f'{scene["id"]}-{index:02}':text for scene in read(project/'script/narration.spoken.ko.json')['scenes'] for index,text in enumerate(scene['lines'],1)}
    changed={key for key,text in current.items() if takes[key]['text']!=text}
    assert changed==set(args.changed_take),(changed,args.changed_take)
    for key,take in takes.items():
        assert sha(original/'voice/chunks'/(key+'.wav'))==take['sha256']
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    archive=local/('audio-preserved-before-wording-repair-'+stamp)
    assert not archive.exists()
    state=local/'finite-finalizer-v1'
    if state.exists():
        status=read(state/'state.json')['status']
        assert status=='failed' or status.startswith('review-files-generated'),status
        state.rename(local/('finite-finalizer-preserved-before-wording-repair-'+stamp))
    original.rename(archive)
    chunks=original/'voice/chunks';chunks.mkdir(parents=True)
    reuse={}
    for key,text in current.items():
        if key in changed:continue
        filename=key+'.wav';source=archive/'voice/chunks'/filename;destination=chunks/filename
        shutil.copy2(source,destination)
        assert sha(destination)==takes[key]['sha256']
        reuse[filename]={'sha256':sha(destination),'text':text}
    (original/'reuse-takes.json').write_text(json.dumps(reuse,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    evidence={'reason':args.reason,'previousAudioDirectory':str(archive),'previousVoiceSha256':record['voiceSha256'],'regenerateTakeKeys':sorted(changed),'unchangedTakeKeys':sorted(k for k in current if k not in changed),'preservedRawPcm':True,'actualListeningPerformed':False,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (original/'wording-repair.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(evidence,ensure_ascii=False))

if __name__=='__main__':
    main()
