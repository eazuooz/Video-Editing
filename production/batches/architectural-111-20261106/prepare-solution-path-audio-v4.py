"""Read-only 11.05 audio readiness/scalar proposal; no execute/mix/worker branch.

Actual complete PCM, blind ASR, numerical review and explicit dispositions are
required in that order. Reuse only pinned numerical functions, never another
episode's producer, paragraph counts, clocks, filenames or accepted decisions.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, re, sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
PROJECT=ROOT/'projects/shorts-leveldesign-11-05'
VOICE=MEDIA/'11-05-voice-evidence.json'; VOICE_STATE=MEDIA/'11-05-voice-progress.json'
ASSET_PLAN=PROJECT/'audio-asset-preparation-v1.json'
ASSET_PLAN_SHA='1238dff5f598d437418eddfb75f7ec27c99676cb2c082b29b4a54253c895728a'
PINS={'prepare-first-audio.py':'29b44bce108c38064a33be5c64f7956d673bb60017afe458c990ce7672390a1f',
      'prepare-prospect-refuge-audio-v2.py':'a7692cdc0ca3fdda1916afa553a66c2d8d925878fe25579b9d35821d6990b1da',
      'prepare-zen-view-audio.py':'363b7e22bd99e1b860d981b12c2d91a965f740b3b77ec00935c74db456f6ed7b',
      'verified-prospect-refuge-audio-build-v3.py':'db521babf1848861979a7580cd0a045540575f945909d99d2a7055433344f3b4',
      'run-solution-path-voice-qa-v4.py':'fe1fd24796ad659f4c1b4c6e09cc1ef53732b1e912947f310c5b35b4c34ce076'}
SELF_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
class Pending(RuntimeError): pass
def need(value,reason):
    if not value: raise Pending(reason)
def note(value): return isinstance(value,str) and bool(value.strip())
def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def pin(path): return dict(path=str(Path(path).resolve()),sha256=sha(path))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); value=importlib.util.module_from_spec(spec)
    sys.modules[name]=value; spec.loader.exec_module(value); return value
def check_sources():
    need(sha(__file__)==SELF_SHA,'Audio preparation adapter changed after import')
    for name,expected in PINS.items(): need(sha(HERE/name)==expected,'Pinned numerical/ASR source changed: '+name)
    need(sha(ASSET_PLAN)==ASSET_PLAN_SHA,'Selected Wholesome asset plan changed')

def primitives():
    check_sources()
    audio=module('solution_audio_readonly_math',HERE/'prepare-prospect-refuge-audio-v2.py')
    qa=module('solution_audio_current_blind_asr',HERE/'run-solution-path-voice-qa-v4.py')
    return audio,qa

def asset_binding(audio,draft):
    plan=read(ASSET_PLAN); old=plan['sourceNarration']; previous=Path(old['path'])
    need(sha(previous)==old['sha256'],'Asset-plan source history changed')
    history=read(previous)
    need(history['narrationKo']==draft['narrationKo'] and history['paragraphsEn']==draft['paragraphsEn'],
         'Audio asset plan no longer refers to the same complete bilingual text')
    music=plan['music']; mix=plan['plannedMix']
    need(music['source']==dict(path=str(audio.MUSIC),sha256=audio.MUSIC_SHA,bytes=audio.MUSIC.stat().st_size)
         and music['licenseRecord']['sha256']==audio.LICENSE_SHA,'Selected music/license identity differs')
    checks={'voiceTargetLufs':'voiceTargetLufs','musicTargetLufs':'musicTargetLufs',
            'musicSpeechDuckDb':'backgroundSpeechDuckDb','duckAttackMs':'duckAttackMs','duckReleaseMs':'duckReleaseMs',
            'musicOuterFadeSeconds':'musicFadeSeconds','voiceSamplePeakCeilingDbfs':'voiceSamplePeakCeilingDbfs',
            'musicSamplePeakCeilingDbfs':'musicSamplePeakCeilingDbfs','mixSamplePeakCeilingDbfs':'mixSamplePeakCeilingDbfs',
            'encodedTruePeakMaximumDbtp':'mixTruePeakMaximumDbtp','mixRate':'mixRate','mixChannels':'mixChannels'}
    need(all(mix[k]==audio.PROFILE[v] for k,v in checks.items()),'Approved planned level/peak/duck profile differs')
    need(mix['musicLoopCrossfadeSeconds']==audio.MUSIC_LOOP_POLICY['crossfadeSeconds']==1.
         and mix['uniformMixGainDb']==0 and mix['voiceSideDuck'] is False and mix['voiceCompression'] is None,
         'Music-only loop/voice-preservation policy differs')
    rights=audio.music_rights()
    return dict(plan=pin(ASSET_PLAN),rights=rights,priorSource=old,currentTextMatchesAssetPlan=True,
                instrumentalAuditionVerified=False,actualListening=False)

def exact_components(voice,timing):
    scenes=voice['identity']['scenes']; n=len(scenes); position=0; rows=[]
    need(n>0 and len({s['id'] for s in scenes})==n and
         len(voice['sceneWavs'])==len(timing['entries'])==len(voice['paragraphMapping'])==n,
         'Variable selected scene/mapping/PCM counts differ')
    for scene,take,entry,mapping in zip(scenes,voice['sceneWavs'],timing['entries'],voice['paragraphMapping']):
        frames=take['frames']; sid=scene['id']; text=' '.join(scene['lines'])
        need(re.fullmatch(r'p\d{3}-c\d{2,}',sid) and type(frames)is int and frames>0,'Nonempty canonical sentence identity required')
        need(entry['scene_id']==mapping['sceneId']==sid and entry['text']==mapping['canonicalText']==text
             and (take['sampleRate'],take['channels'],take['sampleWidthBytes'])==(24000,1,2),'Canonical ordered sentence/PCM format differs')
        end=position+frames
        need(all(type(entry.get(k))in(int,float) and math.isfinite(entry[k]) and abs(entry[k]-v)<=1e-9
                 for k,v in [('start',position/24000),('end',end/24000)]),'Unrounded sample clock differs')
        rows.append(dict(sceneId=sid,paragraph=mapping['paragraph'],text=text,rawTake=take['path'],
            rawTakeSHA256=take['sha256'],rawPcmSHA256=take['pcmSHA256'],sourceSampleRange=[0,frames],
            destinationSampleRange=[position,end],prepared48kSampleRange=[2*position,2*end],frames=frames,rate=24000))
        position=end
    paragraphs=[r['paragraph'] for r in rows]
    need(paragraphs==sorted(paragraphs) and list(dict.fromkeys(paragraphs))==list(range(1,15))
         and position==voice['aggregateWav']['frames'],'Exact14 ordered paragraphs/raw aggregate length required')
    return rows

def verified_asr(qa,path):
    job=qa.prepare_job(); expected=Path(job['output'])/'review.json'; path=Path(path).resolve()
    need(path==expected.resolve() and path.is_file(),'Exact current complete blind-ASR review required')
    before=pin(path); saved=read(path)
    # summary can only compare an existing immutable artifact here, never create it.
    fresh=qa.summary(job)
    need(fresh is not None and fresh==saved and pin(path)==before,'Complete raw ASR records/summary changed')
    need(saved['aliasesApplied'] is False and saved['expectedPrompt'] is None and saved['humanListening'] is False,
         'Blind literal-recognition contract differs')
    return saved,before,job

def verified_levels(audio,qa,path,voice,asr_pin,job):
    path=Path(path).resolve(); need(path.is_file(),'Existing complete word/body/join level review required')
    primitive=HERE/'first-level-continuity-review.py'
    need(sha(primitive)==qa.qa.APPROVED['firstLevelPrimitiveSHA256'],'Numerical word-level primitive changed')
    level_math=module('solution_audio_level_policy',primitive); report=read(path)
    fp=qa.digest(dict(asr=asr_pin,canonicalSHA256=voice['aggregateWav']['sha256'],primitive=pin(primitive),policy=level_math.POLICY))
    need(path==(Path(job['output'])/'raw-level-review'/fp[:24]/'review.json').resolve(),'Numerical review is outside exact raw-ASR identity')
    need(report['voiceFingerprint']==voice['fingerprint'] and report['canonicalWav']==voice['aggregateWav']
         and report['asrReview']==asr_pin and report['levelPrimitive']==pin(primitive) and report['policy']==level_math.POLICY,
         'Word/join level proof differs from actual raw PCM/ASR')
    before=pin(path)
    need(qa.raw_level_review(Path(job['output'])/'job.json').resolve()==path and pin(path)==before,
         'Current numerical review failed exact immutable recomputation')
    n=len(voice['identity']['scenes'])
    need(len(report['takes'])==n and len(report['paragraphs'])==14 and len(report['joins'])==n-1,'Numerical take/paragraph/join coverage differs')
    require_stable_takes(report['flags'])
    return report,before

def require_stable_takes(flags):
    need(not any(f.get('kind')=='sustained-take-word-body-decline' for f in flags),
         'Sustained within-take word-body decline is held; a constant scalar cannot repair it')

def scalar_proposal(audio,voice,rows,review,levels,source_pins):
    require_stable_takes(levels['flags'])  # Before any PCM array read or normalization.
    import numpy as np
    import soundfile as sf
    raw_paths=[Path(voice['aggregateWav']['path'])]+[Path(r['rawTake']) for r in rows]
    before={str(p):sha(p) for p in raw_paths}
    need(before[str(raw_paths[0])]==voice['aggregateWav']['sha256'],'Raw aggregate changed')
    aggregate,rate=sf.read(raw_paths[0],dtype='float32')
    need(rate==24000 and aggregate.ndim==1,'Canonical mono24k raw PCM required')
    records=[];parts=[];recognized={r['task']['sceneId']:r for r in review['takes']}
    need(len(recognized)==len(rows),'Exact independent take ASR coverage required')
    for row in rows:
        need(before[row['rawTake']]==row['rawTakeSHA256'],'Raw scene hash changed')
        samples,sr=sf.read(row['rawTake'],dtype='float32'); a,b=row['destinationSampleRange']
        need(sr==rate and samples.ndim==1 and len(samples)==row['frames'] and np.array_equal(samples,aggregate[a:b]),
             'Canonical raw scene is not an exact unchanged aggregate slice')
        matched,gain=audio.base.match_paragraph(samples,rate,audio.PROFILE)
        need(matched.dtype==np.float32 and matched.shape==samples.shape and np.isfinite(matched).all(),
             'Scalar working copy changed shape or contains nonfinite samples')
        observed=recognized[row['sceneId']]
        records.append(dict(**row,normalization=gain,rawTakeASRRecordSHA256=audio.digest(observed),
            recognizedLiteral=observed['text'],literalComparison=observed['comparison'],
            literalDifferent=audio.base.asr.folded(row['text'])!=audio.base.asr.folded(observed['text'])))
        parts.append(matched)
    normalized=np.concatenate(parts); need(len(normalized)==len(aggregate),'Scalar copies changed sample count')
    joins=[]
    for left,right in zip(records,records[1:]):
        at=left['destinationSampleRange'][1]
        joins.append(dict(previousScene=left['sceneId'],nextScene=right['sceneId'],boundarySample=at,
            rawLastSample=float(aggregate[at-1]),rawFirstSample=float(aggregate[at]),
            normalizedLastSample=float(normalized[at-1]),normalizedFirstSample=float(normalized[at]),
            normalizedAbsoluteStep=float(abs(normalized[at]-normalized[at-1]))))
    need(all(sha(p)==before[str(p)] for p in raw_paths),'Original raw audio changed during CPU proposal')
    identity=dict(protocol='architectural111-11-05-audio-preparation-v4',topicId='11.05',
        voiceFingerprint=voice['fingerprint'],componentCount=len(records),paragraphCount=14,
        canonicalWav=voice['aggregateWav'],canonicalTiming=voice['timing'],components=records,joins=joins,
        levelFlags=levels['flags'],profile=audio.PROFILE,musicLoopPolicy=audio.MUSIC_LOOP_POLICY,
        musicBalancePolicy=audio.MUSIC_BALANCE_POLICY,sourcePins=source_pins,
        adapterSHA256=sha(__file__),numpyVersion=np.__version__,soundfileVersion=sf.__version__,
        libsndfileVersion=sf.__libsndfile_version__,scipyVersion=audio.scipy.__version__)
    return dict(schemaVersion='11.05-scalar-audio-proposal-v1',identity=identity,fingerprint=digest(identity),
        joinsReviewedSHA256=digest(joins),acknowledgedLevelFlagsSHA256=digest(levels['flags']),
        rawFilesUnchanged=True,workingArraysOnly=True,audioWritten=False,actualListening=False,automaticSpeechPass=False)

def component_dispositions(proposal,path,asr_pin,level_pin):
    report=read(path); identity=proposal['identity']; sources=identity['components']
    require_stable_takes(identity['levelFlags'])
    expected=dict(schemaVersion='11.05-audio-component-dispositions-v1',topicId='11.05',
        componentCount=len(sources),voiceFingerprint=identity['voiceFingerprint'],
        canonicalWav=identity['canonicalWav'],canonicalTiming=identity['canonicalTiming'],rawAsrReview=asr_pin,
        levelReview=level_pin,proposalFingerprint=proposal['fingerprint'],joinsReviewedSHA256=proposal['joinsReviewedSHA256'],
        acknowledgedLevelFlagsSHA256=proposal['acknowledgedLevelFlagsSHA256'],technicalOnly=True,actualListening=False,humanApproval=False)
    need(all(report.get(k)==v for k,v in expected.items()),'Internal component dispositions do not bind exact current proposal')
    need(isinstance(report.get('reviewer'),str) and report['reviewer'].strip(),'Explicit internal reviewer required')
    decisions=report.get('components',[])
    need(len(decisions)==len(sources),'Every variable selected component needs a disposition')
    for decision,source in zip(decisions,sources):
        need(all(decision.get(k)==source[k] for k in ('sceneId','rawTakeSHA256','rawPcmSHA256','rawTakeASRRecordSHA256')),
             'Component disposition is stale, missing or reordered')
        need(decision.get('decision')=='accept-scalar-working-copy' and decision.get('literalDecision')=='accepted-for-technical-preparation',
             'Held literal/component cannot be normalized as a fallback')
        gain=decision.get('expectedGainDb')
        need(type(gain)in(int,float) and math.isfinite(gain) and abs(gain-source['normalization']['constantGainDb'])<=1e-7,
             'Reviewed scalar differs from the exact proposal')
        if source['literalDifferent']: need(note(decision.get('literalReviewNote')),'Preserve an explicit literal-difference disposition')
        if abs(source['normalization']['targetErrorDb'])>.5: need(note(decision.get('levelReviewNote')),'Peak-limited target shortfall needs a numerical disposition')
    if identity['levelFlags']: need(note(report.get('levelFlagsDisposition')),'All remaining numerical flags require explicit retained dispositions')
    if any(abs(j['rawLastSample']-j['rawFirstSample'])>.02 or j['normalizedAbsoluteStep']>.02 for j in identity['joins']):
        need(note(report.get('joinLevelReviewNote')),'Large raw/working boundary step needs explicit technical disposition')
    return report

def prepare(asr_path=None,level_path=None,component_path=None):
    check_sources()
    need(VOICE.is_file() and VOICE_STATE.is_file(),'Waiting for actual completed current11.05 canonical voice; no profile/model/resource/PCM read')
    need(read(VOICE_STATE).get('completed') is True,'Current voice is still incomplete; preserve the live worker')
    need(asr_path is not None and level_path is not None,'Complete current blind-ASR and word/join numerical review paths required')
    audio,qa=primitives()
    try:
        out,voice,timing,draft=qa.exact_voice()
        rows=exact_components(voice,timing); assets=asset_binding(audio,draft)
        review,asr_pin,job=verified_asr(qa,asr_path)
        levels,level_pin=verified_levels(audio,qa,level_path,voice,asr_pin,job)
        historical=audio.historical_engine_pins(voice)
    except (audio.Pending,qa.Pending) as error: raise Pending(str(error)) from error
    narration_pin=job['identity']['sourceNarration']
    need(pin(narration_pin['path'])==narration_pin,'Current narration changed after ASR verification')
    source_pins=[pin(__file__)]+[pin(HERE/name) for name in PINS]+[pin(ASSET_PLAN),narration_pin,
        pin(out/'voice-complete-proof.json'),asr_pin,level_pin]+historical
    proposed=scalar_proposal(audio,voice,rows,review,levels,source_pins)
    dispositions=component_dispositions(proposed,component_path,asr_pin,level_pin) if component_path else None
    check_sources()
    need(qa.prepare_job()['fingerprint']==job['fingerprint'],'Current voice/narration/ASR identity changed during CPU preparation')
    return dict(topicId='11.05',ready=False,status='scalar-proposal-ready' if dispositions is None else 'internal-scalar-dispositions-bound',
        proposal=proposed,componentDispositions=pin(component_path) if dispositions else None,assets=assets,
        nextRequired='Explicit current component dispositions' if dispositions is None else 'A separately reviewed11.05 immutable mix producer/verifier; execution is not implemented by this adapter',
        scalarPreparationAllowed=dispositions is not None,mixReady=False,executeSupported=False,
        audioPrepared=False,ffmpegStarted=False,gpuUsed=False,actualListening=False,humanApproval=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--asr-review'); parser.add_argument('--level-review'); parser.add_argument('--component-review')
    parser.add_argument('--proposal-only',action='store_true'); args=parser.parse_args()
    try:
        result=prepare(args.asr_review,args.level_review,args.component_review)
        if args.proposal_only: result=result['proposal']
    except (Pending,FileNotFoundError) as error:
        result=dict(topicId='11.05',ready=False,reason=str(error),executeSupported=False,audioPrepared=False,
                    ffmpegStarted=False,gpuUsed=False,actualListening=False,humanApproval=False)
    print(json.dumps(result,ensure_ascii=False,allow_nan=False))
if __name__=='__main__': main()
