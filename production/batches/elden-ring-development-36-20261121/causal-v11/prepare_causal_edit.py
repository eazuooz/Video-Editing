"""Make an edit from reviewed whole-word clauses and explicit scene-stage anchors."""
import argparse
import math
from pathlib import Path
import re
import sys
import wave
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha
WORK=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11')

def norm(text):return re.sub('[^가-힣a-z0-9]','',text.lower())
def pin(p):return dict(path=str(p),sha256=sha(p))

def prepare(config_path):
    config=read(config_path);number=config['episode'];lock_path=Path(config['lock']);lock=read(lock_path)
    root=WORK/'voice'/number/sha(lock_path)[:12]
    pins=[pin(config_path),pin(lock_path),pin(root/'voice-generation-v2.json')]
    reviews=[];durations=[]
    for i in range(4):
        wav=root/'approved-voice'/f'{number}-{i}.wav';qp=root/'voice-qa-source'/f'{number}-{i}.json'
        q=read(qp);assert q['sha256']==sha(wav) and q['expected']==lock['narrationKo'][i]
        with wave.open(str(wav),'rb') as f:durations.append(f.getnframes()/f.getframerate())
        reviews.append(q);pins.extend([pin(wav),pin(qp)])
    lengths=[]
    for a,b in [(0,1),(2,3)]:lengths.extend([math.ceil((max(durations[a],durations[b])+.38)*60)]*2)
    paragraphs=[];position=0;timed_cuts=[];phases={}
    for i,q in enumerate(reviews):
        words=q['timestamped'];script=lock['narrationKo'][i];parts=[norm(w['text']) for w in words]
        spellings=config.get('spellingReviews',{}).get(str(i),[])
        for correction in spellings:
            index=correction['wordIndex'];assert words[index]['text'].strip()==correction['recognized']
            if 'evidence' in correction:
                proof=Path(correction['evidence']);assert proof.exists();pins.append(pin(proof))
                assert correction['caption'] in read(proof)['recognized']
            parts[index]=norm(correction['caption'])
        assert ''.join(parts)==norm(script),(number,i,q['recognized'])
        chars=[k for k,c in enumerate(script) if norm(c)];totals=[];total=0
        for p in parts:total+=len(p);totals.append(total)
        cues=[];first=0;char_start=0
        for last in config['clauseEnds'][i]:
            assert first<=last<len(words) and words[first]['end']>words[first]['start'] and words[last]['end']>words[last]['start']
            char_end=chars[totals[last]-1]+1
            while char_end<len(script) and not norm(script[char_end]):char_end+=1
            lo=position+round((.13+words[first]['start'])*60);hi=position+round((.13+words[last]['end'])*60)
            assert lo<hi<=position+lengths[i]
            cues.append(dict(text=script[char_start:char_end].strip(),startFrame=lo,endFrame=hi,firstWord=first,lastWord=last))
            first=last+1;char_start=char_end
        assert first==len(words) and norm(' '.join(c['text'] for c in cues))==norm(script)
        paragraphs.append(dict(episode=number,take=i,cues=cues,asrSpellingReview=spellings))
        if i in (1,3):
            cfg=config['native'][str(i)];seconds=[];progress=[]
            for a in cfg['anchors']:
                seconds.append(round(.13+(words[a['word']]['end'] if a.get('edge')=='end' else words[a['word']]['start']),6))
                progress.append(a['progress'])
            assert all(a<b for a,b in zip(seconds,seconds[1:])) and progress==sorted(progress)
            assert progress[0]==0 and progress[-1]==1
            timed_cuts.append(dict(id=f'{number}-{i}',episode=int(number),shot=i,frames=lengths[i],
                speechStartFrame=round((.13+words[0]['start'])*60),speechEndFrame=round((.13+words[-1]['end'])*60),
                cueSeconds=seconds,cueProgress=progress,pilotFrames=[min(lengths[i]-1,round(seconds[k]*60)) for k in cfg['pilotAnchors']]))
            phases[str(i)]=dict(seconds=[0]+[seconds[k] for k in cfg['phaseAnchors'][1:]],labels=cfg['labels'],description=cfg['description'])
            assert len(phases[str(i)]['seconds'])==len(cfg['labels'])
        position+=lengths[i]
    gameplay=[]
    for row in config['gameplay']:
        source=Path(row['path']);assert sha(source)==row['sha256'];pins.append(pin(source))
        assert row['start']+lengths[row['index']]/60<=row['observedUntil']
        gameplay.append({**row,'frames':lengths[row['index']]})
    timing_path=HERE/f'timing-{config_path.stem.removeprefix("edit-config-")}.json'
    timing=dict(version='causal-v11',voiceBoundariesVerified=True,cuts=timed_cuts,allSceneFrames=lengths,inputs=pins,
        anchorMethod='Reviewed positive whole-word edges; explicit semantic scene states, no word-internal interpolation.',
        sourceAudioReview='Content reviewed; local level contexts and mixed review remain separate.')
    save(timing_path,timing)
    result=dict(version='causal-v11',episode=number,lock=str(lock_path),voiceOutput=str(root),paragraphs=paragraphs,
        sceneFrames=lengths,appendixFrames=0,gameplay=gameplay,nativeTiming=str(timing_path),inputs=pins+[pin(timing_path)],
        selectionReview=config['selectionReview'],phases=phases,finalEpisodeComplete=False,humanReview='pending')
    output=HERE/f'edit-{config_path.stem.removeprefix("edit-config-")}.json';save(output,result)
    print(number,lengths,sum(lengths)/60,'seconds',sum(len(p['cues']) for p in paragraphs),'clauses',timing_path)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);prepare(p.parse_args().config)
