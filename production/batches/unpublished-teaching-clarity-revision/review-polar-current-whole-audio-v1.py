"""Current whole AAC:19 entire chapters and19 complete independent contexts.

Run once on CPU2 after the existing owned render job closes. Expected text
is comparison data, never a recognizer prompt. No automatic approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, os, json, hashlib, subprocess, wave, traceback
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/current-whole-audio-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def now():return datetime.now(timezone.utc).isoformat()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
    resource=read(ROOT/args.resource)
    assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8000000
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    five=read(OUT/'five-moving-pilots-execution-v1.json');assert five['status']=='completed' and five['exitCode']==0
    snapshot=read(OUT/'baseline-protected-sha-v1.json');assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
    baseline=ROOT/'shared/output/motion-canvas/game-math-polar-3d.mp4'
    assert sha(baseline)=='b983fb0206b2168f630c16de0c7dd987ab497fdca946f33121e5d5b275a04efd'
    timelinefile=ROOT/'projects/game-math-polar-3d/production/timeline.json';timeline=read(timelinefile)
    scriptfile=ROOT/'projects/game-math-polar-3d/script/narration.ko.json';script=read(scriptfile)
    assert timeline['frames']==54115 and len(timeline['scenes'])==len(script['scenes'])==19
    windows=[]
    for scene,chapter in zip(timeline['scenes'],script['scenes']):
        assert scene['id']==chapter['id']
        assert ''.join(c['text'] for c in scene['cues'])==''.join(chapter['lines'])
        assert sha(ROOT/scene['voice'])==scene['voiceSha256']
        start=round(scene['start']*48000);end=start+scene['frames']*800
        windows.append({'label':'whole-'+scene['id'],'scene':scene['id'],'fromSample':start,'toSample':end,
          'expectedKo':chapter['lines'],'independent':False,'padSamplesEachSide':0,
          'scope':'Entire current final-AAC chapter including pauses, every complete sentence and its ending.'})
        contexts=scene['cues'][-2:]
        windows.append({'label':'independent-complete-context-'+scene['id'],'scene':scene['id'],
          'fromSample':start+round(contexts[0]['start']*48000),'toSample':start+round(contexts[-1]['end']*48000),
          'expectedKo':[c['text'] for c in contexts],'independent':True,'padSamplesEachSide':28800,
          'scope':'Two connected complete narration paragraphs, independently decoded with0.6sec zero padding. Full earlier claims are checked in the entire chapter, not inferred from these endings.'})
    assert len(windows)==38 and sum(w['independent'] for w in windows)==19
    statefile=OUT/'current-whole-audio-asr-execution-v1.json';assert not statefile.exists() and not LOCAL.exists()
    for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
    os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    os.environ['PATH']=str(Path(FF).parent)+os.pathsep+os.environ.get('PATH','')
    if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
    import psutil
    p=psutil.Process();LOCAL.mkdir(parents=True)
    state={'startedAt':now(),'pid':p.pid,'createTime':p.create_time(),'commandLine':p.cmdline(),'cwd':str(ROOT),
      'resourceEvidence':args.resource,'cpuThreads':2,'gpuJobs':0,'status':'copy-current-whole-aac',
      'baselineSha256':sha(baseline),'timelineSha256':sha(timelinefile),'scriptSha256':sha(scriptfile),
      'whole':19,'independentCompleteContexts':19,'completed':0,'total':38,'exitCode':None,
      'expectedWasRecognizerPrompt':False,'automaticApproval':False,'currentWholeMixedAsrApproved':False,
      'humanListeningApproved':False,'publicRightsApproved':False,'researchControlChanges':0,'allFinalPixelsApproved':False}
    def save():
        state['observedAt']=now();statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save();print(json.dumps({'pid':p.pid,'createTime':p.create_time(),'total':38}),flush=True)
    try:
        aac=LOCAL/'current-whole-original-aac.m4a';wav=LOCAL/'current-whole-aac-decoded.wav'
        subprocess.run([FF,'-hide_banner','-nostdin','-v','error','-i',str(baseline),'-map','0:a:0','-c:a','copy','-vn',str(aac)],check=True)
        subprocess.run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(aac),'-c:a','pcm_s16le','-ar','48000','-ac','2',str(wav)],check=True)
        state.update(aac=rel(aac),aacSha256=sha(aac),wav=rel(wav),wavSha256=sha(wav),status='load-local-CPU2-model');save()
        with wave.open(str(wav),'rb') as w:
            params=w.getparams();assert (params.framerate,params.nchannels,params.sampwidth)==(48000,2,2)
            assert max(x['toSample'] for x in windows)<=params.nframes
        request=OUT/'current-whole-audio-asr-request-v1.json'
        request.write_text(json.dumps({'createdAt':now(),'aacSha256':state['aacSha256'],'wavSha256':state['wavSha256'],
          'windows':windows,'expectedWasRecognizerPrompt':False,'allDirectlyCompared':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        import torch
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
        transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        results=[]
        for window in windows:
            dest=LOCAL/(window['label']+'.wav')
            with wave.open(str(wav),'rb') as w:
                w.setpos(window['fromSample']);pcm=w.readframes(window['toSample']-window['fromSample'])
            assert len(pcm)==(window['toSample']-window['fromSample'])*4
            padded=bytes(window['padSamplesEachSide']*4)+pcm+bytes(window['padSamplesEachSide']*4)
            with wave.open(str(dest),'wb') as w:w.setparams(params);w.writeframes(padded)
            state.update(status='transcribing-current-AAC-'+window['label'],activeWindow=window['label']);save()
            raw=transcriber(str(dest),generate_kwargs={'language':'korean','task':'transcribe'},chunk_length_s=30,return_timestamps='word')
            row={**window,'windowPath':rel(dest),'windowSha256':sha(dest),'exactWholeAacPcmSlice':True,
              'mixPcmSliceSha256':hashlib.sha256(pcm).hexdigest(),'text':raw['text'],'words':raw['chunks'],
              'expectedWasRecognizerPrompt':False,'directlyCompared':False}
            results.append(row);(LOCAL/(window['label']+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            (LOCAL/'asr.json').write_text(json.dumps({'aacSha256':state['aacSha256'],'wavSha256':state['wavSha256'],'complete':len(results)==38,
              'results':results,'automaticApproval':False,'currentWholeMixedAsrApproved':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            state['completed']=len(results);save();print(json.dumps({'label':window['label'],'text':row['text']},ensure_ascii=False),flush=True)
        assert sha(baseline)==state['baselineSha256'] and sha(timelinefile)==state['timelineSha256'] and sha(scriptfile)==state['scriptSha256']
        assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
        state.update(status='completed-await-full-direct-comparison',exitCode=0,finishedAt=now(),activeWindow=None,protectedBaselineUnchanged=True);save()
    except Exception:
        state.update(status='failed',exitCode=1,finishedAt=now(),error=traceback.format_exc());save();raise
if __name__=='__main__':main()
