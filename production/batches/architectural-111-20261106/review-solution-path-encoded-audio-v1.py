"""11.05 final AAC numerical review. Default is read-only Pending.

Only --execute may run the installed CPU packet probe/normal AAC decoder and
input loudness measurement. No encoder, model, speech repair or GPU lease.
This body-only version requires an explicit zero-offset whole-audio mapping;
intro/outro audio requires a separately authored whole-mix contract/version.
"""
from __future__ import annotations
import argparse, ast, copy, hashlib, importlib.util, json, math, os, re, shutil, subprocess, sys, types, uuid
from fractions import Fraction
from pathlib import Path
sys.dont_write_bytecode = True
os.environ.update(OMP_NUM_THREADS='2', MKL_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2')
HERE = Path(__file__).resolve().parent
SELF_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
ROOT = HERE.parents[2]
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
TOPIC = MEDIA / 'shorts-leveldesign-11-05'
DEST = TOPIC / 'encoded-audio-review-v1'
WORKER = MEDIA / '11-05-encoded-audio-review-v1-worker.json'
PROTOCOL, OWNER = 'architectural111-11-05-encoded-audio-review-v1', 'architectural-111-11-05-encoded-audio'
SCHEMA = '11.05-encoded-audio-numerical-review-v1'
VOICE_FP = '6691614beecda682a8130136a3dfd952b472e7acdba769a83cd1ca7212df8cc1'
NARRATION_SHA = 'e3179da81b2a23135eb6a8907ebb6205c14fc2d66e528a37372d491d0ffeaa91'
FORMAT_REVIEW = ROOT / 'projects/shorts-leveldesign-11-05/portrait-audio-format-review-v1.json'
FORMAT_REVIEW_SHA = 'f2b81e2a030e06f94254d5f73a3bcf8e6e8808ccfa86ca2222a963aaecab36d4'
RENDERER = HERE / 'render-solution-path-film-v2.py'
RENDERER_SHA = '2e874781f72ed617dab9afa395c3eab7f7d4e889f19ce8d1295e304c4fc91422'  # Reviewed upstream full-film router.
PINS = {
 'review-prospect-refuge-encoded-audio.py': '904d72a386255033bfc99592e3cdca8eb463bf958cbc181f38270266f425e783',
 'first-level-continuity-review.py': '545104df16cf26af0c0637faa76750bea1e5b70f424cc13820f13baa8b773544',
 'prepare-solution-path-audio-mix-v5.py': '1cfa0c387321c73d3b5442cd25ce1cbe144ea5b1573dc2f40498e887f5b62fc3',
 'verified-solution-path-audio-build-v5.py': '0c1d86561745ceca1260a137c57dba0231546a5cf7a1ae547f5b6eb37132a55b',
 'prepare-solution-path-audio-v6.py': '839c2a8f2fe2c996dc5c722d1f6427d5633e23b50a49dd31d5ff286af08bec05',
 'build-solution-path-caption-timing-v6.py': '11a2765b208427d2f5a4caa8bfa0958f390adaa062ecc95d73b77208747f3421',
 'run-solution-path-voice-qa-v6.py': '59618eb71570190ec78cbae98f94b15078cfd852d3325aab7ac10531400d727e',
 'run-solution-path-native-v4.py': '9429b70773f3a334dd5fd45d76ecb6b2fa8b2360dfe576aac341099d7adaea5e',
 'run-first-native.py': 'a38205dac134e58da35a772290f0a151c7377b115b89910585277de76983a1f9',
}
ACTIVE = None
CREATE = getattr(subprocess, 'CREATE_NO_WINDOW', 0) | getattr(subprocess, 'BELOW_NORMAL_PRIORITY_CLASS', 0)
class Pending(RuntimeError): pass

def require(ok, message):
 if not ok: raise Pending(message)
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
 with Path(path).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def pin(path): return dict(path=str(Path(path).resolve()), sha256=sha(path))
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
def bound(row):
 p = Path(row['path']).resolve()
 require(p.is_file() and sha(p) == row['sha256'], 'Changed pinned file: ' + str(p))
 return p
def module(name, path):
 spec = importlib.util.spec_from_file_location(name, path); value = importlib.util.module_from_spec(spec)
 sys.modules[name] = value; spec.loader.exec_module(value); return value
def save(path, value):
 path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
 require(not path.exists(), 'Preserve existing immutable QA artifact: ' + str(path))
 with path.open('x', encoding='utf-8', newline='\n') as f:
  json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')
def check_sources(final=False):
 require(sha(__file__)==SELF_SHA,'Encoded QA source changed after import')
 for name, expected in PINS.items(): require(sha(HERE / name) == expected, 'Reviewed source changed: ' + name)
 if final:
  require(RENDERER_SHA is not None, 'Full-film renderer and exact audio assembly contract are not frozen')
  require(RENDERER.is_file() and sha(RENDERER) == RENDERER_SHA, 'Reviewed final renderer changed')

def pure_functions(path, names, scope):
 tree = ast.parse(Path(path).read_text(encoding='utf-8-sig'))
 nodes = [x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name in names]
 require({x.name for x in nodes} == set(names), 'Pinned pure primitive set changed')
 exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), scope)
 return scope

def primitives():
 """Only topic-neutral numerical functions; no historical bundle/CLI hooks."""
 import numpy as np
 from scipy.signal import correlate
 check_sources()
 path = HERE / 'first-level-continuity-review.py'
 tree = ast.parse(path.read_text(encoding='utf-8-sig'))
 policy = next(x for x in tree.body if isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'POLICY' for t in x.targets))
 scope = dict(np=np, math=math, Fraction=Fraction, correlate=correlate)
 exec(compile(ast.Module(body=[policy], type_ignores=[]), str(path), 'exec'), scope)
 pure_functions(path, {'db', 'sample_window', 'scale_window', 'levels', 'trend', 'residual_summary', 'estimate_alignment'}, scope)
 return types.SimpleNamespace(**scope)

# Exact pure AAC contracts are source-extracted, without importing the old
# 06 module, its fixed103/1041/25 clocks, accepted decisions or worker globals.
_packet_scope = dict(require=require, pin=pin, digest=digest, Path=Path, Fraction=Fraction, re=re, json=json, math=math)
require(sha(HERE / 'review-prospect-refuge-encoded-audio.py') == PINS['review-prospect-refuge-encoded-audio.py'], 'Packet primitive source changed')
pure_functions(HERE / 'review-prospect-refuge-encoded-audio.py',
 {'packet_contract', 'same_packets', 'decoded_grid', 'measured_input', 'peak_flags'}, _packet_scope)
packet_contract, same_packets, decoded_grid, measured_input, peak_flags = [_packet_scope[n] for n in ('packet_contract', 'same_packets', 'decoded_grid', 'measured_input', 'peak_flags')]

def component_grid(rows, raw_frames):
 require(len(rows) == 48 and len({r['sceneId'] for r in rows}) == 48, 'Current48 ordered raw components required')
 position = 0; paragraphs = []
 for row in rows:
  a, b = row['destinationSampleRange']
  require(type(a) is type(b) is int and a == position and a < b and row['frames'] == b-a,
          'Component sample gap/overlap or length mismatch')
  require(row['sourceSampleRange'] == [0, b-a] and row['prepared48kSampleRange'] == [a*2, b*2], 'Exact raw-to-mix2x sample mapping required')
  require(type(row['paragraph']) is int and 1 <= row['paragraph'] <= 14, 'Invalid paragraph index')
  require(math.isfinite(row['normalization']['constantGainDb']), 'Finite accepted complete-take scalar required')
  paragraphs.append(row['paragraph']); position = b
 require(position == raw_frames and paragraphs == sorted(paragraphs) and list(dict.fromkeys(paragraphs)) == list(range(1, 15)), 'All14 paragraphs must cover the complete raw body')

def validate_grid(build, timeline):
 raw, mix = build['rawVoice'], build['mixWav']; n = raw['frames']
 require(build.get('topicId') == '11.05' and build.get('schemaVersion') == '11.05-audio-build-v5'
         and build.get('rawVoiceFingerprint') == VOICE_FP and build.get('selectedComponentCount') == 48, 'Wrong current repaired48 voice/build')
 require((raw['sampleRate'], raw['channels'], raw['sampleWidthBytes']) == (24000, 1, 2), 'Raw24k monoPCM16 required')
 require((mix['sampleRate'], mix['channels'], mix['subtype'], mix['frames']) == (48000, 2, 'FLOAT', n*2), 'Exact current stereoFLOAT2x mix required')
 picture = timeline['picturePlan']
 require(picture['audio']['mix'] == mix, 'Film uses a different accepted mix')
 mapping = dict(reference='accepted-body-mix', bodyStartSample=0, bodyEndSample=mix['frames'], wholeAudioFrames=mix['frames'], rate=48000, noAudioPadding=True)
 require(timeline.get('encodedAudioMapping') == mapping, 'Explicit final whole-audio/body mapping is missing or different; intro/outro requires a new whole-mix contract')
 require((picture['fps'], picture['totalFrames']) == (60, (n*60+23999)//24000), 'Final visual/sample ceil clock differs')
 for key, value in dict(voiceOffsetSeconds=0, insertedSamples=0, trimmedSamples=0, voiceSpeed=1., uniformMixGainDb=0.,
                         wordBoundariesShifted=False, compressorUsed=False, voiceSideDuck=False, originalRawFilesUnchanged=True).items():
  require(build.get(key) == value, 'Forbidden speech DSP/time change: ' + key)
 return dict(rawRate=24000, rawFrames=n, mixRate=48000, mixFrames=n*2, videoFrames=picture['totalFrames'], fps=60, audioMapping=mapping)

def manifest_clock(manifest, timeline):
 picture=timeline['picturePlan']
 require(manifest['format']==dict(width=1080,height=1920,fps=picture['fps'],totalFrames=picture['totalFrames']), 'Actual final manifest format/clock differs')
 require(manifest['encodedAudioMapping']==timeline['encodedAudioMapping'] and manifest['assemblyProfile']==timeline['assemblyProfile'], 'Actual final manifest changed body audio assembly mapping')

def window_plan(review, rows, mathqa):
 """Actual raw ASR words only. Caption/English display clocks are never used."""
 require(len(review['takes']) == 48 and len(review['boundaryWindows']) == 47 and len(review['paragraphs']) == 14, 'Current full48/47/14 raw ASR coverage differs')
 result, unknown = [], []
 for row, take in zip(rows, review['takes']):
  a, b = row['destinationSampleRange']; sid = row['sceneId']; task = take['task']
  require(task['sceneId'] == sid and task['offsetSample'] == a and task['endSample'] == b, 'Ordered take/word sample clock differs')
  require(take.get('aliasesApplied') is False and take.get('expectedPrompt') is None, 'Independent literal ASR required')
  for i, word in enumerate(take['globalWords']):
   item = dict(sceneId=sid, paragraph=row['paragraph'], asrWordIndex=i, recognizedText=word['text'], originalAsrTimestamp=word.get('timestamp'))
   try:
    ts = word.get('timestamp'); require(isinstance(ts, (list, tuple)) and len(ts) == 2, 'Unknown word interval')
    x, y = mathqa.sample_window(*ts, 24000)
    require(a-1 <= x < y <= b+1, 'Word exceeds the unchanged take envelope')
    clamped = [max(a, x), min(b, y)]; require(clamped[0] < clamped[1], 'Empty actual word interval')
    result.append(dict(item, kind='word', rawSampleRange=clamped, mixSampleRange=[v*2 for v in clamped],
       expandedRawSampleRange=[x, y], comparisonWindowEdgeClampOnly=dict(startSamples=clamped[0]-x, endSamples=y-clamped[1]),
       durationSeconds=(clamped[1]-clamped[0])/24000))
   except (ValueError, TypeError, Pending, OverflowError) as error:
    unknown.append(dict(item, kind='unsupported-actual-word-window', reason=str(error), automaticSpeechPass=False))
  result.append(dict(kind='take', sceneId=sid, paragraph=row['paragraph'], rawSampleRange=[a,b], mixSampleRange=[a*2,b*2], durationSeconds=(b-a)/24000))
 for p in review['paragraphs']:
  members = [r for r in rows if r['paragraph'] == p['paragraph']]; a, b = members[0]['destinationSampleRange'][0], members[-1]['destinationSampleRange'][1]
  require(p['sceneIds'] == [r['sceneId'] for r in members] and [p['startSample'], p['endSample']] == [a,b], 'Paragraph clock differs')
  result.append(dict(kind='paragraph', paragraph=p['paragraph'], rawSampleRange=[a,b], mixSampleRange=[a*2,b*2], durationSeconds=(b-a)/24000))
 for left, right, joined in zip(rows, rows[1:], review['boundaryWindows']):
  at = left['destinationSampleRange'][1]; task = joined['task']
  require(task['previousScene'] == left['sceneId'] and task['nextScene'] == right['sceneId'] and task['boundarySample'] == at, 'Actual47 adjacent join identities differ')
  a,b = max(0, at-240), min(rows[-1]['destinationSampleRange'][1], at+240)
  result.append(dict(kind='join', previousScene=left['sceneId'], nextScene=right['sceneId'], boundaryRawSample=at,
                     rawSampleRange=[a,b], mixSampleRange=[a*2,b*2], durationSeconds=(b-a)/24000))
 n = rows[-1]['destinationSampleRange'][1]
 result.append(dict(kind='tail', rawSampleRange=[max(0,n-2400),n], mixSampleRange=[max(0,n-2400)*2,n*2], durationSeconds=min(n,2400)/24000))
 return result, unknown

def prepare(render_manifest, audio_build=None, caption_timing=None):
 check_sources(final=True)
 require(sha(FORMAT_REVIEW)==FORMAT_REVIEW_SHA,'Explicit selected body-only audio format decision changed')
 path = Path(render_manifest).resolve()
 require(path.is_file() and path.name == 'render-manifest.json' and path.parent.parent == (TOPIC/'render-attempts-v2').resolve(), 'Actual immutable11.05 final render required')
 m = read(path)
 require(m.get('schemaVersion') == '11.05-render-manifest-v2' and m.get('topicId') == '11.05' and m.get('complete') is True, 'Complete final11.05 render pending')
 renderer = module('solution_encoded_final_renderer_v2', RENDERER)
 t, _ = renderer.verify_timeline(bound(m['timeline']))
 require(m['renderer'] == dict(path=str(RENDERER), sha256=RENDERER_SHA, gpuUsed=False, modelStarted=False), 'Final renderer provenance differs')
 manifest_clock(m,t)
 require(m['inputs'] == t['inputs'], 'Manifest input snapshot differs')
 for key, suffix in [('clean','clean.mp4'),('captioned','captioned.mp4'),('ko','ko.srt'),('en','en.srt')]:
  p = bound(m['outputs'][key]); require(p.parent == path.parent and p.name == 'shorts-leveldesign-11-05.'+suffix, 'Final output escaped selected attempt')
 aq = m['audioAac']; aac = bound(aq)
 require(aq.get('sharedPacketCopy') is True and aac.parent == path.parent, 'Shared actualAAC source provenance differs')
 picture = t['picturePlan']; ap = bound(picture['audioBuild']); cp = bound(picture['captionTiming'])
 require(audio_build is None or Path(audio_build).resolve() == ap, 'Explicit audio build differs from actual picture plan')
 require(caption_timing is None or Path(caption_timing).resolve() == cp, 'Explicit captions differ from actual picture plan')
 verifier = module('solution_encoded_mix_verifier_v5', HERE/'verified-solution-path-audio-build-v5.py')
 build = verifier.verified_audio_build(ap); grid = validate_grid(build,t)
 cap = module('solution_encoded_caption_v6', HERE/'build-solution-path-caption-timing-v6.py')
 caption = cap.verify_existing(cp); voice = caption['voice']; review = cap.verified_asr_review(bound(build['rawVoiceAsr']))
 require(voice['fingerprint'] == VOICE_FP and voice['aggregateWav'] == build['rawVoice'] and voice['timing'] == build['canonicalTiming'], 'Captions/ASR/acceptedmix do not use the same current rawPCM')
 require(sha(ROOT/'projects/shorts-leveldesign-11-05/narration-final-v5.json') == NARRATION_SHA, 'Final narration changed')
 folder = ap.parent; lines = read(folder/'line-levels.json'); rows = lines['components']; component_grid(rows,grid['rawFrames'])
 require([r['sceneId'] for r in rows] == [s['id'] for s in voice['identity']['scenes']], 'Accepted scalar/raw identity order differs')
 mathqa = primitives(); windows,unknown = window_plan(review,rows,mathqa)
 producer = module('solution_encoded_mix_producer_v5', HERE/'prepare-solution-path-audio-mix-v5.py')
 prepctx,_ = producer.prepare(build['rawVoiceAsr']['path'],build['rawNumericalLevelReview']['path'],build['acceptedComponentsReview']['path'])
 ff = prepctx['_audio'].base.FF.resolve(); probe = ff.with_name('ffprobe.exe')
 inputs = [pin(path),m['timeline'],pin(ap),pin(cp),build['rawVoiceAsr'],build['rawNumericalLevelReview'],build['acceptedComponentsReview'],pin(folder/'line-levels.json'),pin(ff),pin(probe),pin(FORMAT_REVIEW)]
 sources = [pin(__file__),pin(RENDERER)] + [pin(HERE/n) for n in PINS]
 identity = dict(schemaVersion=SCHEMA, topicId='11.05', sourcePins=sources, inputs=inputs,
   outputs=m['outputs'], audioAac=aq, grid=grid, pcmLineage=build['pcmLineage'], windowPlanSHA256=digest(windows),
   unknownWordWindows=unknown, policy=mathqa.POLICY, manualSkipSamples=0, automaticSpeechPass=False)
 return dict(identity=identity,fingerprint=digest(identity),manifest=m,timeline=t,build=build,rows=rows,voice=voice,review=review,
   windows=windows,unknown=unknown,mathqa=mathqa,ff=ff,probe=probe,producer=producer,audio=prepctx['_audio'],renderer=renderer)

def load_float(path, rate, channels, frames):
 import soundfile as sf
 import numpy as np
 info = sf.info(path); require((info.samplerate,info.channels,info.frames,info.subtype)==(rate,channels,frames,'FLOAT'), 'Exact FLOAT working/decode header differs')
 values,sr = sf.read(path,dtype='float32',always_2d=True)
 require(sr==rate and values.shape==(frames,channels) and np.isfinite(values).all(), 'Finite actual FLOAT PCM required')
 return values

def compare_arrays(ctx, arrays, raw, decoded):
 import numpy as np
 q = ctx['mathqa']; n=len(raw); expected=raw.copy()
 for r in ctx['rows']:
  a,b=r['destinationSampleRange'];expected[a:b]=(raw[a:b]*10**(r['normalization']['constantGainDb']/20)).astype(np.float32)
 residuals=dict(rawToScalar=q.residual_summary(arrays['normalized'],expected),
   preparedToVoice=q.residual_summary(arrays['voice'],arrays['prepared']*10**(ctx['build']['voiceGlobalGain']['constantGainDb']/20)),
   knownMixStem=q.residual_summary(arrays['mix'],arrays['voice']+arrays['music']))
 alignment=q.estimate_alignment(arrays['mix'],decoded,48000)
 grid,flags=decoded_grid(n*2,len(decoded),alignment);flags += copy.deepcopy(ctx['unknown'])
 for stage, row in residuals.items():
  if row['exceedsKnownStemTolerance']:flags.append(dict(kind='known-stem-arithmetic-residual',stage=stage,measurement=row))
 records=[]; offset=alignment.get('decodedMinusReferenceSamples',0)
 for window in ctx['windows']:
  a,b=window['rawSampleRange'];x,y=window['mixSampleRange'];measure=dict(canonical=q.levels(raw[a:b],24000))
  for name,values in arrays.items():
   lo,hi,rate=(a,b,24000) if name=='normalized' else (x,y,48000)
   measure[name]=q.levels(values[lo:hi],rate)
  record=dict(window,levels=measure,musicToVoiceRmsDb=measure['music']['rmsDbfs']-measure['voice']['rmsDbfs'])
  if window['kind']=='join':
   at=window['boundaryRawSample']
   def endpoints(values,index):
    left,right=values[index-1],values[index]
    return dict(leftLastSample=left.tolist(),rightFirstSample=right.tolist(),maximumAbsoluteStep=float(np.max(np.abs(right.astype(np.float64)-left.astype(np.float64)))))
   edges=dict(canonical=endpoints(raw,at),normalized=endpoints(arrays['normalized'],at))
   edges.update({name:endpoints(values,at*2) for name,values in arrays.items() if name!='normalized'})
   if alignment.get('supported') and 0<at*2+offset<len(decoded):edges['decoded']=endpoints(decoded,at*2+offset)
   record['boundarySamples']=edges
  if alignment.get('supported') and 0<=x+offset<y+offset<=len(decoded):
   stats=q.levels(decoded[x+offset:y+offset],48000);record.update(decodedSampleRange=[x+offset,y+offset],decoded=stats,bodyDeltaVsMixDb=stats['bodyDbfs']-measure['mix']['bodyDbfs'],rmsDeltaVsMixDb=stats['rmsDbfs']-measure['mix']['rmsDbfs'])
   if abs(record['bodyDeltaVsMixDb'])>q.POLICY['encodedWordLevelDeltaWarningDb'] and window['durationSeconds']>=.08:
    flags.append(dict(kind='encoded-local-level-delta',window=window,bodyDeltaVsMixDb=record['bodyDeltaVsMixDb']))
  else:flags.append(dict(kind='encoded-window-uncovered-or-alignment-unknown',window=window))
  if window['kind']=='word' and window['durationSeconds']>=.08 and record['musicToVoiceRmsDb']>q.POLICY['musicToVoiceRmsWarningDb']:
   flags.append(dict(kind='music-close-to-known-voice-component',window=window,componentRmsRatioDb=record['musicToVoiceRmsDb'],interpretation='Known-stem ratio, not perceptual masking/SNR'))
  records.append(record)
 trends=[]
 groups=[dict(kind='take',sceneId=r['sceneId'],members=[r['sceneId']]) for r in ctx['rows']]
 groups += [dict(kind='paragraph',paragraph=p,members=[r['sceneId'] for r in ctx['rows'] if r['paragraph']==p]) for p in range(1,15)]
 for row in groups:
  words=[]
  for w in records:
   if w['kind']=='word' and w['sceneId'] in row['members']:
    words.append(dict(w,startSeconds=w['rawSampleRange'][0]/24000,endSeconds=w['rawSampleRange'][1]/24000))
  stages={s:q.trend(words,s) for s in ('canonical','normalized','voice','mix')}
  trends.append(dict(row,stages=stages))
  for stage,value in stages.items():
   if value['suspect']:flags.append(dict(kind='sustained-word-body-decline',scope=row,stage=stage,trend=value))
 extra=decoded[n*2:]
 tail=dict(extraDecodedSamples=len(extra),manualPaddingOrTrimmingApplied=False,levels=None if not len(extra) else q.levels(extra,48000),
  finalRawSample=raw[-1].tolist(),finalBodyMixSample=arrays['mix'][-1].tolist(),lastDecodedSample=decoded[-1].tolist())
 return dict(alignment=alignment,decodedGrid=grid,residuals=residuals,windowComparisons=records,componentAndParagraphTrends=trends,decoderTail=tail,
  countByKind={k:sum(w['kind']==k for w in ctx['windows']) for k in ('word','take','paragraph','join','tail')},flags=flags)

def compute(ctx, wav):
 import soundfile as sf
 import numpy as np
 n=ctx['build']['rawVoice']['frames'];folder=Path(ctx['build']['output'])
 raw,sr=sf.read(bound(ctx['build']['rawVoice']),dtype='float32',always_2d=True)
 require(sr==24000 and raw.shape==(n,1) and np.isfinite(raw).all(),'Actual unchanged raw sample clock differs')
 arrays={name:load_float(folder/file,rate,ch,n if rate==24000 else n*2) for name,file,rate,ch in [
  ('normalized','narration-component-normalized.wav',24000,1),('prepared','narration-prepared-stem.wav',48000,2),
  ('voice','narration-stem.wav',48000,2),('music','music-stem.wav',48000,2),('mix','final-mix.wav',48000,2)]}
 info=sf.info(wav);require(info.frames>0,'Decoded AAC is empty');decoded=load_float(wav,48000,2,info.frames)
 return compare_arrays(ctx,arrays,raw,decoded)

def remaining_review(ctx):
 build=ctx['build'];levels=read(bound(build['rawNumericalLevelReview']));decisions=read(bound(build['acceptedComponentsReview']))
 return dict(rawLevelReview=build['rawNumericalLevelReview'],rawLevelFlags=levels['flags'],acceptedTechnicalDispositions=build['acceptedComponentsReview'],
  acceptedTechnicalReview=decisions,rawLiteralComparisons=[dict(sceneId=t['task']['sceneId'],recognizedLiteral=t['text'],comparison=t['comparison'],boundaryFlags=t['boundaryFlags']) for t in ctx['review']['takes']],
  rawBoundaryObservations=ctx['review']['boundaryObservations'],componentPeakAndTargetNotes=[dict(sceneId=r['sceneId'],normalization=r['normalization']) for r in ctx['rows']],
  currentMixedAsr='separate current-mix blind recognition/content review required; this numerical helper never runs ASR',
  existingTargetsCleared=False,actualListening=False,humanApproval=False)

def relocate(value, work, target):
 if isinstance(value,list):return [relocate(v,work,target) for v in value]
 if not isinstance(value,dict):return value
 result={k:relocate(v,work,target) for k,v in value.items()}
 if 'path' in result:
  p=Path(result['path']).resolve()
  if p.is_relative_to(work.resolve()):result['path']=str(target/p.relative_to(work.resolve()))
 return result

def run_tool(ctx, runtime, resource, command, work):
 require(ACTIVE is not None, 'Owned CPU singleton required before tool launch')
 command=[str(v) for v in command];require(Path(command[0]).resolve() in (ctx['ff'],ctx['probe']), 'Only pinned CPU decoder/probe allowed')
 ctx['producer'].fresh_serial_gate(runtime,resource)
 key=uuid.uuid4().hex[:10];request=work/(key+'.request.json');save(request,dict(command=command,inputIdentitySHA256=ctx['fingerprint']))
 ACTIVE.update(phase='launching-owned-audio-tool',launchCommand=command,launchRequest=pin(request),child=None)
 child=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE)
 ACTIVE.update(child=ctx['producer'].child_identity(runtime,child.pid),phase='owned-audio-tool')
 try:out,err=child.communicate(timeout=1800)
 except subprocess.TimeoutExpired:
  child.terminate();out,err=child.communicate(timeout=30)
  (work/(key+'.stdout.bin')).write_bytes(out);(work/(key+'.stderr.bin')).write_bytes(err)
  raise Pending('Only owned CPU audio child exceeded finite1800-second bound; attempt preserved')
 (work/(key+'.stdout.bin')).write_bytes(out);(work/(key+'.stderr.bin')).write_bytes(err)
 save(work/(key+'.result.json'),dict(request=pin(request),exitCode=child.returncode,stdout=pin(work/(key+'.stdout.bin')),stderr=pin(work/(key+'.stderr.bin'))))
 ACTIVE.update(child=None,phase='numerical-analysis',launchCommand=None)
 require(child.returncode==0,'Owned audio tool failed; exact receipts preserved')
 return out,err,pin(work/(key+'.result.json'))

def expected_commands(ctx, work):
 commands={k:[ctx['probe'],'-v','error','-threads','2','-select_streams','a:0','-show_streams','-show_packets','-show_data_hash','sha256','-of','json',ctx['manifest']['outputs'][k]['path']] for k in ('clean','captioned')}
 wav=work/'decoded-encoded-aac.wav'
 commands['decode']=[ctx['ff'],'-hide_banner','-nostdin','-n','-xerror','-err_detect','explode','-threads','2','-filter_threads','2','-hwaccel','none','-i',ctx['manifest']['outputs']['captioned']['path'],'-map','0:a:0','-vn','-ar','48000','-ac','2','-c:a','pcm_f32le',wav]
 for name,source in [('voice',Path(ctx['build']['output'])/'narration-stem.wav'),('mix',Path(ctx['build']['mixWav']['path'])),('decodedAac',wav)]:
  commands[name]=[ctx['ff'],'-hide_banner','-nostdin','-threads','2','-filter_threads','2','-hwaccel','none','-i',source,'-map','0:a:0','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']
 return {k:[str(v) for v in cmd] for k,cmd in commands.items()}

def verify_tool_receipts(old, ctx, target):
 work=Path(old['workOrigin']).resolve()
 require(work.parent==DEST.resolve() and re.fullmatch(r'work-'+ctx['fingerprint'][:16]+r'-[0-9a-f]{10}',work.name), 'Actual original work path escaped QA scope')
 expected=expected_commands(ctx,work);require(set(old['toolReceipts'])==set(expected),'Missing/extra actual tool receipt')
 def original_pin(row):
  original=Path(row['path']).resolve()
  require(original.parent==work and re.fullmatch(r'[0-9a-f]{10}\.(request\.json|stdout\.bin|stderr\.bin)',original.name),'Tool receipt child escaped original attempt')
  return bound(dict(path=str(target/original.name),sha256=row['sha256']))
 for role,cmd in expected.items():
  receipt=bound(old['toolReceipts'][role]);require(receipt.parent==target and re.fullmatch(r'[0-9a-f]{10}\.result\.json',receipt.name),'Tool result escaped QA version')
  result=read(receipt);require(result['exitCode']==0,'Actual tool did not succeed')
  request=read(original_pin(result['request']))
  require(request==dict(command=cmd,inputIdentitySHA256=ctx['fingerprint']),'Actual tool command/source identity differs')
  stdout=original_pin(result['stdout']).read_bytes();stderr=original_pin(result['stderr']).read_bytes()
  if role in ('clean','captioned'):require(json.loads(stdout)==read(target/(role+'-audio-packets.json')),'Saved AAC packets differ from actual probe output')
  if role in ('voice','mix','decodedAac'):require(stderr==(target/(role+'-loudness.log')).read_bytes(),'Stored loudness log differs from actual tool stderr')

def execute(render_manifest, audio_build=None, caption_timing=None):
 global ACTIVE
 check_sources(final=True)
 producer=module('solution_encoded_serial_producer',HERE/'prepare-solution-path-audio-mix-v5.py')
 runtime=module('solution_encoded_singleton',HERE/'run-first-native.py');runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
 resource=module('solution_encoded_current_resource',HERE/'run-solution-path-native-v4.py')
 producer.WORKER=WORKER
 worker=runtime.SingleWorker(WORKER,is_alive=lambda r:producer.owned_alive(runtime,r)).acquire();ACTIVE=worker;work=None
 try:
  worker.update(**producer.child_identity(runtime),stage='CPU-encoded-audio-review',topicId='11.05')
  producer.fresh_serial_gate(runtime,resource);ctx=prepare(render_manifest,audio_build,caption_timing);ctx['producer'].WORKER=WORKER
  target=DEST/ctx['fingerprint'][:24]
  if (target/'review.json').is_file():return verify_existing(target/'review.json',render_manifest)
  require(not target.exists(),'Preserve incomplete prior encoded review')
  n=ctx['build']['mixWav']['frames'];require(shutil.disk_usage(MEDIA).free>n*8+1024**3,'Insufficient proportional decode reserve')
  require(runtime.psutil.virtual_memory().available>n*120+1024**3,'Insufficient memory for exact aligned stem review')
  runtime.psutil.Process().nice(runtime.psutil.BELOW_NORMAL_PRIORITY_CLASS)
  work=DEST/('work-'+ctx['fingerprint'][:16]+'-'+uuid.uuid4().hex[:10]);work.mkdir(parents=True,exist_ok=False)
  worker.update(fingerprint=ctx['fingerprint'],output=str(work),phase='numerical-analysis');save(work/'input-identity.json',ctx['identity'])
  packets={};receipts={};commands=expected_commands(ctx,work)
  for key in ('clean','captioned'):
   cmd=commands[key]
   out,_,receipts[key]=run_tool(ctx,runtime,resource,cmd,work);data=json.loads(out);save(work/(key+'-audio-packets.json'),data)
   packets[key]=packet_contract(data,n)
  packets['comparison']=same_packets(packets['clean'],packets['captioned']);save(work/'audio-packets.json',packets)
  wav=work/'decoded-encoded-aac.wav'
  cmd=commands['decode']
  _,_,receipts['decode']=run_tool(ctx,runtime,resource,cmd,work)
  numerical=compute(ctx,wav);loudness={}
  for name,source in [('voice',Path(ctx['build']['output'])/'narration-stem.wav'),('mix',Path(ctx['build']['mixWav']['path'])),('decodedAac',wav)]:
   cmd=commands[name]
   _,err,receipts[name]=run_tool(ctx,runtime,resource,cmd,work);log=work/(name+'-loudness.log');log.write_bytes(err);loudness[name]=measured_input(log,source)
  numerical['flags']+=peak_flags(loudness);save(work/'numerical.json',numerical)
  require(prepare(render_manifest,audio_build,caption_timing)['identity']==ctx['identity'],'Input changed during measurement')
  producer.fresh_serial_gate(runtime,resource)
  artifacts=[dict(file=p.name,sha256=sha(p),bytes=p.stat().st_size) for p in sorted(work.iterdir()) if p.is_file()]
  report=dict(schemaVersion=SCHEMA,topicId='11.05',status='encoded-numerical-complete-listening-pending',fingerprint=ctx['fingerprint'],inputIdentity=ctx['identity'],
   renderManifest=pin(render_manifest),timeline=ctx['manifest']['timeline'],masters={k:ctx['manifest']['outputs'][k] for k in ('clean','captioned')},mixWav=ctx['build']['mixWav'],
   packetProof=pin(work/'audio-packets.json'),packetMatch=packets['comparison'],decode=dict(source=ctx['manifest']['outputs']['captioned'],wav=pin(wav),manualSkipSamples=0,audioModified=False),
   numerical=pin(work/'numerical.json'),fullFileLoudness=loudness,toolReceipts=receipts,remainingReview=remaining_review(ctx),artifacts=artifacts,output=str(target),workOrigin=str(work),
   actualPcmDecoded=True,modelLoaded=False,gpuUsed=False,mixedAsrPerformed=False,originalPcmUnchanged=True,voiceDspChanged=False,comparisonOffsetAppliedToAudio=False,
   automaticSpeechPass=False,actualListening=False,fullRealtimePlayback=False,naturalnessApproved=False,humanApproval=False,platformActions=[])
  report=relocate(report,work,target);save(work/'review.json',report);require(not target.exists(),'Concurrent result appeared; preserve both attempts');work.rename(target);work=None
  return report
 except BaseException as error:
  if work and work.exists() and not (work/'failed.json').exists():save(work/'failed.json',dict(complete=False,error=repr(error),originalPcmUnchanged=True,actualListening=False))
  raise
 finally:
  ACTIVE=None;worker.close(remove=not(runtime.alive(worker.record.get('child')) or producer.unregistered_child(runtime,worker.record)))

def verify_existing(path, render_manifest=None):
 path=Path(path).resolve();old=read(path);require(old.get('schemaVersion')==SCHEMA and old.get('topicId')=='11.05','Wrong encoded QA report scope')
 manifest=bound(old['renderManifest']);require(render_manifest is None or manifest==Path(render_manifest).resolve(),'Report belongs to another render')
 ctx=prepare(manifest);target=DEST/ctx['fingerprint'][:24]
 require(path==target/'review.json' and old['inputIdentity']==ctx['identity'] and old['fingerprint']==ctx['fingerprint'],'Stale encoded source/input identity')
 saved_bindings(old,ctx,target)
 names=[r['file'] for r in old['artifacts']];require(len(names)==len(set(names)),'Duplicate artifact')
 for row in old['artifacts']:
  require(Path(row['file']).name==row['file'],'Artifact path escape');p=bound(dict(path=str(target/row['file']),sha256=row['sha256']));require(p.stat().st_size==row['bytes'],'Artifact length changed')
 for item,name in [(old['decode']['wav'],'decoded-encoded-aac.wav'),(old['packetProof'],'audio-packets.json'),(old['numerical'],'numerical.json')]:
  require(bound(item)==target/name,'Exact owned result artifact required')
 verify_tool_receipts(old,ctx,target)
 packets={k:packet_contract(read(target/(k+'-audio-packets.json')),ctx['build']['mixWav']['frames']) for k in ('clean','captioned')}
 packets['comparison']=same_packets(packets['clean'],packets['captioned'])
 require(read(bound(old['packetProof']))==packets and old['packetMatch']==packets['comparison'],'AAC packet evidence changed')
 full={k:measured_input(target/(k+'-loudness.log'),p) for k,p in [('voice',Path(ctx['build']['output'])/'narration-stem.wav'),('mix',ctx['build']['mixWav']['path']),('decodedAac',old['decode']['wav']['path'])]}
 numerical=compute(ctx,bound(old['decode']['wav']));numerical['flags']+=peak_flags(full)
 require(read(bound(old['numerical']))==numerical and old['fullFileLoudness']==full,'Actual numerical/input measurement differs')
 require(old['remainingReview']==remaining_review(ctx),'Existing literal/numerical targets were cleared or changed')
 require(old.get('status')=='encoded-numerical-complete-listening-pending' and old.get('actualPcmDecoded') is True
  and old.get('originalPcmUnchanged') is True and old.get('platformActions')==[]
  and old['decode'].get('manualSkipSamples')==0 and old['decode'].get('audioModified') is False,'False completion/DSP/platform claim')
 for key in ('actualListening','fullRealtimePlayback','naturalnessApproved','humanApproval','automaticSpeechPass','mixedAsrPerformed','modelLoaded','gpuUsed','voiceDspChanged','comparisonOffsetAppliedToAudio'):
  require(old.get(key) is False,'Numerical report cannot grant '+key)
 return old

def saved_bindings(old,ctx,target):
 require(old.get('renderManifest')==ctx['identity']['inputs'][0] and old.get('timeline')==ctx['manifest']['timeline']
  and old.get('masters')=={k:ctx['manifest']['outputs'][k] for k in ('clean','captioned')} and old.get('mixWav')==ctx['build']['mixWav']
  and old.get('decode',{}).get('source')==ctx['manifest']['outputs']['captioned'] and Path(old.get('output','')).resolve()==target.resolve(), 'Saved master/timeline/mix/decode substitution')
 hashes={r['file']:r['sha256'] for r in old['artifacts']}
 for item,name in [(old['decode']['wav'],'decoded-encoded-aac.wav'),(old['packetProof'],'audio-packets.json'),(old['numerical'],'numerical.json')]:
  require(Path(item['path']).resolve()==target/name and item['sha256']==hashes.get(name),'Saved owned artifact pin/path mismatch')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--render-manifest');p.add_argument('--audio-build');p.add_argument('--caption-timing');p.add_argument('--verify-report');p.add_argument('--execute',action='store_true');a=p.parse_args()
 try:
  if a.verify_report:result=verify_existing(a.verify_report,a.render_manifest)
  elif a.execute:
   require(a.render_manifest,'Actual final render required');result=execute(a.render_manifest,a.audio_build,a.caption_timing)
  elif a.render_manifest:
   ctx=prepare(a.render_manifest,a.audio_build,a.caption_timing);result=dict(ready=True,fingerprint=ctx['fingerprint'],mediaStarted=False,modelLoaded=False)
  else:result=dict(ready=False,pending='Actual repaired voice/accepted mix/final whole-audio mapping and frozen renderer are required',mediaStarted=False,modelLoaded=False)
 except (Pending,FileNotFoundError,ValueError,KeyError) as error:result=dict(ready=False,pending=str(error),mediaStarted=False,modelLoaded=False,actualListening=False,humanApproval=False)
 print(json.dumps(result,ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()
