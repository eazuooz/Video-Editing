"""Pinned independent ASR for a completed, uniquely locked v11 voice episode."""
import argparse
import atexit
import json
import sys
import uuid
import wave
from pathlib import Path
from voice import HERE, WORK, approved
sys.path.insert(0,str(HERE.parent))
import review_approved_voice_v2 as qa

def run(episode,execute,context=None,lock_path=None,mix_path=None):
    path=lock_path or HERE/'locked'/f'{episode}.json'
    lock=approved.read(path)
    output=WORK/episode/approved.sha(path)[:12]
    proof=approved.read(output/'voice-generation-v2.json')
    assert proof['identity']['planSha256']==approved.sha(path)
    for key,row in proof['takes'].items():
        assert approved.sha(output/'approved-voice'/row['file'])==row['sha256']
    guard=approved.resource_guard()
    guard.OWNER='elden-ring-causal-v11'
    guard.PROTOCOL='elden-ring-causal-v11-source-asr'
    def busy(token=None):
        reason=guard.busy_reason(own_token=token)
        if reason:return reason
        free,use=approved.headroom()
        return f'ASR requires 9216 MiB; {free} available' if free<9216 else None
    reason=busy()
    print({'episode':episode,'guard':reason,'newSourceTakes':len(proof['takes'])},flush=True)
    if reason or not execute:return
    worker=guard.SingleWorker(path=output/'asr-worker.json');worker.acquire()
    try:
        def reserve():
            if reason:=busy():raise RuntimeError(reason)
            token=uuid.uuid4().hex
            record=dict(protocol=guard.PROTOCOL,owner=guard.OWNER,token=token,
                        **guard.identity(),episode=episode,phase='source-asr',
                        resourceProfile='native-shared-guard-25pct-9GiB; user-authorized scoped usage threshold')
            with guard.LEASE.open('x',encoding='utf8') as f:json.dump(record,f)
            def release():
                if guard.LEASE.exists():
                    current=approved.read(guard.LEASE)
                    if guard.ours(current) and current.get('token')==token:guard.LEASE.unlink()
            atexit.register(release)
            if reason:=busy(token):raise RuntimeError(reason)
        if mix_path:
            render_proof=approved.read(mix_path.parent/'render-proof.json')
            assert render_proof['voiceLockSha256']==approved.sha(path)
            assert render_proof['captioned']['sha256']==approved.sha(mix_path)
            target=mix_path.parent/'voice-qa-mix'/f'{episode}.json'
            if target.exists():
                assert approved.read(target)['sha256']==approved.sha(mix_path)
                print('Exact final mix already reviewed; preserved.',flush=True)
                return
            reserve()
            transcriber=qa.load_transcriber('cuda:0')
            result=qa.listen_to(transcriber,mix_path,' '.join(lock['narrationKo']),'mix')
            target.parent.mkdir(parents=True,exist_ok=True);approved.save(target,result)
            print(json.dumps(dict(similarity=result['similarity'],recognized=result['recognized'],
                                  differences=result['differences'],review=str(target)),ensure_ascii=False),flush=True)
            return
        if context:
            request=approved.read(context)
            assert request['episode']==episode and request['lockSha256']==approved.sha(path)
            source=output/'approved-voice'/f"{episode}-{request['take']}.wav"
            assert approved.sha(source)==request['sourceSha256']
            destination=output/'independent-context'/approved.sha(context)[:12]
            result_path=destination/'review.json'
            if result_path.exists():
                assert approved.read(result_path)['requestSha256']==approved.sha(context)
                print('Exact independent context already reviewed; preserved.',flush=True)
                return
            destination.mkdir(parents=True,exist_ok=True)
            cropped=destination/'context.wav'
            with wave.open(str(source),'rb') as original:
                rate=original.getframerate()
                start,end=request['sampleRange']
                assert 0<=start<end<=original.getnframes()
                original.setpos(start)
                pcm=original.readframes(end-start)
                params=original.getparams()
            with wave.open(str(cropped),'wb') as target:
                target.setparams(params);target.writeframes(pcm)
            reserve()
            transcriber=qa.load_transcriber('cuda:0')
            result=qa.listen_to(transcriber,cropped,request['expected'],'source')
            result.update(requestSha256=approved.sha(context),sourceSha256=approved.sha(source),
                          sampleRange=[start,end],sampleRate=rate,wholeTakeRerun=False)
            approved.save(result_path,result)
            print(json.dumps(result,ensure_ascii=False),flush=True)
            return
        qa.reserve_asr=reserve
        qa.pinned_plan=lambda:[lock]
        qa.MIN_FREE=9216
        sys.argv=[__file__,'--output',str(output),'--mode','source','--device','cuda:0']
        qa.main()
    finally:worker.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--episode',required=True);p.add_argument('--execute',action='store_true')
    p.add_argument('--context',type=Path)
    p.add_argument('--lock',type=Path)
    p.add_argument('--mix',type=Path)
    a=p.parse_args();run(a.episode,a.execute,a.context,a.lock,a.mix)
