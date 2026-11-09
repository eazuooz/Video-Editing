"""Verify A04/030 continuity correction touches new padding only."""
from pathlib import Path
import hashlib,shutil,time
import numpy as np
import soundfile as sf
import prepare_final_audio as a

def snap(p):
    return {'sha256':a.sha(p),'mtimeNs':Path(p).stat().st_mtime_ns}

def main():
    old_plan=a.read(a.L/'A04/audio-plan.json')
    target=next(g for g in old_plan['groups']if '030'in g['sentenceIds'])
    current=a.R/target['source']
    folder=Path('C:/Users/1/Videos/YamyamProduction/animation-contrast-v5-work/audio-tail-proof');folder.mkdir(parents=True,exist_ok=True)
    preserved=folder/('A04-030-before-'+target['sourceSha256'][:16]+'.wav')
    if not preserved.exists():shutil.copyfile(current,preserved)
    before,_=sf.read(preserved,dtype='float32',always_2d=True)
    all_audio=[a.R/g['source']for ep in a.read(a.L/'audio-preparation.json')['episodes']for g in ep['groups']if'source'in g]
    other_before={str(p):snap(p)for p in all_audio if p!=current}
    takes={p['take']['path']:p['take']['sha256']for p in target['placements']}
    a.prepare(['A04']);new=next(g for g in a.read(a.L/'A04/audio-plan.json')['groups']if g['id']==target['id'])
    after,_=sf.read(current,dtype='float32',always_2d=True)
    assert before.shape==after.shape and target['placements']==new['placements']
    bridge=new['tailContinuityBridges'][0];start=bridge['startSampleInGroup'];end=start+bridge['samples']
    changed=np.flatnonzero(np.any(before!=after,axis=1))
    assert len(changed)>0 and changed.min()>=start and changed.max()<end
    assert np.array_equal(before[:start],after[:start])and np.array_equal(before[end:],after[end:])
    other_after={str(p):snap(p)for p in all_audio if p!=current};assert other_before==other_after
    assert all(a.sha(a.R/p)==s for p,s in takes.items())
    first=snap(current);time.sleep(1.2);a.prepare(['A04']);second=snap(current);assert first==second
    a.align_ready()
    a.save(a.L/'tail-continuity-proof.json',{'scope':'A04/030 existing new-padding-only continuity correction',
        'preservedBeforeWav':str(preserved),'beforeSha256':a.sha(preserved),'afterSha256':second['sha256'],
        'changedSampleRange':[int(changed.min()),int(changed.max())+1],'declaredPaddingRange':[start,end],
        'allPriorVoicedSamplesExact':True,'allLaterSamplesExact':True,'placementTimingsExact':True,
        'sourceTakesExact':takes,'allOtherMixFilesByteAndMtimeExact':True,'otherMixCount':len(other_before),
        'otherMixFiles':other_after,'secondPrepareExactlyStable':True,'bridge':bridge,
        'ttsGenerated':False,'humanListening':False})
    print('PASS: only',len(changed),'new padding frames changed;',len(other_before),'other mix files and all voiced PCM remain exact')

if __name__=='__main__':main()
