"""Apply only directly reviewed candidates and preserve all unaffected PCM bytes."""
from pathlib import Path
import hashlib,json,shutil,sys
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/picking-sides';WORK=BASE/'production/existing-game-replan'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pcm(p):
    x,sr=sf.read(p,dtype='int16');assert sr==24000 and x.ndim==1
    return x
v2=ROOT/'shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2'
v3=ROOT/'shared/output/narration/picking-sides/qwen3-1.7b-balanced-v3';(v3/'chunks').mkdir(parents=True,exist_ok=True);(v3/'asr').mkdir(exist_ok=True)
if (WORK/'v3-composite-proof.json').exists():raise RuntimeError('Composites already exist; inspect current proof, do not repeat.')
approved={}
for number in [1,2]:
    review=read(WORK/f'phrase-repair{number}/direct-review.json')
    for s in review['scenes']:
        if s['decision']=='content-readback-pass':approved[s['scene']]=s
assert set(approved)=={'02','05','07'}
for sid,s in approved.items():
    folder=ROOT/f'shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2-phrase-repair{1 if sid=="05" else 2}'
    p=folder/'chunks'/f'{sid}-scene.wav';assert sha(p)==s['audio_sha256'];s['candidate']=p
plan=read(WORK/'phrase-repair1/splice-plan.json');proof=[]
for entry in plan['scenes']:
    sid=entry['scene'];source=ROOT/entry['source'];assert sha(source)==entry['sourceSha256']
    original=pcm(source);replacement=pcm(approved[sid]['candidate']);gap=np.zeros(2400,dtype=np.int16)
    parts=[];retained=[]
    def preserve(a,b):
        part=original[round(a*24000):round(b*24000)];offset=sum(len(p) for p in parts);parts.append(part)
        retained.append({'sourceFromSample':round(a*24000),'sourceToSample':round(b*24000),'compositeFromSample':offset,'samples':len(part),'pcmSha256':hashlib.sha256(part.tobytes()).hexdigest()})
    if sid=='02':preserve(0,entry['preservePrefixSeconds']);parts.extend([gap,replacement])
    elif sid=='05':parts.extend([replacement,gap]);preserve(entry['preserveSuffixFromSeconds'],len(original)/24000)
    else:
        preserve(0,entry['preservePrefixSeconds']);parts.extend([gap,replacement,gap]);preserve(entry['preserveSuffixFromSeconds'],len(original)/24000)
    combined=np.concatenate(parts);dest=v3/'chunks'/f'{sid}-scene.wav';sf.write(dest,combined,24000,subtype='PCM_16');decoded=pcm(dest);assert np.array_equal(decoded,combined)
    for r in retained:
        segment=decoded[r['compositeFromSample']:r['compositeFromSample']+r['samples']]
        assert hashlib.sha256(segment.tobytes()).hexdigest()==r['pcmSha256']
    proof.append({'scene':sid,'source':entry['source'],'sourceSha256':sha(source),'candidate':approved[sid]['candidate'].relative_to(ROOT).as_posix(),'candidateSha256':sha(approved[sid]['candidate']),'composite':dest.relative_to(ROOT).as_posix(),'compositeSha256':sha(dest),'seconds':len(combined)/24000,'retainedPcm':retained,'candidateContentDirectlyReviewed':True,'wholeCompositeAsrReviewed':False})
for sid in [f'{i:02}' for i in range(1,13) if i not in [2,5,7]]:
    source=v2/'chunks'/f'{sid}-scene.wav';dest=v3/'chunks'/source.name;shutil.copy2(source,dest);assert sha(source)==sha(dest)
    asr=v2/'asr'/f'{sid}.json';a=read(asr);assert a['audio_sha256']==sha(dest);shutil.copy2(asr,v3/'asr'/asr.name)
    proof.append({'scene':sid,'source':source.relative_to(ROOT).as_posix(),'composite':dest.relative_to(ROOT).as_posix(),'compositeSha256':sha(dest),'wholeWaveByteIdentical':True,'wholeCompositeAsrReviewed':False})
manifest=read(BASE/'project.json');manifest['tts'].update(outputDir=v3.relative_to(ROOT).as_posix(),filenameStem='picking-sides-qwen3-1.7b-balanced-v3')
write(WORK/'v3.manifest.json',manifest);write(WORK/'v3-composite-proof.json',{'status':'preserved-PCM-composites-awaiting-whole-current-hash-ASR','originalExplanationParagraphsPreserved':29,'sampleRate':24000,'encoding':'mono PCM16','scenes':sorted(proof,key=lambda s:s['scene']),'humanListening':'pending'})
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r
r.np=np;r.sf=sf;r.configure_project('picking-sides',manifest_override=(WORK/'v3.manifest.json').relative_to(ROOT).as_posix());r._apply_edge_fades=lambda wav,sr:wav
r.assemble_outputs(r.load_jobs());print('Separatev3 composites created with originalPCM proof; full current-hashASR still required.')
