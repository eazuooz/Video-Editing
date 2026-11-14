"""Resolve operation reveals against existing actual PCM word timestamps."""
import importlib.util
from pathlib import Path
from inventory import ROOT,HERE,read,save,sha
from workings import WORKINGS


def main():
    spec=importlib.util.spec_from_file_location('owned_math_word_normalizer',ROOT/'projects/game-math-shading-lights/production/align-captions-and-cues.py')
    align=importlib.util.module_from_spec(spec);spec.loader.exec_module(align)
    inventory=read(HERE/'inventory.json');evidence=[];unresolved=[]
    for episode in inventory['episodes']:
        if episode['id']=='M21':continue # Its delivered v7 replacement clauses stay authoritative.
        queue=read(ROOT/'projects'/episode['slug']/'production/local'/episode['baselineRevision']/'queue.json')
        audio=Path(queue['audioDirectory']);asr=read(audio/'review/source-full-asr.timestamps.json')
        assert sha(audio/'narration.wav')==asr['audio_sha256']
        for scene in episode['scenes']:
            if scene['scene'] not in WORKINGS.get(episode['id'],{}):continue
            scene['operationWordEvidence']=[]
            text=scene['speech'];normalized,source_owners=align.normalize_owned(text,list(range(len(text))))
            words=[w for w in asr['chunks'] if None not in w['timestamp'] and scene['start']-2-.05<=w['timestamp'][0]<scene['end']-2]
            _,_,mapping,owners,_=align.map_chars(text,words)
            for phrase,formula,meaning in WORKINGS[episode['id']][scene['scene']]['steps']:
                try:
                    needle=align.normalized(phrase);first=normalized.find(needle)
                    assert first>=0 and normalized.find(needle,first+1)<0, 'Phrase must occur exactly once'
                    raw_first=source_owners[first];raw_last=source_owners[first+len(needle)-1]+1
                    literal=text[raw_first:raw_last]
                    at,proof=align.phrase_time(text,literal,mapping,owners,raw_first)
                    assert scene['start']-.05<=at+2<scene['end']
                    proof.update(phrase=phrase,literalSpokenAnchor=literal,audioSha256=asr['audio_sha256'],
                        basis='Actual unchanged narration PCM word timestamp; independently normalized spelling and numbers')
                    scene['operationWordEvidence'].append(proof)
                    evidence.append(dict(episode=episode['id'],scene=scene['scene'],globalTime=at+2,**proof))
                except (ValueError,AssertionError,IndexError) as error:
                    unresolved.append(dict(episode=episode['id'],scene=scene['scene'],phrase=phrase,error=repr(error),
                        fallback='Current delivered caption clause; inspect if stages coincide'))
    save(HERE/'inventory.json',inventory)
    save(HERE/'operation-word-alignment.json',dict(resolved=evidence,unresolved=unresolved,newModelRun=False,humanListening=False))
    print('resolved',len(evidence),'fallback',len(unresolved));print(unresolved)


if __name__=='__main__':main()
