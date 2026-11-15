"""Shorten redundant opening, retain source order and byte-exact natural takes."""
from pathlib import Path
import datetime,hashlib,json,wave
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P=ROOT/'projects/shorts-oot-ninja-show-z-targeting'
BASE=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def write(p,d):
    assert not p.exists(),p
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def digest(d):return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
    old_path=BASE/'voice-sentence-v2/voice-generation-complete-proof.json';old=read(old_path);locked=P/'planning/narration-sentence-v2.json';source=read(locked)
    assert old['modelCompleted'] and old['canonical']['frames']==1900800
    for row in old['rawChunks']+[old['canonical']]:assert sha(row['path'])==row['sha256']
    review=Path(read(BASE/'asr-sentence-v2/status.json')['review']['path']);levels=review.parent/'levels.json';flags=read(levels)['flags']
    assert len(flags)==1 and flags[0]['taskKey']=='paragraph-p001'
    removed={'u003','u005','u006'};kept=[(i,u)for i,u in enumerate(source['units'])if u['id']not in removed];source['units']=[u for i,u in kept]
    for para in source['paragraphs']:
        us=[u for i,u in kept if u['paragraph']==para['id']];para.update(ko=' '.join(u['ko']for u in us),unitIds=[u['id']for u in us])
    source.update(origin=pin(locked),editorialRevision='Remove the redundant spoken term/outlining from the opening; keep the hook, target-relative action and Kyoto question. The word lock-on remains in the title. All explanation, reasons and original article order remain in p002..p007.',previousSourceVoice=pin(old_path),previousAsr=pin(review),previousLevels=pin(levels),voiceAcceptedForFilm=False)
    new_locked=P/'planning/narration-edited-v3.json';write(new_locked,source)
    clauses=read(P/'planning/caption-clauses-sentence-v2.json');clauses['source']=pin(new_locked);clauses['paragraphs'][0]['clauses']=[x for i,x in enumerate(clauses['paragraphs'][0]['clauses'])if i in[0,1,3]]
    for para,cl in zip(source['paragraphs'],clauses['paragraphs']):assert ''.join(para['ko'].split())==''.join(''.join(x[0]for x in cl['clauses']).split())
    write(P/'planning/caption-clauses-edited-v3.json',clauses)
    target=BASE/'voice-edit-v3';target.mkdir(parents=True,exist_ok=True);pieces=[];units=[];raw=[];position=0;gap=6720
    for n,(old_index,u)in enumerate(kept):
        row=old['rawChunks'][old_index]
        with wave.open(row['path'],'rb')as w:
            assert(w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,24000);data=w.readframes(w.getnframes())
        assert hashlib.sha256(data).hexdigest()==row['pcmSHA256']
        pieces.append(data);units.append(dict(index=n+1,scene_id=u['id'],text=u['ko'],start=position/24000,end=(position+row['frames'])/24000));position+=row['frames'];raw.append(row)
        if n<len(kept)-1:pieces.append(bytes(gap*2));position+=gap
    pcm=b''.join(pieces);wav=target/'lockon-edited-v3.wav';assert not wav.exists()
    with wave.open(str(wav),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
    timing=target/'unit-timing.json';write(timing,dict(sample_rate=24000,entries=units,duration_seconds=position/24000,assembly='Unmodified raw natural takes plus explicit0.28s gaps; no removed internal PCM.'))
    paragraphs=[]
    for para in source['paragraphs']:
        rows=[e for e,u in zip(units,source['units'])if u['paragraph']==para['id']];paragraphs.append(dict(id=para['id'],text=para['ko'],start=rows[0]['start'],end=rows[-1]['end'],startSample=round(rows[0]['start']*24000),endSample=round(rows[-1]['end']*24000)))
    para_timing=target/'paragraph-timing.json';write(para_timing,dict(entries=paragraphs,sampleRate=24000,rawBytesPreserved=True))
    identity=dict(slug=P.name,sourceInputs=[pin(new_locked),pin(old_path),pin(review),pin(levels),pin(__file__)],spoken=[u['ko']for u in source['units']],unitGroups=source['units'],paragraphs=source['paragraphs'],unitGapSeconds=.28,removedUnits=sorted(removed),sameApprovedVoice=True,noGainSpeedTrimOrCompression=True)
    proof=dict(fingerprint=digest(identity),identity=identity,rawChunks=raw,canonical=dict(**pin(wav),frames=position,rate=24000,duration=position/24000,pcmSHA256=hashlib.sha256(pcm).hexdigest()),unitTiming=pin(timing),paragraphTiming=pin(para_timing),modelCompleted=True,sourceModelGenerationReused=True,newModelStarted=False,sourceRawPcmAllExact=True,voiceAcceptedForFilm=False,actualListening=False,humanApproval=False)
    write(target/'voice-generation-complete-proof.json',proof);write(target/'edit-review.json',dict(source=pin(old_path),rawChunksRetained=len(raw),removedUnits=sorted(removed),unaffectedParagraphsByteExact=True,reason=source['editorialRevision'],newIndependentReviewRequired=['paragraph-p001','join-u002-u004','join-u004-u007'],unchangedUnitsAndOtherParagraphsUsePriorIndependentReview=True,numericPassNotInferredFromShortening=True))
    print(json.dumps(dict(proof=pin(target/'voice-generation-complete-proof.json'),duration=position/24000,rawChunksRetained=len(raw),accepted=False)))
if __name__=='__main__':main()
