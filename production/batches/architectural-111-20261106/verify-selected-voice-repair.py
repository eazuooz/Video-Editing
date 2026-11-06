"""CPU synthetic WAV/contract checks. No real voice, staging, model or subprocess."""
import copy,hashlib,importlib.util,json,struct,tempfile,wave
from pathlib import Path

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('repair_fixture',HERE/'run-selected-voice-repair.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
checks=[]
def yes(v):
    if not v:raise AssertionError('Expected true')
def rejects(fn):
    try:fn()
    except (ValueError,RuntimeError,KeyError):return
    raise AssertionError('Expected rejection')
def check(name,fn):fn();checks.append(name)
def write_json(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return dict(path=str(p),sha256=m.sha(p))
def wav(p,value,n=48):
    p.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(p),'wb')as w:w.setparams((1,2,24000,n,'NONE','not compressed'));w.writeframes(struct.pack('<h',value)*n)
    return m.base.wav_info(p)

with tempfile.TemporaryDirectory(prefix='yamyam-subset-repair-cpu-')as temp:
    root=Path(temp);original_root=m.ROOT;m.ROOT=root
    try:
        oldfp='a'*64;newfp='b'*64;oldout=root/'shared/output/architectural-111-20261106/07-04/voice-attempts'/oldfp[:24]
        olds=[];oldw=[]
        for p in range(1,8):
            for c in range(1,3):
                sid=f'p{p:03d}-c{c:02d}';text=f'old spoken clause {p} {c}.';olds.append(dict(id=sid,lines=[text]));oldw.append(wav(oldout/'chunks'/(sid+'-scene.wav'),p*100+c))
        profile=dict(tts=dict(language='Korean',speechSpeed=1),modelPins=[dict(path='model',sha256='1'*64)],referenceSHA256='2'*64,referenceTextSHA256='3'*64,engine=dict(path='approved-engine',sha256='4'*64),guard=dict(path='approved-guard',sha256='5'*64),rawPcmPolicy=dict(speechSpeed=1,timeStretch=False))
        old=write_json(root/'immutable-old-proof.json',dict(topicId='07.04',fingerprint=oldfp,identity=dict(profile,scenes=olds),sceneWavs=oldw,output=str(oldout)))
        scenes=[]
        for p,count in enumerate([4,5,4,6,4,5,5],1):
            for c in range(1,count+1):
                sid=f'p{p:03d}-c{c:02d}';text=next(s['lines'][0]for s in olds if s['id']==sid)if sid=='p003-c01'else f'new short clause {p} {c}.'
                scenes.append(dict(id=sid,title='synthetic',lines=[text]))
        source=next(w for s,w in zip(olds,oldw)if s['id']=='p003-c01');narrsha='c'*64
        row=dict(oldSceneId='p003-c01',newSceneId='p003-c01',canonicalText=next(s['lines'][0]for s in scenes if s['id']=='p003-c01'),sourceWav=source,sourceVoiceEvidence=dict(old,fingerprint=oldfp),reuseReason='Root selected one prior clean-tail raw take',sourceMapping=dict(paragraph=3,oldComponent=1,newComponent=1))
        plan=dict(topicId='07.04',sourceNarrationSHA256=narrsha,oldVoiceEvidence=old,oldAsrReview=write_json(root/'old-asr.json',dict(voiceFingerprint=oldfp)),oldLevelReview=write_json(root/'old-levels.json',dict(voiceFingerprint=oldfp)),subsetReuse=[row]);planpath=root/'plan.json';write_json(planpath,plan)
        out=root/'new-output';stage=root/'projects/shorts-leveldesign-07-04/production/voice-preparation/stage'
        identity=dict(profile,scenes=[dict(id=s['id'],lines=s['lines'])for s in scenes]);prov=dict(topicId='07.04',slug='shorts-leveldesign-07-04',fingerprint=newfp,identity=identity,manifest=dict(slug='shorts-leveldesign-07-04',sourceNarrationSHA256=narrsha,paths=dict(script='full.json'),tts=dict(model='approved-model',reference='approved-reference',outputDir='new-output'),editing=dict(exampleSeconds=0),rawPcmPolicy=profile['rawPcmPolicy']),script=dict(scenes=scenes),stagingDirectory=str(stage),qwenSynthesisArgv=['python','-u','-X','utf8','render_narration.py','--project','shorts-leveldesign-07-04','--manifest','full.json','--batch-size','1','--device','cuda:0'],paragraphMapping=[dict(paragraph=int(s['id'][1:4]),sceneId=s['id'],canonicalText=s['lines'][0])for s in scenes])
        repair=m.repair_spec(prov,plan,planpath);prov['repair']=repair
        check('full33 and only32missing derived without fixed scene count',lambda:yes(len(scenes)==33 and len(repair['missing'])==32 and len(repair['rows'])==1))
        check('accepted raw p003c01 excluded from trusted engine subset',lambda:yes('p003-c01'not in[s['id']for s in repair['script']['scenes']]))
        check('subset keeps exact full-script order excluding accepted raw',lambda:yes([s['id']for s in repair['script']['scenes']]==[s['id']for s in scenes if s['id']!='p003-c01']))
        check('subset retains same approved voice model/reference/output profile',lambda:yes(repair['manifest']['tts']==prov['manifest']['tts']))
        check('only manifest argument changes in trusted command',lambda:yes(repair['command'][:8]==prov['qwenSynthesisArgv'][:8]and repair['command'][9:]==prov['qwenSynthesisArgv'][9:]))
        wrong=copy.deepcopy(plan);wrong['subsetReuse'][0]['canonicalText']+=' rewritten'
        check('reused canonical text rewrite rejected',lambda:rejects(lambda:m.validate_reuse(prov,wrong)))
        wrong=copy.deepcopy(plan);wrong['subsetReuse'][0]['sourceWav']['pcmSHA256']='d'*64
        check('wrong prior raw PCM hash rejected',lambda:rejects(lambda:m.validate_reuse(prov,wrong)))
        wrong=copy.deepcopy(plan);wrong['subsetReuse'][0]['oldSceneId']='p006-c01';wrong['subsetReuse'][0]['newSceneId']='p006-c01'
        check('prior nonclean-tail candidate cannot reenter reuse list',lambda:rejects(lambda:m.validate_reuse(prov,wrong)))
        wrong=copy.deepcopy(plan);wrong['subsetReuse'].append(copy.deepcopy(row))
        check('duplicate raw reuse mapping rejected',lambda:rejects(lambda:m.validate_reuse(prov,wrong)))
        original_text=next(s['lines'][0]for s in prov['identity']['scenes']if s['id']=='p003-c01')
        changed=copy.deepcopy(prov);next(s for s in changed['identity']['scenes']if s['id']=='p003-c01')['lines']=['different']
        check('new version may not reuse old speech for different text',lambda:rejects(lambda:m.validate_reuse(changed,plan)))
        changed=copy.deepcopy(prov);changed['identity']['referenceSHA256']='6'*64
        check('old raw voice from a different approved-reference identity rejected',lambda:rejects(lambda:m.validate_reuse(changed,plan)))
        for name,obj in [('narration-missing-only.json',repair['script']),('voice-missing-only-manifest.json',repair['manifest']),('subset-repair-preparation.json',dict(repairFingerprint=repair['fingerprint'],fullVoiceFingerprint=prov['fingerprint'],repairIdentity=repair['identity'],command=repair['command']))]:write_json(Path(repair['stagingDirectory'])/name,obj)
        (Path(repair['stagingDirectory'])/'repair-adapter-source.py').write_bytes(Path(m.__file__).read_bytes())
        attempt=out/'engine-attempts/synthetic';attempt.mkdir(parents=True)
        req=dict(protocol=m.base.PROTOCOL,fingerprint=prov['fingerprint'],identity=prov['identity'],repairFingerprint=repair['fingerprint'],command=repair['command'],engineSceneScope='missing-subset-only',engineSceneIds=[s['id']for s in repair['missing']],subsetPins=m.subset_pins(prov))
        reqpin=write_json(attempt/'request.json',req);pending=dict(attempt=str(attempt),requestPins=[reqpin])
        check('pending immutable request transitively pins subset script/profile/source',lambda:yes(m.validate_launch_request(prov,out,pending)==attempt))
        badreq=copy.deepcopy(req);badreq['command'][8]='full-script-manifest.json';badpin=write_json(attempt/'request.json',badreq)
        check('pending request cannot switch engine back to full scene list',lambda:rejects(lambda:m.validate_launch_request(prov,out,dict(pending,requestPins=[badpin]))))
        reqpin=write_json(attempt/'request.json',req);pending['requestPins']=[reqpin]
        metadata=copy.deepcopy(prov);metadata['repair']['command'][8]='projects/shorts-leveldesign-07-04/production/voice-preparation/metadata-only-new/manifest.json';metadata['repair']['stagingDirectory']=str(stage/'metadata-only-new')
        check('metadata-only new preparation folder reuses exact pinned prior subset request',lambda:yes(m.validate_launch_request(metadata,out,pending)==attempt))
        adapter_path=Path(repair['stagingDirectory'])/'repair-adapter-source.py';adapter_bytes=adapter_path.read_bytes();adapter_path.write_bytes(b'different adapter snapshot')
        changed_req=copy.deepcopy(req);changed_req['subsetPins']=m.subset_pins(prov);changed_reqpin=write_json(attempt/'request.json',changed_req)
        check('changed adapter bytes rejected even with matching transitive outer pins',lambda:rejects(lambda:m.validate_launch_request(prov,out,dict(pending,requestPins=[changed_reqpin]))))
        adapter_path.write_bytes(adapter_bytes);reqpin=write_json(attempt/'request.json',req);pending['requestPins']=[reqpin]
        subset_manifest=Path(repair['stagingDirectory'])/'voice-missing-only-manifest.json';original_manifest=subset_manifest.read_bytes();badmanifest=copy.deepcopy(repair['manifest']);badmanifest['tts']['reference']='different-reference';write_json(subset_manifest,badmanifest)
        check('changed subset reference/profile rejected on recovery',lambda:rejects(lambda:m.validate_launch_request(prov,out,pending)))
        subset_manifest.write_bytes(original_manifest)
        for i,s in enumerate(scenes):
            p=out/'chunks'/(s['id']+'-scene.wav')
            if s['id']=='p003-c01':m.base.immutable(p,Path(source['path']).read_bytes())
            else:wav(p,500+i,n=48+i)
        missing=repair['missing'];pos=0;entries=[];payload=[]
        for s in missing:
            p=out/'chunks'/(s['id']+'-scene.wav');info=m.base.wav_info(p)
            with wave.open(str(p),'rb')as w:payload.append(w.readframes(w.getnframes()))
            entries.append(dict(scene_id=s['id'],text=s['lines'][0],start=pos/24000,end=(pos+info['frames'])/24000));pos+=info['frames']
        aggregate=out/'narration.wav'
        with wave.open(str(aggregate),'wb')as w:w.setparams((1,2,24000,pos,'NONE','not compressed'));w.writeframes(b''.join(payload))
        write_json(out/'narration.timing.json',dict(render_mode='scene',sample_rate=24000,duration_seconds=pos/24000,entries=entries));(out/'narration.srt').write_text('1\n00:00:00,000 --> 00:00:00,100\nsubset\n',encoding='utf8')
        chunks,engine=m.validate_engine_outputs(prov,out)
        check('engine aggregate/timing validate missing32 only not combined33',lambda:yes(engine['engineSceneCount']==32 and engine['fullCanonicalSceneCount']==33 and engine['engineSceneIds']==[s['id']for s in missing]))
        proof=m.canonical_outputs(prov,out,engine)
        allpcm=[]
        for s in scenes:
            with wave.open(str(out/'chunks'/(s['id']+'-scene.wav')),'rb')as w:allpcm.append(w.readframes(w.getnframes()))
        check('full canonical PCM exactly concatenates accepted plus newly generated raw in full order',lambda:yes(proof['aggregateWav']['pcmSHA256']==hashlib.sha256(b''.join(allpcm)).hexdigest()))
        check('full proof truthfully records subset engine did not speak combined script',lambda:yes(proof['engineSpokeFullCombinedScript']is False and proof['rawSceneCount']==33 and len(proof['reusedRawScenes'])==1))
        check('accepted raw copied with exact WAV identity',lambda:yes(m.sha(out/'chunks/p003-c01-scene.wav')==source['sha256']))
        check('interrupted subset without valid aggregate cannot forge full completion',lambda:rejects(lambda:m.canonical_outputs(prov,out,dict(incompleteEngineOutputsAtInterruption=True))))
        badtiming=read_timing=copy.deepcopy(m.read(out/'narration.timing.json'));badtiming['entries'].insert(0,dict(scene_id='p003-c01',text=original_text,start=0,end=.001));write_json(out/'narration.timing.json',badtiming)
        check('engine aggregate including accepted raw is rejected',lambda:rejects(lambda:m.validate_engine_outputs(prov,out)))
        check('completion remains independent-ASR/listening pending',lambda:yes(proof['independentAsrVerified']is False and proof['actualListening']is False and proof['humanApproval']is False))
    finally:m.ROOT=original_root
print(json.dumps(dict(passed=len(checks),checks=checks,syntheticWavOnly=True,realVoiceRead=False,actualStageOrReuseCopy=False,externalProgramsStarted=False,modelStarted=False,gpuLeaseMutated=False),ensure_ascii=False))
