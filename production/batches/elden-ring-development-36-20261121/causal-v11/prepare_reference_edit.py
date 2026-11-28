"""Build explicit picture beats independently of the natural narration takes."""
import argparse, math, re, sys, wave
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha
WORK=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11')
def pin(p):return dict(path=str(p),sha256=sha(p))
def norm(s):return re.sub('[^가-힣a-z0-9]','',s.lower())

def prepare(path):
    cfg=read(path);n=cfg['episode'];lp=Path(cfg['lock']);lock=read(lp)
    root=WORK/'voice'/n/sha(lp)[:12];pins=[pin(path),pin(lp),pin(root/'voice-generation-v2.json'),pin(HERE/'reference-adoption-20261128.json')]
    lengths=[];reviews=[]
    for i,expected in enumerate(lock['narrationKo']):
        wav=root/'approved-voice'/f'{n}-{i}.wav';qp=root/'voice-qa-source'/f'{n}-{i}.json';q=read(qp)
        assert q['sha256']==sha(wav) and q['expected']==expected
        with wave.open(str(wav),'rb') as f:lengths.append(math.ceil((f.getnframes()/f.getframerate()+.38)*60))
        reviews.append(q);pins.extend([pin(wav),pin(qp)])
    if sum(lengths)%2:lengths[-1]+=1
    offsets=[sum(lengths[:i]) for i in range(len(lengths))];total=sum(lengths)
    def edge(take,word,which='start'):
        w=reviews[take]['timestamped'][word];assert w['end']>w['start']
        return offsets[take]+round((.13+w[which])*60)
    paragraphs=[]
    for i,(q,script) in enumerate(zip(reviews,lock['narrationKo'])):
        words=q['timestamped'];parts=[norm(w['text']) for w in words]
        spellings=cfg.get('spellingReviews',{}).get(str(i),[])
        for c in spellings:
            assert words[c['wordIndex']]['text'].strip()==c['recognized']
            if 'evidence' in c:
                proof=Path(c['evidence']);pins.append(pin(proof));assert c['caption'] in read(proof)['recognized']
            parts[c['wordIndex']]=norm(c['caption'])
        assert ''.join(parts)==norm(script),(n,i,q['recognized'])
        chars=[k for k,c in enumerate(script) if norm(c)];totals=[];cnt=0
        for s in parts:cnt+=len(s);totals.append(cnt)
        first=0;char0=0;cues=[]
        for last in cfg['clauseEnds'][i]:
            assert first<=last<len(words)
            char1=chars[totals[last]-1]+1
            while char1<len(script) and not norm(script[char1]):char1+=1
            a=edge(i,first);b=edge(i,last,'end');assert offsets[i]<=a<b<=offsets[i]+lengths[i]
            cues.append(dict(text=script[char0:char1].strip(),startFrame=a,endFrame=b,firstWord=first,lastWord=last))
            first=last+1;char0=char1
        assert first==len(words) and norm(' '.join(c['text'] for c in cues))==norm(script)
        paragraphs.append(dict(episode=n,take=i,cues=cues,asrSpellingReview=spellings))
    # The selected five beats have reviewed roles. This is one configuration,
    # not a fixed four-paragraph or equal-adjacent-pair production rule.
    model1=lengths[1];model3=total//2-model1
    verification_end=edge(*cfg['verificationEnd'])+6
    verification_start=verification_end-model3
    assert offsets[2]<verification_start<offsets[3]<verification_end<total
    bounds=[0,offsets[1],offsets[2],verification_start,verification_end,total]
    cuts=[];timed=[];phases={};game_cursor={}
    for j,beat in enumerate(cfg['beats']):
        a,b=bounds[j:j+2];row=dict(id=f'{n}-beat-{j}',startFrame=a,endFrame=b,frames=b-a,appendix=False,**beat)
        if beat['kind']=='gameplay':
            pool=cfg['gameplayPools'][str(beat['pool'])];source=Path(pool['path']);assert sha(source)==pool['sha256']
            if pin(source) not in pins:pins.append(pin(source))
            start=game_cursor.get(beat['pool'],pool['start']);end=start+(b-a)/60
            assert end<=pool['observedUntil'],(n,j,end,pool['observedUntil'])
            row.update(path=str(source),sha256=pool['sha256'],sourceStart=start,sourceEnd=end);game_cursor[beat['pool']]=end
        else:
            native=f'{n}-{j}';row['nativeId']=native;nc=cfg['native'][str(j)];seconds=[];progress=[]
            for anchor in nc['anchors']:
                if 'localSeconds' in anchor:s=anchor['localSeconds']
                elif anchor.get('end'):s=(b-a-2)/60
                else:s=(edge(*anchor['wordEdge'])-a)/60
                seconds.append(round(s,6));progress.append(anchor['progress'])
            assert all(x<y for x,y in zip(seconds,seconds[1:])) and progress==sorted(progress)
            assert seconds[0]>=0 and seconds[-1]<(b-a)/60 and progress[0]==0 and progress[-1]==1
            timed.append(dict(id=native,episode=int(n),shot=j,frames=b-a,speechStartFrame=max(1,round(seconds[0]*60)),
              speechEndFrame=min(b-a-1,round(seconds[-1]*60)),cueSeconds=seconds,cueProgress=progress,
              pilotFrames=[min(b-a-1,round(seconds[k]*60)) for k in nc['pilotAnchors']]))
            phases[native]=dict(seconds=[0]+[seconds[k] for k in nc['phaseAnchors'][1:]],labels=nc['labels'],description=nc['description'])
        cuts.append(row)
    pins.extend(pin(Path(p)) for p in cfg.get('additionalEvidence',[]))
    timing=HERE/f'timing-{n}-reference.json'
    save(timing,dict(version='causal-v11',voiceBoundariesVerified=True,cuts=timed,inputs=pins,
      anchorMethod='Reviewed whole-word edges; explicit semantic picture beats separate from natural narration.'))
    result=dict(version='reference-causal-demonstration-v1',episode=n,lock=str(lp),voiceOutput=str(root),voiceFrames=lengths,
      paragraphs=paragraphs,cuts=cuts,phases=phases,inputs=pins+[pin(timing)],nativeTiming=str(timing),bodyFrames=total,appendixFrames=0,
      compactBodyTitle=cfg['compactBodyTitle'],voicePcmPreserved=True,selectionReview=cfg['selectionReview'],
      ratio=dict(actualGameplay=sum(c['frames'] for c in cuts if c['kind']=='gameplay'),unity=sum(c['frames'] for c in cuts if c['kind']=='unity')),
      comprehensionReview='pending timed native and final moving review',finalEpisodeComplete=False)
    assert result['ratio']['actualGameplay']==result['ratio']['unity']
    save(HERE/f'edit-{n}-reference.json',result)
    print(n,dict(seconds=total/60,voiceFrames=lengths,pictureCuts=len(cuts),nativeFrames=[c['frames'] for c in timed]))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);prepare(p.parse_args().config)
