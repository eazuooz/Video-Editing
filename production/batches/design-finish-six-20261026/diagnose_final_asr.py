"""One bounded, unprompted check of an observed final-ASR discrepancy."""
from pathlib import Path
import argparse,json,os,sys
ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('slug');ap.add_argument('start',type=float);ap.add_argument('end',type=float);ap.add_argument('--reason',required=True)
args=ap.parse_args()
allowed={'limited-color-world','computer-controlled-players','in-game-cutscenes','start-with-climax','kind-to-beginners','respect-player-time'}
assert args.slug in allowed and 0<=args.start<args.end and args.end-args.start<=30
sys.path.insert(0,str(ROOT/f'projects/{args.slug}/production/batch-v1'))
import audio_pipeline as base
base.require_authorized('bounded diagnosis of observed final encoded ASR discrepancy')
plan=base.read(ROOT/f'projects/{args.slug}/production/batch-v1/edit-plan.json')
source=ROOT/plan['outputDir']/'encoded-audio-for-asr.wav'
full=source.parent/'final-mix-asr.json'
digest=base.sha(source);assert base.read(full)['audio_sha256']==digest
out=Path('C:/Users/1/.codex/video-production/design-finish-six-20261026/review/final-asr-diagnostics')
out.mkdir(parents=True,exist_ok=True)
stem=f'{args.slug}-{digest[:12]}-{args.start:g}-{args.end:g}';receipt=out/(stem+'.json')
if receipt.exists():
    prior=base.read(receipt);assert prior['sourceSha256']==digest
    print(json.dumps(prior,ensure_ascii=False));sys.exit(0)
device=os.environ.get('VIDEO_BATCH_ASR_DEVICE','cpu')
with base.batch_asr_lease(device):
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    import soundfile as sf,torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(4)
    model_id='openai/whisper-large-v3-turbo'
    dtype=torch.float16 if device=='cuda' else torch.float32
    model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=dtype,attn_implementation='sdpa',local_files_only=True)
    p=AutoProcessor.from_pretrained(model_id,local_files_only=True)
    recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=dtype,device=0 if device=='cuda' else 'cpu')
    with sf.SoundFile(source) as a:
        rate=a.samplerate;a.seek(round(args.start*rate));audio=a.read(round((args.end-args.start)*rate),dtype='float32')
    clip=out/(stem+'.wav');sf.write(clip,audio,rate,subtype='FLOAT')
    result=recognize(str(clip),generate_kwargs={'language':'korean','task':'transcribe','num_beams':1},return_timestamps=True)
    record={'slug':args.slug,'sourceSha256':digest,'fullAsrSha256':base.sha(full),'rangeSeconds':[args.start,args.end],'reason':args.reason,'device':device,'threads':4,'noExpectedPrompt':True,'oneBoundedPass':True,'recognized':result['text'],'segments':result.get('chunks'),'sourcePcmChanged':False,'humanListening':'pending'}
    receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(record,ensure_ascii=False))
