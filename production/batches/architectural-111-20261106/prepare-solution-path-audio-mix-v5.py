"""Immutable 11.05 CPU mix producer. Default readiness; only --execute writes.

Requires complete current blind ASR, word/join numerical review and bound
component dispositions. Raw PCM is never edited. Qwen/ASR/native leases and
foreign applications are only observed, never acquired, released or stopped.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, math, os, re, shutil, subprocess, sys, time, uuid
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
TOPIC=MEDIA/'shorts-leveldesign-11-05'; DEST=TOPIC/'audio-preparation-v5'
WORKER=MEDIA/'11-05-audio-worker.json'; STATE=MEDIA/'11-05-audio-progress.json'
PROTOCOL='architectural111-11-05-audio-mix-v5'; OWNER='architectural-111-11-05-audio'
SCHEMA='11.05-audio-build-v5'
PINS={'prepare-solution-path-audio-v6.py':'839c2a8f2fe2c996dc5c722d1f6427d5633e23b50a49dd31d5ff286af08bec05','prepare-solution-path-audio-mix-v4.py':'68bffaddd36a2139533f0bff40abc926799814997d394ce001092bd10cc556d9',
 'prepare-first-audio.py':'29b44bce108c38064a33be5c64f7956d673bb60017afe458c990ce7672390a1f',
 'prepare-prospect-refuge-audio-v2.py':'a7692cdc0ca3fdda1916afa553a66c2d8d925878fe25579b9d35821d6990b1da',
 'verified-prospect-refuge-audio-build-v3.py':'db521babf1848861979a7580cd0a045540575f945909d99d2a7055433344f3b4',
 'run-solution-path-native-v4.py':'9429b70773f3a334dd5fd45d76ecb6b2fa8b2360dfe576aac341099d7adaea5e',
 'run-first-native.py':'a38205dac134e58da35a772290f0a151c7377b115b89910585277de76983a1f9'}
SELF_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0)
class Pending(RuntimeError): pass
def need(ok,message):
    if not ok: raise Pending(message)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def pin(p): return dict(path=str(Path(p).resolve()),sha256=sha(p))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def check_sources():
    need(sha(__file__)==SELF_SHA,'Mix producer changed after import')
    for name,expected in PINS.items():
        need(expected is not None,'Waiting for reviewed frozen source pin: '+name)
        need(sha(HERE/name)==expected,'Reviewed mix source changed: '+name)
def immutable(path,data):
    path=Path(path)
    if path.exists(): need(path.is_file() and path.read_bytes()==data,'Preserve differing immutable artifact: '+str(path));return
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f: f.write(data)
def immutable_json(path,value): immutable(path,(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode())
def local_pin(folder,path):return dict(file=Path(path).relative_to(folder).as_posix(),sha256=sha(path))
def state_save(value):
    STATE.parent.mkdir(parents=True,exist_ok=True); temp=STATE.with_name(STATE.name+'.'+uuid.uuid4().hex+'.tmp')
    with temp.open('x',encoding='utf-8') as f: json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    os.replace(temp,STATE)
def dependencies():
    check_sources(); prep=module('solution_mix_current_preparer',HERE/'prepare-solution-path-audio-v6.py')
    return prep

def require_review_paths(asr,levels,decisions):
    need(all(v and Path(v).is_file() for v in (asr,levels,decisions)),
         'Existing current blind-ASR, numerical word/join review and explicit component dispositions required before PCM decode')

def prepare(asr=None,levels=None,decisions=None):
    check_sources();require_review_paths(asr,levels,decisions); prep=dependencies()
    try: context=prep.prepare(asr,levels,decisions)
    except prep.Pending as error: raise Pending(str(error)) from error
    need(context['scalarPreparationAllowed'] is True,'Every exact selected component must have a bound internal disposition')
    audio,_=prep.primitives(); proposal=context['proposal']; identity=proposal['identity']; rows=identity['components']
    frames=identity['canonicalWav']['frames']; need(type(frames)is int and frames>0,'Nonempty exact canonical sample clock required')
    need(rows and rows[-1]['destinationSampleRange'][1]==frames and list(dict.fromkeys(r['paragraph'] for r in rows))==list(range(1,15)),
         'Current variable components must cover all14 ordered paragraphs')
    ff=audio.base.FF.resolve();probe=ff.with_name('ffprobe.exe')
    need(ff.is_file() and probe.is_file(),'Reviewed installed CPU FFmpeg/FFprobe files required')
    source_pins=[pin(__file__)]+[pin(HERE/name) for name in PINS]+identity['sourcePins']+[pin(ff),pin(probe),context['componentDispositions']]
    pinned={}
    for row in source_pins:
        need(pin(row['path'])==row,'Current mix input changed: '+row['path'])
        need(row['path'] not in pinned or pinned[row['path']]==row['sha256'],'Duplicate input path with differing hashes')
        pinned[row['path']]=row['sha256']
    source_pins=[dict(path=path,sha256=value) for path,value in sorted(pinned.items())]
    recipe_identity=dict(protocol=PROTOCOL,topicId='11.05',proposalFingerprint=proposal['fingerprint'],
        componentDispositions=context['componentDispositions'],profile=audio.PROFILE,musicLoopPolicy=audio.MUSIC_LOOP_POLICY,
        musicBalancePolicy=audio.MUSIC_BALANCE_POLICY,musicSource=pin(audio.MUSIC),musicLicense=pin(audio.LICENSE),
        sourcePins=source_pins,rawVoiceFingerprint=identity['voiceFingerprint'],rawCanonical=identity['canonicalWav'],
        canonicalTiming=identity['canonicalTiming'],componentCount=len(rows),paragraphCount=14,
        ffmpeg=pin(ff),ffprobe=pin(probe),numpyVersion=identity['numpyVersion'],scipyVersion=identity['scipyVersion'],
        soundfileVersion=identity['soundfileVersion'],libsndfileVersion=identity['libsndfileVersion'])
    recipe=dict(schemaVersion='11.05-audio-input-recipe-v5',identity=recipe_identity,fingerprint=digest(recipe_identity))
    context.update(_audio=audio,_prep=prep,asrPin=pin(asr),levelPin=pin(levels),decisionPin=pin(decisions))
    return context,recipe

def authorize(runtime):
    doc=read(ROOT/'shared/publishing/video-production-control.json');auth=doc['explicitArchitectural111Batch20261106']
    need(auth.get('status') not in ('paused','stopped','cancelled') and auth.get('automaticAdvanceWithinExactList') is True
         and auth.get('automaticAdvanceOutsideList') is False and auth.get('humanFinalReviewRequired') is True
         and auth.get('youtubeAuthorized') is False,'Exact111 local-review authority inactive')
    need(read(HERE/'checkpoint.json').get('currentTopicId')=='11.05','Selected topic changed before CPU mix production')
    if runtime.LEASE.exists(): raise Pending('Foreign/unknown shared GPU lease preserved; CPU mix must run serially')

def child_identity(runtime,pid=None):
    p=runtime.psutil.Process(os.getpid() if pid is None else pid);argv=p.cmdline()
    return dict(pid=p.pid,createTime=p.create_time(),argv=argv,commandSHA256=digest(argv),exe=p.exe())

def unregistered_child(runtime,record):
    if not record or record.get('phase')!='launching-owned-audio-tool' or record.get('child'):return False
    command=record.get('launchCommand')
    if not isinstance(command,list) or not command or not Path(command[0]).is_absolute():return True
    for p in runtime.psutil.process_iter(['name','cmdline']):
        try:
            if (p.info.get('name')or'').lower()!=Path(command[0]).name.lower():continue
            if p.info.get('cmdline') is None:return True
            if p.info['cmdline']==command:return True
        except runtime.psutil.NoSuchProcess:continue
        except runtime.psutil.AccessDenied:return True
    return False

def owned_alive(runtime,record): return runtime.alive(record) or unregistered_child(runtime,record)

def fresh_serial_gate(runtime,resource):
    check_sources();authorize(runtime)
    # Scope is the existing111 local media area. Never mutate foreign markers.
    for path in MEDIA.glob('*worker*.json'):
        if path.resolve()==WORKER.resolve():continue
        try: record=read(path)
        except (OSError,ValueError):raise Pending('Uninspected111 worker marker preserved: '+str(path))
        need(not (runtime.alive(record) or runtime.alive(record.get('child')) or unregistered_child(runtime,record)),
             'Another live/unknown111 worker or child is preserved: '+str(path))
    reason=resource.busy_reason() # Pinned read-only strict game/model/media/idle-GUI guards; no lease acquire/recovery.
    need(reason is None,reason or 'Resource guard declined')

def tracked_run(runtime,resource,worker,command,folder):
    command=[str(x) for x in command];audio=worker.audio
    executable=Path(command[0]).resolve()
    need(executable in (audio.base.FF.resolve(),audio.base.FF.resolve().with_name('ffprobe.exe')),'Only pinned CPU audio tools may launch')
    command[0]=str(executable)
    if executable.name.lower()=='ffmpeg.exe':command=command[:1]+['-threads','2','-filter_threads','2','-hwaccel','none']+command[1:]
    fresh_serial_gate(runtime,resource)
    log_id=uuid.uuid4().hex[:10];request=folder/'tool-receipts'/(log_id+'.request.json')
    immutable_json(request,dict(command=command,producerSHA256=SELF_SHA,recipeFingerprint=worker.recipe_fp))
    worker.update(phase='launching-owned-audio-tool',launchCommand=command,launchRequest=pin(request),child=None)
    child=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE)
    worker.update(child=child_identity(runtime,child.pid),phase='owned-audio-tool')
    out,err=child.communicate()
    immutable(folder/'tool-receipts'/(log_id+'.stdout.bin'),out);immutable(folder/'tool-receipts'/(log_id+'.stderr.bin'),err)
    receipt=folder/'tool-receipts'/(log_id+'.result.json')
    immutable_json(receipt,dict(request=local_pin(folder,request),exitCode=child.returncode,
        stdout=local_pin(folder,folder/'tool-receipts'/(log_id+'.stdout.bin')),stderr=local_pin(folder,folder/'tool-receipts'/(log_id+'.stderr.bin'))))
    worker.last_tool_receipt=local_pin(folder,receipt)
    worker.update(child=None,phase='audio-processing',launchCommand=None)
    if child.returncode:raise RuntimeError('Owned CPU audio tool failed; logs preserved: '+err.decode('utf-8','replace')[-2000:])
    result=subprocess.CompletedProcess(command,child.returncode,out,err);result.auditReceipt=worker.last_tool_receipt;return result

def float_sha(values):
    import numpy as np
    return hashlib.sha256(np.asarray(values,dtype='<f4').tobytes(order='C')).hexdigest()

def normalized_voice(audio,proposal):
    import numpy as np
    import soundfile as sf
    parts=[];records=[];raw=proposal['identity']['canonicalWav'];need(pin(raw['path'])['sha256']==raw['sha256'],'Original aggregate changed')
    aggregate,rate=sf.read(raw['path'],dtype='float32');need(rate==24000 and aggregate.ndim==1,'Exact raw mono24k PCM required')
    for row in proposal['identity']['components']:
        need(sha(row['rawTake'])==row['rawTakeSHA256'],'Original raw take changed')
        values,sr=sf.read(row['rawTake'],dtype='float32');a,b=row['destinationSampleRange']
        need(sr==rate and np.array_equal(values,aggregate[a:b]),'Original raw aggregate slice differs')
        matched,measure=audio.base.match_paragraph(values,rate,audio.PROFILE)
        need(measure==row['normalization'] and matched.dtype==np.float32 and len(matched)==row['frames'],'Reviewed scalar proposal changed')
        parts.append(matched);records.append(copy.deepcopy(row))
    whole=np.concatenate(parts);need(len(whole)==raw['frames'],'Scalar copies inserted/trimmed samples')
    return whole,records

def assemble_stems(audio,normalized,music,voice_measure,music_measure):
    """Pure arrays only. ONE whole-voice resample, fixed gains, music-only changes."""
    import numpy as np
    need(normalized.dtype==np.float32 and normalized.ndim==1 and len(normalized)>0 and np.isfinite(normalized).all(),'Finite normalized monoFLOAT32 required')
    need(music.dtype==np.float32 and music.ndim==2 and music.shape[1]==2 and np.isfinite(music).all(),'Finite decoded music stereoFLOAT32 required')
    for measured in (voice_measure,music_measure):need(all(math.isfinite(float(measured[k])) for k in ('input_i','input_tp')),'Finite actual loudness measurements required')
    prepared=audio.base.stereo_voice(normalized,24000)
    need(prepared.shape==(len(normalized)*2,2),'Whole voice resampling changed exact2x sample clock')
    voice_gain,voice_levels=audio.base.fixed_gain(prepared,voice_measure,audio.PROFILE['voiceTargetLufs'],audio.PROFILE['voiceSamplePeakCeilingDbfs'])
    stem=prepared*voice_gain
    music_gain,nominal_levels=audio.base.fixed_gain(music,music_measure,audio.PROFILE['musicTargetLufs'],audio.PROFILE['musicSamplePeakCeilingDbfs'])
    continuous,loop=audio.loop_music(music,len(stem),48000)
    nominal=audio.base.music_bed(continuous,len(stem),48000,music_gain,audio.base.duck_curve(stem,48000,audio.PROFILE),audio.PROFILE)
    compensation=audio.music_headroom_compensation(voice_levels);bed,compensation_proof=audio.apply_music_compensation(nominal,compensation)
    mix=stem+bed
    need(np.isfinite(mix).all() and audio.base.db(np.max(np.abs(mix)))<=audio.PROFILE['mixSamplePeakCeilingDbfs'],
         'Mix sample-peak limit exceeded; hold without attenuating voice, compressor or common-gain fallback')
    return dict(prepared=prepared,voice=stem,music=bed,mix=mix,loop=loop,voiceGain=voice_levels,
                nominalMusicGain=nominal_levels,musicGain=audio.effective_music_levels(nominal_levels,compensation),musicCompensation=compensation_proof)

def artifact(folder,name):
    import soundfile as sf
    path=Path(folder)/name; info=sf.info(path)
    return dict(path=str(path),sha256=sha(path),sampleRate=info.samplerate,channels=info.channels,frames=info.frames,subtype=info.subtype)

def verify_artifacts(folder,report):
    folder=Path(folder).resolve(); rows=report['artifacts']
    need(isinstance(rows,dict) and rows,'Actual immutable artifact ledger required')
    for name,row in rows.items():
        path=(folder/name).resolve()
        need(type(name)is str and row.get('file')==name and path.is_relative_to(folder) and path.is_file()
             and sha(path)==row.get('sha256'),'Artifact changed or escaped immutable output: '+str(name))
    return rows

def verify_tool_receipt(folder,row,artifacts,expected_command,recipe_fp):
    """Read saved source-bound command/result bytes; never launch or remeasure."""
    folder=Path(folder).resolve()
    def existing(pin_row):
        name=pin_row.get('file'); need(name in artifacts and artifacts[name]==pin_row,'Tool evidence is not an immutable declared artifact')
        path=(folder/name).resolve();need(path.is_relative_to(folder) and sha(path)==pin_row['sha256'],'Tool evidence path/hash differs');return path
    result=read(existing(row));need(result.get('exitCode')==0,'Actual CPU tool did not succeed')
    request=read(existing(result['request']))
    need(request==dict(command=expected_command,producerSHA256=SELF_SHA,recipeFingerprint=recipe_fp),'Actual CPU command/source/recipe differs')
    return existing(result['stdout']).read_bytes(),existing(result['stderr']).read_bytes()

def tool_command(ff,args):return [str(Path(ff).resolve()),'-threads','2','-filter_threads','2','-hwaccel','none',*[str(v) for v in args]]

def loudness_args(path):return ['-hide_banner','-i',str(path),'-map','0:a:0','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']

def measured_loudness(stderr):
    blocks=re.findall(r'\{\s*"input_i"[\s\S]*?\}',stderr.decode('utf-8','replace'))
    need(bool(blocks),'Stored actual loudness JSON is absent');result=json.loads(blocks[-1])
    need(all(math.isfinite(float(result[k])) for k in ('input_i','input_tp')),'Stored actual loudness values are nonfinite');return result

def verify_existing_core(path):
    """No FFmpeg/resource/worker. Verify exact current recipe, arrays and lineage."""
    import numpy as np
    import soundfile as sf
    path=Path(path).resolve();need(path.is_file(),'Actual11.05 audio build is not available')
    report=read(path);need(report.get('schemaVersion')==SCHEMA and report.get('topicId')=='11.05','Wrong audio build scope')
    ctx,recipe=prepare(report['rawVoiceAsr']['path'],report['rawNumericalLevelReview']['path'],report['acceptedComponentsReview']['path'])
    folder=(DEST/recipe['fingerprint'][:24]).resolve()
    need(path==folder/'audio-build.json' and report['fingerprint']==recipe['fingerprint'] and Path(report['output']).resolve()==folder,'Actual audio path/recipe identity differs')
    rows=verify_artifacts(folder,report)
    required={'input-recipe.json','line-levels.json','loudness-measurements.json','music-source-decoded.wav','music-loop-plan.json',
        'narration-component-normalized.wav','narration-prepared-stem.wav','narration-stem.wav','music-stem.wav','final-mix.wav'}
    need(required<=set(rows),'Mandatory immutable input/working-stem artifacts missing')
    need(read(folder/'input-recipe.json')==recipe,'Immutable actual input recipe differs')
    for i,source in enumerate(recipe['identity']['sourcePins']):
        name=f'source-snapshots/{i:03}.bin'
        need(name in rows and rows[name]['sha256']==source['sha256'],'Actual immutable source/input snapshot differs')
    proposal=ctx['proposal'];identity=proposal['identity'];audio=ctx['_audio'];frames=identity['canonicalWav']['frames']
    need(report['rawVoice']==identity['canonicalWav'] and report['canonicalTiming']==identity['canonicalTiming']
         and report['rawVoiceFingerprint']==identity['voiceFingerprint'] and report['selectedComponentCount']==identity['componentCount']
         and report['acceptedComponentsReview']==ctx['decisionPin'] and report['rawVoiceAsr']==ctx['asrPin']
         and report['rawNumericalLevelReview']==ctx['levelPin'],'Raw voice/ASR/disposition binding differs')
    normalized,components=normalized_voice(audio,proposal); lines=read(folder/'line-levels.json')
    need(lines['schemaVersion']=='11.05-line-levels-v5' and lines['componentCount']==len(components) and len(lines['components'])==len(components),
         'Normalized component ledger count differs')
    expected_components=[]
    for expected,actual in zip(components,lines['components']):
        need(all(actual.get(k)==v for k,v in expected.items()),'Accepted component ledger changed')
        name=expected['sceneId']+'-normalized.wav';need(actual['normalizedTake']==name and name in rows,'Exact normalized component path missing')
        part,sr=sf.read(folder/name,dtype='float32');a,b=expected['destinationSampleRange']
        need(sr==24000 and sf.info(folder/name).subtype=='FLOAT' and np.array_equal(part,normalized[a:b])
             and actual['normalizedTakeSHA256']==rows[name]['sha256'] and actual['normalizedTakeFloat32PcmSHA256']==float_sha(part),
             'Actual scalar working component changed')
        expected_components.append(dict(**expected,normalizedTake=name,normalizedTakeSHA256=rows[name]['sha256'],normalizedTakeFloat32PcmSHA256=float_sha(part),
            normalizationScope='One reviewed scalar over the complete selected raw sentence; natural lead/tail unchanged'))
    need(lines==dict(schemaVersion='11.05-line-levels-v5',componentCount=len(components),components=expected_components,
        rawCanonical=identity['canonicalWav'],voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,wordBoundariesShifted=False),
        'Actual line ledger or unchanged clock flags differ')
    measures=read(folder/'loudness-measurements.json')
    need(set(measures)=={'voice','music','mix'},'Unexpected/missing loudness measurement role')
    work=Path(report['workOrigin']).resolve()
    need(work.parent==DEST.resolve() and re.fullmatch('work-'+recipe['fingerprint'][:16]+r'-[0-9a-f]{10}',work.name),
         'Recorded actual work origin escaped selected attempt scope')
    for role,input_path in [('voice',work/'narration-prepared-stem.wav'),('music',audio.MUSIC),('mix',work/'final-mix.wav')]:
        _,stderr=verify_tool_receipt(folder,report['measurementReceipts'][role],rows,
            tool_command(audio.base.FF,loudness_args(input_path)),recipe['fingerprint'])
        need(measured_loudness(stderr)==measures[role],'Stored loudness measure differs from actual pinned tool output')
    music,sr=sf.read(folder/'music-source-decoded.wav',dtype='float32')
    need(sr==48000 and sf.info(folder/'music-source-decoded.wav').subtype=='FLOAT','Actual decoded music format differs')
    decoded,_=verify_tool_receipt(folder,report['musicDecodeReceipt'],rows,tool_command(audio.base.FF,
        ['-v','error','-i',audio.MUSIC,'-map','0:a:0','-ar','48000','-ac','2','-f','f32le','pipe:1']),recipe['fingerprint'])
    need(len(decoded)==music.size*4 and hashlib.sha256(decoded).hexdigest()==float_sha(music),
         'Actual decoded music PCM differs from pinned original-source decoder output')
    built=assemble_stems(audio,normalized,music,measures['voice'],measures['music'])
    arrays={'narration-component-normalized.wav':(normalized,24000),'narration-prepared-stem.wav':(built['prepared'],48000),
            'narration-stem.wav':(built['voice'],48000),'music-stem.wav':(built['music'],48000),'final-mix.wav':(built['mix'],48000)}
    for name,(expected,rate) in arrays.items():
        actual,sr=sf.read(folder/name,dtype='float32')
        need(sr==rate and sf.info(folder/name).subtype=='FLOAT' and actual.shape==expected.shape and np.array_equal(actual,expected),
             'Actual FLOAT working stem/sample math differs: '+name)
    # Rebuild loops from decoded source, including exact finite boundary annotations.
    need(read(folder/'music-loop-plan.json')==built['loop']==report['musicLoopPlan'],'Planned or measured music phase/seam annotations differ')
    lineage=dict(normalized24kMonoFloat32SHA256=float_sha(normalized),prepared48kStereoFloat32SHA256=float_sha(built['prepared']),
        finalVoice48kStereoFloat32SHA256=float_sha(built['voice']),finalMusic48kStereoFloat32SHA256=float_sha(built['music']),
        finalMix48kStereoFloat32SHA256=float_sha(built['mix']),voiceOffsetSamples=0,rawToPreparedSampleRatio=[2,1],voiceSpeed=1.)
    need(report['pcmLineage']==lineage and report['voiceGlobalGain']==built['voiceGain']
         and report['musicNominalGain']==built['nominalMusicGain'] and report['musicGain']==built['musicGain']
         and report['musicOnlyCompensation']==built['musicCompensation'],'Actual DSP lineage/gain metadata differs')
    expected_mix=artifact(folder,'final-mix.wav')
    need(report['mixWav']==expected_mix and (expected_mix['sampleRate'],expected_mix['channels'],expected_mix['frames'],expected_mix['subtype'])==(48000,2,frames*2,'FLOAT')
         and report['durationSeconds']==frames/24000 and report['videoFrameTarget']==dict(fps=60,totalFrames=(frames*60+23999)//24000,noAudioTailPadding=True),
         'Exact raw-to-mix2x/visualceil clock differs')
    need(report['musicLoops']==built['loop']['repeatCount'] and report['musicContinuousExcerpt']==(built['loop']['repeatCount']==0)
         and report['musicPlaybackRate']==1. and report['musicPlaybackContinuous'] is True
         and report['musicAttribution']==ctx['assets']['rights']['requiredDescriptionCredit'] and report['musicRights']==ctx['assets']['rights'],
         'Actual music phase/repeat/rights metadata differs')
    need(all(report.get(k)==v for k,v in dict(voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,
        compressorUsed=False,voiceSideDuck=False,uniformMixGainDb=0.,originalRawFilesUnchanged=True,wordBoundariesShifted=False,
        engineAggregatePreservedSeparately=True,finalMixedAsr='pending',encodedAacTruePeak='pending',finalMovieComplete=False,
        platformActions=[],actualListening=False,automaticSpeechPass=False,humanApproval=False,
        status='mix-prepared-mixed-ASR-encoded-AAC-listening-pending').items()),
        'Forbidden voice processing or false approval flag')
    need(measures['mix']==report['measuredPcmMix'] and all(math.isfinite(float(measures['mix'][k])) for k in ('input_i','input_tp'))
         and float(measures['mix']['input_tp'])<=audio.PROFILE['mixTruePeakMaximumDbtp'],'Actual stored true-peak measure held')
    return report

def execute(asr,levels,decisions):
    require_review_paths(asr,levels,decisions);check_sources()
    runtime=module('solution_audio_mix_singleton',HERE/'run-first-native.py');runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
    resource=module('solution_audio_mix_resource',HERE/'run-solution-path-native-v4.py')
    worker=runtime.SingleWorker(WORKER,is_alive=lambda r:owned_alive(runtime,r)).acquire();work=None;state={}
    try:
        worker.update(**child_identity(runtime),stage='CPU-audio-mix',topicId='11.05')
        fresh_serial_gate(runtime,resource);ctx,recipe=prepare(asr,levels,decisions);audio=ctx['_audio']
        final=DEST/recipe['fingerprint'][:24]
        if final.exists():return verify_existing_core(final/'audio-build.json')
        frames=ctx['proposal']['identity']['canonicalWav']['frames']
        need(shutil.disk_usage(MEDIA).free>frames*110+2*1024**3,'Insufficient scoped audio disk reserve')
        need(runtime.psutil.virtual_memory().available>frames*128+2*364*48000*8+1024**3,'Insufficient host RAM for exact FLOAT working stems')
        work=DEST/('work-'+recipe['fingerprint'][:16]+'-'+uuid.uuid4().hex[:10]);work.mkdir(parents=True,exist_ok=False)
        worker.audio=audio;worker.recipe_fp=recipe['fingerprint'];worker.update(fingerprint=recipe['fingerprint'],output=str(work),phase='audio-processing')
        state=dict(protocol=PROTOCOL,owner=OWNER,**child_identity(runtime),fingerprint=recipe['fingerprint'],output=str(work),completed=False)
        state_save(state);immutable_json(work/'input-recipe.json',recipe)
        for i,row in enumerate(recipe['identity']['sourcePins']):immutable(work/'source-snapshots'/f'{i:03}.bin',Path(row['path']).read_bytes())
        import numpy as np
        import soundfile as sf
        normalized,records=normalized_voice(audio,ctx['proposal'])
        for row in records:
            a,b=row['destinationSampleRange'];name=row['sceneId']+'-normalized.wav';sf.write(work/name,normalized[a:b],24000,subtype='FLOAT')
            row.update(normalizedTake=name,normalizedTakeSHA256=sha(work/name),normalizedTakeFloat32PcmSHA256=float_sha(normalized[a:b]),normalizationScope='One reviewed scalar over the complete selected raw sentence; natural lead/tail unchanged')
        sf.write(work/'narration-component-normalized.wav',normalized,24000,subtype='FLOAT')
        prepared=audio.base.stereo_voice(normalized,24000);sf.write(work/'narration-prepared-stem.wav',prepared,48000,subtype='FLOAT')
        immutable_json(work/'line-levels.json',dict(schemaVersion='11.05-line-levels-v5',componentCount=len(records),components=records,
            rawCanonical=ctx['proposal']['identity']['canonicalWav'],voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,wordBoundariesShifted=False))
        original_run=audio.base.run
        audio.base.run=lambda command:tracked_run(runtime,resource,worker,command,work)
        try:
            voice_measure=audio.base.loud(work/'narration-prepared-stem.wav');measure_receipts={'voice':worker.last_tool_receipt}
            music_measure=audio.base.loud(audio.MUSIC);measure_receipts['music']=worker.last_tool_receipt
            decode=audio.base.run([audio.base.FF,'-v','error','-i',audio.MUSIC,'-map','0:a:0','-ar','48000','-ac','2','-f','f32le','pipe:1']);raw=decode.stdout
            need(len(raw)%8==0,'Decoded music stereo sample bytes are truncated')
            music=np.frombuffer(raw,dtype='<f4').reshape(-1,2).copy();sf.write(work/'music-source-decoded.wav',music,48000,subtype='FLOAT')
            built=assemble_stems(audio,normalized,music,voice_measure,music_measure)
            for name,key in [('narration-stem.wav','voice'),('music-stem.wav','music'),('final-mix.wav','mix')]:sf.write(work/name,built[key],48000,subtype='FLOAT')
            mix_measure=audio.base.loud(work/'final-mix.wav');measure_receipts['mix']=worker.last_tool_receipt
            need(float(mix_measure['input_tp'])<=audio.PROFILE['mixTruePeakMaximumDbtp'],'Mix true-peak exceeds profile; preserve work without voice attenuation/compression fallback')
        finally:audio.base.run=original_run
        immutable_json(work/'loudness-measurements.json',dict(voice=voice_measure,music=music_measure,mix=mix_measure))
        immutable_json(work/'music-loop-plan.json',built['loop'])
        need(prepare(asr,levels,decisions)[1]==recipe,'Actual input identity changed during mix; preserve partial version')
        lineage=dict(normalized24kMonoFloat32SHA256=float_sha(normalized),prepared48kStereoFloat32SHA256=float_sha(built['prepared']),
            finalVoice48kStereoFloat32SHA256=float_sha(built['voice']),finalMusic48kStereoFloat32SHA256=float_sha(built['music']),finalMix48kStereoFloat32SHA256=float_sha(built['mix']),voiceOffsetSamples=0,rawToPreparedSampleRatio=[2,1],voiceSpeed=1.)
        artifacts={p.relative_to(work).as_posix():dict(file=p.relative_to(work).as_posix(),sha256=sha(p)) for p in work.rglob('*') if p.is_file()}
        mix=artifact(work,'final-mix.wav');mix['path']=str(final/'final-mix.wav')
        identity=ctx['proposal']['identity']
        report=dict(schemaVersion=SCHEMA,topicId='11.05',status='mix-prepared-mixed-ASR-encoded-AAC-listening-pending',fingerprint=recipe['fingerprint'],output=str(final),workOrigin=str(work),
            artifacts=artifacts,mixWav=mix,selectedComponentCount=len(records),rawVoiceFingerprint=identity['voiceFingerprint'],rawVoice=identity['canonicalWav'],canonicalTiming=identity['canonicalTiming'],
            acceptedComponentsReview=ctx['decisionPin'],rawVoiceAsr=ctx['asrPin'],rawNumericalLevelReview=ctx['levelPin'],durationSeconds=frames/24000,
            videoFrameTarget=dict(fps=60,totalFrames=(frames*60+23999)//24000,noAudioTailPadding=True),pcmLineage=lineage,
            voiceGlobalGain=built['voiceGain'],musicNominalGain=built['nominalMusicGain'],musicGain=built['musicGain'],musicOnlyCompensation=built['musicCompensation'],
            musicLoopPlan=built['loop'],musicLoops=built['loop']['repeatCount'],musicContinuousExcerpt=built['loop']['repeatCount']==0,
            musicPlaybackRate=1.,musicPlaybackContinuous=True,musicAttribution=ctx['assets']['rights']['requiredDescriptionCredit'],musicRights=ctx['assets']['rights'],
            measuredPcmMix=mix_measure,measurementReceipts=measure_receipts,musicDecodeReceipt=decode.auditReceipt,
            voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,compressorUsed=False,voiceSideDuck=False,uniformMixGainDb=0.,
            originalRawFilesUnchanged=True,wordBoundariesShifted=False,engineAggregatePreservedSeparately=True,actualListening=False,automaticSpeechPass=False,
            finalMixedAsr='pending',encodedAacTruePeak='pending',finalMovieComplete=False,humanApproval=False,platformActions=[])
        immutable_json(work/'audio-build.json',report);need(not final.exists(),'Another immutable version appeared; preserve both')
        work.rename(final);work=None
        result=verify_existing_core(final/'audio-build.json');state.update(completed=True,output=str(final),audioBuild=pin(final/'audio-build.json'),status=result['status']);state_save(state);return result
    except BaseException as error:
        if work and work.exists():immutable_json(work/'failed.json',dict(completed=False,error=repr(error),automaticFallback=False))
        state.update(completed=False,error=repr(error),status='failed-preserved');state_save(state);raise
    finally:
        worker.close(remove=not(runtime.alive(worker.record.get('child')) or unregistered_child(runtime,worker.record)))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--asr-review');ap.add_argument('--level-review');ap.add_argument('--component-review');ap.add_argument('--execute',action='store_true');args=ap.parse_args()
    try:
        if args.execute:
            result=execute(args.asr_review,args.level_review,args.component_review)
            print(json.dumps(dict(ready=True,audioBuild=str(Path(result['output'])/'audio-build.json'),fingerprint=result['fingerprint'],mixWav=result['mixWav'],actualListening=False)));return
        context,recipe=prepare(args.asr_review,args.level_review,args.component_review)
        print(json.dumps(dict(ready=True,recipeFingerprint=recipe['fingerprint'],componentCount=context['proposal']['identity']['componentCount'],audioPrepared=False,ffmpegStarted=False,gpuUsed=False,actualListening=False)))
    except (Pending,FileNotFoundError) as error:
        print(json.dumps(dict(ready=False,reason=str(error),audioPrepared=False,ffmpegStarted=False,gpuUsed=False,actualListening=False,humanApproval=False)))
        if args.execute:raise SystemExit(2)
if __name__=='__main__':main()
