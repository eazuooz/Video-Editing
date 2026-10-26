"""Resolve observed Whisper stride-tail anomalies without modifying narration."""
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'projects/limited-color-world/production/batch-v1'))
import audio_pipeline as base
import soundfile as sf

def main():
    device=os.environ.get('VIDEO_BATCH_ASR_DEVICE','cpu')
    cases=[('computer-controlled-players',215,238),('kind-to-beginners',277,297),('start-with-climax',155,178),('in-game-cutscenes',241,263)]
    control=base.read(ROOT/'shared/publishing/video-production-control.json')
    batch=control.get('finiteBatchAuthorizations',{}).get('design-finish-six-20261026',{})
    if batch.get('localProductionAuthorized') is not True or any(c[0] not in batch.get('slugs',[]) for c in cases):
        raise ValueError('Current finite local production authorization is required')
    out=Path('C:/Users/1/.codex/video-production/design-finish-six-20261026/review/asr-overlap')
    out.mkdir(parents=True,exist_ok=True)
    pending=[]
    for slug,start,end in cases:
        source=ROOT/f'projects/{slug}/production/local/batch-v1/voice/narration-source.wav'
        receipt=out/f'{slug}.json'
        if receipt.exists():
            prior=json.loads(receipt.read_text('utf-8'))
            if prior['sourceSha256']!=base.sha(source):raise ValueError('Changed source requires a new revision')
            print(json.dumps(prior,ensure_ascii=False));continue
        pending.append((slug,start,end,source,receipt))
    if not pending:return
    with base.batch_asr_lease(device):
        lease=out.parent.parent/'heavy-job.lock.json'
        lease_record=base.read(lease)
        if lease_record['pid']!=os.getpid():raise ValueError('Only the owned lease may be updated')
        lease_record.update(kind='bounded diagnosis of observed ASR overlap',slugs=[c[0] for c in cases])
        lease.write_text(json.dumps(lease_record),encoding='utf-8')
        os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
        import torch
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(4)
        model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model_id=str(model_path) if (model_path/'config.json').is_file() else 'openai/whisper-large-v3-turbo'
        dtype=torch.float16 if device=='cuda' else torch.float32
        model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=dtype,attn_implementation='sdpa',local_files_only=True)
        p=AutoProcessor.from_pretrained(model_id,local_files_only=True)
        recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=dtype,device=0 if device=='cuda' else 'cpu')
        for slug,start,end,source,receipt in pending:
            audio,rate=sf.read(source,dtype='float32')
            clip=out/f'{slug}-{start}-{end}.wav'
            sf.write(clip,audio[int(start*rate):int(end*rate)],rate,subtype='FLOAT')
            result=recognize(str(clip),generate_kwargs={'language':'korean','task':'transcribe','num_beams':1},return_timestamps=True)
            record={'slug':slug,'sourceSha256':base.sha(source),'rangeSeconds':[start,end],
                    'reason':('Full ASR omits the QTE abbreviation at a chunk boundary' if slug=='in-game-cutscenes' else 'Observed raw full-ASR clock regression and unsupported stride-tail hypothesis'),
                    'device':device,'threads':4,'noExpectedPrompt':True,'oneBoundedPass':True,
                    'recognized':result['text'],'segments':result.get('chunks'),
                    'sourcePcmChanged':False,'humanListening':'pending'}
            receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(json.dumps(record,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
