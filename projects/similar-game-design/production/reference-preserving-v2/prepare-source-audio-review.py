"""Normalize frozen source-retention evidence; no audio extraction or listening."""
from pathlib import Path
import hashlib
import json
from storage_paths import repo_path, relative

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]


def read(p):
    return json.loads(p.read_text('utf-8-sig'))


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for part in iter(lambda:f.read(4*1024*1024),b''):
            h.update(part)
    return h.hexdigest()


def main():
    evidence=PROJECT/'sources/source-audio-review-v2.json'
    inventory=PROJECT/'sources/footage-options-v2.json'
    report=read(evidence);sources={s['id']:s for s in read(inventory)['sources']}
    normalized={}
    for d in report['decisions']:
        sid=d['sourceId'];s=sources[sid];source=repo_path(s['localPath'])
        if sha(source)!=s['sha256']:
            raise ValueError('Changed source audio/image asset: '+sid)
        normalized[sid]={'sha256':s['sha256'],'sourceAudioEnabled':d['enabled'],
            'reason':d['reason'],'reviewed':True,
            'reviewScope':'Hash-bound editorial retain/mute decision from technical short-sample evidence, not actual perceptual listening.',
            'humanListening':False,'modelPerceptualListening':False,'wholeSourceListening':False,
            'actualFinalMixReview':'pending','muteRanges':d['muteRanges'],
            'startingGainDb':d['startingGainDb'],'sampleEvidence':d['sampleIds'],
            'contentAssessment':d['contentAssessment'],'decision':d['decision']}
    if len(normalized)!=7 or sum(s['sourceAudioEnabled'] for s in normalized.values())!=6 or normalized['maker2-world']['sourceAudioEnabled']:
        raise ValueError('Expected six retained sources and the scoped World Maker exception')
    result={'schemaVersion':1,'slug':'similar-game-design','revision':'reference-preserving-v2',
        'status':'editorial-source-decisions-recorded-perceptual-listening-pending',
        'sourceReview':{'path':relative(evidence),'sha256':sha(evidence)},
        'sourceInventory':{'path':relative(inventory),'sha256':sha(inventory)},
        'sources':normalized,'mixRecommendation':report['mixRecommendation'],
        'originalSourceFilesModified':False,'audioJobsStarted':False}
    (HERE/'source-audio-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print('Seven source hashes checked; six retain decisions and range-limited World Maker mute normalized. No listening or audio job claimed.')


if __name__=='__main__':
    main()
