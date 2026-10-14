"""Prepare exact PCM-splice mixing; no audio synthesis or execution."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
src=(ROOT/'production/batches/unpublished-teaching-clarity-revision/build-motion-current-mix-v1.py').read_text('utf-8')
src=src.replace('revision-teaching-clarity-v1','revision-cross-game-four-v1').replace('shared/output/unpublished-teaching-clarity-revision/motion/current-mix-v1','shared/output/cross-game-example-coverage/motion/current17-mix-v1').replace('current14','current17').replace('retained12 and additive2','retained14 and additive3')
start=src.index('    protected=read(');end=src.index('    mf=read(',start)
src=src[:start]+"""    protected=read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs']
    assert len(protected)==71
    for row in protected:assert sha(ROOT/row['path'])==row['sha256']
    plan=read(R/'measured-current17-plan-v1.json')
    assert len(plan['scenes'])==17 and len(plan['voicePlacements'])==29
    assert plan['all14BaselineScenesAndPcmRetained'] and plan['current3PcmAllSamplesMappedExactly']
"""+src[end:]
start=src.index('    cp=read(',src.index('def checkpoint'))
end=src.index("if __name__=='__main__':",start)
src=src[:start]+"""    cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],activeOwnedWorkers=0 if state['actualExitCode'] is not None else 1,
      ownedJob=dict(active=state['actualExitCode'] is None,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=rel(R/'current-mix-execution-v1.json'),cpuThreads=2,gpuJobs=0,actualExitCode=state['actualExitCode']),
      currentMixedAudioApproved=False,next='Verify actual current17 mix exit then whole17 and independent81 current mixed contexts. Retime KOEN/chapter/end together and review final pixels before delivery.')
    save(R/'latest-checkpoint.json',cp)
    qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
    for v in q.values():
        if isinstance(v,dict) and str(v.get('currentCheckpoint','')).endswith('revision-cross-game-four-v1/latest-checkpoint.json'):
            v.update(activeOwnedWorkers=cp['activeOwnedWorkers'],currentMixExecution=rel(R/'current-mix-execution-v1.json'))
    q.update(recordedAt=now(),next=cp['next']);assert qp.read_text('utf-8-sig')==raw;save(qp,q)
"""+src[end:]
start=src.index("        for s in plan['scenes']:");end=src.index('        assert not any(raw',start)
src=src[:start]+"""        voice_coverage={};dest_ranges=[]
        for s in plan['voicePlacements']:
            p=ROOT/s['voice'];assert sha(p)==s['sha256']
            with wave.open(str(p),'rb') as w:
                assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
                ns=w.getnframes();w.setpos(s['sourceStartSample']);pcm=w.readframes(s['sourceEndSample']-s['sourceStartSample'])
            n=s['sourceEndSample']-s['sourceStartSample'];a=s['destinationStartSample'];b=a+n
            assert len(pcm)==n*2 and b<=fullsamples
            for x,y in dest_ranges:assert b<=x or a>=y
            dest_ranges.append((a,b));raw[a*2:b*2]=pcm;assert bytes(raw[a*2:b*2])==pcm
            spans=voice_coverage.setdefault(s['voice'],[]);spans.append((s['sourceStartSample'],s['sourceEndSample'],ns))
            state['placements'].append(dict(s,pcmSha256=hashlib.sha256(pcm).hexdigest(),exactOriginalPcmBytesMatched=True,destinationEndSample=b))
        assert len(voice_coverage)==17
        for spans in voice_coverage.values():
            cursor=0
            for a,b,ns in sorted(spans):assert a==cursor;cursor=b
            assert cursor==ns
"""+src[end:]
src=src.replace('measured-additive-plan-v1.json','measured-current17-plan-v1.json').replace('all26ProtectedInputsUnchanged','all71ProtectedInputsUnchanged').replace('all14RawPcmPlacementsExact','all17RawPcmPlacementsExact').replace('raw14PcmExact','raw17PcmExact').replace('current14 whole and66','current17 whole and81')
dest=B/'build-motion-current17-mix-v1.py';assert not dest.exists();dest.write_text(src,'utf-8')
compile(src,str(dest),'exec')
print('Prepared current17 mixer with29 exact placements,17 whole-source coverage and71 protected inputs; execution0.')
