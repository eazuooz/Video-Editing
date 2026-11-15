"""Preserve generated raw takes and assemble a separate byte-exact PCM edition.

The legacy assembler's bound default fade argument can differ from its mutable
FADE_SECONDS global. This edition never calls that assembler or alters a take.
No model/GPU, gain, fade, time change, trim, compression or platform action.
"""
from pathlib import Path
import datetime,hashlib,json,wave
ROOT=Path(__file__).resolve().parents[3]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
BASE=MEDIA/'shorts-oot-ninja-show-z-targeting';SOURCE=BASE/'voice-v1/voice-generation-complete-proof.json';DEST=BASE/'voice-v2'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def pcm(p):
    with wave.open(str(p),'rb')as w:
        assert(w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getcomptype())==(1,2,24000,'NONE')
        return w.readframes(w.getnframes())
def main():
    source=read(SOURCE);assert source['modelCompleted']and len(source['rawChunks'])==7
    for row in source['rawChunks']:assert sha(row['path'])==row['sha256']and hashlib.sha256(pcm(row['path'])).hexdigest()==row['pcmSHA256']
    if DEST.exists():raise RuntimeError('Preserve existing raw-canonical edition; inspect proof instead of rewriting')
    DEST.mkdir();gap=round(source['identity']['paragraphGapSeconds']*24000);parts=[];entries=[];position=0
    old_timing=read(source['paragraphTiming']['path']);old=pcm(source['canonical']['path']);differences=[]
    import numpy as np
    for i,(raw,e)in enumerate(zip(source['rawChunks'],old_timing['entries'])):
        data=pcm(raw['path']);assert len(data)==raw['frames']*2
        before=np.frombuffer(old[2*position:2*(position+raw['frames'])],dtype='<i2').astype(int);after=np.frombuffer(data,dtype='<i2').astype(int)
        differences.append(dict(scene=e['scene_id'],changedSamples=int(np.sum(before!=after)),maximumAbsolutePcmDifference=int(np.max(np.abs(before-after))),priorCanonicalRetained=True))
        parts.append(data);entry=dict(e,start=position/24000,end=(position+raw['frames'])/24000);entries.append(entry);position+=raw['frames']
        if i<6:parts.append(bytes(gap*2));position+=gap
    path=DEST/'lockon-raw-canonical-v2.wav';all_pcm=b''.join(parts)
    with wave.open(str(path),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(all_pcm)
    assert pcm(path)==all_pcm
    timing=DEST/'paragraph-timing-v2.json';save(timing,dict(sample_rate=24000,duration_seconds=position/24000,render_mode='byte-exact-raw-takes',entries=entries,paragraphGapSamples=gap))
    identity=dict(sourceGenerationProof=pin(SOURCE),sourceInputs=source['identity']['sourceInputs']+[pin(SOURCE),pin(__file__)],paragraphGapSeconds=gap/24000,assembly='raw PCM16 bytes plus explicit paragraph silence only',noGainFadeSpeedTrimOrCompression=True)
    fp=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    canonical=dict(**pin(path),frames=position,rate=24000,duration=position/24000,pcmSHA256=hashlib.sha256(all_pcm).hexdigest())
    proof=dict(fingerprint=fp,identity=identity,rawChunks=source['rawChunks'],canonical=canonical,paragraphTiming=pin(timing),modelCompleted=True,modelRerun=False,voiceAcceptedForFilm=False,actualListening=False,humanApproval=False,
        priorAssemblyAudit=dict(priorProof=pin(SOURCE),findings='Legacy function default edge-fade argument remained bound despite mutable FADE_SECONDS=0. Prior canonical excluded from downstream; raw takes retained byte-exact.',differences=differences))
    save(DEST/'voice-generation-complete-proof.json',proof);print(json.dumps(dict(completed=True,modelRerun=False,rawTakesPreserved=7,frames=position,proof=pin(DEST/'voice-generation-complete-proof.json'))))
if __name__=='__main__':main()
