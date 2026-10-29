"""Selective v4 narration: five new takes, fourteen exact baseline PCM slices.

Default is CPU-only --dry-run. --synthesize needs the coordinator's current GPU
signal. All outputs are additive under audio-v4; audio-v1 is read-only.
"""
from __future__ import annotations
import argparse
import atexit
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[3]
PROJECT=Path(__file__).resolve().parents[1]
SLUG=PROJECT.name
BASE=PROJECT/'production/local/audio-v1'
OUT=PROJECT/'production/local/audio-v4'
PLAN=PROJECT/'planning/revision-v4-workflow.json'
KO=PROJECT/'script/revision-v4/narration.ko.json'
EN=PROJECT/'script/revision-v4/narration.en.json'
LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
BASE_SHA='cde1c69a5bf1f841f52f1195a288c563e258f53f21fc3b5528a9a7aeb2c8c520'

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def pcm_hash(samples):return hashlib.sha256(samples.astype('<f4',copy=False).tobytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def key(scene,paragraph):return f'{scene}-{int(paragraph):02}'
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def resource_guard(allow_idle_editors):
    """Selected v4 resource check; no app changes, model load, or old outputs.

    Root authorized the measured previous peak + allocator-cap margin decision.
    Visible Visual Studio is allowed only by exact installed path and Microsoft
    signature; the remainder retains the established WDDM/Unity classification.
    """
    import psutil
    old_path=PROJECT/'production/render-voice.py'
    old=load_module('buckshot_v1_resource_helpers',old_path)
    if LEASE.exists():raise RuntimeError('Existing GPU lease preserved; wait for the current owner.')
    history_path=BASE/'tts-gpu-coordination.json';history=read(history_path)
    if history.get('state')!='finished' or history.get('exitCode')!=0 or not history.get('generations'):
        raise ValueError('Previous successful same-voice GPU measurements are required.')
    previous_peak=max(g['peakAllocatedMiB'] for g in history['generations'])
    allocator_cap=7680
    if previous_peak>=allocator_cap:raise ValueError('Previous peak does not fit the selected allocator cap.')
    me=psutil.Process();family={p.pid for p in [me,*me.parents()]}
    baseline=[];blocked=[];names={};permitted_gui=set();verified_gui=[]
    gui_allow={'explorer.exe','chrome.exe','msedge.exe','msedgewebview2.exe','shellhost.exe','shellexperiencehost.exe',
               'searchhost.exe','startmenuexperiencehost.exe','applicationframehost.exe','textinputhost.exe','runtimebroker.exe',
               'dwm.exe','codex.exe','steam.exe','steamwebhelper.exe','obs64.exe','discord.exe','nvidia overlay.exe','nvidia share.exe',
               'windowsterminal.exe','crossdeviceresume.exe','phoneexperiencehost.exe','mmgaserver.exe','systemsettings.exe',
               'microsoftsecurityapp.exe','snippingtool.exe','edgegameassist.exe','chatgpt.exe','codex-computer-use-swift.exe',
               'codex-computer-use.exe','radeonsoftware.exe','amdrssrcext.exe','logioptionsplus_agent.exe','icue.exe','parsecd.exe',
               'razerappengine.exe','razer synapse.exe','battle.net.exe','icloudhome.exe','icloudphotos.exe','unity hub.exe',
               'claude.exe','onedrive.exe','obs-browser-page.exe'}
    signed_gui={
        'devenv.exe':('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/IDE/devenv.exe','CN=Microsoft Corporation,'),
        'notion.exe':('C:/Users/1/AppData/Local/Programs/Notion/Notion.exe','CN="Notion Labs, Inc.",'),
    }
    signatures={}
    for proc in psutil.process_iter(['pid','name','exe','cmdline']):
        info=proc.info;pid=info['pid']
        if pid in family:continue
        name=(info['name'] or '').lower();exe=(info['exe'] or '').replace('\\','/').lower()
        names[pid]=name;arguments=[str(a).lower() for a in info.get('cmdline') or []]
        hub=name=='unity.exe' and exe.endswith('/unity hub/resources/unity.exe') and 'serve' in arguments
        imported=allow_idle_editors and old.unity_import_worker(info,proc)
        editor=not hub and (name in ['unity.exe','unrealeditor.exe','blender.exe'] or name.startswith('godot'))
        batch=[flag for flag in ['--write-movie','--headless','--background','-b','-batchmode','-moviepipeline','-render','--render']
               if any(a==flag or (flag=='-moviepipeline' and a.startswith(flag)) or (flag=='-render' and a.startswith('-renderoffscreen')) for a in arguments)]
        game=name in ['buckshot roulette.exe','buckshot roulette_windows.exe','monsterhunterwilds.exe','d2r.exe','diablo ii.exe']
        compute=name.startswith(('python','ffmpeg'))
        reason='actual-game' if game else 'foreign-compute-process' if compute else 'editor-background-render' if editor and batch and not imported else 'editor-not-explicitly-allowed' if editor and not allow_idle_editors else None
        if reason:blocked.append({'pid':pid,'name':name,'reason':reason,'batchFlags':batch})
        if editor or game or compute:baseline.append({'pid':pid,'name':name,'editor':editor,'batchFlags':batch,'verifiedUnityImportWorker':imported,'disposition':reason or 'preserved-visible-editor'})
        if hub or imported or (editor and allow_idle_editors and not batch):permitted_gui.add(pid)
        if allow_idle_editors and name in signed_gui and exe==signed_gui[name][0].lower():
            gui_path,expected_signer=signed_gui[name]
            if name not in signatures:
                command="$s=Get-AuthenticodeSignature -LiteralPath '"+gui_path+"'; [pscustomobject]@{status=$s.Status.ToString();signer=$s.SignerCertificate.Subject}|ConvertTo-Json -Compress"
                signatures[name]=json.loads(subprocess.check_output(['pwsh.exe','-NoProfile','-NonInteractive','-Command',command],text=True,creationflags=old.CREATE_NO_WINDOW))
            signature=signatures[name]
            if signature.get('status')=='Valid' and expected_signer in signature.get('signer',''):
                permitted_gui.add(pid);verified_gui.append({'pid':pid,'path':gui_path,'signature':signature})
    if blocked:raise RuntimeError(('Foreign game/compute/render processes preserved',blocked))
    observed=[];foreign=[]
    for line in old.command_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader']).splitlines():
        if not line.strip() or not line.split(',')[0].strip().isdigit():continue
        pid=int(line.split(',')[0])
        if pid in family:continue
        name=names.get(pid,Path(line.split(',',1)[1].strip()).name.lower())
        allowed=allow_idle_editors and (pid in permitted_gui or name in gui_allow)
        observed.append({'pid':pid,'name':name,'classification':'verified-GUI-preserved' if allowed else 'unclassified-foreign-GPU-process'})
        if not allowed:foreign.append({'pid':pid,'name':name})
    if foreign:raise RuntimeError(('Unclassified GPU processes preserved',foreign))
    samples=[]
    for i in range(3):
        free,total,util=[int(v.strip()) for v in old.command_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits']).splitlines()[0].split(',')]
        samples.append({'freeMiB':free,'totalMiB':total,'utilization':util})
        if i<2:time.sleep(1)
    minimum_free=max(allocator_cap+700,previous_peak+700)
    maximum_util=40 if allow_idle_editors else 14
    if not all(s['freeMiB']>=minimum_free and s['utilization']<=maximum_util for s in samples):
        raise RuntimeError(('Insufficient actual GPU margin; all apps preserved',samples))
    return {'status':'resource-preflight-passed-no-synthesis','checkedAt':now(),'project':SLUG,
            'allowIdleEditors':allow_idle_editors,'baselineProcesses':baseline,'observedGpuRows':observed,'gpuSamples':samples,
            'allocatorCapMiB':allocator_cap,'totalMiB':total,'guardHelperSha256':digest(old_path),'verifiedSignedGui':verified_gui,
            'selectedProjectDecision':{'previousSuccessfulTakes':len(history['generations']),'previousMaxAllocatedMiB':previous_peak,
                'previousReceiptSha256':digest(history_path),'minimumFreeMiB':minimum_free,'maxUtilization':maximum_util,
                'basis':'Root-authorized v4 measured-capacity choice: same1.7Bvoice/reference; max7.5GiBallocator+700MiBfree margin, plus actual3samplecheck; no foreign process changes.'},
            'gpuModelLoaded':False,'gpuLeaseCreated':False,'foreignProcessesChanged':False}

def inputs():
    import numpy as np
    import soundfile as sf
    for path in (PLAN,KO,EN,BASE/'narration.wav',BASE/'narration.timing.json'):
        if not path.is_file():raise FileNotFoundError(path)
    workflow,ko,en=read(PLAN),read(KO),read(EN)
    baseline=read(BASE/'narration.timing.json')
    if digest(BASE/'narration.wav')!=BASE_SHA:raise ValueError('Baseline PCM file changed; preserve and inspect it.')
    if ko['slug']!=SLUG or en['slug']!=SLUG:raise ValueError('Selected-project script mismatch')
    if [(s['id'],len(s['lines'])) for s in ko['scenes']] != [(s['id'],len(s['lines'])) for s in en['scenes']]:
        raise ValueError('KO/EN paragraph structure mismatch')
    mapping=workflow['audioReuseMapping']
    by_new={key(m['scene'],m['paragraph']):m for m in mapping}
    if len(by_new)!=len(mapping):raise ValueError('Duplicate new paragraph mapping')
    old={key(e['scene_id'],e['paragraph']):(i,e) for i,e in enumerate(baseline['entries'])}
    pcm,sr=sf.read(BASE/'narration.wav',dtype='float32',always_2d=True)
    if sr!=24000 or pcm.shape[1]!=1 or sf.info(BASE/'narration.wav').subtype!='FLOAT' or not np.isfinite(pcm).all():
        raise ValueError('Expected finite mono24000HzFLOAT baseline')
    rows=[]
    for scene,en_scene in zip(ko['scenes'],en['scenes']):
        for n,(text,translated) in enumerate(zip(scene['lines'],en_scene['lines']),1):
            ident=key(scene['id'],n);item=by_new[ident]
            row={'id':ident,'scene':scene['id'],'paragraph':n,'title':scene['title'],
                 'text':text,'displayText':scene.get('displayLines',scene['lines'])[n-1],
                 'textEn':translated,'mode':item['mode']}
            if item['mode']=='reuse':
                old_key=key(item['baselineScene'],item['baselineParagraph']);index,entry=old[old_key]
                if text!=entry['text'] or translated!=entry['text_en']:
                    raise ValueError('Changed text cannot silently reuse an old take: '+ident)
                start=round(entry['start']*sr);end=round(entry['end']*sr)
                next_start=round(baseline['entries'][index+1]['start']*sr) if index+1<len(baseline['entries']) else len(pcm)
                if not 0<=start<end<=next_start<=len(pcm):raise ValueError('Invalid baseline sample interval')
                row.update(baselineId=old_key,baselineStartSample=start,baselineSpeechEndSample=end,
                           baselineEndSample=next_start,baselinePcmSha256=pcm_hash(pcm[start:next_start]),
                           speechSamples=end-start,segmentSamples=next_start-start)
            elif item['mode']!='synthesize':raise ValueError('Unknown synthesis mode: '+item['mode'])
            rows.append(row)
    if set(by_new)!={r['id'] for r in rows}:raise ValueError('Unused/absent paragraph mappings')
    new=[r for r in rows if r['mode']=='synthesize'];reused=[r for r in rows if r['mode']=='reuse']
    if len(rows)!=19 or len(new)!=5 or len(reused)!=14:raise ValueError('Expected the root-selected19=5new+14retained plan')
    if [r['id'] for r in new]!=['01-01','01-02','02-01','02-02','08-01']:
        raise ValueError('New takes exceed the selected intro/REA/closing scope')
    expected=[key(e['scene_id'],e['paragraph']) for e in baseline['entries'] if e['scene_id'] in ['02','03','04','05','06','07']]
    if [r['baselineId'] for r in reused]!=expected:raise ValueError('Retained body order changed')
    if any(a['baselineEndSample']!=b['baselineStartSample'] for a,b in zip(reused,reused[1:])):
        raise ValueError('Retained paragraphs are not one exact contiguous baseline block')
    manifest=read(PROJECT/'production/tts-manifest.json')
    frozen=read(BASE/'render-inputs.json')['sha256']
    for field in ['reference','referenceText']:
        if digest(ROOT/manifest['tts'][field])!=frozen[field]:raise ValueError('Voice identity input changed: '+field)
    model=ROOT/manifest['tts']['model']
    if not model.is_dir():raise FileNotFoundError(model)
    fingerprint={'baselineWav':BASE_SHA,'baselineTiming':digest(BASE/'narration.timing.json'),
                 'koScript':digest(KO),'enScript':digest(EN),'workflow':digest(PLAN),
                 'sourceManifest':digest(PROJECT/'production/tts-manifest.json'),
                 'reference':frozen['reference'],'referenceText':frozen['referenceText'],
                 'runner':digest(Path(__file__))}
    block={'startSample':reused[0]['baselineStartSample'],'endSampleExclusive':reused[-1]['baselineEndSample']}
    block.update(samples=block['endSampleExclusive']-block['startSample'],
                 sha256=pcm_hash(pcm[block['startSample']:block['endSampleExclusive']]))
    return rows,pcm,sr,manifest,fingerprint,block

def prepare_subset(rows,manifest,fingerprint):
    target=OUT/'render-inputs.json'
    if target.exists() and read(target)['sha256']!=fingerprint:
        raise ValueError('audio-v4 inputs changed; preserve this revision and choose a new one.')
    save(target,{'sha256':fingerprint,'baselineReadOnly':True,'mode':'5new14exactPCM'})
    script={'slug':SLUG,'scenes':[{'id':r['id'],'title':r['title'],'lines':[r['text']]} for r in rows if r['mode']=='synthesize']}
    script_path=OUT/'new-takes/narration.lines.ko.json';save(script_path,script)
    subset=copy.deepcopy(manifest)
    subset['paths']['script']=script_path.relative_to(ROOT).as_posix()
    subset['paths']['scriptEn']=EN.relative_to(ROOT).as_posix()
    subset['tts']['outputDir']=(OUT/'new-takes').relative_to(ROOT).as_posix()
    subset['tts']['renderMode']='scene'
    subset_path=OUT/'new-takes/render-manifest.json';save(subset_path,subset)
    sys.path.insert(0,str(ROOT/'qwen3-tts'))
    import render_narration as worker
    worker.configure_project(SLUG,subset_path.relative_to(ROOT).as_posix())
    items=worker.build_render_items(worker.load_jobs())
    if len(items)!=5:raise ValueError('Only the five new paragraphs may enter the synthesis queue')
    return worker,items

def synthesize(worker,items,resources):
    import psutil
    import soundfile as sf
    pending=[]
    for item in items:
        if not item.path.exists():pending.append(item)
        elif sf.info(item.path).frames<=0:raise ValueError('Invalid existing new take preserved: '+str(item.path))
    if not pending:return
    if LEASE.exists():raise RuntimeError('Existing GPU lease preserved; wait for its owner')
    me=psutil.Process();token=str(uuid.uuid4())
    state={'schemaVersion':1,'project':SLUG,'token':token,'state':'gpu_granted_to_tts',
           'coordinator':{'pid':me.pid,'createTime':me.create_time()},'startedAt':time.time(),
           'rootExplicitInvocation':'render-voice-v4.py --synthesize','foreignProcessesPaused':[],
           'resources':resources,'requestedNewParagraphs':[item.key for item in pending],'generations':[]}
    LEASE.parent.mkdir(parents=True,exist_ok=True)
    with LEASE.open('x',encoding='utf-8') as handle:json.dump(state,handle,ensure_ascii=False,indent=2)
    receipt=OUT/'tts-gpu-coordination.json';save(receipt,state)
    def release():
        if LEASE.exists() and read(LEASE).get('token')==token:LEASE.unlink()
    atexit.register(release)
    try:
        os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
        import torch
        torch.cuda.set_per_process_memory_fraction(resources['allocatorCapMiB']/resources['totalMiB'],0)
        worker.load_tts_dependencies()
        generate=worker.Qwen3TTSModel.generate_voice_clone
        def measured(model,*args,**kwargs):
            torch.cuda.reset_peak_memory_stats();result=generate(model,*args,**kwargs)
            state['generations'].append({'at':time.time(),'peakAllocatedMiB':round(torch.cuda.max_memory_allocated()/2**20)})
            save(receipt,state);return result
        worker.Qwen3TTSModel.generate_voice_clone=measured
        # Only missing v4 new takes are passed. Existing approved/raw takes never
        # enter the worker's tail-heuristic rerender path.
        worker.render_chunks(pending,1,set())
        state.update(state='finished',exitCode=0,finishedAt=time.time())
    except BaseException as error:
        state.update(state='failed',error=repr(error),finishedAt=time.time());raise
    finally:
        save(receipt,state)
        # CUDA objects may remain alive until exit; release only at atexit.

def write_new_wav(path,samples,sr):
    import soundfile as sf
    if path.exists():raise FileExistsError('Existing assembled output preserved: '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.stem+'.temporary-'+uuid.uuid4().hex+path.suffix)
    try:
        sf.write(temporary,samples,sr,subtype='FLOAT')
        temporary.rename(path)
    finally:
        if temporary.exists():temporary.unlink()

def assemble(rows,baseline,sr,manifest,fingerprint,block):
    import numpy as np
    import soundfile as sf
    if (OUT/'narration.wav').exists():raise FileExistsError('audio-v4 narration already exists; inspect rather than overwrite')
    eq=manifest['tts']['lineLevelEqualization'];new_levels=[];pieces=[];entries=[];cursor=0
    def median_level(samples):
        length=round(sr*eq['frameMs']/1000)
        if len(samples)<length:raise ValueError('Too-short new take')
        windows=samples[:len(samples)//length*length].reshape(-1,length)
        db=20*np.log10(np.maximum(np.sqrt(np.mean(windows*windows,axis=1)),1e-10))
        active=db[db>=db.max()-eq['gateBelowPeakDb']]
        return float(np.median(active))
    for index,row in enumerate(rows):
        if row['mode']=='reuse':
            segment=baseline[row['baselineStartSample']:row['baselineEndSample']].copy()
            speech_samples=row['speechSamples']
            if pcm_hash(segment)!=row['baselinePcmSha256']:raise ValueError('Unexpected reused PCM mutation')
        else:
            raw=OUT/'new-takes/chunks'/f'{row["id"]}-scene.wav'
            samples,rate=sf.read(raw,dtype='float32',always_2d=True)
            if rate!=sr or samples.shape[1]!=1 or not len(samples) or not np.isfinite(samples).all():
                raise ValueError('Invalid/mismatched new take: '+str(raw))
            mono=samples[:,0];before=median_level(mono)
            gain=max(-eq['maxGainDb'],min(eq['maxGainDb'],eq['targetSpeechFrameMedianDbfs']-before))
            mono=mono*np.float32(10**(gain/20))
            fade=min(round(sr*manifest['tts']['edgeFadeSeconds']),len(mono)//2)
            if fade>1:
                ramp=np.linspace(0,1,fade,dtype=np.float32);mono[:fade]*=ramp;mono[-fade:]*=ramp[::-1]
            speech_samples=len(mono)
            gap=0 if index==len(rows)-1 else manifest['tts']['lineGapSeconds'] if rows[index+1]['scene']==row['scene'] else manifest['tts']['sceneGapSeconds']
            segment=np.concatenate([mono,np.zeros(round(sr*gap),dtype=np.float32)])[:,None]
            new_levels.append({'id':row['id'],'rawSha256':digest(raw),'beforeMedianDbfs':before,'gainDb':gain,
                               'afterMedianDbfs':median_level(mono),'peak':float(np.abs(mono).max()),
                               'samples':speech_samples,'pcmSha256':pcm_hash(mono),'integerClippingApplied':False})
        entry={'index':index+1,'scene_id':row['scene'],'scene_title':row['title'],'paragraph':row['paragraph'],
               'text':row['text'],'display_text':row['displayText'],'text_en':row['textEn'],
               'start':cursor/sr,'end':(cursor+speech_samples)/sr,'startSample':cursor,
               'endSample':cursor+speech_samples,'segmentEndSample':cursor+len(segment),
               'mode':row['mode'],'segmentPcmSha256':pcm_hash(segment)}
        if row['mode']=='reuse':
            entry['reuse']={name:row[name] for name in ['baselineId','baselineStartSample','baselineSpeechEndSample','baselineEndSample','baselinePcmSha256']}
        pieces.append(segment);entries.append(entry);cursor+=len(segment)
    full=np.concatenate(pieces,axis=0)
    reused=[e for e in entries if e['mode']=='reuse']
    new_start=reused[0]['startSample'];new_end=reused[-1]['segmentEndSample']
    if not np.array_equal(full[new_start:new_end],baseline[block['startSample']:block['endSampleExclusive']]):
        raise ValueError('Whole retained middle PCM block differs from baseline')
    write_new_wav(OUT/'narration.wav',full,sr)
    proof={'createdAt':now(),'baselineAudioSha256':BASE_SHA,'inputHashes':fingerprint,
           'newParagraphs':5,'reusedParagraphs':14,'baselineBlock':block,
           'newBlockStartSample':new_start,'newBlockEndSampleExclusive':new_end,
           'newPrefixSeconds':new_start/sr,'newClosingStartSeconds':new_end/sr,
           'reusedPcmBitExact':True,'reusedPcmResampled':False,'reusedPcmNormalized':False,
           'reusedPcmFaded':False,'reusedBreathingSamplesPreserved':True,'voiceSha256':digest(OUT/'narration.wav'),
           'finalSampleCount':len(full),'sampleRate':sr,'channels':1,'format':'FLOAT',
           'humanListening':False,'newSpeechReview':'pending','wholeCurrentAsr':'pending','finalMixReview':'pending'}
    for sid in dict.fromkeys(e['scene_id'] for e in entries):
        selected=[e for e in entries if e['scene_id']==sid]
        write_new_wav(OUT/'scenes'/f'{sid}.wav',full[selected[0]['startSample']:selected[-1]['endSample']],sr)
    save(OUT/'narration.timing.json',{'sample_rate':sr,'duration_seconds':len(full)/sr,'render_mode':'five-new-plus-fourteen-exact-baseline-PCM',
                                   'narration_placement':'continuous-across-all-three-segments','entries':entries,'paceListening':'pending'})
    save(OUT/'line-levels-new-only.json',{'equalization':eq,'newLines':new_levels,'reusedBodyProcessing':'none','floatHeadroomPreserved':True})
    def stamp(seconds):
        n=round(seconds*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
    for name,field in [('narration.srt','display_text'),('narration.en.srt','text_en')]:
        (OUT/name).write_text('\n\n'.join(f'{e["index"]}\n{stamp(e["start"])} --> {stamp(e["end"])}\n{e[field]}' for e in entries)+'\n',encoding='utf-8')
    # Read the written FLOAT file back: verify actual stored samples, not only the
    # assembly's in-memory intent, including values above nominal full scale.
    decoded,rate=sf.read(OUT/'narration.wav',dtype='float32',always_2d=True)
    if rate!=sr or not np.array_equal(decoded,full):raise ValueError('Stored FLOAT PCM changed')
    if digest(BASE/'narration.wav')!=BASE_SHA:raise ValueError('Baseline file changed during generation; inspect external work')
    proof['storedPcmVerified']=True;save(OUT/'pcm-reuse-proof.json',proof)
    return proof

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--dry-run',action='store_true')
    group.add_argument('--check-resources',action='store_true')
    group.add_argument('--synthesize',action='store_true')
    group.add_argument('--assemble-only',action='store_true',help='CPU-only; requires all five v4 takes already present')
    parser.add_argument('--allow-idle-editors',action='store_true')
    args=parser.parse_args()
    rows,baseline,sr,manifest,fingerprint,block=inputs()
    auth=read(ROOT/'shared/publishing/video-production-control.json')['scopedSetupAuthorizations'][SLUG]
    if auth.get('productionAllowedNow') is not True:raise ValueError('Selected project start not authorized')
    if not(args.synthesize or args.assemble_only or args.check_resources):
        print(json.dumps({'status':'dry-run-passed-no-writes-no-GPU','paragraphs':len(rows),'newTakes':[r['id'] for r in rows if r['mode']=='synthesize'],
                          'reusedParagraphs':14,'baselineBlock':block,'baselineBlockSeconds':block['samples']/sr,
                          'newPrefixSeconds':'known after four new takes are generated','sampleRate':sr,'inputHashes':fingerprint},ensure_ascii=False));return
    resources=None
    if args.synthesize or args.check_resources:
        resources=resource_guard(args.allow_idle_editors)
        save(OUT/'resource-preflight.json',resources)
    if args.check_resources:
        print(json.dumps(resources,ensure_ascii=False));return
    if (OUT/'narration.wav').exists():raise FileExistsError('Existing v4 narration preserved; inspect it before any rerun')
    worker,items=prepare_subset(rows,manifest,fingerprint)
    if args.synthesize:synthesize(worker,items,resources)
    elif any(not item.path.is_file() for item in items):raise ValueError('Missing new takes; --assemble-only never synthesizes')
    proof=assemble(rows,baseline,sr,manifest,fingerprint,block)
    print(json.dumps({'status':'assembled-awaiting-new-speech-and-full-mix-review','seconds':proof['finalSampleCount']/sr,
                      'newPrefixSeconds':proof['newPrefixSeconds'],'reusedPcmBitExact':proof['reusedPcmBitExact'],
                      'baselineBlock':block,'voiceSha256':proof['voiceSha256']},ensure_ascii=False))

if __name__=='__main__':main()
