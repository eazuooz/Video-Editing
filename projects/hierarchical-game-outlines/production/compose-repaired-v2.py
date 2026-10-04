"""Apply only directly accepted repair candidates to a separate speech version.

Preserve every unaffected v1 PCM segment. This prepares composites for ASR;
it cannot approve the voice, timing, captions or final render.
"""
from pathlib import Path
import hashlib, json, shutil, sys
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/hierarchical-game-outlines'
WORK=BASE/'production/repair1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pcm(p):
    x,sr=sf.read(p,dtype='int16')
    assert sr==24000 and x.ndim==1
    return x
proof_path=WORK/'v2-composite-proof.json'
if proof_path.exists():raise RuntimeError('Composites already exist; review their ASR instead.')
request=read(WORK/'request.json')
for item in request['inputs']:
    assert sha(ROOT/item['path'])==item['sha256'], item['path']
review=read(WORK/'direct-review.json')
accepted={row['scene']:row for row in review['scenes'] if row['decision']=='content-readback-pass'}
assert set(accepted)=={edit['id'] for edit in request['edits']}, 'All six candidates must pass direct current-hash content review.'
assert review['allCandidateParagraphsDirectlyCompared'] is True
for row in accepted.values():
    audio=ROOT/row['audio'];cache=ROOT/row['asr']
    assert sha(audio)==row['audio_sha256']
    assert sha(cache)==row['asr_sha256']
    assert read(cache)['audio_sha256']==sha(audio)
v1=ROOT/'shared/output/narration/hierarchical-game-outlines/qwen3-1.7b-balanced-v1'
v2=ROOT/'shared/output/narration/hierarchical-game-outlines/qwen3-1.7b-balanced-v2'
if v2.exists() and any(v2.rglob('*.wav')):
    raise RuntimeError('An existing v2 speech package must not be overwritten.')
splices={row['scene']:row for row in read(WORK/'splice-plan.json')['scenes']}
prepared=[]
# All source/candidate hashes, PCM ranges and explanation lengths are checked
# before any output is written, so a failed gate cannot leave a partial v2.
for sid in [f'{n:02}' for n in range(1,13)]:
    source=v1/'chunks'/f'{sid}-scene.wav'
    original=pcm(source)
    assert read(v1/'asr'/f'{sid}.json')['audio_sha256']==sha(source)
    if sid not in splices:
        prepared.append((sid,source,None,{'scene':sid,'source':source.relative_to(ROOT).as_posix(),
            'sourceSha256':sha(source),'wholeWaveByteIdentical':True,
            'wholeCompositeAsrReviewed':False}))
        continue
    entry=splices[sid]
    assert sha(source)==entry['sourceSha256']
    parts=[];retained=[];replacements=[];cursor=0
    def preserve(a,b):
        if b<=a:return
        segment=original[a:b];offset=sum(len(part) for part in parts)
        parts.append(segment)
        retained.append({'sourceFromSample':a,'sourceToSample':b,
            'compositeFromSample':offset,'samples':len(segment),
            'pcmSha256':hashlib.sha256(segment.tobytes()).hexdigest()})
    for patch in sorted(entry['replacements'],key=lambda p:p['from']):
        a,b=round(patch['from']*24000),round(patch['to']*24000)
        assert cursor<=a<b<=len(original)
        candidate=ROOT/accepted[patch['candidateId']]['audio']
        replacement=pcm(candidate)
        if int(sid)%2==0 and len(replacement)<b-a:
            raise RuntimeError(f'Explanation {sid} candidate is shorter than the original paragraph. Do not pad or delete explanation to pass.')
        preserve(cursor,a)
        # Join spacing at reviewed quiet boundaries, never speech stretching.
        if parts:parts.append(np.zeros(2400,dtype=np.int16))
        offset=sum(len(part) for part in parts);parts.append(replacement)
        if b<len(original):parts.append(np.zeros(2400,dtype=np.int16))
        replacements.append({'candidateId':patch['candidateId'],
            'candidate':candidate.relative_to(ROOT).as_posix(),'sha256':sha(candidate),
            'compositeFromSample':offset,'samples':len(replacement),
            'sourceRemovedSamples':[a,b]})
        cursor=b
    preserve(cursor,len(original))
    combined=np.concatenate(parts)
    if int(sid)%2==0 and len(combined)<len(original):
        raise RuntimeError(f'Explanation {sid} would shrink before output.')
    prepared.append((sid,source,combined,{'scene':sid,'source':entry['source'],
        'sourceSha256':sha(source),'seconds':len(combined)/24000,
        'originalSeconds':len(original)/24000,'retainedPcm':retained,
        'replacements':replacements,'wholeCompositeAsrReviewed':False}))
(v2/'chunks').mkdir(parents=True,exist_ok=True);(v2/'asr').mkdir(exist_ok=True)
proof=[]
for sid,source,combined,entry in prepared:
    dest=v2/'chunks'/source.name
    if combined is None:
        shutil.copy2(source,dest);assert sha(dest)==sha(source)
        shutil.copy2(v1/'asr'/f'{sid}.json',v2/'asr'/f'{sid}.json')
    else:
        sf.write(dest,combined,24000,subtype='PCM_16')
        decoded=pcm(dest);assert np.array_equal(decoded,combined)
        for part in entry['retainedPcm']:
            offset=part['compositeFromSample'];length=part['samples']
            assert hashlib.sha256(decoded[offset:offset+length].tobytes()).hexdigest()==part['pcmSha256']
    entry.update(composite=dest.relative_to(ROOT).as_posix(),compositeSha256=sha(dest))
    proof.append(entry)
manifest=read(BASE/'project.json')
stem='hierarchical-game-outlines-qwen3-1.7b-balanced-v2'
manifest['tts'].update(outputDir=v2.relative_to(ROOT).as_posix(),filenameStem=stem)
manifest['paths'].update(narration=(v2/f'{stem}.wav').relative_to(ROOT).as_posix(),
    captionsKo=(v2/f'{stem}.srt').relative_to(ROOT).as_posix(),
    captionsEn=(v2/f'{stem}.en.srt').relative_to(ROOT).as_posix())
write(WORK/'v2.manifest.json',manifest)
write(proof_path,{'status':'preserved-PCM-composites-awaiting-current-hash-whole-scene-ASR',
    'candidateReadback':(WORK/'direct-review.json').relative_to(ROOT).as_posix(),
    'compositionInputs':request['inputs'],'unchangedParagraphs':54,
    'originalExplanationClaimsPreserved':True,'humanListening':'pending','scenes':proof})
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import render_narration as r
r.np=np;r.sf=sf
r.configure_project('hierarchical-game-outlines',manifest_override=(WORK/'v2.manifest.json').relative_to(ROOT).as_posix())
r._apply_edge_fades=lambda x,sr:x
r.assemble_outputs(r.load_jobs())
print('Separate v2 composites created; direct full current-hash ASR and final timing/cut review remain required.')
